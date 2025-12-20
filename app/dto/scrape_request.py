from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.enums.platform import Platform


class ScrapeRequestDTO(BaseModel):
    """
    DTO for scrape request parameters
    """
    ville: str = Field(..., description="City name", min_length=1)
    code_postal: Optional[str] = Field(None, description="Postal code")
    prix_max: Optional[float] = Field(None, description="Maximum price", gt=0)
    plateforme: str = Field(..., description="Platform name (SeLoger or Espacil)")
    surface_min: Optional[float] = Field(None, description="Minimum surface area in m²", gt=0)
    
    @field_validator('plateforme')
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """Validate that platform is one of the supported platforms"""
        try:
            Platform[v.upper()]
        except KeyError:
            raise ValueError(f"Invalid platform. Supported platforms: {[p.value for p in Platform]}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "ville": "Paris",
                "code_postal": "75001",
                "prix_max": 1000.0,
                "plateforme": "SeLoger",
                "surface_min": 30.0
            }
        }

