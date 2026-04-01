from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.schemas.user_schema import UserUpdate, UserResponse
from app.schemas.role_schema import UserRolesUpdate, RoleResponse
from app.models.user import User
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "",
    response_model=list[UserResponse],
    summary="List all users",
    description="Returns a paginated list of all users with their roles. Requires authentication.",
)
def get_users(
        limit: int = Query(10, ge=1, le=100, description="Number of users to return (1–100)"),
        offset: int = Query(0, ge=0, description="Number of users to skip"),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return user_service.read_all(db, limit=limit, offset=offset)

@router.get(
    "/search",
    response_model=list[UserResponse],
    summary="Search users",
    description="Search users by username, first name, last name, or email. Case-insensitive.",
)
def search_users(
        q: str = Query(min_length=1, description="Search query string"),
        limit: int = Query(10, ge=1, le=100, description="Number of results to return (1–100)"),
        offset: int = Query(0, ge=0, description="Number of results to skip"),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return user_service.search(db, q, limit=limit, offset=offset)

@router.get(
    "/{id}/permissions",
    response_model=list[RoleResponse],
    summary="Get user permissions",
    description="Returns the list of roles assigned to a specific user.",
)
def get_user_permissions(
        id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return user_service.read_permissions(db, id)

@router.get(
    "/{id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns a single user by their ID, including assigned roles.",
)
def get_user(
        id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return user_service.read_by_id(db, id)

@router.put(
    "/{id}",
    response_model=UserResponse,
    summary="Update user",
    description="""
Update user profile information.

- **Regular users** can only update their own profile
- **Administrators** can update any user's profile

Note: password and creation date cannot be changed through this endpoint.
    """,
)
def update_user(
        id: int,
        user: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return user_service.update(db, id, user, current_user)

@router.delete(
    "/{id}",
    status_code=204,
    summary="Delete user",
    description="Permanently delete a user and all their articles. **Administrator only.**",
)
def delete_user(
        id: int,
        db: Session = Depends(get_db),
        _: User = Depends(require_roles("Administrator")),
):
    user_service.delete(db, id)

@router.put(
    "/{id}/roles",
    response_model=UserResponse,
    summary="Update user roles",
    description="""
Replace the user's current roles with the provided list.

Provide an array of role IDs. Get available role IDs from `GET /roles`.

**Administrator only.**
    """,
)
def update_user_roles(
        id: int,
        body: UserRolesUpdate,
        db: Session = Depends(get_db),
        _: User = Depends(require_roles("Administrator")),
):
    return user_service.update_roles(db, id, body)
