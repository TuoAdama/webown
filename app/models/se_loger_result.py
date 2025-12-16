from typing import Optional

from app.enums.type_searching import TypeSearching


class SeLogerResult:
    def __init__(self):
        self.id: Optional[str] = None
        self.price: Optional[float] = None
        self.space: Optional[float] = None
        self.type_searching = TypeSearching.RENT.value
        self.link: Optional[str] = None
        self.images: list[str] = []
        self.baths: Optional[int] = None
        self.floors: Optional[dict] = {
            "floor": None,
            "total": None,
        }
