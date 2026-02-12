from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, SessionLocal, Base
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import all models before creating tables (required for Base.metadata.create_all)
from app.models import User, Company, Category, PriceItem, Estimate, EstimateRoom, EstimateItem

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
