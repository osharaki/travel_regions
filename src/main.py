from shapely.geometry import Polygon
from typing import Dict, List, Tuple
from utils.file_utils import *
from outliers import *
from polygons import *


def main():
    data: List[str] = read_csv(
        "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv"
    )
    l1Communities: Dict[int, List[List[str]]] = get_communities(
        data, 1
    )  # All L1 regions (continents)
    """ l2Communities: Dict[int, List[List[str]]] = get_communities(
        [node for continentNodes in l1Communities.values() for node in continentNodes],
        2,
    ) """  # All L2 regions (~continents)
    l2CommunitiesLatinAmerica: Dict[int, List[List[str]]] = get_communities(
        l1Communities[0], 2
    )  # L2 regions in SA (~countries)

    l2CommunitiesX: Dict[int, List[List[str]]] = get_communities(
        l1Communities[0] + l1Communities[1] + l1Communities[2] + l1Communities[3], 2
    )  # L2 regions
    print(len(list(l1Communities.values())))
    communities = []
    outliers = []
    for community in list(l2CommunitiesX.values()):
        communityNodes: List[Tuple[float, float]] = [
            [float(point[-3]), float(point[-2])] for point in community
        ]

        outliersZScore = detect_outliers_z_score(communityNodes, threshold=3)
        if len(outliersZScore) > 1:
            outlierIndices, _ = zip(*outliersZScore)
        elif len(outliersZScore) > 0:
            outlierIndices = [outliersZScore[0][0]]
        else:
            outlierIndices = []

        nonoutliers = [
            node[1]
            for node in enumerate(communityNodes)
            if node[0] not in outlierIndices
        ]
        communities.append(nonoutliers)
        outliers.append([communityNodes[index] for index in outlierIndices])

    containingAreaShape = read_geo_json(
        os.path.join("data", "cutouts", "world.geojson",)
    )

    containingAreaShape = list(
        map(
            lambda point: [point[1], point[0]],
            containingAreaShape["geometry"]["coordinates"][0],
        )
    )  # flipping coordinates for geovoronoi and Leaflet compatibility
    containingArea = containingAreaShape
    containingAreaShape = Polygon(containingAreaShape)
    nonoutliersJoined = [
        nonoutlier for community in communities for nonoutlier in community
    ]

    voronoiClusters = generate_constrained_voronoi_diagram(
        nonoutliersJoined, containingAreaShape, communities
    )
    mergedVoronoiClusters = merge_regions(*voronoiClusters)
    print(
        classify_points(
            [
                [-14.269798, -40.821783],
                [-24.452236, -48.556158],
                [-38.826944, -71.847173],
            ],
            mergedVoronoiClusters,
        )
    )
    # Convert merged regions from Shapely polygons to list of coordinates taking into consideration regions with fragmented unions (typically the result of communities with noncontiguous Voronoi regions)
    polygons = extract_geometries(*mergedVoronoiClusters)

    cluster_to_json(
        {
            "boundary": containingArea,
            "polygons": polygons,
            "communities": communities,
            "outliers": outliers,
        },
        "C:/Users/osharaki/OneDrive - Technische Universitat Munchen/programming_misc/WebDev/Leaflet_Sandbox/data.json",
    )

    return


if __name__ == "__main__":
    main()
