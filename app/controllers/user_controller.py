from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.schemas.user_schema import UserUpdate, UserResponse
from app.schemas.role_schema import UserRolesUpdate, RoleResponse
from app.models.user import User
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=list[UserResponse])
def get_users(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return user_service.read_all(db, limit=limit, offset=offset)

@router.get("/search", response_model=list[UserResponse])
def search_users(
        q: str = Query(min_length=1),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return user_service.search(db, q, limit=limit, offset=offset)

@router.get("/{id}/permissions", response_model=list[RoleResponse])
def get_user_permissions(id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return user_service.read_permissions(db, id)

@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return user_service.read_by_id(db, id)

@router.put("/{id}", response_model=UserResponse)
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return user_service.update(db, id, user, current_user)

@router.delete("/{id}", status_code=204)
def delete_user(id: int, db: Session = Depends(get_db), _: User = Depends(require_roles("Administrator"))):
    user_service.delete(db, id)

@router.put("/{id}/roles", response_model=UserResponse)
def update_user_roles(id: int, body: UserRolesUpdate, db: Session = Depends(get_db),
                      _: User = Depends(require_roles("Administrator"))):
    return user_service.update_roles(db, id, body)
