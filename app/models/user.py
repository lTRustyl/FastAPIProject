from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.models.role import user_roles

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    firstName = Column(String)
    lastName = Column(String)
    phone = Column(String)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    birthday = Column(DateTime)
    createdAt = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Role", secondary=user_roles, lazy="selectin")
    articles = relationship("Article", back_populates="user", lazy="selectin")
