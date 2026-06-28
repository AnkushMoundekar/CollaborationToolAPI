from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.modules.users.repository import UserRepository
from app.modules.auth.repository import RefreshTokenRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, hash_refresh_token

class AuthService:
    def __init__(self, user_repository: UserRepository, token_repository: RefreshTokenRepository):
        self.user_repository = user_repository
        self.token_repository = token_repository
        
    def login_user(self, email: str, password: str):
        user = self.user_repository.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("User is inactive")
        
        # create access token
        access_token = create_access_token(subject= str(user.id))
        refresh_token = create_refresh_token()

        hashed_token = hash_refresh_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        self.token_repository.save_refresh_token(user_id=user.id, hashed_token=hashed_token, expires_at=expires_at)

        self.token_repository.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

class TokenService:
    def __init__(self, token_repository: RefreshTokenRepository):
        self.token_repository = token_repository

    def refresh_access_token(self, refresh_token: str):
        hashed_token = hash_refresh_token(refresh_token)

        token_record = self.token_repository.get_by_token_hash(hashed_token)
        if not token_record:
            raise ValueError("Invalid refresh token")
        if token_record.expires_at < datetime.now(timezone.utc):
            self.token_repository.delete_by_token_hash(hashed_token)
            self.token_repository.db.commit()
            raise ValueError("Refresh token expired")
        
        user_id = token_record.user_id

        access_token = create_access_token(subject=str(user_id))
        
        self.token_repository.delete_by_token_hash(hashed_token)
        new_refresh_token = create_refresh_token()

        new_hashed_token = hash_refresh_token(new_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        self.token_repository.save_refresh_token(user_id=user_id, hashed_token=new_hashed_token, expires_at=expires_at)

        self.token_repository.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    def logout_user(self, refresh_token: str):
        hashed_token = hash_refresh_token(refresh_token)
        self.token_repository.delete_by_token_hash(hashed_token)
        self.token_repository.db.commit()

    def logout_all_user_devices(self, user_id: UUID):
        
        self.token_repository.delete_all_user_tokens(user_id)
        self.token_repository.db.commit()