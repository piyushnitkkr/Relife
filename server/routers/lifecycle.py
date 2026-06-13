"""Feature 1 — AI Product Lifecycle Engine router."""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel
from agents.lifecycle_classifier import classify_lifecycle
from agents.vision_grader import grade_from_images
from db import db
from utils.auth import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])


class LifecycleInput(BaseModel):
    product_id: str
    category: str
    return_reason: str
    product_age_days: int
    return_frequency: int = 0
    repair_cost_estimate: float = 0.0
    seller_reputation: float = 4.0
    accessories_present: bool = True
    days_since_purchase: int = 0


@router.post("/classify")
async def classify_product(data: LifecycleInput, user=Depends(get_current_user)):
    result = classify_lifecycle(data.model_dump())
    db.lifecycle_events.insert_one({
        "product_id": data.product_id,
        "user_id":    user["user_id"],
        "input":      data.model_dump(),
        "result":     result,
        "created_at": datetime.utcnow(),
    })
    # Award credits
    db.users.update_one(
        {"_id": user["user_id"]},
        {"$inc": {"green_credits": result["green_credits_awarded"]}}
    )
    return result


@router.post("/classify-with-images")
async def classify_with_images(
    product_id: str = Form(...),
    category: str = Form(...),
    return_reason: str = Form(...),
    product_age_days: int = Form(...),
    images: list[UploadFile] = File(...),
    user=Depends(get_current_user),
):
    image_data_list = [await img.read() for img in images]
    vision_result   = await grade_from_images(image_data_list)

    payload = {
        "product_id":          product_id,
        "category":            category,
        "return_reason":       return_reason,
        "product_age_days":    product_age_days,
        "vision_grade_numeric": vision_result["grade_numeric"],
    }
    lifecycle_result = classify_lifecycle(payload)

    db.lifecycle_events.insert_one({
        "product_id": product_id, "user_id": user["user_id"],
        "input": payload, "result": lifecycle_result,
        "vision": vision_result, "created_at": datetime.utcnow(),
    })
    db.users.update_one(
        {"_id": user["user_id"]},
        {"$inc": {"green_credits": 10}}  # award for upload
    )

    return {
        "vision_grade":       vision_result,
        "lifecycle_decision": lifecycle_result,
    }
