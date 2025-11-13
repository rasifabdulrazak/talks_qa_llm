from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
import time
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import User
from app.schema.bot import PDFQuestionResponse
from app.core.utils import PDFExtractor,LLMService
from app.core.config import settings


router = APIRouter()


@router.post("/ask", response_model=PDFQuestionResponse)
async def ask_pdf_question(
    file: UploadFile = File(description="PDF file to analyze"),
    question: str = Form(min_length=5, max_length=500, description="Question about the PDF"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a PDF file and ask a question about its content.
    
    - **file**: PDF file (max 10 MB)
    - **question**: Question about the PDF content
    
    Returns the answer based on the PDF content or "NOT_FOUND" if question is irrelevant.
    """
    start_time = time.time()
    
    print(PDFExtractor.validate_pdf(file),"============")
    if not PDFExtractor.validate_pdf(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed. Please upload a file with .pdf extension."
        )
    
    file_content = await file.read()
    print(len(file_content))
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    
    try: 
        pdf_text = PDFExtractor.extract_text(file_content)
        print(pdf_text)
        
        if len(pdf_text) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract sufficient text from PDF. The document might be empty or consist of images only."
            )
        
        llm_service = LLMService()
        answer = llm_service.answer_question(pdf_text, question)
        
        if answer == "NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The question is not relevant to the PDF content or cannot be answered based on the document."
            )
        
        processing_time = time.time() - start_time
        
        return PDFQuestionResponse(
            question=question,
            answer=answer,
            pdf_filename=file.filename,
            extracted_text_length=len(pdf_text),
            processing_time=round(processing_time, 2),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again."
        )