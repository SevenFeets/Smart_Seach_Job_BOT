"""Database repository for job operations."""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, Job, Application, ApplicationStatus
from ..config import get_settings


class JobRepository:
    """Repository for job and application database operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the repository with database connection."""
        settings = get_settings()
        self.database_url = database_url or settings.database_url
        
        # Ensure data directory exists
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(self.database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    # ==================== Job Operations ====================
    
    def job_exists(self, linkedin_job_id: str) -> bool:
        """Check if a job already exists in the database."""
        with self.get_session() as session:
            return session.query(Job).filter(
                Job.linkedin_job_id == linkedin_job_id
            ).first() is not None
    
    def add_job(self, job_data: dict) -> Optional[Job]:
        """Add a new job to the database if it doesn't exist."""
        if self.job_exists(job_data.get("linkedin_job_id", "")):
            return None
        
        with self.get_session() as session:
            job = Job(**job_data)
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
    
    def add_jobs_batch(self, jobs_data: List[dict]) -> List[Job]:
        """Add multiple jobs, skipping duplicates."""
        added_jobs = []
        with self.get_session() as session:
            for job_data in jobs_data:
                linkedin_job_id = job_data.get("linkedin_job_id", "")
                
                # Check if already exists
                existing = session.query(Job).filter(
                    Job.linkedin_job_id == linkedin_job_id
                ).first()
                
                if not existing:
                    job = Job(**job_data)
                    session.add(job)
                    added_jobs.append(job)
            
            session.commit()
            for job in added_jobs:
                session.refresh(job)
        
        return added_jobs
    
    def get_job_by_linkedin_id(self, linkedin_job_id: str) -> Optional[Job]:
        """Get a job by its LinkedIn job ID."""
        with self.get_session() as session:
            return session.query(Job).filter(
                Job.linkedin_job_id == linkedin_job_id
            ).first()
    
    def get_all_jobs(self, limit: int = 100, offset: int = 0) -> List[Job]:
        """Get all jobs with pagination."""
        with self.get_session() as session:
            return session.query(Job).order_by(
                Job.scraped_at.desc()
            ).offset(offset).limit(limit).all()
    
    def get_unapplied_easy_apply_jobs(self, limit: int = 10) -> List[Job]:
        """Get jobs with Easy Apply that haven't been applied to."""
        with self.get_session() as session:
            # Subquery to get job IDs that have been applied to
            applied_job_ids = session.query(Application.job_id).filter(
                Application.status.in_([
                    ApplicationStatus.APPLIED.value,
                    ApplicationStatus.EASY_APPLY.value,
                    ApplicationStatus.SKIPPED.value
                ])
            ).subquery()
            
            # Get Easy Apply jobs not in the applied list
            return session.query(Job).filter(
                Job.is_easy_apply == True,
                ~Job.id.in_(applied_job_ids)
            ).order_by(Job.scraped_at.desc()).limit(limit).all()
    
    def get_job_count(self) -> int:
        """Get total number of jobs in database."""
        with self.get_session() as session:
            return session.query(Job).count()
    
    def search_jobs(self, keyword: str, limit: int = 50) -> List[Job]:
        """Search jobs by keyword in title or company."""
        with self.get_session() as session:
            return session.query(Job).filter(
                (Job.title.ilike(f"%{keyword}%")) |
                (Job.company.ilike(f"%{keyword}%"))
            ).limit(limit).all()
    
    # ==================== Application Operations ====================
    
    def create_application(
        self,
        job_id: int,
        status: ApplicationStatus = ApplicationStatus.PENDING,
        cover_letter: Optional[str] = None,
        resume_used: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Application:
        """Create a new application record."""
        with self.get_session() as session:
            application = Application(
                job_id=job_id,
                status=status.value,
                cover_letter=cover_letter,
                resume_used=resume_used,
                notes=notes,
                applied_at=datetime.utcnow() if status in [
                    ApplicationStatus.APPLIED,
                    ApplicationStatus.EASY_APPLY
                ] else None
            )
            session.add(application)
            session.commit()
            session.refresh(application)
            return application
    
    def update_application_status(
        self,
        application_id: int,
        status: ApplicationStatus,
        error_message: Optional[str] = None
    ) -> Optional[Application]:
        """Update application status."""
        with self.get_session() as session:
            application = session.query(Application).filter(
                Application.id == application_id
            ).first()
            
            if application:
                application.status = status.value
                if error_message:
                    application.error_message = error_message
                if status in [ApplicationStatus.APPLIED, ApplicationStatus.EASY_APPLY]:
                    application.applied_at = datetime.utcnow()
                session.commit()
                session.refresh(application)
            
            return application
    
    def get_application_for_job(self, job_id: int) -> Optional[Application]:
        """Get application for a specific job."""
        with self.get_session() as session:
            return session.query(Application).filter(
                Application.job_id == job_id
            ).first()
    
    def get_applications_by_status(
        self,
        status: ApplicationStatus,
        limit: int = 100
    ) -> List[Application]:
        """Get applications by status."""
        with self.get_session() as session:
            return session.query(Application).filter(
                Application.status == status.value
            ).limit(limit).all()
    
    def get_application_stats(self) -> dict:
        """Get application statistics."""
        with self.get_session() as session:
            stats = {
                "total_jobs": session.query(Job).count(),
                "total_applications": session.query(Application).count(),
                "applied": session.query(Application).filter(
                    Application.status == ApplicationStatus.APPLIED.value
                ).count(),
                "easy_apply": session.query(Application).filter(
                    Application.status == ApplicationStatus.EASY_APPLY.value
                ).count(),
                "pending": session.query(Application).filter(
                    Application.status == ApplicationStatus.PENDING.value
                ).count(),
                "skipped": session.query(Application).filter(
                    Application.status == ApplicationStatus.SKIPPED.value
                ).count(),
                "failed": session.query(Application).filter(
                    Application.status == ApplicationStatus.FAILED.value
                ).count(),
            }
            return stats
