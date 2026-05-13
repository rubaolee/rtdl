from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1937_fixed_radius_repeat3_pod_perf_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1937_fixed_radius_repeat3_pod" / "fixed_radius_524288_repeat3.json"
LOG = ROOT / "docs" / "reports" / "goal1937_fixed_radius_repeat3_pod" / "run.log"


class Goal1937FixedRadiusRepeat3PodPerfTest(unittest.TestCase):
    def test_artifact_has_repeat3_seconds_scale_positive_rows(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(len(payload["results"]), 12)
        for row in payload["results"]:
            with self.subTest(app=row["app"], partner=row["partner"]):
                self.assertEqual(row["query_count"], 524288)
                self.assertEqual(row["search_count"], 524288)
                self.assertEqual(row["status"], "pass")
                forward = row["forward"]
                v18 = forward["v1_8_prepared_optix"]
                v2 = forward["v2_prepared_native_optix_partner"]
                self.assertGreaterEqual(v18["median_s"], 1.0)
                self.assertLess(v2["median_s"], 0.003)
                self.assertLess(forward["v2_vs_v1_8_prepared_ratio"], 0.001)
                self.assertNotEqual(v18["min_s"], v18["max_s"])
                self.assertTrue(forward["parity"]["counts_match"])
                self.assertTrue(forward["parity"]["summary_match"])

    def test_log_shows_visible_progress_and_repeat3(self) -> None:
        text = LOG.read_text(encoding="utf-8")

        self.assertIn("[goal1925] start app=facility_knn_assignment", text)
        self.assertIn("repeat=3", text)
        self.assertIn("iter=3", text)
        self.assertIn('"status": "pass"', text)

    def test_report_preserves_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: fixed-radius-repeat3-evidence-collected-release-still-blocked", text)
        self.assertIn("resolves the Goal1936 single-repeat caveat", text)
        self.assertIn("do not authorize v2.0", text)
        self.assertIn("whole-app speedup", text)
        self.assertIn("package-install", text)


if __name__ == "__main__":
    unittest.main()
