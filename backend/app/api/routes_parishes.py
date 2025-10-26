"""
Parish API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.parish import Parish

router = APIRouter()


@router.get("/parishes", tags=["parishes"])
def get_parishes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    city: Optional[str] = None,
    state: Optional[str] = None,
    service: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of parishes with optional filters.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **city**: Filter by city name (partial match)
    - **state**: Filter by state code (exact match)
    - **service**: Filter by service type (partial match in services array)
    """
    query = db.query(Parish).filter(Parish.is_active == True)
    
    if city:
        query = query.filter(Parish.city.ilike(f"%{city}%"))
    
    if state:
        query = query.filter(Parish.state == state.upper())
    
    if service:
        # PostgreSQL array contains check
        query = query.filter(Parish.services.any(service.lower()))
    
    total = query.count()
    parishes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "parishes": [p.to_dict() for p in parishes]
    }


@router.get("/parishes/{parish_id}", tags=["parishes"])
def get_parish(parish_id: int, db: Session = Depends(get_db)):
    """Get a specific parish by ID."""
    parish = db.query(Parish).filter(Parish.id == parish_id).first()
    
    if not parish:
        raise HTTPException(status_code=404, detail="Parish not found")
    
    return parish.to_dict()


@router.get("/parishes/search/{name}", tags=["parishes"])
def search_parishes_by_name(
    name: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search parishes by name (partial match)."""
    parishes = db.query(Parish).filter(
        Parish.name.ilike(f"%{name}%"),
        Parish.is_active == True
    ).limit(limit).all()
    
    return {
        "query": name,
        "count": len(parishes),
        "parishes": [p.to_dict() for p in parishes]
    }


@router.get("/parishes/by-state/{state}", tags=["parishes"])
def get_parishes_by_state(
    state: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get all parishes in a specific state."""
    query = db.query(Parish).filter(
        Parish.state == state.upper(),
        Parish.is_active == True
    )
    
    total = query.count()
    parishes = query.offset(skip).limit(limit).all()
    
    return {
        "state": state.upper(),
        "total": total,
        "skip": skip,
        "limit": limit,
        "parishes": [p.to_dict() for p in parishes]
    }


@router.get("/states", tags=["parishes"])
def get_states(db: Session = Depends(get_db)):
    """Get list of all states that have parishes."""
    states = db.query(Parish.state).filter(
        Parish.state.isnot(None),
        Parish.is_active == True
    ).distinct().order_by(Parish.state).all()
    
    return {
        "states": [s[0] for s in states if s[0]]
    }