from sqlalchemy.orm import Session
from app.models.article import Article
from app.schemas.article_schema import ArticleCreate, ArticleUpdate
from datetime import datetime

def get_all(db: Session, limit: int = 10, offset: int = 0, status: bool | None = None) -> list[Article]:
    q = db.query(Article)
    if status is not None:
        q = q.filter(Article.status == status)
    return q.offset(offset).limit(limit).all()

def get_by_id(db: Session, article_id: int) -> Article | None:
    return db.query(Article).filter(Article.id == article_id).first()

def get_by_user(db: Session, user_id: int, limit: int = 10, offset: int = 0, status: bool | None = None) -> list[
    Article]:
    q = db.query(Article).filter(Article.user_id == user_id)
    if status is not None:
        q = q.filter(Article.status == status)
    return q.offset(offset).limit(limit).all()

def search(db: Session, query: str, limit: int = 10, offset: int = 0, status: bool | None = None) -> list[Article]:
    q = f"%{query}%"
    result = db.query(Article).filter(
        Article.title.ilike(q) |
        Article.description.ilike(q)
    )
    if status is not None:
        result = result.filter(Article.status == status)
    return result.offset(offset).limit(limit).all()

def create(db: Session, article: ArticleCreate) -> Article:
    data = article.model_dump()
    if not data.get("publication_time"):
        data["publication_time"] = datetime.utcnow()
    db_article = Article(**data)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update(db: Session, article_id: int, article: ArticleUpdate) -> Article | None:
    db_article = get_by_id(db, article_id)
    if not db_article:
        return None
    for key, value in article.model_dump().items():
        setattr(db_article, key, value)
    db.commit()
    db.refresh(db_article)
    return db_article

def delete(db: Session, article_id: int) -> Article | None:
    db_article = get_by_id(db, article_id)
    if not db_article:
        return None
    db.delete(db_article)
    db.commit()
    return db_article
