"""
Database Service 

"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from app.core.database import SessionLocal
from app.models.parish import Parish
from app.models.event import Event
from app.models.volunteer import Volunteer
from app.models.registration import Registration

logger = logging.getLogger(__name__)


def get_nearby_parishes(
    city: str = None,
    services: List[str] = None,
    limit: int = 10,
    db: Session = None
) -> List[Dict]:
    """
    Find parishes near a location with optional service filtering.
    
    Args:
        city: City name to search
        services: List of services to filter by
        limit: Maximum number of results
        db: Database session (optional, for testing)
    """
    # Use provided db or create new session
    db_session = db if db is not None else SessionLocal()
    
    try:
        # Build query
        query = db_session.query(Parish).filter(Parish.is_active == True)
        
        # Filter by city if provided
        if city:
            query = query.filter(Parish.city.ilike(f"%{city}%"))
        
        # Filter by services if provided (works with PostgreSQL arrays)
        if services:
            for service in services:
                query = query.filter(Parish.services.any(service))
        
        # Execute query
        parishes = query.limit(limit).all()
        
        # Convert to dict
        return [parish.to_dict() for parish in parishes]
        
    except Exception as e:
        logger.error(f"Error finding parishes: {e}")
        return []
    finally:
        # Only close if we created the session
        if db is None:
            db_session.close()


def search_volunteer_events(
    location: str = None,
    skills: List[str] = None,
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 10,
    db: Session = None
) -> List[Dict]:
    """
    Search for volunteer events with various filters.
    
    Args:
        location: City/location to search
        skills: Required skills
        start_date: Filter events from this date
        end_date: Filter events until this date
        limit: Maximum number of results
        db: Database session (optional, for testing)
    """
    db_session = db if db is not None else SessionLocal()
    
    try:
        # Build query - join with parish to get location info
        query = db_session.query(Event).join(Parish).filter(
            Event.is_active == True,
            Event.status == "open",
            Event.event_date > datetime.now()  # Only future events
        )
        
        # Filter by location
        if location:
            query = query.filter(Parish.city.ilike(f"%{location}%"))
        
        # Filter by date range
        if start_date:
            query = query.filter(Event.event_date >= start_date)
        
        if end_date:
            query = query.filter(Event.event_date <= end_date)
        
        # Filter by skills if provided (works with PostgreSQL arrays)
        if skills:
            for skill in skills:
                query = query.filter(Event.skills_needed.any(skill))
        
        # Order by date
        query = query.order_by(Event.event_date)
        
        # Execute query
        events = query.limit(limit).all()
        
        # Convert to dict with parish info
        result = []
        for event in events:
            event_dict = event.to_dict()
            # Add parish info
            event_dict["parish_name"] = event.parish.name
            event_dict["parish_city"] = event.parish.city
            event_dict["parish_address"] = event.parish.address
            result.append(event_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching events: {e}")
        return []
    finally:
        if db is None:
            db_session.close()


def register_volunteer_for_event(
    volunteer_email: str,
    event_id: int,
    volunteer_name: str = None,
    db: Session = None
) -> Dict:
    """
    Register a volunteer for an event.
    
    Args:
        volunteer_email: Volunteer's email
        event_id: Event ID
        volunteer_name: Volunteer's name (for new volunteers)
        db: Database session (optional, for testing)
    """
    db_session = db if db is not None else SessionLocal()
    
    try:
        # Check if event exists
        event = db_session.query(Event).filter(Event.id == event_id).first()
        if not event:
            return {
                "success": False,
                "error": "Event not found"
            }
        
        # Check if event is full
        if event.max_volunteers and event.registered_volunteers >= event.max_volunteers:
            return {
                "success": False,
                "error": "Event is full"
            }
        
        # Find or create volunteer
        volunteer = db_session.query(Volunteer).filter(
            Volunteer.email == volunteer_email
        ).first()
        
        if not volunteer:
            # Create new volunteer
            if not volunteer_name:
                return {
                    "success": False,
                    "error": "Volunteer name required for new volunteers"
                }
            
            # Parse name
            name_parts = volunteer_name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            volunteer = Volunteer(
                first_name=first_name,
                last_name=last_name,
                email=volunteer_email,
                is_active=True
            )
            db_session.add(volunteer)
            db_session.flush()  # Get volunteer ID
        
        # Check if already registered
        existing = db_session.query(Registration).filter(
            Registration.volunteer_id == volunteer.id,
            Registration.event_id == event_id
        ).first()
        
        if existing:
            return {
                "success": False,
                "error": "Volunteer already registered for this event"
            }
        
        # Create registration
        registration = Registration(
            volunteer_id=volunteer.id,
            event_id=event_id,
            registration_date=datetime.now(),  # Set registration date!
            status="confirmed"
        )
        db_session.add(registration)
        
        # Update event volunteer count
        event.registered_volunteers += 1
        
        # Update status if full
        if event.max_volunteers and event.registered_volunteers >= event.max_volunteers:
            event.status = "full"
        
        # Commit changes
        db_session.commit()
        
        # Get parish info for response
        parish = event.parish
        
        return {
            "success": True,
            "registration_id": registration.id,
            "volunteer_name": f"{volunteer.first_name} {volunteer.last_name}",
            "event_title": event.title,
            "event_date": event.event_date.isoformat(),
            "parish_name": parish.name,
            "coordinator": "Parish Coordinator",
            "coordinator_email": parish.email or "contact@parish.org"
        }
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error registering volunteer: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        if db is None:
            db_session.close()


def get_parish_analytics(
    parish_name: str,
    db: Session = None
) -> Dict:
    """
    Get analytics for a specific parish.
    
    Args:
        parish_name: Parish name (partial match)
        db: Database session (optional, for testing)
    """
    db_session = db if db is not None else SessionLocal()
    
    try:
        # Find parish
        parish = db_session.query(Parish).filter(
            Parish.name.ilike(f"%{parish_name}%")
        ).first()
        
        if not parish:
            return {"error": "Parish not found"}
        
        # Get upcoming events
        upcoming_events = db_session.query(Event).filter(
            Event.parish_id == parish.id,
            Event.event_date > datetime.now(),
            Event.is_active == True
        ).count()
        
        # Get past events
        past_events = db_session.query(Event).filter(
            Event.parish_id == parish.id,
            Event.event_date <= datetime.now()
        ).count()
        
        # Get total events
        total_events = db_session.query(Event).filter(
            Event.parish_id == parish.id
        ).count()
        
        # Get total registrations
        total_registrations = db_session.query(Registration).join(Event).filter(
            Event.parish_id == parish.id
        ).count()
        
        # Get this month's stats
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        month_events = db_session.query(Event).filter(
            Event.parish_id == parish.id,
            Event.event_date >= month_start,
            Event.event_date < next_month
        ).count()
        
        month_registrations = db_session.query(Registration).join(Event).filter(
            Event.parish_id == parish.id,
            Registration.created_at >= month_start,
            Registration.created_at < next_month
        ).count()
        
        return {
            "parish_id": parish.id,
            "parish_name": parish.name,
            "city": parish.city,
            "total_events": total_events,
            "upcoming_events": upcoming_events,
            "past_events": past_events,
            "total_registrations": total_registrations,
            "services_offered": parish.services or [],
            "this_month": {
                "events": month_events,
                "registrations": month_registrations
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting parish analytics: {e}")
        return {"error": str(e)}
    finally:
        if db is None:
            db_session.close()