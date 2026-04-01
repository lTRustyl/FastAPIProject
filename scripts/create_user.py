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
    Base.metadata.create_all(bind=engine)
    seed_roles()

    db = SessionLocal()
    try:
        print("=== Create new user ===")
        username = input("Username: ").strip()

        if db.query(User).filter(User.username == username).first():
            print(f"Error: username '{username}' already exists")
            return

        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        phone = input("Phone (+380991234567): ").strip()
        email = input("Email: ").strip()
        password = input("Password (min 6 chars): ").strip()
        birthday_str = input("Birthday (YYYY-MM-DD): ").strip()

        try:
            birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
        except ValueError:
            print("Error: invalid date format. Use YYYY-MM-DD")
            return

        roles = db.query(Role).all()
        print("\nAvailable roles:")
        for role in roles:
            print(f"  {role.id}. {role.name}")

        role_ids_input = input("Enter role IDs (comma-separated, e.g. 1,2): ").strip()
        try:
            role_ids = [int(rid.strip()) for rid in role_ids_input.split(",")]
        except ValueError:
            print("Error: invalid role IDs")
            return

        selected_roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        if len(selected_roles) != len(role_ids):
            print("Error: one or more role IDs not found")
            return

        user = User(
            username=username,
            firstName=first_name,
            lastName=last_name,
            phone=phone,
            email=email,
            password=hash_password(password),
            birthday=birthday,
            createdAt=datetime.utcnow(),
            roles=selected_roles,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        role_names = [r.name for r in user.roles]
        print(f"\nUser '{username}' created successfully with roles: {role_names}")

    finally:
        db.close()
