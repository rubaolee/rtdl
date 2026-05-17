import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2298_closed_shape_geos_toggle_negative_probe_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2298_closed_shape_geos_toggle_negative_probe_pod_2026-05-17.json"


class Goal2298ClosedShapeGeosToggleNegativeProbeTest(unittest.TestCase):
    def test_artifact_rejects_fallback_exact_refine_speedup(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        default = data["default_geos"]
        fallback = data["host_float_exact"]
        self.assertTrue(default["all_expected"])
        self.assertTrue(fallback["all_expected"])
        self.assertEqual(set(default["counts"]), {8686})
        self.assertEqual(set(fallback["counts"]), {8686})
        self.assertLess(default["median_sec"], fallback["median_sec"])
        self.assertLess(default["median_sec"] / fallback["median_sec"], 1.0)

    def test_report_records_rejection_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: rejected optimization idea.", text)
        self.assertIn("Rejected.", text)
        self.assertIn("candidate traversal/write", text)
        self.assertIn("not GEOS exact refinement", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release readiness", text)


if __name__ == "__main__":
    unittest.main()
