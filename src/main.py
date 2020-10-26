from typing import Dict, List, Tuple
import matplotlib.pyplot as pl

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
    L2CommunitesGlobal: Dict[int, List[List[str]]] = getCommunities(
        [
            location
            for locationsInContinent in l1Communities.values()
            for location in locationsInContinent
        ],
        2,
    )
    l2MembersLatinAmerica: List[List[str]] = [
        (float(l2MemberAtId[-3]), float(l2MemberAtId[-2]))
        for l2CommunityId in l2CommunitiesLatinAmerica
        for l2MemberAtId in l2CommunitiesLatinAmerica[l2CommunityId]
    ]

    """ x: float
    y: float 
    x, y = zip(*l2MembersLatinAmerica[:200]) 
    fig = pl.figure(figsize=(10,10))
    pl.scatter(x, y)
    polygon = generateConvexHull(l2MembersLatinAmerica[:200])
    plot_polygon(polygon, fig)
    pl.show() """
    polygons = []
    communities = []
    outliers = []
    # centroids = []
    for community in list(l2CommunitiesLatinAmerica.values())[:3]:
        communityNodes: List[Tuple[float, float]] = [
            [float(point[-3]), float(point[-2])] for point in community
        ]

        # centroid = findCentroid(communityNodes)
        outliersZScore = detectOutliersZScore(communityNodes, threshold=3)
        if(len(outliersZScore) > 1):
            outlierIndices, _ = zip(*outliersZScore)
        elif(len(outliersZScore) > 0):
            outlierIndices = [outliersZScore[0][0]]
        else:
            outlierIndices = []

        nonoutliers = [
            node[1]
            for node in enumerate(communityNodes)
            if node[0] not in outlierIndices
        ]
        polygon = generateConcaveHull(communityNodes)
        # polygon = generateConcaveHull(nonoutliers)

        # polygon = generateConvexHull(communityNodes)
        # polygon = generateConvexHull(nonoutliers)

        polygons.append(polygon)

        # communities.append(communityNodes)
        communities.append(nonoutliers)
        outliers.append([communityNodes[index] for index in outlierIndices])
        # centroids.append(centroid)

    clusterToJSON(
        {"polygons": polygons, "communities": communities, "outliers": outliers},
        "C:/Users/osharaki/OneDrive - Technische Universitat Munchen/programming_misc/WebDev/Leaflet_Sandbox/data.json",
    )

    return
    writeData: List[List[str]] = [
        memberAtId
        for l2CommunityId in L2CommunitesGlobal
        for memberAtId in L2CommunitesGlobal[l2CommunityId]
    ]
    writeCSV(
        writeData,
        path="C:/Users/osharaki/OneDrive - Technische Universitat Munchen/programming_misc/WebDev/Leaflet_Sandbox/data.csv",
    )
    """ for l2CommunityId in l2CommunitiesLatinAmerica:
        for memberAtId in l2CommunitiesLatinAmerica[l2CommunityId]:
            print(memberAtId)
        print(f"End members in community {l2CommunityId}") """


if __name__ == "__main__":
    main()
