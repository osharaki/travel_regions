from travel_regions import TravelRegions

travel_regions = TravelRegions()

# Get nearest known node to the given coordinates
nearest_node = travel_regions.get_nearest_node((40.781459, -73.966551))

# Find the regions that contain the given points
points = [[-14.269798, -40.821783], [-24.452236, -48.556158], [-38.826944, -71.847173]]
region_mappings = travel_regions.points_to_regions(points)

# Get a level 2 region's neighbors on the same hierarchical level
l2_regions = travel_regions.regions[2]
neighboring_regions = l2_regions[1].get_neighbors(l2_regions)

# Filter regions by continent
regions_south_america = travel_regions.get_continent_regions("SA")

# Find node by name
matching_nodes = travel_regions.find_node("Springfield")

# Get region by ID
region = travel_regions.get_region("22")

# Find region by countries spanned
matching_regions = travel_regions.find_region(["Paraguay", "Brazil"])
