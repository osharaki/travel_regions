import matplotlib.pyplot as pl
import numpy as np

from shapely.affinity import scale
from shapely.geometry import Polygon
from typing import Dict, List, Tuple
from csvIO import *
from shpIO import *
from jsonIO import *
from parseCSV import *
from boundary import *
from outliers import *


def main():
    data: List[str] = readCSV(
        "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv"
    )
    l1Communities: Dict[int, List[List[str]]] = getCommunities(
        data, 1
    )  # All L1 regions (continents)
    l2CommunitiesLatinAmerica: Dict[int, List[List[str]]] = getCommunities(
        l1Communities[0], 2
    )  # L2 regions in SA (~countries)

    polygons = []
    communities = []
    outliers = []
    for community in list(l2CommunitiesLatinAmerica.values())[:3]:
        communityNodes: List[Tuple[float, float]] = [
            [float(point[-3]), float(point[-2])] for point in community
        ]

        outliersZScore = detectOutliersZScore(communityNodes, threshold=3)
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
        containingAreaShape = readGeoJSON(
            os.path.join(
                "c://",
                "users",
                "osharaki",
                "desktop",
                "tmp",
                "geo",
                "SouthAmerica.geojson",
            )
        )

    containingAreaShape = list(
        map(
            lambda point: [point[1], point[0]],
            containingAreaShape["geometry"]["coordinates"][0],
        )
    )  # flipping coordinates for Leaflet compatibility

    containingAreaShape = Polygon(containingAreaShape)
    nonoutliersJoined = [
        nonoutlier
        for community in communities
        for nonoutlier in community
    ]
    poly_shapes, pts, poly_to_pt_assignments = generateConstrainedVoronoiDiagram(
        nonoutliersJoined, containingAreaShape
    )
    pt_to_poly_assignments = [None]*len(nonoutliersJoined)
    for polygon, points_in_polygon in zip(poly_shapes, poly_to_pt_assignments):
        pt_to_poly_assignments[points_in_polygon[0]] = polygon
    for i, c in enumerate(communities):
        start = end if i != 0 else 0
        end = start + len(communities[i])
        polygons.append([list(zip(*polygon.exterior.coords.xy)) for polygon in pt_to_poly_assignments[start:end]])

    clusterToJSON(
        {"polygons": polygons, "communities": communities, "outliers": outliers},
        "C:/Users/osharaki/OneDrive - Technische Universitat Munchen/programming_misc/WebDev/Leaflet_Sandbox/data.json",
    )

    return


if __name__ == "__main__":
    main()
