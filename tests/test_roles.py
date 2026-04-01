from tests.conftest import auth_headers

class TestGetRoles:
    def test_get_roles_authenticated(self, client, user_token):
        response = client.get("/roles", headers=auth_headers(user_token))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        role_names = [r["name"] for r in data]
        assert "User" in role_names
        assert "Editor" in role_names
        assert "Administrator" in role_names

    def test_get_roles_unauthenticated(self, client):
        response = client.get("/roles")
        assert response.status_code == 401

    def test_roles_have_correct_fields(self, client, user_token):
        response = client.get("/roles", headers=auth_headers(user_token))
        assert response.status_code == 200
        for role in response.json():
            assert "id" in role
            assert "name" in role
