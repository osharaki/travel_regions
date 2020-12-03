from typing import *

from shapely import geometry
from node import Node


class Region:
    def __init__(
        self,
        id: str,
        name: str,
        level: int,
        geometry: List[Tuple[float, float]],
        nodes: List[Node],
    ):
        self.id = id
        self.name = name
        self.level = level
        self.geometry = geometry
        self.nodes = nodes

    def get_countries(self, threshold: int = 1) -> Set["Region"]:
        # TODO implement get_countries
        pass

    def get_neighbours(self) -> Set["Region"]:
        # TODO implement get_neighbours
        pass
