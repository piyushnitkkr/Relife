"""Feature 3 — Personalized Refurbished Recommendations router."""
from fastapi import APIRouter, Depends, Query
from agents.recommendation_engine import get_recommendations, calculate_health_score
from db import db
from utils.auth import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/refurbished")
async def get_refurbished(
    category: str = Query(default=None),
    n: int = Query(default=6),
    user=Depends(get_current_user),
):
    products = get_recommendations(user["user_id"], category=category, n=n)
    # Serialize ObjectId-like fields
    for p in products:
        p.pop("_id", None)
    return {"products": products, "count": len(products)}


@router.get("/health-score/{product_id}")
async def get_health_score(product_id: str, user=Depends(get_current_user)):
    product = db.refurbished_products.find_one({"product_id": product_id})
    if not product:
        return {"error": "Product not found"}
    health = calculate_health_score(product)
    return {**health, "product_id": product_id, "name": product.get("name")}
