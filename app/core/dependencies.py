from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.core.database import get_db
from app.modules.users.repository import UserRepository

security = HTTPBearer()

def get_current_user(
        cred: HTTPAuthorizationCredentials = Depends(security),
        db: Session= Depends(get_db)
        ):
    token = cred.credentials
    user_id = decode_access_token(token)
    user_repository = UserRepository(db)
    user = user_repository.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code = 404, detail="Invalid user")

    return user