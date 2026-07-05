from pydantic import BaseModel
from uuid import UUID
from app.models.enums import TaskPriority, TaskStatus

class CreateTaskRequest(BaseModel):
    title: str
    description: str

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str
    org_id: UUID

class AssignTasktoUserRequest(BaseModel):
    user_id: UUID

class AssignTasktoTeamRequest(BaseModel):
    team_id: UUID

class UpdateStatusRequest(BaseModel):
    status: TaskStatus

class UpdatePriorityRequest(BaseModel):
    priority: TaskPriority