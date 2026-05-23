from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports"


class Goal2571BenchmarkAppGoalAuditTest(unittest.TestCase):
    def test_audit_artifacts_exist(self) -> None:
        required = [
            "goal2571_benchmark_app_goal_audit_2026-05-23.md",
            "goal2571_claude_benchmark_app_goal_audit_review_2026-05-23.md",
            "goal2571_gemini_benchmark_app_goal_audit_review_2026-05-23.md",
            "goal2571_3ai_consensus_benchmark_app_goal_audit_2026-05-23.md",
        ]
        for name in required:
            with self.subTest(name=name):
                path = REPORTS / name
                self.assertTrue(path.exists(), f"missing {path}")
                self.assertGreater(path.stat().st_size, 500, f"truncated {path}")

    def test_audit_covers_goal_ranges_and_app_closeouts(self) -> None:
        text = (REPORTS / "goal2571_benchmark_app_goal_audit_2026-05-23.md").read_text()
        for phrase in [
            "Goals2392-2478",
            "Goals2479-2491",
            "Goals2492-2528",
            "Goals2530-2550",
            "Goals2552-2570",
            "goal2478_rt_dbscan_project_completion",
            "goal2491_robot_collision_benchmark_app_closeout",
            "goal2528_raydb_style_benchmark_app_closeout",
            "goal2550_barnes_hut_final_performance_and_closeout",
            "Compatibility Debt Versus Review Debt",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_external_reviews_have_acceptable_verdicts(self) -> None:
        claude = (
            REPORTS / "goal2571_claude_benchmark_app_goal_audit_review_2026-05-23.md"
        ).read_text()
        gemini = (
            REPORTS / "goal2571_gemini_benchmark_app_goal_audit_review_2026-05-23.md"
        ).read_text()
        self.assertIn("ACCEPT-WITH-BOUNDARY", claude)
        self.assertIn("Verdict: ACCEPT", gemini)
        self.assertIn("Goal2491", claude)
        self.assertIn("Barnes-Hut", claude)
        self.assertIn("Compatibility DB Aliases", gemini)

    def test_final_consensus_preserves_boundaries(self) -> None:
        text = (
            REPORTS
            / "goal2571_3ai_consensus_benchmark_app_goal_audit_2026-05-23.md"
        ).read_text()
        for phrase in [
            "Final verdict: `ACCEPT-WITH-BOUNDARY`",
            "no unresolved review or consensus debt",
            "internal-benchmark-apps-2026-05-23",
            "Goal2529's 3-AI consensus",
            "Goal2551's 3-AI benchmark-wave rethinking",
            "Compatibility Debt",
            "not a same-contract speedup ratio",
            "native GPU validation",
            "not stable external ABI claims",
            "Do not publish broad speedup claims",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
