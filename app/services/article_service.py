from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.article import Article
from app.schemas.article_schema import ArticleCreate, ArticleUpdate
from app.repositories import article_repository, user_repository

def _get_user_role_names(user: User) -> set:
    return {r.name for r in user.roles}

def read_all(db: Session) -> list[Article]:
    return article_repository.get_all(db)

def read_by_id(db: Session, article_id: int) -> Article:
    article = article_repository.get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

def read_by_user(db: Session, user_id: int) -> list[Article]:
    if not user_repository.get_by_id(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return article_repository.get_by_user(db, user_id)

def search(db: Session, query: str) -> list[Article]:
    return article_repository.search(db, query)

def create(db: Session, data: ArticleCreate, current_user: User) -> Article:
    roles = _get_user_role_names(current_user)
    is_privileged = "Administrator" in roles or "Editor" in roles
    if not is_privileged and data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create articles for yourself")
    if not user_repository.get_by_id(db, data.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return article_repository.create(db, data)

def update(db: Session, article_id: int, data: ArticleUpdate, current_user: User) -> Article:
    article = read_by_id(db, article_id)
    roles = _get_user_role_names(current_user)
    is_privileged = "Administrator" in roles or "Editor" in roles
    if not is_privileged and article.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own articles")
    return article_repository.update(db, article_id, data)

def delete(db: Session, article_id: int, current_user: User) -> None:
    article = read_by_id(db, article_id)
    roles = _get_user_role_names(current_user)
    if "Administrator" not in roles and article.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    article_repository.delete(db, article_id)