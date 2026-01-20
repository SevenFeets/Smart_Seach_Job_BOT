#!/usr/bin/env python3
"""LinkedIn Job Bot - Main entry point and CLI."""
import asyncio
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_settings
from src.database import JobRepository
from src.linkedin import LinkedInScraper, JobApplier
from src.ai import CoverLetterGenerator
from src.scheduler import JobBotScheduler, run_once_if_in_schedule
from src.resume_selector import get_resume_selector

app = typer.Typer(
    name="linkedin-job-bot",
    help="Automated LinkedIn job search and application bot"
)
console = Console()


def print_banner():
    """Print the application banner."""
    banner = """
    ========================================================
          LinkedIn Job Bot v1.0.0
          Automated Job Search & Application
    ========================================================
    """
    console.print(banner, style="bold cyan")


@app.command()
def search(
    keywords: Optional[str] = typer.Option(
        None,
        "--keywords", "-k",
        help="Comma-separated job keywords to search"
    ),
    pages: int = typer.Option(
        3,
        "--pages", "-p",
        help="Number of pages to scrape per keyword"
    ),
    easy_apply: bool = typer.Option(
        False,
        "--easy-apply", "-e",
        help="Only search for Easy Apply jobs"
    ),
    details: bool = typer.Option(
        False,
        "--details", "-d",
        help="Fetch detailed job descriptions"
    )
):
    """Search for jobs on LinkedIn and save to database."""
    print_banner()
    settings = get_settings()
    
    search_keywords = keywords.split(",") if keywords else settings.keywords_list
    
    console.print(f"[cyan]Search Keywords:[/cyan] {', '.join(search_keywords)}")
    console.print(f"[cyan]Experience Levels:[/cyan] {settings.experience_levels}")
    console.print(f"[cyan]Date Posted:[/cyan] {settings.date_posted}")
    console.print(f"[cyan]Location:[/cyan] {settings.location}")
    console.print()
    
    scraper = LinkedInScraper()
    
    try:
        jobs = asyncio.run(scraper.run(
            keywords=search_keywords,
            max_pages_per_keyword=pages,
            get_details=details,
            easy_apply_only=easy_apply
        ))
        console.print(f"\n[bold green]✓ Search complete! Found {len(jobs)} jobs.[/bold green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Search cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during search: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def apply(
    max_apps: int = typer.Option(
        10,
        "--max", "-m",
        help="Maximum number of applications to submit"
    ),
    use_ai: bool = typer.Option(
        True,
        "--ai/--no-ai",
        help="Use AI to generate cover letters"
    )
):
    """Apply to saved jobs using Easy Apply."""
    print_banner()
    settings = get_settings()
    
    if not settings.auto_apply_enabled:
        console.print("[yellow]⚠️ Auto-apply is disabled. Enable it in your .env file.[/yellow]")
        raise typer.Exit(0)
    
    console.print(f"[cyan]Max Applications:[/cyan] {max_apps}")
    console.print(f"[cyan]Resume:[/cyan] {settings.resume_path}")
    console.print(f"[cyan]AI Cover Letters:[/cyan] {'Enabled' if use_ai else 'Disabled'}")
    console.print()
    
    cover_letter_gen = CoverLetterGenerator() if use_ai else None
    applier = JobApplier(cover_letter_generator=cover_letter_gen)
    
    try:
        stats = asyncio.run(applier.run(max_applications=max_apps))
        console.print(f"\n[bold green]✓ Applications complete![/bold green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Applications cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during applications: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def run(
    keywords: Optional[str] = typer.Option(
        None,
        "--keywords", "-k",
        help="Comma-separated job keywords to search"
    ),
    max_apps: int = typer.Option(
        10,
        "--max", "-m",
        help="Maximum number of applications per run"
    ),
    easy_apply: bool = typer.Option(
        True,
        "--easy-apply/--all",
        help="Only search for Easy Apply jobs"
    )
):
    """Run full pipeline: search + apply."""
    print_banner()
    settings = get_settings()
    
    search_keywords = keywords.split(",") if keywords else settings.keywords_list
    
    console.print("[bold cyan]Starting full job search and apply pipeline...[/bold cyan]")
    console.print(f"[cyan]Keywords:[/cyan] {', '.join(search_keywords)}")
    console.print(f"[cyan]Max Applications:[/cyan] {max_apps}")
    console.print()
    
    async def full_pipeline():
        # Step 1: Search
        console.print("\n[bold]📍 Step 1: Searching for jobs...[/bold]")
        scraper = LinkedInScraper()
        await scraper.run(
            keywords=search_keywords,
            max_pages_per_keyword=3,
            easy_apply_only=easy_apply
        )
        
        # Step 2: Apply (if enabled)
        if settings.auto_apply_enabled:
            console.print("\n[bold]📍 Step 2: Applying to jobs...[/bold]")
            cover_letter_gen = CoverLetterGenerator()
            applier = JobApplier(cover_letter_generator=cover_letter_gen)
            await applier.run(max_applications=max_apps)
        else:
            console.print("\n[yellow]Auto-apply disabled. Skipping applications.[/yellow]")
    
    try:
        asyncio.run(full_pipeline())
        console.print(f"\n[bold green]✓ Pipeline complete![/bold green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Pipeline cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during pipeline: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def schedule(
    start_hour: int = typer.Option(
        8,
        "--start", "-s",
        help="Start hour (24h format)"
    ),
    end_hour: int = typer.Option(
        18,
        "--end", "-e",
        help="End hour (24h format)"
    )
):
    """Run the bot on a schedule (hourly within specified hours)."""
    print_banner()
    
    console.print(f"[cyan]Schedule:[/cyan] {start_hour}:00 - {end_hour}:00")
    console.print("[dim]Bot will run every hour within this window[/dim]")
    console.print()
    
    settings = get_settings()
    search_keywords = settings.keywords_list
    
    async def scheduled_job():
        scraper = LinkedInScraper()
        await scraper.run(
            keywords=search_keywords,
            max_pages_per_keyword=2,
            easy_apply_only=True
        )
        
        if settings.auto_apply_enabled:
            cover_letter_gen = CoverLetterGenerator()
            applier = JobApplier(cover_letter_generator=cover_letter_gen)
            await applier.run(max_applications=5)
    
    scheduler = JobBotScheduler(
        job_func=scheduled_job,
        start_hour=start_hour,
        end_hour=end_hour
    )
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.stop()
        console.print("\n[yellow]Scheduler stopped.[/yellow]")


