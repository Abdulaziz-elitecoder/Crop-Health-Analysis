from supabase import create_async_client, AsyncClient
from config import SUPABASE_URL, SUPABASE_KEY
import httpx

async def get_supabase() -> AsyncClient:
    print("Creating Supabase client with service role key")
    supabase: AsyncClient = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase