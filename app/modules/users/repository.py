from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.sql import func

from app.models.users import User

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        user = self.db.scalar(select(User).where(User.id == user_id , User.deleted_at == None))
        return user
    
    def get_by_email(self, email:str) -> Optional[User]:
        user = self.db.scalar(select(User).where(User.email == email , User.deleted_at == None))
        return user
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user
    
    def soft_delete(self, user_id: UUID) -> None:
        self.db.execute(update(User).where(User.id==user_id).values(is_active = False, deleted_at = func.now()))
    
    def get_active_users(self) -> list[User]:
        return self.db.scalars(select(User).where(User.deleted_at == None))
