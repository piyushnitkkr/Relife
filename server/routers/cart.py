"""Feature 6 — Predictive Return Prevention cart router."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from agents.return_predictor import predict_return_risk
from utils.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


class CartItem(BaseModel):
    product_id: str
    category: str
    color: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = None


class CartAnalyzeRequest(BaseModel):
    items: list[CartItem]


@router.post("/analyze")
async def analyze_cart(req: CartAnalyzeRequest, user=Depends(get_current_user)):
    return {
        "analysis": [
            {
                "product_id":  item.product_id,
                "return_risk": predict_return_risk(user["user_id"], item.model_dump()),
            }
            for item in req.items
        ]
    }
