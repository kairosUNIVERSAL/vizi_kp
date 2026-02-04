from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Any
import logging

from app.api.deps import get_current_active_user
from app.database import get_db
from app.services import pdf_service, estimate_service
from app.schemas.pdf import PdfGenerateRequest
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate")
def generate_pdf(
    request: PdfGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    try:
        estimate = estimate_service.get_estimate(db, request.estimate_id)
        if not estimate:
            raise HTTPException(status_code=404, detail="Estimate not found")
        
        if not current_user.company:
            raise HTTPException(status_code=400, detail="User has no company")
            
        if estimate.company_id != current_user.company.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        logger.info(f"Generating PDF for estimate {estimate.id}")
        pdf_content = pdf_service.generate(estimate, current_user.company)
        
        # Sanitize filename
        from urllib.parse import quote
        client_name = estimate.client_name.replace('"', '').replace("'", "").replace("/", "_")
        filename = f"KP_{estimate.id}_{client_name}.pdf"
        encoded_filename = quote(filename)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.get("/preview/{estimate_id}")
def preview_pdf(
    estimate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Generate PDF for inline preview (no download)"""
    try:
        estimate = estimate_service.get_estimate(db, estimate_id)
        if not estimate:
            raise HTTPException(status_code=404, detail="Estimate not found")
        
        if not current_user.company:
            raise HTTPException(status_code=400, detail="User has no company")
            
        if estimate.company_id != current_user.company.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        pdf_content = pdf_service.generate(estimate, current_user.company)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline",  # For preview, not download
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error previewing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")
