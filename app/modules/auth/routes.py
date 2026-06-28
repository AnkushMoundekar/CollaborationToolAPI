from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.modules.users.repository import UserRepository
from app.modules.auth.repository import RefreshTokenRepository
from app.modules.auth.service import AuthService, TokenService
from app.modules.auth.schemas import TokenResponse, LoginRequest, RefreshTokenRequest
from app.core.database import get_db
from app.models.users import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user_repository = UserRepository(db)
        token_repository = RefreshTokenRepository(db)
        auth_service = AuthService(user_repository, token_repository) 
        return auth_service.login_user(request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(refresh_token: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        token_repository = RefreshTokenRepository(db)
        token_service = TokenService(token_repository)
        return token_service.refresh_access_token(refresh_token.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/logout")
def logout(refresh_token: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_repository = RefreshTokenRepository(db)
    token_service = TokenService(token_repository)
    token_service.logout_user(refresh_token.refresh_token)
    return {"message": "user logged out"}
    
@router.post("/logout-all-devices")
def logout_all_devices(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = user.id

    token_repository = RefreshTokenRepository(db)
    token_service = TokenService(token_repository)
    token_service.logout_all_user_devices(user_id)
    return {"message": "user logged out all devices"}