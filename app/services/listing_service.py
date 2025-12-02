"""
Service for managing listings in the database.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from loguru import logger
from app.models import Listing
from app.database import SessionLocal


class ListingService:
    """
    Service for CRUD operations on listings.
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the listing service.
        
        Args:
            db: Optional database session (creates new one if not provided)
        """
        self.db = db or SessionLocal()
    
    def save_listing(self, listing_data: dict) -> Optional[Listing]:
        """
        Save or update a listing in the database.
        
        Args:
            listing_data: Listing dictionary
            
        Returns:
            Saved Listing object or None
        """
        try:
            # Check if listing already exists
            existing = self.db.query(Listing).filter(
                and_(
                    Listing.source == listing_data['source'],
                    Listing.source_id == listing_data['source_id']
                )
            ).first()
            
            if existing:
                # Update existing listing
                for key, value in listing_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                logger.debug(f"Updated listing: {existing.id}")
            else:
                # Create new listing
                existing = Listing(**listing_data)
                self.db.add(existing)
                logger.debug(f"Created new listing: {listing_data.get('title', '')[:50]}")
            
            self.db.commit()
            self.db.refresh(existing)
            return existing
            
        except Exception as e:
            logger.error(f"Error saving listing: {e}")
            self.db.rollback()
            return None
    
    def save_listings(self, listings: List[dict]) -> int:
        """
        Save multiple listings.
        
        Args:
            listings: List of listing dictionaries
            
        Returns:
            Number of listings saved
        """
        saved_count = 0
        for listing_data in listings:
            if self.save_listing(listing_data):
                saved_count += 1
        
        logger.info(f"Saved {saved_count}/{len(listings)} listings")
        return saved_count
    
    def get_listing(self, listing_id: int) -> Optional[Listing]:
        """
        Get a listing by ID.
        
        Args:
            listing_id: Listing ID
            
        Returns:
            Listing object or None
        """
        return self.db.query(Listing).filter(Listing.id == listing_id).first()
    
    def get_listings_by_source(self, source: str, limit: int = 100) -> List[Listing]:
        """
        Get listings by source.
        
        Args:
            source: Source name
            limit: Maximum number of listings to return
            
        Returns:
            List of Listing objects
        """
        return self.db.query(Listing).filter(
            Listing.source == source
        ).order_by(Listing.last_updated.desc()).limit(limit).all()
    
    def get_active_listings(self, limit: int = 100) -> List[Listing]:
        """
        Get active listings.
        
        Args:
            limit: Maximum number of listings to return
            
        Returns:
            List of active Listing objects
        """
        return self.db.query(Listing).filter(
            Listing.is_active == True
        ).order_by(Listing.last_updated.desc()).limit(limit).all()
    
    def deactivate_old_listings(self, source: str, days: int = 7) -> int:
        """
        Deactivate listings that haven't been updated in a while.
        
        Args:
            source: Source name
            days: Number of days since last update
            
        Returns:
            Number of listings deactivated
        """
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        count = self.db.query(Listing).filter(
            and_(
                Listing.source == source,
                Listing.is_active == True,
                Listing.last_updated < cutoff_date
            )
        ).update({'is_active': False})
        
        self.db.commit()
        logger.info(f"Deactivated {count} old listings from {source}")
        return count
    
    def close(self):
        """Close the database session."""
        if self.db:
            self.db.close()

