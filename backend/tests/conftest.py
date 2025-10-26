"""
Shared Test Fixtures - HANDLES MULTIPLE BASES
Works with both Base and BaseModel
"""

import pytest
import os
import sys
from pathlib import Path

# ============================================================================
# ENVIRONMENT SETUP - MUST BE FIRST!
# ============================================================================

os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["OPENAI_API_KEY"] = "test-key-not-real"

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# ============================================================================
# IMPORTS
# ============================================================================

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

# Import BOTH Base classes
from app.core.database import Base, get_db
from app.main import app

# Try to import BaseModel too (for Volunteer/Registration)
try:
    from app.models.base import BaseModel
    HAS_BASE_MODEL = True
except ImportError:
    BaseModel = None
    HAS_BASE_MODEL = False

# Import all models
from app.models.parish import Parish
from app.models.event import Event
from app.models.volunteer import Volunteer
from app.models.registration import Registration


# ============================================================================
# SQLITE COMPATIBILITY
# ============================================================================

def _fk_pragma_on_connect(dbapi_con, con_record):
    """Enable foreign key constraints for SQLite."""
    dbapi_con.execute('pragma foreign_keys=ON')


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh in-memory SQLite database for each test.
    Handles BOTH Base and BaseModel tables.
    """
    # Create in-memory database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Enable foreign keys
    event.listen(engine, "connect", _fk_pragma_on_connect)
    
    # Create tables from BOTH bases
    Base.metadata.create_all(engine)
    if HAS_BASE_MODEL and BaseModel is not None:
        BaseModel.metadata.create_all(engine)
    
    # Debug: Show what was created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    # print(f"DEBUG: Created tables: {tables}")  # Uncomment to debug
    
    if not tables:
        print("WARNING: No tables created!")
        print(f"  Base.metadata.tables: {list(Base.metadata.tables.keys())}")
        if HAS_BASE_MODEL:
            print(f"  BaseModel.metadata.tables: {list(BaseModel.metadata.tables.keys())}")
    
    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    session = TestingSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()
    
    # Drop tables from both bases
    Base.metadata.drop_all(engine)
    if HAS_BASE_MODEL and BaseModel is not None:
        BaseModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI TestClient with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# MODEL FIXTURES
# ============================================================================

@pytest.fixture
def sample_parish(test_db):
    """Create and return a sample parish."""
    parish = Parish(
        name="St. Mary's Church",
        address="123 Main St",
        city="Baltimore",
        state="MD",
        zip_code="21201",
        email="contact@stmarys.org"
    )
    
    # Handle services field
    if hasattr(parish, 'services'):
        try:
            parish.services = json.dumps(["food pantry", "counseling"])
        except:
            try:
                parish.services = ["food pantry", "counseling"]
            except:
                pass
    
    test_db.add(parish)
    test_db.commit()
    test_db.refresh(parish)
    return parish


@pytest.fixture
def multiple_parishes(test_db):
    """Create multiple parishes for testing."""
    parishes = []
    parishes_data = [
        {"name": "St. Mary's Church", "city": "Baltimore", "state": "MD"},
        {"name": "Holy Spirit Parish", "city": "Baltimore", "state": "MD"},
        {"name": "St. John's Church", "city": "New York", "state": "NY"},
    ]
    
    for data in parishes_data:
        parish = Parish(**data)
        test_db.add(parish)
        parishes.append(parish)
    
    test_db.commit()
    
    for parish in parishes:
        test_db.refresh(parish)
    
    return parishes


@pytest.fixture
def sample_event(test_db, sample_parish):
    """Create and return a sample event."""
    event = Event(
        parish_id=sample_parish.id,
        title="Weekend Food Pantry",
        description="Help distribute food",
        event_date=datetime.now() + timedelta(days=7)
    )
    
    # Set optional fields
    for field, value in [
        ('skills_needed', json.dumps(["packing"])),
        ('max_volunteers', 10),
        ('registered_volunteers', 0),
        ('status', 'open')
    ]:
        if hasattr(event, field):
            try:
                setattr(event, field, value)
            except:
                pass
    
    test_db.add(event)
    test_db.commit()
    test_db.refresh(event)
    return event


@pytest.fixture
def multiple_events(test_db, sample_parish):
    """Create multiple events for testing."""
    events = []
    for title, days in [("Food Pantry", 7), ("Tutoring", 14)]:
        event = Event(
            parish_id=sample_parish.id,
            title=title,
            event_date=datetime.now() + timedelta(days=days)
        )
        test_db.add(event)
        events.append(event)
    
    test_db.commit()
    
    for event in events:
        test_db.refresh(event)
    
    return events


@pytest.fixture
def sample_volunteer(test_db):
    """Create and return a sample volunteer."""
    volunteer = Volunteer(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    test_db.add(volunteer)
    test_db.commit()
    test_db.refresh(volunteer)
    return volunteer


@pytest.fixture
def sample_registration(test_db, sample_volunteer, sample_event):
    """Create and return a sample registration."""
    registration = Registration(
        volunteer_id=sample_volunteer.id,
        event_id=sample_event.id,
        registration_date=datetime.now()
    )
    
    if hasattr(registration, 'status'):
        try:
            registration.status = "confirmed"
        except:
            pass
    
    test_db.add(registration)
    test_db.commit()
    test_db.refresh(registration)
    return registration


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def future_date():
    """Return a date 7 days in the future."""
    return datetime.now() + timedelta(days=7)


@pytest.fixture
def past_date():
    """Return a date 7 days in the past."""
    return datetime.now() - timedelta(days=7)
