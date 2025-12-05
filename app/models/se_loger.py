from app.enums.type_searching import TypeSearching


class SeLoger:
    def __init__(self, city_name: str, postal_code: str, type_searching: TypeSearching = TypeSearching.RENT):
        self.city_name = city_name
        self.postal_code = postal_code
        self.type_searching = type_searching