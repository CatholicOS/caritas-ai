"""
Base Model
"""

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create Base class
Base = declarative_base()


class BaseModel(Base):
    """
    Base model class with common fields.
    All other models inherit from this.
    """
    __abstract__ = True

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"