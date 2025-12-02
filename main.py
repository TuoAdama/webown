"""
Main entry point for the Webown scraping application.
"""
import sys
import time
from loguru import logger
from app.config import settings
from app.database import init_db
from app.scheduler import ScrapingScheduler


def setup_logging():
    """Configure logging."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL
    )
    logger.add(
        "logs/webown_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=settings.LOG_LEVEL
    )


def wait_for_db():
    """Wait for database to be ready."""
    from sqlalchemy import create_engine, text
    from app.config import settings
    
    max_retries = 30
    retry_count = 0
    
    database_url = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    
    while retry_count < max_retries:
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
            return True
        except Exception as e:
            retry_count += 1
            logger.warning(f"Waiting for database... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    logger.error("Failed to connect to database")
    return False


def main():
    """Main function."""
    setup_logging()
    logger.info("Starting Webown scraping application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Wait for database
    if not wait_for_db():
        sys.exit(1)
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)
    
    # Create and start scheduler
    scheduler = ScrapingScheduler()
    
    # Run initial scrape
    logger.info("Running initial scrape...")
    scheduler.run_once()
    
    # Start scheduler if enabled
    if settings.SCHEDULER_ENABLED:
        logger.info("Starting scheduler...")
        scheduler.start()
    else:
        logger.info("Scheduler is disabled. Exiting after initial scrape.")


if __name__ == "__main__":
    main()

