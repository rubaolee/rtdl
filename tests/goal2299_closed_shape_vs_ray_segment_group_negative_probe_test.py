import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2299_closed_shape_vs_ray_segment_group_negative_probe_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2299_pip_closed_shape_vs_ray_segment_group_probe_pod_2026-05-17.json"


class Goal2299ClosedShapeVsRaySegmentGroupNegativeProbeTest(unittest.TestCase):
    def test_artifact_rejects_ray_segment_group_for_pip_perf(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(data["sets_match"])
        self.assertEqual(data["closed_rows"], 8686)
        self.assertEqual(data["odd_rows"], 8686)
        self.assertEqual(data["missing_from_odd"], 0)
        self.assertEqual(data["extra_in_odd"], 0)
        self.assertGreater(data["odd_vs_closed_rows_ratio"], 50.0)
        self.assertGreater(data["odd_vs_closed_count_ratio"], 70.0)

    def test_report_keeps_next_primitive_direction_clear(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: rejected fallback path.", text)
        self.assertIn("correct but much slower", text)
        self.assertIn("improve closed-shape membership directly", text)
        self.assertIn("should not route", text)
        self.assertIn("boundary-segment ray crossings", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
