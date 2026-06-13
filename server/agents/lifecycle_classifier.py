"""
Lifecycle Classifier — XGBoost-backed product fate engine.
Bootstraps with synthetic training data if no saved model exists.
"""
import pickle
import numpy as np
from pathlib import Path
import os

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
    features = build_feature_vector(data)
    prediction = int(_model.predict(features)[0])
    probabilities = _model.predict_proba(features)[0]
    confidence = round(float(probabilities[prediction]) * 100, 1)
    result = LABEL_MAP[prediction]
    return {
        "action":                result["action"],
        "label":                 result["label"],
        "confidence":            confidence,
        "all_scores":            {
            LABEL_MAP[i]["label"]: round(float(p) * 100, 1)
            for i, p in enumerate(probabilities)
        },
        "green_credits_awarded": _credits_for_action(result["action"]),
    }
