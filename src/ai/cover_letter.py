"""AI-powered cover letter generator using various free LLM providers."""
import json
from pathlib import Path
from typing import Optional
import requests
from rich.console import Console

from ..config import get_settings, LLMProvider

console = Console()


class CoverLetterGenerator:
    """Generates personalized cover letters using AI."""
    
    # Default prompt template
    PROMPT_TEMPLATE = """You are a professional cover letter writer. Write a concise, compelling cover letter for the following job application.

Job Title: {job_title}
Company: {company}
Job Description:
{job_description}

Resume Summary:
{resume_summary}

Requirements:
1. Keep it under 300 words
2. Be professional but personable
3. Highlight relevant skills and experience
4. Show enthusiasm for the role and company
5. Don't include placeholder text like [Your Name] - write the actual content only
6. Start directly with the letter content (no "Dear Hiring Manager" unless specifically needed)

Write the cover letter now:"""
    
    def __init__(self, resume_path: Optional[str] = None):
        """Initialize the cover letter generator."""
        self.settings = get_settings()
        self.resume_path = resume_path or self.settings.resume_path
        self.resume_summary = self._load_resume_summary()
    
    def _load_resume_summary(self) -> str:
        """Load resume summary from file or return default."""
        # Try to load from a text version of resume
        txt_path = Path(self.resume_path).with_suffix(".txt")
        if txt_path.exists():
            try:
                return txt_path.read_text(encoding="utf-8")[:2000]  # Limit length
            except:
                pass
        
        # Try to load from a summary file
        summary_path = Path(self.resume_path).parent / "resume_summary.txt"
        if summary_path.exists():
            try:
                return summary_path.read_text(encoding="utf-8")
            except:
                pass
        
        # Return placeholder
        return """
Experienced software professional with expertise in Python, JavaScript, and cloud technologies.
Strong background in building scalable applications and working with cross-functional teams.
Passionate about learning new technologies and solving complex problems.
"""
    
    async def generate(
        self,
        job_title: str,
        company: str,
        job_description: str
    ) -> Optional[str]:
        """Generate a cover letter for a job."""
        prompt = self.PROMPT_TEMPLATE.format(
            job_title=job_title,
            company=company,
            job_description=job_description[:3000],  # Limit description length
            resume_summary=self.resume_summary
        )
        
        provider = self.settings.llm_provider
        
        try:
            if provider == LLMProvider.OLLAMA:
                return await self._generate_with_ollama(prompt)
            elif provider == LLMProvider.GROQ:
                return await self._generate_with_groq(prompt)
            elif provider == LLMProvider.OPENAI:
                return await self._generate_with_openai(prompt)
            elif provider == LLMProvider.GOOGLE:
                return await self._generate_with_google(prompt)
            else:
                console.print(f"[yellow]Unknown LLM provider: {provider}[/yellow]")
                return None
        except Exception as e:
            console.print(f"[red]Error generating cover letter: {e}[/red]")
            return None
    
    async def _generate_with_ollama(self, prompt: str) -> Optional[str]:
        """Generate using Ollama (free, local or remote)."""
        url = f"{self.settings.ollama_base_url}/api/generate"
        
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 500
            }
        }
        
        # Add headers with API key if configured
        headers = {"Content-Type": "application/json"}
        if self.settings.ollama_api_key:
            headers["Authorization"] = f"Bearer {self.settings.ollama_api_key}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            console.print("[red]Could not connect to Ollama.[/red]")
            console.print(f"[dim]URL: {self.settings.ollama_base_url}[/dim]")
            if "localhost" in self.settings.ollama_base_url:
                console.print("[dim]For local: Start Ollama with: ollama serve[/dim]")
            else:
                console.print("[dim]For remote: Check OLLAMA_BASE_URL and OLLAMA_API_KEY[/dim]")
            return None
        except Exception as e:
            console.print(f"[red]Ollama error: {e}[/red]")
            return None
    
    async def _generate_with_groq(self, prompt: str) -> Optional[str]:
        """Generate using Groq API (free tier available)."""
        if not self.settings.groq_api_key:
            console.print("[red]GROQ_API_KEY not set[/red]")
            return None
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.settings.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama2-70b-4096",  # or mixtral-8x7b-32768
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            console.print(f"[red]Groq API error: {e}[/red]")
            return None
    
    async def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """Generate using OpenAI API."""
        if not self.settings.openai_api_key:
            console.print("[red]OPENAI_API_KEY not set[/red]")
            return None
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            console.print(f"[red]OpenAI API error: {e}[/red]")
            return None
    
    async def _generate_with_google(self, prompt: str) -> Optional[str]:
        """Generate using Google AI (Gemini) API."""
        if not self.settings.google_ai_api_key:
            console.print("[red]GOOGLE_AI_API_KEY not set[/red]")
            return None
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.settings.google_ai_api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            console.print(f"[red]Google AI error: {e}[/red]")
            return None
    
    def set_resume_summary(self, summary: str):
        """Update the resume summary used for generation."""
        self.resume_summary = summary


class SimpleCoverLetterGenerator:
    """Simple template-based cover letter generator (no AI required)."""
    
    TEMPLATES = [
        """I am writing to express my strong interest in the {job_title} position at {company}. 
With my background in software development and passion for building innovative solutions, 
I am confident that I would be a valuable addition to your team.

Throughout my career, I have developed expertise in various programming languages and technologies. 
I am particularly drawn to {company}'s commitment to innovation and would welcome the opportunity 
to contribute to your continued success.

I am excited about the prospect of bringing my skills and enthusiasm to your organization 
and would welcome the opportunity to discuss how I can contribute to your team's goals.

Thank you for considering my application. I look forward to hearing from you.""",
        
        """I am excited to apply for the {job_title} role at {company}. Your company's 
reputation for excellence and innovation aligns perfectly with my professional goals 
and experience.

My background has prepared me well for this opportunity, and I am eager to bring my 
skills in problem-solving, collaboration, and technical expertise to your team. I am 
particularly impressed by {company}'s work and would be honored to contribute to your 
mission.

I would welcome the chance to discuss how my experience and skills can benefit your 
organization. Thank you for your time and consideration."""
    ]
    
    def __init__(self):
        """Initialize simple generator."""
        self.template_index = 0
    
    async def generate(
        self,
        job_title: str,
        company: str,
        job_description: str = ""
    ) -> str:
        """Generate a simple template-based cover letter."""
        template = self.TEMPLATES[self.template_index % len(self.TEMPLATES)]
        self.template_index += 1
        
        return template.format(
            job_title=job_title,
            company=company
        )
