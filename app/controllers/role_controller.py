from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.role_schema import RoleResponse
from app.repositories import role_repository

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("", response_model=list[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return role_repository.get_all(db)
