import geopandas as gpd
import os

""" world_cities = gpd.read_file(gpd.datasets.get_path("naturalearth_cities"))
world_countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
print(world_countries)
print(world_cities)
world_cities.plot(figsize=(10, 3)); """
""" world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
germany_france = world.loc[world['name'].isin(['Germany','Switzerland', 'Austria', 'Liechtenstein'])]
print(germany_france)
germany_france.plot(figsize=(10, 3)) """


def extractShape(path, name):
    shapefile = gpd.read_file(path)
    # portion = shapefile.loc[shapefile['SOV0NAME']=='India']
    # print(shapefile)
    portion = shapefile.loc[shapefile["name_en"] == name]
    # print(shapefile['name_en'].values.tolist())
    return portion
    # portion.plot(figsize=(10, 3))


def polyToShp(polygons, target):
    gdf = gpd.GeoDataFrame(geometry=polygons)
    gdf.to_file(target)
