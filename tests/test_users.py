import pytest
from tests.conftest import auth_headers

class TestGetUsers:
    def test_get_users_authenticated(self, client, admin_token, regular_user):
        response = client.get("/users", headers=auth_headers(admin_token))
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_users_unauthenticated(self, client):
        response = client.get("/users")
        assert response.status_code == 401

    def test_get_users_with_limit(self, client, admin_token, regular_user, second_user):
        response = client.get("/users?limit=1", headers=auth_headers(admin_token))
        assert response.status_code == 200
        assert len(response.json()) <= 1

    def test_get_users_with_offset(self, client, admin_token, regular_user, second_user):
        all_users = client.get("/users?limit=100", headers=auth_headers(admin_token)).json()
        offset_users = client.get("/users?limit=100&offset=1", headers=auth_headers(admin_token)).json()
        assert len(offset_users) == len(all_users) - 1

    def test_get_users_invalid_limit(self, client, admin_token):
        response = client.get("/users?limit=0", headers=auth_headers(admin_token))
        assert response.status_code == 422

class TestGetUser:
    def test_get_user_by_id(self, client, admin_token, regular_user):
        response = client.get(f"/users/{regular_user.id}", headers=auth_headers(admin_token))
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "user_one"
        assert "roles" in data
        assert "password" not in data

    def test_get_user_not_found(self, client, admin_token):
        response = client.get("/users/99999", headers=auth_headers(admin_token))
        assert response.status_code == 404

    def test_get_user_unauthenticated(self, client, regular_user):
        response = client.get(f"/users/{regular_user.id}")
        assert response.status_code == 401

class TestUpdateUser:
    def test_update_own_user(self, client, user_token, regular_user):
        response = client.put(
            f"/users/{regular_user.id}",
            headers=auth_headers(user_token),
            json={
                "username": "user_one",
                "firstName": "UpdatedName",
                "lastName": "User",
                "phone": "+380991234567",
                "email": "user_one@test.com",
                "birthday": "1990-01-01T00:00:00",
            },
        )
        assert response.status_code == 200
        assert response.json()["firstName"] == "UpdatedName"

    def test_update_other_user_as_regular(self, client, user_token, second_user):
        response = client.put(
            f"/users/{second_user.id}",
            headers=auth_headers(user_token),
            json={
                "username": "user_two",
                "firstName": "Hacked",
                "lastName": "User",
                "phone": "+380991234568",
                "email": "user_two@test.com",
                "birthday": "1990-01-01T00:00:00",
            },
        )
        assert response.status_code == 403

    def test_update_any_user_as_admin(self, client, admin_token, regular_user):
        response = client.put(
            f"/users/{regular_user.id}",
            headers=auth_headers(admin_token),
            json={
                "username": "user_one",
                "firstName": "AdminUpdated",
                "lastName": "User",
                "phone": "+380991234567",
                "email": "user_one@test.com",
                "birthday": "1990-01-01T00:00:00",
            },
        )
        assert response.status_code == 200
        assert response.json()["firstName"] == "AdminUpdated"

    def test_update_user_not_found(self, client, admin_token):
        response = client.put(
            "/users/99999",
            headers=auth_headers(admin_token),
            json={
                "username": "ghost",
                "firstName": "Ghost",
                "lastName": "User",
                "phone": "+380991234567",
                "email": "ghost@test.com",
                "birthday": "1990-01-01T00:00:00",
            },
        )
        assert response.status_code == 404

class TestDeleteUser:
    def test_delete_user_as_admin(self, client, admin_token, regular_user):
        response = client.delete(f"/users/{regular_user.id}", headers=auth_headers(admin_token))
        assert response.status_code == 204

    def test_delete_user_as_regular(self, client, user_token, regular_user):
        response = client.delete(f"/users/{regular_user.id}", headers=auth_headers(user_token))
        assert response.status_code == 403

    def test_delete_user_not_found(self, client, admin_token):
        response = client.delete("/users/99999", headers=auth_headers(admin_token))
        assert response.status_code == 404

class TestSearchUsers:
    def test_search_users(self, client, admin_token, regular_user):
        response = client.get("/users/search?q=user_one", headers=auth_headers(admin_token))
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(u["username"] == "user_one" for u in data)

    def test_search_users_no_results(self, client, admin_token):
        response = client.get("/users/search?q=zzznoresults", headers=auth_headers(admin_token))
        assert response.status_code == 200
        assert response.json() == []

    def test_search_users_with_limit(self, client, admin_token, regular_user, second_user):
        response = client.get("/users/search?q=user&limit=1", headers=auth_headers(admin_token))
        assert response.status_code == 200
        assert len(response.json()) <= 1

class TestUserPermissions:
    def test_get_permissions(self, client, admin_token, regular_user):
        response = client.get(f"/users/{regular_user.id}/permissions", headers=auth_headers(admin_token))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(r["name"] == "User" for r in data)

    def test_update_roles_as_admin(self, client, admin_token, regular_user, db):
        from app.models.role import Role
        editor_role = db.query(Role).filter(Role.name == "Editor").first()
        response = client.put(
            f"/users/{regular_user.id}/roles",
            headers=auth_headers(admin_token),
            json={"role_ids": [editor_role.id]},
        )
        assert response.status_code == 200
        roles = response.json()["roles"]
        assert any(r["name"] == "Editor" for r in roles)

    def test_update_roles_as_regular(self, client, user_token, regular_user, db):
        from app.models.role import Role
        editor_role = db.query(Role).filter(Role.name == "Editor").first()
        response = client.put(
            f"/users/{regular_user.id}/roles",
            headers=auth_headers(user_token),
            json={"role_ids": [editor_role.id]},
        )
        assert response.status_code == 403