@app.command()
def stats():
    """Show job search and application statistics."""
    print_banner()
    
    repo = JobRepository()
    stats = repo.get_application_stats()
    
    table = Table(title="Job Bot Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Jobs Scraped", str(stats["total_jobs"]))
    table.add_row("Total Applications", str(stats["total_applications"]))
    table.add_row("Successfully Applied", str(stats["applied"] + stats["easy_apply"]))
    table.add_row("Pending", str(stats["pending"]))
    table.add_row("Skipped", str(stats["skipped"]))
    table.add_row("Failed", str(stats["failed"]))
    
    console.print(table)


@app.command()
def jobs(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of jobs to show"),
    keyword: Optional[str] = typer.Option(None, "--search", "-s", help="Search keyword")
):
    """List saved jobs from database."""
    print_banner()
    
    repo = JobRepository()
    
    if keyword:
        job_list = repo.search_jobs(keyword, limit=limit)
        console.print(f"[cyan]Search results for '{keyword}':[/cyan]")
    else:
        job_list = repo.get_all_jobs(limit=limit)
        console.print("[cyan]Recent jobs:[/cyan]")
    
    if not job_list:
        console.print("[yellow]No jobs found.[/yellow]")
        return
    
    table = Table()
    table.add_column("ID", style="dim")
    table.add_column("Title", style="cyan")
    table.add_column("Company", style="green")
    table.add_column("Location")
    table.add_column("Easy Apply", style="yellow")
    table.add_column("Posted")
    
    for job in job_list:
        table.add_row(
            str(job.id),
            job.title[:40] + "..." if len(job.title) > 40 else job.title,
            job.company[:25] + "..." if len(job.company) > 25 else job.company,
            job.location[:20] if job.location else "",
            "Yes" if job.is_easy_apply else "No",
            job.posted_date or ""
        )
    
    console.print(table)


@app.command()
def resumes(
    test_job: Optional[str] = typer.Option(
        None,
        "--test",
        "-t",
        help="Test which resume would be selected for a job title"
    )
):
    """Manage and test resume selection."""
    print_banner()
    settings = get_settings()
    
    if not settings.use_smart_resume_selection:
        console.print("[yellow]Smart resume selection is disabled.[/yellow]")
        console.print(f"[cyan]Current resume:[/cyan] {settings.resume_path}")
        console.print("\n[dim]To enable smart selection, set USE_SMART_RESUME_SELECTION=true in .env[/dim]")
        return
    
    selector = get_resume_selector()
    available = selector.list_available_resumes()
    
    console.print("[bold cyan]Available Resume Profiles:[/bold cyan]")
    for profile in available:
        profile_data = selector.resume_profiles[profile]
        console.print(f"\n[green]• {profile}[/green]")
        console.print(f"  File: {profile_data['file']}")
        console.print(f"  Keywords: {', '.join(profile_data['keywords'][:10])}...")
    
    if test_job:
        console.print(f"\n[bold cyan]Testing job:[/bold cyan] {test_job}")
        selected = selector.select_resume(job_title=test_job, job_description="")
        if selected:
            console.print(f"[green]Would use:[/green] {selected}")
        else:
            console.print("[red]No resume selected[/red]")
    else:
        console.print("\n[dim]Tip: Use --test 'Job Title' to see which resume would be selected[/dim]")


@app.command()
def github_action():
    """Run for GitHub Actions (checks schedule, runs once)."""
    settings = get_settings()
    
    # Check if within schedule
    if not run_once_if_in_schedule():
        console.print("[dim]Skipping run - outside scheduled hours[/dim]")
        raise typer.Exit(0)
    
    console.print("[bold cyan]Running GitHub Actions job...[/bold cyan]")
    
    async def github_action_job():
        # Search for jobs
        scraper = LinkedInScraper()
        # Search more pages and include non-Easy Apply jobs for better coverage
        await scraper.run(
            keywords=settings.keywords_list,
            max_pages_per_keyword=5,  # Increased from 2 to 5 (125 jobs per keyword)
            easy_apply_only=False  # Search all jobs, not just Easy Apply
        )
        
        # Apply if enabled
        if settings.auto_apply_enabled:
            cover_letter_gen = CoverLetterGenerator()
            applier = JobApplier(cover_letter_generator=cover_letter_gen)
            await applier.run(max_applications=settings.max_applications_per_run)
    
    try:
        asyncio.run(github_action_job())
        console.print("[bold green]✓ GitHub Action completed successfully![/bold green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
