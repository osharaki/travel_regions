"""
Functions that facilitate the extraction of countries and top-level
administrative regions from Natural Earth Data shapefiles.
"""
from ._file_utils import extract_shape
from pathlib import Path
from typing import List, Union
import os
from shapely.ops import transform
from shapely import geometry


def get_admin_regions(
    country_alpha_2: str,
) -> Union[List[geometry.Polygon], List[geometry.MultiPolygon]]:
    """
    Returns a country's geometry or that of its top-level administrative regions
    (e.g. states or provinces) depending on the `level` specified.

    Args: country_alpha_2 (str): Two-letter country code as defined in ISO
        3166-1

    Raises: Exception: An exception is raised if the provided alpha-2 country
        code did not yield any results.

    Returns: Union[List[geometry.Polygon],List[geometry.MultiPolygon]]: The
        geometries of both the country (at position 0) and its top-level
        administrative regions.
    """
    package_directory = os.path.dirname(os.path.abspath(__file__))
    NED_admin1 = extract_shape(
        os.path.join(
            Path(package_directory).parent, "data", "ne_10m_admin_1_states_provinces",
        ),
        country_alpha_2,
    )
    # TODO Administrative regions should be identifiable by name
    if not NED_admin1.empty:
        regions = [transform(lambda x, y: (y, x), NED_admin1.geometry.cascaded_union)]
        for region in NED_admin1.gn_name.values:
            region = NED_admin1[NED_admin1.gn_name == region].geometry.cascaded_union
            region = transform(lambda x, y: (y, x), region)
            regions.append(region)
        return regions

    else:
        raise Exception(
            f'No country with code "{country_alpha_2}" found. Country code must be 2 letters as specified by ISO 3166-1 alpha-2'
        )
