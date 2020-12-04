from utils.file_utils import getCommunities, readCSV


def generateBoundedRegions(level: int = 1, continent: str = None):
    # TODO add available continent options to docs

    # TODO Add continent cutouts
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
        # TODO generate Voronoi regions within continental boundary
    else:
        communities = getCommunities(
            communities[0] + communities[1] + communities[2] + communities[3], level
        )  # Level 1 communities 4 and above are very sparsely populated and thus excluded
        # TODO generate Voronoi regions within global boundary


def exportRegions():
    pass
