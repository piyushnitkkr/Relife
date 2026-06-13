"""Feature 2 — Vision grading router."""
from fastapi import APIRouter, UploadFile, File, Depends
from agents.vision_grader import grade_from_images
from utils.auth import get_current_user

router = APIRouter(prefix="/vision", tags=["vision"])


@router.post("/grade")
async def grade_product(
    images: list[UploadFile] = File(...),
    user=Depends(get_current_user),
):
    image_data_list = [await img.read() for img in images]
    result          = await grade_from_images(image_data_list)
    return result
