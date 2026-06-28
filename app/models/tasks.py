from sqlalchemy import Column, ForeignKey, DateTime, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, CommonBaseModel
from app.models.enums import TaskStatus, TaskPriority


def ChoiceEnum(enum_cls, **kwargs):
    """Helper to automatically map Python Enums to DB string values."""
    return Enum(
        enum_cls, 
        values_callable=lambda e: [item.value for item in e], 
        **kwargs
    )

class Task(CommonBaseModel, Base):

    __tablename__ = "tasks"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)

    status = Column(ChoiceEnum(TaskStatus, name="task_status"), nullable=False, default=TaskStatus.TODO)
    priority = Column(ChoiceEnum(TaskPriority, name="task_priority"), nullable=False, default= TaskPriority.MEDIUM)

    current_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    current_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    organization = relationship("Organization", back_populates="tasks")
    team = relationship("Team", back_populates="tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[current_user_id], back_populates="assigned_tasks")