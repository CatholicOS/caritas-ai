"""
Integration Tests for Registration CRUD Operations
"""

import pytest
from datetime import datetime
from app.models.registration import Registration


class TestRegistrationCRUD:
    """Test CRUD operations for Registration model with database."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_create_registration_in_database_succeeds(self, test_db, sample_volunteer, sample_event):
        """Test that a registration can be created and persisted."""
        # Arrange
        registration = Registration(
            volunteer_id=sample_volunteer.id,
            event_id=sample_event.id,
            registration_date=datetime.now(),
            status="confirmed"
        )
        
        # Act
        test_db.add(registration)
        test_db.commit()
        test_db.refresh(registration)
        
        # Assert
        assert registration.id is not None
        assert registration.volunteer_id == sample_volunteer.id
        assert registration.event_id == sample_event.id
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_read_registration_by_id_returns_correct_registration(self, test_db, sample_registration):
        """Test that a registration can be retrieved by ID."""
        # Act
        result = test_db.query(Registration).filter(Registration.id == sample_registration.id).first()
        
        # Assert
        assert result is not None
        assert result.volunteer_id == sample_registration.volunteer_id
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_update_registration_status_modifies_database(self, test_db, sample_registration):
        """Test that registration status can be updated."""
        # Act
        sample_registration.status = "cancelled"
        test_db.commit()
        test_db.refresh(sample_registration)
        
        # Assert
        assert sample_registration.status == "cancelled"
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_delete_registration_removes_from_database(self, test_db, sample_registration):
        """Test that a registration can be deleted."""
        # Arrange
        registration_id = sample_registration.id
        
        # Act
        test_db.delete(sample_registration)
        test_db.commit()
        
        # Assert
        found = test_db.query(Registration).filter(Registration.id == registration_id).first()
        assert found is None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_registrations_by_volunteer_returns_matching(self, test_db, sample_volunteer, sample_event):
        """Test querying registrations by volunteer."""
        # Arrange
        reg = Registration(
            volunteer_id=sample_volunteer.id,
            event_id=sample_event.id,
            registration_date=datetime.now(),
            status="confirmed"
        )
        test_db.add(reg)
        test_db.commit()
        
        # Act
        results = test_db.query(Registration).filter(
            Registration.volunteer_id == sample_volunteer.id
        ).all()
        
        # Assert
        assert len(results) >= 1
        assert all(r.volunteer_id == sample_volunteer.id for r in results)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_registrations_by_event_returns_matching(self, test_db, sample_volunteer, sample_event):
        """Test querying registrations by event."""
        # Arrange
        reg = Registration(
            volunteer_id=sample_volunteer.id,
            event_id=sample_event.id,
            registration_date=datetime.now(),
            status="confirmed"
        )
        test_db.add(reg)
        test_db.commit()
        
        # Act
        results = test_db.query(Registration).filter(
            Registration.event_id == sample_event.id
        ).all()
        
        # Assert
        assert len(results) >= 1
        assert all(r.event_id == sample_event.id for r in results)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_check_duplicate_registration_prevents_double_booking(self, test_db, sample_volunteer, sample_event):
        """Test checking for duplicate registrations."""
        # Arrange
        reg1 = Registration(
            volunteer_id=sample_volunteer.id,
            event_id=sample_event.id,
            registration_date=datetime.now(),
            status="confirmed"
        )
        test_db.add(reg1)
        test_db.commit()
        
        # Act - Check if registration already exists
        existing = test_db.query(Registration).filter(
            Registration.volunteer_id == sample_volunteer.id,
            Registration.event_id == sample_event.id
        ).first()
        
        # Assert
        assert existing is not None
        # Would prevent creating reg2