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


def load_nodes() -> Dict[int, Node]:
    """
    Parses the communities data file creates an Node instance for each location.

    Returns:
        Dict[int, Node]: The generated Node instances
    """
    data = read_csv(
        "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv"
    )
    nodes = {}
    for i, row in enumerate(data):
        if i == 0:
            continue  # skip first row (headers)
        nodes[row[0]] = Node(
            row[0], row[-1], (float(row[-3]), float(row[-2])), row[-4],
        )
    return nodes


def generate_bounded_regions(
    path: str, level: int = 1, continent: str = None, z_threshold: float = 3,
):
    # FIXME remove continent parameter
    """
    Generates a region file for the specified hierarchical level.

    Args:
        path (str): The path to the region file, e.g. "path/to/file/level_2_region.json"
        level (int, optional): The hierarchical level. Defaults to 1.
        continent (str, optional): One of SA, NA, EU, AS. If specified, regions are constrained to a specific continent (Not yet available). Defaults to None.
        z_threshold (float, optional): Determines outlier elimination strictness. The higher this value the shorter the distance required for a node to be considered an outlier. Defaults to 3.
    """
    assert 0 < level < 5, "Level must be in the interval [1, 5)"
    # TODO add available continent options to docs

    # TODO Add continent cutouts
    #######################
    # Extract communities #
    #######################
    continents = {"SA": 0, "NA": 1, "EU": 2, "AS": 3}
    data = read_csv(
        "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv"
    )
    communities = get_communities(data, 1)
    if continent:
        communities = get_communities(data, 1)  # Extract l1 communities
        communities = communities[continents[continent]]  # Filter by continent
        communities = get_communities(
            communities, level
        )  # Extract communities in continent at specified hierarichal level
    else:
        communities = get_communities(
            communities[0] + communities[1] + communities[2] + communities[3], level
        )  # Level 1 communities 4 and above are very sparsely populated and thus excluded
    community_IDs = list(communities.keys())
    #####################
    # Outlier detection #
    #####################
    nonoutliers_by_community = []
    outliers = []
    for community in list(communities.values()):
        community_nodes = [point for point in community]
        outliersZScore = detect_outliers_z_score(
            [(float(node[-3]), float(node[-2])) for node in community_nodes],
            threshold=z_threshold,
        )
        if len(outliersZScore) > 1:
            outlier_indices, _ = zip(*outliersZScore)
        elif len(outliersZScore) > 0:
            outlier_indices = [outliersZScore[0][0]]
        else:
            outlier_indices = []
        nonoutliers_by_community += [
            [
                node[1]
                for node in enumerate(community_nodes)
                if node[0] not in outlier_indices
            ]
        ]
        outliers.append([community_nodes[index] for index in outlier_indices])

    #####################
    # Generate polygons #
    #####################
    # TODO Create cutouts and load if continent is not None
    bounding_area = read_geo_json(
        None if continent else os.path.join("data", "cutouts", "world.geojson",)
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
        (float(nonoutlier[-3]), float(nonoutlier[-2])) for nonoutlier in nonoutliers
    ]
    voronoiClusters = generate_constrained_voronoi_diagram(
        nonoutliers_latlng, bounding_area_shape, nonoutliers_by_community
    )
    merged_voronoi_clusters = merge_regions(
        *voronoiClusters
    )  # For each cluster, unifies the cluster's single-point voronoi regions into a single polygon

    ######################
    # Export communities #
    ######################
    region_geometries = extract_geometries(*merged_voronoi_clusters)
    cluster_to_json(
        {
            "level": level,
            "community_IDs": community_IDs,
            "bounding_area": bounding_area,
            "geometries": region_geometries,
            "nodes": nonoutliers_by_community,
            "outliers": outliers,
        },
        path,
    )


def load_regions(
    nodes: Dict[int, Node], path: str = None, level: int = 1
) -> List[Region]:
    """
    Generates Regions from a region file. If no `path` to a custom region file is provided, the default region file for the hierarchical level specified by `level` is used. If, however, a `path` argument is provided, `level` will be ignored and instead that region file is used to load the regions.

    Args:
        nodes (Dict[int, Node]): The nodes contained in the regions to be generated. Typically the result of running load_nodes(). The nodes are mapped to the appropriate regions as the regions are being created.
        path (str, optional): An optional path to a custom region file (see :func:`~generate_bounded_regions`). If specified, causes `level` to be ignored. Defaults to None.
        level (int, optional): The hierarchical level for which to generate the regions. Ignored if `path` is not None. Defaults to 1.

    Returns:
        List[Region]: The regions generated from the region file
    """
    if not path:
        path = os.path.join(
            Path(".").parent, "data", "region_files", f"level_{level}_regions.json"
        )
    regions = []
    with open(path, "r") as f:
        regions_serialized = json.load(f)
        hierarchical_level = regions_serialized["level"]
        community_IDs = regions_serialized["community_IDs"]
        geometries = regions_serialized["geometries"]
        region_nodes_serialized = regions_serialized["nodes"]
        for i in range(len(geometries)):
            region_nodes = []
            for region_node_serialized in region_nodes_serialized[i]:
                region_nodes.append(nodes[region_node_serialized[0]])
            regions.append(
                Region(
                    hierarchical_level, community_IDs[i], geometries[i], region_nodes
                )
            )
        return regions


def find_node(name: str, nodes: List[Node]) -> List[Node]:
    hits = []
    for node in nodes:
        matches = find_near_matches(name, node.name, max_l_dist=1)
        if matches:
            hits.append(node)


def get_continent_regions(regions: List[Region], continent: str) -> List[Region]:
    """
    Given a list of regions, returns those regions with at least one node in the specified continent

    Args:
        regions (List[Region]): List of regions. Typically retrieved by calling :func:`~load_regions()` or 
        continent (str): One of SA, NA, EU, AS, AF, OC, or AN

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
    Uses Haversine distance to return the nearest known node to `point` whose coordinates aren't identical to `point`.

    Args:
        point (Tuple[float, float]): The coordinates of the point whose nearest node is to be found
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
        regions (List[Region]): The regions to search for the points in. Typically the result of :func:`~load_regions` Can be be combination of regions from multiple hierarchical levels.
        points (List[Tuple[float, float]]): The points to whose regions are to be found

    Returns:
        Dict[str, List[Tuple[float, float]]]: A mapping from region IDs to points. A point may be mapped to multiple regions if regions from multiple hierarchical levels were used.
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
