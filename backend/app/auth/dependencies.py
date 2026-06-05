import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.db.session import get_db
from backend.app.db.models import APIKey
from sqlmodel import select

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
) -> str:
    api_key = credentials.credentials

    try:
        result = await db.execute(
            select(APIKey).where(APIKey.key == api_key)
        )
        key_record = result.scalar_one_or_none()

    except Exception as e:
        logger.error(f"Database error during auth: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable"
        )

    if not key_record:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")

    logger.info(f"Authenticated user: {key_record.user_id}")
    return str(key_record.user_id)