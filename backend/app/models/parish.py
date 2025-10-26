"""

"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ARRAY, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Parish(Base):
    """
    Parish Model - Simplified to match CSV only
    
    CSV Columns: EIN, NAME, STREET, CITY, STATE, ZIP, EMAIL, SERVICES
    Database Columns: id, name, address, city, state, zip_code, email, services, is_active, created_at
    """
    __tablename__ = "parishes"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # CSV columns (EIN is not stored, used only for reference)
    name = Column(String(255), nullable=False, index=True)  # from NAME
    address = Column(String(255))                            # from STREET
    city = Column(String(100), index=True)                   # from CITY
    state = Column(String(2), index=True)                    # from STATE
    zip_code = Column(String(10))                            # from ZIP
    email = Column(String(255))                              # from EMAIL
    services = Column(ARRAY(Text))                           # from SERVICES (comma-separated -> array)
    
    # System columns
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    events = relationship("Event", back_populates="parish", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Parish(id={self.id}, name='{self.name}', city='{self.city}', state='{self.state}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "email": self.email,
            "services": self.services or [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }