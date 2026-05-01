import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md"
REPORT = ROOT / "docs" / "reports" / "goal823_v1_0_nvidia_rt_core_app_promotion_plan_2026-04-23.md"


class Goal823V10NvidiaRtCoreAppPromotionPlanTest(unittest.TestCase):
    def test_plan_records_cloud_cost_rule(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        self.assertIn("Do not ask the user to restart or stop a cloud pod per app", text)
        self.assertIn("one consolidated batch", text)

    def test_plan_covers_all_promotion_tiers(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        for phrase in (
            "Tier 1: Finish Near-Ready RT-Core Apps",
            "Tier 2: Phase Evidence Before Promotion",
            "Tier 3: Native OptiX Redesign Needed",
            "Tier 4: App Surface Needed First",
            "robot_collision_screening",
            "service_coverage_gaps",
            "segment_polygon_hitcount",
            "facility_knn_assignment",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_links_plan_and_preserves_no_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn(str(PLAN), text)
        self.assertIn("will not equate `--backend optix` with NVIDIA RT-core acceleration", text)
        self.assertIn("No release or speedup claim", PLAN.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
