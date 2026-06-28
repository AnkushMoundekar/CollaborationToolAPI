from pydantic import BaseModel, ConfigDict
from uuid import UUID

class TeamCreateRequest(BaseModel):
    name: str

class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    org_id: UUID

class AddUsertoTeam(BaseModel):
    user_id: UUID

class TeamMemberResponse(BaseModel):
    user_id: UUID
    email: str

class TeamMembersResponse(BaseModel):
    team_id:UUID
    team_name:str
    members:list[TeamMemberResponse]
