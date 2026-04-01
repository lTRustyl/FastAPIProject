import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.models.role import Role, user_roles  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.article import Article  # noqa: F401

from app.main import app

app.dependency_overrides[get_db] = override_get_db

from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    for name in ["User", "Editor", "Administrator"]:
        if not db.query(Role).filter(Role.name == name).first():
            db.add(Role(name=name))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    return TestClient(app)

def _create_user(db, username, password, role_name, email=None):
    role = db.query(Role).filter(Role.name == role_name).first()
    user = User(
        username=username,
        firstName="Test",
        lastName="User",
        phone="+380991234567",
        email=email or f"{username}@test.com",
        password=hash_password(password),
        birthday=datetime(1990, 1, 1),
        createdAt=datetime.utcnow(),
        roles=[role],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def _get_token(client, username, password):
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    return response.json()["access_token"]

@pytest.fixture
def admin_user(db):
    return _create_user(db, "admin", "admin123", "Administrator")

@pytest.fixture
def editor_user(db):
    return _create_user(db, "editor", "editor123", "Editor")

@pytest.fixture
def regular_user(db):
    return _create_user(db, "user_one", "user123", "User")

@pytest.fixture
def second_user(db):
    return _create_user(db, "user_two", "user123", "User", email="user_two@test.com")

@pytest.fixture
def admin_token(client, admin_user):
    return _get_token(client, "admin", "admin123")

@pytest.fixture
def editor_token(client, editor_user):
    return _get_token(client, "editor", "editor123")

@pytest.fixture
def user_token(client, regular_user):
    return _get_token(client, "user_one", "user123")

@pytest.fixture
def second_user_token(client, second_user):
    return _get_token(client, "user_two", "user123")

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
