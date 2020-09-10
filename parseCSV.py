import csv
from typing import List, Dict


def getMaxInCol(col: int) -> int:
    """
    Returns the highest value in the specified column.

    Arguments:
        col {int} -- Column index

    Returns:
        int -- Maximum value in column
    """
    with open(
        "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=",")
        maxComm1 = -1
        for i, row in enumerate(csvReader):
            if i == 0:
                continue  # skip first row (headers)
            comm1 = int(row[col])
            if comm1 > maxComm1:
                maxComm1 = comm1
        return maxComm1


def getCommunities(data: List[str], commLevel: int) -> Dict[int, List[List[str]]]:
    """
    Creates a mapping that assigns to each community the location entries belonging to it.

    Arguments:
        data {List[str]} -- The location data to be filtered. Each location is expected to correspond to the form: community_1,community_2,community_3,community_4,community_5,community_6,country_code,latitude,longitude,place_name
        commLevel {int} -- The community level in the region hierarchy.

    Returns:
        Dict[int, List[List[str]]] -- The mapping between communities to location entries.
    """
    communities = {}
    for i, row in enumerate(data):
        if i == 0:
            continue  # skip first row (headers)
        community: int = int(row[commLevel])
        if community not in communities:
            communities[
                community
            ] = []  # Create community entry in dict if it doesn't exist
        communities[community].append(
            row
        )  # Retrieve all communities on commLevel if commId is not ommited
    return communities


def getData(path) -> List[str]:
    with open(path, newline="", encoding="utf-8",) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=",")
        data: List[str] = []
        for row in csvReader:
            data.append(row)
        return data
