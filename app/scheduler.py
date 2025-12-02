"""
Scheduler for running scraping tasks periodically.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from app.config import settings
from app.scrapers.manager import ScraperManager
from app.services.listing_service import ListingService


class ScrapingScheduler:
    """
    Scheduler for periodic scraping tasks.
    """
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BlockingScheduler()
        self.scraper_manager = ScraperManager()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs for each scraper."""
        if not settings.SCHEDULER_ENABLED:
            logger.info("Scheduler is disabled in configuration")
            return
        
        # Leboncoin job
        self.scheduler.add_job(
            self._scrape_leboncoin,
            trigger=IntervalTrigger(minutes=settings.LEBONCOIN_INTERVAL_MINUTES),
            id='scrape_leboncoin',
            name='Scrape Leboncoin',
            replace_existing=True
        )
        
        # SeLoger job
        self.scheduler.add_job(
            self._scrape_seloger,
            trigger=IntervalTrigger(minutes=settings.SELOGER_INTERVAL_MINUTES),
            id='scrape_seloger',
            name='Scrape SeLoger',
            replace_existing=True
        )
        
        # La Carte des Coloc job
        self.scheduler.add_job(
            self._scrape_carte_coloc,
            trigger=IntervalTrigger(minutes=settings.CARTE_COLOC_INTERVAL_MINUTES),
            id='scrape_carte_coloc',
            name='Scrape La Carte des Coloc',
            replace_existing=True
        )
        
        logger.info("Scheduled jobs configured")
    
    def _scrape_leboncoin(self):
        """Scrape Leboncoin listings."""
        logger.info("Starting Leboncoin scraping job...")
        try:
            scraper = self.scraper_manager.get_scraper('leboncoin')
            if scraper:
                listings = scraper.scrape_listings()
                service = ListingService()
                service.save_listings(listings)
                service.close()
                logger.info(f"Leboncoin scraping job completed: {len(listings)} listings")
        except Exception as e:
            logger.error(f"Error in Leboncoin scraping job: {e}")
    
    def _scrape_seloger(self):
        """Scrape SeLoger listings."""
        logger.info("Starting SeLoger scraping job...")
        try:
            scraper = self.scraper_manager.get_scraper('seloger')
            if scraper:
                listings = scraper.scrape_listings()
                service = ListingService()
                service.save_listings(listings)
                service.close()
                logger.info(f"SeLoger scraping job completed: {len(listings)} listings")
        except Exception as e:
            logger.error(f"Error in SeLoger scraping job: {e}")
    
    def _scrape_carte_coloc(self):
        """Scrape La Carte des Coloc listings."""
        logger.info("Starting La Carte des Coloc scraping job...")
        try:
            scraper = self.scraper_manager.get_scraper('carte_coloc')
            if scraper:
                listings = scraper.scrape_listings()
                service = ListingService()
                service.save_listings(listings)
                service.close()
                logger.info(f"La Carte des Coloc scraping job completed: {len(listings)} listings")
        except Exception as e:
            logger.error(f"Error in La Carte des Coloc scraping job: {e}")
    
    def start(self):
        """Start the scheduler."""
        logger.info("Starting scheduler...")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped")
            self.scheduler.shutdown()
    
    def run_once(self, source: str = None):
        """
        Run scraping once for a specific source or all sources.
        
        Args:
            source: Optional source name (if None, scrapes all)
        """
        if source:
            logger.info(f"Running one-time scrape for {source}...")
            scraper = self.scraper_manager.get_scraper(source)
            if scraper:
                listings = scraper.scrape_listings()
                service = ListingService()
                service.save_listings(listings)
                service.close()
                logger.info(f"One-time scrape completed: {len(listings)} listings")
        else:
            logger.info("Running one-time scrape for all sources...")
            listings = self.scraper_manager.scrape_all()
            service = ListingService()
            service.save_listings(listings)
            service.close()
            logger.info(f"One-time scrape completed: {len(listings)} listings")

