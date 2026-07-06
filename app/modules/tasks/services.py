from uuid import UUID
from sqlalchemy.orm import Session

from app.modules.tasks.repository import TaskRepository, TaskHistoryRepository
from app.modules.organizations.repository import OrganizationMemberRepository, OrganizationRepository
from app.modules.users.repository import UserRepository
from app.modules.teams.repository import TeamMemberRepository, TeamRepository
from app.models.tasks import Task
from app.models.task_history import TaskHistory
from app.models.enums import TaskStatus, TaskPriority, OrganizationRole, TaskHistoryActions

class TaskService:
    def __init__(self, task_repository: TaskRepository,
                 org_repository: OrganizationRepository,
                 org_member_repository: OrganizationMemberRepository,
                 db: Session):
        self.task_repository = task_repository
        self.org_repository = org_repository
        self.org_member_repository = org_member_repository
        self.db = db
    
    def create_task(self, org_id:UUID, data: dict, current_user_id: UUID) ->Task:
        organization = self.org_repository.get_by_id(org_id)
        if not organization:
            raise ValueError("organization not found")
        
        membership = self.org_member_repository.get_membership(org_id, current_user_id)
        if not membership:
            raise ValueError("user not in organization")
        
        new_value = {
            "title": data.title,
            "description": data.description,
            "status": TaskStatus.TODO,
            "priority": TaskPriority.MEDIUM,
        }
        try:
            task = self.task_repository.create_task(
                Task(
                    org_id = org_id,
                    title = data.title,
                    description = data.description,
                    created_by = current_user_id
                )
            )
            TaskHistoryRepository(self.db).create(
                TaskHistory(
                    task_id = task.id,
                    user_id = current_user_id,
                    action = TaskHistoryActions.TASK_CREATED,
                    new_value = new_value
                )
            )

            self.db.commit()
            return task
        except Exception:
            self.db.rollback()
            raise

