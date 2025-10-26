"""

"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ARRAY, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Event(Base):
    """
    Event Model - Simplified to match CSV only
    
    CSV Columns: EIN, TITLE, EVENT_DATE, PARISH, EVENT_DESCRIPTION, SKILLS_NEEDED, MAX_VOLUNTEERS
    Database Columns: id, parish_id, title, event_date, description, skills_needed, 
                      max_volunteers, registered_volunteers, is_active, status, created_at
    """
    __tablename__ = "events"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    parish_id = Column(Integer, ForeignKey('parishes.id', ondelete='CASCADE'), 
                      nullable=False, index=True)  # from PARISH (lookup by name)
    
    # CSV columns (EIN not stored)
    title = Column(String(255), nullable=False)                  # from TITLE
    event_date = Column(TIMESTAMP, nullable=False, index=True)   # from EVENT_DATE
    description = Column(Text)                                   # from EVENT_DESCRIPTION
    skills_needed = Column(ARRAY(Text))                          # from SKILLS_NEEDED (comma-separated -> array)
    max_volunteers = Column(Integer)                             # from MAX_VOLUNTEERS
    
    # System columns (useful for tracking)
    registered_volunteers = Column(Integer, default=0)           # count of registrations
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default='open', index=True)      # open, closed, full
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    parish = relationship("Parish", back_populates="events")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', parish_id={self.parish_id}, date={self.event_date})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "parish_id": self.parish_id,
            "parish_name": self.parish.name if self.parish else None,
            "title": self.title,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "description": self.description,
            "skills_needed": self.skills_needed or [],
            "max_volunteers": self.max_volunteers,
            "registered_volunteers": self.registered_volunteers,
            "spots_available": (self.max_volunteers - self.registered_volunteers) if self.max_volunteers else None,
            "is_active": self.is_active,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }