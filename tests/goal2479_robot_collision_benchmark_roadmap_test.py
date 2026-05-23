from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "docs" / "reports" / "goal2479_robot_collision_benchmark_roadmap_2026-05-21.md"
GEMINI = ROOT / "docs" / "reviews" / "goal2479_gemini_review_robot_collision_roadmap_2026-05-21.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal2479_claude_review_robot_collision_roadmap_2026-05-21.md"
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2479_codex_gemini_claude_consensus_robot_collision_roadmap_2026-05-21.md"
)


class Goal2479RobotCollisionBenchmarkRoadmapTest(unittest.TestCase):
    def test_roadmap_chooses_robot_collision_before_raydb_with_bounded_reason(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("robot collision detection, not RayDB", roadmap)
        self.assertIn("citation is tentative", roadmap)
        self.assertIn("confirm the full authorship", roadmap)
        self.assertIn("dynamic transformed query geometry", roadmap)
        self.assertIn("prepared static obstacle scenes", roadmap)
        self.assertIn("RayDB remains valuable", roadmap)

    def test_roadmap_keeps_native_engine_app_agnostic(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("no robot-specific native ABI", roadmap)
        self.assertIn("forbidden native vocabulary", roadmap)
        for forbidden in ("`robot`", "`link`", "`pose`", "`joint`", "`kinematics`", "`planner`"):
            self.assertIn(forbidden, roadmap)
        self.assertIn("avoid native `collision` vocabulary", roadmap)
        self.assertIn("`intersection`", roadmap)
        self.assertIn("`any_hit`", roadmap)
        self.assertIn("prepared_static_triangles + batched_transformed_query_geometry", roadmap)
        self.assertIn("compact any-hit flags", roadmap)

    def test_roadmap_sequences_cpu_reference_before_native_work(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("Goal2480: CPU Reference Robot Collision App", roadmap)
        self.assertIn("Goal2481: Generic RTDL Contract Design", roadmap)
        self.assertIn("Whether compact output should be byte-per-query, bit-packed", roadmap)
        self.assertIn("existing RTDL", roadmap)
        self.assertIn("buffer and tensor conventions", roadmap)
        self.assertIn("Goal2482: Embree Prototype", roadmap)
        self.assertIn("Goal2483: OptiX Prototype", roadmap)
        self.assertIn("Goal2484 must define the warmup protocol before measurement", roadmap)
        self.assertIn("Do not start native Embree/OptiX work until the CPU reference app", roadmap)

    def test_roadmap_blocks_paper_reproduction_and_public_speedup_claims(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("No official implementation has been verified", roadmap)
        self.assertIn("should not claim comparison against the authors' implementation", roadmap)
        self.assertIn("If authors' code becomes available", roadmap)
        self.assertIn("requires a separate", roadmap)
        self.assertIn("Full ICRA paper reproduction", roadmap)
        self.assertIn("Public speedup wording", roadmap)
        self.assertIn("No public speedup wording", roadmap)

    def test_external_reviews_and_consensus_approve_starting_goal2480(self) -> None:
        gemini = GEMINI.read_text(encoding="utf-8")
        claude = CLAUDE.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: Approved", gemini)
        self.assertIn("Blocking Issues", gemini)
        self.assertIn("None", gemini)
        self.assertIn("Verdict: Approved", claude)
        self.assertIn("Blocking Issues", claude)
        self.assertIn("None", claude)
        self.assertIn("Codex, Gemini, and Claude agree", consensus)
        self.assertIn("Goal2479/2480 may proceed", consensus)
        self.assertIn("does not authorize paper reproduction claims", consensus)


if __name__ == "__main__":
    unittest.main()
