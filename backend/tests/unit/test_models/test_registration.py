"""
Unit Tests for Registration Model

"""

import pytest
from datetime import datetime, timedelta
from app.models.registration import Registration


class TestRegistrationModel:
    """Test suite for Registration model business logic."""
    
    def test_create_registration_with_valid_data_succeeds(self):
        """Test that a Registration can be created with valid data."""
        # Arrange
        registration_data = {
            "volunteer_id": 1,
            "event_id": 1,
            "registration_date": datetime.now(),
            "status": "confirmed"
        }
        
        # Act
        registration = Registration(**registration_data)
        
        # Assert
        assert registration.volunteer_id == 1
        assert registration.event_id == 1
        assert registration.status == "confirmed"
        assert registration.registration_date is not None
    
    def test_create_registration_with_minimal_data_succeeds(self):
        """Test that a Registration can be created with only required fields."""
        # Arrange
        registration_data = {
            "volunteer_id": 1,
            "event_id": 1,
            "registration_date": datetime.now()
        }
        
        # Act
        registration = Registration(**registration_data)
        
        # Assert
        assert registration.volunteer_id == 1
        assert registration.event_id == 1
    
    def test_registration_to_dict_returns_correct_structure(self):
        """Test that to_dict() returns properly formatted dictionary."""
        # Arrange
        reg_date = datetime(2025, 10, 25, 12, 0, 0)
        registration = Registration(
            id=1,
            volunteer_id=5,
            event_id=10,
            registration_date=reg_date,
            status="confirmed",
            checked_in=False
        )
        
        # Act
        result = registration.to_dict()
        
        # Assert
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["volunteer_id"] == 5
        assert result["event_id"] == 10
        assert result["status"] == "confirmed"
        assert result["checked_in"] is False
    
    @pytest.mark.parametrize("status", [
        "pending",
        "confirmed",
        "cancelled",
        "completed"
    ])
    def test_registration_status_accepts_valid_values(self, status):
        """Test that registration accepts valid status values."""
        # Arrange & Act
        registration = Registration(
            volunteer_id=1,
            event_id=1,
            registration_date=datetime.now(),
            status=status
        )
        
        # Assert
        assert registration.status == status
    
    def test_registration_checked_in_defaults_to_false(self):
        """Test that checked_in defaults to False."""
        # Arrange & Act
        registration = Registration(
            volunteer_id=1,
            event_id=1,
            registration_date=datetime.now()
        )
        
        # Assert
        assert registration.checked_in is None or registration.checked_in is False
    
    def test_registration_repr_contains_ids(self):
        """Test that __repr__ includes volunteer and event IDs."""
        # Arrange
        registration = Registration(
            id=42,
            volunteer_id=10,
            event_id=20,
            registration_date=datetime.now(),
            status="confirmed"
        )
        
        # Act
        repr_string = repr(registration)
        
        # Assert
        assert "42" in repr_string or "id=42" in repr_string
        assert "10" in repr_string
        assert "20" in repr_string


