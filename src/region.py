from typing import *

from shapely import geometry
from node import Node


class Region:
    def __init__(
        self, level: int, geometry: List[Tuple[float, float]], nodes: List[Node],
    ):
        self.id = self.generate_id()
        self.name = self.generate_name()
        self.level = level
        self.geometry = geometry
        # TODO assign self to nodes at `level`: node.regions[level] = self
        self.nodes = nodes

    def get_countries(self, threshold: int = 1) -> Set["Region"]:
        # TODO implement get_countries
        pass

    def get_neighbours(self) -> Set["Region"]:
        # TODO implement get_neighbours
        pass

    def generate_id(self):
        # TODO performs deterministic region id generation
        pass

    def generate_name(self):
        # TODO performs deterministic region name generation
        pass
