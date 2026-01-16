"""LinkedIn job application automation."""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from playwright.async_api import Page, async_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from ..config import get_settings
from ..database import JobRepository, Job, ApplicationStatus
from .authenticator import LinkedInAuthenticator
from ..resume_selector import get_resume_selector

console = Console()


class JobApplier:
    """Automates job applications on LinkedIn."""
    
    def __init__(self, cover_letter_generator=None):
        """Initialize the job applier."""
        self.settings = get_settings()
        self.auth = LinkedInAuthenticator()
        self.repository = JobRepository()
        self.cover_letter_generator = cover_letter_generator
        self.resume_selector = get_resume_selector() if self.settings.use_smart_resume_selection else None
        self.page: Optional[Page] = None
        
        # Stats tracking
        self.stats = {
            "attempted": 0,
            "successful": 0,
            "skipped": 0,
            "failed": 0
        }
    
    async def apply_to_job(self, job: Job) -> bool:
        """Apply to a single job using Easy Apply."""
        console.print(f"\n[cyan]Applying to: {job.title} at {job.company}[/cyan]")
        
        try:
            # Navigate to job page
            await self.page.goto(job.job_url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)
            
            # Check if already applied
            already_applied = await self.page.query_selector(
                "[class*='applied'], .jobs-s-apply--fadein"
            )
            if already_applied:
                text = await already_applied.inner_text()
                if "applied" in text.lower():
                    console.print("[yellow]Already applied to this job[/yellow]")
                    return False
            
            # Find Easy Apply button
            easy_apply_btn = await self.page.query_selector(
                ".jobs-apply-button, "
                "button[data-control-name='jobdetails_topcard_inapply'], "
                "button.jobs-s-apply button, "
                ".jobs-apply-button--top-card"
            )
            
            if not easy_apply_btn:
                console.print("[yellow]No Easy Apply button found[/yellow]")
                return False
            
            # Check if it's actually Easy Apply
            btn_text = await easy_apply_btn.inner_text()
            if "easy apply" not in btn_text.lower():
                console.print("[yellow]Not an Easy Apply position[/yellow]")
                return False
            
            # Click Easy Apply
            await easy_apply_btn.click()
            await self.page.wait_for_timeout(2000)
            
            # Handle the application modal
            success = await self._complete_application_modal(job)
            
            return success
            
        except Exception as e:
            console.print(f"[red]Error applying to job: {e}[/red]")
            return False
    
    async def _complete_application_modal(self, job: Job) -> bool:
        """Complete the Easy Apply application modal."""
        max_steps = 10  # Prevent infinite loops
        step = 0
        
        while step < max_steps:
            step += 1
            await self.page.wait_for_timeout(1500)
            
            # Check for success/completion
            success_indicator = await self.page.query_selector(
                "[class*='post-apply'], "
                ".artdeco-modal__content h2"
            )
            if success_indicator:
                text = await success_indicator.inner_text()
                if "application sent" in text.lower() or "applied" in text.lower():
                    console.print("[green]Application submitted successfully![/green]")
                    return True
            
            # Check for submit button
            submit_btn = await self.page.query_selector(
                "button[aria-label='Submit application'], "
                "button[aria-label='Review'], "
                ".jobs-easy-apply-content footer button.artdeco-button--primary"
            )
            
            if submit_btn:
                btn_text = await submit_btn.inner_text()
                
                if "submit" in btn_text.lower():
                    # Final submit
                    await submit_btn.click()
                    await self.page.wait_for_timeout(3000)
                    console.print("[green]Application submitted![/green]")
                    return True
                    
                elif "next" in btn_text.lower() or "continue" in btn_text.lower():
                    # Fill current step and continue
                    await self._fill_application_step(job)
                    await submit_btn.click()
                    continue
                    
                elif "review" in btn_text.lower():
                    await submit_btn.click()
                    continue
            
            # Try to find and click Next button
            next_btn = await self.page.query_selector(
                "button[aria-label='Continue to next step'], "
                "button[data-easy-apply-next-button]"
            )
            if next_btn:
                await self._fill_application_step(job)
                await next_btn.click()
                continue
            
            # Check for close/dismiss button (application complete)
            dismiss_btn = await self.page.query_selector(
                "button[aria-label='Dismiss'], "
                ".artdeco-modal__dismiss"
            )
            if dismiss_btn:
                # Check if we completed
                modal_content = await self.page.query_selector(".artdeco-modal__content")
                if modal_content:
                    content_text = await modal_content.inner_text()
                    if "application sent" in content_text.lower():
                        await dismiss_btn.click()
                        return True
            
            # Check for errors
            error_elem = await self.page.query_selector(
                ".artdeco-inline-feedback--error, "
                "[class*='error']"
            )
            if error_elem:
                error_text = await error_elem.inner_text()
                console.print(f"[red]Form error: {error_text}[/red]")
        
        console.print("[yellow]Could not complete application (max steps reached)[/yellow]")
        return False
    
    async def _fill_application_step(self, job: Job):
        """Fill in required fields for current application step."""
        # Handle resume upload if needed
        resume_input = await self.page.query_selector(
            "input[type='file'][name*='resume'], "
            "input[accept*='.pdf']"
        )
        if resume_input:
            # Select the appropriate resume
            if self.resume_selector:
                selected_resume = self.resume_selector.select_resume(
                    job_title=job.title,
                    job_description=job.description,
                    company=job.company
                )
                resume_path = Path(selected_resume) if selected_resume else Path(self.settings.resume_path)
            else:
                resume_path = Path(self.settings.resume_path)
            
            if resume_path.exists():
                await resume_input.set_input_files(str(resume_path))
                console.print(f"[cyan]Uploaded resume: {resume_path.name}[/cyan]")
            else:
                console.print(f"[red]Resume not found: {resume_path}[/red]")
        
        # Handle cover letter textarea
        cover_letter_input = await self.page.query_selector(
            "textarea[name*='cover'], "
            "textarea[aria-label*='cover letter'], "
            "textarea[id*='cover']"
        )
        if cover_letter_input and self.cover_letter_generator:
            # Generate cover letter
            cover_letter = await self.cover_letter_generator.generate(
                job_title=job.title,
                company=job.company,
                job_description=job.description or ""
            )
            if cover_letter:
                await cover_letter_input.fill(cover_letter)
                console.print("[cyan]Generated and filled cover letter[/cyan]")
        
        # Handle phone number field
        phone_input = await self.page.query_selector(
            "input[name*='phone'], "
            "input[aria-label*='phone'], "
            "input[id*='phone']"
        )
        if phone_input:
            current_value = await phone_input.input_value()
            if not current_value:
                # Skip if no phone configured
                pass
        
        # Handle text inputs with labels
        required_fields = await self.page.query_selector_all(
            ".jobs-easy-apply-form-section__grouping input[required], "
            ".jobs-easy-apply-form-section__grouping select[required]"
        )
        
        for field in required_fields:
            try:
                field_type = await field.get_attribute("type")
                current_value = await field.input_value() if field_type != "select" else None
                
                # Skip if already filled
                if current_value:
                    continue
                
                # Try to find label
                field_id = await field.get_attribute("id")
                if field_id:
                    label = await self.page.query_selector(f"label[for='{field_id}']")
                    if label:
                        label_text = await label.inner_text()
                        # Handle common fields
                        label_lower = label_text.lower()
                        
                        if "year" in label_lower and "experience" in label_lower:
                            await field.fill("3")
                        elif "city" in label_lower:
                            await field.fill(self.settings.location.split(",")[0])
                            
            except Exception as e:
                continue
        
        # Handle radio buttons and checkboxes (usually "yes" questions)
        radio_groups = await self.page.query_selector_all(
            ".jobs-easy-apply-form-section__grouping fieldset"
        )
        
        for group in radio_groups:
            try:
                # Check if required
                legend = await group.query_selector("legend")
                if not legend:
                    continue
                
                # Find the "Yes" option and select it
                yes_option = await group.query_selector(
                    "input[value='Yes'], "
                    "input[value='yes'], "
                    "label:has-text('Yes') input"
                )
                if yes_option:
                    is_checked = await yes_option.is_checked()
                    if not is_checked:
                        await yes_option.click()
            except:
                continue
    
    async def apply_to_jobs(
        self,
        jobs: Optional[List[Job]] = None,
        max_applications: Optional[int] = None
    ) -> Dict:
        """Apply to multiple jobs."""
        max_apps = max_applications or self.settings.max_applications_per_run
        
        # Get jobs to apply to
        if jobs is None:
            jobs = self.repository.get_unapplied_easy_apply_jobs(limit=max_apps)
        
        if not jobs:
            console.print("[yellow]No jobs to apply to.[/yellow]")
            return self.stats
        
        console.print(f"\n[bold cyan]Starting applications ({len(jobs)} jobs)[/bold cyan]")
        
        async with async_playwright() as playwright:
            await self.auth.start_browser(playwright)
            await self.auth.get_context()
            self.page = await self.auth.ensure_logged_in()
            
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=console
                ) as progress:
                    task = progress.add_task(
                        "[cyan]Applying to jobs...",
                        total=min(len(jobs), max_apps)
                    )
                    
                    for i, job in enumerate(jobs[:max_apps]):
                        self.stats["attempted"] += 1
                        
                        # Determine which resume will be used
                        if self.resume_selector:
                            selected_resume = self.resume_selector.select_resume(
                                job_title=job.title,
                                job_description=job.description,
                                company=job.company
                            )
                            resume_to_use = selected_resume or self.settings.resume_path
                        else:
                            resume_to_use = self.settings.resume_path
                        
                        # Create application record
                        application = self.repository.create_application(
                            job_id=job.id,
                            status=ApplicationStatus.PENDING,
                            resume_used=resume_to_use
                        )
                        
                        success = await self.apply_to_job(job)
                        
                        if success:
                            self.stats["successful"] += 1
                            self.repository.update_application_status(
                                application.id,
                                ApplicationStatus.EASY_APPLY
                            )
                        else:
                            self.stats["failed"] += 1
                            self.repository.update_application_status(
                                application.id,
                                ApplicationStatus.FAILED,
                                error_message="Application could not be completed"
                            )
                        
                        progress.update(task, advance=1)
                        
                        # Delay between applications
                        await asyncio.sleep(5)
                        
            finally:
                await self.auth.close()
        
        # Print summary
        console.print("\n[bold green]Application Summary:[/bold green]")
        console.print(f"  Attempted: {self.stats['attempted']}")
        console.print(f"  Successful: {self.stats['successful']}")
        console.print(f"  Failed: {self.stats['failed']}")
        
        return self.stats
    
    async def run(self, max_applications: Optional[int] = None) -> Dict:
        """Run the job applier."""
        if not self.settings.auto_apply_enabled:
            console.print("[yellow]Auto-apply is disabled in settings.[/yellow]")
            return self.stats
        
        return await self.apply_to_jobs(max_applications=max_applications)
