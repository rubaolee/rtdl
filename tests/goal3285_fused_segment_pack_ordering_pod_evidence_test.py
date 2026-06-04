from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
REPORT = ROOT / "docs" / "reports" / "goal3285_fused_segment_pack_ordering_rayjoin_lsi_probe_2026-06-04.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3285_fused_pack_lsi_segment_order_pod"
MODES = ("natural", "x_then_y", "y_then_x", "morton_xy")


class Goal3285FusedSegmentPackOrderingPodEvidenceTest(unittest.TestCase):
    def _artifact(self, mode: str) -> dict:
        return json.loads((ARTIFACT_DIR / f"{mode}.json").read_text(encoding="utf-8"))

    def test_report_and_artifacts_exist(self) -> None:
        self.assertTrue(REPORT.exists())
        for mode in MODES:
            self.assertTrue((ARTIFACT_DIR / f"{mode}.json").exists(), mode)

    def test_all_modes_preserve_lsi_count_and_claim_boundary(self) -> None:
        for mode in MODES:
            data = self._artifact(mode)
            self.assertEqual(data["rtdl"]["lsi"]["counts"]["last"], 269)
            self.assertTrue(data["rtdl"]["lsi"]["counts"]["consistent"])
            self.assertEqual(data["rtdl"]["lsi"]["segment_order_mode"], mode)
            for value in data["claim_boundary"].values():
                self.assertFalse(value)

    def test_ordering_improves_query_phase_but_not_host_pack_cost(self) -> None:
        natural = self._artifact("natural")["rtdl"]["lsi"]
        y_then_x = self._artifact("y_then_x")["rtdl"]["lsi"]

        self.assertLess(
            y_then_x["prepared_query_ms"]["median"],
            natural["prepared_query_ms"]["median"],
        )
        self.assertGreater(
            y_then_x["query_pack_ms"]["median"],
            natural["query_pack_ms"]["median"],
        )
        self.assertGreater(
            y_then_x["static_segment_pack_ms"]["median"],
            natural["static_segment_pack_ms"]["median"],
        )

    def test_report_blocks_default_promotion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        unwrapped = " ".join(text.split())

        self.assertIn("not a benchmark win", text)
        self.assertIn("not a promoted high-performance", unwrapped)
        self.assertIn("RayJoin route", unwrapped)
        self.assertIn("No native ABI was added", text)


if __name__ == "__main__":
    unittest.main()
