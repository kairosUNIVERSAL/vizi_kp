from sqlalchemy.orm import Session
from app.models import User, Company
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def register_user(self, db: Session, user_in: UserRegister):
        # Check if email exists
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create default company for user
        company = Company(user_id=user.id)
        db.add(company)
        db.commit()
        
        return user

    def authenticate_user(self, db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    def create_tokens(self, user_id: int):
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600 # Should match config
        }

auth_service = AuthService()
