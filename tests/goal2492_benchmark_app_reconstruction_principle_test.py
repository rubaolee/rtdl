from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2492_benchmark_app_reconstruction_principle_and_raydb_scope_2026-05-22.md"
BENCHMARK_README = ROOT / "examples/v2_0/research_benchmarks/README.md"
CLAUDE_REVIEW = ROOT / "docs/reviews/goal2492_claude_review_benchmark_app_reconstruction_principle_2026-05-22.md"
CONSENSUS = ROOT / "docs/reviews/goal2492_codex_claude_consensus_benchmark_app_reconstruction_principle_2026-05-22.md"


class Goal2492BenchmarkAppReconstructionPrincipleTest(unittest.TestCase):
    def test_report_locks_partial_app_reconstruction_boundary(self) -> None:
        text = REPORT.read_text()
        self.assertIn("benchmark apps are reconstruction instruments", text.lower())
        self.assertIn("smaller slice is enough", text)
        self.assertIn("must force a concrete", text)
        self.assertIn("language/runtime improvement", text)
        self.assertIn("not full paper-system reproduction", BENCHMARK_README.read_text())

    def test_report_scopes_raydb_as_database_shaped_rt_pressure(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "table-like query columns",
            "declarative query-result mode selection",
            "prepared scene or prepared index lifetime",
            "columnar memory descriptors",
            "query-plan lowering in Python",
        ]:
            self.assertIn(phrase, text)

    def test_report_preserves_native_app_agnostic_boundary(self) -> None:
        text = REPORT.read_text()
        self.assertIn("native engines stay app-name-free", text)
        self.assertIn("app-specific native engine ABI", text)
        self.assertIn("native `raydb`, `sql`, `table`, or `database` vocabulary", text)
        self.assertIn("no authors-code comparison", text.lower())

    def test_research_benchmark_readme_points_to_goal2492(self) -> None:
        text = BENCHMARK_README.read_text()
        self.assertIn("benchmark apps are reconstruction instruments", text.lower())
        self.assertIn("missing RTDL primitive", text)
        self.assertIn("Goal2492 Benchmark-App Reconstruction Principle", text)

    def test_consensus_records_external_review_and_next_step(self) -> None:
        review = CLAUDE_REVIEW.read_text()
        consensus = CONSENSUS.read_text()
        self.assertIn("APPROVE_WITH_NON_BLOCKING_NOTES", review)
        self.assertIn("APPROVE. Goal2492 can be used", consensus)
        self.assertIn("Goal2493: RayDB local/external code intake", consensus)
        self.assertIn("CPU/Embree", consensus)
        self.assertIn("reconstruction slice", consensus)


if __name__ == "__main__":
    unittest.main()
