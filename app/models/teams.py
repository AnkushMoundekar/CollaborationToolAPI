from sqlalchemy import Column, ForeignKey, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import CommonBaseModel, Base

class Team(CommonBaseModel,Base):

    __tablename__ = "teams"

    name = Column(String(255), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
 

    __table_args__ = (
        UniqueConstraint(
            "name",
            "org_id",
            name="unique_team_name_in_org"
        )
    ,)

    organization = relationship("Organization", back_populates="teams")
    memberships = relationship("TeamMember", back_populates="team")
    tasks = relationship("Task", back_populates="team")