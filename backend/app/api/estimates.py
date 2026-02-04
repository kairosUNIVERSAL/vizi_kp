from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Any, List

from app.api.deps import get_current_active_user
from app.database import get_db
from app.services import estimate_service, ai_parser_service
from app.schemas.estimate import (
    EstimateCreate, EstimateResponse, EstimateParseResponse
)
from app.models import User

router = APIRouter()

@router.get("/", response_model=List[EstimateResponse])
def list_estimates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List all estimates for the current user's company."""
    if not current_user.company:
        raise HTTPException(status_code=400, detail="User has no company")
    return estimate_service.list_estimates(db, current_user.company.id)

@router.post("/", response_model=EstimateResponse, status_code=201)
def create_estimate(
    estimate_in: EstimateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if not current_user.company:
        raise HTTPException(status_code=400, detail="User has no company")
    return estimate_service.create_estimate(db, current_user.company.id, estimate_in)

@router.get("/{estimate_id}", response_model=EstimateResponse)
def get_estimate(
    estimate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    estimate = estimate_service.get_estimate(db, estimate_id)
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    if estimate.company_id != current_user.company.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return estimate

@router.post("/parse", response_model=EstimateParseResponse)
def parse_transcript(
    transcript: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if not current_user.company:
         raise HTTPException(status_code=400, detail="User has no company")
         
    return ai_parser_service.parse_transcript(db, current_user.company.id, transcript)
