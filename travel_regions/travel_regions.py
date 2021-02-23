import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Union
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon
from fuzzysearch import find_near_matches
from haversine import haversine
from pycountry_convert import *
import os
from geovoronoi import coords_to_points

from ._map_features import Node, Region
from ._geometry import (
    classify_points,
    extract_geometries,
    generate_constrained_voronoi_diagram,
    merge_regions,
    detect_outliers_z_score,
    geometry_to_shapely,
)
from ._file_utils import get_communities, read_csv, read_geo_json

package_directory = os.path.dirname(os.path.abspath(__file__))


class TravelRegions:
    def __init__(
        self,
        *bounding_area_paths: List[str],
        region_model: str = None,
        levels: int = None,
        region_node_threshold: int = 10,
        z_score_threshold: int = 4,
    ):
        """
        A class representation of a region model

        Args:
            TODO region_model (str, optional): Path to a custom region model if one
                should be used instead of the default. See ____ for a reference of
                the expected file structure. Defaults to None.
            levels (int, optional): The number of hierarchical levels in the
                region model. Defaults to None.
            region_nodes_threshold (int): The minimum number of nodes a region
                needs to have to be included in the travel region model.
            z_score_threshold (int): Controls how far away nodes are allowed to
                be from the centers of their communities without being considered outliers.
        """
        self.nodes = {}
        self.regions = {}
        self.regions_serialized = {}

        #######################
        # Extract communities #
        #######################
        if region_model or bounding_area_paths:
            if region_model:
                assert (
                    levels is not None
                ), "The number of hierarchical levels in the region model must be provided"
            else:
                region_model = os.path.join(
                    Path(package_directory).parent,
                    "data",
                    "communities_-1__with_distance_multi-level_geonames_cities_7.csv",
                )
                levels = 4
            if not bounding_area_paths:
                bounding_area_paths = [
                    os.path.join("data", "cutouts", "eu_af_as_au.geojson"),
                    os.path.join("data", "cutouts", "americas.geojson"),
                    os.path.join("data", "cutouts", "nz.geojson"),
                ]
            print(
                "Initializing travel regions with custom parameters. This operation may take some time..."
            )

            data = read_csv(region_model)
            # Generate communities for hierarchical levels 1-4
            communities_by_level = {
                i: get_communities(data, i) for i in range(1, levels + 1)
            }
            self.regions_serialized = {}
            for level, communities in communities_by_level.items():
                community_IDs = list(communities.keys())

                #####################
                # Outlier detection #
                #####################
                outliers = []

                #####################
                # Generate polygons #
                #####################
                bounding_areas = []
                voronoi_clusters_by_bounding_area = []
                nonoutliers_by_community_combined = [
                    [] for _ in range(len(communities))
                ]
                for bounding_area_path in bounding_area_paths:
                    bounding_area = read_geo_json(bounding_area_path)
                    bounding_area = list(
                        map(
                            lambda point: [point[1], point[0]],
                            bounding_area["geometry"]["coordinates"][0],
                        )
                    )  # flipping coordinates for geovoronoi and Leaflet compatibility
                    bounding_areas.append(bounding_area)
                    bounding_area_shape = Polygon(bounding_area)

                    nonoutliers_by_community = []
                    for community in communities.values():
                        community_nodes = [point for point in community]
                        outliers_z_score = detect_outliers_z_score(
                            [
                                (float(node[-3]), float(node[-2]))
                                for node in community_nodes
                            ],
                            z_score_threshold,
                        )
                        if len(outliers_z_score) > 1:
                            outlier_indices, _ = zip(*outliers_z_score)
                        elif len(outliers_z_score) > 0:
                            outlier_indices = [outliers_z_score[0][0]]
                        else:
                            outlier_indices = []
                        nonoutliers_by_community += [
                            [
                                {"id": node[1][0], "latlng": [node[1][8], node[1][9]]}
                                for node in enumerate(community_nodes)
                                if node[0] not in outlier_indices
                                and coords_to_points(
                                    [[float(node[1][8]), float(node[1][9])]]
                                )[0].within(bounding_area_shape)
                            ]
                        ]

                        outliers.append(
                            [community_nodes[index] for index in outlier_indices]
                        )
                    for i in range(len(nonoutliers_by_community)):
                        nonoutliers_by_community_combined[
                            i
                        ] += nonoutliers_by_community[i]
                    nonoutliers = [
                        community_nonoutlier
                        for community_nonoutliers in nonoutliers_by_community
                        for community_nonoutlier in community_nonoutliers
                    ]  # ordered by community
                    nonoutliers_latlng = [
                        (float(nonoutlier["latlng"][0]), float(nonoutlier["latlng"][1]))
                        for nonoutlier in nonoutliers
                    ]
                    voronoi_clusters_by_bounding_area.append(
                        generate_constrained_voronoi_diagram(
                            nonoutliers_latlng,
                            bounding_area_shape,
                            nonoutliers_by_community,
                        )
                    )
                voronoi_clusters = []
                for i in range(len(community_IDs)):
                    voronoi_clusters.append([])
                    for j in range(len(voronoi_clusters_by_bounding_area)):
                        voronoi_clusters[-1] += (
                            voronoi_clusters_by_bounding_area[j][i]
                            if len(voronoi_clusters_by_bounding_area[j]) > i
                            else []
                        )
                merged_voronoi_clusters = merge_regions(
                    *voronoi_clusters
                )  # For each cluster, unifies the cluster's single-point voronoi regions into a single polygon
                region_geometries = extract_geometries(*merged_voronoi_clusters)

                # Generate region file JSON dump
                self.regions_serialized[level] = {
                    "level": level,
                    "community_IDs": community_IDs,
                    "bounding_area": bounding_areas,
                    "geometries": region_geometries,
                    "nodes": nonoutliers_by_community_combined,
                    "outliers": outliers,
                }
        else:
            for level in range(1, 5):
                path = os.path.join(
                    Path(package_directory).parent,
                    "data",
                    "region_files",
                    f"level_{level}_regions.json",
                )
                with open(path, "r") as f:
                    self.regions_serialized[level] = json.load(f)

        ################################
        # Load nodes from region model #
        ################################

        data = read_csv(
            region_model
            if region_model
            else os.path.join(
                Path(package_directory).parent,
                "data",
                "communities_-1__with_distance_multi-level_geonames_cities_7.csv",
            )
        )
        self.nodes = {}
        for i, row in enumerate(data):
            if i == 0:
                continue  # skip first row (headers)
            self.nodes[row[0]] = Node(
                row[0], row[-1], (float(row[-3]), float(row[-2])), row[-4],
            )

        #######################
        # Instantiate regions #
        #######################
        for level, regions_dump in self.regions_serialized.items():
            regions = []
            hierarchical_level = regions_dump["level"]
            community_IDs = regions_dump["community_IDs"]
            geometries = regions_dump["geometries"]
            region_nodes_serialized = regions_dump["nodes"]
            for i in range(len(geometries)):
                if geometries[i]:
                    region_nodes = []
                    for region_node_serialized in region_nodes_serialized[i]:
                        region_nodes.append(self.nodes[region_node_serialized["id"]])
                    if len(region_nodes) >= region_node_threshold:
                        regions.append(
                            Region(
                                hierarchical_level,
                                community_IDs[i],
                                geometries[i],
                                region_nodes,
                            )
                        )
            self.regions[level] = regions
        if region_model:
            print("Initialization complete!")

    def export_regions(self, level: int, path: str, regions_ids: List[int] = []):
        """
        Generates a region file for the specified hierarchical level

        Args:
            level (int): Hierarchical level for which the region file is to be generated
            path (str): Target location in the file system where the region file
                is to be saved (must include filename). For example,
                ``path/to/file/my_l2_regions.json``
            region_ids (List[int], optional): An optional list of region IDs if
                only select regions are to be exported. Defaults to [].
        """
        with open(path, "w") as f:
            if regions_ids:
                regions_serialized = {
                    "level": level,
                    "community_IDs": [],
                    "bounding_area": [],
                    "geometries": [],
                    "nodes": [],
                    "outliers": [],
                }
                for region_id in regions_ids:
                    region = self.get_region(str(region_id))
                    regions_serialized["geometries"].append(region.geometry)
                    regions_serialized["community_IDs"].append(region.community_id)
                    regions_serialized["nodes"].append(
                        [{"latlng": node.latlng} for node in region.nodes]
                    )
                json.dump(regions_serialized, f, indent=4)
            else:
                json.dump(self.regions_serialized[level], f, indent=4)

    def get_region(self, id: str) -> Region:
        """
        Returns the region with the given ``id``

        Args:
            id (str): Region ID

        Returns:
            Region: Region with matching ID
        """
        for level_regions in self.regions.values():
            for region in level_regions:
                if region.id == id:
                    return region
        print(f"No region with id {id}")
        return None

    def get_country_regions(
        self, country: str, level: int, include_multipolygons: bool = True
    ) -> List[str]:
        matching_regions = [
            node.regions[level].id
            for node in self.nodes.values()
            if node.country == str.upper(country)
            and level in node.regions
            and (
                include_multipolygons
                or node.regions[level].geometry["type"] == "polygon"
            )
        ]
        if matching_regions:
            return matching_regions
        print("No matching country regions found!")

    def get_node(self, id: str) -> Node:
        """
        Returns the node with the given ``id``

        Args:
            id (str): Node ID

        Returns:
            Node: Node with matching ID
        """
        try:
            node = self.nodes[id]
            return node
        except KeyError as key:
            print(f"No node with id {key}")
            return None

    def find_region(self, countries: List[str]) -> List[Region]:
        """
        Finds all regions that overlap with the countries provided, where
        overlap is defined as the country having at least one node contained
        within the region. See :func:`~region.get_countries()` for more.

        Args:
            countries (List[str]): Countries of interest

        Returns:
            List[Region]: Regions that overlap with the given countries
        """
        # TODO Make search able to work with a wider range of terms: cities,
        # landmarks, etc.
        candidates = set()
        for level_regions in self.regions.values():
            for region in level_regions:
                hits = 0
                for country in countries:
                    for region_country in region.countries:
                        matches = find_near_matches(
                            country, region_country, max_l_dist=1
                        )
                        if matches:
                            hits += 1
                            break
                if hits == len(countries):
                    candidates.add(region)
        return list(candidates)

    def find_node(self, name: str) -> List[Node]:
        """
        Searches for a node by name and returns all approximate matches

        Args:
            name (str): Location name

        Returns:
            List[Node]: All nodes whose names fulfill the matching criteria
        """
        hits = []
        for node in self.nodes.values():
            matches = find_near_matches(name, node.name, max_l_dist=1)
            if matches:
                hits.append(node)
        return hits

    def get_continent_regions(self, continent: str) -> List[Region]:
        """
        Returns regions with at least one node in the specified continent

        Args:
            continent (str): One of SA, NA, EU, AS, AF, OC, or AN

        Returns:
            List[Region]: Regions with at least one node in the given continent
        """
        continent_regions = set()
        for level_regions in self.regions.values():
            for region in level_regions:
                for country in region.countries:
                    country = country_name_to_country_alpha2(
                        country, cn_name_format="default"
                    )
                    try:
                        country_continent = country_alpha2_to_continent_code(country)
                        # DEBUG Remove nested try/except and add a continue here
                        # Nested try/except was only added for development to see which country codes need to be handled
                    except KeyError:
                        try:
                            country_continent = {"EH": "AF", "VA": "EU", "PN": "OC"}[
                                country
                            ]
                        except KeyError as key:
                            print(
                                f"Country code {key} found neither in pycountry_convert nor in custom dict!"
                            )
                            continue
                    if country_continent == continent:
                        continent_regions.add(region)
        return list(continent_regions)

    def get_nearest_node(self, point: Tuple[float, float]) -> Node:
        """
        Uses Haversine distance to return the nearest known node to ``point``
        whose coordinates aren't identical to it.

        Args:
            point (Tuple[float, float]): The coordinates of the point whose
                nearest node is to be found

        Returns:
            Node: The closest, non-identical node to point
        """
        nodes = [
            node for node in self.nodes.values() if node.latlng != point
        ]  # extract all nodes
        distances = [haversine(point, node.latlng) for node in nodes]
        nearest_node = nodes[distances.index(min(distances))]
        return nearest_node

    def points_to_regions(
        self, points: List[Tuple[float, float]]
    ) -> Dict[str, List[Tuple[float, float]]]:
        """
        Maps ``points`` to the regions that contain them

        Args:
            points (List[Tuple[float, float]]): The points of interest

        Returns:
            Dict[str, List[Tuple[float, float]]]: A mapping from region IDs to
                points. A point may be mapped to multiple regions if regions from
                multiple hierarchical levels were used.
        """
        regions = []
        for level_regions in self.regions.values():
            regions += [region for region in level_regions]

        region_geometries = [
            Polygon(region.geometry["geometry"])
            if region.geometry["type"] == "polygon"
            else MultiPolygon(
                [Polygon(geometry) for geometry in region.geometry["geometry"]]
            )
            for region in regions
        ]  # convert region geometries to Shapely polygons
        classifications = classify_points(points, region_geometries)
        return {regions[index].id: points for index, points in classifications.items()}

    def compare_overlap(
        self,
        level: int,
        area: Union[Polygon, MultiPolygon],
        overlap_threshold: int = 10,
    ) -> Dict[str, Tuple[float, float]]:
        """
        Finds the travel regions that overlap with a given area as well as the
        degrees to which they overlap as a percentage of each travel
        region's area
        and as a percentage of the target area itself.

        Args: 
            level (int): The hierarchical level at which to search for
                overlapping travel regions 
            area (Union[Polygon, MultiPolygon]): A
                Shapely Polygon or MultiPolygon describing the area's geometry

        Returns: Dict[str, tuple[float, float]]: A dict that maps IDs of regions
            overlapping with the given area to a tuple whose first element is the
            intersection of the two as a percentage of the region and whose second
            element is the intersection as a percentage of the area.
        """
        overlapping_regions = {}
        for region in self.regions[level]:
            region_geom = geometry_to_shapely(
                region.geometry
            )  # Convert geometry to Shapely Polygons/MultiPolygons
            intersection_as_region_percentage = (
                region_geom.intersection(area).area / region_geom.area
            ) * 100
            intersection_as_area_percentage = (
                area.intersection(region_geom).area / area.area
            ) * 100
            if intersection_as_area_percentage >= overlap_threshold:
                overlapping_regions[region.id] = (
                    intersection_as_region_percentage,
                    intersection_as_area_percentage,
                )
        return overlapping_regions
