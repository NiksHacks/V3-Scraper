import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from apify import Actor
import httpx
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adslibrary import AdsLibrary
from facebook_business.exceptions import FacebookRequestError

class MetaAdsLibraryScraper:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.api = None
        self.client = None
        
    async def __aenter__(self):
        # Initialize Facebook API
        FacebookAdsApi.init(access_token=self.access_token)
        self.api = FacebookAdsApi.get_default_api()
        
        # Initialize HTTP client for direct API calls
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Meta Ads Library Scraper/1.0'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def search_ads(self, 
                        search_terms: Optional[str] = None,
                        ad_reached_countries: List[str] = ['IT'],
                        ad_active_status: str = 'ALL',
                        ad_type: str = 'ALL',
                        limit: int = 100,
                        max_pages: int = 10,
                        fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search ads in Meta Ads Library using the Graph API
        """
        if fields is None:
            fields = [
                'id',
                'ad_creation_time',
                'ad_creative_bodies',
                'ad_creative_link_captions', 
                'ad_creative_link_descriptions',
                'ad_creative_link_titles',
                'ad_delivery_start_time',
                'ad_delivery_stop_time',
                'ad_snapshot_url',
                'currency',
                'demographic_distribution',
                'funding_entity',
                'impressions',
                'page_id',
                'page_name',
                'publisher_platforms',
                'spend'
            ]
        
        all_ads = []
        page_count = 0
        next_page_token = None
        
        while page_count < max_pages:
            try:
                Actor.log.info(f"Fetching page {page_count + 1} of ads...")
                
                # Build API URL
                base_url = "https://graph.facebook.com/v18.0/ads_archive"
                params = {
                    'access_token': self.access_token,
                    'fields': ','.join(fields),
                    'ad_reached_countries': json.dumps(ad_reached_countries),
                    'ad_active_status': ad_active_status,
                    'ad_type': ad_type,
                    'limit': limit
                }
                
                if search_terms:
                    params['search_terms'] = search_terms
                    
                if next_page_token:
                    params['after'] = next_page_token
                
                # Make API request
                response = await self.client.get(base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' not in data:
                    Actor.log.warning("No data field in response")
                    break
                    
                ads_batch = data['data']
                if not ads_batch:
                    Actor.log.info("No more ads found")
                    break
                    
                # Process and clean ads data
                processed_ads = []
                for ad in ads_batch:
                    processed_ad = self.process_ad_data(ad)
                    processed_ads.append(processed_ad)
                    
                all_ads.extend(processed_ads)
                Actor.log.info(f"Processed {len(processed_ads)} ads from page {page_count + 1}")
                
                # Check for next page
                if 'paging' in data and 'next' in data['paging']:
                    # Extract after token from next URL
                    next_url = data['paging']['next']
                    if 'after=' in next_url:
                        next_page_token = next_url.split('after=')[1].split('&')[0]
                    else:
                        break
                else:
                    Actor.log.info("No more pages available")
                    break
                    
                page_count += 1
                
                # Small delay to respect rate limits
                await asyncio.sleep(1)
                
            except httpx.HTTPStatusError as e:
                Actor.log.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 429:  # Rate limit
                    Actor.log.info("Rate limit hit, waiting 60 seconds...")
                    await asyncio.sleep(60)
                    continue
                else:
                    break
            except Exception as e:
                Actor.log.error(f"Error fetching ads: {str(e)}")
                break
                
        Actor.log.info(f"Total ads collected: {len(all_ads)}")
        return all_ads
    
    def process_ad_data(self, ad: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and clean individual ad data
        """
        processed = {
            'ad_id': ad.get('id'),
            'page_name': ad.get('page_name'),
            'page_id': ad.get('page_id'),
            'ad_creation_time': ad.get('ad_creation_time'),
            'ad_delivery_start_time': ad.get('ad_delivery_start_time'),
            'ad_delivery_stop_time': ad.get('ad_delivery_stop_time'),
            'ad_snapshot_url': ad.get('ad_snapshot_url'),
            'currency': ad.get('currency'),
            'funding_entity': ad.get('funding_entity'),
            'impressions': ad.get('impressions', {}),
            'spend': ad.get('spend', {}),
            'demographic_distribution': ad.get('demographic_distribution', []),
            'publisher_platforms': ad.get('publisher_platforms', []),
            'scraped_at': datetime.now().isoformat()
        }
        
        # Process creative content
        if 'ad_creative_bodies' in ad and ad['ad_creative_bodies']:
            processed['ad_creative_body'] = ad['ad_creative_bodies'][0] if ad['ad_creative_bodies'] else ''
        else:
            processed['ad_creative_body'] = ''
            
        if 'ad_creative_link_captions' in ad and ad['ad_creative_link_captions']:
            processed['ad_creative_link_caption'] = ad['ad_creative_link_captions'][0] if ad['ad_creative_link_captions'] else ''
        else:
            processed['ad_creative_link_caption'] = ''
            
        if 'ad_creative_link_descriptions' in ad and ad['ad_creative_link_descriptions']:
            processed['ad_creative_link_description'] = ad['ad_creative_link_descriptions'][0] if ad['ad_creative_link_descriptions'] else ''
        else:
            processed['ad_creative_link_description'] = ''
            
        if 'ad_creative_link_titles' in ad and ad['ad_creative_link_titles']:
            processed['ad_creative_link_title'] = ad['ad_creative_link_titles'][0] if ad['ad_creative_link_titles'] else ''
        else:
            processed['ad_creative_link_title'] = ''
        
        return processed

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        
        # Validate required input
        access_token = actor_input.get('accessToken')
        if not access_token:
            Actor.log.error("Access token is required. Please provide 'accessToken' in the input.")
            return
            
        # Input parameters
        search_terms = actor_input.get('searchTerms')
        ad_reached_countries = actor_input.get('adReachedCountries', ['IT'])
        ad_active_status = actor_input.get('adActiveStatus', 'ALL')
        ad_type = actor_input.get('adType', 'ALL')
        limit = actor_input.get('limit', 100)
        max_pages = actor_input.get('maxPages', 10)
        fields = actor_input.get('fields')
        
        Actor.log.info(f"Starting Meta Ads Library scraper")
        Actor.log.info(f"Search terms: {search_terms or 'None'}")
        Actor.log.info(f"Countries: {ad_reached_countries}")
        Actor.log.info(f"Ad status: {ad_active_status}")
        Actor.log.info(f"Ad type: {ad_type}")
        Actor.log.info(f"Limit per page: {limit}")
        Actor.log.info(f"Max pages: {max_pages}")
        
        try:
            async with MetaAdsLibraryScraper(access_token) as scraper:
                ads = await scraper.search_ads(
                    search_terms=search_terms,
                    ad_reached_countries=ad_reached_countries,
                    ad_active_status=ad_active_status,
                    ad_type=ad_type,
                    limit=limit,
                    max_pages=max_pages,
                    fields=fields
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