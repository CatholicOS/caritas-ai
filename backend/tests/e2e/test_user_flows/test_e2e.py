"""
End-to-End Tests for Complete User Flows
Tests entire system with all components working together
"""

import pytest
from datetime import datetime, timedelta
from app.services.db_service import search_volunteer_events, register_volunteer_for_event


class TestVolunteerRegistrationFlow:
    """Test complete volunteer registration workflow."""
    
    @pytest.mark.e2e
    def test_complete_volunteer_registration_flow_succeeds(self, test_db, sample_parish):
        """
        Test complete flow:
        1. User searches for opportunities
        2. Finds an event
        3. Registers for the event
        4. Registration is confirmed
        """
        # Step 1: Create an event
        from app.models.event import Event
        event = Event(
            parish_id=sample_parish.id,
            title="Weekend Food Pantry",
            description="Help distribute food",
            event_date=datetime.now() + timedelta(days=7),
            skills_needed=["packing"],
            max_volunteers=10,
            registered_volunteers=0,
            status="open",
            is_active=True
        )
        test_db.add(event)
        test_db.commit()
        test_db.refresh(event)
        
        # Step 2: User searches for opportunities
        events = search_volunteer_events(
            location=sample_parish.city,
            skills=["packing"],
            db=test_db
        )
        
        assert len(events) >= 1
        found_event = events[0]
        assert found_event["title"] == "Weekend Food Pantry"
        
        # Step 3: User registers for the event
        result = register_volunteer_for_event(
            volunteer_email="volunteer@test.com",
            event_id=found_event["id"],
            volunteer_name="John Volunteer",
            db=test_db
        )
        
        assert result["success"] is True
        assert "registration_id" in result
        
        # Step 4: Verify registration in database
        from app.models.registration import Registration
        registration = test_db.query(Registration).filter(
            Registration.id == result["registration_id"]
        ).first()
        
        assert registration is not None
        assert registration.status == "confirmed"
        assert registration.registration_date is not None
        
        # Step 5: Verify event volunteer count increased
        test_db.refresh(event)
        assert event.registered_volunteers == 1
    
    @pytest.mark.e2e
    def test_volunteer_cannot_register_for_full_event(self, test_db, sample_parish):
        """
        Test that volunteer cannot register for full event:
        1. Event reaches max capacity
        2. New volunteer tries to register
        3. Registration is rejected
        """
        # Step 1: Create event with limited capacity
        from app.models.event import Event
        event = Event(
            parish_id=sample_parish.id,
            title="Limited Event",
            event_date=datetime.now() + timedelta(days=7),
            max_volunteers=1,
            registered_volunteers=0,
            status="open"
        )
        test_db.add(event)
        test_db.commit()
        
        # Step 2: Fill the event
        result1 = register_volunteer_for_event(
            volunteer_email="vol1@test.com",
            event_id=event.id,
            volunteer_name="Volunteer One",
            db=test_db
        )
        assert result1["success"] is True
        
        # Step 3: Try to register another volunteer
        result2 = register_volunteer_for_event(
            volunteer_email="vol2@test.com",
            event_id=event.id,
            volunteer_name="Volunteer Two",
            db=test_db
        )
        
        # Step 4: Verify rejection
        assert result2["success"] is False
        assert "full" in result2["error"].lower()
    
    @pytest.mark.e2e
    def test_volunteer_registration_with_existing_account(self, test_db, sample_parish, sample_volunteer):
        """
        Test registration flow with existing volunteer:
        1. Existing volunteer searches for events
        2. Registers with existing email
        3. System recognizes existing volunteer
        4. Registration succeeds without creating duplicate
        """
        # Step 1: Create event
        from app.models.event import Event
        event = Event(
            parish_id=sample_parish.id,
            title="Test Event",
            event_date=datetime.now() + timedelta(days=7),
            status="open"
        )
        test_db.add(event)
        test_db.commit()
        
        # Step 2: Register with existing email
        result = register_volunteer_for_event(
            volunteer_email=sample_volunteer.email,
            event_id=event.id,
            db=test_db
        )
        
        # Step 3: Verify success and correct volunteer used
        assert result["success"] is True
        assert result["volunteer_name"] == f"{sample_volunteer.first_name} {sample_volunteer.last_name}"
        
        # Step 4: Verify no duplicate volunteer created
        from app.models.volunteer import Volunteer
        volunteers = test_db.query(Volunteer).filter(
            Volunteer.email == sample_volunteer.email
        ).all()
        assert len(volunteers) == 1


class TestParishAdminFlow:
    """Test parish administrator workflow."""
    
    @pytest.mark.e2e
    def test_parish_admin_views_analytics(self, test_db, sample_parish, sample_event, sample_registration):
        """
        Test parish admin workflow:
        1. Admin requests parish analytics
        2. System provides event count
        3. System provides registration count
        4. Data is accurate
        """
        # Step 1: Get analytics
        from app.services.db_service import get_parish_analytics
        analytics = get_parish_analytics(sample_parish.name, db=test_db)
        
        # Step 2: Verify analytics structure
        assert "error" not in analytics
        assert "parish_name" in analytics
        assert "total_events" in analytics
        assert "upcoming_events" in analytics
        assert "total_registrations" in analytics
        
        # Step 3: Verify data accuracy
        assert analytics["parish_name"] == sample_parish.name
        assert analytics["total_events"] >= 1
        assert analytics["total_registrations"] >= 1


class TestMultipleVolunteersFlow:
    """Test multiple volunteers registering for same event."""
    
    @pytest.mark.e2e
    def test_multiple_volunteers_register_for_same_event(self, test_db, sample_parish):
        """
        Test multiple volunteers registering:
        1. Create event with capacity for 3
        2. Three different volunteers register
        3. All registrations succeed
        4. Event count is accurate
        """
        # Step 1: Create event
        from app.models.event import Event
        event = Event(
            parish_id=sample_parish.id,
            title="Group Event",
            event_date=datetime.now() + timedelta(days=7),
            max_volunteers=5,
            registered_volunteers=0,
            status="open"
        )
        test_db.add(event)
        test_db.commit()
        
        # Step 2: Register three volunteers
        volunteers = [
            ("vol1@test.com", "Volunteer One"),
            ("vol2@test.com", "Volunteer Two"),
            ("vol3@test.com", "Volunteer Three")
        ]
        
        for email, name in volunteers:
            result = register_volunteer_for_event(
                volunteer_email=email,
                event_id=event.id,
                volunteer_name=name,
                db=test_db
            )
            assert result["success"] is True
        
        # Step 3: Verify event volunteer count
        test_db.refresh(event)
        assert event.registered_volunteers == 3
        
        # Step 4: Verify all registrations in database
        from app.models.registration import Registration
        registrations = test_db.query(Registration).filter(
            Registration.event_id == event.id
        ).all()
        assert len(registrations) == 3