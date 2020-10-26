# http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/
from typing import Dict, List, Tuple
import shapely.geometry as geometry
import matplotlib.pyplot as pl
from descartes import PolygonPatch
import alphashape
import time

def generateConcaveHull(points: List[Tuple[float, float]], visualize=False):
    start = time.time()
    alpha_shape = alphashape.alphashape(points)
    fig, ax = pl.subplots()
    ax.scatter(*zip(*points))
    ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
    end = time.time()
    print(f'Elapsed time: {end-start}')
    if(visualize):
        pl.show()
    return list(zip(*alpha_shape.exterior.coords.xy))

def generateConvexHull(points: List[Tuple[float, float]]):
    point_collection = geometry.MultiPoint(points)
    pp = PolygonPatch(point_collection.convex_hull)
    return pp._path.vertices.tolist()


def plot_polygon(polygon, figure):
    ax = figure.add_subplot(111)
    margin = 0.3
    x_min, y_min, x_max, y_max = polygon.bounds
    ax.set_xlim([x_min - margin, x_max + margin])
    ax.set_ylim([y_min - margin, y_max + margin])
    patch = PolygonPatch(polygon, fc="#999999", ec="#000000", fill=True, zorder=-1)
    ax.add_patch(patch)
    return figure
