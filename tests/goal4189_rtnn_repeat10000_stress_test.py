import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4189_rtnn_repeat10000_stress_rtx4000ada"
PAYLOAD_PATH = ARTIFACT_DIR / "rtnn_prepared_optix_65536_repeat10000.stdout.json"
STDERR_PATH = ARTIFACT_DIR / "rtnn_prepared_optix_65536_repeat10000.stderr.txt"
REPORT_PATH = ROOT / "docs" / "reports" / "goal4189_rtnn_repeat10000_stress_rtx4000ada_2026-06-09.md"


class Goal4189RtnnRepeat10000StressTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
        cls.report = REPORT_PATH.read_text(encoding="utf-8")

    def test_repeat_samples_clear_second_level_floor(self) -> None:
        runner = self.payload["runner_payload"]
        runs = runner["elapsed_runs_sec"]

        self.assertEqual(self.payload["repeat"], 10000)
        self.assertEqual(runner["repeat"], 10000)
        self.assertEqual(len(runs), 10000)
        self.assertGreater(sum(runs), 1.0)
        self.assertTrue(math.isclose(sum(runs), 1.704869568347931, rel_tol=1e-12, abs_tol=1e-12))
        self.assertLess(runner["elapsed_median_sec"], 0.001)
        self.assertEqual(runner["elapsed_min_sec"], min(runs))
        self.assertEqual(runner["elapsed_max_sec"], max(runs))
        self.assertTrue(runner["ok"])

    def test_route_and_claim_boundary_are_unchanged(self) -> None:
        self.assertEqual(self.payload["mode"], "prepared_optix_ranked_summary")
        self.assertEqual(self.payload["contract"], "prepared 3-D fixed-radius bounded ranked-summary aggregate")
        self.assertEqual(self.payload["point_count"], 65536)
        self.assertEqual(self.payload["query_batch_size"], 65536)
        self.assertEqual(self.payload["radius"], 0.02)
        self.assertEqual(self.payload["k"], 50)

        boundary = self.payload["claim_boundary"]
        for key, value in boundary.items():
            if key == "benchmark_app":
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_report_and_artifact_do_not_overclaim(self) -> None:
        self.assertEqual(STDERR_PATH.read_text(encoding="utf-8"), "")
        self.assertIn("No runtime code is", self.report)
        self.assertIn("changed.", self.report)
        self.assertIn("does not authorize public speedup", self.report)
        self.assertIn("native engine is not customized for RTNN semantics", self.report)
        self.assertNotIn("release authorized", self.report.lower())


if __name__ == "__main__":
    unittest.main()