class TaskAssignmentService:
    def __init__(self, db:Session,
                 taskrepository: TaskRepository,
                 user_repository: UserRepository,
                 orgmember_repository: OrganizationMemberRepository,
                 teammember_repository: TeamMemberRepository,
                 team_repository: TeamRepository):
        self.db = db 
        self.taskrepository = taskrepository
        self.user_repository = user_repository
        self.orgmember_repository = orgmember_repository
        self.teammember_repository = teammember_repository
        self.team_repository = team_repository

    def assign_user(self, task_id:UUID, assigned_to:UUID, current_user_id:UUID):
        task = self.taskrepository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")

        task_org = task.org_id
        
        assignee = self.user_repository.get_by_id(assigned_to)
        if not assignee:
            raise ValueError("assigned_to user id is incorrect")
        
        if not self.orgmember_repository.get_membership(org_id=task_org, user_id=assigned_to):
            raise ValueError("task cannot be assigned to user outside the organization")
        
        if not self.orgmember_repository.get_membership(org_id=task_org, user_id=current_user_id):
            raise ValueError("task cannot be assigned by user outside the organization")

        task_team = task.assigned_team_id
        if not task_team:
            raise ValueError("Assign a team before assigning a user")
        
        if not self.teammember_repository.get_membership(team_id=task_team, user_id=assigned_to):
            raise ValueError("User and task not in the same team")
        
        old_value = {
            "assigned_user_id": str(task.assigned_user_id),
            "status": task.status
        }
        
        try:
            self.taskrepository.update(
                task_id=task_id,
                assigned_user_id=assigned_to,
                status= TaskStatus.IN_PROGRESS
            )
            new_value = {
                "assigned_user_id": str(assigned_to),
                "status": task.status
            }
            TaskHistoryRepository(self.db).create(
                TaskHistory(
                    task_id = task.id,
                    user_id = current_user_id,
                    action = TaskHistoryActions.USER_ASSIGNED,
                    old_value = old_value,
                    new_value = new_value
                )
            )

            self.db.commit()

        except:
            self.db.rollback()
            raise 
    
    def assign_team(self,task_id: UUID, team_id: UUID, current_user_id: UUID):
        task = self.taskrepository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")

        task_org = task.org_id

        if not self.orgmember_repository.get_membership(org_id=task_org, user_id=current_user_id):
            raise ValueError("task cannot be assigned by user outside the organization")

        team = self.team_repository.get_by_id(team_id)
        if not team:
            raise ValueError("Invalid team id")
        
        if team.org_id != task_org:
            raise ValueError("cannot assign task to team from different organization")
        
        old_value = {
            "assigned_team_id": str(task.assigned_team_id)
        }
        new_value = {
            "assigned_team_id": str(team_id)
        }

        try:
            self.taskrepository.update(
                task_id = task_id,
                assigned_team_id=team_id,
                assigned_user_id=None
            )
            TaskHistoryRepository(self.db).create(
                TaskHistory(
                    task_id = task.id,
                    user_id = current_user_id,
                    action = TaskHistoryActions.TEAM_ASSIGNED,
                    old_value = old_value,
                    new_value = new_value
                )
            )

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def reopen_task(self, task_id: UUID, current_user_id:UUID):
        task = self.taskrepository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        
        org_membership = self.orgmember_repository.get_membership(task.org_id, current_user_id)
        if not org_membership:
            raise ValueError("Task cannot be reopend by user outside organization")
        
        if ((task.created_by != current_user_id) and 
            (org_membership.role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN])):
            raise ValueError("You are not authorized to reopen the task")

        if (task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]):
            raise ValueError("the task is already open")
        
        assigned_team_id = None
        old_value = {
            "status": task.status,
            "assigned_team_id": str(task.assigned_team_id),
            "assigned_user_id": str(task.assigned_user_id)
        }
        
        if task.assigned_team_id:
            team = self.team_repository.get_by_id(task.assigned_team_id)
            if team:
                assigned_team_id = team.id
        
        new_value = {
            "status": TaskStatus.TODO,
            "assigned_team_id": str(assigned_team_id),
            "assigned_user_id": None
        }
        try:
            self.taskrepository.update(
                task_id=task_id,
                assigned_team_id = assigned_team_id,
                status = TaskStatus.TODO,
                assigned_user_id = None
            )
            TaskHistoryRepository(self.db).create(
                TaskHistory(
                    task_id = task.id,
                    user_id = current_user_id,
                    action = TaskHistoryActions.TEAM_ASSIGNED,
                    old_value = old_value,
                    new_value = new_value
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
            

class TaskUpdateService:
    def __init__(self, db: Session,
                 taskrepository: TaskRepository,
                 orgmember_repository: OrganizationMemberRepository):
        self.taskrepository = taskrepository
        self.orgmember_repository =orgmember_repository
        self.db = db
    
    ALLOWED_TRANSITIONS = {
    TaskStatus.TODO: [
        TaskStatus.IN_PROGRESS,
        TaskStatus.CANCELLED
    ],

    TaskStatus.IN_PROGRESS: [
        TaskStatus.ON_HOLD,
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED
    ],

    TaskStatus.ON_HOLD: [
        TaskStatus.IN_PROGRESS,
        TaskStatus.CANCELLED
    ],

    TaskStatus.COMPLETED: [],

    TaskStatus.CANCELLED: []
    }
    def change_status(self, task_id: UUID, status: TaskStatus, current_user_id: UUID):
        task = self.taskrepository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")

        if task.assigned_user_id == None:
            raise ValueError("Task has not been assigned to user")
        
        # the task status can be only updated by user whom the task is assigned
        if current_user_id != task.assigned_user_id:
            raise ValueError("Cannot update the status")
        # status can be updated only in the allowed transition
        if status not in self.ALLOWED_TRANSITIONS[task.status]:
            raise ValueError("Invalid status tranisition")
        old_value = {"status": task.status}
        try:
            self.taskrepository.update(
                task_id=task_id,
                status=status
            )
            TaskHistoryRepository(self.db).create(
                TaskHistory(
                    task_id = task.id,
                    user_id = current_user_id,
                    action = TaskHistoryActions.TEAM_ASSIGNED,
                    old_value = old_value,
                    new_value = {"status": status}
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    
    def change_priority(self, task_id: UUID, priority: TaskPriority, current_user_id: UUID):
        task = self.taskrepository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        #task priority can be changed by anyone in the organization 
        if not self.orgmember_repository.get_membership(task.org_id, current_user_id):
            raise ValueError("priority cannot be changed by user outside the organization")
        old_value = {"priority": task.priority}
        try:
            self.taskrepository.update(
                task_id = task_id,
                priority = priority
            )
            TaskHistoryRepository(self.db).create(
                TaskHistory(
                    task_id = task.id,
                    user_id = current_user_id,
                    action = TaskHistoryActions.TEAM_ASSIGNED,
                    old_value = old_value,
                    new_value = {"priority": priority}
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    
        
        