from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import goal2801_hausdorff_xhd_v25_canonical_entrypoint as entrypoint


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2952_hausdorff_target8192_default_tuning_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2952_hausdorff_target8192_sweep_pod"


class Goal2952HausdorffTarget8192DefaultTuningTest(unittest.TestCase):
    def test_entrypoint_default_uses_target8192(self) -> None:
        self.assertEqual(8192, entrypoint.DEFAULT_REDUCED_TARGET_POINTS_PER_GROUP)
        self.assertIn("target8192", entrypoint.GOAL2801_ENTRYPOINT_VERSION)
        self.assertFalse(entrypoint.CLAIM_BOUNDARY["native_engine_customization"])

    def test_8k_sweep_selects_reduced_target8192_over_seeded_pruned(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "goal2952_hd_sweep.json").read_text(encoding="utf-8"))
        baseline = float(payload["baseline_median"])
        rows = {(row["method"], int(row["target"])): row for row in payload["rows"]}

        self.assertLess(float(rows[("reduced", 8192)]["median"]), baseline)
        self.assertLess(float(rows[("reduced", 8192)]["median"]), float(rows[("reduced", 4096)]["median"]))
        self.assertGreater(float(rows[("seeded_pruned", 8192)]["median"]), baseline)
        for row in payload["rows"]:
            self.assertAlmostEqual(0.12003618286664636, float(row["distance"]), places=12)

    def test_16k_confirmation_is_exact_and_faster_than_cupy_grid(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "goal2952_hd16384_target8192_repeat7.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["source_dirty"])
        self.assertTrue(payload["matches_exact_baseline"])
        self.assertEqual(0.0, float(payload["distance_error"]))
        self.assertTrue(payload["rtdl"]["uses_rt_cores"])
        self.assertEqual(8192, payload["rtdl"]["reduced_target_points_per_group"])
        self.assertLess(float(payload["rtdl_over_cupy_grid_elapsed_ratio"]), 0.9)
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2952",
            "Target points/group",
            "`0.843x`",
            "`0.873x`",
            "app-level parameter/default tuning",
            "does not customize the native engine",
            "does not authorize public speedup",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
