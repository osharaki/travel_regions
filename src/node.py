from typing import *

from region import Region


class Node:
    def __init__(
        self,
        id: str,
        name: str,
        latlng: Tuple[float, float],
        country: str,
        regions: Dict[int, Region],
    ):
        self.id = id
        self.name = name
        self.latlng = (latlng,)
        self.country = (country,)
        self.regions = regions
