# http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/
from typing import Dict, List, Tuple, Union
from haversine import haversine
from scipy import stats
from functools import reduce
from math import sqrt
import operator
import shapely.geometry as geometry
import matplotlib.pyplot as pl
import alphashape
import time
import numpy as np

from typing import Dict, List, Tuple
from descartes import PolygonPatch
from geovoronoi import voronoi_regions_from_coords, coords_to_points, points_to_coords
from shapely.ops import cascaded_union


def generate_concave_hull(points: List[Tuple[float, float]], visualize=False):
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


def generate_convex_hull(points: List[Tuple[float, float]]):
    point_collection = geometry.MultiPoint(points)
    pp = PolygonPatch(point_collection.convex_hull)
    return pp._path.vertices.tolist()


def generate_constrained_voronoi_diagram(
    points: List[List[float]],
    containing_area: geometry.Polygon,
    communities: List[List[List[float]]] = None,
) -> Union[List[List[geometry.Polygon]], List[geometry.Polygon]]:
    """
    Generates a Voronoi diagram from a list of points that is constrained within a given area. If `communities` is provided, this method further assigns the generated Voronoi regions to their corresponding communities. All coordinates must be given as latitude followed by longitude. All polygons are returned as Shapely polygons.

    Args:
        points (List[List[float]]): A list of coordinates.
        containing_area (geometry.Polygon): A Shapely polygon that forms the boundary of the generated Voronoi diagram. All `points` must be contained within this area.
        communities (List[List[List[float]]], optional): An optional mapping that associates each community with the points (provided as coordinates) belonging to it. Defaults to None.

    Returns:
        Union[List[List[geometry.Polygon]], List[geometry.Polygon]]: The Voronoi diagram as a list of Shapely polygons. If `communities` is provided, the generated Voronoi regions will further be organized and returned as a list of communities of the form List[List[geometry.Polygon]], where each community contains the Voronoi regions surrounding the nodes that form it.
    """
    points = np.array(points)

    coords = coords_to_points(points)
    # use only the points inside the geographic area
    contained_points = []
    community_tracker = (
        []
    )  # HACK: Keeps track of which points aren't inside of the bounding area so that community associations can be maintained
    for p in coords:  # converts to shapely Point
        if p.within(containing_area):
            contained_points.append(p)
            community_tracker.append(True)
        else:
            community_tracker.append(False)
    if len(contained_points) < 5:
        print("Bounding area must contain at least 4 nodes from region model")
        return []
    points = points_to_coords(contained_points)
    poly_shapes, pts, poly_to_pt_assignments = voronoi_regions_from_coords(
        points, containing_area
    )
    if communities:
        polygons = []
        pt_to_poly_assignments = [None] * len(community_tracker)
        j = 0
        for i, point_inside in enumerate(community_tracker):
            if point_inside:
                pt_to_poly_assignments[i] = poly_shapes[j]
                j += 1
        for i, c in enumerate(communities):
            start = end if i != 0 else 0
            end = start + len(communities[i])
            polygons.append(list(filter(None, pt_to_poly_assignments[start:end])))
        return polygons
    return poly_shapes


def merge_regions(
    *voronoi_communities: List[geometry.Polygon],
) -> Union[List[geometry.MultiPolygon], List[geometry.Polygon]]:
    """
    This function takes an arbitrary number of communities, each represented as a list of Shapely polygons and combines each community's regions into a single unified region.

    Args:
        *voronoi_communities: Arbitrary number of communities, each represented as a list of Shapely polygons.

    Returns:
        Union[List[geometry.MultiPolygon], List[geometry.Polygon]]: Communities each represented by either a Shapely Polygon or MultiPolygon depending on whether the community's original regions were spatially contiguous.
    """
    merged_regions = []
    for community_regions in voronoi_communities:
        # cascaded_union() turns empty lists into objects of type GeometryCollection in the
        # list of merged regions, which later raise an error in TravelRegions.extract_geometries
        if community_regions:
            merged_region = cascaded_union(community_regions)
            merged_regions.append(merged_region)
        else:
            merged_regions.append([])
    return merged_regions


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
def extract_geometries(*shapely_polygons) -> List[Dict]:
    """
    Given one or more Shapely polygons/multipolygons, extracts their geometries as lists of coordinates.

    Args:
        *shapely_polygons: Arbitrary number of Shapely polygons.

    Returns:
        List[Dict] -- List of coordinates representing the geometries of the given polygons.
    """
    geometries = []
    for polygon in shapely_polygons:
        if polygon:
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
        else:
            geometries.append({})
    return geometries


def classify_points(
    points: List[List[float]],
    communities: List[Union[geometry.Polygon, geometry.MultiPolygon]],
) -> Dict[int, np.array]:
    classifications = {i: [] for i, _ in enumerate(communities)}
    for p in coords_to_points(points):
        for i, community in enumerate(communities):
            if p.within(community):
                classifications[i].append(points_to_coords([p])[0])
    return classifications


def detect_outliers_z_score(data, threshold=3) -> List[Tuple[int, float]]:
    centroid = find_centroid(data)
    distances_from_center = [haversine(point, centroid) for point in data]
    with np.errstate(invalid="ignore", divide="ignore"):
        z_scores: float = stats.zscore(distances_from_center)
    outliers: List[Tuple[int, float]] = list(
        filter(lambda x: abs(x[1]) > threshold, enumerate(z_scores))
    )
    return outliers


def find_centroid(data):
    x, y = zip(*data)
    size = len(x)
    x_center = sum(x) / size
    y_center = sum(y) / size
    return (x_center, y_center)


def find_distance(a, b):
    """
    Finds Eucledian distance between two points.

    Args:
        a (List[float]): Coordinates of point a.
        b (List[float]): Coordinates of point b.

    Returns:
        float: Distance between a and b.
    """
    dimensions = zip(a, b)
    dimensions_subtracted = map(
        lambda dimension: reduce(operator.sub, dimension), dimensions
    )
    distance = sqrt(
        sum(
            [
                dimension_subtracted ** 2
                for dimension_subtracted in dimensions_subtracted
            ]
        )
    )
    return distance
