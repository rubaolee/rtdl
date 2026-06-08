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
            "rtdl.v2_10.benchmark_adequacy_after_goal3841.v1",
        )
        self.assertEqual(rt.current_benchmark_adequacy(), v2_9_benchmark_adequacy())
        self.assertEqual(
            rt.summarize_current_benchmark_adequacy(),
            summarize_v2_9_benchmark_adequacy(),
        )
        self.assertEqual(
            rt.validate_current_benchmark_adequacy(),
            validate_v2_9_benchmark_adequacy(),
        )
        self.assertEqual(rt.validate_current_benchmark_adequacy()["status"], "accept")

    def test_active_learner_docs_use_v2_10_current_surface(self) -> None:
        for path in ACTIVE_DOCS:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("current v2.8", text, path.relative_to(ROOT))
            self.assertNotIn("RTDL v2.8 Tutorials", text, path.relative_to(ROOT))
            self.assertNotIn("RTDL v2.8 Research Benchmarks", text, path.relative_to(ROOT))
        self.assertIn("current v2.10 source-tree RTDL surface", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("RTDL v2.10 Tutorials", (ROOT / "docs" / "tutorials" / "README.md").read_text(encoding="utf-8"))
        self.assertIn(
            "RTDL v2.10 Research Benchmarks",
            (ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md").read_text(encoding="utf-8"),
        )

    def test_partner_docs_point_to_current_aliases_and_updated_roles(self) -> None:
        partner = (ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md").read_text(encoding="utf-8")
        matrix = (ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md").read_text(encoding="utf-8")

        self.assertIn("current_benchmark_adequacy", partner)
        self.assertIn("summarize_current_benchmark_adequacy", matrix)
        self.assertNotIn("v2_8_benchmark_matrix()", partner)
        self.assertNotIn("v2_8_benchmark_matrix()", matrix)
        self.assertIn("Numba now has measured prepared-repeat component-continuation coverage", partner)
        self.assertIn("Goal3834/3838 no-RawKernel scalar-count coverage", matrix)
        self.assertIn("Goal3835 current-head prepared-repeat evidence", matrix)
        self.assertIn("prepared_optix_ranked_summary", matrix)
        self.assertIn("--optix-graph-mode native", matrix)

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
