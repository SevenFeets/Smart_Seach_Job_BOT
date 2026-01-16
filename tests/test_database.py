"""Tests for the database module."""
import pytest
import tempfile
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import JobRepository, Job, ApplicationStatus


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    repo = JobRepository(f"sqlite:///{db_path}")
    yield repo
    
    # Cleanup
    os.unlink(db_path)


class TestJobRepository:
    """Test cases for JobRepository."""
    
    def test_add_job(self, temp_db):
        """Test adding a job to the database."""
        job_data = {
            "linkedin_job_id": "12345",
            "title": "Software Engineer",
            "company": "Test Company",
            "location": "Remote",
            "is_easy_apply": True,
            "search_keyword": "Python"
        }
        
        job = temp_db.add_job(job_data)
        
        assert job is not None
        assert job.linkedin_job_id == "12345"
        assert job.title == "Software Engineer"
        assert job.is_easy_apply == True
    
    def test_job_exists(self, temp_db):
        """Test checking if a job exists."""
        job_data = {
            "linkedin_job_id": "12345",
            "title": "Software Engineer",
            "company": "Test Company"
        }
        
        assert temp_db.job_exists("12345") == False
        temp_db.add_job(job_data)
        assert temp_db.job_exists("12345") == True
    
    def test_no_duplicate_jobs(self, temp_db):
        """Test that duplicate jobs are not added."""
        job_data = {
            "linkedin_job_id": "12345",
            "title": "Software Engineer",
            "company": "Test Company"
        }
        
        job1 = temp_db.add_job(job_data)
        job2 = temp_db.add_job(job_data)
        
        assert job1 is not None
        assert job2 is None  # Duplicate should return None
    
    def test_batch_add_jobs(self, temp_db):
        """Test adding multiple jobs in batch."""
        jobs_data = [
            {"linkedin_job_id": "1", "title": "Job 1", "company": "Company 1"},
            {"linkedin_job_id": "2", "title": "Job 2", "company": "Company 2"},
            {"linkedin_job_id": "3", "title": "Job 3", "company": "Company 3"},
        ]
        
        added = temp_db.add_jobs_batch(jobs_data)
        
        assert len(added) == 3
        assert temp_db.get_job_count() == 3
    
    def test_create_application(self, temp_db):
        """Test creating an application."""
        job_data = {
            "linkedin_job_id": "12345",
            "title": "Software Engineer",
            "company": "Test Company"
        }
        job = temp_db.add_job(job_data)
        
        application = temp_db.create_application(
            job_id=job.id,
            status=ApplicationStatus.PENDING
        )
        
        assert application is not None
        assert application.job_id == job.id
        assert application.status == ApplicationStatus.PENDING.value
    
    def test_update_application_status(self, temp_db):
        """Test updating application status."""
        job_data = {
            "linkedin_job_id": "12345",
            "title": "Software Engineer",
            "company": "Test Company"
        }
        job = temp_db.add_job(job_data)
        application = temp_db.create_application(job.id)
        
        updated = temp_db.update_application_status(
            application.id,
            ApplicationStatus.EASY_APPLY
        )
        
        assert updated.status == ApplicationStatus.EASY_APPLY.value
        assert updated.applied_at is not None
    
    def test_get_application_stats(self, temp_db):
        """Test getting application statistics."""
        # Add some jobs and applications
        for i in range(5):
            job = temp_db.add_job({
                "linkedin_job_id": str(i),
                "title": f"Job {i}",
                "company": f"Company {i}",
                "is_easy_apply": True
            })
            if i < 3:
                temp_db.create_application(job.id, ApplicationStatus.EASY_APPLY)
        
        stats = temp_db.get_application_stats()
        
        assert stats["total_jobs"] == 5
        assert stats["total_applications"] == 3
        assert stats["easy_apply"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
