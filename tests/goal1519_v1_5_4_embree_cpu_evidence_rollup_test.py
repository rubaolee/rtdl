from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1519_v1_5_4_embree_cpu_evidence_rollup_2026-05-08.md"


class Goal1519EmbreeCpuEvidenceRollupTest(unittest.TestCase):
    def test_rollup_report_exists_and_keeps_claim_boundary(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal 1519", text)
        self.assertIn("Evidence Matrix", text)
        self.assertIn("What This Proves", text)
        self.assertIn("What This Does Not Prove", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("does not promote `COLLECT_K_BOUNDED`", text)

    def test_rollup_points_to_required_recent_artifacts(self):
        text = REPORT.read_text(encoding="utf-8")
        for stem in [
            "goal1514_v1_5_4_embree_cpu_promotion_lane_2026-05-08.md",
            "goal1515_v1_5_4_embree_native_linux_validation_2026-05-08.md",
            "goal1516_v1_5_4_embree_materialization_summary_perf_2026-05-08.md",
            "goal1516_v1_5_4_embree_materialization_summary_perf_2026-05-08.json",
            "goal1517_v1_5_4_embree_prepared_summary_reuse_perf_2026-05-08.md",
            "goal1517_v1_5_4_embree_prepared_summary_reuse_perf_2026-05-08.json",
            "goal1518_v1_5_4_embree_polygon_native_assisted_perf_2026-05-08.md",
            "goal1518_v1_5_4_embree_polygon_native_assisted_perf_2026-05-08.json",
        ]:
            self.assertIn(stem, text)
            self.assertTrue((ROOT / "docs" / "reports" / stem).exists(), stem)

    def test_rollup_records_mixed_polygon_outcome(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("1.794x", text)
        self.assertIn("0.068x", text)
        self.assertIn("no broad polygon/GIS claim", text)


if __name__ == "__main__":
    unittest.main()
