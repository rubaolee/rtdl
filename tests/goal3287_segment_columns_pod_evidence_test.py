from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
REPORT = ROOT / "docs" / "reports" / "goal3287_segment_columns_2d_layout_and_rayjoin_probe_2026-06-04.md"
HARNESS = ROOT / "docs" / "reports" / "goal3287_segment_columns_lsi_dense_count_pod_2026-06-04.json"
MICRO = ROOT / "docs" / "reports" / "goal3287_segment_columns_pack_left_micro_pod_2026-06-04.json"


class Goal3287SegmentColumnsPodEvidenceTest(unittest.TestCase):
    def test_pod_artifacts_exist(self) -> None:
        self.assertTrue(REPORT.exists())
        self.assertTrue(HARNESS.exists())
        self.assertTrue(MICRO.exists())

    def test_dense_count_harness_passes_with_boundaries_false(self) -> None:
        data = json.loads(HARNESS.read_text(encoding="utf-8"))

        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["rows"][0]["workload"], "lsi")
        self.assertEqual(data["rows"][0]["observed_count"], 269)
        self.assertTrue(data["rows"][0]["matches_cpu_reference"])
        self.assertLess(data["rows"][0]["phase_medians_ms"]["left_id_count_device_columns_sec"], 1.0)
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["paper_reproduction_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_pack_left_micro_records_column_and_pack_costs(self) -> None:
        data = json.loads(MICRO.read_text(encoding="utf-8"))

        self.assertEqual(data["left_segment_count"], 19987)
        self.assertGreater(data["column_prepare_seconds"]["median"], 0.0)
        self.assertGreater(data["pack_seconds"]["median"], 0.0)
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])

    def test_report_blocks_performance_promotion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        normalized = " ".join(text.replace("**", "").split())

        self.assertIn("not a performance win", normalized)
        self.assertIn("No native ABI was added", text)
        self.assertIn("host-side data layout is now the blocker", normalized)


if __name__ == "__main__":
    unittest.main()
