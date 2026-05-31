from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2849_v2_5_readiness_indexes_current_canonical_harness_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2850_gemini_review_goal2849_v2_5_readiness_current_canonical_harness_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2850_goal2849_v2_5_readiness_current_canonical_harness_consensus_2026-05-31.md"
EXPECTED_COMMIT = "23b047e5d44bfda7e535ca7ba78d94f195e2be86"


class Goal2849V25ReadinessIndexesCurrentCanonicalHarnessTest(unittest.TestCase):
    def test_internal_readiness_indexes_goal2847_and_goal2848(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(
            validation["current_canonical_harness_artifact_count"],
            7,
        )
        for path in (
            "docs/reports/goal2847_current_head_canonical_harness_refresh_2026-05-31.md",
            "docs/reports/goal2848_goal2847_current_head_canonical_harness_consensus_2026-05-31.md",
        ):
            with self.subTest(path=path):
                self.assertTrue(packet["required_report_presence"][path])

        review_path = (
            "docs/reviews/"
            "goal2848_gemini_review_goal2847_current_head_canonical_harness_2026-05-31.md"
        )
        self.assertTrue(packet["external_review_presence"][review_path])

    def test_current_canonical_harness_metadata_is_clean_and_bounded(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        harness = packet["current_canonical_harness"]

        self.assertEqual("pass", harness["summary_status"])
        self.assertEqual("Goal2847", harness["goal"])
        self.assertEqual(EXPECTED_COMMIT, harness["source_commit"])
        self.assertEqual(7, harness["artifact_count"])
        self.assertIn("does not authorize v2.5 release", harness["claim_boundary"])

        for name, artifact in harness["artifacts"].items():
            with self.subTest(name=name):
                self.assertEqual("pass", artifact["status"])
                self.assertEqual(EXPECTED_COMMIT, artifact["source_commit"])
                self.assertEqual([], artifact["source_dirty"])
                self.assertIn("NVIDIA RTX A5000", artifact["gpu"])

    def test_report_records_readiness_refresh_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal2849",
            "Goal2847",
            "Goal2848",
            "seven canonical v2.5 harness artifacts",
            "not a v2.5 release authorization",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, text)

    def test_review_and_consensus_accept_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "independent Gemini review",
            "`accept-with-boundary`",
            "not a v2.5 release authorization",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, review)

        for phrase in (
            "Consensus verdict: **accept-with-boundary**",
            "Codex",
            "Gemini",
            "not final v2.5 release consensus",
        ):
            self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()
