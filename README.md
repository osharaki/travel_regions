## Installing for development

1. Clone this repository
2. Navigate to its root directory
3. Run `pip install -e .`

## Usage

```python
from travel_regions import TravelRegions

travel_regions = TravelRegions()
```

The [examples](./examples) section shows how `TravelRegions` can be utilized for various use cases.

## Exporting results

Results are exported in the form of region files, which are serialized
representations, following a standardized structure, of an instance of
TravelRegions at a specific hierarchical level.

Four region files for the first four hierarchical levels of the default [region
model](/data/communities_-1__with_distance_multi-level_geonames_cities_7) are already available
in [region_files](/data/region_files). These are what's used when
`TravelRegions` is instantiated without any arguments (default instantiation).

If, however, a region model is provided, i.e.
`TravelRegions(region_model="path/to/my_region_model.csv", levels=3)`, then that
region model is used as a point of origin instead. For an example of how the CSV
file representing a region model should be structured, refer to the [travel
region
model](/data/communities_-1__with_distance_multi-level_geonames_cities_7).

The serialized class representation of any region model can be exported as a region file
for a specific hierarchical level by
calling the [`export_regions()`](src/regions.py#L180-L191) method of `TravelRegions`.

## Visualization

[Travel Regions Visualizer](https://github.com/osharaki/travel_regions_visualizer) is a simple JavaScript library built to interpret region files and visualize them using Leaflet.
