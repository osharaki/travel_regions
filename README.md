## Environment setup

Before the code can be run, all module dependencies must be installed.

1. Clone this repository
2. Navigate to its root directory
3. In your terminal, run `conda env create` _(it is assumed [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) is already installed)_

   This will use [environment.yml](/environment.yml) to create a Conda environment called `giscience` with all the required dependencies in your default Conda environment path.

   _Should an environment with that name already exist, you can give the new environment a different name by changing the `name` field's value in `environment.yml` to something else._

4. Be sure to activate the environment before running the code

## Usage

First, [Node](/src/node.py) and [Region](/src/region.py) objects need to be instantiated. These will be needed for all subsequent operations.

```python
from regions import *

nodes = load_nodes()

l1_regions = load_regions(nodes, level=1)
l2_regions = load_regions(nodes, level=2)
l3_regions = load_regions(nodes, level=3)
l4_regions = load_regions(nodes, level=4)
```

Now, one of the following, currently supported operations can be executed.

```python
# Get nearest known node to the given coordinates
nearest_node = get_nearest_node((40.781459, -73.966551), l2_regions)

# Find the regions that contain the given points
points = [
            [-14.269798, -40.821783],
            [-24.452236, -48.556158],
            [-38.826944, -71.847173]
         ]
region_mappings = points_to_regions(l2_regions, points)

# Get a region's neighbors
neighboring_regions =  l2_regions[1].get_neighbors(l2_regions)

# Filter regions by continent
regions_south_america = get_continent_regions(l2_regions, "SA")

# Find node by name
matching_nodes = find_node("Springfield", list(nodes.values()))

# Get region by ID
region = get_region("22", l1_regions + l2_regions + l3_regions + l4_regions)

# Find region by countries spanned
matching_regions = find_region(["Paraguay", "Brazil"], l2_regions)
```

## Region files

The library utilizes so-called region files, one for each hierarchical level, to derive the information needed for all subsequent operations. These region files are in turn derived from the communities data [file](/data/communities_-1__with_distance_multi-level_geonames_cities_7).

Four region files for the first four hierarchical levels are already available in [region_files](/data/region_files). When calling `load_regions()`, unless a path to a custom region file is provided, the default region file for the specified hierarchical level is used.

_Note that no region files were generated for the remaining three hierarchical levels due to data sparseness._

### Custom region files

Custom region files can be generated using `generate_bounded_regions()`. For example, the following generates a level 2 region file called `level_2_region.json` at the specified path:

```python
generate_bounded_regions('path/to/file/level_2_region.json', level=2)
```

See function definition for full list of parameters.

## Visualization

[Travel Regions Visualizer](https://github.com/osharaki/travel_regions_visualizer) is a simple JavaScript library built to interpret region files and visualize them using Leaflet.
