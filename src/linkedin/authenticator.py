"""LinkedIn authentication handler."""
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import Page, Browser, BrowserContext, async_playwright
from rich.console import Console

from ..config import get_settings

console = Console()


class LinkedInAuthenticator:
    """Handles LinkedIn login and session management."""
    
    LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
    LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"
    STORAGE_STATE_PATH = "./browser_data/linkedin_session.json"
    
    def __init__(self):
        """Initialize authenticator."""
        self.settings = get_settings()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Ensure storage directory exists
        Path(self.STORAGE_STATE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    async def start_browser(self, playwright) -> Browser:
        """Start the browser instance."""
        self.browser = await playwright.chromium.launch(
            headless=self.settings.headless,
            slow_mo=self.settings.slow_mo
        )
        return self.browser
    
    async def get_context(self) -> BrowserContext:
        """Get browser context, loading saved session if available."""
        storage_path = Path(self.STORAGE_STATE_PATH)
        
        if storage_path.exists():
            console.print("[cyan]Loading saved session...[/cyan]")
            self.context = await self.browser.new_context(
                storage_state=str(storage_path)
            )
        else:
            console.print("[yellow]No saved session found, creating new context...[/yellow]")
            self.context = await self.browser.new_context()
        
        return self.context
    
    async def is_logged_in(self, page: Page) -> bool:
        """Check if user is currently logged in to LinkedIn."""
        try:
            await page.goto(self.LINKEDIN_FEED_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Check for feed elements that indicate logged-in state
            feed_selector = ".feed-shared-update-v2, .scaffold-layout__main"
            try:
                await page.wait_for_selector(feed_selector, timeout=5000)
                return True
            except:
                return False
        except Exception as e:
            console.print(f"[red]Error checking login status: {e}[/red]")
            return False
    
    async def login(self, page: Page) -> bool:
        """Perform LinkedIn login."""
        console.print("[cyan]Navigating to LinkedIn login page...[/cyan]")
        
        try:
            await page.goto(self.LINKEDIN_LOGIN_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Fill in credentials
            email_input = page.locator("#username")
            password_input = page.locator("#password")
            
            await email_input.fill(self.settings.linkedin_email)
            await password_input.fill(self.settings.linkedin_password)
            
            # Click sign in button
            await page.locator('button[type="submit"]').click()
            
            # Wait for navigation
            await page.wait_for_timeout(5000)
            
            # Check for security challenges
            if "checkpoint" in page.url or "challenge" in page.url:
                console.print("[yellow]Security challenge detected![/yellow]")
                console.print("[yellow]Please complete the verification manually...[/yellow]")
                
                # Wait for manual verification (up to 2 minutes)
                for i in range(24):
                    await page.wait_for_timeout(5000)
                    if "feed" in page.url or "jobs" in page.url:
                        break
                    console.print(f"[yellow]Waiting for verification... ({(i+1)*5}s)[/yellow]")
            
            # Verify login success
            if await self.is_logged_in(page):
                console.print("[green]Successfully logged in to LinkedIn![/green]")
                # Save session
                await self.save_session()
                return True
            else:
                console.print("[red]Login failed. Please check your credentials.[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Login error: {e}[/red]")
            return False
    
    async def save_session(self):
        """Save the current session state."""
        if self.context:
            await self.context.storage_state(path=self.STORAGE_STATE_PATH)
            console.print("[green]Session saved successfully.[/green]")
    
    async def ensure_logged_in(self) -> Page:
        """Ensure user is logged in and return the page."""
        if not self.context:
            raise RuntimeError("Browser context not initialized. Call get_context() first.")
        
        self.page = await self.context.new_page()
        
        if await self.is_logged_in(self.page):
            console.print("[green]Already logged in.[/green]")
            return self.page
        
        # Need to login
        if not self.settings.linkedin_email or not self.settings.linkedin_password:
            raise ValueError(
                "LinkedIn credentials not set. Please set LINKEDIN_EMAIL and "
                "LINKEDIN_PASSWORD in your .env file."
            )
        
        if await self.login(self.page):
            return self.page
        else:
            raise RuntimeError("Failed to log in to LinkedIn")
    
    async def close(self):
        """Close browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
