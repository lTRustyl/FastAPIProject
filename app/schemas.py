from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    firstName: str
    lastName: str
    phone: str
    email: EmailStr
    birthday: datetime

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    createdAt: datetime

    class Config:
        from_attributes = True
