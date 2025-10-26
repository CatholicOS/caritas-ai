"""
WORKING CSV Import
"""

import csv
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from app.core.config import settings
from app.core.database import Base


def parse_services(services_str: str) -> List[str]:
    """Parse comma-separated services into list."""
    if not services_str or services_str.strip() == "":
        return []
    return [s.strip() for s in services_str.split(",") if s.strip()]


def parse_date(date_str: str) -> datetime:
    """Parse date string in multiple formats."""
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse date: {date_str}")


def import_parishes(session: Session, csv_file: Path, batch_size: int = 100) -> int:
    """Import parishes using raw SQL."""
    total_count = 0
    errors = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [field.strip().upper() for field in reader.fieldnames]
        
        print(f"📋 CSV Columns: {', '.join(reader.fieldnames)}")
        print(f"📦 Batch size: {batch_size}")
        print()
        
        batch_data = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                name = row.get('NAME', '').strip()
                if not name:
                    errors.append(f"Row {row_num}: Missing NAME")
                    continue
                
                if len(name) > 255:
                    name = name[:255]
                
                services = parse_services(row.get('SERVICES', ''))
                
                batch_data.append({
                    'name': name,
                    'address': row.get('STREET', '').strip()[:255] if row.get('STREET') else None,
                    'city': row.get('CITY', '').strip()[:100] if row.get('CITY') else None,
                    'state': row.get('STATE', '').strip()[:2] if row.get('STATE') else None,
                    'zip_code': row.get('ZIP', '').strip()[:10] if row.get('ZIP') else None,
                    'email': row.get('EMAIL', '').strip()[:255] if row.get('EMAIL') else None,
                    'services': services  # Pass as list, not string
                })
                
                if len(batch_data) >= batch_size:
                    try:
                        for data in batch_data:
                            # Check if exists
                            result = session.execute(
                                text("SELECT id FROM parishes WHERE name = :name LIMIT 1"),
                                {'name': data['name']}
                            ).fetchone()
                            
                            if not result:
                                session.execute(
                                    text("""
                                        INSERT INTO parishes 
                                        (name, address, city, state, zip_code, email, services, is_active, created_at)
                                        VALUES 
                                        (:name, :address, :city, :state, :zip_code, :email, :services, true, NOW())
                                    """),
                                    {
                                        'name': data['name'],
                                        'address': data['address'],
                                        'city': data['city'],
                                        'state': data['state'],
                                        'zip_code': data['zip_code'],
                                        'email': data['email'],
                                        'services': data['services']  # Pass as list
                                    }
                                )
                                total_count += 1
                        
                        session.commit()
                        print(f"✓ Batch committed: {total_count} parishes imported")
                        batch_data = []
                        
                    except Exception as e:
                        session.rollback()
                        errors.append(f"Batch ~row {row_num}: {str(e)[:150]}")
                        print(f"⚠️  Batch failed at row {row_num}: {str(e)[:100]}")
                        batch_data = []
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)[:100]}")
        
        # Final batch
        if batch_data:
            try:
                for data in batch_data:
                    result = session.execute(
                        text("SELECT id FROM parishes WHERE name = :name LIMIT 1"),
                        {'name': data['name']}
                    ).fetchone()
                    
                    if not result:
                        session.execute(
                            text("""
                                INSERT INTO parishes 
                                (name, address, city, state, zip_code, email, services, is_active, created_at)
                                VALUES 
                                (:name, :address, :city, :state, :zip_code, :email, :services, true, NOW())
                            """),
                            {
                                'name': data['name'],
                                'address': data['address'],
                                'city': data['city'],
                                'state': data['state'],
                                'zip_code': data['zip_code'],
                                'email': data['email'],
                                'services': data['services']  # Pass as list
                            }
                        )
                        total_count += 1
                
                session.commit()
                print(f"✓ Final batch committed: {total_count} total parishes")
            except Exception as e:
                session.rollback()
                errors.append(f"Final batch: {str(e)[:150]}")
    
    print()
    print("=" * 60)
    print(f"✅ Successfully imported {total_count} parishes")
    if errors:
        print(f"⚠️  {len(errors)} errors:")
        for error in errors[:10]:
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
    print("=" * 60)
    
    return total_count


