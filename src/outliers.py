from typing import Dict, List, Tuple
from haversine import haversine
from scipy import stats
import operator
from functools import reduce
from math import sqrt


def detect_outliers_z_score(data, threshold=3) -> List[Tuple[int, float]]:
    centroid = find_centroid(data)
    distancesFromCenter = [haversine(point, centroid) for point in data]
    zScores: float = stats.zscore(distancesFromCenter)
    outliers: List[Tuple[int, float]] = list(
        filter(lambda x: abs(x[1]) > threshold, enumerate(zScores))
    )
    return outliers


def find_centroid(data):
    x, y = zip(*data)
    size = len(x)
    xCenter = sum(x) / size
    yCenter = sum(y) / size
    return (xCenter, yCenter)


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
    dimesionsSubtracted = map(
        lambda dimension: reduce(operator.sub, dimension), dimensions
    )
    distance = sqrt(
        sum([dimensionSubtracted ** 2 for dimensionSubtracted in dimesionsSubtracted])
    )
    return distance
