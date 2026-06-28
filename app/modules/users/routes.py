from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.users.schemas import UserRegisterRequest, UserResponse
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse)
def register_user(user: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        user_repository = UserRepository(db)
        user_service = UserService(user_repository)
        return user_service.register_user(user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    try:
        user_repository = UserRepository(db)
        user_service = UserService(user_repository)
        return user_service.get_users()
    except Exception as e:
        raise HTTPException(detail=str(e))