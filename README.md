### Environment setup

Before the code can be run, all module dependecies must be installed. To do this, create a Conda environment _(it is assumed [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) is already installed)_ by running `conda env create --file envname.yml`

### Usage

First, [Node](/src/Node.py) and [Region](/src/Region.py) objects need to be instantiated. These will be needed for all subsequent operations.

```python
nodes = load_nodes()
l2_regions = load_regions(nodes, level=2)
```

Now, one of the following, currently supported operations can be executed.

```python
# Get nearest Node to the given coordinates
nearest_node = get_nearest_node((40.781459, -73.966551), l2_regions)

# Assign points to the Regions that contain them
points = [
            [-14.269798, -40.821783],
            [-24.452236, -48.556158],
            [-38.826944, -71.847173]
         ]
region_mappings = points_to_regions(points)

# Get a region's neighbors
neighboring_regions =  l2_regions[1].get_neighbors(l2_regions)
```

### Region files

The library utilizes so-called region files, one for each hierarchical level, to derive the information needed for all subsequent operations. These region files are in turn derived from the communities data [file](/data/communities_-1__with_distance_multi-level_geonames_cities_7).

Four region files for the first four hierarchical levels are already available in [region_files](/data/region_files). When calling `load_regions()`, unless a path to a custom region file is provided, the default region file for the specified hierarchical level is used.

_Note that no region files were generated for the remaining three hierarchical levels due to data sparseness._

#### Custom region files

Custom region files can be generated using `generate_bounded_regions()`. For example, the following generates a level 2 region file called `level_2_region.json` at the specified path:

```python
generate_bounded_regions('path/to/file/level_2_region.json', level=2)
```

See function [definition](https://github.com/osharaki/regions/blob/master/src/regions.py#L134) for full list of parameters.
