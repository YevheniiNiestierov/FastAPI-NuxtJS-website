import os
from app.sqlite.database import SessionLocal, engine, Base
from app.users.models import User
from app.users.hashing import get_password_hash

def create_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "jhgMvjhgbyhb11@!")

        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print("Admin already exists. Deleting old admin...")
            db.delete(existing_admin)
            db.commit()

        print(f"Current users in database: {db.query(User).count()}")

        hashed_password = get_password_hash(admin_password)
        print(f"[create_admin] Generated Argon2 hash: {hashed_password}")

        admin = User(
            username=admin_username,
            email=admin_email,
            password=hashed_password,
            role=1,
            is_admin=True
        )

        db.add(admin)
        db.flush()
        print(f"Admin user flushed with ID: {admin.id}")
        db.commit()
        print("Transaction committed!")
        print(f"Users after commit: {db.query(User).count()}")
        print(f"Database URL: {engine.url}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
