"""
An example that finds the L4 region containing Munich
"""

from travel_regions import TravelRegions
import os
import json

# Initialize travel regions
travel_regions = TravelRegions()

level = 4
# Find node corresponding to Munich
munich = travel_regions.find_node("Munich")[0]

# Get L4 region containing Munich
l4_region_munich = munich.regions[level]

# TODO Update output path and uncomment to export regions
""" regions_serialized = {
    "level": level,
    "community_IDs": [l4_region_munich.community_id],
    "nodes": [[{"id": munich.id, "latlng": munich.latlng}]],
    "geometries": [l4_region_munich.geometry],
}
path = None
with open(path, "w",) as f:
    json.dump(regions_serialized, f, indent=4) """

