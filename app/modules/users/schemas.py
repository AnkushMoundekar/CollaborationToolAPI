from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
