from uuid import UUID
from sqlalchemy.orm import Session

from app.modules.teams.repository import TeamRepository, TeamMemberRepository
from app.modules.organizations.repository import OrganizationMemberRepository, OrganizationRepository
from app.modules.users.repository import UserRepository
from app.models.users import User
from app.models.teams import Team
from app.models.team_members import TeamMember
from app.models.enums import OrganizationRole

class TeamService:
    def __init__(self, team_repository: TeamRepository,
                 membership_repository: OrganizationMemberRepository,
                 organization_repository: OrganizationRepository,
                 db: Session):
        self.team_repository = team_repository
        self.membership_repository = membership_repository
        self.organization_repository = organization_repository
        self.db = db

    def create_team(self, name: str, org_id: UUID, current_user: User) -> Team:
        try:
            organization = self.organization_repository.get_by_id(org_id)
            if not organization:
                raise ValueError("Organization not found")

            membership = self.membership_repository.get_membership(org_id, current_user.id)
            if not membership:
                raise ValueError("User not in organization")
            
            if membership.role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
                raise ValueError("don't have access to create team")
            
            if self.team_repository.get_by_name(name, org_id):
                raise ValueError("Team already exist")

            team = self.team_repository.create(name, org_id)
            self.db.commit()

            return team
        except Exception:
            self.db.rollback()
            raise

class TeamMembershipService:
    def __init__(self, team_repository: TeamRepository,
                 team_member_repository:TeamMemberRepository,
                 org_repository: OrganizationRepository,
                 org_member_repository: OrganizationMemberRepository,
                 user_repository: UserRepository,
                 db: Session):
        self.team_repository = team_repository
        self.team_member_repository = team_member_repository
        self.org_repository = org_repository
        self.org_member_repository = org_member_repository
        self.user_repository = user_repository
        self.db = db

    def add_team_member(self, team_id: UUID, user_id: UUID, current_user: User):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("user not exist")
        
        team = self.team_repository.get_by_id(team_id)
        if not team:
            raise ValueError("team not exist")
        
        org_membership = self.org_member_repository.get_membership(org_id=team.org_id, user_id=user_id)
        if not org_membership:
            raise ValueError("user not in organization")
        
        curr_user_membership =  self.org_member_repository.get_membership(org_id=team.org_id, user_id=current_user.id)
        if not curr_user_membership:
            raise ValueError("you are not in organization")
        
        if curr_user_membership.role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            raise ValueError("you are unauthorized to add user to team")

        team_membership = self.team_member_repository.get_membership(team_id=team_id, user_id=user_id)
        if team_membership:
            raise ValueError("user already in team")
        
        try:
            self.team_member_repository.create(
                TeamMember(
                    team_id = team_id,
                    user_id = user_id
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    def get_team_members(self, team_id):
        team = self.team_repository.get_by_id(team_id)

        if not team:
            raise ValueError("incorrect team id")
        
        members = self.team_member_repository.get_team_members(team_id)
        print(members)
        return {
            "team_id": team_id,
            "team_name": team.name,
            "members": [{
                "user_id": member.id,
                "email": member.email
            }for member in members
            ]
        }

        