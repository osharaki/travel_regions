from csvIO import *
from parseCSV import *
from typing import Dict, List


def main():
    data: List[str] = readCSV(
        "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv"
    )
    l1Communities: Dict[int, List[List[str]]] = getCommunities(data, 1)
    l2CommunitiesLatinAmerica: Dict[int, List[List[str]]] = getCommunities(
        l1Communities[0], 2
    )
    writeData: List[List[str]] = [
        memberAtId
        for l2CommunityId in l2CommunitiesLatinAmerica
        for memberAtId in l2CommunitiesLatinAmerica[l2CommunityId]
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
