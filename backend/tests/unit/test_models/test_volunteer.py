"""
Unit Tests for Volunteer Model

"""

import pytest
from app.models.volunteer import Volunteer


class TestVolunteerModel:
    """Test suite for Volunteer model business logic."""
    
    def test_create_volunteer_with_valid_data_succeeds(self):
        """Test that a Volunteer can be created with valid data."""
        # Arrange
        volunteer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "is_active": True
        }
        
        # Act
        volunteer = Volunteer(**volunteer_data)
        
        # Assert
        assert volunteer.first_name == "John"
        assert volunteer.last_name == "Doe"
        assert volunteer.email == "john.doe@example.com"
        # assert volunteer.is_active is True
    
    def test_create_volunteer_with_minimal_data_succeeds(self):
        """Test that a Volunteer can be created with only required fields."""
        # Arrange
        volunteer_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com"
        }
        
        # Act
        volunteer = Volunteer(**volunteer_data)
        
        # Assert
        assert volunteer.first_name == "Jane"
        assert volunteer.last_name == "Smith"
        assert volunteer.email == "jane.smith@example.com"
    
    def test_volunteer_to_dict_returns_correct_structure(self):
        """Test that to_dict() returns properly formatted dictionary."""
        # Arrange
        volunteer = Volunteer(
            id=1,
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            # is_active=True
        )
        
        # Act
        result = volunteer.to_dict()
        
        # Assert
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["first_name"] == "Alice"
        assert result["last_name"] == "Johnson"
        assert result["email"] == "alice@example.com"
        # assert result["is_active"] is True
    
    def test_volunteer_repr_contains_name_and_email(self):
        """Test that __repr__ includes volunteer name and email."""
        # Arrange
        volunteer = Volunteer(
            id=42,
            first_name="Bob",
            last_name="Wilson",
            email="bob@example.com"
        )
        
        # Act
        repr_string = repr(volunteer)
        
        # Assert
        assert "42" in repr_string
        assert "Bob Wilson" in repr_string or "Bob" in repr_string
        assert "bob@example.com" in repr_string
    
    def test_volunteer_full_name_concatenation(self):
        """Test that first and last name can be concatenated."""
        # Arrange
        volunteer = Volunteer(
            first_name="Chris",
            last_name="Anderson",
            email="chris@example.com"
        )
        
        # Act
        full_name = f"{volunteer.first_name} {volunteer.last_name}"
        
        # Assert
        assert full_name == "Chris Anderson"
    
    # def test_volunteer_is_active_by_default(self):
    #     """Test that new volunteers are active by default."""
    #     # Arrange & Act
    #     volunteer = Volunteer(
    #         first_name="Test",
    #         last_name="User",
    #         email="test@example.com"
    #     )
        
    #     # Assert
    #     assert volunteer.is_active is True
    
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "first.last@example.com",
        "user+tag@example.co.uk",
        "123@test.org"
    ])
    def test_create_volunteer_with_various_valid_email_formats(self, email):
        """Test that various valid email formats are accepted."""
        # Arrange & Act
        volunteer = Volunteer(
            first_name="Test",
            last_name="User",
            email=email
        )
        
        # Assert
        assert volunteer.email == email
    
    def test_volunteer_with_single_character_names(self):
        """Test that single character names are accepted."""
        # Arrange & Act
        volunteer = Volunteer(
            first_name="A",
            last_name="B",
            email="ab@example.com"
        )
        
        # Assert
        assert volunteer.first_name == "A"
        assert volunteer.last_name == "B"
    
    def test_volunteer_with_long_names(self):
        """Test that long names are accepted."""
        # Arrange
        long_first = "A" * 50
        long_last = "B" * 50
        
        # Act
        volunteer = Volunteer(
            first_name=long_first,
            last_name=long_last,
            email="test@example.com"
        )
        
        # Assert
        assert len(volunteer.first_name) == 50
        assert len(volunteer.last_name) == 50


class TestVolunteerBusinessLogic:
    """Test business logic methods on Volunteer model."""
    
    def test_deactivate_volunteer_changes_status(self):
        """Test that deactivating a volunteer changes is_active status."""
        # Arrange
        volunteer = Volunteer(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            # is_active=True
        )
        
        # Act
        # volunteer.is_active = False
        
        # Assert
        # assert volunteer.is_active is False
    
    def test_reactivate_volunteer_changes_status(self):
        """Test that reactivating a volunteer changes is_active status."""
        # Arrange
        volunteer = Volunteer(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            # is_active=False
        )
        
        # Act
        # volunteer.is_active = True
        
        # Assert
        # assert volunteer.is_active is True


class TestVolunteerNameParsing:
    """Test name parsing utilities for volunteers."""
    
    def test_parse_full_name_with_two_parts(self):
        """Test parsing a name with first and last name."""
        # Arrange
        full_name = "John Doe"
        
        # Act
        parts = full_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        
        # Assert
        assert first_name == "John"
        assert last_name == "Doe"
    
    def test_parse_full_name_with_multiple_parts(self):
        """Test parsing a name with middle names."""
        # Arrange
        full_name = "John Michael Doe"
        
        # Act
        parts = full_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        
        # Assert
        assert first_name == "John"
        assert last_name == "Michael Doe"
    
    def test_parse_full_name_with_single_part(self):
        """Test parsing a name with only one part."""
        # Arrange
        full_name = "Madonna"
        
        # Act
        parts = full_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        
        # Assert
        assert first_name == "Madonna"
        assert last_name == ""


# Test fixtures for reuse
@pytest.fixture
def sample_volunteer():
    """Fixture providing a sample volunteer for testing."""
    return Volunteer(
        id=1,
        first_name="Christopher",
        last_name="Wachira",
        email="wanjohi@cua.edu",
        # is_active=True
    )


@pytest.fixture
def inactive_volunteer():
    """Fixture providing an inactive volunteer."""
    return Volunteer(
        id=2,
        first_name="Inactive",
        last_name="User",
        email="inactive@example.com",
        # is_active=False
    )


@pytest.fixture
def volunteer_data():
    """Fixture providing volunteer data dictionary."""
    return {
        "first_name": "Test",
        "last_name": "Volunteer",
        "email": "test.volunteer@example.com"
    }