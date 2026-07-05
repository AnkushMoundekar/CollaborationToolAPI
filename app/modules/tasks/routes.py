from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.modules.tasks.repository import TaskRepository
from app.modules.organizations.repository import OrganizationRepository, OrganizationMemberRepository
from app.modules.users.repository import UserRepository
from app.modules.teams.repository import TeamRepository, TeamMemberRepository
from app.modules.tasks.services import TaskService, TaskAssignmentService, TaskUpdateService
from app.modules.tasks.schema import (CreateTaskRequest,
                                      TaskResponse,
                                      AssignTasktoUserRequest,
                                      AssignTasktoTeamRequest,
                                      UpdatePriorityRequest,
                                      UpdateStatusRequest)
from app.models.users import User
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter(tags=["Tasks"])

@router.post("/org/{org_id}/task/create", response_model=TaskResponse)
def create_task(org_id: UUID,
                task: CreateTaskRequest,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    task_repo = TaskRepository(db)
    org_repo = OrganizationRepository(db)
    membership_repo = OrganizationMemberRepository(db)
    try:
        task_service = TaskService(
            task_repository=task_repo,
            org_repository=org_repo,
            org_member_repository=membership_repo,
            db=db
        )
        response = task_service.create_task(org_id,task,current_user.id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/task/{task_id}", response_model= TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    try:
        task_repo = TaskRepository(db)
        return task_repo.get_task(task_id)
    except Exception as e:
        raise HTTPException(detail=str(e))
    
@router.get("/org/{org_id}/tasks", response_model=list[TaskResponse])
def get_org_tasks(org_id: UUID, db: Session = Depends(get_db)):
    try:
        task_repo = TaskRepository(db)
        return task_repo.get_org_tasks(org_id)
    except Exception as e:
        raise HTTPException(detail=str(e))
    
@router.patch("/task/{task_id}/assign-user")
def assign_user(task_id: UUID,
                request: AssignTasktoUserRequest,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    try:
        task_repo = TaskRepository(db)
        user_repo = UserRepository(db)
        org_member_repo = OrganizationMemberRepository(db)
        team_member_repo = TeamMemberRepository(db)
        team_repo = TeamRepository(db)
        
        task_assign_service = TaskAssignmentService(db, taskrepository=task_repo, 
                                                    user_repository=user_repo,
                                                     orgmember_repository= org_member_repo,
                                                      teammember_repository= team_member_repo,
                                                       team_repository= team_repo)

        task_assign_service.assign_user(task_id, request.user_id, current_user.id)
        return {"message": "user assigned"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/task/{task_id}/assign-team")
def assign_team(task_id: UUID,
                request: AssignTasktoTeamRequest,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    try:
        task_repo = TaskRepository(db)
        user_repo = UserRepository(db)
        org_member_repo = OrganizationMemberRepository(db)
        team_member_repo = TeamMemberRepository(db)
        team_repo = TeamRepository(db)
        task_assign_service = TaskAssignmentService(db, taskrepository=task_repo, 
                                                    user_repository=user_repo,
                                                     orgmember_repository= org_member_repo,
                                                      teammember_repository= team_member_repo,
                                                       team_repository= team_repo)
        task_assign_service.assign_team(task_id, request.team_id, current_user.id)
        return {"message": "team assigned"}
    except ValueError as e:
        raise HTTPException(status_code= 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/task/{task_id}/status")
def update_status(task_id: UUID,
                  request: UpdateStatusRequest,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    try:
        task_repo = TaskRepository(db)
        orgmember_repo = OrganizationMemberRepository(db)

        task_update_service = TaskUpdateService(db, 
                                                taskrepository= task_repo, 
                                                orgmember_repository=orgmember_repo)
        task_update_service.change_status(task_id, request.status, current_user.id)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/task/{task_id}/priority")
def update_priority(task_id: UUID,
                  request: UpdatePriorityRequest,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    try:
        task_repo = TaskRepository(db)
        orgmember_repo = OrganizationMemberRepository(db)

        task_update_service = TaskUpdateService(db, 
                                                taskrepository= task_repo, 
                                                orgmember_repository=orgmember_repo)
        task_update_service.change_priority(task_id, request.priority, current_user.id)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/task/{task_id}/reopen")
def reopen(task_id: UUID,
           db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    try: 
        task_repo = TaskRepository(db)
        user_repo = UserRepository(db)
        org_member_repo = OrganizationMemberRepository(db)
        team_member_repo = TeamMemberRepository(db)
        team_repo = TeamRepository(db)
        task_assign_service = TaskAssignmentService(db, taskrepository=task_repo, 
                                                    user_repository=user_repo,
                                                     orgmember_repository= org_member_repo,
                                                      teammember_repository= team_member_repo,
                                                       team_repository= team_repo)
        task_assign_service.reopen_task(task_id, current_user.id)
        return {"message": "Task has been reopened"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
