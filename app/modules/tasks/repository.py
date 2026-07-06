from sqlalchemy.orm import Session
from sqlalchemy import select, update
from uuid import UUID
from typing import Optional

from app.models.tasks import Task
from app.models.task_history import TaskHistory
from app.models.enums import TaskStatus, TaskPriority

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task: Task)->Task:
        self.db.add(task)
        self.db.flush()
        return task
    
    def get_task(self, task_id:UUID)-> Optional[Task]:
        return self.db.scalar(
            select(Task).where(
                Task.id == task_id
            )
        )
    def get_org_tasks(self, org_id:UUID)->list[Task]:
        return self.db.scalars(
            select(Task).where(Task.org_id == org_id)
        ).all()
    
    # def assign_user(self, task_id: UUID, assign_to:UUID):
    #     self.db.execute(update(Task).where(Task.id == task_id).values(assigned_user_id = assign_to, status = TaskStatus.IN_PROGRESS))


    # def assign_team(self, task_id: UUID, team_id:UUID):
    #     self.db.execute(update(Task).where(Task.id == task_id).values(assigned_team_id = team_id))

    def update(self, task_id: UUID, **kwargs):
        self.db.execute(update(Task).where(Task.id == task_id).values(**kwargs))

class TaskHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, history: TaskHistory) -> TaskHistory:
        self.db.add(history)
        self.db.flush
        return history
    
    def get_task_history(self, task_id:UUID) -> list[TaskHistory]:
        return self.db.scalars(
            select(TaskHistory).where(
                TaskHistory.task_id == task_id
            ).order_by(TaskHistory.created_at.desc())
        ).all()