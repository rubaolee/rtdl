import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1753_v1_8_decision_status_after_perf_summary_2026-05-12.md"


class Goal1753V18DecisionStatusAfterPerfSummaryTest(unittest.TestCase):
    def test_status_note_names_remaining_blockers(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn(
            "v1_8_decision_status_ready_pending_user_release_authorization",
            text,
        )
        self.assertIn("Goal1762 recorded final v1.8 release-prep consensus", text)
        self.assertIn("explicit user authorization", text)

    def test_status_note_records_perf_summary_without_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal1750 produced the strict same-contract performance summary", text)
        self.assertIn("OptiX: 15 artifact-pair rows, 12 same-contract primary ratios", text)
        self.assertIn("Embree: 1 strict same-contract database row", text)
        self.assertIn("recovered v1.0 Embree app-level rows as public same-contract speedup evidence", text)
        self.assertIn("Public speedup wording", text)
        self.assertIn("Whole-application performance claims", text)

    def test_status_note_records_goal1758_source_abi_blocker_resolution(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal1758 migrated the remaining older Apple RT / HIPRT / Oracle / Vulkan", text)
        self.assertIn("removed the final known multi-backend source/ABI app-shaped blocker", text)
        self.assertIn("native engine source/ABI boundary", text)

    def test_status_note_records_claude_failure_as_non_review(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("did not produce the review file", text)
        self.assertIn("You're out of extra usage", text)
        self.assertIn("does not count Claude as having reviewed", text)
        self.assertFalse(
            (ROOT / "docs" / "reviews" / "goal1752_claude_review_updated_goal1742_1750_v1_8_packet_2026-05-12.md").exists()
        )

    def test_status_note_is_not_release_action(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not a release decision", text)
        self.assertIn("not authorize release", text)
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "v1.8")

    def test_status_note_records_fresh_reviews_and_final_prep_consensus(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goals1760 and 1761 supplied fresh independent Claude and Gemini review", text)
        self.assertIn("Goal1762 recorded final v1.8 release-prep consensus", text)
        self.assertIn("Goals1763-1768 added the final public-doc", text)
        self.assertIn("Re-run the focused v1.8 gate", text)


if __name__ == "__main__":
    unittest.main()
