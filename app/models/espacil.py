from typing import Optional
from app.enums.type_house_space import TypeHouseSpace

class Espacil:
    def __init__(self, city_name: str):
        self.city_name = city_name
        self.type_house_space: Optional[TypeHouseSpace] = None
        self.price_max: int = 1_000