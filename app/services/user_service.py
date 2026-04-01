from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserUpdate
from app.schemas.role_schema import UserRolesUpdate
from app.repositories import user_repository, role_repository

def read_all(db: Session) -> list[User]:
    return user_repository.get_all(db)

def read_by_id(db: Session, user_id: int) -> User:
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def search(db: Session, query: str) -> list[User]:
    return user_repository.search(db, query)

def read_permissions(db: Session, user_id: int) -> list:
    user = read_by_id(db, user_id)
    return user.roles

def update(db: Session, user_id: int, data: UserUpdate, current_user: User) -> User:
    is_admin = any(r.name == "Administrator" for r in current_user.roles)
    if current_user.id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    updated = user_repository.update(db, user_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

def delete(db: Session, user_id: int) -> None:
    deleted = user_repository.delete(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

def update_roles(db: Session, user_id: int, body: UserRolesUpdate) -> User:
    unique_role_ids = list(set(body.role_ids))
    roles = role_repository.get_by_ids(db, unique_role_ids)
    if len(roles) != len(unique_role_ids):
        found_ids = {role.id for role in roles}
        missing = [rid for rid in unique_role_ids if rid not in found_ids]
        raise HTTPException(status_code=404, detail=f"Roles not found: {missing}")
    updated = user_repository.update_roles(db, user_id, roles)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated
