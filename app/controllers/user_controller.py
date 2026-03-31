from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.schemas.role_schema import UserRolesUpdate
from app.repositories import user_repository, role_repository

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return user_repository.get_all(db)

@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = user_repository.get_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_repository.create(db, user)

@router.put("/{id}", response_model=UserResponse)
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    updated = user_repository.update(db, id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{id}", status_code=204)
def delete_user(id: int, db: Session = Depends(get_db)):
    deleted = user_repository.delete(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/{id}/roles", response_model=UserResponse)
def update_user_roles(id: int, body: UserRolesUpdate, db: Session = Depends(get_db)):
    unique_role_ids = list(set(body.role_ids))
    roles = role_repository.get_by_ids(db, unique_role_ids)

    if len(roles) != len(unique_role_ids):
        found_ids = {role.id for role in roles}
        missing = [rid for rid in unique_role_ids if rid not in found_ids]
        raise HTTPException(status_code=404, detail=f"Roles not found: {missing}")

    updated = user_repository.update_roles(db, id, roles)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

