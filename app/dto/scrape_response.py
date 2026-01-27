from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class PropertyDTO(BaseModel):
    """
    DTO for property information
    """
    rooms: Optional[int] = Field(None, description="Number of rooms")
    price: Optional[float] = Field(None, description="Monthly rent amount")
    charges_included: Optional[bool] = Field(False, description="Whether charges are included")
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    url: Optional[str] = Field(None, description="Property URL")
    title: Optional[str] = Field(None, description="Property title")
    postal_code: Optional[str] = Field(None, description="Postal code")
    
    # Common fields
    id: Optional[str] = Field(None, description="Property ID")
    space: Optional[float] = Field(None, description="Surface area in m²")
    city: Optional[str] = Field(None, description="City name")
    address: Optional[str] = Field(None, description="Property address")
    property_type: Optional[str] = Field(None, description="Type of property (studio, apartment, room, etc.)")
    
    # SeLoger specific fields
    type_searching: Optional[str] = Field(None, description="Type of search (Buy/Rent)")
    baths: Optional[int] = Field(None, description="Number of bathrooms")
    floors: Optional[Dict[str, Optional[int]]] = Field(None, description="Floor information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rooms": 2,
                "price": 800.0,
                "charges_included": True,
                "images": ["https://example.com/image.jpg"],
                "url": "https://example.com/property",
                "title": "Beautiful apartment",
                "postal_code": "75001"
            }
        }


class ScrapeResponseDTO(BaseModel):
    """
    DTO for scrape API response
    """
    status: str = Field(..., description="Status of the request (success or error)")
    platform: Optional[str] = Field(None, description="Platform used for scraping")
    count: int = Field(0, description="Number of properties found")
    results: List[PropertyDTO] = Field(default_factory=list, description="List of properties")
    message: Optional[str] = Field(None, description="Error message if status is error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "platform": "SeLoger",
                "count": 10,
                "results": [
                    {
                        "rooms": 2,
                        "price": 800.0,
                        "charges_included": True,
                        "images": [],
                        "url": "https://example.com/property",
                        "title": "Beautiful apartment",
                        "postal_code": "75001"
                    }
                ]
            }
        }

