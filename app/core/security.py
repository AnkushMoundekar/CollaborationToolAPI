from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from uuid import UUID
from fastapi import HTTPException

from datetime import datetime, timedelta, timezone
import secrets, hashlib

from app.core.config import settings

pwd = PasswordHasher()

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify_password(plain: str, hash: str) -> bool:
    try:
        return pwd.verify(hash, plain)
    except VerifyMismatchError:
        return False

def create_access_token(subject: str) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload ={
        "sub": subject,
        "expire": expire.timestamp()
    }
    return jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = UUID(payload.get("sub"))

        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token")
        return user_id
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=400, detail=str(e))


def create_refresh_token()->str:
    return secrets.token_urlsafe(32)

def hash_refresh_token(refresh_token: str)->str:
    return hashlib.sha256(refresh_token.encode()).hexdigest()