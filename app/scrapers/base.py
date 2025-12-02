"""
Base scraper class that all scrapers should inherit from.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger
from app.config import settings


class BaseScraper(ABC):
    """
    Base class for all scrapers.
    Provides common functionality like HTTP requests, retries, etc.
    """
    
    def __init__(self, source_name: str):
        """
        Initialize the base scraper.
        
        Args:
            source_name: Name of the source (e.g., 'leboncoin', 'seloger')
        """
        self.source_name = source_name
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy.
        """
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=settings.RETRY_ATTEMPTS,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        return session
    
    def fetch_page(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Fetch a web page with error handling.
        
        Args:
            url: URL to fetch
            params: Optional query parameters
            
        Returns:
            Response object or None if failed
        """
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=settings.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    @abstractmethod
    def scrape_listings(self, search_params: Optional[Dict] = None) -> List[Dict]:
        """
        Scrape listings from the source.
        
        Args:
            search_params: Optional search parameters (location, price range, etc.)
            
        Returns:
            List of listing dictionaries
        """
        pass
    
    @abstractmethod
    def parse_listing(self, listing_data: Dict) -> Dict:
        """
        Parse a single listing from raw data.
        
        Args:
            listing_data: Raw listing data
            
        Returns:
            Parsed listing dictionary with standardized fields
        """
        pass
    
    def normalize_listing(self, listing: Dict) -> Dict:
        """
        Normalize a listing to ensure all required fields are present.
        
        Args:
            listing: Listing dictionary
            
        Returns:
            Normalized listing dictionary
        """
        return {
            'source': self.source_name,
            'source_id': listing.get('source_id', ''),
            'source_url': listing.get('source_url', ''),
            'title': listing.get('title', ''),
            'description': listing.get('description', ''),
            'price': listing.get('price'),
            'surface': listing.get('surface'),
            'rooms': listing.get('rooms'),
            'bedrooms': listing.get('bedrooms'),
            'city': listing.get('city'),
            'postal_code': listing.get('postal_code'),
            'address': listing.get('address'),
            'latitude': listing.get('latitude'),
            'longitude': listing.get('longitude'),
            'property_type': listing.get('property_type'),
            'energy_class': listing.get('energy_class'),
            'furnished': listing.get('furnished', False),
            'images': listing.get('images', '[]'),
        }

