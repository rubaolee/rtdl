from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3622_next_version_direction_consensus_status_2026-06-06.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal3620_gemini_review_goal3619_next_version_direction_2026-06-06.md"


class Goal3622NextVersionDirectionConsensusStatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.gemini_review = GEMINI_REVIEW.read_text(encoding="utf-8")

    def test_status_does_not_claim_final_consensus(self):
        self.assertIn("not final 3-AI consensus", self.report)
        self.assertIn("strict 3-AI consensus is **pending**", self.report)
        self.assertIn("Claude review is unavailable", self.report)
        self.assertIn("write a separate final consensus file only if", self.report)

    def test_records_codex_and_gemini_acceptance(self):
        self.assertIn("Codex + Gemini direction verdict: `accept-with-boundary`", self.report)
        self.assertIn("Gemini accepted the direction with boundary", self.report)
        self.assertIn("`accept-with-boundary`", self.gemini_review)

    def test_answers_gemini_clarifications(self):
        self.assertIn("Partner-Compatible Handoff Contracts", self.report)
        self.assertIn("__cuda_array_interface__", self.report)
        self.assertIn("DLPack-compatible descriptors", self.report)
        self.assertIn("Criteria For Future Primitive Contracts", self.report)
        self.assertIn("External Dependency Strategy", self.report)

    def test_keeps_core_direction_and_claim_boundaries(self):
        self.assertIn("contract-and-residency first", self.report)
        self.assertIn("Keep partners user-chosen", self.report)
        self.assertIn("Keep shader injection parked", self.report)
        self.assertIn("This does not authorize true zero-copy", self.report)


if __name__ == "__main__":
    unittest.main()
