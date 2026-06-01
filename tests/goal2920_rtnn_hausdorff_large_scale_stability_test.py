from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import goal2801_hausdorff_xhd_v25_canonical_entrypoint as hd_entrypoint


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2920_rtnn_hausdorff_large_scale_stability_and_hd_default_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2920_hausdorff_rtnn_large_probe_pod"


class Goal2920RtnnHausdorffLargeScaleStabilityTest(unittest.TestCase):
    def test_rtnn_large_probe_removes_short_row_concern(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "rtnn_262144_repeat9.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual(262144, payload["point_count"])
        self.assertEqual(9, payload["repeat"])
        ratios = {
            row["distribution"]: float(row["cupy_grid_over_rtdl_elapsed_ratio"])
            for row in payload["rows"]
        }
        self.assertGreater(ratios["uniform"], 3.0)
        self.assertGreater(ratios["clustered"], 1.5)
        self.assertGreater(ratios["shell"], 4.0)
        for row in payload["rows"]:
            self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
            self.assertFalse(row["claim_boundary"]["rtdl_beats_rtnn_claim_authorized"])

    def test_hausdorff_target4096_is_confirmed_at_8k_and_16k(self) -> None:
        for name in ("hd8192_target4096_repeat9.json", "hd16384_target4096_repeat9.json"):
            with self.subTest(name=name):
                payload = json.loads((ARTIFACT_DIR / "hd_confirm" / name).read_text(encoding="utf-8"))
                self.assertEqual("pass", payload["status"])
                self.assertTrue(payload["matches_exact_baseline"])
                self.assertTrue(payload["rtdl"]["uses_rt_cores"])
                self.assertLess(float(payload["rtdl_over_cupy_grid_elapsed_ratio"]), 1.0)
                self.assertEqual(4096, payload["rtdl"]["reduced_target_points_per_group"])
                self.assertFalse(payload["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

    def test_hausdorff_default_uses_latest_target_without_native_engine_change(self) -> None:
        self.assertEqual(8192, hd_entrypoint.DEFAULT_REDUCED_TARGET_POINTS_PER_GROUP)
        self.assertIn("target8192", hd_entrypoint.GOAL2801_ENTRYPOINT_VERSION)
        self.assertFalse(hd_entrypoint.CLAIM_BOUNDARY["native_engine_customization"])

    def test_report_documents_boundary_and_next_packet_requirement(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2920",
            "RTNN 262,144-point",
            "target `4096`",
            "does not change the RTDL",
            "seven-app packet must be rerun",
            "not a v2.5 release authorization",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
