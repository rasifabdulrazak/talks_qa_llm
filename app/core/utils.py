import pdfplumber
import hashlib
import json
from datetime import datetime
from io import BytesIO
from openai import OpenAI
from app.core.config import settings
from fastapi import UploadFile, HTTPException, status
from app.core.redis import redis_client

class PDFExtractor:

    @staticmethod
    def extract_text_pdfplumber(file_content: bytes) -> str:
        """Extract text using pdfplumber (better for complex PDFs)"""
        try:
            pdf_file = BytesIO(file_content)
            text = ""
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            return ""
        
    @classmethod
    def extract_text(cls, file_content: bytes) -> str:
        """Extract text"""
        text = cls.extract_text_pdfplumber(file_content)
        if not text or len(text) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract sufficient text from PDF. The document might be empty or consist of images only."
            )
        return text
    
    @staticmethod
    def validate_pdf(file) -> bool:
        """Validate if file is a valid PDF"""
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed. Please upload a file with .pdf extension."
            )
        return True 
        
        
class LLMService:
    """Service for interacting with LLM providers"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.LLM_API_KEY)
    
    def get_system_prompt(self, pdf_text: str) -> str:
        """Generate comprehensive system prompt for PDF QA"""
        return f"""You are an expert PDF document analyzer and question-answering assistant. Your task is to answer questions based STRICTLY on the content of the provided PDF document.

        **DOCUMENT CONTENT:**
        {pdf_text}

        **INSTRUCTIONS:**
        1. **Answer ONLY from the document**: Base your answers exclusively on the information present in the PDF content above. Do not use external knowledge.

        2. **Relevance Check**: Before answering, determine if the question is related to the document content:
        - If the question is clearly about the document's topic/content, provide a detailed answer
        - If the question is unrelated, irrelevant, or about topics not covered in the document, respond with exactly: "NOT_FOUND"

        3. **Answer Quality**:
        - Be specific and cite relevant parts of the document
        - Keep answers concise but complete (2-4 sentences typically)
        - Use exact terms and phrases from the document when possible
        - If information is partially available, state what you know and what's missing

        4. **Uncertainty Handling**:
        - If the document mentions the topic but lacks specific details, say: "The document mentions [topic] but doesn't provide details about [specific question]."
        - Never make up or infer information not present in the document

        5. **Question Types to Mark as NOT_FOUND**:
        - Questions about completely different topics
        - Personal questions about the user
        - Questions requiring real-time information
        - Questions about the PDF file itself (metadata, formatting)
        - Off-topic or inappropriate questions
        
        6. **Question Types to summarize**:
        - Questions like "What does this say"
        - Questions like "What is this"
        - Questions like similar to above then summarize the content

        **EXAMPLES:**

        Document: "The Eiffel Tower was completed in 1889..."
        Question: "When was the Eiffel Tower built?"
        Answer: "The Eiffel Tower was completed in 1889."

        Document: "The Eiffel Tower was completed in 1889..."
        Question: "What is the capital of France?"
        Answer: "NOT_FOUND"

        Document: "The company revenue increased by 20% in Q4..."
        Question: "What's the weather today?"
        Answer: "NOT_FOUND"

        **REMEMBER**: Your primary goal is accuracy and relevance. When in doubt, respond with "NOT_FOUND" rather than providing potentially incorrect information."""

    def answer_question(self, pdf_text: str, question: str, stream:bool=False) -> str:
        """Get answer from LLM based on PDF content and question"""
        try:
            system_prompt = self.get_system_prompt(pdf_text)
            
            if self.provider == "openai":
                if stream:
                    return self._answer_with_openai_stream(system_prompt, question)
                else:
                    return self._answer_with_openai(system_prompt, question)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
        except Exception as e:
            raise
    
    def _answer_with_openai(self, system_prompt: str, question: str) -> str:
        """Answer using OpenAI"""
        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=settings.MAX_TOKEN,
            temperature=settings.TEMPERATURE
        )
        
        answer = response.choices[0].message.content.strip()
        return answer
    
    def _answer_with_openai_stream(self, system_prompt: str, question: str):
        """Stream response using OpenAI realtime completions"""
        stream = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            max_tokens=settings.MAX_TOKEN,
            temperature=settings.TEMPERATURE,
            stream=True
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
                
                
class CommonUtil:
    @staticmethod
    async def validate_pdf_file(file: UploadFile):
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed. Upload a .pdf file."
            )

        file_bytes = await file.read()

        if len(file_bytes) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File too large! Max size is {settings.MAX_FILE_SIZE / (1024*1024):.0f} MB."
            )

        return file_bytes
    
    @staticmethod
    def generate_stream_response(llm_service, pdf_text, filename, question,cache_key):
        def event_stream():
            try:
                full_answer = ""
                metadata = {
                    "type": "metadata",
                    "filename": filename,
                    "question": question,
                    "extracted_text_length": len(pdf_text),
                    "timestamp": str(datetime.now())
                }
                yield f"data: {json.dumps(metadata)}\n\n"

                # Stream LLM chunks
                for chunk in llm_service.answer_question(pdf_text, question, stream=True):
                    full_answer += chunk
                    yield f"data: {chunk}\n\n"
                
                CacheUtil.set_cached_answer(cache_key, full_answer)

            except Exception as e:
                print(e)
                error_data = {
                    "type": "error",
                    "message": "An error occurred during streaming."
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        return event_stream()
    
    
class CacheUtil:

    @staticmethod
    def generate_key(pdf_text: str, question: str) -> str:
        """Generate unique cache key based on PDF content + question."""
        raw = pdf_text + "|" + question.lower().strip()
        return "pdfqa:" + hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def get_cached_answer(key: str):
        return redis_client.get(key)

    @staticmethod
    def set_cached_answer(key: str, answer: str, ttl: int = 3600):
        redis_client.set(key, answer, ex=ttl)