from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from app.models.base import CommonBaseModel, Base

class Organization(CommonBaseModel, Base):
     __tablename__ = "organizations"

     name = Column(String, nullable=False)
     deleted_at = Column(DateTime(timezone=True), nullable=True)

     teams = relationship("Team", back_populates="organization")
     memberships = relationship("OrganizationMember", back_populates="organization")
     tasks = relationship("Task", back_populates="organization")
