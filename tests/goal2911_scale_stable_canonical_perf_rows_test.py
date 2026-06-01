import json
import unittest
from pathlib import Path

from scripts import goal2800_rtnn_v25_live_ranked_summary_harness as rtnn_harness
from scripts import goal2801_hausdorff_xhd_v25_canonical_entrypoint as hausdorff_entry


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2911_scale_stable_canonical_perf_rows_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2911_scale_probe_pod"


class Goal2911ScaleStableCanonicalPerfRowsTest(unittest.TestCase):
    def test_canonical_defaults_use_scaled_rows(self) -> None:
        self.assertEqual(hausdorff_entry.DEFAULT_POINTS_A, 8192)
        self.assertEqual(hausdorff_entry.DEFAULT_POINTS_B, 8192)
        self.assertEqual(hausdorff_entry.DEFAULT_REPEAT, 9)
        self.assertEqual(rtnn_harness.DEFAULT_POINT_COUNT, 65536)
        self.assertEqual(rtnn_harness.DEFAULT_REPEAT, 9)

    def test_hausdorff_scaled_probe_is_near_parity(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "hausdorff_8192_repeat9.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["source_commit"], "1e3c98ffa76e602959f943a83e79fb5b442d9cd1")
        self.assertEqual(payload["source_dirty"], [])
        self.assertTrue(payload["matches_exact_baseline"])
        self.assertEqual(payload["scenario"]["points_a"], 8192)
        self.assertEqual(payload["scenario"]["points_b"], 8192)
        self.assertLess(payload["rtdl_over_cupy_grid_elapsed_ratio"], 1.01)

    def test_rtnn_scaled_probe_is_green_on_all_distributions(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "rtnn_65536_repeat9.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["source_commit"], "1e3c98ffa76e602959f943a83e79fb5b442d9cd1")
        self.assertEqual(payload["source_dirty"], [])
        self.assertEqual(payload["point_count"], 65536)
        self.assertEqual(payload["repeat"], 9)
        ratios = {row["distribution"]: row["cupy_grid_over_rtdl_elapsed_ratio"] for row in payload["rows"]}
        self.assertGreater(ratios["uniform"], 1.0)
        self.assertGreater(ratios["clustered"], 2.0)
        self.assertGreater(ratios["shell"], 7.0)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("8,192 x 8,192", text)
        self.assertIn("65,536 points", text)
        self.assertIn("No native engine code changed", text)
        self.assertIn("not a v2.5 release packet", text)


if __name__ == "__main__":
    unittest.main()
