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
        regions.remove(self)
        neighboring_regions = set()
        if self.geometry["type"] == "polygon":
            ego_region_polygon = Polygon(self.geometry["geometry"])
            for candidate_region in regions:
                if candidate_region.geometry["type"] == "polygon":
                    candidate_region_polygon = Polygon(
                        candidate_region.geometry["geometry"]
                    )
                    if ego_region_polygon.touches(candidate_region_polygon):
                        neighboring_regions.add(candidate_region)
                elif candidate_region.geometry["type"] == "multipolygon":
                    for region_polygon in [
                        Polygon(geometry)
                        for geometry in candidate_region.geometry["geometry"]
                    ]:
                        if ego_region_polygon.touches(region_polygon):
                            neighboring_regions.add(candidate_region)
        elif self.geometry["type"] == "multipolygon":
            for ego_region_polygon in [
                Polygon(geometry) for geometry in self.geometry["geometry"]
            ]:
                for candidate_region in regions:
                    if candidate_region.geometry["type"] == "polygon":
                        candidate_region_polygon = Polygon(
                            candidate_region.geometry["geometry"]
                        )
                        if ego_region_polygon.touches(candidate_region_polygon):
                            neighboring_regions.add(candidate_region)
                    else:
                        for region_polygon in [
                            Polygon(geometry)
                            for geometry in candidate_region.geometry["geometry"]
                        ]:
                            if ego_region_polygon.touches(region_polygon):
                                neighboring_regions.add(candidate_region)
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
