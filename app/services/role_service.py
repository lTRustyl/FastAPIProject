from sqlalchemy.orm import Session
from app.models.role import Role
from app.repositories import role_repository

def read_all(db: Session) -> list[Role]:
    return role_repository.get_all(db)
