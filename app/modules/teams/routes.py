from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session

from app.modules.teams.schema import TeamCreateRequest, TeamResponse, AddUsertoTeam, TeamMembersResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.users import User
from app.modules.organizations.repository import OrganizationRepository, OrganizationMemberRepository
from app.modules.teams.repository import TeamRepository, TeamMemberRepository
from app.modules.teams.services import TeamService, TeamMembershipService
from app.modules.users.repository import UserRepository

router = APIRouter(tags=["Teams"])

@router.post("/org/{org_id}/teams/create", response_model=TeamResponse)
def create_team(org_id: UUID, 
                request: TeamCreateRequest,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    try:
        org_repository = OrganizationRepository(db)
        membership_repositoy = OrganizationMemberRepository(db)
        team_repository = TeamRepository(db)

        team_service = TeamService(team_repository,membership_repositoy,org_repository,db)
        return team_service.create_team(request.name, org_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/org/{org_id}/teams", response_model=list[TeamResponse])
def get_teams(org_id: UUID,
              db: Session = Depends(get_db)):
    team_repository = TeamRepository(db)
    return team_repository.get_by_org(org_id)

@router.post("/teams/{team_id}/add_user")
def add_user_to_team(team_id: UUID,
                     request: AddUsertoTeam,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    
    try:
        team_repository = TeamRepository(db)
        team_member_repository = TeamMemberRepository(db)
        org_repository = OrganizationRepository(db)
        org_member_repository = OrganizationMemberRepository(db)
        user_repository = UserRepository(db)

        team_membership_service = TeamMembershipService(
            team_repository=team_repository,
            team_member_repository=team_member_repository,
            org_repository=org_repository,
            org_member_repository=org_member_repository,
            user_repository=user_repository,
            db=db
        )
        team_membership_service.add_team_member(team_id=team_id, user_id=request.user_id, current_user=current_user)
        return {"message": "user added to team"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/{team_id}/members", response_model=TeamMembersResponse)
def get_team_members(team_id: UUID,
                     db:Session = Depends(get_db)):
    team_repository = TeamRepository(db)
    team_member_repository = TeamMemberRepository(db)
    org_repository = OrganizationRepository(db)
    org_member_repository = OrganizationMemberRepository(db)
    user_repository = UserRepository(db)
    try:
        team_membership_service = TeamMembershipService(
                team_repository=team_repository,
                team_member_repository=team_member_repository,
                org_repository=org_repository,
                org_member_repository=org_member_repository,
                user_repository=user_repository,
                db=db)
        return team_membership_service.get_team_members(team_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

