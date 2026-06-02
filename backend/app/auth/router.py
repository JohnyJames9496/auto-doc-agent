from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from pydantic import BaseModel, EmailStr, field_validator
from backend.app.db.session import get_db
from backend.app.db.models import User, APIKey
from backend.app.auth.security import hash_password, verify_password
import secrets

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be under 72 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db=Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    await db.flush()

    # Generate API key
    api_key = f"autodoc_{secrets.token_urlsafe(32)}"
    key = APIKey(key=api_key, user_id=user.id)
    db.add(key)
    await db.commit()

    return TokenResponse(access_token=api_key)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Get or create API key
    result = await db.execute(select(APIKey).where(APIKey.user_id == user.id))
    api_key = result.scalar_one_or_none()

    if not api_key:
        api_key_str = f"autodoc_{secrets.token_urlsafe(32)}"
        api_key = APIKey(key=api_key_str, user_id=user.id)
        db.add(api_key)
        await db.commit()
    else:
        api_key_str = api_key.key

    return TokenResponse(access_token=api_key_str)
