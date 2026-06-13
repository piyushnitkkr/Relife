"""
Lifecycle Classifier — ML + Gemini-powered product fate engine.
Uses GradientBoosting as base, with smart overrides and optional Gemini reasoning.
"""
import pickle
import numpy as np
from pathlib import Path
import json
import os
from config import settings

try:
    import google.generativeai as genai
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini = genai.GenerativeModel("gemini-3.1-flash-lite")
    else:
        _gemini = None
except Exception:
    _gemini = None

MODEL_PATH = Path(__file__).parent.parent / "ml" / "models" / "lifecycle_xgb.pkl"

LABEL_MAP = {
    0: {"action": "resell_certified",     "label": "Certified Refurbished"},
    1: {"action": "refurbish",            "label": "Send for Refurbishment"},
    2: {"action": "exchange_marketplace", "label": "Exchange Marketplace"},
    3: {"action": "donate",               "label": "Donate to NGO"},
    4: {"action": "recycle",              "label": "Recycle"},
}

CATEGORY_ENCODING = {
    "electronics": 0, "clothing": 1, "baby_products": 2,
    "furniture": 3, "sports": 4, "books": 5, "other": 6,
    "gaming": 7, "toys": 8,
}

RETURN_REASON_ENCODING = {
    "defective": 0, "wrong_item": 1, "size_issue": 2,
    "changed_mind": 3, "better_price": 4, "not_as_described": 5,
}


def _credits_for_action(action: str) -> int:
    return {
        "resell_certified": 50, "refurbish": 35,
        "exchange_marketplace": 30, "donate": 60, "recycle": 25,
    }.get(action, 0)


def build_feature_vector(data: dict) -> np.ndarray:
    return np.array([[
        CATEGORY_ENCODING.get(data.get("category", "other"), 6),
        RETURN_REASON_ENCODING.get(data.get("return_reason", "changed_mind"), 3),
        min(data.get("product_age_days", 0), 1825) / 1825,
        min(data.get("return_frequency", 0), 10) / 10,
        min(data.get("repair_cost_estimate", 0), 5000) / 5000,
        data.get("vision_grade_numeric", 2) / 4,
        min(data.get("seller_reputation", 3.0), 5.0) / 5.0,
        1 if data.get("accessories_present", False) else 0,
        min(data.get("days_since_purchase", 0), 365) / 365,
    ]])


def _load_or_bootstrap_model():
    """Load saved model or train on synthetic data."""
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)

    # Bootstrap with deterministic synthetic data
    from sklearn.ensemble import GradientBoostingClassifier
    rng = np.random.RandomState(42)
    n = 2000
    X = rng.rand(n, 9)
    # Heuristic labels:
    # Low damage (feature 5), low age (2) → resell (0)
    # High damage, moderate age         → refurbish (1)
    # Clothing/size                     → exchange (2)
    # Baby + old                        → donate (3)
    # Very damaged + defective          → recycle (4)
    y = []
    for row in X:
        grade = row[5]          # vision_grade_numeric (high = good)
        age   = row[2]
        cat   = int(row[0] * 8)
        reason = int(row[1] * 5)
        if grade > 0.75 and age < 0.3:
            y.append(0)   # resell
        elif grade > 0.5:
            y.append(1)   # refurbish
        elif cat == 1 or reason == 2:
            y.append(2)   # exchange
        elif cat == 2 and age > 0.5:
            y.append(3)   # donate
        else:
            y.append(4)   # recycle
    y = np.array(y)

    model = GradientBoostingClassifier(n_estimators=200, max_depth=4,
                                       learning_rate=0.1, random_state=42)
    model.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return model


# Load once at import time
_model = _load_or_bootstrap_model()


def classify_lifecycle(data: dict) -> dict:
    # Try Gemini-powered classification first
    if _gemini:
        try:
            return _classify_with_gemini(data)
        except Exception as e:
            print(f"Gemini lifecycle failed: {e}, falling back to ML")

    # Fallback: ML model + smart overrides
    return _classify_with_ml(data)


