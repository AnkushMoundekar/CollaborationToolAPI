from sqlalchemy import Column, DateTime, ForeignKey, Enum, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import TaskHistoryActions

class TaskHistory(Base):

    __tablename__ = "task_history"

    id =  Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    action = Column(Enum(TaskHistoryActions, values_callable = lambda action: [a.value for a in action]), nullable=False)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    comment = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=func.now())

    task = relationship("Task", back_populates="task_history")
    user = relationship("User", back_populates="task_history")
