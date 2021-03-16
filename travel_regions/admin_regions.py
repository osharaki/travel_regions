"""
Functions that facilitate the extraction of country and top-level
administrative region data including their geometries.
"""
from ._file_utils import extract_shape
from pathlib import Path
from typing import List, Union, Dict
import os
from shapely.ops import transform
from shapely import geometry
from pycountry_convert import country_alpha2_to_country_name
import pycountry


def get_country_codes(identifier: str) -> "pycountry.db.Country":
    """
    Given a country's "common" name, returns an object containing all its codes
    as attributes. These are ``alpha_2``, ``alpha_3``, ``name``, ``numeric``,
    and ``official_name``.

    Args:
        identifier (str): Country name, alpha-2, or alpha-3 code

    Returns:
        pycountry.db.Country: An object containing the country's identifiers.
    """
    if (country := pycountry.countries.get(name=identifier.capitalize())) is not None:
        return country
    elif (country := pycountry.countries.get(alpha_2=identifier.upper())) is not None:
        return country
    elif (country := pycountry.countries.get(alpha_3=identifier.upper())) is not None:
        return country
    print("Country identifier must be a valid name, alpha-2, or alpha-3 code.")
    return None


def get_countries() -> Dict[str, "pycountry.db.Country"]:
    """
    Retrieves all ISO 3166 countries.

    Returns:
        Dict[str, pycountry.db.Country]: Returns a dict whose keys are country
            names and whose values are objects containing all the country's
            codes as attributes. 
    """
    return pycountry.countries.indices["name"]


def get_admin_regions(country_alpha_2: str):
    # TODO implement function to retrieve a countries admin regions given its name
    pass


def get_admin_region_geoms(
    country_alpha_2: str,
) -> Dict[str, Union[geometry.Polygon, geometry.MultiPolygon]]:
    """
    Returns a country's geometry and that of its top-level administrative
    regions (e.g. states or provinces).

    Args: 
        country_alpha_2 (str): Two-letter country code (i.e. alpha-2) as
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
