"""Scheduler for running the LinkedIn bot at specified intervals."""
import asyncio
from datetime import datetime, time
from typing import Optional, Callable
import schedule
from rich.console import Console

from .config import get_settings

console = Console()


class JobBotScheduler:
    """Schedules and runs the LinkedIn job bot at configured intervals."""
    
    def __init__(
        self,
        job_func: Callable,
        start_hour: Optional[int] = None,
        end_hour: Optional[int] = None,
        interval_minutes: Optional[int] = None
    ):
        """Initialize the scheduler."""
        self.settings = get_settings()
        self.job_func = job_func
        self.start_hour = start_hour or self.settings.scheduler_start_hour
        self.end_hour = end_hour or self.settings.scheduler_end_hour
        self.interval_minutes = interval_minutes or self.settings.scheduler_interval_minutes
        self.is_running = False
    
    def is_within_schedule(self) -> bool:
        """Check if current time is within scheduled hours."""
        current_hour = datetime.now().hour
        return self.start_hour <= current_hour < self.end_hour
    
    def _run_if_scheduled(self):
        """Run the job function if within scheduled hours."""
        if self.is_within_schedule():
            console.print(f"\n[bold cyan]⏰ Running scheduled job at {datetime.now().strftime('%H:%M')}[/bold cyan]")
            try:
                # Run async job in sync context
                asyncio.run(self.job_func())
            except Exception as e:
                console.print(f"[red]Error running scheduled job: {e}[/red]")
        else:
            console.print(f"[dim]Outside scheduled hours ({self.start_hour}:00 - {self.end_hour}:00)[/dim]")
    
    def schedule_jobs(self):
        """Set up the schedule."""
        # Clear any existing jobs
        schedule.clear()
        
        # Schedule at the start of each hour within the range
        for hour in range(self.start_hour, self.end_hour + 1):
            schedule.every().day.at(f"{hour:02d}:00").do(self._run_if_scheduled)
        
        console.print(f"[green]✓ Scheduled jobs from {self.start_hour}:00 to {self.end_hour}:00[/green]")
        console.print(f"[dim]Jobs will run every hour within this window[/dim]")
    
    def run_now(self):
        """Run the job immediately."""
        console.print("[cyan]Running job immediately...[/cyan]")
        asyncio.run(self.job_func())
    
    def start(self):
        """Start the scheduler loop."""
        self.is_running = True
        self.schedule_jobs()
        
        console.print("\n[bold green]🚀 Scheduler started![/bold green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        
        # Run immediately if within schedule
        if self.is_within_schedule():
            self._run_if_scheduled()
        
        while self.is_running:
            schedule.run_pending()
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(60))
    
    def stop(self):
        """Stop the scheduler."""
        self.is_running = False
        schedule.clear()
        console.print("[yellow]Scheduler stopped.[/yellow]")


def run_once_if_in_schedule():
    """Run the bot once if within scheduled hours (for GitHub Actions)."""
    settings = get_settings()
    current_hour = datetime.now().hour
    
    if settings.scheduler_start_hour <= current_hour < settings.scheduler_end_hour:
        console.print(f"[green]✓ Within schedule ({settings.scheduler_start_hour}:00 - {settings.scheduler_end_hour}:00)[/green]")
        return True
    else:
        console.print(f"[yellow]Outside scheduled hours. Current: {current_hour}:00, Schedule: {settings.scheduler_start_hour}:00 - {settings.scheduler_end_hour}:00[/yellow]")
        return False
