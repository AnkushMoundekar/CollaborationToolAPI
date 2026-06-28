from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from app.models.organizations import Organization
from app.models.organization_members import OrganizationMember
from app.models.users import User

class OrganizationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, organization: Organization) -> Organization:
        self.db.add(organization)
        self.db.flush()
        return organization
    
    def get_by_id(self, org_id: UUID) -> Optional[Organization]:
        organization = self.db.scalar(
            select(Organization).where(
                Organization.id == org_id,
                Organization.deleted_at == None
            )
        )
        return organization
    
    def get_by_name(self, name: str) -> Optional[Organization]:
        organization = self.db.scalar(
            select(Organization).where(
                Organization.name == name,
                Organization.deleted_at == None
            )
        )

        return organization
    
class OrganizationMemberRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, membership: OrganizationMember) -> OrganizationMember:
        self.db.add(membership)
        self.db.flush()
        return membership
    
    def get_membership(self, org_id: UUID, user_id: UUID) -> Optional[OrganizationMember]:
        membership = self.db.scalar(
            select(OrganizationMember).where(
                OrganizationMember.org_id == org_id,
                OrganizationMember.user_id == user_id
            )
        )
        return membership
    
    def get_memberships(self, user_id:UUID) -> list[OrganizationMember]:
        memberships = self.db.scalars(
            select(OrganizationMember).where(
                OrganizationMember.user_id == user_id
            )
        ).all()

        return memberships
    
    def get_org_users(self, org_id: UUID) -> list[OrganizationMember]:
        return self.db.scalars(
            select(OrganizationMember).where(
                OrganizationMember.org_id == org_id
            )
        ).all()