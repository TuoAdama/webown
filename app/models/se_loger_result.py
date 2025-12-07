from typing import Optional

from app.enums.type_searching import TypeSearching


class SeLogerResult:
    def __init__(self):
        self.price: Optional[float] = None
        self.space: Optional[int] = None
        self.type_searching = TypeSearching.RENT.value
        self.link: Optional[str] = None
        self.images: list[str] = []