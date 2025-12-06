from typing import Optional

from app.enums.type_searching import TypeSearching


class SeLoger:
    def __init__(self, city_name: str, type_searching: TypeSearching = TypeSearching.RENT):
        self.city_name = city_name
        self.postal_code = None
        self.type_searching = type_searching
        self.min_price = None
        self.max_price = None
        self.number_of_rooms_min = None
        self.number_of_rooms_max = None
        self.space_min = None
        self.space_max = None

    def set_postal_code(self, postal_code):
        self.postal_code = postal_code

    def set_min_price(self, min_price: float):
        self.min_price = min_price

    def set_max_price(self, max_price: float):
        self.max_price = max_price

    def set_number_of_rooms(self, number_of_rooms_min: int):
        self.number_of_rooms_min = number_of_rooms_min

    def set_space_min(self, space_min: float):
        self.space_min = space_min

    def set_space_max(self, space_max: float):
        self.space_max = space_max