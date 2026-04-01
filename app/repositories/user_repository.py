from sqlalchemy.orm import Session, selectinload
from app.models.user import User
from app.models.role import Role
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import hash_password

def _query_with_roles(db: Session):
    return db.query(User).options(selectinload(User.roles))

def get_all(db: Session, limit: int = 10, offset: int = 0) -> list[User]:
    return _query_with_roles(db).offset(offset).limit(limit).all()

def get_by_id(db: Session, user_id: int) -> User | None:
    return _query_with_roles(db).filter(User.id == user_id).first()

def get_by_username(db: Session, username: str) -> User | None:
    return _query_with_roles(db).filter(User.username == username).first()

def search(db: Session, query: str, limit: int = 10, offset: int = 0) -> list[User]:
    q = f"%{query}%"
    return _query_with_roles(db).filter(
        User.username.ilike(q) |
        User.firstName.ilike(q) |
        User.lastName.ilike(q) |
        User.email.ilike(q)
    ).offset(offset).limit(limit).all()

def create(db: Session, user: UserCreate) -> User:
    data = user.model_dump()
    data["password"] = hash_password(data["password"])
    default_role = db.query(Role).filter(Role.name == "User").first()
    db_user = User(**data)
    if default_role:
        db_user.roles = [default_role]
    db.add(db_user)
    db.commit()
    return get_by_id(db, db_user.id)

def update(db: Session, user_id: int, user: UserUpdate) -> User | None:
    db_user = get_by_id(db, user_id)
    if not db_user:
        return None
    for key, value in user.model_dump().items():
        setattr(db_user, key, value)
    db.commit()
    return get_by_id(db, user_id)

def delete(db: Session, user_id: int) -> User | None:
    db_user = get_by_id(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

def update_roles(db: Session, user_id: int, roles: list[Role]) -> User | None:
    db_user = get_by_id(db, user_id)
    if not db_user:
        return None
    db_user.roles = roles
    db.commit()
    return get_by_id(db, user_id)
