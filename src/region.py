from functools import reduce
from typing import *

from shapely import geometry
from shapely.geometry import Polygon
from shapely.geometry.multipolygon import MultiPolygon
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

    def get_neighbors(self, regions: List["Region"]) -> Set["Region"]:
        # TODO Improve code quality
        regions.remove(self)
        neighboring_regions = set()
        if self.geometry["type"] == "polygon":
            polygon = Polygon(self.geometry["geometry"])
            for region in regions:
                if region.geometry["type"] == "polygon":
                    region_polygon = Polygon(region.geometry["geometry"])
                    if polygon.touches(region_polygon):
                        neighboring_regions.add(region)
                else:
                    for region_polygon in [
                        Polygon(geometry) for geometry in region.geometry["geometry"]
                    ]:
                        if polygon.touches(region_polygon):
                            neighboring_regions.add(region)
        else:
            for polygon in [
                Polygon(geometry) for geometry in self.geometry["geometry"]
            ]:
                for region in regions:
                    if region.geometry["type"] == "polygon":
                        region_polygon = Polygon(region.geometry["geometry"])
                        if polygon.touches(region_polygon):
                            neighboring_regions.add(region)
                    else:
                        for region_polygon in [
                            Polygon(geometry)
                            for geometry in region.geometry["geometry"]
                        ]:
                            if polygon.touches(region_polygon):
                                neighboring_regions.add(region)
        return neighboring_regions

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
