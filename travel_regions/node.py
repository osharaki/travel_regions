from typing import *


class Node:
    def __init__(
        self, id: str, name: str, latlng: Tuple[float, float], country: str,
    ):
        from region import Region

        self.id = id
        self.name = name
        self.latlng = latlng
        self.country = country
        self.regions: Dict[int, Region] = {}
