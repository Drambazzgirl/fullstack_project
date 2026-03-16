from database import SessionLocal
from models import User
from utils import hash_password

def seed_admins():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.role == 'cm_admin').first():
            print('Admins already exist, skipping seed')
            return

        cm = User(name='CM Admin', username='cmadmin',
                  password_hash=hash_password('admin123'), role='cm_admin')
        ca = User(name='Chennai Admin', username='cadmin',
                  password_hash=hash_password('admin123'), role='c_admin', district='Chennai')
        db.add(cm)
        db.add(ca)
        db.commit()
        print('Admins created!')
    finally:
        db.close()
        