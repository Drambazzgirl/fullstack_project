import os
from database import SessionLocal
from models import User
from utils import hash_password

def seed_admins():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.role == 'cm_admin').first():
            if not os.getenv('RESET_SEED'):
                print('Admins already exist, skipping seed')
                return
            # ✅ Reset - existing admins delete பண்ணி recreate பண்ணு
            db.query(User).filter(User.role.in_(['cm_admin', 'c_admin'])).delete()
            db.commit()

        # CM Admin
        db.add(User(name='CM Admin', username='cmadmin',
                    password_hash=hash_password('admin123'), role='cm_admin'))

        # ✅ All District Admins
        districts = [
            ('Chennai',        'cadmin'),
            ('Chengalpattu',   'cadmin_chengalpattu'),
            ('Kanchipuram',    'cadmin_kanchipuram'),
            ('Vellore',        'cadmin_vellore'),
            ('Ranipet',        'cadmin_ranipet'),
            ('Tirupattur',     'cadmin_tirupattur'),
            ('Tiruvannamalai', 'cadmin_tiruvannamalai'),
            ('Krishnagiri',    'cadmin_krishnagiri'),
            ('Dharmapuri',     'cadmin_dharmapuri'),
            ('Kallakurichi',   'cadmin_kallakurichi'),
            ('Villupuram',     'cadmin_villupuram'),
        ]

        for district, username in districts:
            db.add(User(
                name=f'{district} Admin',
                username=username,
                password_hash=hash_password('admin123'),
                role='c_admin',
                district=district
            ))

        db.commit()
        print('All admins created!')
    finally:
        db.close()