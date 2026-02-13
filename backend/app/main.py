import logging
import sys
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.services.activity_log_service import activity_log_service

LOG_DIR = Path("logs")
log_handlers = [logging.StreamHandler(sys.stdout)]
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_handlers.append(logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"))
except OSError:
    # Keep API running even if filesystem is read-only.
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=log_handlers,
)
logger = logging.getLogger(__name__)

# Import all models before creating tables (required for Base.metadata.create_all)
from app.models import (
    ActivityLog,
    Category,
    Company,
    Estimate,
    EstimateItem,
    EstimateRoom,
    PriceItem,
    User,
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS - configure before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _extract_user_id(authorization_header: Optional[str]) -> Optional[int]:
    if not authorization_header:
        return None

    parts = authorization_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None

    subject = payload.get("sub")
    if subject is None:
        return None

    try:
        return int(subject)
    except (TypeError, ValueError):
        return None


@app.middleware("http")
async def audit_requests(request: Request, call_next):
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        if request.url.path.startswith("/api"):
            duration_ms = int((time.perf_counter() - start) * 1000)
            user_id = _extract_user_id(request.headers.get("authorization"))
            query = request.url.query or None

            activity_log_service.safe_log(
                action="api_request",
                user_id=user_id,
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code if response else 500,
                duration_ms=duration_ms,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                details={"query": query} if query else None,
            )


# Import routers after app is created
from app.api import auth, users, price, estimates, pdf, transcribe, admin, upload

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(price.router, prefix="/api/price", tags=["Price"])
app.include_router(estimates.router, prefix="/api/estimates", tags=["Estimates"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF"])
app.include_router(transcribe.router, prefix="/api", tags=["Transcribe"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])

@app.on_event("startup")
def on_startup():
    from app.initial_data import init_db
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Ceiling KP Generator API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "app_name": settings.APP_NAME}
