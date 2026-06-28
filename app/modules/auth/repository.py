from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from sqlalchemy import select, delete

from app.models.refresh_token import RefreshToken

class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_refresh_token(self, user_id: UUID, hashed_token: str, expires_at)-> None:
        tokens = self.db.scalars(select(RefreshToken).where(RefreshToken.user_id == user_id)).all()

        if len(tokens)>=5:
            oldest_token = sorted(
                tokens,
                key = lambda t: t.created_at 
            )[0]
            self.db.delete(oldest_token)
        
        self.db.add(
            RefreshToken(
                user_id = user_id,
                token_hash = hashed_token,
                expires_at = expires_at
            )
        )
        self.db.flush()
    
    def get_by_token_hash(self, hashed_token:str) -> Optional[RefreshToken]:
        token = self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hashed_token))
        return token
    
    def delete_by_token_hash(self, hashed_token: str) -> None:
        token = self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hashed_token))
        if token:
            self.db.delete(token)

    def delete_all_user_tokens(self, user_id: UUID) -> None:
        self.db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))



