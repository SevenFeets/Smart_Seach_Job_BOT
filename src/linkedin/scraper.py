"""LinkedIn job scraper using Playwright."""
import re
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlencode
from playwright.async_api import Page, async_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import get_settings, ExperienceLevel, DatePosted
from ..database import JobRepository
from .authenticator import LinkedInAuthenticator

console = Console()


class LinkedInScraper:
    """Scrapes job listings from LinkedIn."""
    
    JOBS_SEARCH_URL = "https://www.linkedin.com/jobs/search/"
    
    def __init__(self):
        """Initialize the scraper."""
        self.settings = get_settings()
        self.auth = LinkedInAuthenticator()
        self.repository = JobRepository()
        self.page: Optional[Page] = None
    
    def build_search_url(
        self,
        keywords: str,
        location: Optional[str] = None,
        experience_levels: Optional[List[ExperienceLevel]] = None,
        date_posted: Optional[DatePosted] = None,
        easy_apply_only: bool = False,
        page: int = 0
    ) -> str:
        """Build LinkedIn job search URL with filters."""
        params = {
            "keywords": keywords,
            "location": location or self.settings.location,
            "sortBy": "DD",  # Sort by date
            "start": page * 25,  # 25 jobs per page
        }
        
        # Add experience level filter
        if experience_levels:
            exp_values = ",".join([level.value for level in experience_levels])
            params["f_E"] = exp_values
        
        # Add date posted filter
        if date_posted and date_posted.value:
            params["f_TPR"] = date_posted.value
        
        # Add Easy Apply filter
        if easy_apply_only:
            params["f_AL"] = "true"
        
        return f"{self.JOBS_SEARCH_URL}?{urlencode(params)}"
    
    async def search_jobs(
        self,
        keywords: str,
        max_pages: int = 3,
        easy_apply_only: bool = False
    ) -> List[Dict]:
        """Search for jobs with given keywords."""
        all_jobs = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"[cyan]Searching jobs for '{keywords}'...",
                total=max_pages
            )
            
            for page_num in range(max_pages):
                search_url = self.build_search_url(
                    keywords=keywords,
                    experience_levels=self.settings.experience_levels_list,
                    date_posted=self.settings.date_posted_filter,
                    easy_apply_only=easy_apply_only,
                    page=page_num
                )
                
                console.print(f"[dim]Page {page_num + 1}: {search_url}[/dim]")
                
                jobs = await self._scrape_job_listings(search_url, keywords)
                all_jobs.extend(jobs)
                
                progress.update(task, advance=1)
                
                # Small delay between pages
                await asyncio.sleep(2)
                
                # If we got less than 25 jobs, we've reached the end
                if len(jobs) < 20:
                    break
        
        return all_jobs
    
    async def _scrape_job_listings(self, url: str, search_keyword: str) -> List[Dict]:
        """Scrape job listings from a search results page."""
        jobs = []
        
        try:
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)
            
            # Wait for job cards to load
            try:
                await self.page.wait_for_selector(
                    ".jobs-search-results__list-item, .job-card-container",
                    timeout=10000
                )
            except:
                console.print("[yellow]No job listings found on this page.[/yellow]")
                return jobs
            
            # Scroll to load more jobs
            await self._scroll_job_list()
            
            # Get all job cards
            job_cards = await self.page.query_selector_all(
                ".jobs-search-results__list-item, .job-card-container"
            )
            
            console.print(f"[cyan]Found {len(job_cards)} job cards[/cyan]")
            
            for card in job_cards:
                try:
                    job_data = await self._extract_job_from_card(card, search_keyword)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    console.print(f"[red]Error extracting job: {e}[/red]")
                    continue
            
        except Exception as e:
            console.print(f"[red]Error scraping job listings: {e}[/red]")
        
        return jobs
    
    async def _scroll_job_list(self):
        """Scroll the job list to load more results."""
        job_list = await self.page.query_selector(".jobs-search-results-list")
        if job_list:
            for _ in range(3):
                await job_list.evaluate("el => el.scrollTop += 500")
                await self.page.wait_for_timeout(500)
    
    async def _extract_job_from_card(
        self,
        card,
        search_keyword: str
    ) -> Optional[Dict]:
        """Extract job data from a job card element."""
        try:
            # Get job ID from data attribute or link
            job_id = await card.get_attribute("data-job-id")
            if not job_id:
                # Try to extract from link
                link = await card.query_selector("a[href*='/jobs/view/']")
                if link:
                    href = await link.get_attribute("href")
                    match = re.search(r"/jobs/view/(\d+)", href)
                    if match:
                        job_id = match.group(1)
            
            if not job_id:
                return None
            
            # Extract title
            title_elem = await card.query_selector(
                ".job-card-list__title, .job-card-container__link, "
                "a[data-control-name='job_card_title']"
            )
            title = await title_elem.inner_text() if title_elem else "Unknown"
            title = title.strip()
            
            # Extract company
            company_elem = await card.query_selector(
                ".job-card-container__company-name, "
                ".job-card-container__primary-description, "
                ".artdeco-entity-lockup__subtitle"
            )
            company = await company_elem.inner_text() if company_elem else "Unknown"
            company = company.strip()
            
            # Extract location
            location_elem = await card.query_selector(
                ".job-card-container__metadata-item, "
                ".artdeco-entity-lockup__caption"
            )
            location = await location_elem.inner_text() if location_elem else ""
            location = location.strip()
            
            # Check for Easy Apply badge
            easy_apply_badge = await card.query_selector(
                ".job-card-container__apply-method, "
                "[class*='easy-apply'], "
                ".jobs-apply-button--top-card"
            )
            is_easy_apply = easy_apply_badge is not None
            
            # If badge not found, check text content
            if not is_easy_apply:
                card_text = await card.inner_text()
                is_easy_apply = "Easy Apply" in card_text or "easy apply" in card_text.lower()
            
            # Extract posted date
            posted_elem = await card.query_selector(
                ".job-card-container__footer-item, time"
            )
            posted_date = await posted_elem.inner_text() if posted_elem else ""
            posted_date = posted_date.strip()
            
            # Build job URL
            job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
            
            return {
                "linkedin_job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "job_url": job_url,
                "posted_date": posted_date,
                "is_easy_apply": is_easy_apply,
                "search_keyword": search_keyword,
                "scraped_at": datetime.utcnow()
            }
            
        except Exception as e:
            console.print(f"[dim red]Error parsing card: {e}[/dim red]")
            return None
    
    async def get_job_details(self, job_url: str) -> Dict:
        """Get detailed information about a specific job."""
        details = {}
        
        try:
            await self.page.goto(job_url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)
            
            # Get job description
            desc_elem = await self.page.query_selector(
                ".jobs-description__content, "
                ".jobs-box__html-content, "
                "[class*='description']"
            )
            if desc_elem:
                details["description"] = await desc_elem.inner_text()
            
            # Get additional details from the side panel
            detail_items = await self.page.query_selector_all(
                ".jobs-unified-top-card__job-insight, "
                ".job-details-jobs-unified-top-card__job-insight"
            )
            
            for item in detail_items:
                text = await item.inner_text()
                text_lower = text.lower()
                
                if "experience" in text_lower or "level" in text_lower:
                    details["experience_level"] = text.strip()
                elif "full-time" in text_lower or "part-time" in text_lower or "contract" in text_lower:
                    details["employment_type"] = text.strip()
                elif "$" in text or "salary" in text_lower:
                    details["salary_range"] = text.strip()
            
            # Get applicant count
            applicant_elem = await self.page.query_selector(
                ".jobs-unified-top-card__applicant-count, "
                "[class*='applicant']"
            )
            if applicant_elem:
                details["applicant_count"] = await applicant_elem.inner_text()
            
        except Exception as e:
            console.print(f"[red]Error getting job details: {e}[/red]")
        
        return details
    
    async def run(
        self,
        keywords: Optional[List[str]] = None,
        max_pages_per_keyword: int = 3,
        get_details: bool = False,
        easy_apply_only: bool = False
    ) -> List[Dict]:
        """Run the scraper for multiple keywords."""
        keywords = keywords or self.settings.keywords_list
        all_jobs = []
        
        async with async_playwright() as playwright:
            # Start browser and authenticate
            await self.auth.start_browser(playwright)
            await self.auth.get_context()
            self.page = await self.auth.ensure_logged_in()
            
            try:
                for keyword in keywords:
                    console.print(f"\n[bold cyan]Searching for: {keyword}[/bold cyan]")
                    
                    jobs = await self.search_jobs(
                        keywords=keyword,
                        max_pages=max_pages_per_keyword,
                        easy_apply_only=easy_apply_only
                    )
                    
                    # Save to database
                    added = self.repository.add_jobs_batch(jobs)
                    console.print(
                        f"[green]Found {len(jobs)} jobs, "
                        f"{len(added)} new jobs added to database[/green]"
                    )
                    
                    # Optionally get detailed info for new jobs
                    if get_details and added:
                        console.print("[cyan]Getting job details...[/cyan]")
                        for job in added[:5]:  # Limit to first 5 to avoid rate limiting
                            details = await self.get_job_details(job.job_url)
                            # Update job with details (would need repo method)
                            await asyncio.sleep(1)
                    
                    all_jobs.extend(jobs)
                    
                    # Delay between keywords
                    await asyncio.sleep(3)
                    
            finally:
                await self.auth.close()
        
        # Print summary
        stats = self.repository.get_application_stats()
        console.print("\n[bold green]Database Stats:[/bold green]")
        console.print(f"  Total jobs in database: {stats['total_jobs']}")
        console.print(f"  Total applications: {stats['total_applications']}")
        
        return all_jobs
