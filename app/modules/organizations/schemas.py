from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.models.enums import OrganizationRole

class OrganizationCreateRequest(BaseModel):
    name: str

class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: UUID
    name: str

class AddUserToOrganizationRequest(BaseModel):
    user_id: UUID
    org_id: UUID
    role: OrganizationRole

class GetOrgUsersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    org_id: UUID
    user_id: UUID
    role: OrganizationRole