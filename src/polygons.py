# http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/
from typing import Dict, List, Tuple, Union
import shapely.geometry as geometry
import matplotlib.pyplot as pl
import alphashape
import time
import os
import numpy as np

from typing import Dict, List, Tuple
from descartes import PolygonPatch
from geovoronoi import voronoi_regions_from_coords, coords_to_points, points_to_coords
from shapely.ops import cascaded_union


def generateConcaveHull(points: List[Tuple[float, float]], visualize=False):
    start = time.time()
    alpha_shape = alphashape.alphashape(points)
    fig, ax = pl.subplots()
    ax.scatter(*zip(*points))
    ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
    end = time.time()
    print(f"Elapsed time: {end-start}")
    if visualize:
        pl.show()
    return list(zip(*alpha_shape.exterior.coords.xy))


def generateConvexHull(points: List[Tuple[float, float]]):
    point_collection = geometry.MultiPoint(points)
    pp = PolygonPatch(point_collection.convex_hull)
    return pp._path.vertices.tolist()


def generateConstrainedVoronoiDiagram(
    points: List[List[float]],
    containingArea: geometry.Polygon,
    communities: List[List[List[float]]] = None,
) -> Union[List[List[geometry.Polygon]], List[geometry.Polygon]]:
    """
    Generates a Voronoi diagram from a list of points that is constrained within a given area. If `communities` is provided, this method further assigns the generated Voronoi regions to their corresponding communities. All coordinates must be given as latitude followed by longitude. All polygons are returned as Shapely polygons.

    Args:
        points (List[List[float]]): A list of coordinates.
        containingArea (geometry.Polygon): A Shapely polygon that forms the boundary of the generated Voronoi diagram. All `points` must be contained within this area.
        communities (List[List[List[float]]], optional): An optional mapping that associates each community with the points (provided as coordinates) belonging to it. Defaults to None.

    Returns:
        Union[List[List[geometry.Polygon]], List[geometry.Polygon]]: The Voronoi diagram as a list of Shapely polygons. If `communities` is provided, the generated Voronoi regions will further be organized and returned as a list of communities of the form List[List[geometry.Polygon]], where each community contains the Voronoi regions surrounding the nodes that form it.
    """
    points = np.array(points)

    coords = coords_to_points(points)
    # use only the points inside the geographic area
    containedPoints = []
    for p in coords:  # converts to shapely Point
        if p.within(containingArea):
            containedPoints.append(p)
    poly_shapes, pts, poly_to_pt_assignments = voronoi_regions_from_coords(
        points, containingArea
    )
    if communities:
        polygons = []
        pt_to_poly_assignments = [None] * len(points)
        for polygon, points_in_polygon in zip(poly_shapes, poly_to_pt_assignments):
            pt_to_poly_assignments[points_in_polygon[0]] = polygon
        for i, c in enumerate(communities):
            start = end if i != 0 else 0
            end = start + len(communities[i])
            polygons.append(pt_to_poly_assignments[start:end])
        return polygons
    return poly_shapes


def mergeRegions(
    *voronoiCommunities: List[geometry.Polygon],
) -> Union[List[geometry.MultiPolygon], List[geometry.Polygon]]:
    """
    This function takes an arbitrary number of communities, each represented as a list of Shapely polygons and combines each community's regions into a single unified region.

    Args:
        *voronoiCommunties: Arbitrary number of communities, each represented as a list of Shapely polygons.

    Returns:
        Union[List[geometry.MultiPolygon], List[geometry.Polygon]]: Communities each represented by either a Shapely Polygon or MultiPolygon depending on whether the community's original regions were spatially contiguous.
    """
    mergedRegions = []
    for communityRegions in voronoiCommunities:
        mergedRegion = cascaded_union(communityRegions)
        mergedRegions.append(mergedRegion)
    return mergedRegions


def plot_polygon(polygon, figure):
    ax = figure.add_subplot(111)
    margin = 0.3
    x_min, y_min, x_max, y_max = polygon.bounds
    ax.set_xlim([x_min - margin, x_max + margin])
    ax.set_ylim([y_min - margin, y_max + margin])
    patch = PolygonPatch(polygon, fc="#999999", ec="#000000", fill=True, zorder=-1)
    ax.add_patch(patch)
    return figure


# Convert Shapely regions to list coordinates
def extractGeometries(*shapelyPolygons) -> List[Dict]:
    """
    Given one or more Shapely polygons/multipolygons, extracts their geometries as lists of coordinates.

    Args:
        *shapelyPolygons: Arbitrary number of Shapely polygons.

    Returns:
        List[Dict] -- List of coordinates representing the geometries of the given polygons.
    """
    geometries = []
    for polygon in shapelyPolygons:
        geometries.append(
            {"type": "polygon", "geometry": list(zip(*polygon.exterior.coords.xy)),}
            if not isinstance(polygon, geometry.MultiPolygon)
            else {
                "type": "multipolygon",
                "geometry": list(
                    map(
                        lambda polygon: list(zip(*polygon.exterior.coords.xy)),
                        list(polygon),
                    )
                ),
            }
        )
    return geometries


def classifyPoints(
    points: List[List[float]],
    communities: List[Union[geometry.Polygon, geometry.MultiPolygon]],
) -> int:
    classifications = {i: [] for i, _ in enumerate(communities)}
    for p in coords_to_points(points):
        for i, community in enumerate(communities):
            if p.within(community):
                classifications[i].append(points_to_coords([p])[0])
    return classifications
