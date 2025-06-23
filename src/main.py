import asyncio
import json
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional

from apify import Actor
import httpx
from bs4 import BeautifulSoup
from parsel import Selector
import w3lib.html
import w3lib.url

class NHKHackScraper:
    def __init__(self):
        self.client = None
        self.visited_urls = set()
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a single page and extract data"""
        try:
            Actor.log.info(f"Fetching: {url}")
            response = await self.client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                Actor.log.warning(f"Skipping non-HTML content: {url}")
                return None
                
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            selector = Selector(text=html)
            
            # Extract basic page data
            page_data = {
                'url': url,
                'title': self.extract_title(soup),
                'text': self.extract_text(soup),
                'html': html,
                'links': self.extract_links(soup, url),
                'images': self.extract_images(soup, url),
                'metadata': self.extract_metadata(soup, selector)
            }
            
            return page_data
            
        except httpx.HTTPStatusError as e:
            Actor.log.error(f"HTTP error for {url}: {e.response.status_code}")
            return None
        except Exception as e:
            Actor.log.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
            
        return ''

    def extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from the page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            links.append({
                'url': absolute_url,
                'text': link.get_text().strip(),
                'title': link.get('title', '')
            })
            
        return links

    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images from the page"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            
            images.append({
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
            
        return images

    def extract_metadata(self, soup: BeautifulSoup, selector: Selector) -> Dict[str, Any]:
        """Extract metadata from the page"""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
                
        # JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        structured_data = []
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
                
        if structured_data:
            metadata['structured_data'] = structured_data
            
        return metadata

    def should_follow_link(self, url: str, allowed_domains: List[str], max_depth: int, current_depth: int) -> bool:
        """Determine if a link should be followed"""
        if current_depth >= max_depth:
            return False
            
        if url in self.visited_urls:
            return False
            
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        if allowed_domains:
            return any(allowed_domain in domain for allowed_domain in allowed_domains)
            
        return True

    async def crawl_website(self, start_urls: List[str], max_pages: int = 10, max_depth: int = 1, allowed_domains: List[str] = None) -> List[Dict[str, Any]]:
        """Crawl multiple pages starting from given URLs"""
        results = []
        urls_to_visit = [(url, 0) for url in start_urls]  # (url, depth)
        
        while urls_to_visit and len(results) < max_pages:
            current_url, current_depth = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            page_data = await self.fetch_page(current_url)
            
            if page_data:
                results.append(page_data)
                
                # Add links for further crawling if within depth limit
                if current_depth < max_depth:
                    for link in page_data.get('links', []):
                        link_url = link['url']
                        if self.should_follow_link(link_url, allowed_domains, max_depth, current_depth + 1):
                            urls_to_visit.append((link_url, current_depth + 1))
                            
        return results

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        
        # Input parameters
        start_urls = actor_input.get('startUrls', [])
        if isinstance(start_urls, str):
            start_urls = [start_urls]
            
        max_pages = actor_input.get('maxPages', 10)
        max_depth = actor_input.get('maxDepth', 1)
        allowed_domains = actor_input.get('allowedDomains', [])
        
        # Validate input
        if not start_urls:
            Actor.log.error("No start URLs provided. Please specify 'startUrls' in the input.")
            return
            
        Actor.log.info(f"Starting NHK Hack scraper with {len(start_urls)} URLs")
        Actor.log.info(f"Max pages: {max_pages}, Max depth: {max_depth}")
        
        async with NHKHackScraper() as scraper:
            if max_depth > 1:
                # Crawling mode
                Actor.log.info("Running in crawling mode")
                results = await scraper.crawl_website(start_urls, max_pages, max_depth, allowed_domains)
            else:
                # Single page scraping mode
                Actor.log.info("Running in single page scraping mode")
                results = []
                for url in start_urls[:max_pages]:
                    page_data = await scraper.fetch_page(url)
                    if page_data:
                        results.append(page_data)
                        
            # Save results
            if results:
                await Actor.push_data(results)
                Actor.log.info(f"Successfully scraped {len(results)} pages")
            else:
                Actor.log.warning("No data was scraped")

if __name__ == "__main__":
    asyncio.run(main())