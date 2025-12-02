"""
Scraper manager to coordinate all scrapers.
"""
from typing import List, Dict, Optional
from loguru import logger
from app.scrapers.leboncoin import LeboncoinScraper
from app.scrapers.seloger import SeLogerScraper
from app.scrapers.carte_coloc import CarteColocScraper
from app.scrapers.base import BaseScraper


class ScraperManager:
    """
    Manages all scrapers and coordinates scraping operations.
    """
    
    def __init__(self):
        """Initialize scraper manager with all available scrapers."""
        self.scrapers: Dict[str, BaseScraper] = {
            'leboncoin': LeboncoinScraper(),
            'seloger': SeLogerScraper(),
            'carte_coloc': CarteColocScraper(),
        }
    
    def get_scraper(self, source: str) -> Optional[BaseScraper]:
        """
        Get a scraper by source name.
        
        Args:
            source: Source name (e.g., 'leboncoin')
            
        Returns:
            Scraper instance or None
        """
        return self.scrapers.get(source)
    
    def scrape_all(self, search_params: Optional[Dict] = None) -> List[Dict]:
        """
        Scrape all sources.
        
        Args:
            search_params: Optional search parameters
            
        Returns:
            List of all listings from all sources
        """
        all_listings = []
        
        for source_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping {source_name}...")
                listings = scraper.scrape_listings(search_params)
                
                # Normalize listings
                normalized = [scraper.normalize_listing(listing) for listing in listings]
                all_listings.extend(normalized)
                
                logger.info(f"Found {len(listings)} listings from {source_name}")
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                continue
        
        return all_listings
    
    def scrape_source(self, source: str, search_params: Optional[Dict] = None) -> List[Dict]:
        """
        Scrape a specific source.
        
        Args:
            source: Source name
            search_params: Optional search parameters
            
        Returns:
            List of listings from the source
        """
        scraper = self.get_scraper(source)
        if not scraper:
            logger.error(f"Unknown source: {source}")
            return []
        
        try:
            listings = scraper.scrape_listings(search_params)
            return [scraper.normalize_listing(listing) for listing in listings]
        except Exception as e:
            logger.error(f"Error scraping {source}: {e}")
            return []

