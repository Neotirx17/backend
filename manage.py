import sys
from sqlmodel import SQLModel, Session, select
from app.db import engine
from app import models  # ensure models imported
from app.seed import seed_db
from app.security import get_password_hash

USAGE = """
Usage:
  python backend/manage.py reset   # drop all, create all, seed
  python backend/manage.py reset_empty  # drop all, create all (no seed)
  python backend/manage.py drop    # drop all tables
  python backend/manage.py create  # create all tables
  python backend/manage.py seed    # seed initial data (if empty)
  python backend/manage.py add_admin [username] [password] [name]  # create or update admin user
"""

def drop_all():
    SQLModel.metadata.drop_all(engine)
    print("Dropped all tables")

def create_all():
    SQLModel.metadata.create_all(engine)
    print("Created all tables")

def add_admin_user(username: str, password: str, name: str | None = None):
    name = name or username
    with Session(engine) as session:
        user = session.exec(select(models.User).where(models.User.username == username)).first()
        if user:
            user.role = "admin"
            user.name = name
            if password:
                user.password_hash = get_password_hash(password)
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Updated admin user: {username}")
            return
        user = models.User(
            username=username,
            password_hash=get_password_hash(password),
            role="admin",
            name=name,
        )
        session.add(user)
        session.commit()
        print(f"Created admin user: {username}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "reset":
        drop_all()
        create_all()
        seed_db()
        print("Reset complete.")
    elif cmd == "reset_empty":
        drop_all()
        create_all()
        print("Reset (empty) complete.")
    elif cmd == "drop":
        drop_all()
    elif cmd == "create":
        create_all()
    elif cmd == "seed":
        seed_db()
        print("Seed complete.")
    elif cmd == "add_admin":
        username = sys.argv[2] if len(sys.argv) > 2 else "pavlik"
        password = sys.argv[3] if len(sys.argv) > 3 else "842384"
        name = sys.argv[4] if len(sys.argv) > 4 else username
        add_admin_user(username, password, name)
    else:
        print(USAGE)
        sys.exit(1)
