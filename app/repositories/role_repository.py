from sqlalchemy.orm import Session
from app.models.role import Role

def get_all(db: Session) -> list[Role]:
    return db.query(Role).all()

def get_by_id(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()

def get_by_ids(db: Session, role_ids: list[int]) -> list[Role]:
    return db.query(Role).filter(Role.id.in_(role_ids)).all()
