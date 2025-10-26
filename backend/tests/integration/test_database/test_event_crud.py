"""
Integration Tests for Event CRUD Operations

"""

import pytest
from datetime import datetime, timedelta
from app.models.event import Event
from app.models.parish import Parish


class TestEventCRUD:
    """Test CRUD operations for Event model with database."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_create_event_in_database_succeeds(self, test_db, sample_parish):
        """Test that an event can be created and persisted to database."""
        # Arrange
        event = Event(
            parish_id=sample_parish.id,
            title="Test Event",
            description="Test Description",
            event_date=datetime.now() + timedelta(days=7),
            start_time="09:00:00",
            end_time="12:00:00",
            skills_needed=["packing"],
            max_volunteers=10,
            registered_volunteers=0,
            status="open",
            is_active=True
        )
        
        # Act
        test_db.add(event)
        test_db.commit()
        test_db.refresh(event)
        
        # Assert
        assert event.id is not None
        assert event.title == "Test Event"
        
        # Verify in database
        found = test_db.query(Event).filter(Event.title == "Test Event").first()
        assert found is not None
        assert found.id == event.id
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_read_event_by_id_returns_correct_event(self, test_db, sample_event):
        """Test that an event can be retrieved by ID."""
        # Arrange
        event_id = sample_event.id
        
        # Act
        result = test_db.query(Event).filter(Event.id == event_id).first()
        
        # Assert
        assert result is not None
        assert result.title == sample_event.title
        assert result.parish_id == sample_event.parish_id
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_update_event_modifies_database_record(self, test_db, sample_event):
        """Test that an event can be updated in the database."""
        # Arrange
        original_title = sample_event.title
        new_title = "Updated Event Title"
        
        # Act
        sample_event.title = new_title
        test_db.commit()
        test_db.refresh(sample_event)
        
        # Assert
        assert sample_event.title == new_title
        assert sample_event.title != original_title
        
        # Verify in database
        found = test_db.query(Event).filter(Event.id == sample_event.id).first()
        assert found.title == new_title
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_delete_event_removes_from_database(self, test_db, sample_event):
        """Test that an event can be deleted from the database."""
        # Arrange
        event_id = sample_event.id
        
        # Act
        test_db.delete(sample_event)
        test_db.commit()
        
        # Assert
        found = test_db.query(Event).filter(Event.id == event_id).first()
        assert found is None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_future_events_returns_only_upcoming(self, test_db, sample_parish):
        """Test that querying future events excludes past events."""
        # Arrange
        future_event = Event(
            parish_id=sample_parish.id,
            title="Future Event",
            event_date=datetime.now() + timedelta(days=7)
        )
        past_event = Event(
            parish_id=sample_parish.id,
            title="Past Event",
            event_date=datetime.now() - timedelta(days=7)
        )
        
        test_db.add(future_event)
        test_db.add(past_event)
        test_db.commit()
        
        # Act
        future_events = test_db.query(Event).filter(
            Event.event_date > datetime.now()
        ).all()
        
        # Assert
        assert len(future_events) >= 1
        assert all(e.event_date > datetime.now() for e in future_events)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_events_by_parish_returns_matching_events(self, test_db, multiple_events):
        """Test that events can be filtered by parish."""
        # Arrange
        parish_id = multiple_events[0].parish_id
        
        # Act
        parish_events = test_db.query(Event).filter(
            Event.parish_id == parish_id
        ).all()
        
        # Assert
        assert len(parish_events) >= len(multiple_events)
        assert all(e.parish_id == parish_id for e in parish_events)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_events_by_status_returns_matching_events(self, test_db, sample_parish):
        """Test that events can be filtered by status."""
        # Arrange
        open_event = Event(
            parish_id=sample_parish.id,
            title="Open Event",
            event_date=datetime.now() + timedelta(days=7),
            status="open"
        )
        full_event = Event(
            parish_id=sample_parish.id,
            title="Full Event",
            event_date=datetime.now() + timedelta(days=7),
            status="full"
        )
        
        test_db.add(open_event)
        test_db.add(full_event)
        test_db.commit()
        
        # Act
        open_events = test_db.query(Event).filter(Event.status == "open").all()
        
        # Assert
        assert len(open_events) >= 1
        assert all(e.status == "open" for e in open_events)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_events_by_skills_returns_matching_events(self, test_db, sample_parish):
        """Test that events can be filtered by required skills."""
        # Arrange
        packing_event = Event(
            parish_id=sample_parish.id,
            title="Packing Event",
            event_date=datetime.now() + timedelta(days=7),
            skills_needed=["packing", "sorting"]
        )
        teaching_event = Event(
            parish_id=sample_parish.id,
            title="Teaching Event",
            event_date=datetime.now() + timedelta(days=7),
            skills_needed=["teaching"]
        )
        
        test_db.add(packing_event)
        test_db.add(teaching_event)
        test_db.commit()
        
        # Act
        packing_events = test_db.query(Event).filter(
            Event.skills_needed.any("packing")
        ).all()
        
        # Assert
        assert len(packing_events) >= 1
        assert all("packing" in (e.skills_needed or []) for e in packing_events)


class TestEventAvailability:
    """Test event availability and capacity logic with database."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_increment_registered_volunteers_persists(self, test_db, sample_event):
        """Test that incrementing registered volunteers persists to database."""
        # Arrange
        original_count = sample_event.registered_volunteers
        
        # Act
        sample_event.registered_volunteers += 1
        test_db.commit()
        test_db.refresh(sample_event)
        
        # Assert
        assert sample_event.registered_volunteers == original_count + 1
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_event_status_changes_to_full_when_capacity_reached(self, test_db, sample_parish):
        """Test that event status updates to full when max volunteers reached."""
        # Arrange
        event = Event(
            parish_id=sample_parish.id,
            title="Limited Event",
            event_date=datetime.now() + timedelta(days=7),
            max_volunteers=5,
            registered_volunteers=4,
            status="open"
        )
        test_db.add(event)
        test_db.commit()
        
        # Act
        event.registered_volunteers += 1
        if event.registered_volunteers >= event.max_volunteers:
            event.status = "full"
        test_db.commit()
        test_db.refresh(event)
        
        # Assert
        assert event.registered_volunteers == 5
        assert event.status == "full"


