import pytest
from app.models.article import Article
from tests.conftest import auth_headers

def _create_article(db, user_id, title="Test Article", status=True):
    from datetime import datetime
    article = Article(
        title=title,
        description="Test description for the article",
        user_id=user_id,
        status=status,
        publication_time=datetime.utcnow(),
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

class TestGetArticles:
    def test_get_articles_authenticated(self, client, user_token, regular_user, db):
        _create_article(db, regular_user.id)
        response = client.get("/articles", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_articles_unauthenticated(self, client):
        response = client.get("/articles")
        assert response.status_code == 401

    def test_get_articles_with_limit(self, client, user_token, regular_user, db):
        _create_article(db, regular_user.id, "Article 1")
        _create_article(db, regular_user.id, "Article 2")
        _create_article(db, regular_user.id, "Article 3")
        response = client.get("/articles?limit=2", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert len(response.json()) <= 2

    def test_get_articles_with_offset(self, client, user_token, regular_user, db):
        for i in range(3):
            _create_article(db, regular_user.id, f"Article {i}")
        all_resp = client.get("/articles?limit=100", headers=auth_headers(user_token)).json()
        offset_resp = client.get("/articles?limit=100&offset=1", headers=auth_headers(user_token)).json()
        assert len(offset_resp) == len(all_resp) - 1

    def test_get_articles_filter_by_status_published(self, client, user_token, regular_user, db):
        _create_article(db, regular_user.id, "Published", status=True)
        _create_article(db, regular_user.id, "Draft", status=False)
        response = client.get("/articles?status=true", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert all(a["status"] is True for a in response.json())

    def test_get_articles_filter_by_status_draft(self, client, user_token, regular_user, db):
        _create_article(db, regular_user.id, "Published", status=True)
        _create_article(db, regular_user.id, "Draft", status=False)
        response = client.get("/articles?status=false", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert all(a["status"] is False for a in response.json())

class TestGetArticle:
    def test_get_article_by_id(self, client, user_token, regular_user, db):
        article = _create_article(db, regular_user.id)
        response = client.get(f"/articles/{article.id}", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert response.json()["title"] == "Test Article"

    def test_get_article_not_found(self, client, user_token):
        response = client.get("/articles/99999", headers=auth_headers(user_token))
        assert response.status_code == 404

    def test_get_articles_by_user(self, client, user_token, regular_user, second_user, db):
        _create_article(db, regular_user.id, "User One Article")
        _create_article(db, second_user.id, "User Two Article")
        response = client.get(f"/articles/user/{regular_user.id}", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert all(a["user_id"] == regular_user.id for a in response.json())

    def test_get_articles_by_nonexistent_user(self, client, user_token):
        response = client.get("/articles/user/99999", headers=auth_headers(user_token))
        assert response.status_code == 404

class TestCreateArticle:
    def test_create_own_article(self, client, user_token, regular_user):
        response = client.post(
            "/articles",
            headers=auth_headers(user_token),
            json={
                "title": "My New Article",
                "description": "Description of my new article",
                "user_id": regular_user.id,
                "status": False,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My New Article"
        assert data["user_id"] == regular_user.id

    def test_create_article_for_other_user_as_regular(self, client, user_token, second_user):
        response = client.post(
            "/articles",
            headers=auth_headers(user_token),
            json={
                "title": "Fake Article",
                "description": "Trying to post as another user",
                "user_id": second_user.id,
                "status": False,
            },
        )
        assert response.status_code == 403

    def test_create_article_for_any_user_as_admin(self, client, admin_token, regular_user):
        response = client.post(
            "/articles",
            headers=auth_headers(admin_token),
            json={
                "title": "Admin Article",
                "description": "Article created by admin for user",
                "user_id": regular_user.id,
                "status": True,
            },
        )
        assert response.status_code == 201

    def test_create_article_for_any_user_as_editor(self, client, editor_token, regular_user):
        response = client.post(
            "/articles",
            headers=auth_headers(editor_token),
            json={
                "title": "Editor Article",
                "description": "Article created by editor for user",
                "user_id": regular_user.id,
                "status": True,
            },
        )
        assert response.status_code == 201

    def test_create_article_nonexistent_user(self, client, admin_token):
        response = client.post(
            "/articles",
            headers=auth_headers(admin_token),
            json={
                "title": "Ghost Article",
                "description": "Article for nonexistent user",
                "user_id": 99999,
                "status": False,
            },
        )
        assert response.status_code == 404

    def test_create_article_missing_fields(self, client, user_token):
        response = client.post(
            "/articles",
            headers=auth_headers(user_token),
            json={"title": "No description"},
        )
        assert response.status_code == 422

class TestUpdateArticle:
    def test_update_own_article(self, client, user_token, regular_user, db):
        article = _create_article(db, regular_user.id)
        response = client.put(
            f"/articles/{article.id}",
            headers=auth_headers(user_token),
            json={
                "title": "Updated Title",
                "description": "Updated description",
                "status": True,
            },
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_update_other_user_article_as_regular(self, client, second_user_token, regular_user, db):
        article = _create_article(db, regular_user.id)
        response = client.put(
            f"/articles/{article.id}",
            headers=auth_headers(second_user_token),
            json={
                "title": "Hacked Title",
                "description": "Should not work",
                "status": False,
            },
        )
        assert response.status_code == 403

    def test_update_any_article_as_editor(self, client, editor_token, regular_user, db):
        article = _create_article(db, regular_user.id)
        response = client.put(
            f"/articles/{article.id}",
            headers=auth_headers(editor_token),
            json={
                "title": "Editor Updated",
                "description": "Editor can update any article",
                "status": True,
            },
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Editor Updated"

    def test_update_any_article_as_admin(self, client, admin_token, regular_user, db):
        article = _create_article(db, regular_user.id)
        response = client.put(
            f"/articles/{article.id}",
            headers=auth_headers(admin_token),
            json={
                "title": "Admin Updated",
                "description": "Admin can update any article",
                "status": True,
            },
        )
        assert response.status_code == 200

    def test_update_nonexistent_article(self, client, user_token):
        response = client.put(
            "/articles/99999",
            headers=auth_headers(user_token),
            json={
                "title": "Ghost",
                "description": "Does not exist",
                "status": False,
            },
        )
        assert response.status_code == 404

class TestDeleteArticle:
    def test_delete_own_article(self, client, user_token, regular_user, db):
        article = _create_article(db, regular_user.id)
        response = client.delete(f"/articles/{article.id}", headers=auth_headers(user_token))
        assert response.status_code == 204

    def test_delete_other_user_article_as_regular(self, client, second_user_token, regular_user, db):
        article = _create_article(db, regular_user.id)
        response = client.delete(f"/articles/{article.id}", headers=auth_headers(second_user_token))
        assert response.status_code == 403

    def test_delete_any_article_as_admin(self, client, admin_token, regular_user, db):
        article = _create_article(db, regular_user.id)
        response = client.delete(f"/articles/{article.id}", headers=auth_headers(admin_token))
        assert response.status_code == 204

    def test_delete_nonexistent_article(self, client, user_token):
        response = client.delete("/articles/99999", headers=auth_headers(user_token))
        assert response.status_code == 404

class TestSearchArticles:
    def test_search_articles(self, client, user_token, regular_user, db):
        _create_article(db, regular_user.id, "FastAPI Guide")
        response = client.get("/articles/search?q=FastAPI", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert any("FastAPI" in a["title"] for a in response.json())

    def test_search_articles_no_results(self, client, user_token):
        response = client.get("/articles/search?q=zzznoresults", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert response.json() == []

    def test_search_articles_with_status_filter(self, client, user_token, regular_user, db):
        _create_article(db, regular_user.id, "Published FastAPI", status=True)
        _create_article(db, regular_user.id, "Draft FastAPI", status=False)
        response = client.get("/articles/search?q=FastAPI&status=true", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert all(a["status"] is True for a in response.json())

    def test_search_articles_with_limit(self, client, user_token, regular_user, db):
        for i in range(5):
            _create_article(db, regular_user.id, f"Article {i}")
        response = client.get("/articles/search?q=Article&limit=2", headers=auth_headers(user_token))
        assert response.status_code == 200
        assert len(response.json()) <= 2
