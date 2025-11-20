from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.calendar import CalendarEvent
from app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
)

router = APIRouter()


@router.post("/", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: CalendarEventCreate,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Create a new calendar event"""

    # Validate dates
    if event_data.start_time >= event_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    event = CalendarEvent(
        user_id=user_id,
        **event_data.model_dump(),
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)

    return event


@router.get("/", response_model=List[CalendarEventResponse])
async def get_events(
    user_id: int = 1,  # TODO: Get from auth
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get calendar events for a user"""
    query = select(CalendarEvent).where(CalendarEvent.user_id == user_id)

    # Filter by date range if provided
    if start_date:
        query = query.where(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.where(CalendarEvent.end_time <= end_date)

    query = query.order_by(CalendarEvent.start_time.asc())

    result = await db.execute(query)
    events = result.scalars().all()

    return events


@router.get("/upcoming", response_model=List[CalendarEventResponse])
async def get_upcoming_events(
    user_id: int = 1,  # TODO: Get from auth
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming events for the next N days"""
    now = datetime.utcnow()
    end_date = now + timedelta(days=days)

    result = await db.execute(
        select(CalendarEvent)
        .where(
            CalendarEvent.user_id == user_id,
            CalendarEvent.start_time >= now,
            CalendarEvent.start_time <= end_date,
        )
        .order_by(CalendarEvent.start_time.asc())
    )
    events = result.scalars().all()

    return events


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Get a specific calendar event"""
    result = await db.execute(
        select(CalendarEvent).where(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == user_id,
        )
    )
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Update a calendar event"""
    result = await db.execute(
        select(CalendarEvent).where(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == user_id,
        )
    )
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # Update fields
    update_data = event_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(event, field, value)

    # Validate dates after update
    if event.start_time >= event.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    await db.commit()
    await db.refresh(event)

    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    user_id: int = 1,  # TODO: Get from auth
    db: AsyncSession = Depends(get_db),
):
    """Delete a calendar event"""
    result = await db.execute(
        select(CalendarEvent).where(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == user_id,
        )
    )
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    await db.delete(event)
    await db.commit()

    return None
