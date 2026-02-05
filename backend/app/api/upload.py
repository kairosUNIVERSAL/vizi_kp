"""Logo upload endpoint for company branding."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path

from app.api.deps import get_current_active_user, get_db
from app.models import User

router = APIRouter()

UPLOAD_DIR = Path("/app/uploads/logos")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload company logo."""
    if not current_user.company:
        raise HTTPException(status_code=400, detail="Company not found")
    
    # Validate file extension
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    # Create upload directory if not exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Delete old logo if exists
    if current_user.company.logo_path:
        old_path = Path(current_user.company.logo_path)
        if old_path.exists():
            old_path.unlink()
    
    # Save new file
    filename = f"{current_user.company.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # Update company
    current_user.company.logo_path = str(filepath)
    db.commit()
    
    return {"logo_path": str(filepath), "filename": filename}


@router.delete("/logo")
def delete_logo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete company logo."""
    if not current_user.company:
        raise HTTPException(status_code=400, detail="Company not found")
    
    if current_user.company.logo_path:
        filepath = Path(current_user.company.logo_path)
        if filepath.exists():
            filepath.unlink()
        
        current_user.company.logo_path = None
        db.commit()
    
    return {"status": "deleted"}


@router.get("/logo/{filename}")
def get_logo(filename: str):
    """Serve logo file."""
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Logo not found")
    
    return FileResponse(filepath)
