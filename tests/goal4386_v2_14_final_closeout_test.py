from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "docs/release_reports/v2_14"
REPORT = ROOT / "docs/reports/goal4386_v2_14_final_closeout_2026-06-15.md"
M1_UNLOCK = ROOT / "docs/reports/goal4387_v3_0_m1_design_only_unlock_2026-06-15.md"


class Goal4386V214FinalCloseoutTest(unittest.TestCase):
    def test_inventory_freezes_public_and_internal_rows(self) -> None:
        text = (RELEASE_DIR / "promoted_benchmark_inventory.md").read_text(encoding="utf-8")
        for row in (
            "rtnn_ranked_summary",
            "rt_dbscan_core_flags_numba_signature",
            "spatial_rayjoin_lsi",
            "spatial_rayjoin_pip",
            "spatial_rayjoin_overlay",
            "raydb_style_grouped_i64_count",
            "librts_spatial_index_aabb",
            "triangle_counting_any_hit",
            "barnes_hut_node_coverage",
            "hausdorff_xhd_threshold",
            "robot_collision_grouped_segment_flags",
            "contact_manifold_aabb_collect_k",
        ):
            self.assertIn(row, text)
        self.assertIn("public-review-ready for the available 2/8 exact subset", text)
        self.assertIn("not a full 8/8 Section 5.7 reproduction", text)

    def test_final_matrix_uses_goal4383_supersession_numbers(self) -> None:
        text = (RELEASE_DIR / "public_rt_vs_embree_comparison.md").read_text(encoding="utf-8")
        self.assertIn("RTDBSCAN must use the compact-Embree-threshold result", text)
        self.assertIn("total 1.05x OptiX faster", text)
        self.assertIn("threshold stage 1.37x faster", text)
        self.assertIn("hot query 13.39x faster", text)
        self.assertIn("hot query 107.61x faster", text)
        self.assertIn("AABB query 1.23x faster", text)
        self.assertIn("ready for available 2/8 exact-subset wording", text)
        self.assertNotIn("RT cores make every benchmark app faster", text)

    def test_wording_boundaries_block_overclaims(self) -> None:
        text = (RELEASE_DIR / "public_wording_boundaries.md").read_text(encoding="utf-8")
        self.assertIn("Do not say", text)
        self.assertIn("RTDL hot compute matches", text)
        self.assertIn("must not claim full 8/8 Section 5.7 reproduction", text)
        self.assertIn("RTDBSCAN has a large full-app RT-core speedup", text)
        self.assertIn("V3.0 implementation is not authorized", text)

    def test_final_closeout_records_1_to_7_and_blocks_v3_implementation(self) -> None:
        text = (RELEASE_DIR / "final_closeout.md").read_text(encoding="utf-8")
        self.assertIn("v2.14 is closed", text)
        self.assertIn("Final local focused gates passed", text)
        self.assertIn("Final pod focused gates passed", text)
        self.assertIn("V3.0 M1 design may begin", text)
        self.assertIn("V3.0 implementation remains blocked", text)

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("The requested 1-7 sequence is complete", report)
        self.assertIn("V3.0 implementation remains blocked", report)

    def test_v3_m1_design_only_unlock_keeps_implementation_blocked(self) -> None:
        text = M1_UNLOCK.read_text(encoding="utf-8")
        self.assertIn("M1 design-only unlock", text)
        self.assertIn("V3.0 implementation remains blocked", text)
        self.assertIn("native V3.0 fused execution code", text)
        self.assertIn("v3_0_m1_design_allowed_implementation_blocked", text)


if __name__ == "__main__":
    unittest.main()
