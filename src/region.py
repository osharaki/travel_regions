from functools import reduce
from typing import *

from shapely import geometry
from node import Node


class Region:
    def __init__(
        self, level: int, geometry: List[Tuple[float, float]], nodes: List[Node],
    ):
        self.name = self.generate_name()
        self.level = level
        self.geometry = geometry
        self.id = self.generate_id()
        self.nodes = nodes
        for node in nodes:
            node.regions[level] = self

    def get_countries(self, threshold: int = 1) -> Set["Region"]:
        # TODO implement get_countries
        pass

    def get_neighbors(self) -> Set["Region"]:
        # TODO implement get_neighbours
        pass

    def generate_id(self):
        # Performs deterministic region id generation.
        # 1. Adds up the x coorinates of all points in the region's geometry
        # 2. Gets the absolute value of the result
        # 3. Converts that to int
        # 4. Modulo to stay within reasonable id length
        geometry_points = []
        if self.geometry["type"] == "polygon":
            geometry_points += list(zip(*self.geometry["geometry"]))[0]
        else:
            for geometry in self.geometry["geometry"]:
                geometry_points += list(zip(*geometry))[0]
        return int(abs(sum(geometry_points))) % 99999

    def generate_name(self):
        # TODO performs deterministic region name generation
        pass
