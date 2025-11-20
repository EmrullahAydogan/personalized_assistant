from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import aiofiles
import os
from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import (
    DocumentResponse,
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
)
from app.services.document_service import DocumentService
from app.core.config import settings

router = APIRouter()
document_service = DocumentService()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Upload a document"""

    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes",
        )

    # Generate unique filename
    file_extension = file.filename.split('.')[-1].lower()
    unique_filename = f"{user_id}_{datetime.utcnow().timestamp()}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    # Create database record
    document = Document(
        user_id=user_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_type=file_extension,
        file_size=len(content),
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


@router.post("/{document_id}/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    document_id: int,
    request: DocumentAnalysisRequest,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Analyze a document using AI"""

    # Get document
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        # Analyze document
        analysis = await document_service.analyze_document(
            document.file_path,
            request.custom_prompt,
            request.ai_provider,
        )

        # Update document with analysis results
        document.extracted_text = analysis["extracted_text"]
        document.summary = analysis["summary"]
        document.analysis_result = analysis["analysis"]
        document.analyzed_at = datetime.utcnow()

        await db.commit()

        return DocumentAnalysisResponse(
            document_id=document.id,
            extracted_text=analysis["extracted_text"],
            summary=analysis["summary"],
            analysis=analysis["analysis"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(e)}",
        )


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Get all documents for a user"""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Get a specific document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Delete file
    if os.path.exists(document.file_path):
        os.unlink(document.file_path)

    # Delete database record
    await db.delete(document)
    await db.commit()

    return None
