import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import urllib.parse

from apify import Actor
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class MetaAdsLibraryWebScraper:
    def __init__(self):
        self.base_url = "https://www.facebook.com/ads/library"
        self.client = None
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        # Initialize HTTP client for basic requests
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        
        # Initialize Playwright for dynamic content
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page()
        
        # Set user agent
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        if self.client:
            await self.client.aclose()

    async def search_ads(self, 
                        search_terms: Optional[str] = None,
                        ad_reached_countries: List[str] = ['IT'],
                        ad_active_status: str = 'ALL',
                        ad_type: str = 'ALL',
                        limit: int = 50,
                        max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Search ads in Meta Ads Library using web scraping
        """
        all_ads = []
        
        try:
            # Build search URL
            search_url = self.build_search_url(
                search_terms=search_terms,
                countries=ad_reached_countries,
                ad_type=ad_type,
                ad_active_status=ad_active_status
            )
            
            Actor.log.info(f"Navigating to: {search_url}")
            
            # Navigate to the search page
            await self.page.goto(search_url, wait_until='networkidle')
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Handle cookie consent if present
            await self.handle_cookie_consent()
            
            # Scroll and load more ads
            ads_collected = 0
            scroll_attempts = 0
            max_scroll_attempts = max_pages * 3
            
            while ads_collected < limit and scroll_attempts < max_scroll_attempts:
                # Extract ads from current page
                page_ads = await self.extract_ads_from_page()
                
                # Add new ads (avoid duplicates)
                new_ads = []
                existing_ids = {ad.get('ad_id') for ad in all_ads}
                
                for ad in page_ads:
                    if ad.get('ad_id') not in existing_ids:
                        new_ads.append(ad)
                        existing_ids.add(ad.get('ad_id'))
                
                all_ads.extend(new_ads)
                ads_collected = len(all_ads)
                
                Actor.log.info(f"Found {len(new_ads)} new ads, total: {ads_collected}")
                
                if len(new_ads) == 0:
                    Actor.log.info("No new ads found, stopping")
                    break
                
                # Scroll to load more content
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
                
                # Try to click "See More" button if present
                try:
                    see_more_button = await self.page.query_selector('[data-testid="see-more-button"], [aria-label*="See more"], [aria-label*="Load more"]')
                    if see_more_button:
                        await see_more_button.click()
                        await asyncio.sleep(3)
                except Exception:
                    pass
                
                scroll_attempts += 1
                
                if ads_collected >= limit:
                    break
                    
        except Exception as e:
            Actor.log.error(f"Error during scraping: {str(e)}")
            
        Actor.log.info(f"Total ads collected: {len(all_ads)}")
        return all_ads[:limit]  # Return only up to the limit
    
    def build_search_url(self, search_terms: Optional[str], countries: List[str], 
                        ad_type: str, ad_active_status: str) -> str:
        """
        Build the search URL for Meta Ads Library
        """
        params = {
            'active_status': 'all' if ad_active_status == 'ALL' else ad_active_status.lower(),
            'ad_type': 'all' if ad_type == 'ALL' else ad_type.lower(),
            'country': ','.join(countries),
            'media_type': 'all'
        }
        
        if search_terms:
            params['q'] = search_terms
            
        query_string = urllib.parse.urlencode(params)
        return f"{self.base_url}?{query_string}"
    
    async def handle_cookie_consent(self):
        """
        Handle cookie consent popup if present
        """
        try:
            # Look for common cookie consent buttons
            consent_selectors = [
                '[data-testid="cookie-policy-manage-dialog-accept-button"]',
                '[aria-label*="Accept"]',
                '[aria-label*="Allow"]',
                'button:has-text("Accept")',
                'button:has-text("Allow")',
                'button:has-text("OK")'
            ]
            
            for selector in consent_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        await button.click()
                        await asyncio.sleep(1)
                        break
                except Exception:
                    continue
                    
        except Exception as e:
            Actor.log.debug(f"Cookie consent handling: {str(e)}")
    
    async def extract_ads_from_page(self) -> List[Dict[str, Any]]:
        """
        Extract ad data from the current page
        """
        ads = []
        
        try:
            # Get page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find ad containers - these selectors may need adjustment based on Facebook's current structure
            ad_containers = soup.find_all(['div'], attrs={
                'data-testid': lambda x: x and 'ad-library-card' in x if x else False
            })
            
            # If the above doesn't work, try more generic selectors
            if not ad_containers:
                # Look for containers that might contain ads
                potential_containers = soup.find_all('div', class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['card', 'result', 'item', 'ad']
                ) if x else False)
                
                # Filter containers that seem to contain ad data
                ad_containers = []
                for container in potential_containers:
                    if self.looks_like_ad_container(container):
                        ad_containers.append(container)
            
            Actor.log.info(f"Found {len(ad_containers)} potential ad containers")
            
            for i, container in enumerate(ad_containers):
                try:
                    ad_data = self.extract_ad_data_from_container(container)
                    if ad_data:
                        ads.append(ad_data)
                except Exception as e:
                    Actor.log.debug(f"Error extracting ad {i}: {str(e)}")
                    
        except Exception as e:
            Actor.log.error(f"Error extracting ads from page: {str(e)}")
            
        return ads
    
    def looks_like_ad_container(self, container) -> bool:
        """
        Determine if a container likely contains an ad
        """
        text = container.get_text().lower()
        
        # Look for indicators that this is an ad
        ad_indicators = [
            'sponsored',
            'ad library',
            'page name',
            'started running',
            'see ad details',
            'impressions',
            'spend'
        ]
        
        return any(indicator in text for indicator in ad_indicators)
    
    def extract_ad_data_from_container(self, container) -> Optional[Dict[str, Any]]:
        """
        Extract ad data from a single container
        """
        try:
            ad_data = {
                'ad_id': self.generate_ad_id(container),
                'page_name': self.extract_page_name(container),
                'ad_creative_body': self.extract_ad_text(container),
                'ad_snapshot_url': self.extract_snapshot_url(container),
                'ad_delivery_start_time': self.extract_start_date(container),
                'impressions': self.extract_impressions(container),
                'spend': self.extract_spend(container),
                'scraped_at': datetime.now().isoformat(),
                'source': 'web_scraping'
            }
            
            # Only return if we have some meaningful data
            if ad_data['page_name'] or ad_data['ad_creative_body']:
                return ad_data
                
        except Exception as e:
            Actor.log.debug(f"Error extracting ad data: {str(e)}")
            
        return None
    
    def generate_ad_id(self, container) -> str:
        """
        Generate a unique ID for the ad based on content
        """
        # Try to find an actual ID in the HTML
        for attr in ['data-id', 'id', 'data-testid']:
            if container.get(attr):
                return str(container.get(attr))
        
        # Generate based on content hash
        content = container.get_text()[:100]
        return f"web_ad_{hash(content) % 1000000}"
    
    def extract_page_name(self, container) -> str:
        """
        Extract the page name from the container
        """
        # Look for page name in various possible locations
        selectors = [
            '[data-testid*="page-name"]',
            '.page-name',
            'h3',
            'h4',
            'strong'
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""
    
    def extract_ad_text(self, container) -> str:
        """
        Extract the main ad text
        """
        # Look for the main ad content
        text_elements = container.find_all(['p', 'div', 'span'])
        
        # Find the longest text that looks like ad content
        longest_text = ""
        for element in text_elements:
            text = element.get_text().strip()
            if len(text) > len(longest_text) and len(text) > 20:
                longest_text = text
        
        return longest_text
    
    def extract_snapshot_url(self, container) -> str:
        """
        Extract the ad snapshot URL
        """
        # Look for links that might be the snapshot
        links = container.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'ads/library' in href or 'ad_archive' in href:
                if href.startswith('/'):
                    return f"https://www.facebook.com{href}"
                return href
        return ""
    
    def extract_start_date(self, container) -> str:
        """
        Extract when the ad started running
        """
        text = container.get_text()
        
        # Look for date patterns
        date_patterns = [
            r'Started running on ([A-Za-z]+ \d+, \d+)',
            r'Running since ([A-Za-z]+ \d+, \d+)',
            r'Active since ([A-Za-z]+ \d+, \d+)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ""
    
    def extract_impressions(self, container) -> str:
        """
        Extract impressions data
        """
        text = container.get_text()
        
        # Look for impression patterns
        impression_patterns = [
            r'(\d+[KMB]?) impressions',
            r'Reached ([\d,]+[KMB]?) people',
            r'([\d,]+[KMB]?) views'
        ]
        
        for pattern in impression_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def extract_spend(self, container) -> str:
        """
        Extract spend data
        """
        text = container.get_text()
        
        # Look for spend patterns
        spend_patterns = [
            r'€([\d,]+(?:\.\d+)?)',
            r'\$([\d,]+(?:\.\d+)?)',
            r'([\d,]+(?:\.\d+)?) EUR',
            r'([\d,]+(?:\.\d+)?) USD'
        ]
        
        for pattern in spend_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ""

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        
        # Input parameters (no access token needed)
        search_terms = actor_input.get('searchTerms', 'Marketing')
        ad_reached_countries = actor_input.get('adReachedCountries', ['IT'])
        ad_active_status = actor_input.get('adActiveStatus', 'ALL')
        ad_type = actor_input.get('adType', 'ALL')
        limit = actor_input.get('limit', 50)
        max_pages = actor_input.get('maxPages', 5)
        
        Actor.log.info(f"Starting Meta Ads Library web scraper")
        Actor.log.info(f"Search terms: {search_terms}")
        Actor.log.info(f"Countries: {ad_reached_countries}")
        Actor.log.info(f"Ad status: {ad_active_status}")
        Actor.log.info(f"Ad type: {ad_type}")
        Actor.log.info(f"Limit: {limit}")
        Actor.log.info(f"Max pages: {max_pages}")
        
        try:
            async with MetaAdsLibraryWebScraper() as scraper:
                ads = await scraper.search_ads(
                    search_terms=search_terms,
                    ad_reached_countries=ad_reached_countries,
                    ad_active_status=ad_active_status,
                    ad_type=ad_type,
                    limit=limit,
                    max_pages=max_pages
                )
                
                if ads:
                    await Actor.push_data(ads)
                    Actor.log.info(f"Successfully scraped {len(ads)} ads")
                else:
                    Actor.log.warning("No ads were found with the given criteria")
                    
        except Exception as e:
            Actor.log.error(f"Error during scraping: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(main())