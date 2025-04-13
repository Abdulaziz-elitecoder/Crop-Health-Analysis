from supabase import create_client, Client
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Fernet cipher for encryption
cipher = Fernet(ENCRYPTION_KEY.encode())