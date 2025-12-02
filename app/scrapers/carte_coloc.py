"""
Scraper for La Carte des Coloc
"""
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from loguru import logger
from app.scrapers.base import BaseScraper


class CarteColocScraper(BaseScraper):
    """
    Scraper for La Carte des Coloc housing listings.
    """
    
    BASE_URL = "https://www.lacartedescolocs.fr"
    
    def __init__(self):
        super().__init__("carte_coloc")
    
    def scrape_listings(self, search_params: Optional[Dict] = None) -> List[Dict]:
        """
        Scrape listings from La Carte des Coloc.
        
        Args:
            search_params: Search parameters (location, price_min, price_max, etc.)
            
        Returns:
            List of listing dictionaries
        """
        listings = []
        
        # Build search URL
        search_url = f"{self.BASE_URL}/annonces"
        
        params = {}
        if search_params:
            if 'location' in search_params:
                params['ville'] = search_params['location']
            if 'price_max' in search_params:
                params['prix_max'] = search_params['price_max']
        
        response = self.fetch_page(search_url, params=params)
        if not response:
            return listings
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing containers (this selector may need adjustment)
            listing_elements = soup.find_all('div', class_='annonce') or soup.find_all('article')
            
            for element in listing_elements:
                try:
                    listing = self._parse_listing_element(element)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error parsing Carte Coloc listing: {e}")
                    continue
            
            logger.info(f"Scraped {len(listings)} listings from La Carte des Coloc")
            
        except Exception as e:
            logger.error(f"Error scraping La Carte des Coloc: {e}")
        
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
            link = element.find('a')
            if not link or not link.get('href'):
                return None
            
            url = link.get('href')
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"
            
            # Extract title
            title_elem = element.find('h2') or element.find('h3') or link
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract price
            price_elem = element.find(class_='prix') or element.find(class_='price')
            price_text = price_elem.get_text(strip=True) if price_elem else ''
            price = self._extract_price(price_text)
            
            # Extract location
            location_elem = element.find(class_='ville') or element.find(class_='location')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Extract description
            desc_elem = element.find('p') or element.find(class_='description')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Extract source ID from URL
            source_id = url.split('/')[-1] if url else ''
            
            return {
                'source_id': source_id,
                'source_url': url,
                'title': title,
                'price': price,
                'city': location,
                'description': description,
                'property_type': 'room',  # Colocation is typically rooms
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
            price_text: Price text (e.g., "500 €/mois")
            
        Returns:
            Price as float or None
        """
        try:
            # Remove common text and keep numbers
            price_clean = price_text.replace('€', '').replace('/mois', '').replace(' ', '').replace(',', '.')
            return float(price_clean)
        except (ValueError, AttributeError):
            return None

