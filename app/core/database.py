from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_roles():
    from app.models.role import Role
    db = SessionLocal()
    try:
        default_roles = ["User", "Editor", "Administrator"]
        for name in default_roles:
            if not db.query(Role).filter(Role.name == name).first():
                db.add(Role(name=name))
        db.commit()
    finally:
        db.close()
