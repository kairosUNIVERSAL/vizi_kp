from pydantic import BaseModel

class PdfGenerateRequest(BaseModel):
    estimate_id: int

class PdfPreviewResponse(BaseModel):
    pdf_base64: str
    filename: str
