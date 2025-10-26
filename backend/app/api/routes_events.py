"""
Event API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.models.event import Event
from app.models.parish import Parish

router = APIRouter()


@router.get("/events", tags=["events"])
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    parish_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    skill: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of events with optional filters.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **parish_id**: Filter by parish ID
    - **status**: Filter by status (open, closed, full)
    - **from_date**: Filter events from this date (YYYY-MM-DD)
    - **to_date**: Filter events until this date (YYYY-MM-DD)
    - **skill**: Filter by required skill (partial match in skills array)
    """
    query = db.query(Event).filter(Event.is_active == True)
    
    if parish_id:
        query = query.filter(Event.parish_id == parish_id)
    
    if status:
        query = query.filter(Event.status == status.lower())
    
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(Event.event_date >= from_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid from_date format. Use YYYY-MM-DD")
    
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            query = query.filter(Event.event_date <= to_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid to_date format. Use YYYY-MM-DD")
    
    if skill:
        # PostgreSQL array contains check
        query = query.filter(Event.skills_needed.any(skill.lower()))
    
    # Order by event date (upcoming first)
    query = query.order_by(Event.event_date)
    
    total = query.count()
    events = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "events": [e.to_dict() for e in events]
    }


@router.get("/events/{event_id}", tags=["events"])
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event.to_dict()


@router.get("/events/upcoming", tags=["events"])
def get_upcoming_events(
    limit: int = Query(50, ge=1, le=500),
    parish_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get upcoming events (future dates only)."""
    query = db.query(Event).filter(
        Event.is_active == True,
        Event.event_date >= datetime.now(),
        Event.status == 'open'
    )
    
    if parish_id:
        query = query.filter(Event.parish_id == parish_id)
    
    query = query.order_by(Event.event_date).limit(limit)
    events = query.all()
    
    return {
        "count": len(events),
        "events": [e.to_dict() for e in events]
    }


@router.get("/events/by-parish/{parish_id}", tags=["events"])
def get_events_by_parish(
    parish_id: int,
    upcoming_only: bool = True,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get all events for a specific parish."""
    # Check if parish exists
    parish = db.query(Parish).filter(Parish.id == parish_id).first()
    if not parish:
        raise HTTPException(status_code=404, detail="Parish not found")
    
    query = db.query(Event).filter(
        Event.parish_id == parish_id,
        Event.is_active == True
    )
    
    if upcoming_only:
        query = query.filter(Event.event_date >= datetime.now())
    
    query = query.order_by(Event.event_date).limit(limit)
    events = query.all()
    
    return {
        "parish_id": parish_id,
        "parish_name": parish.name,
        "count": len(events),
        "events": [e.to_dict() for e in events]
    }


@router.get("/events/search/{title}", tags=["events"])
def search_events_by_title(
    title: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search events by title (partial match)."""
    events = db.query(Event).filter(
        Event.title.ilike(f"%{title}%"),
        Event.is_active == True
    ).order_by(Event.event_date).limit(limit).all()
    
    return {
        "query": title,
        "count": len(events),
        "events": [e.to_dict() for e in events]
    }


@router.get("/skills", tags=["events"])
def get_all_skills(db: Session = Depends(get_db)):
    """Get list of all unique skills needed across all events."""
    from sqlalchemy import func
    
    # Get all events with skills
    events = db.query(Event.skills_needed).filter(
        Event.skills_needed.isnot(None),
        Event.is_active == True
    ).all()
    
    # Flatten the list of skills
    all_skills = set()
    for event in events:
        if event[0]:  # skills_needed is a list
            all_skills.update(event[0])
    
    return {
        "skills": sorted(list(all_skills))
    }