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
        community_nodes = [
            Node(point[0], point[-1], (float(point[-3]), float(point[-2]), None, {}),)
            for point in community
        ]
        outliersZScore = detectOutliersZScore(
            [node.latlng for node in community_nodes], threshold=zThreshold
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
    # TODO Generate and return Region instances
    regions = []
    with open(path, "r") as f:
        regions = json.load(f)
        hierarchical_level = regions["level"]
        geometries = regions["geometries"]
        nodes = regions["nodes"]

        for i in range(len(geometries)):
            # TODO add nodes to region
            # [Node() for region_node in nodes[i]]
            regions.append(Region(level, geometries[i],))


def load_regions(path: str, level: int) -> List[Region]:
    # TODO read region file and generate Region objects accordingly
    # TODO Assign each node the correct region id on this hierarchical level: node.regions[level] = regionId
    pass


def export_regions():
    # TODO save generated community regions to file
    pass
