import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
REPORT = ROOT / "docs" / "reports" / "goal3729_rayjoin_lsi_exact_count_front_door_adoption_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3729_rayjoin_lsi_exact_count_front_door_app_a5000" / "summary.json"


class Goal3729RayJoinLsiExactCountFrontDoorAdoptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        start = cls.app.index('elif workload == "lsi":')
        end = cls.app.index("from rtdsl.optix_runtime import pack_points", start)
        cls.lsi_block = cls.app[start:end]

    def test_lsi_prepared_count_uses_exact_count_front_door(self):
        self.assertIn("prepare_segment_pair_left_set_optix", self.lsi_block)
        self.assertIn("prepared.count_prepared_left_exact_intersections(prepared_left)", self.lsi_block)
        self.assertIn('stability_value=lambda value: int(value["count"])', self.lsi_block)
        self.assertIn('"segment_pair_count_route"', self.lsi_block)
        self.assertIn('"front_door_schema"', self.lsi_block)
        self.assertIn("count_prepared_left_exact_intersections", self.report)

    def test_lsi_rows_and_unprepared_fallback_are_unchanged(self):
        self.assertIn("prepared.run_raw(packed_left)", self.lsi_block)
        self.assertIn("prepared.count(packed_left)", self.lsi_block)
        self.assertIn("Row-producing LSI mode still uses `prepared.run_raw(...)`", self.report)
        self.assertIn("Unprepared count fallback still uses `prepared.count(packed_left)`", self.report)

    def test_route_metadata_is_generic_and_claim_bounded(self):
        for key in (
            '"primitive"',
            '"output_contract"',
            '"route"',
            '"native_symbol"',
            '"right_group_count"',
            '"experimental_front_door"',
            '"public_speedup_claim_authorized"',
        ):
            self.assertIn(key, self.lsi_block)
        self.assertIn("does not", self.report)
        self.assertIn("Add a RayJoin-specific native symbol", self.report)
        self.assertIn("Authorize public RayJoin speedup claims", self.report)

    def test_pod_artifact_confirms_app_runtime_route(self):
        summary = self.artifact["summary"]
        route = summary["segment_pair_count_route"]
        timings = self.artifact["native_phase_timings"]
        self.assertEqual("a546fa58", self.artifact["goal3729_probe"]["git_commit"][:8])
        self.assertEqual(20860, int(summary["intersection_count"]))
        self.assertTrue(summary["prepared_left_for_count"])
        self.assertEqual(
            "rtdl.optix.segment_pair_prepared_left_exact_intersection_count.front_door.v1",
            route["front_door_schema"],
        )
        self.assertEqual("SEGMENT_PAIR_INTERSECTION_ROWS_2D", route["primitive"])
        self.assertEqual("scalar_exact_count", route["output_contract"])
        self.assertEqual("count_prepared_left_grouped_range_direct_intersection", timings["mode"])
        self.assertEqual(326193, int(route["right_group_count"]))
        self.assertLess(float(self.artifact["phases_sec"]["prepared_query_sec"]), 0.001)
        for value in self.artifact["goal3729_probe"]["claim_boundary"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
