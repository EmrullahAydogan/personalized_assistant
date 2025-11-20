from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    reminder_minutes_before: int = 15
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    reminder_minutes_before: Optional[int] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None


class CalendarEventResponse(CalendarEventBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
