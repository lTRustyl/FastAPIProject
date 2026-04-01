from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base, seed_roles
from app.models.role import Role, user_roles  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.article import Article  # noqa: F401

from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.role_controller import router as role_router
from app.controllers.article_controller import router as article_router
from app.controllers.health_controller import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_roles()
    yield

app = FastAPI(
    title="Python Internship Task",
    version="1.0.0",
    lifespan=lifespan,
    )

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(article_router)