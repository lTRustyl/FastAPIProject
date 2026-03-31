from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.article_schema import ArticleCreate, ArticleUpdate, ArticleResponse
from app.repositories import article_repository, user_repository

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.get("", response_model=list[ArticleResponse])
def get_articles(db: Session = Depends(get_db)):
    return article_repository.get_all(db)

@router.get("/{id}", response_model=ArticleResponse)
def get_article(id: int, db: Session = Depends(get_db)):
    article = article_repository.get_by_id(db, id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.get("/user/{user_id}", response_model=list[ArticleResponse])
def get_articles_by_user(user_id: int, db: Session = Depends(get_db)):
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return article_repository.get_by_user(db, user_id)

@router.post("", response_model=ArticleResponse, status_code=201)
def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    user = user_repository.get_by_id(db, article.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return article_repository.create(db, article)

@router.put("/{id}", response_model=ArticleResponse)
def update_article(id: int, article: ArticleUpdate, db: Session = Depends(get_db)):
    updated = article_repository.update(db, id, article)
    if not updated:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated

@router.delete("/{id}", status_code=204)
def delete_article(id: int, db: Session = Depends(get_db)):
    deleted = article_repository.delete(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
