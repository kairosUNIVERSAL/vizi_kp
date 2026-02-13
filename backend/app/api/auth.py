from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from app.database import get_db
from app.services import auth_service
from app.services.activity_log_service import activity_log_service
from app.schemas.auth import UserRegister, Token
from app.schemas.user import UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    """
    user = auth_service.register_user(db, user_in)
    activity_log_service.safe_log(
        action="register_success",
        user=user,
        method="POST",
        endpoint="/api/auth/register",
        status_code=status.HTTP_201_CREATED,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return user

@router.post("/login", response_model=Token)
def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        activity_log_service.safe_log(
            action="login_failed",
            user_email=form_data.username,
            method="POST",
            endpoint="/api/auth/login",
            status_code=status.HTTP_400_BAD_REQUEST,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"reason": "incorrect_credentials"},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    activity_log_service.safe_log(
        action="login_success",
        user=user,
        method="POST",
        endpoint="/api/auth/login",
        status_code=status.HTTP_200_OK,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return auth_service.create_tokens(user.id)
