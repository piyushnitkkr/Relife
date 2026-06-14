"""
Lifecycle Classifier — Groq (Llama 4 Scout) + ML fallback.
Decides product fate: resell / refurbish / exchange / donate / recycle.
"""
import pickle
import json
import random
import numpy as np
from pathlib import Path
from config import settings

try:
    from groq import Groq
    if settings.GROQ_API_KEY:
        _groq = Groq(api_key=settings.GROQ_API_KEY)
    else:
        _groq = None
except Exception:
    _groq = None

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

LIFECYCLE_PROMPT = """You are a product lifecycle decision AI for a refurbished e-commerce marketplace.

ANALYZE ALL the following factors TOGETHER to decide the best fate for this returned product:

Product Data:
- Product Name: {product_name}
- Category: {category}
- Return Reason: {return_reason}
- Product Age: {product_age_days} days old
- Repair Cost Estimate: ₹{repair_cost_estimate}
- Times Previously Returned: {return_frequency}
- Seller Reputation: {seller_reputation}/5
- Accessories Present: {accessories_present}
- Days Since Purchase: {days_since_purchase}

DECISION MATRIX (consider ALL factors, not just one):

| Scenario | Decision |
|----------|----------|
| New product (<30 days), changed mind, no damage | resell_certified |
| Minor defect, low repair cost (<₹2000), good seller | refurbish |
| Clothing/shoes + size issue, any age | exchange_marketplace |
| Old product (>1 year), baby/kids category, functional | donate |
| High repair cost (>₹3000), old (>2 years), defective | recycle |
| Very high repair cost (>₹5000), any category | recycle |
| Low demand product, functional, old | donate |
| Good condition, moderate age (1-6 months), accessories present | resell_certified |
| Moderate damage, reasonable repair (<₹2000), popular category | refurbish |

WEIGHTING:
- Repair cost relative to product value: 25%
- Product age and condition: 25%
- Return reason: 20%
- Category demand and seller reputation: 15%
- Accessories and return history: 15%

Return ONLY valid JSON (no markdown, no backticks, no explanation outside JSON):
{{
  "decision": "<resell_certified | refurbish | exchange_marketplace | donate | recycle>",
  "scores": {{
    "Certified Refurbished": <0-100>,
    "Send for Refurbishment": <0-100>,
    "Exchange Marketplace": <0-100>,
    "Donate to NGO": <0-100>,
    "Recycle": <0-100>
  }},
  "reasoning": "<one sentence explaining which factors led to this decision>"
}}

CONSTRAINTS:
- Scores MUST sum to exactly 100
- "decision" MUST match the highest scoring option
- Consider ALL 9 input parameters, not just repair cost"""


def classify_lifecycle(data: dict) -> dict:
    """Main entry point — tries Groq Llama 4, falls back to ML."""
    if _groq:
        try:
            return _classify_with_groq(data)
        except Exception as e:
            print(f"Groq lifecycle error: {e}")

    return _classify_with_ml(data)


def _classify_with_groq(data: dict) -> dict:
    """Use Groq (Llama 4 Scout 17B) for intelligent lifecycle decisions."""
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

    response = _groq.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=300,
    )

    text = response.choices[0].message.content.strip()
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
    confidence = scores.get(ACTION_LABELS.get(action, ""), 70)

    return {
        "action": action,
        "label": ACTION_LABELS.get(action, action),
        "confidence": round(confidence, 1),
        "reasoning": reasoning,
        "all_scores": scores,
        "green_credits_awarded": CREDITS.get(action, 0),
        "engine": "groq-llama4-scout",
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
