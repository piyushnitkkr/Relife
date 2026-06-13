"""
Lifecycle Classifier — Gemini AI + ML fallback.
Decides product fate: resell / refurbish / exchange / donate / recycle.
"""
import pickle
import json
import random
import numpy as np
from pathlib import Path
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

ACTION_LABELS = {
    "resell_certified": "Certified Refurbished",
    "refurbish": "Send for Refurbishment",
    "exchange_marketplace": "Exchange Marketplace",
    "donate": "Donate to NGO",
    "recycle": "Recycle",
}

CREDITS = {
    "resell_certified": 50, "refurbish": 35,
    "exchange_marketplace": 30, "donate": 60, "recycle": 25,
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


# ============================================================
# GEMINI CLASSIFICATION
# ============================================================

LIFECYCLE_PROMPT = """You are a product lifecycle decision AI. Analyze this returned product and assign probability scores to each possible action.

Return ONLY valid JSON (no markdown, no code fences):
{{
  "decision": "<resell_certified | refurbish | exchange_marketplace | donate | recycle>",
  "scores": {{
    "Certified Refurbished": <0-100>,
    "Send for Refurbishment": <0-100>,
    "Exchange Marketplace": <0-100>,
    "Donate to NGO": <0-100>,
    "Recycle": <0-100>
  }},
  "reasoning": "<one sentence why>"
}}

Rules (STRICT):
- Scores must sum to exactly 100
- "decision" must be the action with the highest score
- If repair_cost > ₹3000: scores for "Certified Refurbished" and "Send for Refurbishment" MUST be below 10
- If repair_cost > ₹5000: "Recycle" score must be highest
- If product_age < 30 days AND return_reason is "changed_mind": "Certified Refurbished" should score highest
- If return_reason is "size_issue" AND category is clothing: "Exchange Marketplace" should score highest
- If product_age > 1000 days AND reason is "defective": "Recycle" or "Donate to NGO" should be highest
- Baby products older than 1 year: "Donate to NGO" should score high

Product:
- Name: {product_name}
- Category: {category}
- Return reason: {return_reason}
- Age: {product_age_days} days
- Repair cost: ₹{repair_cost_estimate}
- Return frequency: {return_frequency}
- Seller reputation: {seller_reputation}/5
- Accessories: {accessories_present}
- Days since purchase: {days_since_purchase}"""


def classify_lifecycle(data: dict) -> dict:
    """Main entry point — tries Gemini, falls back to ML."""
    if _gemini:
        try:
            return _classify_with_gemini(data)
        except Exception as e:
            print(f"Gemini lifecycle error: {e}")

    return _classify_with_ml(data)


def _classify_with_gemini(data: dict) -> dict:
    """Use Gemini 3.1 Flash Lite for intelligent lifecycle decisions."""
    prompt = LIFECYCLE_PROMPT.format(
        product_name=data.get("product_name", "Unknown Product"),
        category=data.get("category", "other"),
        return_reason=data.get("return_reason", "unknown"),
        product_age_days=data.get("product_age_days", 0),
        repair_cost_estimate=data.get("repair_cost_estimate", 0),
        return_frequency=data.get("return_frequency", 0),
        seller_reputation=data.get("seller_reputation", 4.0),
        accessories_present=data.get("accessories_present", False),
        days_since_purchase=data.get("days_since_purchase", 0),
    )

    response = _gemini.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=0.1, max_output_tokens=300),
    )

    text = response.text.strip()
    # Clean markdown fences
    if "```" in text:
        text = text.replace("```json", "").replace("```", "").strip()

    result = json.loads(text)
    action = result.get("decision", "refurbish")
    scores = result.get("scores", {})
    reasoning = result.get("reasoning", "")

    # Validate action
    if action not in ACTION_LABELS:
        action = "refurbish"

    # Get confidence from scores
    confidence = scores.get(ACTION_LABELS[action], 70)

    return {
        "action": action,
        "label": ACTION_LABELS[action],
        "confidence": round(confidence, 1),
        "reasoning": reasoning,
        "all_scores": scores,
        "green_credits_awarded": CREDITS.get(action, 0),
        "engine": "gemini-3.1-flash-lite",
    }


# ============================================================
# ML FALLBACK
# ============================================================

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

    from sklearn.ensemble import GradientBoostingClassifier
    rng = np.random.RandomState(42)
    n = 2000
    X = rng.rand(n, 9)
    y = []
    for row in X:
        grade = row[5]
        age = row[2]
        cat = int(row[0] * 8)
        reason = int(row[1] * 5)
        repair = row[4]
        if repair > 0.6:
            y.append(4)   # high repair → recycle
        elif grade > 0.75 and age < 0.3:
            y.append(0)   # like new → resell
        elif grade > 0.5 and repair < 0.4:
            y.append(1)   # minor issues → refurbish
        elif cat == 1 or reason == 2:
            y.append(2)   # clothing/size → exchange
        elif cat == 2 and age > 0.5:
            y.append(3)   # baby + old → donate
        else:
            y.append(4)   # default → recycle
    y = np.array(y)

    model = GradientBoostingClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.1, random_state=42
    )
    model.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return model


_model = _load_or_bootstrap_model()


def _classify_with_ml(data: dict) -> dict:
    """ML classification with business rule overrides."""
    features = build_feature_vector(data)
    prediction = int(_model.predict(features)[0])
    probabilities = _model.predict_proba(features)[0]
    confidence = round(float(probabilities[prediction]) * 100, 1)
    result = LABEL_MAP[prediction]

    # Business rule overrides
    repair_cost = float(data.get("repair_cost_estimate", 0))
    category = data.get("category", "other")
    return_reason = data.get("return_reason", "")
    product_age = int(data.get("product_age_days", 0))

    if repair_cost > 5000:
        prediction, confidence = 4, 85.0
        result = LABEL_MAP[prediction]
    elif repair_cost > 3000:
        prediction, confidence = 3, 76.0
        result = LABEL_MAP[prediction]

    if product_age > 1095 and return_reason == "defective":
        prediction, confidence = 4, 80.0
        result = LABEL_MAP[prediction]

    if return_reason == "changed_mind" and product_age < 30:
        prediction, confidence = 0, 92.0
        result = LABEL_MAP[prediction]

    if return_reason == "size_issue" and category in ("clothing", "shoes"):
        prediction, confidence = 2, 88.0
        result = LABEL_MAP[prediction]

    # Build scores dict
    all_scores = {
        LABEL_MAP[i]["label"]: round(float(p) * 100, 1)
        for i, p in enumerate(probabilities)
    }

    return {
        "action": result["action"],
        "label": result["label"],
        "confidence": confidence,
        "all_scores": all_scores,
        "green_credits_awarded": CREDITS.get(result["action"], 0),
        "engine": "ml-gradient-boosting",
    }
