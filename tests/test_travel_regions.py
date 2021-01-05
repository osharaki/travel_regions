#!/usr/bin/env python

"""Tests for `travel_regions` package."""


import unittest

# from travel_regions import travel_regions
from travel_regions import TravelRegions


class TestTravel_regions(unittest.TestCase):
    """Tests for `travel_regions` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.travel_regions = TravelRegions()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_nearest_neighbors(self):
        nearest_node = self.travel_regions.get_nearest_node((40.781459, -73.966551))
        self.assertIsNotNone(nearest_node)
        self.assertEqual(nearest_node.id, "45")

    def test_points_to_regions(self):
        points = [
            [-14.269798, -40.821783],
            [-24.452236, -48.556158],
            [-38.826944, -71.847173],
        ]
        region_mappings = self.travel_regions.points_to_regions(points)
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
        l2_regions = self.travel_regions.regions[2]
        neighboring_regions = l2_regions[1].get_neighbors(l2_regions)
        self.assertIsNotNone(neighboring_regions)
        self.assertEqual(
            set(["22", "27"]), set([region.id for region in neighboring_regions])
        )

    def test_get_continent_regions(self):
        regions_south_america = self.travel_regions.get_continent_regions("SA")
        self.assertIsNotNone(regions_south_america)
        self.assertEqual(len(regions_south_america), 227)

    def test_find_node(self):
        matching_nodes = self.travel_regions.find_node("Springfield")
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
        region = self.travel_regions.get_region("22")
        self.assertIsNotNone(region)
        self.assertEqual(region.id, "22")

    def test_find_region(self):
        matching_regions = self.travel_regions.find_region(["Paraguay", "Brazil"])
        self.assertIsNotNone(matching_regions)
        self.assertEqual(
            set(["415", "3100", "10", "384", "22", "23", "49"]),
            set([matching_region.id for matching_region in matching_regions]),
        )
