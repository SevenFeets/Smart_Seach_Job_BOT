"""Smart resume selector based on job requirements."""
import os
from pathlib import Path
from typing import Optional, Dict, List
from rich.console import Console

console = Console()


class ResumeSelector:
    """Selects the most appropriate resume based on job details."""
    
    def __init__(self, resumes_dir: str = "./resumes"):
        """Initialize the resume selector."""
        self.resumes_dir = Path(resumes_dir)
        self.resume_profiles: Dict[str, Dict] = {}
        self._load_resume_profiles()
    
    def _load_resume_profiles(self):
        """Load resume profiles from configuration."""
        # Define resume profiles with keywords
        profiles = {
            "backend": {
                "file": "Backend.pdf",
                "keywords": [
                    "backend", "python", "django", "flask", "fastapi", "api", 
                    "rest", "graphql", "database", "sql", "postgresql", "mysql",
                    "mongodb", "redis", "microservices", "docker", "kubernetes",
                    "aws", "cloud", "serverless", "node.js", "express", "spring",
                    "java", ".net", "c#", "ruby", "rails", "php", "laravel"
                ],
                "weight": 1.0
            },
            "embedded": {
                "file": "embedded.pdf",
                "keywords": [
                    "embedded", "firmware", "c", "c++", "microcontroller", "mcu",
                    "arm", "rtos", "real-time", "iot", "hardware", "fpga", "vhdl",
                    "verilog", "assembly", "linux kernel", "device driver", "uart",
                    "spi", "i2c", "can", "automotive", "robotics", "raspberry pi",
                    "arduino", "stm32", "esp32", "sensor", "actuator"
                ],
                "weight": 1.0
            }
        }
        
        # Only keep profiles where the resume file exists
        for profile_name, profile_data in profiles.items():
            resume_path = self.resumes_dir / profile_data["file"]
            if resume_path.exists():
                self.resume_profiles[profile_name] = profile_data
                console.print(f"[dim]Loaded resume profile: {profile_name} ({profile_data['file']})[/dim]")
            else:
                console.print(f"[yellow]Warning: Resume not found: {profile_data['file']}[/yellow]")
    
    def select_resume(
        self,
        job_title: str,
        job_description: Optional[str] = None,
        company: Optional[str] = None
    ) -> Optional[str]:
        """
        Select the best resume based on job details.
        
        Args:
            job_title: The job title
            job_description: Full job description
            company: Company name
            
        Returns:
            Path to the selected resume file, or None if no resumes available
        """
        if not self.resume_profiles:
            console.print("[yellow]No resume profiles configured[/yellow]")
            return None
        
        # If only one resume, return it
        if len(self.resume_profiles) == 1:
            profile = list(self.resume_profiles.values())[0]
            return str(self.resumes_dir / profile["file"])
        
        # Combine all text for matching
        search_text = f"{job_title} {job_description or ''} {company or ''}".lower()
        
        # Score each resume
        scores = {}
        for profile_name, profile_data in self.resume_profiles.items():
            score = 0
            matched_keywords = []
            
            for keyword in profile_data["keywords"]:
                if keyword.lower() in search_text:
                    score += 1
                    matched_keywords.append(keyword)
            
            # Apply weight
            score *= profile_data["weight"]
            scores[profile_name] = {
                "score": score,
                "matched_keywords": matched_keywords,
                "file": profile_data["file"]
            }
        
        # Find the best match
        if not any(s["score"] > 0 for s in scores.values()):
            # No keywords matched, use default (first resume)
            default_profile = list(self.resume_profiles.values())[0]
            console.print(f"[yellow]No keyword matches, using default: {default_profile['file']}[/yellow]")
            return str(self.resumes_dir / default_profile["file"])
        
        # Get the highest scoring resume
        best_profile = max(scores.items(), key=lambda x: x[1]["score"])
        profile_name, profile_info = best_profile
        
        console.print(
            f"[cyan]Selected resume:[/cyan] {profile_info['file']} "
            f"[dim](score: {profile_info['score']}, "
            f"keywords: {', '.join(profile_info['matched_keywords'][:5])}...)[/dim]"
        )
        
        return str(self.resumes_dir / profile_info["file"])
    
    def get_resume_by_name(self, name: str) -> Optional[str]:
        """Get a specific resume by profile name."""
        if name in self.resume_profiles:
            return str(self.resumes_dir / self.resume_profiles[name]["file"])
        return None
    
    def list_available_resumes(self) -> List[str]:
        """List all available resume profiles."""
        return list(self.resume_profiles.keys())
    
    def add_custom_profile(
        self,
        name: str,
        filename: str,
        keywords: List[str],
        weight: float = 1.0
    ):
        """
        Add a custom resume profile.
        
        Args:
            name: Profile name (e.g., "fullstack", "devops")
            filename: Resume filename in resumes directory
            keywords: List of keywords to match against
            weight: Weight multiplier for scoring (default: 1.0)
        """
        resume_path = self.resumes_dir / filename
        if resume_path.exists():
            self.resume_profiles[name] = {
                "file": filename,
                "keywords": [k.lower() for k in keywords],
                "weight": weight
            }
            console.print(f"[green]Added resume profile: {name}[/green]")
        else:
            console.print(f"[red]Resume file not found: {filename}[/red]")


# Singleton instance
_resume_selector = None


def get_resume_selector(resumes_dir: str = "./resumes") -> ResumeSelector:
    """Get or create the resume selector instance."""
    global _resume_selector
    if _resume_selector is None:
        _resume_selector = ResumeSelector(resumes_dir)
    return _resume_selector
