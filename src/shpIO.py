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

""" shapefile = gpd.read_file(
    os.path.join(
        "c://",
        "users",
        "osharaki",
        "desktop",
        "tmp",
        "geo",
        "ne_110m_populated_places",
        "ne_110m_populated_places.shp",
    )
)
portion = shapefile.loc[shapefile['SOV0NAME']=='India']
print(portion)
portion.plot(figsize=(10, 3)) """

def polyToShp(polygons, target):
    gdf = gpd.GeoDataFrame(geometry=polygons)
    gdf.to_file(target)