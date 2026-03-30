from fastapi import FastAPI
from app.db import engine
from app import models
from app.routers import get_users, get_user, create_user, update_user, delete_user

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(get_users.router)
app.include_router(get_user.router)
app.include_router(create_user.router)
app.include_router(update_user.router)
app.include_router(delete_user.router)


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/hello")
def say_hello():
    return {"message": "Hello world !!"}
