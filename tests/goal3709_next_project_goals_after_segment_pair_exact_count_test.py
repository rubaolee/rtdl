import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3709_next_project_goals_after_segment_pair_exact_count_2026-06-07.md"


class Goal3709NextProjectGoalsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = REPORT.read_text(encoding="utf-8")

    def test_report_exists_and_tracks_current_lsi_evidence(self):
        self.assertIn("Goal3705 prepared-left one-pass exact count", self.text)
        self.assertIn("0.0010864129", self.text)
        self.assertIn("0.833929x", self.text)
        self.assertIn("Goal3708 no-telemetry negative probe", self.text)
        self.assertIn("0.777436x", self.text)

    def test_next_goals_are_major_not_minor_tuning(self):
        required = [
            "RayJoin Same-Contract Composite Rebaseline",
            "Generic Dense-Boundary Exact Scalar Count",
            "Segment-Pair Exact Count Final Push",
            "Numba Reference Paths For Partner-Needed Apps",
            "Seconds-Scale Benchmark Matrix",
            "AMD HIP RT Preparation",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_report_preserves_app_agnostic_and_claim_boundaries(self):
        self.assertIn("native engine must stay generic and app-agnostic", self.text)
        self.assertIn("No \"RTDL beats RayJoin\" claim", self.text)
        self.assertIn("Claim-boundary flags remain false", self.text)
        self.assertIn("Codex plus Claude plus Gemini", self.text)

    def test_immediate_next_goal_is_parallel_rebaseline_and_dense_boundary(self):
        immediate = self.text.split("## Immediate Next Goal", 1)[1]
        self.assertIn("Start with Goal 1 and Goal 2 in parallel", immediate)
        self.assertIn("clean RayJoin app-level answer", immediate)
        self.assertIn("biggest generic performance gap", immediate)

    def test_no_public_release_or_paper_reproduction_authorization(self):
        forbidden_patterns = [
            r"\bRTDL beats RayJoin\b(?!\" claim)",
            r"\brelease authorized\b",
            r"\bpaper reproduction claim authorized\b",
            r"\btrue zero-copy\b.*\bdelivered\b",
        ]
        lowered = self.text.lower()
        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, lowered))


if __name__ == "__main__":
    unittest.main()
