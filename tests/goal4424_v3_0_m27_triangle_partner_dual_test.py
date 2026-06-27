from __future__ import annotations

import json
from pathlib import Path
import unittest

from examples.benchmark_apps.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as app,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py"
CONTRACT = ROOT / "examples/benchmark_apps/triangle_counting/rt_graph_contract.py"
RUNNER = ROOT / "scripts/v3_0_m27_triangle_partner_dual_measure.py"
REPORT = ROOT / "docs/reports/goal4424_v3_0_m27_triangle_partner_dual_2026-06-15.md"
EVIDENCE_JSONS = {
    5_000: ROOT / "docs/reports/goal4424_v3_0_m27_triangle_partner_dual_cliques5000_2026-06-15.json",
    50_000: ROOT / "docs/reports/goal4424_v3_0_m27_triangle_partner_dual_cliques50000_2026-06-15.json",
    200_000: ROOT / "docs/reports/goal4424_v3_0_m27_triangle_partner_dual_cliques200000_2026-06-15.json",
}


class Goal4424V30M27TrianglePartnerDualTest(unittest.TestCase):
    def test_triangle_counting_source_exposes_numba_summary_partner(self) -> None:
        source = APP.read_text(encoding="utf-8")
        contract = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("build_rt_graph_triangle_summary_contract_numba_binary", contract)
        self.assertIn("direct_binary_numpy_summary_then_numba_device_upload", contract)
        self.assertIn("cpu_contract_then_numba_device_upload", contract)
        self.assertIn("cuda.to_device", contract)
        self.assertIn("partner not in {\"cupy\", \"numba\"}", source)
        self.assertIn("_build_rt_graph_2a1_numba_device_geometry", source)
        self.assertIn("_build_rt_graph_1a2_numba_device_geometry", source)
        self.assertIn("numba_device_columns", source)
        self.assertNotIn("--partner cupy currently supports only", source)

    def test_prepared_session_descriptor_distinguishes_cupy_and_numba_device_columns(self) -> None:
        cupy = app.describe_rt_graph_v2_4_prepared_session(
            backend="optix",
            paper_method="RT-2A1",
            primitive_count=8,
            ray_count=4,
            device_column_summary=True,
            partner="cupy",
        )
        numba = app.describe_rt_graph_v2_4_prepared_session(
            backend="optix",
            paper_method="RT-2A1",
            primitive_count=8,
            ray_count=4,
            device_column_summary=True,
            partner="numba",
        )
        self.assertEqual(
            {buffer["source_protocol"] for buffer in cupy["input_buffers"]},
            {"cupy_device_columns"},
        )
        self.assertEqual(
            {buffer["source_protocol"] for buffer in numba["input_buffers"]},
            {"numba_device_columns"},
        )

    def test_runner_and_report_capture_m27_boundary(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        for phrase in (
            "rt_graph_2a1_generic_rt,rt_graph_1a2_generic_rt",
            "cupy,numba",
            "signature_match_by_mode",
            "cpu_contract_then_numba_device_upload",
            "direct_binary_numpy_summary_then_numba_device_upload",
            "v2_4_input_source_protocols",
            "prewarm",
        ):
            self.assertIn(phrase, runner)

        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Triangle Counting Partner Dual-Path Closure",
            "CuPy remains the high-performance GPU graph-contract builder",
            "Numba route is deliberately bounded",
            "Measured Matrix",
            "numba_device_columns",
            "parameters.prewarm.enabled",
            "cliques200000",
            "public whole-app speedup wording",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_records_both_modes_and_partners_at_three_scales(self) -> None:
        for cliques, evidence_json in EVIDENCE_JSONS.items():
            self.assertTrue(evidence_json.exists(), f"missing M27 evidence: {evidence_json}")
            payload = json.loads(evidence_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["parameters"]["cliques"], cliques)
            self.assertEqual(payload["parameters"]["expected_triangle_count"], cliques * 4)
            self.assertTrue(payload["parameters"]["prewarm"]["enabled"])
            self.assertTrue(payload["comparison"]["all_triangle_counts_match_oracle"])
            self.assertEqual(set(payload["comparison"]["partners_covered"]), {"cupy", "numba"})
            self.assertEqual(
                set(payload["comparison"]["modes_covered"]),
                {"rt_graph_1a2_generic_rt", "rt_graph_2a1_generic_rt"},
            )
            self.assertTrue(all(payload["comparison"]["signature_match_by_mode"].values()))
            rows = {(row["mode"], row["partner"]): row for row in payload["rows"]}
            self.assertEqual(len(rows), 4)
            for mode in ("rt_graph_1a2_generic_rt", "rt_graph_2a1_generic_rt"):
                self.assertIsNone(rows[(mode, "cupy")]["partner_construction_mode"])
                self.assertEqual(
                    rows[(mode, "numba")]["partner_construction_mode"],
                    "cpu_contract_then_numba_device_upload",
                )
                self.assertIn("numba_device_columns", rows[(mode, "numba")]["v2_4_input_source_protocols"])
                self.assertTrue(rows[(mode, "numba")]["triangle_count_matches_oracle"])


if __name__ == "__main__":
    unittest.main()
