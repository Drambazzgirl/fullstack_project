# seed.py - Run this ONCE to create admin accounts
# Usage: python seed.py

from database import SessionLocal, engine, Base
from models import User
from utils import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

def create_admin(name, username, password, role):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"⚠️  {role} '{username}' already exists")
        return
    admin = User(
        name          = name,
        username      = username,
        password_hash = hash_password(password),
        role          = role
    )
    db.add(admin)
    db.commit()
    print(f"Created {role}: username={username}, password={password}")

# Department Admin
create_admin(
    name     = "Department Admin",
    username = "cadmin",
    password = "cadmin@123",
    role     = "c_admin"
)

# CM Admin
create_admin(
    name     = "Chief Minister Admin",
    username = "cmadmin",
    password = "cmadmin@123",
    role     = "cm_admin"
)

db.close()
print("\n🎉 Seed complete! Admin accounts ready.")
print("c_admin  → username: cadmin   | password: cadmin@123")
print("cm_admin → username: cmadmin  | password: cmadmin@123")
