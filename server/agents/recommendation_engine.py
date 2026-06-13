"""
Recommendation Engine — Health Score calculator + product ranker.
Collaborative filtering replaced by content-based scoring for demo.
"""
from db.mongo import db


def calculate_health_score(product: dict) -> dict:
    """Calculate transparent trust score for refurbished products."""
    grade_map   = {"A": 100, "B": 75, "C": 50, "D": 20}
    grade_score = grade_map.get(product.get("vision_grade", "B"), 75)

    repairs      = product.get("repair_count", 0)
    repair_score = max(0, 100 - repairs * 15)

    w_months  = product.get("warranty_months_remaining", 0)
    w_total   = product.get("warranty_months_total", 12)
    w_score   = (w_months / max(w_total, 1)) * 100

    seller_rating = product.get("seller_rating", 4.0)
    seller_score  = (seller_rating / 5.0) * 100

    battery   = product.get("battery_health_pct", 100)

    health_score = (
        grade_score  * 0.35 +
        repair_score * 0.20 +
        w_score      * 0.20 +
        seller_score * 0.15 +
        battery      * 0.10
    )

    return {
        "health_score": round(health_score, 1),
        "breakdown": {
            "condition":        round(grade_score  * 0.35, 1),
            "repair_history":   round(repair_score * 0.20, 1),
            "warranty":         round(w_score      * 0.20, 1),
            "seller_trust":     round(seller_score * 0.15, 1),
            "component_health": round(battery      * 0.10, 1),
        },
        "trust_badge": (
            "🏆 Highly Trusted" if health_score >= 85 else
            "✅ Verified Good"   if health_score >= 70 else
            "⚠️ Use with Caution"
        ),
    }


def get_recommendations(user_id: str, category: str = None, n: int = 6) -> list:
    """Return top refurbished products with health scores."""
    query = {}
    if category:
        query["category"] = category

    products = list(db.refurbished_products.find(query))
    for p in products:
        health = calculate_health_score(p)
        p["health_score"] = health["health_score"]
        p["trust_badge"]  = health["trust_badge"]
        p["breakdown"]    = health["breakdown"]

    products.sort(key=lambda x: x["health_score"], reverse=True)
    return products[:n]
