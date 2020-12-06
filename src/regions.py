import json
import os
from pathlib import Path
from typing import List

from shapely.geometry.polygon import Polygon

from node import Node
from outliers import detect_outliers_z_score
from polygons import (
    extract_geometries,
    generate_constrained_voronoi_diagram,
    merge_regions,
)
from region import Region
from utils.file_utils import cluster_to_json, get_communities, read_csv, read_geo_json


def generate_bounded_regions(
    path: str, level: int = 1, continent: str = None, zThreshold: float = 3
) -> List[Region]:
    # TODO break up into multiple functions

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

    #####################
    # Outlier detection #
    #####################
    nonoutliers_by_community = []
    outliers = []
    # TODO consider only creating list of Nodes at the very end to not have to reiterate over them to fill in missing region information
    for community in list(communities.values()):
        # TODO use nodes in serialized form instead (like in main)
        community_nodes = [point for point in community]
        outliersZScore = detect_outliers_z_score(
            [(float(node[-3]), float(node[-2])) for node in community_nodes],
            threshold=zThreshold,
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
            "bounding_area": bounding_area,
            "geometries": region_geometries,
            "nodes": nonoutliers_by_community,
            "outliers": outliers,
        },
        path,
    )

    ###########################################
    # Load communities as instances of Region #
    ###########################################
    return load_regions(path, level)


def load_regions(path: str, level: int) -> List[Region]:
    # Read region file and generate Region objects accordingly
    regions = []
    with open(path, "r") as f:
        regions_serialized = json.load(f)
        hierarchical_level = regions_serialized["level"]
        geometries = regions_serialized["geometries"]
        nodes = regions_serialized["nodes"]

        for i in range(len(geometries)):
            region_nodes = [
                Node(
                    region_node[0],
                    region_node[-1],
                    (float(region_node[-3]), float(region_node[-2])),
                    None,
                )
                for region_node in nodes[i]
            ]
            regions.append(Region(hierarchical_level, geometries[i], region_nodes))
        return regions


def export_regions():
    # TODO save generated community regions to file
    pass


regions = generate_bounded_regions(
    os.path.join(Path(".").parent, "output", "regions_test.json")
)
print(regions)

