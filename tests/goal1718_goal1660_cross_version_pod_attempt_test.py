import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1718_goal1660_cross_version_pod_attempt_2026-05-12.md"
RAW = ROOT / "docs" / "reports" / "goal1718_goal1660_cross_version_raw_2026-05-12.json"


class Goal1718Goal1660CrossVersionPodAttemptTest(unittest.TestCase):
    def test_raw_runner_completed_all_invocations(self):
        payload = json.loads(RAW.read_text(encoding="utf-8"))
        self.assertTrue(payload["done"])
        self.assertEqual(payload["planned_row_count"], 28)
        self.assertEqual(payload["expected_invocation_count"], 56)
        self.assertEqual(payload["completed_invocation_count"], 56)

    def test_current_candidate_has_all_planned_artifacts(self):
        payload = json.loads(RAW.read_text(encoding="utf-8"))
        current = [row for row in payload["results"] if row["version"] == "v1_6_11"]
        self.assertEqual(len(current), 28)
        self.assertFalse(
            [
                row
                for row in current
                if row["returncode"] != 0 or not row.get("output_json_exists")
            ]
        )

    def test_v1_0_baseline_has_command_shape_blockers(self):
        payload = json.loads(RAW.read_text(encoding="utf-8"))
        baseline = [row for row in payload["results"] if row["version"] == "v1_0"]
        ok = [
            row
            for row in baseline
            if row["returncode"] == 0 and row.get("output_json_exists")
        ]
        blocked = [
            row
            for row in baseline
            if row["returncode"] != 0 or not row.get("output_json_exists")
        ]
        self.assertEqual(len(ok), 4)
        self.assertEqual(len(blocked), 24)
        self.assertTrue(all(row["returncode"] == 2 for row in blocked))
        self.assertTrue(all("unrecognized arguments: --backend" in row["stderr_tail"] for row in blocked))
        self.assertEqual(
            {(row["app"], row["engine"]) for row in ok},
            {
                ("database_analytics", "embree"),
                ("database_analytics", "optix"),
                ("graph_analytics", "optix"),
                ("outlier_detection", "optix"),
            },
        )

    def test_report_preserves_release_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "v1_6_11: 28 / 28 planned invocations returned 0",
            "v1_0: 4 / 28 planned invocations returned 0",
            "24 v1.0 invocations failed",
            "baseline command-shape/schema compatibility blocker",
            "accept-with-boundary",
            "needs-more-evidence",
            "No public speedup wording",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
