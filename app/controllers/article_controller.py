from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.article_schema import ArticleCreate, ArticleUpdate, ArticleResponse
from app.models.user import User
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.get("", response_model=list[ArticleResponse])
def get_articles(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        status: Optional[bool] = Query(None, description="Filter by status: true=published, false=draft"),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return article_service.read_all(db, limit=limit, offset=offset, status=status)

@router.get("/search", response_model=list[ArticleResponse])
def search_articles(
        q: str = Query(min_length=1),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        status: Optional[bool] = Query(None, description="Filter by status: true=published, false=draft"),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return article_service.search(db, q, limit=limit, offset=offset, status=status)

@router.get("/user/{user_id}", response_model=list[ArticleResponse])
def get_articles_by_user(
        user_id: int,
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        status: Optional[bool] = Query(None, description="Filter by status: true=published, false=draft"),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return article_service.read_by_user(db, user_id, limit=limit, offset=offset, status=status)

@router.get("/{id}", response_model=ArticleResponse)
def get_article(id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return article_service.read_by_id(db, id)

@router.post("", response_model=ArticleResponse, status_code=201)
def create_article(article: ArticleCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return article_service.create(db, article, current_user)

@router.put("/{id}", response_model=ArticleResponse)
def update_article(id: int, article: ArticleUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return article_service.update(db, id, article, current_user)

@router.delete("/{id}", status_code=204)
def delete_article(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    article_service.delete(db, id, current_user)
