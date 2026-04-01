import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, engine, Base, seed_roles
from app.models.role import Role, user_roles  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.article import Article  # noqa: F401
from app.core.security import hash_password
from datetime import datetime

def run():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    print("Seeding roles...")
    seed_roles()

    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already has users, skipping seed.")
            return

        roles = {r.name: r for r in db.query(Role).all()}

        # ── Users ──────────────────────────────────────────────
        users_data = [
            {
                "username": "admin",
                "firstName": "Admin",
                "lastName": "System",
                "phone": "+380990000001",
                "email": "admin@example.com",
                "password": hash_password("admin123"),
                "birthday": datetime(1985, 1, 15),
                "roles": [roles["Administrator"]],
            },
            {
                "username": "editor_one",
                "firstName": "Emma",
                "lastName": "Wilson",
                "phone": "+380990000002",
                "email": "emma.wilson@example.com",
                "password": hash_password("editor123"),
                "birthday": datetime(1990, 3, 22),
                "roles": [roles["Editor"]],
            },
            {
                "username": "editor_two",
                "firstName": "Liam",
                "lastName": "Brown",
                "phone": "+380990000003",
                "email": "liam.brown@example.com",
                "password": hash_password("editor123"),
                "birthday": datetime(1988, 7, 10),
                "roles": [roles["Editor"]],
            },
            {
                "username": "user_one",
                "firstName": "Sofia",
                "lastName": "Davis",
                "phone": "+380990000004",
                "email": "sofia.davis@example.com",
                "password": hash_password("user123"),
                "birthday": datetime(1995, 11, 5),
                "roles": [roles["User"]],
            },
            {
                "username": "user_two",
                "firstName": "Noah",
                "lastName": "Martinez",
                "phone": "+380990000005",
                "email": "noah.martinez@example.com",
                "password": hash_password("user123"),
                "birthday": datetime(2000, 6, 18),
                "roles": [roles["User"]],
            },
            {
                "username": "user_three",
                "firstName": "Olivia",
                "lastName": "Taylor",
                "phone": "+380990000006",
                "email": "olivia.taylor@example.com",
                "password": hash_password("user123"),
                "birthday": datetime(1993, 9, 30),
                "roles": [roles["User"]],
            },
        ]

        created_users = []
        for data in users_data:
            user_roles_list = data.pop("roles")
            user = User(**data, createdAt=datetime.utcnow())
            user.roles = user_roles_list
            db.add(user)
            db.flush()
            created_users.append(user)
            print(f"  Created user: {user.username} ({[r.name for r in user.roles]})")

        db.commit()

        # ── Articles ───────────────────────────────────────────
        admin, editor1, editor2, user1, user2, user3 = created_users

        articles_data = [
            {
                "title": "Getting Started with FastAPI",
                "description": "A comprehensive guide to building APIs with FastAPI, SQLAlchemy, and Docker.",
                "user_id": editor1.id,
                "status": True,
                "publication_time": datetime(2024, 1, 10),
            },
            {
                "title": "Understanding JWT Authentication",
                "description": "Deep dive into JSON Web Tokens and best practices for securing FastAPI.",
                "user_id": editor1.id,
                "status": True,
                "publication_time": datetime(2024, 2, 5),
            },
            {
                "title": "SQLAlchemy Relationships Explained",
                "description": "Exploring one-to-many and many-to-many relationships in SQLAlchemy.",
                "user_id": editor2.id,
                "status": True,
                "publication_time": datetime(2024, 3, 15),
            },
            {
                "title": "Docker Compose for Python Projects",
                "description": "How to containerize your FastAPI app with PostgreSQL using Docker Compose.",
                "user_id": editor2.id,
                "status": False,
                "publication_time": datetime(2024, 4, 1),
            },
            {
                "title": "My First Article",
                "description": "This is my very first article on this platform about Python development.",
                "user_id": user1.id,
                "status": True,
                "publication_time": datetime(2024, 5, 20),
            },
            {
                "title": "Tips for Learning Python",
                "description": "Practical tips and resources that helped me learn Python from scratch.",
                "user_id": user2.id,
                "status": True,
                "publication_time": datetime(2024, 6, 8),
            },
            {
                "title": "Draft: API Design Patterns",
                "description": "Notes on REST API design patterns — versioning, pagination, error handling.",
                "user_id": user3.id,
                "status": False,
                "publication_time": datetime(2024, 7, 14),
            },
        ]

        for data in articles_data:
            db.add(Article(**data))
            print(f"  Created article: '{data['title']}'")

        db.commit()

        print("\nSeed completed successfully!")
        print("\nCredentials:")
        print("  admin        / admin123  (Administrator)")
        print("  editor_one   / editor123 (Editor)")
        print("  editor_two   / editor123 (Editor)")
        print("  user_one     / user123   (User)")
        print("  user_two     / user123   (User)")
        print("  user_three   / user123   (User)")

    except Exception as e:
        db.rollback()
        print(f"Error during seed: {e}")
        raise
    finally:
        db.close()
