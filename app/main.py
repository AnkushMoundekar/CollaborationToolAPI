from fastapi import FastAPI

from app.modules.users.routes import router as user_router
from app.modules.auth.routes import router as auth_router
from app.modules.organizations.routes import router as org_router
from app.modules.teams.routes import router as team_router
from app.modules.tasks.routes import router as task_router

app = FastAPI(title="Collaboration Platform")

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(org_router)
app.include_router(team_router)
app.include_router(task_router)

#default router
@app.get("/")
def root():
    return {"message": "app is running"}