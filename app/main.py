from fastapi import FastAPI
from app.core.database import engine, Base
from app.controllers.user_controller import router as user_router
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/hello")
def say_hello():
    return {"message": "Hello world !!"}
