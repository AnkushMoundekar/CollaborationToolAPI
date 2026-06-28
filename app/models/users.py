from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.models.base import CommonBaseModel, Base

class User(CommonBaseModel, Base):

    __tablename__ = "users"


    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    organization_memberships = relationship("OrganizationMember", back_populates="user")
    team_memberships = relationship("TeamMember", back_populates="user")

    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="Task.current_user_id", back_populates="assignee")
