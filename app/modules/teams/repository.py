from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from sqlalchemy import select

from app.models.teams import Team
from app.models.users import User
from app.models.team_members import TeamMember

class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, org_id: UUID) -> Team:
        team = Team(
            name = name,
            org_id = org_id
        )
        self.db.add(team)
        self.db.flush()
        return team
    
    def get_by_id(self, id: UUID) -> Optional[Team]:
        return self.db.scalar(
            select(Team).where(
                Team.id == id,
                Team.deleted_at == None
            )
        )
    def get_by_name(self, name: str, org_id: UUID) -> Optional[Team]:
        return self.db.scalar(
            select(Team).where(
                Team.name == name,
                Team.org_id == org_id,
                Team.deleted_at == None
            )
        )
    def get_by_org(self, org_id: UUID) -> list[Team]:
        return self.db.scalars(
            select(Team).where(
                Team.org_id == org_id,
                Team.deleted_at == None
            )
        ).all()
    
class TeamMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, membership: TeamMember) -> TeamMember:
        self.db.add(membership)
        self.db.flush()
        return membership
    
    def get_membership(self, team_id: UUID, user_id: UUID) -> Optional[TeamMember]:
        membership = self.db.scalar(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id
            )
        )
        return membership

    def get_memberships(self, user_id: UUID) -> list[TeamMember]:
        memberships = self.db.scalars(
            select(TeamMember).where(
                TeamMember.user_id == user_id
            )
        ).all()
        return memberships
    def get_team_members(self, team_id: UUID) -> list:
        users = self.db.execute(
            select(User.id, User.email).join(
                TeamMember,
                TeamMember.user_id == User.id
            ).where(
                TeamMember.team_id == team_id
            )
        ).all()
        print(users)
        return users
