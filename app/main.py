from fastapi import FastAPI
from app.core.database import engine, Base, seed_roles
from app.models.role import Role, user_roles  # noqa: F401
from app.models.user import User  # noqa: F401

from app.controllers.user_controller import router as user_router
from app.controllers.role_controller import router as role_router

Base.metadata.create_all(bind=engine)
seed_roles()

app = FastAPI()

app.include_router(user_router)
app.include_router(role_router)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/hello")
def say_hello():
    return {"message": "Hello world !!"}
