from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1514_v1_5_4_embree_cpu_promotion_lane_2026-05-08.md"


class Goal1514EmbreeCpuPromotionLaneTest(unittest.TestCase):
    def test_report_exists(self):
        self.assertTrue(REPORT.exists())

    def test_report_defines_embree_cpu_value(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "Embree is the right non-GPU lane",
            "app-name-free primitive contracts",
            "fail-closed overflow behavior",
            "stable row schemas and row ordering",
            "Python/native ABI routing",
        ]:
            self.assertIn(phrase, text)

    def test_report_has_work_item_table(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "| Work item | CPU-only value | Acceptance signal | Not a claim |",
            "Bounded collection parity",
            "Fail-closed overflow tests",
            "Reduction parity",
            "ABI/export checks",
            "Linux/Windows smoke slices",
        ]:
            self.assertIn(phrase, text)

    def test_report_records_local_test_slices(self):
        text = REPORT.read_text(encoding="utf-8")
        for test_name in [
            "tests.goal1316_v1_5_embree_candidate_collection_surface_test",
            "tests.goal1317_v1_5_embree_native_candidate_collection_abi_test",
            "tests.goal1416_v1_5_1_collect_k_native_parity_test",
            "tests.goal1418_v1_5_1_collect_k_readiness_gate_test",
            "tests.goal715_embree_fixed_radius_summary_test",
            "tests.goal736_robot_collision_embree_scaled_test",
        ]:
            self.assertIn(test_name, text)

    def test_report_keeps_claim_boundary_conservative(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "does not promote\n`COLLECT_K_BOUNDED`",
            "Passing Embree semantics does not imply OptiX performance",
            "does not authorize\npublic speedup wording",
            "true zero-copy",
            "NVIDIA performance claims",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