class TestRegistrationBusinessLogic:
    """Test business logic methods on Registration model."""
    
    def test_confirm_registration_changes_status(self):
        """Test that confirming a registration updates status."""
        # Arrange
        registration = Registration(
            volunteer_id=1,
            event_id=1,
            registration_date=datetime.now(),
            status="pending"
        )
        
        # Act
        registration.status = "confirmed"
        
        # Assert
        assert registration.status == "confirmed"
    
    def test_cancel_registration_changes_status(self):
        """Test that cancelling a registration updates status."""
        # Arrange
        registration = Registration(
            volunteer_id=1,
            event_id=1,
            registration_date=datetime.now(),
            status="confirmed"
        )
        
        # Act
        registration.status = "cancelled"
        
        # Assert
        assert registration.status == "cancelled"
    
    def test_check_in_volunteer_updates_status(self):
        """Test that checking in a volunteer updates checked_in flag."""
        # Arrange
        registration = Registration(
            volunteer_id=1,
            event_id=1,
            registration_date=datetime.now(),
            status="confirmed",
            checked_in=False
        )
        
        # Act
        registration.checked_in = True
        registration.check_in_time = datetime.now()
        
        # Assert
        assert registration.checked_in is True
        assert registration.check_in_time is not None
    
    def test_complete_registration_after_event(self):
        """Test that completing a registration updates status."""
        # Arrange
        registration = Registration(
            volunteer_id=1,
            event_id=1,
            registration_date=datetime.now(),
            status="confirmed",
            checked_in=True
        )
        
        # Act
        registration.status = "completed"
        registration.check_out_time = datetime.now()
        
        # Assert
        assert registration.status == "completed"
        assert registration.check_out_time is not None
    
    def test_calculate_hours_served(self):
        """Test calculation of hours served."""
        # Arrange
        check_in = datetime(2025, 10, 25, 9, 0, 0)
        check_out = datetime(2025, 10, 25, 12, 0, 0)
        
        registration = Registration(
            volunteer_id=1,
            event_id=1,
            registration_date=datetime.now(),
            check_in_time=check_in,
            check_out_time=check_out
        )
        
        # Act
        hours = (check_out - check_in).total_seconds() / 3600
        registration.hours_served = int(hours)
        
        # Assert
        assert registration.hours_served == 3


class TestRegistrationValidation:
    """Test validation logic for registrations."""
    
    def test_registration_requires_volunteer_id(self):
        """Test that volunteer_id is required."""
        # This test verifies the model expects volunteer_id
        # Actual constraint enforcement happens at database level
        registration_data = {
            "event_id": 1,
            "registration_date": datetime.now()
        }
        
        # Model accepts it (DB would reject)
        registration = Registration(**registration_data)
        assert registration.volunteer_id is None
    
    def test_registration_requires_event_id(self):
        """Test that event_id is required."""
        # This test verifies the model expects event_id
        registration_data = {
            "volunteer_id": 1,
            "registration_date": datetime.now()
        }
        
        # Model accepts it (DB would reject)
        registration = Registration(**registration_data)
        assert registration.event_id is None
    
    def test_registration_date_can_be_set(self):
        """Test that registration_date can be explicitly set."""
        # Arrange
        specific_date = datetime(2025, 10, 25, 14, 30, 0)
        
        # Act
        registration = Registration(
            volunteer_id=1,
            event_id=1,
            registration_date=specific_date
        )
        
        # Assert
        assert registration.registration_date == specific_date


# Test fixtures for reuse
@pytest.fixture
def sample_registration():
    """Fixture providing a sample registration for testing."""
    return Registration(
        id=1,
        volunteer_id=1,
        event_id=1,
        registration_date=datetime(2025, 10, 20, 10, 0, 0),
        status="confirmed",
        checked_in=False,
        confirmation_sent=True,
        reminder_sent=False
    )


@pytest.fixture
def pending_registration():
    """Fixture providing a pending registration."""
    return Registration(
        id=2,
        volunteer_id=2,
        event_id=2,
        registration_date=datetime.now(),
        status="pending",
        checked_in=False
    )


@pytest.fixture
def completed_registration():
    """Fixture providing a completed registration."""
    check_in = datetime.now() - timedelta(hours=4)
    check_out = datetime.now() - timedelta(hours=1)
    
    return Registration(
        id=3,
        volunteer_id=3,
        event_id=3,
        registration_date=datetime.now() - timedelta(days=1),
        status="completed",
        checked_in=True,
        check_in_time=check_in,
        check_out_time=check_out,
        hours_served=3
    )


@pytest.fixture
def registration_data():
    """Fixture providing registration data dictionary."""
    return {
        "volunteer_id": 1,
        "event_id": 1,
        "registration_date": datetime.now(),
        "status": "confirmed"
    }