class TestEventWithParish:
    """Test event relationships with parish."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_event_has_parish_relationship(self, test_db, sample_event):
        """Test that event can access its parish through relationship."""
        # Act
        parish = sample_event.parish
        
        # Assert
        assert parish is not None
        assert parish.id == sample_event.parish_id
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_parish_has_events_relationship(self, test_db, sample_parish, sample_event):
        """Test that parish can access its events through relationship."""
        # Act
        events = sample_parish.events
        
        # Assert
        assert len(events) >= 1
        assert any(e.id == sample_event.id for e in events)


class TestEventDateFiltering:
    """Test date-based filtering of events."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_events_by_date_range_returns_matching_events(self, test_db, sample_parish):
        """Test filtering events by date range."""
        # Arrange
        start_date = datetime.now() + timedelta(days=5)
        end_date = datetime.now() + timedelta(days=15)
        
        in_range_event = Event(
            parish_id=sample_parish.id,
            title="In Range Event",
            event_date=datetime.now() + timedelta(days=10)
        )
        out_range_event = Event(
            parish_id=sample_parish.id,
            title="Out of Range Event",
            event_date=datetime.now() + timedelta(days=30)
        )
        
        test_db.add(in_range_event)
        test_db.add(out_range_event)
        test_db.commit()
        
        # Act
        events = test_db.query(Event).filter(
            Event.event_date >= start_date,
            Event.event_date <= end_date
        ).all()
        
        # Assert
        assert in_range_event in events
        assert out_range_event not in events
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_weekend_events_returns_correct_events(self, test_db, sample_parish):
        """Test filtering events for weekends."""
        # Arrange - Find next Saturday
        today = datetime.now()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        saturday = today + timedelta(days=days_until_saturday)
        sunday = saturday + timedelta(days=1)
        
        saturday_event = Event(
            parish_id=sample_parish.id,
            title="Saturday Event",
            event_date=saturday
        )
        test_db.add(saturday_event)
        test_db.commit()
        
        # Act
        weekend_events = test_db.query(Event).filter(
            Event.event_date >= saturday,
            Event.event_date <= sunday
        ).all()
        
        # Assert
        assert len(weekend_events) >= 1
        assert saturday_event in weekend_events