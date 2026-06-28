from sqlalchemy.orm import Session
from uuid import UUID

from app.models.users import User
from app.models.organizations import Organization
from app.models.organization_members import OrganizationMember
from app.modules.organizations.repository import OrganizationRepository, OrganizationMemberRepository
from app.modules.users.repository import UserRepository
from app.models.enums import OrganizationRole

class OrganizationService:
    def __init__(self, 
                 organization_repository: OrganizationRepository,
                 membership_repository: OrganizationMemberRepository,
                 db: Session):
        self.db = db
        self.organization_repository = organization_repository
        self.membership_repository = membership_repository

    def create_organization(self, name: str, current_user: User) -> Organization:
        existing_org = self.organization_repository.get_by_name(name)

        if existing_org:
            raise ValueError("Organization already exists")
        
        try:
            org_data = Organization(
                name = name
            )
            organization = self.organization_repository.create(organization=org_data)

            self.membership_repository.create(
                OrganizationMember(
                    org_id = organization.id,
                    user_id = current_user.id,
                    role = OrganizationRole.OWNER
                )
            )
            self.db.commit()
            return organization
        except Exception:
            self.db.rollback()
            raise 
        
    def get_my_organizations(self, current_user: User) -> list[Organization]:

        membership_list = self.membership_repository.get_memberships(current_user.id)

        return [
            membership.organization for membership in membership_list
        ]

class OrganizationMemberService:
    def __init__(self,
                 organization_repository: OrganizationRepository,
                 membership_repository: OrganizationMemberRepository,
                 user_repository: UserRepository,
                 db: Session):
        self.db = db
        self.organization_repository = organization_repository
        self.membership_repository = membership_repository
        self.user_repository = user_repository
        

    def add_user_organization(self, user_id: UUID, role: OrganizationRole, org_id: UUID, current_user: User)-> None:
        organization =  self.organization_repository.get_by_id(org_id)
        if not organization:
            raise ValueError("organization not found")
        
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("user not found")
        user_in_org = self.membership_repository.get_membership(org_id, user_id)
        if user_in_org:
            raise ValueError("user already exist in organization")
        membership = self.membership_repository.get_membership(org_id, current_user.id)
        if not membership:
            raise ValueError("you are not the member of organization")
        
        if membership.role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            raise ValueError("you are not authorized to add user to organization")
        
        if role == OrganizationRole.OWNER:
            raise ValueError("cannot create owner")
        
        try:
            self.membership_repository.create(
                OrganizationMember(
                    org_id = org_id,
                    user_id = user_id,
                    role = role
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        
    def get_org_users(self, org_id) -> list[OrganizationMember]:
        return self.membership_repository.get_org_users(org_id)

    