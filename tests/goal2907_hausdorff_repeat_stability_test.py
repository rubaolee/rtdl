import json
import unittest
from pathlib import Path

from scripts import goal2801_hausdorff_xhd_v25_canonical_entrypoint as hausdorff_entry


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2907_hausdorff_repeat_stability_and_rtnn_near_parity_2026-05-31.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2907_pod_artifacts"
    / "goal2907_hausdorff_repeat9_pod_69_30_85_171_2026-05-31.json"
)


class Goal2907HausdorffRepeatStabilityTest(unittest.TestCase):
    def test_hausdorff_default_repeat_is_stable_enough_for_short_rows(self) -> None:
        self.assertEqual(hausdorff_entry.DEFAULT_REPEAT, 9)

    def test_repeat9_pod_artifact_keeps_hausdorff_near_parity(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["source_commit"], "1756dce2386cd086aa91edce8e2656ce8d8899f2")
        self.assertEqual(payload["source_dirty"], [])
        self.assertTrue(payload["matches_exact_baseline"])
        self.assertEqual(payload["distance_error"], 0.0)
        self.assertEqual(payload["scenario"]["repeat"], 9)
        self.assertTrue(payload["rtdl"]["uses_rt_cores"])
        self.assertEqual(payload["rtdl"]["method"], "rtdl_rt_grouped_reduced_nearest_witness")
        self.assertLess(payload["rtdl_over_cupy_grid_elapsed_ratio"], 1.10)

    def test_report_records_boundary_and_reason(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("repeat = 9", text)
        self.assertIn("RTDL uses RT cores: `true`", text)
        self.assertIn("current_path_acceptable_near_parity_distribution_dependent", text)
        self.assertIn("not a release packet", text)


if __name__ == "__main__":
    unittest.main()
