from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "reports" / "goal1266_v1_2_optix_plan_after_v1_1_findings_2026-05-05.md"


class Goal1266V12OptixPlanTest(unittest.TestCase):
    def test_plan_records_current_backend_scope(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        for phrase in (
            "NVIDIA OptiX/RTX performance is the top priority",
            "Embree remains the same-contract CPU RT/BVH baseline",
            "Vulkan, HIPRT, and Apple RT receive no new implementation work before v2.1",
            "does not authorize public wording",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_plan_accepts_explained_slower_optix_outcome(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        for phrase in (
            "optix_still_slower_with_reason",
            "result can close as `optix_still_slower_with_reason`",
            "not positive public RTX speedup\nwording",
            "Positive public wording still requires",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_plan_covers_four_v1_2_targets(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        for phrase in (
            "`polygon_pair_overlap_area_rows`",
            "`graph_analytics`",
            "`database_analytics`",
            "`polygon_set_jaccard`",
            "candidate_count_matches_expected: false",
            "host-side input construction, scene/ray prepare, and ray packing dominate",
            "warm-query median still favors Embree",
            "chunk `1024`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_plan_preserves_pod_policy(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("Do more local inspection before starting a pod", text)
        self.assertIn("exact commands, expected artifacts, and the phase fields", text)


if __name__ == "__main__":
    unittest.main()
