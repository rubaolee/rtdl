from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt
from rtdsl.v2_9_benchmark_adequacy import (
    summarize_v2_9_benchmark_adequacy,
    validate_v2_9_benchmark_adequacy,
    v2_9_benchmark_adequacy,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3812_current_benchmark_docs_and_adequacy_aliases_2026-06-07.md"
ACTIVE_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "tutorials" / "README.md",
    ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md",
    ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md",
    ROOT / "docs" / "learn" / "primitive_discovery_workflow.md",
    ROOT / "docs" / "learn" / "prepared_execution_pattern.md",
    ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md",
)


class Goal3812CurrentBenchmarkDocsAndAdequacyAliasesTest(unittest.TestCase):
    def test_current_adequacy_aliases_match_versioned_source(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ADEQUACY_VERSION,
            "rtdl.v3_0.current_benchmark_adequacy.goal4447.v1",
        )
        self.assertNotEqual(rt.current_benchmark_adequacy(), v2_9_benchmark_adequacy())
        self.assertEqual(summarize_v2_9_benchmark_adequacy()["version"], "rtdl.v2_10.benchmark_adequacy_after_goal3936.v1")
        self.assertEqual(validate_v2_9_benchmark_adequacy()["status"], "accept")
        self.assertEqual(rt.validate_current_benchmark_adequacy()["status"], "accept")
        self.assertIn("Goal4447", rt.summarize_current_benchmark_adequacy()["claim_boundary"])

    def test_active_learner_docs_use_v2_10_current_surface(self) -> None:
        for path in ACTIVE_DOCS:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("current v2.8", text, path.relative_to(ROOT))
            self.assertNotIn("RTDL v2.8 Tutorials", text, path.relative_to(ROOT))
            self.assertNotIn("RTDL v2.8 Research Benchmarks", text, path.relative_to(ROOT))
        self.assertIn("current v2.14 source-tree RTDL surface", (ROOT / "README.md").read_text(encoding="utf-8"))
        tutorials = ROOT / "docs" / "tutorials" / "README.md"
        if tutorials.exists():
            self.assertIn("RTDL v2.14 Tutorials", tutorials.read_text(encoding="utf-8"))
        research_readme = ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md"
        if research_readme.exists():
            self.assertIn("RTDL v2.14 Research Benchmarks", research_readme.read_text(encoding="utf-8"))

    def test_partner_docs_point_to_current_aliases_and_updated_roles(self) -> None:
        partner = (ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md").read_text(encoding="utf-8")
        matrix = (ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md").read_text(encoding="utf-8")

        self.assertIn("current_benchmark_adequacy", partner)
        self.assertIn("summarize_current_benchmark_adequacy", matrix)
        self.assertNotIn("v2_8_benchmark_matrix()", partner)
        self.assertNotIn("v2_8_benchmark_matrix()", matrix)
        self.assertIn("Goal4447", matrix)
        self.assertIn("Goal4445", matrix)
        self.assertIn("Goal4444", matrix)
        self.assertIn("current_benchmark_adequacy", partner)
        self.assertIn("prepared_ranked_summary_graph_partner_bridge", matrix)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3812",
            "current_benchmark_adequacy",
            "v2.10 adequacy",
            "Historical `v2_8_*` and `v2_9_*` helpers remain available",
            "No native engine code changed",
            "No public speedup",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
