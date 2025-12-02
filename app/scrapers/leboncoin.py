"""
Scraper for Leboncoin.fr
"""
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from loguru import logger
from app.scrapers.base import BaseScraper


class LeboncoinScraper(BaseScraper):
    """
    Scraper for Leboncoin.fr housing listings.
    """
    
    BASE_URL = "https://www.leboncoin.fr/recherche"
    
    def __init__(self):
        super().__init__("leboncoin")
    
    def scrape_listings(self, search_params: Optional[Dict] = None) -> List[Dict]:
        """
        Scrape listings from Leboncoin.
        
        Args:
            search_params: Search parameters (location, price_min, price_max, etc.)
            
        Returns:
            List of listing dictionaries
        """
        listings = []
        
        # Build search URL
        params = {
            'text': '',
            'category': '9',  # Real estate category
            'locations': search_params.get('location', '') if search_params else '',
        }
        
        if search_params:
            if 'price_min' in search_params:
                params['price_min'] = search_params['price_min']
            if 'price_max' in search_params:
                params['price_max'] = search_params['price_max']
            if 'surface_min' in search_params:
                params['surface_min'] = search_params['surface_min']
        
        response = self.fetch_page(self.BASE_URL, params=params)
        if not response:
            return listings
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing containers (this selector may need adjustment based on actual HTML structure)
            listing_elements = soup.find_all('div', class_='aditem') or soup.find_all('a', class_='aditem')
            
            for element in listing_elements:
                try:
                    listing = self._parse_listing_element(element)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error parsing Leboncoin listing: {e}")
                    continue
            
            logger.info(f"Scraped {len(listings)} listings from Leboncoin")
            
        except Exception as e:
            logger.error(f"Error scraping Leboncoin: {e}")
        
        return listings
    
    def _parse_listing_element(self, element) -> Optional[Dict]:
        """
        Parse a single listing element from HTML.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Listing dictionary or None
        """
        try:
            # Extract URL
            link = element.find('a') if element.name != 'a' else element
            if not link or not link.get('href'):
                return None
            
            url = link.get('href')
            if not url.startswith('http'):
                url = f"https://www.leboncoin.fr{url}"
            
            # Extract title
            title_elem = element.find('span', class_='aditem_title') or element.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract price
            price_elem = element.find('span', class_='aditem_price') or element.find(class_='price')
            price_text = price_elem.get_text(strip=True) if price_elem else ''
            price = self._extract_price(price_text)
            
            # Extract location
            location_elem = element.find('span', class_='aditem_location') or element.find(class_='location')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Extract source ID from URL
            source_id = url.split('/')[-1].split('.')[0] if url else ''
            
            return {
                'source_id': source_id,
                'source_url': url,
                'title': title,
                'price': price,
                'city': location,
                'description': '',
            }
        except Exception as e:
            logger.warning(f"Error parsing listing element: {e}")
            return None
    
    def parse_listing(self, listing_data: Dict) -> Dict:
        """
        Parse a single listing from raw data.
        
        Args:
            listing_data: Raw listing data
            
        Returns:
            Parsed listing dictionary
        """
        return self.normalize_listing(listing_data)
    
    @staticmethod
    def _extract_price(price_text: str) -> Optional[float]:
        """
        Extract numeric price from text.
        
        Args:
            price_text: Price text (e.g., "1 200 €")
            
        Returns:
            Price as float or None
        """
        try:
            # Remove currency symbols and spaces
            price_clean = price_text.replace('€', '').replace(' ', '').replace(',', '.')
            return float(price_clean)
        except (ValueError, AttributeError):
            return None

