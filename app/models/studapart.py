from typing import Optional, List


class Studapart:
    """
    Model for Studapart search parameters.
    """
    def __init__(self, city_name: str):
        self.city_name = city_name
        self.price_min: int = 1
        self.price_max: int = 3500
        self.available_from: Optional[str] = None  # Format: YYYY-MM-DD
        self.available_to: Optional[str] = None  # Format: YYYY-MM-DD
        self.property_types: Optional[List[str]] = None  # e.g. ["studio", "apartment", "room"]
        self.page: int = 1
        self.per_page: int = 20
    
    def set_price_range(self, min_price: int, max_price: int):
        """Set price range for the search."""
        self.price_min = min_price
        self.price_max = max_price
    
    def set_availability(self, available_from: str, available_to: Optional[str] = None):
        """Set availability dates for the search."""
        self.available_from = available_from
        self.available_to = available_to
    
    def set_property_types(self, types: List[str]):
        """Set property types to filter."""
        self.property_types = types
    
    def set_pagination(self, page: int, per_page: int = 20):
        """Set pagination parameters."""
        self.page = page
        self.per_page = per_page
