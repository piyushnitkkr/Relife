"""
Return Predictor — Random Forest trained on synthetic data.
Predicts probability that a cart item will be returned.
"""
import pickle
import numpy as np
from pathlib import Path
from db.mongo import db

MODEL_PATH = Path(__file__).parent.parent / "ml" / "models" / "return_predictor.pkl"


def _load_or_train():
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)

    from sklearn.ensemble import RandomForestClassifier
    rng = np.random.RandomState(42)
    X = rng.rand(1000, 8)
    # High clothing + high personal return rate → returned
    y = ((X[:, 0] * 0.4 + X[:, 2] * 0.3 + X[:, 3] * 0.3) > 0.5).astype(int)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return model


_model = _load_or_train()


def predict_return_risk(user_id: str, product: dict) -> dict:
    user   = db.users.find_one({"_id": user_id}) or {}
    orders = list(db.orders.find({"user_id": user_id}))
    total    = max(len(orders), 1)
    returned = sum(1 for o in orders if o.get("status") == "returned")
    same_cat = [o for o in orders if o.get("product_category") == product.get("category", "")]
    cat_ret  = sum(1 for o in same_cat if o.get("status") == "returned")

    global_signals = db.return_signals.find_one({"_id": product.get("product_id", "")}) or {}

    features = np.array([[
        returned / total,
        cat_ret / max(len(same_cat), 1),
        min(global_signals.get("return_rate_pct", 15), 100) / 100,
        1 if product.get("category") in ["clothing", "shoes", "fashion"] else 0,
        1 if product.get("size") else 0,
        min(product.get("price", 0), 50000) / 50000,
        min(user.get("account_age_days", 0), 1825) / 1825,
        1 if user.get("prime_member") else 0,
    ]])

    prob       = _model.predict_proba(features)[0][1]
    risk_score = round(prob * 100)

    reasons, tips = [], []
    if returned / total > 0.3:
        reasons.append("you have a high personal return rate")
    if cat_ret / max(len(same_cat), 1) > 0.4:
        reasons.append(f"you've returned {product.get('category','similar')} items before")
    if global_signals.get("return_rate_pct", 0) > 35:
        reasons.append(f"this product has a {global_signals['return_rate_pct']:.0f}% global return rate")
        if global_signals.get("top_reasons"):
            tips.append(f"Common reason: {global_signals['top_reasons'][0].replace('_',' ')}")
    if product.get("category") in ["clothing", "shoes"]:
        tips.append("Check the size guide carefully before ordering")

    return {
        "risk_score": risk_score,
        "risk_level": "High" if risk_score >= 70 else "Medium" if risk_score >= 45 else "Low",
        "reason":     (f"Our AI flagged this because {' and '.join(reasons)}."
                       if reasons else "Low return risk based on your profile."),
        "tip":        tips[0] if tips else "You're likely to enjoy this product!",
        "top_return_reasons": global_signals.get("top_reasons", [])[:3],
    }
