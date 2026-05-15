import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1863_segment_polygon_hitcount_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal2054_segment_polygon_hitcount_prepared_scaling_l4_2026-05-15.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2054_segment_polygon_hitcount_cupy_l4_8192_prepared_capacity262144.json"
ARTIFACT_16384 = ROOT / "docs" / "reports" / "goal2054_segment_polygon_hitcount_cupy_l4_16384_prepared_capacity1048576.json"
ARTIFACT_32768 = ROOT / "docs" / "reports" / "goal2054_segment_polygon_hitcount_cupy_l4_32768_prepared_capacity4194304.json"
ARTIFACT_65536 = ROOT / "docs" / "reports" / "goal2054_segment_polygon_hitcount_cupy_l4_65536_prepared_capacity16777216.json"


class Goal2054SegmentPolygonHitcountPreparedScalingL4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.artifact_16384 = json.loads(ARTIFACT_16384.read_text(encoding="utf-8"))
        cls.artifact_32768 = json.loads(ARTIFACT_32768.read_text(encoding="utf-8"))
        cls.artifact_65536 = json.loads(ARTIFACT_65536.read_text(encoding="utf-8"))

    def test_runner_can_skip_one_shot_baseline_for_large_prepared_scaling(self):
        self.assertIn('parser.add_argument("--skip-one-shot-baseline"', self.script)
        self.assertIn("v1_8_one_shot_native_optix_hitcount_rows skipped", self.script)
        self.assertIn("explicit --skip-one-shot-baseline for large prepared-only scaling", self.script)

    def test_artifact_records_skipped_one_shot_and_prepared_parity(self):
        self.assertEqual(self.artifact["status"], "pass")
        self.assertEqual(self.artifact["count"], 8192)
        self.assertEqual(self.artifact["output_capacity"], 262144)
        self.assertEqual(self.artifact["source_commit_label"], "4e26c379-plus-goal2054-skip-one-shot")
        self.assertTrue(self.artifact["baseline"]["skipped"])
        self.assertIsNone(self.artifact["baseline"]["query_summary"])
        self.assertTrue(self.artifact["parity"]["strict_counts_match"])
        self.assertEqual(self.artifact["prepared_baseline"]["row_count"], 8192)

    def test_prepared_v2_beats_prepared_v1_8_same_contract_row(self):
        prepared = self.artifact["partners"]["cupy"]["goal1886_prepared_reuse"]
        self.assertLess(prepared["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertIsNone(prepared["query_median_ratio_vs_v1_8_one_shot_native"])
        self.assertTrue(prepared["prepared_scene_reused"])
        self.assertTrue(prepared["witness_output_columns_reused"])
        self.assertEqual(prepared["row_count"], 8192)

    def test_16384_artifact_extends_prepared_scaling_evidence(self):
        self.assertEqual(self.artifact_16384["status"], "pass")
        self.assertEqual(self.artifact_16384["count"], 16384)
        self.assertEqual(self.artifact_16384["output_capacity"], 1048576)
        self.assertTrue(self.artifact_16384["baseline"]["skipped"])
        self.assertTrue(self.artifact_16384["parity"]["strict_counts_match"])
        prepared = self.artifact_16384["partners"]["cupy"]["goal1886_prepared_reuse"]
        self.assertLess(prepared["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertEqual(prepared["row_count"], 16384)

    def test_32768_artifact_extends_prepared_scaling_evidence(self):
        self.assertEqual(self.artifact_32768["status"], "pass")
        self.assertEqual(self.artifact_32768["count"], 32768)
        self.assertEqual(self.artifact_32768["output_capacity"], 4194304)
        self.assertTrue(self.artifact_32768["baseline"]["skipped"])
        self.assertTrue(self.artifact_32768["parity"]["strict_counts_match"])
        prepared = self.artifact_32768["partners"]["cupy"]["goal1886_prepared_reuse"]
        self.assertLess(prepared["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertEqual(prepared["row_count"], 32768)

    def test_65536_artifact_extends_prepared_scaling_evidence(self):
        self.assertEqual(self.artifact_65536["status"], "pass")
        self.assertEqual(self.artifact_65536["count"], 65536)
        self.assertEqual(self.artifact_65536["output_capacity"], 16777216)
        self.assertTrue(self.artifact_65536["baseline"]["skipped"])
        self.assertTrue(self.artifact_65536["parity"]["strict_counts_match"])
        prepared = self.artifact_65536["partners"]["cupy"]["goal1886_prepared_reuse"]
        self.assertLess(prepared["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertEqual(prepared["row_count"], 65536)

    def test_report_blocks_overclaims(self):
        required = [
            "about 8.2x faster",
            "about 16.3x faster",
            "about 44.7x faster",
            "about 78.6x faster",
            "nearly flat over these sizes",
            "same-contract v1.8 prepared OptiX row path",
            "not a broad all-app speedup claim",
            "v2.0 release readiness",
            "broad RT-core speedup",
            "exact polygon overlay/Jaccard acceleration",
            "exact Hausdorff witness bridge",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
