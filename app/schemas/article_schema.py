from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ArticleCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200, examples=["Getting Started with FastAPI"])
    description: str = Field(min_length=10,
                             examples=["A comprehensive guide to building APIs with FastAPI and SQLAlchemy."])
    user_id: int = Field(examples=[1])
    publication_time: Optional[datetime] = Field(default=None, examples=["2024-01-10T12:00:00"])
    status: bool = Field(default=False, examples=[False])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Getting Started with FastAPI",
                    "description": "A comprehensive guide to building APIs with FastAPI and SQLAlchemy.",
                    "user_id": 1,
                    "status": False,
                }
            ]
        }
    }

class ArticleUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=200, examples=["Updated: Getting Started with FastAPI"])
    description: str = Field(min_length=10, examples=["An updated comprehensive guide to building APIs with FastAPI."])
    status: bool = Field(examples=[True])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated: Getting Started with FastAPI",
                    "description": "An updated comprehensive guide to building APIs with FastAPI.",
                    "status": True,
                }
            ]
        }
    }

class ArticleResponse(BaseModel):
    id: int = Field(examples=[1])
    title: str = Field(examples=["Getting Started with FastAPI"])
    description: str = Field(examples=["A comprehensive guide to building APIs with FastAPI."])
    user_id: int = Field(examples=[1])
    publication_time: datetime = Field(examples=["2024-01-10T12:00:00"])
    status: bool = Field(examples=[True])

    model_config = {"from_attributes": True}
