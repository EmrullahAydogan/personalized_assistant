from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    analysis_result: Optional[str] = None
    created_at: datetime
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentAnalysisRequest(BaseModel):
    custom_prompt: Optional[str] = None
    ai_provider: Optional[str] = None


class DocumentAnalysisResponse(BaseModel):
    document_id: int
    extracted_text: str
    summary: str
    analysis: str
