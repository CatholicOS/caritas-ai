"""
Models Package

CRITICAL: Import order matters for SQLAlchemy relationships!
"""

# Import Base first
from .base import Base, BaseModel

# Import models in dependency order
# (models without foreign keys first, then models with foreign keys)
from .parish import Parish
from .volunteer import Volunteer
from .event import Event
from .registration import Registration

# Export all models
__all__ = [
    "Base",
    "BaseModel",
    "Parish",
    "Volunteer",
    "Event",
    "Registration",
]