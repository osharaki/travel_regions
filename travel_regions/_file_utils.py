import csv
import json
import geopandas as gpd
from typing import List, Dict


def read_csv(path: str) -> List[List[str]]:
    with open(path, newline="", encoding="utf-8",) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        data: List[str] = []
        for row in csv_reader:
            data.append(row)
        return data


def write_csv(
    data: List[List[str]],
    headers: List[str] = [
        "",
        "community_1",
        "community_2",
        "community_3",
        "community_4",
        "community_5",
        "community_6",
        "country_code",
        "latitude",
        "longitude",
        "place_name",
    ],
    path: str = "output/data.csv",
):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(headers)
        csv_writer.writerows(data)


######################
# CSV file utilities #
######################
def get_max_in_col(col: int) -> int:
    """
    Returns the highest value in the specified column.

    Args:
        col (int): Column index.

    Returns:
        int: Maximum value in column.
    """
    with open(
        "data/communities_-1__with_distance_multi-level_geonames_cities_7.csv",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        max_comm1 = -1
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue  # skip first row (headers)
            comm1 = int(row[col])
            if comm1 > max_comm1:
                max_comm1 = comm1
        return max_comm1


def get_communities(
    data: List[List[str]], comm_level: int
) -> Dict[int, List[List[str]]]:
    """
    Creates a mapping that assigns to each community the location entries belonging to it.

    Args:
        data (List[List[str]]): The location data to be filtered. Each location is expected to correspond to the form: community_1,community_2,community_3,community_4,community_5,community_6,country_code,latitude,longitude,place_name.
        comm_level (int): The community level in the region hierarchy.

    Returns:
        Dict[int, List[List[str]]]: The mapping between communities to location entries.
    """
    communities = {}
    for i, row in enumerate(data):
        if i == 0:
            continue  # skip first row (headers)
        community: int = int(row[comm_level])
        if community not in communities:
            communities[
                community
            ] = []  # Create community entry in dict if it doesn't exist
        communities[community].append(
            row
        )  # Retrieve all communities on comm_level if commId is not ommited
    return communities


#######################
# JSON file utilities #
#######################
def cluster_to_json(data: Dict[str, List[List[float]]], target):
    with open(target, "w") as f:
        json.dump(data, f, indent=4)


def read_geo_json(path):
    with open(path, "r") as f:
        return json.load(f)["features"][0]


#######################
# Shapefile utilities #
#######################
def extract_shape(path, name):
    shapefile = gpd.read_file(path)
    # portion = shapefile.loc[shapefile['SOV0NAME']=='India']
    # print(shapefile)
    portion = shapefile.loc[shapefile["name_en"] == name]
    # print(shapefile['name_en'].values.tolist())
    return portion
    # portion.plot(figsize=(10, 3))


def poly_to_shp(polygons, target):
    gdf = gpd.GeoDataFrame(geometry=polygons)
    gdf.to_file(target)

