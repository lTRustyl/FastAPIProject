from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ArticleCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    user_id: int
    publication_time: Optional[datetime] = None
    status: bool = False

class ArticleUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    publication_time: Optional[datetime] = None
    status: bool

class ArticleResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
    publication_time: datetime
    status: bool

    class Config:
        from_attributes = True
