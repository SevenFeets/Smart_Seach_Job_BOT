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
        # Use more realistic browser args to avoid detection
        self.browser = await playwright.chromium.launch(
            headless=self.settings.headless,
            slow_mo=self.settings.slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        return self.browser
    
    async def get_context(self) -> BrowserContext:
        """Get browser context, loading saved session if available."""
        storage_path = Path(self.STORAGE_STATE_PATH)
        
        # Add realistic browser context settings
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
            'permissions': ['geolocation'],
            'geolocation': {'latitude': 40.7128, 'longitude': -74.0060},  # New York
            'extra_http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        }
        
        if storage_path.exists():
            console.print("[cyan]Loading saved session...[/cyan]")
            context_options['storage_state'] = str(storage_path)
            self.context = await self.browser.new_context(**context_options)
        else:
            console.print("[yellow]No saved session found, creating new context...[/yellow]")
            self.context = await self.browser.new_context(**context_options)
        
        return self.context
    
    async def is_logged_in(self, page: Page) -> bool:
        """Check if user is currently logged in to LinkedIn."""
        try:
            # Add stealth scripts before navigation
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = { runtime: {} };
            """)
            
            await page.goto(self.LINKEDIN_FEED_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Check for feed elements that indicate logged-in state
            feed_selector = ".feed-shared-update-v2, .scaffold-layout__main, nav.global-nav"
            try:
                await page.wait_for_selector(feed_selector, timeout=8000)
                # Additional check: make sure we're not on login page
                current_url = page.url
                if "login" in current_url or "checkpoint" in current_url or "challenge" in current_url:
                    return False
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
    
    def is_session_file_valid(self) -> bool:
        """Check if session file exists and is not too old."""
        from datetime import datetime, timedelta
        import json
        
        storage_path = Path(self.STORAGE_STATE_PATH)
        if not storage_path.exists():
            return False
        
        try:
            # Check file age (LinkedIn sessions typically last 30 days)
            file_age = datetime.now() - datetime.fromtimestamp(storage_path.stat().st_mtime)
            if file_age > timedelta(days=25):  # Refresh before 30 days
                console.print("[yellow]Session file is older than 25 days, may need refresh[/yellow]")
                return False
            
            # Check if file is valid JSON
            with open(storage_path, 'r') as f:
                data = json.load(f)
                if not data.get('cookies'):
                    console.print("[yellow]Session file has no cookies[/yellow]")
                    return False
            
            return True
        except Exception as e:
            console.print(f"[yellow]Session file validation failed: {e}[/yellow]")
            return False
    
    async def ensure_logged_in(self) -> Page:
        """Ensure user is logged in and return the page."""
        if not self.context:
            raise RuntimeError("Browser context not initialized. Call get_context() first.")
        
        self.page = await self.context.new_page()
        
        # Add stealth scripts to every page
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            window.chrome = { runtime: {} };
        """)
        
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
