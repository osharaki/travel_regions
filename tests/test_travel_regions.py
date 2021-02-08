#!/usr/bin/env python

"""Tests for `travel_regions` package."""


import unittest
import os

from travel_regions import TravelRegions
import travel_regions


class TestTravel_regions(unittest.TestCase):
    """Tests for `travel_regions` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

        self.travel_regions_instances = list(
            filter(None, TestTravel_regions.travel_regions_instances)
        )

    @classmethod
    def setUpClass(cls):
        super(TestTravel_regions, cls).setUpClass()

        # TravelRegions can be instantiated in one of 4 ways depending on which
        # constructor parameters receive arguments. The following flags can be
        # used to toggle which of the four instantiation methods to use when
        # running testcases.
        travel_regions_default = True
        travel_regions_model = True
        travel_regions_boundaries = True
        travel_regions_model_boundaries = True

        cls.travel_regions_default = TravelRegions() if travel_regions_default else None
        cls.travel_regions_model = (
            TravelRegions(
                region_model=os.path.join(
                    "data",
                    "communities_-1__with_distance_multi-level_geonames_cities_7.csv",
                ),
                levels=4,
            )
            if travel_regions_model
            else None
        )
        cls.travel_regions_boundaries = (
            TravelRegions(
                *[
                    os.path.join("data", "cutouts", "eu_af_as_au.geojson"),
                    os.path.join("data", "cutouts", "americas.geojson"),
                    os.path.join("data", "cutouts", "nz.geojson"),
                ]
            )
            if travel_regions_boundaries
            else None
        )
        cls.travel_regions_model_boundaries = (
            TravelRegions(
                *[
                    os.path.join("data", "cutouts", "eu_af_as_au.geojson"),
                    os.path.join("data", "cutouts", "americas.geojson"),
                    os.path.join("data", "cutouts", "nz.geojson"),
                ],
                region_model=os.path.join(
                    "data",
                    "communities_-1__with_distance_multi-level_geonames_cities_7.csv",
                ),
                levels=4,
            )
            if travel_regions_model_boundaries
            else None
        )
        cls.travel_regions_instances = [
            cls.travel_regions_default,
            cls.travel_regions_model,
            cls.travel_regions_boundaries,
            cls.travel_regions_model_boundaries,
        ]

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_nearest_neighbors(self):
        for travel_regions in self.travel_regions_instances:
            nearest_node = travel_regions.get_nearest_node((40.781459, -73.966551))
            self.assertIsNotNone(nearest_node)
            self.assertEqual(nearest_node.id, "45")

    def test_points_to_regions(self):
        points = [
            [-14.269798, -40.821783],
            [-24.452236, -48.556158],
            [-38.826944, -71.847173],
        ]
        for travel_regions in self.travel_regions_instances:
            region_mappings = travel_regions.points_to_regions(points)
            region_IDs = []
            for k, v in region_mappings.items():
                if v:
                    region_IDs.append(k)
            self.assertIsNotNone(region_mappings)
            self.assertEqual(
                set(["10", "22", "26", "24", "356", "3154", "3113", "40", "415"]),
                set(region_IDs),
            )

    def test_get_neighbors(self):
        for travel_regions in self.travel_regions_instances:
            l2_regions = travel_regions.regions[2]
            neighboring_regions = travel_regions.get_region("23").get_neighbors(
                l2_regions
            )
            self.assertIsNotNone(neighboring_regions)
            self.assertEqual(
                set(["22", "27"]), set([region.id for region in neighboring_regions])
            )

    def test_get_country_regions(self):
        for travel_regions in self.travel_regions_instances:
            DE_regions = travel_regions.get_country_regions("de", 3)
            self.assertEqual(len(DE_regions), 974)
            self.assertTrue(
                all(
                    [
                        "Germany" in travel_regions.get_region(str(region_id)).countries
                        for region_id in DE_regions
                    ]
                )
            )

    def test_get_continent_regions(self):
        for travel_regions in self.travel_regions_instances:
            regions_south_america = travel_regions.get_continent_regions("SA")
            self.assertIsNotNone(regions_south_america)
            self.assertEqual(len(regions_south_america), 224)

    def test_find_node(self):
        for travel_regions in self.travel_regions_instances:
            matching_nodes = travel_regions.find_node("Springfield")
            self.assertIsNotNone(matching_nodes)
            self.assertEqual(
                set(
                    [
                        "380",
                        "575",
                        "1842",
                        "2293",
                        "3749",
                        "4016",
                        "5882",
                        "5971",
                        "6323",
                        "7751",
                        "8060",
                    ]
                ),
                set([matching_node.id for matching_node in matching_nodes]),
            )

    def test_get_region(self):
        for travel_regions in self.travel_regions_instances:
            region = travel_regions.get_region("22")
            self.assertIsNotNone(region)
            self.assertEqual(region.id, "22")

    def test_find_region(self):
        for travel_regions in self.travel_regions_instances:
            matching_regions = travel_regions.find_region(["Paraguay", "Brazil"])
            self.assertIsNotNone(matching_regions)
            self.assertEqual(
                set(["415", "3100", "10", "384", "22", "23", "49"]),
                set([matching_region.id for matching_region in matching_regions]),
            )
