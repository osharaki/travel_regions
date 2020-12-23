from typing import Dict, List, Tuple
from haversine import haversine
from scipy import stats
import operator
from functools import reduce
from math import sqrt
import numpy as np


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
