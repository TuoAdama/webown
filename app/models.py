"""
Database models for housing listings.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.sql import func
from app.database import Base


class Listing(Base):
    """
    Model representing a housing listing from various sources.
    """
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # leboncoin, seloger, carte_coloc, etc.
    source_id = Column(String(255), nullable=False)  # Original ID from the source
    source_url = Column(Text, nullable=False)
    
    # Listing details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(Float)
    surface = Column(Float)  # Surface area in m²
    rooms = Column(Integer)  # Number of rooms
    bedrooms = Column(Integer)  # Number of bedrooms
    
    # Location
    city = Column(String(100))
    postal_code = Column(String(10))
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Additional details
    property_type = Column(String(100))  # apartment, house, room, etc.
    energy_class = Column(String(10))
    furnished = Column(Boolean, default=False)
    
    # Images
    images = Column(Text)  # JSON array of image URLs
    
    # Metadata
    is_active = Column(Boolean, default=True)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Unique constraint on source and source_id
    __table_args__ = (
        Index('idx_source_source_id', 'source', 'source_id', unique=True),
    )
    
    def __repr__(self):
        return f"<Listing(id={self.id}, source={self.source}, title={self.title[:50]}...)>"

