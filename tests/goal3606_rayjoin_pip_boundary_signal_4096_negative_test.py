from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3606_rayjoin_pip_boundary_signal_4096_negative_2026-06-06.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3606_rayjoin_pip_boundary_signal_4096_negative_a5000" / "summary.json"


class Goal3606RayJoinPipBoundarySignal4096NegativeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_records_4096_chain_negative_probe(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3606.rayjoin_pip_boundary_signal_4096_negative.v1")
        self.assertEqual(payload["goal"], 3606)
        self.assertEqual(payload["git_commit"], "df9c355a3f9a37c72a1b8aba1b19a2f3d3e80fd7")
        self.assertEqual(payload["chain_count"], 4096)
        self.assertEqual(payload["start"], 256)
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertFalse(payload["all_tolerances_match_exact"])

    def test_no_tested_tolerance_matches_exact(self):
        rows = self.payload["rows"]
        self.assertEqual([row["crossing_tolerance"] for row in rows], [0.0, 0.001, 0.0001, 1e-05, 1e-06])
        for row in rows:
            with self.subTest(tolerance=row["crossing_tolerance"]):
                self.assertFalse(row["matches_exact"])
                self.assertEqual(row["exact_row_count"], 11316)
                self.assertGreater(row["selected_point_count"], 0)
                self.assertEqual(row["selected_missed_extra_point_count"], 1)
                self.assertEqual(row["selected_false_positive_point_count"], 6)

    def test_report_blocks_boundary_signal_default_route(self):
        self.assertIn("not robust enough for default routing", self.report)
        self.assertIn("CuPy dense CUDA-core scalar count", self.report)
        self.assertIn("future fused generic exact closed-shape membership/count primitive", self.report)
        self.assertIn("does not authorize public claims", self.report)
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
