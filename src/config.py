"""Configuration management for LinkedIn Job Bot."""
import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum


class ExperienceLevel(str, Enum):
    """LinkedIn experience level filters."""
    INTERNSHIP = "1"
    ENTRY_LEVEL = "2"
    ASSOCIATE = "3"
    MID_SENIOR = "4"
    DIRECTOR = "5"
    EXECUTIVE = "6"


class DatePosted(str, Enum):
    """LinkedIn date posted filters."""
    ANY_TIME = ""
    PAST_MONTH = "r2592000"
    PAST_WEEK = "r604800"
    PAST_24_HOURS = "r86400"


class LLMProvider(str, Enum):
    """Supported LLM providers for cover letter generation."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    GROQ = "groq"
    GOOGLE = "google"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LinkedIn Credentials
    linkedin_email: str = Field(default="", description="LinkedIn login email")
    linkedin_password: str = Field(default="", description="LinkedIn login password")
    
    # Job Search Configuration
    job_keywords: str = Field(
        default="Python Developer",
        description="Comma-separated list of job keywords to search"
    )
    experience_levels: str = Field(
        default="ENTRY_LEVEL,ASSOCIATE",
        description="Comma-separated experience levels"
    )
    location: str = Field(default="Remote", description="Job location filter")
    date_posted: str = Field(default="PAST_WEEK", description="Date posted filter")
    
    # Auto Apply Settings
    auto_apply_enabled: bool = Field(default=False, description="Enable auto-apply")
    max_applications_per_run: int = Field(default=10, description="Max applications per run")
    
    # Resume/CV Configuration
    resume_path: str = Field(default="./resumes/my_resume.pdf", description="Path to resume")
    use_smart_resume_selection: bool = Field(
        default=True,
        description="Use smart resume selection based on job keywords"
    )
    
    # LLM Configuration
    llm_provider: LLMProvider = Field(default=LLMProvider.OLLAMA, description="LLM provider")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama API URL")
    ollama_model: str = Field(default="llama2", description="Ollama model name")
    ollama_api_key: Optional[str] = Field(default=None, description="Ollama API key (for remote servers)")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    google_ai_api_key: Optional[str] = Field(default=None, description="Google AI API key")
    
    # Scheduler Settings
    scheduler_start_hour: int = Field(default=8, description="Scheduler start hour (24h)")
    scheduler_end_hour: int = Field(default=18, description="Scheduler end hour (24h)")
    scheduler_interval_minutes: int = Field(default=60, description="Run interval in minutes")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./data/jobs.db",
        description="Database connection URL"
    )
    
    # Browser Settings
    headless: bool = Field(default=True, description="Run browser in headless mode")
    slow_mo: int = Field(default=100, description="Slow motion delay in ms")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def keywords_list(self) -> List[str]:
        """Get job keywords as a list."""
        return [k.strip() for k in self.job_keywords.split(",") if k.strip()]
    
    @property
    def experience_levels_list(self) -> List[ExperienceLevel]:
        """Get experience levels as a list of enums."""
        levels = []
        for level in self.experience_levels.split(","):
            level = level.strip().upper()
            if hasattr(ExperienceLevel, level):
                levels.append(ExperienceLevel[level])
        return levels
    
    @property
    def date_posted_filter(self) -> DatePosted:
        """Get date posted as enum."""
        filter_name = self.date_posted.upper().replace(" ", "_")
        if hasattr(DatePosted, filter_name):
            return DatePosted[filter_name]
        return DatePosted.PAST_WEEK


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings."""
    return settings
