# services/log.py
from uuid import UUID
from typing import List, Dict, Any
from database.supabase import get_supabase

async def record_action(user_id: UUID, action: str, details: Dict[str, Any] = None) -> None:
    supabase = await get_supabase()
    insert_payload = {
        "user_id": str(user_id),
        "action": action,
        "details": details or {}
    }
    try:
        response = await supabase.table("logs").insert(insert_payload).execute()
        if not response.data:
            raise ValueError("Failed to record log entry")
    except Exception as e:
        raise ValueError(f"Failed to record log: {str(e)}")

async def get_logs(user_id: UUID) -> List[Dict]:
    supabase = await get_supabase()
    response = await supabase.table("logs").select("*").eq("user_id", str(user_id)).execute()
    return response.data