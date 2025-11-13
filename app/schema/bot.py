from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PDFQuestionResponse(BaseModel):
    question: str
    answer: str
    pdf_filename: str
    extracted_text_length: int
    processing_time: float
    timestamp: datetime
    
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None