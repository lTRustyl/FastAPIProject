from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.article_schema import ArticleCreate, ArticleUpdate, ArticleResponse
from app.models.user import User
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["Articles"])

@router.get(
    "",
    response_model=list[ArticleResponse],
    summary="List all articles",
    description="Returns a paginated list of articles. Optionally filter by publication status.",
)
def get_articles(
        limit: int = Query(10, ge=1, le=100, description="Number of articles to return (1–100)"),
        offset: int = Query(0, ge=0, description="Number of articles to skip"),
        status: Optional[bool] = Query(None, description="Filter by status: `true`=published, `false`=draft"),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return article_service.read_all(db, limit=limit, offset=offset, status=status)

@router.get(
    "/search",
    response_model=list[ArticleResponse],
    summary="Search articles",
    description="Search articles by title or description. Case-insensitive. Optionally filter by status.",
)
def search_articles(
        q: str = Query(min_length=1, description="Search query string"),
        limit: int = Query(10, ge=1, le=100, description="Number of results to return (1–100)"),
        offset: int = Query(0, ge=0, description="Number of results to skip"),
        status: Optional[bool] = Query(None, description="Filter by status: `true`=published, `false`=draft"),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return article_service.search(db, q, limit=limit, offset=offset, status=status)

@router.get(
    "/user/{user_id}",
    response_model=list[ArticleResponse],
    summary="Get articles by user",
    description="Returns all articles created by a specific user. Optionally filter by status.",
)
def get_articles_by_user(
        user_id: int,
        limit: int = Query(10, ge=1, le=100, description="Number of articles to return (1–100)"),
        offset: int = Query(0, ge=0, description="Number of articles to skip"),
        status: Optional[bool] = Query(None, description="Filter by status: `true`=published, `false`=draft"),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return article_service.read_by_user(db, user_id, limit=limit, offset=offset, status=status)

@router.get(
    "/{id}",
    response_model=ArticleResponse,
    summary="Get article by ID",
    description="Returns a single article by its ID.",
)
def get_article(
        id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
):
    return article_service.read_by_id(db, id)

@router.post(
    "",
    response_model=ArticleResponse,
    status_code=201,
    summary="Create article",
    description="""
Create a new article.

- **Regular users** can only create articles assigned to themselves (`user_id` must match their own ID)
- **Editors** and **Administrators** can create articles for any user

If `publication_time` is not provided, it defaults to the current timestamp.
    """,
)
def create_article(
        article: ArticleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return article_service.create(db, article, current_user)

@router.put(
    "/{id}",
    response_model=ArticleResponse,
    summary="Update article",
    description="""
Update an existing article's title, description, and status.

- **Regular users** can only update their own articles
- **Editors** and **Administrators** can update any article

Note: `publication_time` and `user_id` cannot be changed after creation.
    """,
)
def update_article(
        id: int,
        article: ArticleUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return article_service.update(db, id, article, current_user)

@router.delete(
    "/{id}",
    status_code=204,
    summary="Delete article",
    description="""
Permanently delete an article.

- **Regular users** can only delete their own articles
- **Administrators** can delete any article
- **Editors** cannot delete articles
    """,
)
def delete_article(
        id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    article_service.delete(db, id, current_user)
