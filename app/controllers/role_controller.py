from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.role_schema import RoleResponse
from app.models.user import User
from app.services import role_service

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("", response_model=list[RoleResponse])
def get_roles(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return role_service.read_all(db)