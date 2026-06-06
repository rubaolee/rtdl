import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3647_rayjoin_lsi_prepared_left_route_adoption_2026-06-06.md"
APP_SMOKE = ROOT / "docs" / "reports" / "goal3647_rayjoin_prepared_left_app_a5000" / "app_smoke_summary.json"
SAME_SLICE = ROOT / "docs" / "reports" / "goal3647_rayjoin_prepared_left_app_a5000" / "same_slice_summary.json"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"


class Goal3647RayJoinLsiPreparedLeftRouteAdoptionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.app_smoke = json.loads(APP_SMOKE.read_text(encoding="utf-8"))
        cls.same_slice = json.loads(SAME_SLICE.read_text(encoding="utf-8"))
        cls.app = APP.read_text(encoding="utf-8")

    def test_app_smoke_uses_prepared_left_native_symbol(self):
        self.assertEqual(self.app_smoke["goal3647_probe"]["git_commit"][:8], "fd7abe1d")
        self.assertEqual(
            self.app_smoke["execution_route"],
            "prepared_optix_left_id_dense_count_prepared_left_reuse",
        )
        self.assertEqual(
            self.app_smoke["dense_left_id_count_columns"]["native_symbol"],
            "rtdl_optix_prepared_segment_pair_left_id_count_prepared_left_device_columns",
        )
        reuse = self.app_smoke["packed_left_reuse"]
        self.assertTrue(reuse["native_prepared_left_set_enabled"])
        self.assertTrue(reuse["native_prepared_left_set_paid_once"])
        self.assertFalse(reuse["query_pack_paid_in_call"])

    def test_same_slice_lsi_count_matches_and_is_faster_than_rayjoin_query_timing(self):
        self.assertEqual(self.same_slice["rtdl_commit"][:8], "fd7abe1d")
        lsi = next(row for row in self.same_slice["comparisons"] if row["workload"] == "lsi")
        self.assertEqual(lsi["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(lsi["rayjoin_visible_count"], 269)
        self.assertEqual(lsi["rtdl_count"], 269)
        self.assertLess(lsi["rtdl_over_rayjoin_query_ratio"], 1.0)
        self.assertLess(lsi["rtdl_prepared_query_ms_median"], lsi["rayjoin_query_ms_reported_median"])
        self.assertGreater(
            lsi["rayjoin_query_ms_reported_median"] / lsi["rtdl_prepared_query_ms_median"],
            1.2,
        )

    def test_source_and_report_keep_boundaries_visible(self):
        self.assertIn("left_id_count_prepared_left_device_columns", self.app)
        self.assertIn("prepare_segment_pair_left_set_optix", self.app)
        self.assertIn("full RayJoin paper reproduction claims", self.report)
        self.assertIn("PIP is not part of this Goal3647 claim", self.report)
        for flag, value in self.app_smoke["claim_boundary"].items():
            self.assertFalse(value, flag)
        for flag, value in self.same_slice["claim_boundary"].items():
            self.assertFalse(value, flag)


if __name__ == "__main__":
    unittest.main()
