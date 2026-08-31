from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/learn/v2_14_app_author_implementation_strategy.md"
LEARN_README = ROOT / "docs/learn/README.md"
HANDOFF = (
    ROOT
    / "docs/handoff/HANDOFF_CLAUDE_GOAL4390_V2_14_APP_AUTHOR_IMPLEMENTATION_STRATEGY_2026-06-15.md"
)
CLAUDE_STATUS = (
    ROOT
    / "docs/reviews/goal4390_claude_review_status_v2_14_app_author_implementation_strategy_2026-06-15.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs/reviews/goal4390_claude_review_v2_14_app_author_implementation_strategy_2026-06-15.md"
)


class Goal4390V214AppAuthorStrategyTest(unittest.TestCase):
    def test_strategy_doc_covers_user_decision_points(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        for phrase in (
            "Start primitive-first",
            "OptiX-vs-Embree claims must use the same app row",
            "Use Prepared Execution When Reuse Exists",
            "Add Partner Continuation Only For App-Specific Work",
            "Choose A Partner",
            "Compose Complex Apps As Pipelines",
            "When To Request A New Primitive",
            "Why v2.14 Does Not Expose Raw OptiX Callback APIs",
        ):
            self.assertIn(phrase, text)

    def test_strategy_doc_preserves_boundaries(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("does not expose arbitrary OptiX callback functions", text)
        self.assertIn("does not expose arbitrary", text)
        self.assertIn("partner choice is not automatic", text)
        self.assertIn("same-contract Numba reference", text)
        self.assertIn("app policy belongs in the app or partner", text)
        self.assertIn("native RTDL engine remains app-agnostic", text)
        self.assertIn("available 2/8 exact Section 5.7 subset", text)
        self.assertIn("fix Numba as the continuation lock", text)
        self.assertIn("continuation phase is about 6.9s", text)
        self.assertIn("Do not use this path to claim RTDL primitive performance exceeds a specialized implementation", text)
        self.assertIn("fixed partner used for backend comparison", text)
        self.assertNotIn("RTDL automatically chooses the best partner.", text.split("Blocked:", 1)[0])

    def test_learn_index_and_claude_handoff_exist(self) -> None:
        readme = LEARN_README.read_text(encoding="utf-8")
        handoff = HANDOFF.read_text(encoding="utf-8")
        status = CLAUDE_STATUS.read_text(encoding="utf-8")
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")
        self.assertIn("v2.14 App-Author Implementation Strategy", readme)
        self.assertIn("One-Sentence Reviewer Prompt", handoff)
        self.assertIn("raw OptiX callback support", handoff)
        self.assertIn("Verdict: **accept-with-boundary**", review)
        self.assertIn("Required Fixes Before Public Release", review)
        self.assertIn("Claude review completed", status)
        self.assertIn("accept-with-boundary", status)
        self.assertIn("All four were applied", status)


if __name__ == "__main__":
    unittest.main()
