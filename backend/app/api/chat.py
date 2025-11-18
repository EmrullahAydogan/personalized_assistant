from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.conversation import Conversation, Message, MessageRole
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)
from app.services.ai_factory import AIServiceFactory

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Send a chat message and get AI response"""

    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == request.conversation_id)
            .options(selectinload(Conversation.messages))
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            ai_provider=request.ai_provider or "gemini",
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Create user message
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # Get AI service
    ai_service = AIServiceFactory.get_service(
        request.ai_provider or conversation.ai_provider
    )

    # Prepare message history
    messages = []
    for msg in conversation.messages:
        messages.append({"role": msg.role.value, "content": msg.content})
    messages.append({"role": "user", "content": request.message})

    # Get AI response
    if request.stream:
        # TODO: Implement streaming response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Streaming not yet implemented",
        )

    try:
        ai_response = await ai_service.chat(messages)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )

    # Create assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=ai_response,
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return ChatResponse(
        conversation_id=conversation.id,
        message=user_message,
        response=assistant_message,
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Get all conversations for a user"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .options(selectinload(Conversation.messages))
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Get a specific conversation"""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    await db.delete(conversation)
    await db.commit()

    return None
