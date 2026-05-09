from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "docs" / "reports" / "goal1609_v1_6_x_performance_roadmap_2026-05-09.md"
REVIEWS = (
    ROOT / "docs" / "reviews" / "goal1609_v1_6_x_performance_roadmap_claude_review_2026-05-09.md",
    ROOT / "docs" / "reviews" / "goal1609_v1_6_x_performance_roadmap_gemini_review_2026-05-09.md",
    ROOT / "docs" / "reviews" / "goal1609_v1_6_x_performance_roadmap_3ai_consensus_2026-05-09.md",
)


class Goal1609V16XPerformanceRoadmapTest(unittest.TestCase):
    def test_roadmap_exists_and_names_version_slots(self):
        text = ROADMAP.read_text(encoding="utf-8")
        for version in [f"v1.6.{index}" for index in range(1, 11)]:
            with self.subTest(version=version):
                self.assertIn(version, text)

    def test_roadmap_has_required_workstreams(self):
        text = ROADMAP.read_text(encoding="utf-8")
        for phrase in [
            "Measurement Before Optimization",
            "Prepared Host Output And Thin Results",
            "Reduced-Copy Host Input",
            "`COLLECT_K_BOUNDED`",
            "OptiX/NVIDIA RT-Core Performance",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_roadmap_blocks_unsupported_claims(self):
        text = ROADMAP.read_text(encoding="utf-8")
        for phrase in [
            "does not authorize a release tag",
            "no true zero-copy wording",
            "broad RTX/GPU speedup wording",
            "whole-app speedup wording",
            "stable `COLLECT_K_BOUNDED` promotion by itself",
            "Do not start a paid pod for roadmap writing",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_first_concrete_goals_are_ordered_before_pod_packet(self):
        text = ROADMAP.read_text(encoding="utf-8")
        self.assertLess(text.index("Goal1610"), text.index("Goal1614"))
        self.assertIn("prepare the first RTX pod packet only after Goals1610-1613", text)

    def test_external_review_notes_were_resolved_in_roadmap(self):
        text = ROADMAP.read_text(encoding="utf-8")
        for phrase in [
            "must be re-sampled in the later v1.6.8 package",
            "Include the v1.6.6 session paths",
            "A positive control means",
            "Split scene preparation, probe/ray packing",
            "migration pattern from compatibility rows to thin views",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_three_ai_consensus_exists(self):
        for path in REVIEWS:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)
        consensus = REVIEWS[-1].read_text(encoding="utf-8")
        for phrase in [
            "Codex Verdict",
            "Claude Verdict",
            "Gemini Verdict",
            "ACCEPT",
            "Goal1610",
            "does not authorize",
            "stable `COLLECT_K_BOUNDED` promotion",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()