def import_events(session: Session, csv_file: Path, batch_size: int = 50) -> int:
    """Import events using raw SQL."""
    total_count = 0
    errors = []
    
    # Cache parish lookups
    parish_cache = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [field.strip().upper() for field in reader.fieldnames]
        
        print(f"📋 CSV Columns: {', '.join(reader.fieldnames)}")
        print(f"📦 Batch size: {batch_size}")
        print()
        
        batch_data = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                title = row.get('TITLE', '').strip()
                if not title or len(title) > 255:
                    errors.append(f"Row {row_num}: Invalid TITLE")
                    continue
                
                event_date_str = row.get('EVENT_DATE', '').strip()
                if not event_date_str:
                    errors.append(f"Row {row_num}: Missing EVENT_DATE")
                    continue
                
                try:
                    event_date = parse_date(event_date_str)
                except:
                    errors.append(f"Row {row_num}: Invalid date '{event_date_str}'")
                    continue
                
                parish_name = row.get('PARISH', '').strip()
                if not parish_name:
                    errors.append(f"Row {row_num}: Missing PARISH")
                    continue
                
                # Check cache first
                if parish_name not in parish_cache:
                    result = session.execute(
                        text("SELECT id FROM parishes WHERE name ILIKE :name LIMIT 1"),
                        {'name': f'%{parish_name}%'}
                    ).fetchone()
                    
                    if result:
                        parish_cache[parish_name] = result[0]
                    else:
                        errors.append(f"Row {row_num}: Parish '{parish_name[:30]}...' not found")
                        continue
                
                parish_id = parish_cache[parish_name]
                
                skills = parse_services(row.get('SKILLS_NEEDED', ''))
                
                max_vol_str = row.get('MAX_VOLUNTEERS', '').strip()
                max_volunteers = int(max_vol_str) if max_vol_str and max_vol_str.isdigit() else None
                
                batch_data.append({
                    'parish_id': parish_id,
                    'title': title,
                    'description': row.get('EVENT_DESCRIPTION', '').strip() or None,
                    'event_date': event_date.isoformat(),
                    'skills_needed': skills,  # Pass as list
                    'max_volunteers': max_volunteers
                })
                
                if len(batch_data) >= batch_size:
                    try:
                        for data in batch_data:
                            session.execute(
                                text("""
                                    INSERT INTO events 
                                    (parish_id, title, description, event_date, skills_needed, max_volunteers, 
                                     registered_volunteers, is_active, status, created_at)
                                    VALUES 
                                    (:parish_id, :title, :description, :event_date, :skills_needed, 
                                     :max_volunteers, 0, true, 'open', NOW())
                                """),
                                data
                            )
                            total_count += 1
                        
                        session.commit()
                        print(f"✓ Batch committed: {total_count} events imported")
                        batch_data = []
                    except Exception as e:
                        session.rollback()
                        errors.append(f"Batch ~row {row_num}: {str(e)[:150]}")
                        print(f"⚠️  Batch failed at row {row_num}")
                        batch_data = []
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)[:100]}")
        
        # Final batch
        if batch_data:
            try:
                for data in batch_data:
                    session.execute(
                        text("""
                            INSERT INTO events 
                            (parish_id, title, description, event_date, skills_needed, max_volunteers, 
                             registered_volunteers, is_active, status, created_at)
                            VALUES 
                            (:parish_id, :title, :description, :event_date, :skills_needed, 
                             :max_volunteers, 0, true, 'open', NOW())
                        """),
                        data
                    )
                    total_count += 1
                
                session.commit()
                print(f"✓ Final batch: {total_count} total events")
            except Exception as e:
                session.rollback()
                errors.append(f"Final batch: {str(e)[:150]}")
    
    print()
    print("=" * 60)
    print(f"✅ Successfully imported {total_count} events")
    if errors:
        print(f"⚠️  {len(errors)} errors:")
        for error in errors[:10]:
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
    print("=" * 60)
    
    return total_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--type', required=True, choices=['parishes', 'events'])
    parser.add_argument('--batch-size', type=int, default=100)
    
    args = parser.parse_args()
    csv_path = Path(args.file)
    
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print(f"🚀 CaritasAI CSV Import (WORKING VERSION)")
    print(f"📁 File: {csv_path}")
    print(f"📊 Type: {args.type}")
    print("=" * 60)
    print()
    
    try:
        db_url = settings.DATABASE_URL or os.getenv('DATABASE_URL')
        engine = create_engine(db_url)
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
    except Exception as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    
    try:
        if args.type == 'parishes':
            count = import_parishes(session, csv_path, args.batch_size)
        else:
            count = import_events(session, csv_path, args.batch_size)
        
        print()
        print(f"✅ Total imported: {count}")
        print()
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()