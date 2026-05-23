from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORTS = REPO_ROOT / "docs" / "reports"


class Goal2529FinishedBenchmarkAppsConsensusTest(unittest.TestCase):
    def test_consensus_artifacts_exist(self) -> None:
        required = [
            "goal2529_finished_benchmark_apps_consensus_packet_2026-05-23.md",
            "goal2529_claude_review_finished_benchmark_apps_2026-05-23.md",
            "goal2529_gemini_review_finished_benchmark_apps_2026-05-23.md",
            "goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md",
        ]
        for name in required:
            with self.subTest(name=name):
                path = REPORTS / name
                self.assertTrue(path.exists(), f"missing {path}")
                self.assertGreater(path.stat().st_size, 100, f"empty or truncated {path}")

    def test_final_consensus_records_five_finished_apps_and_boundaries(self) -> None:
        text = (REPORTS / "goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md").read_text()
        normalized = " ".join(text.split())
        for phrase in [
            "Final verdict: `ACCEPT-WITH-BOUNDARY`",
            "Hausdorff/X-HD-style",
            "Spatial RayJoin-style",
            "RT-DBSCAN-style",
            "Robot-collision-style",
            "RayDB-style",
            "research benchmarks",
            "reconstruction instruments",
            "current-main/v2.1 performance refresh is pending",
            "authors-code parity",
            "full paper reproduction",
            "broad speedup wins",
            "native Embree/OptiX paths app-name-free",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_external_reviews_have_acceptable_verdicts(self) -> None:
        claude = (REPORTS / "goal2529_claude_review_finished_benchmark_apps_2026-05-23.md").read_text()
        gemini = (REPORTS / "goal2529_gemini_review_finished_benchmark_apps_2026-05-23.md").read_text()
        self.assertIn("ACCEPT", claude)
        self.assertIn("ACCEPT-WITH-BOUNDARY", gemini)
        self.assertIn("Hausdorff", gemini)
        self.assertIn("App-agnostic native engine boundary", claude)


if __name__ == "__main__":
    unittest.main()
