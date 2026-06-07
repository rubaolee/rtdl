import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal3728_segment_pair_exact_count_front_door_2026-06-07.md"


class Goal3728SegmentPairExactCountFrontDoorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = RUNTIME.read_text(encoding="utf-8")
        cls.catalog = CATALOG.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.method = cls.runtime.split("def count_prepared_left_exact_intersections", 1)[1].split(
            "def candidate_device_columns",
            1,
        )[0]

    def test_front_door_exists_and_reuses_measured_route(self):
        self.assertIn("def count_prepared_left_exact_intersections", self.runtime)
        self.assertIn("count_prepared_left_grouped_range_direct_intersection(prepared_left)", self.method)
        self.assertIn("rtdl.optix.segment_pair_prepared_left_exact_intersection_count.front_door.v1", self.method)
        self.assertIn('"route": "intersection_program_identity_or_ranged_primitive_records"', self.method)
        self.assertIn('"default_right_range_policy": "identity_range"', self.method)

    def test_front_door_is_contract_shaped_not_app_shaped(self):
        self.assertIn('"primitive": "SEGMENT_PAIR_INTERSECTION_ROWS_2D"', self.method)
        self.assertIn('"output_contract": "scalar_exact_count"', self.method)
        self.assertIn('"backend": "optix"', self.method)
        self.assertIn("RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_MAX_SIZE", self.method)
        self.assertIn("RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_AREA_ENLARGE", self.method)
        for forbidden in ("RayJoin", "county", "soil", "map"):
            self.assertNotIn(forbidden, self.method)

    def test_claim_boundaries_remain_false(self):
        for key in (
            "public_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "release_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "whole_app_acceleration_claim_authorized",
        ):
            self.assertIn(f'"{key}": False', self.method)
        self.assertIn('"experimental_front_door": True', self.method)
        self.assertIn("does not authorize", self.report)

    def test_existing_anyhit_count_route_is_not_replaced(self):
        existing = self.runtime.split("def count_prepared_left(", 1)[1].split(
            "def count_prepared_left_repeated",
            1,
        )[0]
        self.assertIn("OPTIX_SEGMENT_PAIR_COUNT_PREPARED_LEFT_SYMBOL", existing)
        self.assertNotIn("count_prepared_left_grouped_range_direct_intersection", existing)
        self.assertIn("does not change the existing `count_prepared_left(...)` any-hit route", self.report)

    def test_catalog_maps_this_to_existing_segment_pair_primitive(self):
        self.assertIn("rows.segment_pair_intersection_rows_2d", self.catalog)
        self.assertIn("segment_pair_intersection_count", self.catalog)
        self.assertIn("lsi_count", self.catalog)
        self.assertIn("does not create a duplicate primitive family", self.report)


if __name__ == "__main__":
    unittest.main()
