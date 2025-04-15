# routers/classifications.py
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import Dict
from utils.dependencies import get_current_user
from services.classification import classify_image, get_result
from services.log import record_action

router = APIRouter(prefix="/classifications", tags=["Classifications"])

@router.post("/{image_id}")
async def classify_image_route(
    image_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    try:
        classification = await classify_image(image_id, UUID(current_user["user_id"]))
        # Log the action
        await record_action(
            user_id=UUID(current_user["user_id"]),
            action="classification",
            details={"image_id": str(image_id), "classification_id": str(classification["id"])}
        )
        return classification
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to classify image: {str(e)}")

@router.get("/{image_id}/result")
async def get_classification_result(
    image_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    try:
        result = await get_result(image_id, UUID(current_user["user_id"]))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve classification result: {str(e)}")