import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon
from fuzzysearch import find_near_matches

from node import Node
from outliers import detect_outliers_z_score
from polygons import (
    classify_points,
    extract_geometries,
    generate_constrained_voronoi_diagram,
    merge_regions,
)
from region import Region
from utils.file_utils import cluster_to_json, get_communities, read_csv, read_geo_json
from haversine import haversine
from pycountry_convert import *


class TravelRegions:
    def __init__(self, region_model: str = None, levels: int = None):
        """
        A representation of a region model

        Args:
            region_model (str, optional): Path to a custom region model if one
            should be used instead of the default. See
            TODO for a reference of the expected file structure. Defaults to None.
            levels (int, optional): The number of hierarchical levels in the
            region model. Defaults to None.
        """
        self.nodes = {}
        self.regions = {}
        self.regions_serialized = {}

        #######################
        # Extract communities #
        #######################
        if region_model:
            assert (
                levels is not None
            ), "The number of hierarchical levels in the region model must be provided"
            print(
                "Initializing with data from provided region model. This operation may take some time..."
            )
            data = read_csv(region_model)
            # Generate communities for hierarchical levels 1-4
            communities_by_level = {
                i: get_communities(data, i) for i in range(1, levels)
            }
            self.regions_serialized = {}
            for level, communities in communities_by_level.items():
                community_IDs = list(communities.keys())

                #####################
                # Outlier detection #
                #####################
                nonoutliers_by_community = []
                outliers = []
                for community in communities.values():
                    community_nodes = [point for point in community]
                    outliers_z_score = detect_outliers_z_score(
                        [
                            (float(node[-3]), float(node[-2]))
                            for node in community_nodes
                        ],
                        threshold=3,
                    )
                    if len(outliers_z_score) > 1:
                        outlier_indices, _ = zip(*outliers_z_score)
                    elif len(outliers_z_score) > 0:
                        outlier_indices = [outliers_z_score[0][0]]
                    else:
                        outlier_indices = []
                    nonoutliers_by_community += [
                        [
                            node[1]
                            for node in enumerate(community_nodes)
                            if node[0] not in outlier_indices
                        ]
                    ]
                    outliers.append(
                        [community_nodes[index] for index in outlier_indices]
                    )

                #####################
                # Generate polygons #
                #####################
                bounding_area = read_geo_json(
                    os.path.join("data", "cutouts", "world.geojson",)
                )
                bounding_area = list(
                    map(
                        lambda point: [point[1], point[0]],
                        bounding_area["geometry"]["coordinates"][0],
                    )
                )  # flipping coordinates for geovoronoi and Leaflet compatibility
                bounding_area_shape = Polygon(bounding_area)
                nonoutliers = [
                    community_nonoutlier
                    for community_nonoutliers in nonoutliers_by_community
                    for community_nonoutlier in community_nonoutliers
                ]
                nonoutliers_latlng = [
                    (float(nonoutlier[-3]), float(nonoutlier[-2]))
                    for nonoutlier in nonoutliers
                ]
                voronoi_clusters = generate_constrained_voronoi_diagram(
                    nonoutliers_latlng, bounding_area_shape, nonoutliers_by_community
                )
                merged_voronoi_clusters = merge_regions(
                    *voronoi_clusters
                )  # For each cluster, unifies the cluster's single-point voronoi regions into a single polygon
                region_geometries = extract_geometries(*merged_voronoi_clusters)

                # Generate region file JSON dump
                self.regions_serialized[level] = {
                    "level": level,
                    "community_IDs": community_IDs,
                    "bounding_area": bounding_area,
                    "geometries": region_geometries,
                    "nodes": nonoutliers_by_community,
                    "outliers": outliers,
                }
        else:
            for level in range(1, 5):
                path = os.path.join(
                    Path(".").parent,
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
            else "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv"
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
                region_nodes = []
                for region_node_serialized in region_nodes_serialized[i]:
                    region_nodes.append(self.nodes[region_node_serialized[0]])
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

    def export_regions(self, level: int, path: str):
        """
        Generates a region file for the specified hierarchical level

        Args:
            level (int): Hierarchical level for which the region file is to be generated
            path (str): Target location in the file system where the region file is to
            be saved (must include filename). For example, ``path/to/file/my_l2_regions.json``
        """
        with open(path, "w") as f:
            json.dump(self.json_dump[level], f, indent=4)

    # TODO Port remaining functions to TravelRegions


def get_region(id: str, regions: List[Region]) -> Region:
    """
    Returns the region with the given `id` from the provided list

    Args:
        id (str): Region ID
        regions (List[Region]): List of regions to be searched. Typically the result
            of :func:`~load_regions()`.

    Returns:
        Region: Region with matching ID
    """
    for region in regions:
        if region.id == id:
            return region


def get_node(id: str, nodes: List[Node]) -> Node:
    """
    Returns the node with the given `id` from the provided list

    Args:
        id (str): Node ID
        nodes (List[Node]): List of nodes to be searched. Typically the result
            of :func:`~load_nodes()`. 

    Returns:
        Node: Node with matching ID
    """
    for node in nodes:
        if node.id == id:
            return node


def find_region(countries: List[str], regions: List[Region]) -> List[Region]:
    """
    Finds all regions that overlap with the countries in `countries` as
    defined by :func:`~region.get_countries()`

    Args:
        countries (List[str]): Countries of interest
        regions (List[Region]): List of regions to search. Typically the result
            of :func:`~load_regions()`

    Returns:
        List[Region]: Regions that overlap with the given countries
    """
    candidates = set()
    for region in regions:
        hits = 0
        for country in countries:
            for region_country in region.countries:
                matches = find_near_matches(country, region_country, max_l_dist=1)
                if matches:
                    hits += 1
                    break
        if hits == len(countries):
            candidates.add(region)
    return list(candidates)


def find_node(name: str, nodes: List[Node]) -> List[Node]:
    """
    Searches for a node by name and returns all approximate matches

    Args:
        name (str): The search term
        nodes (List[Node]): A list of nodes to be searched for matches. Typically the result
            of :func:`~load_nodes()`.

    Returns:
        List[Node]: All nodes whose names fulfill the matching criterea
    """
    hits = []
    for node in nodes:
        matches = find_near_matches(name, node.name, max_l_dist=1)
        if matches:
            hits.append(node)
    return hits


def get_continent_regions(regions: List[Region], continent: str) -> List[Region]:
    """
    Given a list of regions, returns those regions with at least one node in the
    specified continent

    Args:
        regions (List[Region]): List of regions. Typically retrieved by calling
            :func:`~load_regions()` or continent (str): One of SA, NA, EU, AS, AF,
            OC, or AN

    Returns:
        List[Region]: Regions with at least one node in the given continent
    """
    continent_regions = set()
    for region in regions:
        for country in region.get_countries().keys():
            country = country_name_to_country_alpha2(country, cn_name_format="default")
            try:
                country_continent = country_alpha2_to_continent_code(country)
                # FIXME Remove nested try/except and add a continue here
                # Nested try/except was only added for development to see which country codes need to be handled
            except KeyError:
                try:
                    country_continent = {"EH": "AF", "VA": "EU", "PN": "OC"}[country]
                except KeyError as key:
                    print(
                        f"Country code {key} found neither in pycountry_convert nor in custom dict!"
                    )
                    continue
            if country_continent == continent:
                continent_regions.add(region)
    return list(continent_regions)


def get_nearest_node(point: Tuple[float, float], regions: List[Region]) -> Node:
    """
    Uses Haversine distance to return the nearest known node to `point` whose
    coordinates aren't identical to `point`.

    Args:
        point (Tuple[float, float]): The coordinates of the point whose nearest
        node is to be found
        regions (List[Region]): The regions where the search is to be performed

    Returns:
        Node: The closest, non-identical node to point
    """
    nodes = [
        node for region in regions for node in region.nodes if node.latlng != point
    ]  # extract all nodes
    distances = [haversine(point, node.latlng) for node in nodes]
    nearest_node = nodes[distances.index(min(distances))]
    return nearest_node


def points_to_regions(
    regions: List[Region], points: List[Tuple[float, float]],
) -> Dict[str, List[Tuple[float, float]]]:
    """
    Given a list of points, maps these points to the regions that contain them

    Args:
        regions (List[Region]): The regions to search for the points in.
            Typically the result of :func:`~load_regions()` Can be be combination of
            regions from multiple hierarchical levels.
        points (List[Tuple[float, float]]): The points to whose regions are to be found

    Returns:
        Dict[str, List[Tuple[float, float]]]: A mapping from region IDs to
        points. A point may be mapped to multiple regions if regions from
        multiple hierarchical levels were used.
    """
    region_geometries = [region.geometry for region in regions]

    region_geometries = [
        Polygon(region_geometry["geometry"])
        if region_geometry["type"] == "polygon"
        else MultiPolygon(
            [Polygon(geometry) for geometry in region_geometry["geometry"]]
        )
        for region_geometry in region_geometries
    ]  # convert region geometries to Shapely polygons
    classsifications = classify_points(points, region_geometries)
    return {regions[index].id: points for index, points in classsifications.items()}
