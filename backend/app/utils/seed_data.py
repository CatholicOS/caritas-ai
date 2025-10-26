"""
Seed Data Script
Location: backend/app/utils/seed_data.py

Run this to populate the database with sample data.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from app.core.database import SessionLocal
from app.models import Parish, Event, Volunteer

def seed_parishes(db: Session):
    """Seed parishes with real US locations."""
    parishes_data = [
        {
            "name": "St. Mary's Parish",
            "diocese": "Archdiocese of Washington",
            "address": "520 1st St NE",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20002",
            "phone": "(202) 289-7770",
            "email": "info@stmarysdc.org",
            "services": ["food pantry", "counseling", "financial assistance"],
            "hours": "Mon-Fri: 9 AM - 5 PM",
            "description": "Historic parish serving the Capitol Hill community",
            "latitude": 38.8977,
            "longitude": -77.0074
        },
        {
            "name": "St. Joseph's Church",
            "diocese": "Archdiocese of Baltimore",
            "address": "7429 3rd Ave",
            "city": "Sykesville",
            "state": "MD",
            "zip_code": "21784",
            "phone": "(410) 795-1433",
            "email": "office@stjosephsykesville.org",
            "services": ["food bank", "youth ministry", "elderly care"],
            "hours": "Mon-Sat: 8 AM - 6 PM",
            "description": "Family-oriented parish with active outreach programs",
            "latitude": 39.3723,
            "longitude": -76.9683
        },
        {
            "name": "Cathedral of Mary Our Queen",
            "diocese": "Archdiocese of Baltimore",
            "address": "5200 N Charles St",
            "city": "Baltimore",
            "state": "MD",
            "zip_code": "21210",
            "phone": "(410) 464-4000",
            "email": "info@cmoq.org",
            "services": ["food pantry", "clothing closet", "education"],
            "hours": "Daily: 7 AM - 7 PM",
            "description": "Cathedral parish with extensive social ministries",
            "latitude": 39.3562,
            "longitude": -76.6248
        },
        {
            "name": "St. Anne's Church",
            "diocese": "Archdiocese of Washington",
            "address": "4200 Wisconsin Ave NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20016",
            "phone": "(202) 966-6288",
            "email": "parish@stannedc.org",
            "services": ["tutoring", "immigration assistance", "counseling"],
            "hours": "Mon-Fri: 9 AM - 5 PM, Sat: 10 AM - 2 PM",
            "description": "Vibrant community focused on education and service",
            "latitude": 38.9435,
            "longitude": -77.0843
        },
        {
            "name": "St. Matthew's Cathedral",
            "diocese": "Archdiocese of Washington",
            "address": "1725 Rhode Island Ave NW",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20036",
            "phone": "(202) 347-3215",
            "email": "info@stmatthewscathedral.org",
            "services": ["homeless outreach", "soup kitchen", "job training"],
            "hours": "Daily: 6 AM - 6:30 PM",
            "description": "Downtown cathedral serving the homeless and vulnerable",
            "latitude": 38.9067,
            "longitude": -77.0397
        }
    ]
    
    for data in parishes_data:
        # Create PostGIS point from lat/lng
        lat = data.pop("latitude")
        lng = data.pop("longitude")
        location = WKTElement(f'POINT({lng} {lat})', srid=4326)
        
        parish = Parish(**data, location=location)
        db.add(parish)
    
    db.commit()
    print("✅ Seeded 5 parishes")


def seed_events(db: Session):
    """Seed volunteer events."""
    parishes = db.query(Parish).all()
    
    if not parishes:
        print("❌ No parishes found. Seed parishes first!")
        return
    
    base_date = datetime.now() + timedelta(days=2)
    
    events_data = [
        {
            "parish": parishes[0],  # St. Mary's
            "title": "Weekend Food Pantry",
            "description": "Help sort and distribute food to families in need. No experience necessary!",
            "event_date": base_date + timedelta(days=5),
            "start_time": "9:00 AM",
            "end_time": "12:00 PM",
            "duration_hours": 3,
            "event_type": "food pantry",
            "category": "direct service",
            "skills_needed": ["organization", "compassion"],
            "max_volunteers": 10,
            "coordinator_name": "Maria Garcia",
            "coordinator_email": "maria@stmarysdc.org",
            "coordinator_phone": "(202) 289-7770"
        },
        {
            "parish": parishes[1],  # St. Joseph's
            "title": "Youth Tutoring Program",
            "description": "Tutor middle school students in math and reading. Perfect for teachers or college students!",
            "event_date": base_date + timedelta(days=6),
            "start_time": "2:00 PM",
            "end_time": "4:00 PM",
            "duration_hours": 2,
            "event_type": "education",
            "category": "tutoring",
            "skills_needed": ["teaching", "patience"],
            "max_volunteers": 8,
            "coordinator_name": "John Smith",
            "coordinator_email": "john@stjosephsykesville.org",
            "coordinator_phone": "(410) 795-1433"
        },
        {
            "parish": parishes[2],  # Cathedral of Mary
            "title": "Clothing Closet Volunteer",
            "description": "Help organize donated clothing and assist families in selecting items.",
            "event_date": base_date + timedelta(days=3),
            "start_time": "10:00 AM",
            "end_time": "2:00 PM",
            "duration_hours": 4,
            "event_type": "clothing closet",
            "category": "direct service",
            "skills_needed": ["organization", "customer service"],
            "max_volunteers": 6,
            "coordinator_name": "Sarah Johnson",
            "coordinator_email": "sarah@cmoq.org",
            "coordinator_phone": "(410) 464-4000"
        },
        {
            "parish": parishes[3],  # St. Anne's
            "title": "Homework Help Program",
            "description": "Assist elementary students with homework and reading. Great for college students!",
            "event_date": base_date + timedelta(days=7),
            "start_time": "3:30 PM",
            "end_time": "5:30 PM",
            "duration_hours": 2,
            "event_type": "education",
            "category": "tutoring",
            "skills_needed": ["teaching", "patience"],
            "max_volunteers": 5,
            "coordinator_name": "Emily Brown",
            "coordinator_email": "emily@stannedc.org",
            "coordinator_phone": "(202) 966-6288"
        },
        {
            "parish": parishes[4],  # St. Matthew's
            "title": "Soup Kitchen Service",
            "description": "Serve hot meals to our homeless neighbors. Join us in serving Christ in the least of these.",
            "event_date": base_date + timedelta(days=4),
            "start_time": "6:00 PM",
            "end_time": "8:00 PM",
            "duration_hours": 2,
            "event_type": "soup kitchen",
            "category": "direct service",
            "skills_needed": ["compassion", "food service"],
            "max_volunteers": 12,
            "coordinator_name": "Father Michael",
            "coordinator_email": "fr.michael@stmatthewscathedral.org",
            "coordinator_phone": "(202) 347-3215"
        },
        {
            "parish": parishes[0],  # St. Mary's
            "title": "Home Visit Companions",
            "description": "Visit elderly parishioners who are homebound. Bring companionship and joy!",
            "event_date": base_date + timedelta(days=8),
            "start_time": "1:00 PM",
            "end_time": "4:00 PM",
            "duration_hours": 3,
            "event_type": "elderly care",
            "category": "pastoral care",
            "skills_needed": ["compassion", "listening"],
            "min_age": 21,
            "max_volunteers": 4,
            "coordinator_name": "Sister Anne",
            "coordinator_email": "sisteranne@stmarysdc.org",
            "coordinator_phone": "(202) 289-7770"
        }
    ]
    
    for data in events_data:
        parish = data.pop("parish")
        event = Event(**data, parish_id=parish.id)
        db.add(event)
    
    db.commit()
    print("✅ Seeded 6 volunteer events")


def seed_volunteers(db: Session):
    """Seed sample volunteers."""
    volunteers_data = [
        {
            "first_name": "Christopher",
            "last_name": "Wanjohi",
            "email": "chris@example.com",
            "phone": "(555) 123-4567",
            "city": "Washington",
            "state": "DC",
            "zip_code": "20001",
            "skills": ["technology", "teaching", "web development"],
            "interests": ["youth", "education", "tech"],
            "preferred_days": ["Saturday", "Sunday"],
            "is_verified": True
        },
        {
            "first_name": "James",
            "last_name": "Nartey",
            "email": "james@example.com",
            "phone": "(555) 987-6543",
            "city": "Baltimore",
            "state": "MD",
            "zip_code": "21201",
            "skills": ["cooking", "food service", "community organizing"],
            "interests": ["homeless", "food security"],
            "preferred_days": ["Friday", "Saturday"],
            "is_verified": True
        }
    ]
    
    for data in volunteers_data:
        volunteer = Volunteer(**data)
        db.add(volunteer)
    
    db.commit()
    print("✅ Seeded 2 volunteers")


def main():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    db = SessionLocal()
    try:
        # Check if already seeded
        existing_parishes = db.query(Parish).count()
        if existing_parishes > 0:
            print("⚠️  Database already seeded! Skipping...")
            return
        
        seed_parishes(db)
        seed_events(db)
        seed_volunteers(db)
        
        print("🎉 Database seeded successfully!")
        print("\nSeeded:")
        print(f"  - {db.query(Parish).count()} parishes")
        print(f"  - {db.query(Event).count()} events")
        print(f"  - {db.query(Volunteer).count()} volunteers")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()