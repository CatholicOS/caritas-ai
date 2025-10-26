"""
Registration Model - Matches Database Schema
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class Registration(BaseModel):
    """Registration model linking volunteers to events."""
    
    __tablename__ = "registrations"

    # Foreign Keys
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    
    # Required field
    registration_date = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    volunteer = relationship("Volunteer", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
    
    # Registration Details
    status = Column(String(50))  # pending, confirmed, cancelled, completed
    checked_in = Column(Boolean)
    check_in_time = Column(TIMESTAMP)
    check_out_time = Column(TIMESTAMP)
    hours_served = Column(Integer)
    
    # Notes
    volunteer_notes = Column(Text)
    admin_notes = Column(Text)
    
    # Ratings and Feedback
    rating = Column(Integer)
    feedback = Column(Text)
    
    # Communication tracking
    confirmation_sent = Column(Boolean)
    reminder_sent = Column(Boolean)
    
    def __repr__(self):
        return f"<Registration(id={self.id}, volunteer_id={self.volunteer_id}, event_id={self.event_id}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert registration to dictionary."""
        return {
            "id": self.id,
            "volunteer_id": self.volunteer_id,
            "event_id": self.event_id,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "status": self.status,
            "checked_in": self.checked_in,
            "check_in_time": self.check_in_time.isoformat() if self.check_in_time else None,
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
            "hours_served": self.hours_served,
            "volunteer_notes": self.volunteer_notes,
            "admin_notes": self.admin_notes,
            "rating": self.rating,
            "feedback": self.feedback,
            "confirmation_sent": self.confirmation_sent,
            "reminder_sent": self.reminder_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }