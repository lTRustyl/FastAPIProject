from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    phone = Column(String)
    email = Column(String)
    birthday = Column(DateTime)
    createdAt = Column(DateTime, default=datetime.utcnow)
