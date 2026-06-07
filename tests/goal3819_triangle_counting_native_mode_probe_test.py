from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOAL3818 = ROOT / "docs" / "reports" / "goal3818_current_benchmark_contract_smoke_a5000"
GOAL3819 = ROOT / "docs" / "reports" / "goal3819_triangle_counting_native_mode_probe_a5000"
REPORT = ROOT / "docs" / "reports" / "goal3819_triangle_counting_native_mode_probe_2026-06-07.md"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "triangle_counting" / "README.md"


class Goal3819TriangleCountingNativeModeProbeTest(unittest.TestCase):
    def test_native_mode_probe_is_faster_but_not_rt_core_authorized(self) -> None:
        auto_payload = json.loads((GOAL3818 / "triangle_counting.stdout.txt").read_text(encoding="utf-8"))
        native_payload = json.loads((GOAL3819 / "triangle_native.stdout.txt").read_text(encoding="utf-8"))

        auto_section = auto_payload["section"]
        native_section = native_payload["section"]
        self.assertEqual(auto_section["optix_graph_mode"], "auto")
        self.assertEqual(native_section["optix_graph_mode"], "native")
        self.assertLess(
            native_section["run_phases"]["query_raw_view_sec"],
            auto_section["run_phases"]["query_raw_view_sec"],
        )
        self.assertFalse(native_section["rt_core_accelerated"])
        self.assertFalse(native_payload["claim_boundary"]["triangle_count_rt_core_claim_authorized"])
        self.assertEqual(native_section["optix_performance"]["class"], "host_indexed_fallback")

    def test_report_and_readme_record_native_mode_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        for phrase in (
            "--optix-graph-mode native",
            "rt_core_accelerated=false",
            "triangle_count_rt_core_claim_authorized=false",
            "not public RT-core triangle-count evidence",
        ):
            self.assertIn(phrase, report)
        self.assertIn("--optix-graph-mode native", readme)
        self.assertIn("triangle_count_rt_core_claim_authorized=false", readme)


if __name__ == "__main__":
    unittest.main()
