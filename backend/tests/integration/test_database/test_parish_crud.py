"""
Integration Tests for Parish CRUD Operations
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.parish import Parish
from app.services.db_service import get_nearby_parishes


@pytest.fixture(scope="function")
def test_db():
    """
    Create an in-memory SQLite database for testing.
    Each test gets a fresh database.
    """
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_parishes(test_db):
    """Fixture that populates database with sample parishes."""
    parishes = [
        Parish(
            name="St. Mary's Church",
            address="123 Main St",
            city="Baltimore",
            state="MD",
            zip_code="21201",
            services=["food pantry", "counseling"],
            is_active=True
        ),
        Parish(
            name="Holy Spirit Parish",
            address="456 Oak Ave",
            city="Baltimore",
            state="MD",
            zip_code="21202",
            services=["tutoring", "food pantry"],
            is_active=True
        ),
        Parish(
            name="St. John's Church",
            address="789 Elm St",
            city="New York",
            state="NY",
            zip_code="10001",
            services=["counseling"],
            is_active=True
        ),
        Parish(
            name="Inactive Parish",
            address="999 Dead End",
            city="Baltimore",
            state="MD",
            services=[],
            is_active=False  # Inactive
        )
    ]
    
    for parish in parishes:
        test_db.add(parish)
    
    test_db.commit()
    
    return parishes


class TestParishCRUD:
    """Test CRUD operations for Parish model with database."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_create_parish_in_database_succeeds(self, test_db):
        """Test that a parish can be created and persisted to database."""
        # Arrange
        parish = Parish(
            name="New Test Church",
            address="100 Test St",
            city="Boston",
            state="MA",
            zip_code="02101",
            services=["food pantry"],
            is_active=True
        )
        
        # Act
        test_db.add(parish)
        test_db.commit()
        test_db.refresh(parish)
        
        # Assert
        assert parish.id is not None  # ID was assigned
        assert parish.name == "New Test Church"
        
        # Verify it's in database
        found = test_db.query(Parish).filter(Parish.name == "New Test Church").first()
        assert found is not None
        assert found.id == parish.id
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_read_parish_by_id_returns_correct_parish(self, test_db, sample_parishes):
        """Test that a parish can be retrieved by ID."""
        # Arrange
        parish_id = sample_parishes[0].id
        
        # Act
        result = test_db.query(Parish).filter(Parish.id == parish_id).first()
        
        # Assert
        assert result is not None
        assert result.name == "St. Mary's Church"
        assert result.city == "Baltimore"
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_update_parish_modifies_database_record(self, test_db, sample_parishes):
        """Test that a parish can be updated in the database."""
        # Arrange
        parish = sample_parishes[0]
        original_name = parish.name
        new_name = "Updated Church Name"
        
        # Act
        parish.name = new_name
        test_db.commit()
        test_db.refresh(parish)
        
        # Assert
        assert parish.name == new_name
        assert parish.name != original_name
        
        # Verify in database
        found = test_db.query(Parish).filter(Parish.id == parish.id).first()
        assert found.name == new_name
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_delete_parish_removes_from_database(self, test_db, sample_parishes):
        """Test that a parish can be deleted from the database."""
        # Arrange
        parish = sample_parishes[0]
        parish_id = parish.id
        
        # Act
        test_db.delete(parish)
        test_db.commit()
        
        # Assert
        found = test_db.query(Parish).filter(Parish.id == parish_id).first()
        assert found is None
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_parishes_by_city_returns_matching_parishes(self, test_db, sample_parishes):
        """Test that parishes can be filtered by city."""
        # Act
        baltimore_parishes = test_db.query(Parish).filter(
            Parish.city == "Baltimore",
            Parish.is_active == True
        ).all()
        
        # Assert
        assert len(baltimore_parishes) == 2  # 2 active Baltimore parishes
        assert all(p.city == "Baltimore" for p in baltimore_parishes)
        assert all(p.is_active for p in baltimore_parishes)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_query_parishes_by_service_returns_matching_parishes(self, test_db, sample_parishes):
        """Test that parishes can be filtered by service offered."""
        # Act
        food_pantry_parishes = test_db.query(Parish).filter(
            Parish.services.contains(["food pantry"])
        ).all()
        
        # Assert
        assert len(food_pantry_parishes) == 2
        assert all("food pantry" in p.services for p in food_pantry_parishes)


class TestGetNearbyParishes:
    """Test the get_nearby_parishes service function."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_nearby_parishes_with_city_returns_matching_parishes(self, test_db, sample_parishes):
        """Test that get_nearby_parishes returns parishes in specified city."""
        # Act
        result = get_nearby_parishes(city="Baltimore", db=test_db)
        
        # Assert
        assert len(result) == 2  # 2 active Baltimore parishes
        assert all(p["city"] == "Baltimore" for p in result)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_nearby_parishes_with_service_filter_returns_filtered_parishes(self, test_db, sample_parishes):
        """Test that get_nearby_parishes filters by service."""
        # Act
        result = get_nearby_parishes(
            city="Baltimore",
            services=["food pantry"],
            db=test_db
        )
        
        # Assert
        assert len(result) == 2
        assert all("food pantry" in p["services"] for p in result)
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_nearby_parishes_with_limit_returns_limited_results(self, test_db, sample_parishes):
        """Test that limit parameter restricts number of results."""
        # Act
        result = get_nearby_parishes(city="Baltimore", limit=1, db=test_db)
        
        # Assert
        assert len(result) == 1
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_nearby_parishes_excludes_inactive_parishes(self, test_db, sample_parishes):
        """Test that inactive parishes are not returned."""
        # Act
        result = get_nearby_parishes(city="Baltimore", db=test_db)
        
        # Assert
        assert all(p["is_active"] for p in result)
        assert len(result) == 2  # Only active ones
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_get_nearby_parishes_with_no_matches_returns_empty_list(self, test_db, sample_parishes):
        """Test that no matches returns empty list, not None or error."""
        # Act
        result = get_nearby_parishes(city="NonexistentCity", db=test_db)
        
        # Assert
        assert result == []
        assert isinstance(result, list)


@pytest.mark.integration
@pytest.mark.database
class TestParishConstraints:
    """Test database constraints and validations."""
    
    def test_duplicate_email_is_allowed(self, test_db):
        """Test that duplicate emails are allowed (no unique constraint)."""
        # Arrange
        parish1 = Parish(name="Church 1", city="NYC", state="NY", email="same@email.com")
        parish2 = Parish(name="Church 2", city="Boston", state="MA", email="same@email.com")
        
        # Act
        test_db.add(parish1)
        test_db.add(parish2)
        test_db.commit()
        
        # Assert - no exception raised
        assert parish1.id is not None
        assert parish2.id is not None
    
    def test_parish_without_required_fields_fails(self, test_db):
        """Test that parishes must have required fields."""
        # Arrange
        parish = Parish()  # Missing required fields
        
        # Act & Assert
        with pytest.raises(Exception):  # Will raise when trying to commit
            test_db.add(parish)
            test_db.commit()