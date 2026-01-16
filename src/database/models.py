"""Database models for storing job listings and applications."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, 
    Boolean, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum


Base = declarative_base()


class ApplicationStatus(str, Enum):
    """Status of a job application."""
    PENDING = "pending"
    APPLIED = "applied"
    EASY_APPLY = "easy_apply"
    EXTERNAL = "external"
    SKIPPED = "skipped"
    FAILED = "failed"


class Job(Base):
    """Model representing a LinkedIn job listing."""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    linkedin_job_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    company = Column(String(300), nullable=False)
    location = Column(String(300))
    description = Column(Text)
    job_url = Column(String(1000))
    posted_date = Column(String(100))
    experience_level = Column(String(50))
    employment_type = Column(String(50))
    salary_range = Column(String(200))
    applicant_count = Column(String(100))
    is_easy_apply = Column(Boolean, default=False)
    
    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow)
    search_keyword = Column(String(200))
    
    # Relationships
    applications = relationship("Application", back_populates="job")
    
    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"
    
    def to_dict(self) -> dict:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "linkedin_job_id": self.linkedin_job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "job_url": self.job_url,
            "posted_date": self.posted_date,
            "experience_level": self.experience_level,
            "employment_type": self.employment_type,
            "salary_range": self.salary_range,
            "applicant_count": self.applicant_count,
            "is_easy_apply": self.is_easy_apply,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "search_keyword": self.search_keyword,
        }


class Application(Base):
    """Model representing a job application."""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String(50), default=ApplicationStatus.PENDING.value)
    applied_at = Column(DateTime)
    cover_letter = Column(Text)
    resume_used = Column(String(500))
    notes = Column(Text)
    error_message = Column(Text)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    
    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Convert application to dictionary."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "status": self.status,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "cover_letter": self.cover_letter,
            "resume_used": self.resume_used,
            "notes": self.notes,
            "error_message": self.error_message,
        }
