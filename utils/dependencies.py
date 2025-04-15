# dependencies.py
from fastapi import HTTPException
from uuid import UUID

async def get_current_user(user_id: str = None):
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    try:
        return {"user_id": str(UUID(user_id))}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")