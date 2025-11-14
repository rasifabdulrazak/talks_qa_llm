import time
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import User
from app.schema.bot import PDFQuestionResponse
from app.core.utils import PDFExtractor,LLMService,CommonUtil
from app.core.config import settings



router = APIRouter()

@router.post("/ask/", response_model=PDFQuestionResponse)
async def ask_pdf_question(
    file: UploadFile = File(description="PDF file to analyze"),
    question: str = Form(min_length=5, max_length=500, description="Question about the PDF"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a PDF file and ask a question about its content.
    
    - **file**: PDF file (Fix the size in the .env MAX_FILE_SIZE variable)
    - **question**: Question about the PDF content
    
    Returns the answer based on the PDF content or "NOT_FOUND" if question is irrelevant.
    """
    
    try: 
        start_time = time.time()
    
        file_content = await CommonUtil.validate_pdf_file(file)
        pdf_text = PDFExtractor.extract_text(file_content)
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
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again."
        )
        

@router.post("/ask-stream/")
async def ask_pdf_question_stream(
    file: UploadFile = File(description="PDF file to analyze"),
    question: str = Form(min_length=5, max_length=500, description="Question about the PDF"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a PDF file and ask a question with streaming response.
    
    - **file**: PDF file (Fix the size in the .env MAX_FILE_SIZE variable)
    - **question**: Question about the PDF content
    
    Returns the answer as a streaming response (Server-Sent Events format).
    """
    
    try:
        file_content = await CommonUtil.validate_pdf_file(file)
        pdf_text = PDFExtractor.extract_text(file_content)
        llm_service = LLMService()
        
        stream = CommonUtil.generate_stream_response(
            llm_service=llm_service,
            pdf_text=pdf_text,
            filename=file.filename,
            question=question
        )
        
        return StreamingResponse(
            stream,
            media_type="text/event-stream",
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again."
        )
