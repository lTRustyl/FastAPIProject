from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from app.schemas.role_schema import RoleResponse
import re

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=30, examples=["john_doe"])
    firstName: str = Field(min_length=1, max_length=50, examples=["John"])
    lastName: str = Field(min_length=1, max_length=50, examples=["Doe"])
    phone: str = Field(min_length=10, max_length=15, examples=["+380991234567"])
    email: EmailStr = Field(examples=["john.doe@example.com"])
    birthday: datetime = Field(examples=["1990-05-15T00:00:00"])

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username may only contain letters, digits, and underscores")
        return v

    @field_validator("firstName", "lastName")
    @classmethod
    def name_letters_only(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Zа-яА-ЯіІїЇєЄёЁ\s\-']+$", v):
            raise ValueError("Name may only contain letters, spaces, hyphens, and apostrophes")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str) -> str:
        if not re.match(r"^\+?[0-9]{10,14}$", v):
            raise ValueError("Invalid phone number format (e.g. +380991234567)")
        return v

    @field_validator("birthday")
    @classmethod
    def birthday_not_future_and_min_age(cls, v: datetime) -> datetime:
        v_naive = v.replace(tzinfo=None) if v.tzinfo else v
        now = datetime.utcnow()
        age = (now - v_naive).days // 365
        if v_naive > now:
            raise ValueError("Birthday cannot be in the future")
        if age < 12:
            raise ValueError("User must be at least 12 years old")
        if age > 120:
            raise ValueError("Invalid birthday date")
        return v_naive

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100, examples=["securepassword123"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe",
                    "firstName": "John",
                    "lastName": "Doe",
                    "phone": "+380991234567",
                    "email": "john.doe@example.com",
                    "birthday": "1990-05-15T00:00:00",
                    "password": "securepassword123",
                }
            ]
        }
    }


class UserUpdate(UserBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe",
                    "firstName": "John",
                    "lastName": "Smith",
                    "phone": "+380991234567",
                    "email": "john.smith@example.com",
                    "birthday": "1990-05-15T00:00:00",
                }
            ]
        }
    }

class UserResponse(UserBase):
    id: int = Field(examples=[1])
    createdAt: datetime = Field(examples=["2024-01-10T12:00:00"])
    roles: list[RoleResponse] = []

    model_config = {"from_attributes": True}
