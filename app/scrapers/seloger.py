"""
Scraper for SeLoger.com
"""
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from loguru import logger
from app.scrapers.base import BaseScraper


class SeLogerScraper(BaseScraper):
    """
    Scraper for SeLoger.com housing listings.
    """
    
    BASE_URL = "https://www.seloger.com/list.htm"
    
    def __init__(self):
        super().__init__("seloger")
    
    def scrape_listings(self, search_params: Optional[Dict] = None) -> List[Dict]:
        """
        Scrape listings from SeLoger.
        
        Args:
            search_params: Search parameters (location, price_min, price_max, etc.)
            
        Returns:
            List of listing dictionaries
        """
        listings = []
        
        # Build search URL
        params = {
            'types': '2',  # Rental
        }
        
        if search_params:
            if 'location' in search_params:
                params['projects'] = '2'  # Rental
                params['idtt'] = '2'
                # Location would need to be converted to SeLoger's location codes
            if 'price_max' in search_params:
                params['price'] = f"0/{search_params['price_max']}"
            if 'surface_min' in search_params:
                params['surface'] = f"{search_params['surface_min']}/999"
        
        response = self.fetch_page(self.BASE_URL, params=params)
        if not response:
            return listings
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing containers (this selector may need adjustment)
            listing_elements = soup.find_all('div', class_='c-pa-link') or soup.find_all('a', class_='c-pa-link')
            
            for element in listing_elements:
                try:
                    listing = self._parse_listing_element(element)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error parsing SeLoger listing: {e}")
                    continue
            
            logger.info(f"Scraped {len(listings)} listings from SeLoger")
            
        except Exception as e:
            logger.error(f"Error scraping SeLoger: {e}")
        
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
                url = f"https://www.seloger.com{url}"
            
            # Extract title
            title_elem = element.find('h2', class_='c-pa-link__title') or element.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract price
            price_elem = element.find('div', class_='c-pa-price') or element.find(class_='price')
            price_text = price_elem.get_text(strip=True) if price_elem else ''
            price = self._extract_price(price_text)
            
            # Extract location
            location_elem = element.find('div', class_='c-pa-city') or element.find(class_='location')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Extract surface and rooms
            details_elem = element.find('div', class_='c-pa-criterion')
            surface = None
            rooms = None
            if details_elem:
                details_text = details_elem.get_text()
                surface = self._extract_surface(details_text)
                rooms = self._extract_rooms(details_text)
            
            # Extract source ID from URL
            source_id = url.split('/')[-1].split('.')[0] if url else ''
            
            return {
                'source_id': source_id,
                'source_url': url,
                'title': title,
                'price': price,
                'surface': surface,
                'rooms': rooms,
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
            price_clean = price_text.replace('€', '').replace(' ', '').replace(',', '.')
            return float(price_clean)
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def _extract_surface(text: str) -> Optional[float]:
        """
        Extract surface area from text.
        
        Args:
            text: Text containing surface information
            
        Returns:
            Surface as float or None
        """
        import re
        try:
            match = re.search(r'(\d+(?:[.,]\d+)?)\s*m', text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', '.'))
        except (ValueError, AttributeError):
            pass
        return None
    
    @staticmethod
    def _extract_rooms(text: str) -> Optional[int]:
        """
        Extract number of rooms from text.
        
        Args:
            text: Text containing room information
            
        Returns:
            Number of rooms as int or None
        """
        import re
        try:
            match = re.search(r'(\d+)\s*(?:pièce|chambre)', text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except (ValueError, AttributeError):
            pass
        return None

