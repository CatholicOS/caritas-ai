"""
Integration Tests for Volunteer CRUD Operations
"""

import pytest
from app.models.volunteer import Volunteer


class TestVolunteerCRUD:
    """Test CRUD operations for Volunteer model with database."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_create_volunteer_in_database_succeeds(self, test_db):
        """Test that a volunteer can be created and persisted."""
        # Arrange
        volunteer = Volunteer(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            is_active=True
        )
        
        # Act
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)
        
        # Assert
        assert volunteer.id is not None
        found = test_db.query(Volunteer).filter(Volunteer.email == "test@example.com").first()
        assert found is not None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_read_volunteer_by_id_returns_correct_volunteer(self, test_db, sample_volunteer):
        """Test that a volunteer can be retrieved by ID."""
        # Act
        result = test_db.query(Volunteer).filter(Volunteer.id == sample_volunteer.id).first()
        
        # Assert
        assert result is not None
        assert result.email == sample_volunteer.email
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_update_volunteer_modifies_database_record(self, test_db, sample_volunteer):
        """Test that a volunteer can be updated."""
        # Act
        sample_volunteer.first_name = "Updated"
        test_db.commit()
        test_db.refresh(sample_volunteer)
        
        # Assert
        assert sample_volunteer.first_name == "Updated"
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_delete_volunteer_removes_from_database(self, test_db, sample_volunteer):
        """Test that a volunteer can be deleted."""
        # Arrange
        volunteer_id = sample_volunteer.id
        
        # Act
        test_db.delete(sample_volunteer)
        test_db.commit()
        
        # Assert
        found = test_db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
        assert found is None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_volunteers_by_email_returns_matching(self, test_db):
        """Test querying volunteers by email."""
        # Arrange
        volunteer = Volunteer(first_name="Test", last_name="User", email="unique@test.com")
        test_db.add(volunteer)
        test_db.commit()
        
        # Act
        result = test_db.query(Volunteer).filter(Volunteer.email == "unique@test.com").first()
        
        # Assert
        assert result is not None
        assert result.email == "unique@test.com"
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_active_volunteers_excludes_inactive(self, test_db):
        """Test filtering by active status."""
        # Arrange
        active = Volunteer(first_name="Active", last_name="User", email="active@test.com", is_active=True)
        inactive = Volunteer(first_name="Inactive", last_name="User", email="inactive@test.com", is_active=False)
        test_db.add(active)
        test_db.add(inactive)
        test_db.commit()
        
        # Act
        active_vols = test_db.query(Volunteer).filter(Volunteer.is_active == True).all()
        
        # Assert
        assert active in active_vols
        assert inactive not in active_vols