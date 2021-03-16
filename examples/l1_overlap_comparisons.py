"""
An example showcasing overlap comparisons between L1 regions and continents
"""

from travel_regions._geometry import *
from travel_regions import TravelRegions
import os
from shapely.ops import transform
import geopandas as gpd

# Initialize travel regions
travel_regions = TravelRegions()

# Extract continents from Natural Earth Data
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
continent = "South America"
continent_geometry = world[world.continent == continent].geometry.cascaded_union
continent_geometry = transform(lambda x, y: (y, x), continent_geometry)

# Compare overlaps
level = 1
overlap_threshold = 10
overlapping_regions = travel_regions.compare_overlap(level, continent_geometry)

# TODO Decide whether to treat overlap threshold as percentage of region or as percentage
# of continent, by commenting out the corresponding statement
overlapping_regions = {
    k: v for k, v in overlapping_regions.items() if v[1] >= overlap_threshold
}  # only include overlapping regions whose overlap with the continent makes up at least 10% of the continent's area
""" overlapping_regions = {
    k: v for k, v in overlapping_regions.items() if v[0] >= overlap_threshold
}  # only include overlapping regions whose overlap with the continent makes up at least 10% of their area """

# TODO Update output path and uncomment to export regions
""" path = None  
travel_regions.export_regions(
    path, regions_ids=overlapping_regions, level=level,
) """

