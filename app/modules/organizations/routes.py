from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.modules.organizations.services import OrganizationService, OrganizationMemberService
from app.modules.organizations.repository import OrganizationRepository, OrganizationMemberRepository
from app.modules.organizations.schemas import (OrganizationCreateRequest, 
                                               OrganizationResponse, 
                                               AddUserToOrganizationRequest,
                                               GetOrgUsersResponse)
from app.modules.users.repository import UserRepository
from app.models.users import User
from app.core.database import get_db
from app.core.dependencies import get_current_user


router = APIRouter(prefix="/org", tags=["Organization"])

@router.post("/create", response_model= OrganizationResponse)
def create_organization(org_data: OrganizationCreateRequest,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    
    org_repository = OrganizationRepository(db)
    member_repository = OrganizationMemberRepository(db)
    org_service = OrganizationService(org_repository, member_repository, db)
    try:
        return org_service.create_organization(org_data.name, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/me", response_model=list[OrganizationResponse])
def get_orgs(current_user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    
    org_repository = OrganizationRepository(db)
    member_repository = OrganizationMemberRepository(db)
    org_service = OrganizationService(org_repository, member_repository, db)
    try:
        my_orgs = org_service.get_my_organizations(current_user)
        return my_orgs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/add_user")
def add_user_to_org(data: AddUserToOrganizationRequest,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    
    org_repository = OrganizationRepository(db)
    member_repository = OrganizationMemberRepository(db)
    user_repository = UserRepository(db)
    org_member_service = OrganizationMemberService(
        organization_repository=org_repository,
        membership_repository=member_repository,
        user_repository=user_repository,
        db=db
    )
    try:
        org_member_service.add_user_organization(
            user_id=data.user_id,
            role=data.role,
            org_id=data.org_id,
            current_user=current_user)
        return {"message": "user added to organization"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{org_id}/get_users", response_model=list[GetOrgUsersResponse])
def get_org_users(org_id: UUID,
                  db: Session = Depends(get_db)):
    org_repository = OrganizationRepository(db)
    member_repository = OrganizationMemberRepository(db)
    user_repository = UserRepository(db)
    org_member_service = OrganizationMemberService(
        organization_repository=org_repository,
        membership_repository=member_repository,
        user_repository=user_repository,
        db=db
    )
    return org_member_service.get_org_users(org_id)
