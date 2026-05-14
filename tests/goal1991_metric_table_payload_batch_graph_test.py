from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EXAMPLE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
REPORT = ROOT / "docs" / "reports" / "goal1991_metric_table_payload_batch_graph_2026-05-14.md"


class Goal1991MetricTablePayloadBatchGraphTest(unittest.TestCase):
    def test_metric_table_payload_batch_api_is_generic_and_public(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def metric_table_payload_to_partner_columns", adapters)
        self.assertIn("caller_supplied_metric_table_payload", adapters)
        self.assertIn("generic_metric_table_columns", adapters)
        self.assertIn("def partner_metric_table_reduce_batch", adapters)
        self.assertIn("def partner_metric_table_reduce_repeated_pattern", adapters)
        self.assertIn("assume_aligned_output", adapters)
        self.assertIn("generic_metric_table_batch_reductions", adapters)
        self.assertIn("not_called_partner_reference_only", adapters)
        self.assertIn("from .partner_adapters import metric_table_payload_to_partner_columns", init_text)
        self.assertIn("from .partner_adapters import partner_metric_table_reduce_repeated_pattern", init_text)
        self.assertIn('"metric_table_payload_to_partner_columns"', init_text)
        self.assertIn('"partner_metric_table_reduce_repeated_pattern"', init_text)
        self.assertIn('"partner_metric_table_reduce_batch"', init_text)

    def test_graph_control_path_uses_metric_table_payload_batch(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("partner_metric_table_reduce_repeated_pattern", text)
        self.assertIn("assume_aligned_output=True", text)
        self.assertIn('"partner_metric_table_reduce_repeated_pattern"', text)
        self.assertIn("GRAPH_SUM_METRIC_VALUES", text)
        self.assertIn("GRAPH_MAX_METRIC_VALUES", text)
        self.assertNotIn("GRAPH_RAWKERNEL_SOURCE", text)
        self.assertNotIn("rtdl_user_graph_summary", text)

    def test_cpu_fallback_still_matches_oracle(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--app",
                "graph_analytics",
                "--copies",
                "3",
                "--partner",
                "cpu_fallback",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertTrue(payload["matches_v1_8_python_rtdl_oracle"])
        self.assertEqual(payload["summary"]["bfs"]["discovered_edge_count"], 6)
        self.assertEqual(payload["summary"]["triangle_count"]["triangle_count"], 3)
        self.assertEqual(payload["summary"]["visibility_edges"]["blocked_edge_count"], 9)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("metric-table payload handoff", report)
        self.assertIn("batched metric-table reduction", report)
        self.assertIn("does not add graph traversal semantics to the native engine", report)
        self.assertIn("not a broad graph acceleration claim", report)


if __name__ == "__main__":
    unittest.main()
