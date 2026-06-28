from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.models.users import User
from app.modules.users.repository import UserRepository
from app.core.security import hash_password

class UserService:
    def __init__(self, userRepository: UserRepository):
        self.userRepository = userRepository

    def register_user(self, email: str, password: str) -> User:
        # check if the email already exists
        existing_user = self.userRepository.get_by_email(email)

        if existing_user:
            raise ValueError("Email already exists")
        try:
            password_hash = hash_password(password)
            user = self.userRepository.create(User(email = email, password_hash = password_hash))
            self.userRepository.db.commit()
            return user
        except Exception:
            self.userRepository.db.rollback()
            raise 
        
    def get_users(self)->list[User]:
        return self.userRepository.get_active_users()
