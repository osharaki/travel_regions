from typing import *

from shapely.geometry import Polygon

from collections import Counter

import pycountry


class Node:
    def __init__(
        self, id: str, name: str, latlng: Tuple[float, float], country: str,
    ):
        self.id = id
        self.name = name
        self.latlng = latlng
        self.country = country
        self.regions: Dict[int, Region] = {}


class Region:
    def __init__(
        self,
        level: int,
        community_id: int,
        geometry: List[Tuple[float, float]],
        nodes: List[Node],
    ):
        self.level = level
        self.community_id = community_id
        self.geometry = geometry
        self.id = self.generate_id()
        self.nodes = nodes
        for node in nodes:
            node.regions[level] = self
        self.countries = list(self.get_countries().keys())

    def get_countries(self, threshold: int = 1) -> Dict[str, int]:
        """
        Returns countries with a minimum number of cities contained within the
        region

        Args: threshold (int, optional): The minimum number of a country's
            cities located within the region in order for the country to be
            included. Defaults to 1.

        Returns: Dict[str, int]: The countries fulfilling the threshold along
            with how many of their cities are in the region
        """
        countries = []
        for node in self.nodes:
            country = pycountry.countries.get(alpha_2=f"{node.country}")
            if country != None:
                countries.append(country.name)
        country_counts = Counter(countries)
        country_counts = list(
            filter(
                lambda country_count: country_count[1] >= threshold,
                country_counts.items(),
            )
        )
        country_counts = {
            country_count[0]: country_count[1] for country_count in country_counts
        }
        return country_counts

    # FIXME requiring a list of regions to be passed is awkward. Do away with
    # this need by finding a way, from inside Region.get_neighbors(), to access all regions in the TravelRegion
    # instance that are on this region's level.
    def get_neighbors(self, regions: List["Region"]) -> Set["Region"]:
        """
        Returns all regions whose geometries share at least one point with the calling region. This applies to both single and multi-polygon regions. For example, a multi-polygon region is considered another region's neighbor even if only one of its polygons shares at least one geometry point with that region.

        Args:
            regions (List[Region]): List of regions to check for neighbor-status. Typically all regions in a hierarchical level

        Returns:
            Set[Region]: All regions whose geometries share at least one point with the calling region
        """
        regions = list(regions)
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