def _classify_with_gemini(data: dict) -> dict:
    """Use Gemini 3.1 Flash Lite to reason about product lifecycle."""
    prompt = f"""You are a product lifecycle decision AI for a refurbished marketplace.

Given this returned product data, decide what should happen to it.
Return ONLY valid JSON (no markdown, no backticks):

{{
  "action": "<one of: resell_certified, refurbish, exchange_marketplace, donate, recycle>",
  "label": "<human readable label>",
  "confidence": <number 60-99>,
  "reasoning": "<one sentence explaining why>"
}}

Decision rules:
- resell_certified: Product is like new, minimal age, changed mind return, low/no repair needed
- refurbish: Minor issues, repair cost is LOW (under ₹2000). NEVER refurbish if repair cost > ₹3000
- exchange_marketplace: Size/fit issues, clothing, still functional
- donate: Old but functional, low demand, baby products outgrown
- recycle: Broken beyond repair, repair cost > ₹3000, very old defective electronics, repair cost exceeds 30% of typical product value

CRITICAL: If repair cost > ₹3000, the answer MUST be "donate" or "recycle", NEVER "refurbish" or "resell_certified".

Product data:
- Category: {data.get('category', 'other')}
- Return reason: {data.get('return_reason', 'unknown')}
- Product age: {data.get('product_age_days', 0)} days
- Repair cost estimate: ₹{data.get('repair_cost_estimate', 0)}
- Return frequency: {data.get('return_frequency', 0)} times
- Seller reputation: {data.get('seller_reputation', 4.0)}/5
- Accessories present: {data.get('accessories_present', False)}
- Days since purchase: {data.get('days_since_purchase', 0)}
- Product name: {data.get('product_name', 'Unknown')}"""

    response = _gemini.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=0.1, max_output_tokens=200),
    )
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    result = json.loads(text)
    action = result.get("action", "refurbish")
    confidence = min(99, max(60, result.get("confidence", 75)))

    # Map action to label
    action_labels = {
        "resell_certified": "Certified Refurbished",
        "refurbish": "Send for Refurbishment",
        "exchange_marketplace": "Exchange Marketplace",
        "donate": "Donate to NGO",
        "recycle": "Recycle",
    }
    label = result.get("label", action_labels.get(action, action))

    return {
        "action": action,
        "label": label,
        "confidence": confidence,
        "reasoning": result.get("reasoning", ""),
        "all_scores": {action_labels[a]: (confidence if a == action else round((100 - confidence) / 4, 1)) for a in action_labels},
        "green_credits_awarded": _credits_for_action(action),
        "engine": "gemini-3.1-flash-lite",
    }


def _classify_with_ml(data: dict) -> dict:
    """Fallback ML classification with smart overrides."""
    features = build_feature_vector(data)
    prediction = int(_model.predict(features)[0])
    probabilities = _model.predict_proba(features)[0]
    confidence = round(float(probabilities[prediction]) * 100, 1)
    result = LABEL_MAP[prediction]

    # Smart overrides based on business logic
    repair_cost = data.get("repair_cost_estimate", 0)
    category = data.get("category", "other")
    return_reason = data.get("return_reason", "")
    product_age = data.get("product_age_days", 0)

    if repair_cost > 3000 and result["action"] in ("refurbish", "resell_certified"):
        if repair_cost > 5000:
            prediction = 4
            confidence = 82.0
        else:
            prediction = 3
            confidence = 75.0
        result = LABEL_MAP[prediction]

    if product_age > 1095 and return_reason == "defective":
        if result["action"] in ("resell_certified", "refurbish"):
            prediction = 4
            confidence = 78.0
            result = LABEL_MAP[prediction]

    if return_reason == "changed_mind" and product_age < 30:
        prediction = 0
        confidence = 91.0
        result = LABEL_MAP[prediction]

    if return_reason == "size_issue" and category in ("clothing", "shoes"):
        prediction = 2
        confidence = 88.0
        result = LABEL_MAP[prediction]

    return {
        "action": result["action"],
        "label": result["label"],
        "confidence": confidence,
        "all_scores": {
            LABEL_MAP[i]["label"]: round(float(p) * 100, 1)
            for i, p in enumerate(probabilities)
        },
        "green_credits_awarded": _credits_for_action(result["action"]),
        "engine": "ml-gradient-boosting",
    }
