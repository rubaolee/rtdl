import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3719_rayjoin_lsi_native_repeated_count_diagnostic_pod_validation_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3718_segment_pair_prepared_left_repeated_count_a5000" / "summary.json"


class Goal3719RayJoinLsiNativeRepeatedCountDiagnosticPodValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_report_documents_diagnostic_boundary(self):
        self.assertIn("diagnostic-only", self.report)
        self.assertIn("does not authorize", self.report)
        self.assertIn("RTDL-beats-RayJoin claims", self.report)
        self.assertIn("RayJoin paper reproduction claims", self.report)
        self.assertIn("True zero-copy claims", self.report)

    def test_pod_artifact_counts_match_same_source_rayjoin_lsi(self):
        comparison = self.artifact["comparison"]
        self.assertTrue(comparison["counts_match"])
        self.assertEqual(20860, int(comparison["rayjoin_lsi_intersections"]))
        self.assertEqual(20860, int(comparison["rtdl_count"]))
        self.assertEqual(20860, int(self.artifact["rtdl_python_front_door"]["count"]))
        self.assertEqual(20860, int(self.artifact["rtdl_native_repeated"]["count"]))

    def test_native_repeated_closes_python_overhead_hypothesis(self):
        comparison = self.artifact["comparison"]
        self.assertLess(float(comparison["python_front_door_over_native_repeated_ratio"]), 1.01)
        self.assertGreater(float(comparison["python_front_door_over_native_repeated_ratio"]), 0.99)
        self.assertIn("Python/ctypes overhead is negligible", self.report)
        self.assertIn("native OptiX route", self.report)

    def test_native_repeated_remains_slower_than_rayjoin_without_overclaim(self):
        comparison = self.artifact["comparison"]
        self.assertLess(float(comparison["native_repeated_speedup_vs_rayjoin"]), 1.0)
        self.assertIn("RTDL native route remains slower than RayJoin", self.report)
        boundary = self.artifact["claim_boundary"]
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            self.assertFalse(boundary[key], key)

    def test_report_names_next_native_route_work(self):
        self.assertIn("launch shape", self.report)
        self.assertIn("SBT layout", self.report)
        self.assertIn("payload size", self.report)
        self.assertIn("counter update strategy", self.report)
        self.assertIn("app-agnostic changes", self.report)


if __name__ == "__main__":
    unittest.main()
