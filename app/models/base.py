import uuid
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class CommonBaseModel:
    __abstract__ = True
    
    id = Column(UUID(as_uuid= True), primary_key=True, default= uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())