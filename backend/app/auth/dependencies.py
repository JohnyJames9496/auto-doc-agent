from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.db.session import get_db
from backend.app.db.models import APIKey
from sqlmodel import select

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
) -> str:
    api_key = credentials.credentials
    
    result = await db.execute(select(APIKey).where(APIKey.key == api_key))
    key_record = result.scalar_one_or_none()
    
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return str(key_record.user_id)