from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import User
from app.schemas.auth import TokenData
from app.core.exceptions import CredentialsException, InactiveUserException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise CredentialsException()
        token_data = TokenData(user_id=int(user_id))
    except (JWTError, ValidationError):
        raise CredentialsException()
        
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise CredentialsException()
    if not user.is_active:
        raise InactiveUserException()
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user
