# routers/logs.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List, Dict
from utils.dependencies import get_current_user
from services.log import get_logs

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/", response_model=List[Dict])
async def get_user_logs(current_user: dict = Depends(get_current_user)):
    try:
        user_id = UUID(current_user["user_id"])
        logs = await get_logs(user_id)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")