from __future__ import annotations

import importlib
import json
from pathlib import Path
import tempfile
import unittest

from examples.benchmark_apps.triangle_counting import rt_graph_contract as contract_mod
from examples.benchmark_apps.triangle_counting import rtdl_triangle_counting_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py"
CONTRACT = ROOT / "examples/benchmark_apps/triangle_counting/rt_graph_contract.py"
REPORT = ROOT / "docs" / "reports" / "goal4457_v3_0_m61_triangle_cupy_no_host_columns_2026-06-16.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal4457_v3_0_m61_triangle_cupy_no_host_columns_200000_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")


def _has_cupy() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    return True


class Goal4457V30M61TriangleCuPyNoHostColumnsTest(unittest.TestCase):
    def test_app_requests_cupy_summary_without_host_columns(self) -> None:
        app_source = APP.read_text(encoding="utf-8")
        contract_source = CONTRACT.read_text(encoding="utf-8")

        self.assertIn(
            "build_rt_graph_triangle_summary_contract_cupy_binary(edge_file, materialize_host_columns=False)",
            app_source,
        )
        self.assertIn("materialize_host_columns: bool = True", contract_source)
        self.assertIn("RTGraphHostColumnPlaceholder", contract_source)
        self.assertIn('"host_columns_materialized": bool(materialize_host_columns)', contract_source)

    @unittest.skipUnless(_has_cupy(), "CuPy is not available")
    def test_live_cupy_app_route_skips_host_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            edge_file = Path(tmp) / "k4.edge"
            contract_mod.write_binary_edges(
                edge_file,
                (
                    (0, 1),
                    (0, 2),
                    (0, 3),
                    (1, 2),
                    (1, 3),
                    (2, 3),
                ),
            )
            payload = app.run_app(
                "rt_graph_2a1_generic_rt",
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                warmup=0,
                repeat=1,
            )

        self.assertTrue(payload["triangle_count_matches_oracle"])
        timing = payload["rt_graph_contract"]["partner_timing_ms"]
        self.assertFalse(timing["host_columns_materialized"])
        self.assertIn("device_count_summary_ms", timing)
        self.assertNotIn("download_needed_columns_ms", timing)

    def test_report_evidence_and_route_record_m61_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        route = routes.explain_current_benchmark_route("triangle_counting")

        self.assertIn("Goal4457", report)
        self.assertIn("materialize_host_columns=False", report)
        self.assertIn("not a triangle-counting RT-core speedup claim", report)
        self.assertEqual(4457, evidence["goal"])
        self.assertEqual("cupy_no_host_columns_summary_route", evidence["implementation"])
        self.assertFalse(evidence["comparison"]["host_columns_materialized"])
        self.assertGreater(evidence["rows"][0]["speedup_vs_m59_total"], 1.3)
        self.assertGreater(evidence["rows"][1]["speedup_vs_m59_total"], 1.3)
        self.assertIn("Goal4457", route["evidence_refs"])
        self.assertIn("host-column materialization", route["current_reader_decision"])
        self.assertFalse(route["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
