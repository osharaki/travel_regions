## Installing for development

1. Clone this repository
2. Navigate to its root directory
3. Run `pip install -e .`

## Usage

```python
from travel_regions import TravelRegions

travel_regions = TravelRegions()
```

Now, one of the following, currently supported operations can be executed.

```python
# Get nearest known node to the given coordinates
nearest_node = travel_regions.get_nearest_node((40.781459, -73.966551))

# Find the regions that contain the given points
points = [
            [-14.269798, -40.821783],
            [-24.452236, -48.556158],
            [-38.826944, -71.847173]
         ]
region_mappings = travel_regions.points_to_regions(points)

# Get a level 2 region's neighbors on the same hierarchical level
l2_regions = travel_regions.regions[2]
neighboring_regions =  l2_regions[1].get_neighbors(l2_regions)

# Filter regions by continent
regions_south_america = travel_regions.get_continent_regions("SA")

# Find node by name
matching_nodes = travel_regions.find_node("Springfield")

# Get region by ID
region = travel_regions.get_region("22")

# Find region by countries spanned
matching_regions = travel_regions.find_region(["Paraguay", "Brazil"])
```

## Region files

A region file is a serialized class representations of
a region model.

Four region files for the first four hierarchical levels of the default [region
model](/data/communities_-1__with_distance_multi-level_geonames_cities_7) are already available
in [region_files](/data/region_files). These are what's used when
`TravelRegions` is instantiated without any arguments.
_Note that no region files were generated for the remaining three hierarchical
levels due to data sparseness._

If, however, a custom
region model is provided, i.e.
`TravelRegions(region_model="path/to/my_region_model.csv", levels=3)`, then that
region model is used as a point of origin instead.

The serialized class representation of any region model can be exported as a region file
for a specific hierarchical level by
calling the [`export_regions()`](src/regions.py#L180-L191) method of `TravelRegions`.

## Visualization

[Travel Regions Visualizer](https://github.com/osharaki/travel_regions_visualizer) is a simple JavaScript library built to interpret region files and visualize them using Leaflet.
