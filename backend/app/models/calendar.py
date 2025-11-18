from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CalendarEvent(Base):
    """Calendar event model"""
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)

    # Time settings
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean, default=False)

    # Reminder
    reminder_minutes_before = Column(Integer, default=15)

    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)  # iCalendar RRULE format

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="calendar_events")
