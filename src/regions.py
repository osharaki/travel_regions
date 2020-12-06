import json
import os
from typing import List
from node import Node
from outliers import detectOutliersZScore
from polygons import extractGeometries, generateConstrainedVoronoiDiagram, mergeRegions
from region import Region
from utils.file_utils import clusterToJSON, getCommunities, readCSV, readGeoJSON


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
    data = readCSV(
        "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv"
    )
    communities = getCommunities(data, 1)
    if continent:
        communities = getCommunities(data, 1)  # Extract l1 communities
        communities = communities[continents[continent]]  # Filter by continent
        communities = getCommunities(
            communities, level
        )  # Extract communities in continent at specified hierarichal level
    else:
        communities = getCommunities(
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
        outliersZScore = detectOutliersZScore(
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
    bounding_area = readGeoJSON(
        None if continent else os.path.join("data", "cutouts", "world.geojson",)
    )
    bounding_area = list(
        map(
            lambda point: [point[1], point[0]],
            bounding_area["geometry"]["coordinates"][0],
        )
    )  # flipping coordinates for geovoronoi and Leaflet compatibility
    nonoutliers = [
        community_nonoutlier
        for community_nonoutliers in nonoutliers_by_community
        for community_nonoutlier in community_nonoutliers
    ]
    voronoiClusters = generateConstrainedVoronoiDiagram(
        nonoutliers, bounding_area, nonoutliers_by_community
    )
    merged_voronoi_clusters = mergeRegions(
        *voronoiClusters
    )  # For each cluster, unifies the cluster's single-point voronoi regions into a single polygon

    ######################
    # Export communities #
    ######################
    region_geometries = extractGeometries(*merged_voronoi_clusters)
    clusterToJSON(
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
        regions = json.load(f)
        hierarchical_level = regions["level"]
        geometries = regions["geometries"]
        nodes = regions["nodes"]

        for i in range(len(geometries)):
            region_nodes = [
                Node(
                    region_node[0],
                    region_node[-1],
                    (float(region_node[-3]), float(region_node[-2]), None),
                )
                for region_node in nodes[i]
            ]
            regions.append(Region(hierarchical_level, geometries[i], region_nodes))
        return regions


def export_regions():
    # TODO save generated community regions to file
    pass
