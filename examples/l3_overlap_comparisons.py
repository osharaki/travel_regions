"""
An example that finds all L3 travel regions overlapping with Germany and the
nodes they contain organized by country
"""

from travel_regions._geometry import extract_geometries
from travel_regions.admin_regions import get_country_codes, get_admin_region_geoms
from travel_regions import TravelRegions
import os
import json

# Initialize travel regions
travel_regions = TravelRegions()

# Get top-level administrative regions of Germany
de_admin_regions = get_admin_region_geoms("de")

# Organize all nodes by country
country_nodes = {}
for node in travel_regions.nodes.values():
    if (country := get_country_codes(node.country)) is not None:
        if country.name in country_nodes:
            country_nodes[country.name].append(node)
        else:
            country_nodes[country.name] = [node]

level = 3
# TODO Decide whether to perform overlap comparison Germany or Bavaria by commenting out the corresponding statement
""" regions_overlap = travel_regions.compare_overlap(level, de_admin_regions["Germany"])
overlap_threshold = 2 """
regions_overlap = travel_regions.compare_overlap(
    level, de_admin_regions["Freistaat Bayern"]
)
overlap_threshold = 10

# TODO Decide whether threshold applies to overlap as percentage of region or as percentage
# of country, by commenting out the corresponding statement
regions_overlap = {
    k: v for k, v in regions_overlap.items() if v[1] >= overlap_threshold
}  # only include overlapping regions whose overlap with Germany makes up at least 2% of the country's area
""" regions_overlap = {
    k: v for k, v in regions_overlap.items() if v[0] >= overlap_threshold
}  # only include overlapping regions whose overlap with Germany makes up at least 2% of their area """

region_country_nodes = {}
overlapping_regions = {}
overlapping_region_geoms = []
overlapping_region_nodes = []
for overlapping_region_ID in regions_overlap:
    overlapping_region_nodes.append([])
    region_country_nodes[overlapping_region_ID] = {}
    overlapping_regions[overlapping_region_ID] = travel_regions.get_region(
        overlapping_region_ID
    )

    overlapping_region_geoms.append(
        (
            overlapping_regions[overlapping_region_ID].community_id,
            overlapping_regions[overlapping_region_ID].geometry,
        )
    )
    for node in overlapping_regions[overlapping_region_ID].nodes:
        if node.name == "Munich":
            overlapping_region_nodes[-1].append({"id": node.id, "latlng": node.latlng})
        if (country := get_country_codes(node.country)) is not None:
            if country.name in region_country_nodes[overlapping_region_ID]:
                region_country_nodes[overlapping_region_ID][country.name].append(node)
            else:
                region_country_nodes[overlapping_region_ID][country.name] = [node]
    print(f"Region ID: {overlapping_region_ID}")
    for country, nodes in region_country_nodes[overlapping_region_ID].items():
        print(
            f"\t{country}: {len(nodes)}/{len(country_nodes[country])} nodes ({(len(nodes)/len(country_nodes[country]))*100:.2f}\%)"
        )

# TODO Update output path and uncomment to export regions
""" serialized_IDs, serialized_geoms = zip(*overlapping_region_geoms)
regions_serialized = {
    "level": level,
    "community_IDs": list(serialized_IDs),
    "nodes": overlapping_region_nodes,
    "geometries": list(serialized_geoms),
}
path = None
with open(path, "w",) as f:
    json.dump(regions_serialized, f, indent=4) """

