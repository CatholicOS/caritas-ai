"""
Volunteer Model - Compatible with BaseModel
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel


class Volunteer(BaseModel):
    """
    Volunteer Model - Simplified for registration only
    
    Extends BaseModel to have created_at and updated_at for consistency.
    """
    __tablename__ = "volunteers"
    
    # Basic info (required for registration)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # System columns
    is_active = Column(Boolean, default=True)
    
    # Note: id, created_at, updated_at come from BaseModel
    
    # Relationships
    registrations = relationship("Registration", back_populates="volunteer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Volunteer(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }