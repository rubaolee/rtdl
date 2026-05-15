import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1869_road_hazard_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal2062_road_hazard_prepared_only_scaling_l4_2026-05-15.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2062_road_hazard_cupy_l4_8192_prepared_only.json"


class Goal2062RoadHazardPreparedOnlyScalingL4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_runner_exposes_honest_skip_one_shot_mode(self):
        self.assertIn('parser.add_argument("--skip-one-shot-baseline"', self.script)
        self.assertIn("v1_8_one_shot_native_optix_road_hazard_rows skipped", self.script)
        self.assertIn("explicit --skip-one-shot-baseline for large prepared-only scaling", self.script)
        self.assertIn("def _median_ratio", self.script)

    def test_artifact_records_prepared_only_8192_success(self):
        self.assertEqual(self.artifact["status"], "pass")
        self.assertEqual(self.artifact["count"], 8192)
        self.assertEqual(self.artifact["output_capacity"], 100663296)
        self.assertEqual(self.artifact["source_commit_label"], "05fbfccb-plus-goal2062-road-skip-one-shot")
        self.assertTrue(self.artifact["baseline"]["skipped"])
        self.assertIsNone(self.artifact["baseline"]["query_summary"])
        self.assertTrue(self.artifact["parity"]["strict_priority_flags_match"])

    def test_prepared_v2_beats_prepared_v1_8_and_preserves_zero_copy_metadata(self):
        cupy = self.artifact["partners"]["cupy"]
        prepared = cupy["goal1889_prepared_reuse"]
        self.assertLess(cupy["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertLess(prepared["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertIsNone(prepared["query_median_ratio_vs_v1_8_one_shot_native"])
        self.assertTrue(prepared["prepared_scene_reused"])
        self.assertTrue(prepared["witness_output_columns_reused"])
        self.assertTrue(prepared["metadata"]["whole_app_true_zero_copy_authorized"])

    def test_report_blocks_overclaims(self):
        required = [
            "about 8.9x faster",
            "same-contract v1.8 prepared OptiX row path",
            "one-shot baseline as skipped",
            "v2.0 release readiness",
            "broad all-app speedup",
            "broad RT-core speedup",
            "one-shot speedup for the skipped 8192 baseline",
            "`accept-with-boundary`",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
