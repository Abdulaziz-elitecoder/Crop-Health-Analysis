from config import cipher
from typing import Dict, Any
import json

# Encrypt data before storing
def encrypt_data(data: Dict[str, Any]) -> str:
    if data is None:
        return None
    return cipher.encrypt(json.dumps(data).encode()).decode()

# Decrypt data when retrieving
def decrypt_data(encrypted_data: str) -> Dict[str, Any]:
    if encrypted_data is None:
        return None
    return json.loads(cipher.decrypt(encrypted_data.encode()).decode())