from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2481_robot_collision_generic_contract_design_2026-05-21.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2481_gemini_review_robot_collision_generic_contract_2026-05-21.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal2481_claude_review_robot_collision_generic_contract_2026-05-21.md"
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2481_codex_gemini_claude_consensus_robot_collision_generic_contract_2026-05-21.md"
)
ACTIVE_NATIVE_DIRS = (
    ROOT / "src" / "native" / "embree",
    ROOT / "src" / "native" / "optix",
)
FORBIDDEN_NATIVE_WORDS = re.compile(
    r"\b(robot|collision|link|pose|joint|kinematic|kinematics|planner)\b",
    re.IGNORECASE,
)


class Goal2481RobotCollisionGenericContractDesignTest(unittest.TestCase):
    def test_report_chooses_first_minimal_generic_contract(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1", report)
        self.assertIn("prepared_static_triangle_scene_3d", report)
        self.assertIn("grouped finite 3D query segment probes", report)
        self.assertIn("byte-per-query-group any-hit flags", report)
        self.assertIn("not a native robot-collision API", report)
        self.assertIn("Python owns application geometry, transforms, grouping", report)

    def test_report_resolves_goal2480_followups(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2481 chooses a 3D native", report)
        self.assertIn("Goal2480 CPU fixture remains an application-level seed", report)
        self.assertIn("3D CPU probe-oracle fixture", report)
        self.assertIn("Before claiming Embree parity", report)

    def test_output_format_and_non_goals_are_locked(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2481 chooses byte-per-query-group `uint8` flags", report)
        self.assertIn("must be rejected by the", report)
        self.assertIn("Python packer before native traversal", report)
        self.assertIn("backend may narrow to float32 if metadata records it", report)
        self.assertIn("bit-packed flags", report)
        self.assertIn("row witness lists", report)
        self.assertIn("pair rows", report)
        self.assertIn("Bit-packed output can be reconsidered only after Goal2485", report)
        self.assertIn("does not authorize", report)
        self.assertIn("paper reproduction claims", report)
        self.assertIn("public speedup wording", report)
        self.assertIn("continuous or swept collision support", report)
        self.assertIn("release/tag action", report)

    def test_active_native_targets_remain_free_of_app_vocabulary(self) -> None:
        hits: list[str] = []
        for directory in ACTIVE_NATIVE_DIRS:
            for path in directory.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if FORBIDDEN_NATIVE_WORDS.search(text):
                    hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])

    def test_goal2482_native_work_is_gated(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2482 may start Embree work only under this contract", report)
        self.assertIn("must not add native robot-collision", report)
        self.assertIn("no forbidden native vocabulary was introduced", report)
        self.assertIn("full-float64 input fixture", report)
        self.assertIn("Goal2481 tests, external reviews, and consensus artifact must be green", report)

    def test_external_reviews_and_consensus_approve_goal2481(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: Approved", gemini)
        self.assertIn("Blocking Issues", gemini)
        self.assertIn("None", gemini)
        self.assertIn("Verdict: Approved", claude)
        self.assertIn("Blocking Issues", claude)
        self.assertIn("None", claude)
        self.assertIn("Consensus: Approved", consensus)
        self.assertIn("Goal2482 may proceed", consensus)


if __name__ == "__main__":
    unittest.main()
