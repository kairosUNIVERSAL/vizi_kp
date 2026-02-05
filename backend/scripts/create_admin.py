import sys
import os
import argparse

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, Company
from app.services.auth_service import auth_service

def create_admin(email, password):
    db = SessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Error: User with email {email} already exists.")
            return

        # Create user with is_admin=True
        user = auth_service.create_user(db, email, password, is_admin=True)
        print(f"Admin user created successfully: {email}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an admin user.")
    parser.add_argument("--email", required=True, help="Email for the admin user")
    parser.add_argument("--password", required=True, help="Password for the admin user")
    
    args = parser.parse_args()
    create_admin(args.email, args.password)
