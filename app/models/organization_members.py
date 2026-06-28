from sqlalchemy import Column, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import CommonBaseModel, Base
from app.models.enums import OrganizationRole

class OrganizationMember(CommonBaseModel,Base):

    __tablename__ = "organization_members"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    #default it was storing the name but we needed the values to be store to be consistent
    role = Column(Enum(OrganizationRole, values_callable = lambda obj: [e.value for e in obj]),
                   nullable=False)

    __table_args__=(UniqueConstraint(
        "org_id", "user_id",
        name= "unique_org_member"
    ),)

    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="organization_memberships")