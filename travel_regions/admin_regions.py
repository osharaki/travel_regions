"""
Functions that facilitate the extraction of countries and top-level
administrative regions from Natural Earth Data shapefiles.
"""
from ._file_utils import extract_shape
from pathlib import Path
from typing import List, Union, Dict
import os
from shapely.ops import transform
from shapely import geometry
from pycountry_convert import country_alpha2_to_country_name


def get_admin_regions(
    country_alpha_2: str,
) -> Dict[str, Union[geometry.Polygon, geometry.MultiPolygon]]:
    """
    Returns a country's geometry and that of its top-level administrative
    regions (e.g. states or provinces).

    Args: country_alpha_2 (str): Two-letter country code (i.e. alpha-2) as
        defined in ISO 3166-1

    Raises: Exception: An exception is raised if no country was found that
    corresponds to the provided ISO 3166-1 alpha-2 code.

    Returns: Dict[str, Union[geometry.Polygon, geometry.MultiPolygon]]: The
        geometries of the country and its top-level administrative regions as a
        name:geometry mapping.
    """
    package_directory = os.path.dirname(os.path.abspath(__file__))
    NED_admin1 = extract_shape(
        os.path.join(
            Path(package_directory).parent, "data", "ne_10m_admin_1_states_provinces",
        ),
        country_alpha_2,
    )
    if not NED_admin1.empty:
        regions = {
            country_alpha2_to_country_name(country_alpha_2.upper()): transform(
                lambda x, y: (y, x), NED_admin1.geometry.cascaded_union
            )
        }
        for region in NED_admin1.gn_name.values:
            region_geom = NED_admin1[
                NED_admin1.gn_name == region
            ].geometry.cascaded_union
            region_geom = transform(lambda x, y: (y, x), region_geom)
            regions[region] = region_geom
        return regions

    else:
        raise Exception(
            f'No country with ISO 3166-1 alpha-2 code "{country_alpha_2}" found.'
        )
