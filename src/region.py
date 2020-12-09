from functools import reduce
from typing import *

from shapely import geometry
from node import Node


class Region:
    def __init__(
        self,
        level: int,
        community_id: int,
        geometry: List[Tuple[float, float]],
        nodes: List[Node],
    ):
        self.name = self.generate_name()
        self.level = level
        self.community_id = community_id
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

    def get_parent(self) -> "Region":
        # TODO finds this region's parent
        pass

    def get_children(self) -> Set["Region"]:
        # TODO finds the regions on the next level down that are "contained" within this region
        pass

    def generate_id(self) -> str:
        return f"{self.level}{self.community_id}"

    def generate_name(self):
        # TODO performs deterministic region name generation
        pass
