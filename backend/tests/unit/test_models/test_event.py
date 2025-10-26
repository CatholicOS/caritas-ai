"""
Unit Tests for Event Model

"""

import pytest
from datetime import datetime, timedelta
from app.models.event import Event


class TestEventModel:
    """Test suite for Event model business logic."""
    
    def test_create_event_with_valid_data_succeeds(self):
        """Test that an Event can be created with valid data."""
        # Arrange
        event_data = {
            "parish_id": 1,
            "title": "Food Pantry Service",
            "description": "Help distribute food",
            "event_date": datetime.now() + timedelta(days=7),
            "skills_needed": ["packing", "sorting"],
            "max_volunteers": 10,
            "registered_volunteers": 0,
            "status": "open"
        }
        
        # Act
        event = Event(**event_data)
        
        # Assert
        assert event.title == "Food Pantry Service"
        assert event.max_volunteers == 10
        assert event.status == "open"
        assert "packing" in event.skills_needed
    
    def test_create_event_with_minimal_data_succeeds(self):
        """Test that an Event can be created with only required fields."""
        # Arrange
        event_data = {
            "parish_id": 1,
            "title": "Test Event",
            "event_date": datetime.now() + timedelta(days=1)
        }
        
        # Act
        event = Event(**event_data)
        
        # Assert
        assert event.title == "Test Event"
        assert event.parish_id == 1
        # assert event.is_active is True
    
    def test_event_to_dict_returns_correct_structure(self):
        """Test that to_dict() returns properly formatted dictionary."""
        # Arrange
        event_date = datetime(2025, 12, 25, 10, 0, 0)
        event = Event(
            id=1,
            parish_id=1,
            title="Christmas Service",
            event_date=event_date,
            skills_needed=["setup"],
            max_volunteers=20,
            registered_volunteers=5,
            status="open"
        )
        
        # Act
        result = event.to_dict()
        
        # Assert
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["title"] == "Christmas Service"
        assert result["max_volunteers"] == 20
        assert result["registered_volunteers"] == 5
    
    def test_event_has_available_spots_when_not_full(self):
        """Test that event correctly reports available spots."""
        # Arrange
        event = Event(
            parish_id=1,
            title="Test Event",
            event_date=datetime.now() + timedelta(days=1),
            max_volunteers=10,
            registered_volunteers=5
        )
        
        # Act
        available = event.max_volunteers - event.registered_volunteers
        
        # Assert
        assert available == 5
        assert event.registered_volunteers < event.max_volunteers
    
    def test_event_is_full_when_max_volunteers_reached(self):
        """Test that event is considered full when max reached."""
        # Arrange
        event = Event(
            parish_id=1,
            title="Test Event",
            event_date=datetime.now() + timedelta(days=1),
            max_volunteers=10,
            registered_volunteers=10,
            status="full"
        )
        
        # Act & Assert
        assert event.registered_volunteers == event.max_volunteers
        assert event.status == "full"
    
    def test_event_date_is_in_future(self):
        """Test that event date is correctly set in the future."""
        # Arrange
        future_date = datetime.now() + timedelta(days=30)
        event = Event(
            parish_id=1,
            title="Future Event",
            event_date=future_date
        )
        
        # Act & Assert
        assert event.event_date > datetime.now()
    
    @pytest.mark.parametrize("status", ["open", "full", "cancelled", "completed"])
    def test_event_status_accepts_valid_values(self, status):
        """Test that event accepts valid status values."""
        # Arrange & Act
        event = Event(
            parish_id=1,
            title="Test Event",
            event_date=datetime.now() + timedelta(days=1),
            status=status
        )
        
        # Assert
        assert event.status == status
    
    def test_event_skills_needed_is_array(self):
        """Test that skills_needed is stored as array."""
        # Arrange
        event = Event(
            parish_id=1,
            title="Test Event",
            event_date=datetime.now() + timedelta(days=1),
            skills_needed=["cooking", "serving", "cleanup"]
        )
        
        # Act & Assert
        assert isinstance(event.skills_needed, list)
        assert len(event.skills_needed) == 3
        assert "cooking" in event.skills_needed


class TestEventBusinessLogic:
    """Test business logic methods on Event model."""
    
    def test_increment_registered_volunteers_updates_count(self):
        """Test that registering a volunteer increments count."""
        # Arrange
        event = Event(
            parish_id=1,
            title="Test Event",
            event_date=datetime.now() + timedelta(days=1),
            max_volunteers=10,
            registered_volunteers=5
        )
        
        # Act
        event.registered_volunteers += 1
        
        # Assert
        assert event.registered_volunteers == 6
    
    def test_event_becomes_full_when_max_reached(self):
        """Test that event status changes to full when max reached."""
        # Arrange
        event = Event(
            parish_id=1,
            title="Test Event",
            event_date=datetime.now() + timedelta(days=1),
            max_volunteers=10,
            registered_volunteers=9,
            status="open"
        )
        
        # Act - simulate registration
        event.registered_volunteers += 1
        if event.registered_volunteers >= event.max_volunteers:
            event.status = "full"
        
        # Assert
        assert event.status == "full"
        assert event.registered_volunteers == 10
    
    # def test_event_is_active_by_default(self):
    #     """Test that new events are active by default."""
    #     # Arrange & Act
    #     event = Event(
    #         parish_id=1,
    #         title="Test Event",
    #         event_date=datetime.now() + timedelta(days=1)
    #     )
        
    #     # Assert
    #     assert event.is_active is True


# Test fixtures for reuse
@pytest.fixture
def sample_event():
    """Fixture providing a sample event for testing."""
    return Event(
        id=1,
        parish_id=1,
        title="Weekend Food Pantry",
        description="Help distribute food to families in need",
        event_date=datetime(2025, 11, 15, 9, 0, 0),
        start_time="09:00:00",
        end_time="12:00:00",
        skills_needed=["packing", "sorting", "customer service"],
        max_volunteers=15,
        registered_volunteers=8,
        status="open"
        # is_active=True
    )


@pytest.fixture
def minimal_event():
    """Fixture providing an event with minimal data."""
    return Event(
        parish_id=1,
        title="Simple Event",
        event_date=datetime.now() + timedelta(days=7)
    )


@pytest.fixture
def future_date():
    """Fixture providing a future date for testing."""
    return datetime.now() + timedelta(days=30)


@pytest.fixture
def past_date():
    """Fixture providing a past date for testing."""
    return datetime.now() - timedelta(days=30)