# routes/classifications.py
from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
from config import supabase
from models import ClassificationCreate, ClassificationResponse

router = APIRouter(prefix="/classifications", tags=["Classifications"])

@router.post("/", response_model=ClassificationResponse)
async def add_classification(classification: ClassificationCreate):
    try:
        response = supabase.table("classifications").insert({
            "image_id": str(classification.image_id),
            "ndvi_value": classification.ndvi_value,
            "classification": classification.classification
        }).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{image_id}", response_model=List[ClassificationResponse])
async def get_image_classification(image_id: UUID):
    response = supabase.table("classifications").select("*").eq("image_id", str(image_id)).execute()
    return response.data

@router.put("/{classification_id}")
async def edit_classification(classification_id: UUID, classification: ClassificationCreate):
    response = supabase.table("classifications").update({
        "ndvi_value": classification.ndvi_value,
        "classification": classification.classification
    }).eq("id", str(classification_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Classification not found")
    return response.data[0]