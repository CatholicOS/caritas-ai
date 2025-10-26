"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2025-10-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create parishes table
    op.create_table('parishes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('diocese', sa.String(length=200), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('services', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('hours', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parishes_id'), 'parishes', ['id'], unique=False)
    op.create_index(op.f('ix_parishes_name'), 'parishes', ['name'], unique=False)
    op.create_index(op.f('ix_parishes_city'), 'parishes', ['city'], unique=False)
    
    # Create spatial index on location
    op.execute('CREATE INDEX IF NOT EXISTS idx_parishes_location ON parishes USING GIST(location)')    
    # Create volunteers table
    op.create_table('volunteers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('skills', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('interests', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('languages', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('availability', sa.Text(), nullable=True),
        sa.Column('preferred_days', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('previous_experience', sa.Text(), nullable=True),
        sa.Column('hours_volunteered', sa.Integer(), nullable=True),
        sa.Column('events_attended', sa.Integer(), nullable=True),
        sa.Column('home_parish', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('background_check_status', sa.String(length=50), nullable=True),
        sa.Column('max_distance_miles', sa.Integer(), nullable=True),
        sa.Column('notification_preferences', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('emergency_contact_name', sa.String(length=100), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_volunteers_id'), 'volunteers', ['id'], unique=False)
    op.create_index(op.f('ix_volunteers_email'), 'volunteers', ['email'], unique=True)
    op.create_index(op.f('ix_volunteers_city'), 'volunteers', ['city'], unique=False)
    
    # Create events table
    op.create_table('events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('parish_id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.DateTime(), nullable=False),
        sa.Column('start_time', sa.String(length=20), nullable=True),
        sa.Column('end_time', sa.String(length=20), nullable=True),
        sa.Column('duration_hours', sa.Integer(), nullable=True),
        sa.Column('location_name', sa.String(length=200), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('skills_needed', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('min_age', sa.Integer(), nullable=True),
        sa.Column('max_volunteers', sa.Integer(), nullable=True),
        sa.Column('registered_volunteers', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_full', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('coordinator_name', sa.String(length=100), nullable=True),
        sa.Column('coordinator_email', sa.String(length=100), nullable=True),
        sa.Column('coordinator_phone', sa.String(length=20), nullable=True),
        sa.Column('what_to_bring', sa.Text(), nullable=True),
        sa.Column('parking_info', sa.Text(), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['parish_id'], ['parishes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_title'), 'events', ['title'], unique=False)
    op.create_index(op.f('ix_events_parish_id'), 'events', ['parish_id'], unique=False)
    op.create_index(op.f('ix_events_event_date'), 'events', ['event_date'], unique=False)
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    
    # Create registrations table
    op.create_table('registrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('volunteer_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('registration_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('checked_in', sa.Boolean(), nullable=True),
        sa.Column('check_in_time', sa.DateTime(), nullable=True),
        sa.Column('check_out_time', sa.DateTime(), nullable=True),
        sa.Column('hours_served', sa.Integer(), nullable=True),
        sa.Column('volunteer_notes', sa.Text(), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('confirmation_sent', sa.Boolean(), nullable=True),
        sa.Column('reminder_sent', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.ForeignKeyConstraint(['volunteer_id'], ['volunteers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_registrations_id'), 'registrations', ['id'], unique=False)
    op.create_index(op.f('ix_registrations_volunteer_id'), 'registrations', ['volunteer_id'], unique=False)
    op.create_index(op.f('ix_registrations_event_id'), 'registrations', ['event_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_registrations_event_id'), table_name='registrations')
    op.drop_index(op.f('ix_registrations_volunteer_id'), table_name='registrations')
    op.drop_index(op.f('ix_registrations_id'), table_name='registrations')
    op.drop_table('registrations')
    
    op.drop_index(op.f('ix_events_event_type'), table_name='events')
    op.drop_index(op.f('ix_events_event_date'), table_name='events')
    op.drop_index(op.f('ix_events_parish_id'), table_name='events')
    op.drop_index(op.f('ix_events_title'), table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')
    
    op.drop_index(op.f('ix_volunteers_city'), table_name='volunteers')
    op.drop_index(op.f('ix_volunteers_email'), table_name='volunteers')
    op.drop_index(op.f('ix_volunteers_id'), table_name='volunteers')
    op.drop_table('volunteers')
    
    op.execute('DROP INDEX IF EXISTS idx_parishes_location')
    op.drop_index(op.f('ix_parishes_city'), table_name='parishes')
    op.drop_index(op.f('ix_parishes_name'), table_name='parishes')
    op.drop_index(op.f('ix_parishes_id'), table_name='parishes')
    op.drop_table('parishes')
    
    op.execute('DROP EXTENSION IF EXISTS postgis')