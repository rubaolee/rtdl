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
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1972_graph_metric_table_partner_reduction_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1972_pod_graph_metric_table_control_perf.json"


class Goal1972GraphMetricTablePartnerReductionTest(unittest.TestCase):
    def test_partner_metric_table_reduce_helper_is_public_and_generic(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def partner_metric_table_reduce_by_key", adapters)
        self.assertIn("def metric_table_payload_to_partner_columns", adapters)
        self.assertIn("def partner_metric_table_reduce_batch", adapters)
        self.assertIn("caller_supplied_metric_table_payload", adapters)
        self.assertIn("generic_metric_table_batch_reductions", adapters)
        self.assertIn("metric_keys and values must have the same length", adapters)
        self.assertIn("metric_keys must be present in output_metric_keys", adapters)
        self.assertIn("torch.searchsorted", adapters)
        self.assertIn("cupy.searchsorted", adapters)
        self.assertIn("reduce must be 'sum', 'max', or 'min'", adapters)
        self.assertIn("from .partner_adapters import partner_metric_table_reduce_by_key", init_text)
        self.assertIn("from .partner_adapters import metric_table_payload_to_partner_columns", init_text)
        self.assertIn('"partner_metric_table_reduce_batch"', init_text)
        self.assertIn('"partner_metric_table_reduce_by_key"', init_text)

    def test_graph_control_path_uses_metric_table_not_closed_form_rawkernel(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("GRAPH_SUM_METRIC_IDS", text)
        self.assertIn("GRAPH_MAX_METRIC_IDS", text)
        self.assertIn("metric_table_payload_to_partner_columns", text)
        self.assertIn("partner_metric_table_reduce_batch", text)
        self.assertIn('"reduce": "sum"', text)
        self.assertIn('"reduce": "max"', text)
        self.assertNotIn("GRAPH_RAWKERNEL_SOURCE", text)
        self.assertNotIn("rtdl_user_graph_summary", text)

    def test_graph_cpu_fallback_still_matches_v1_8_oracle(self) -> None:
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
        self.assertEqual(payload["summary"]["bfs"]["max_level"], 1)
        self.assertEqual(payload["summary"]["triangle_count"]["triangle_count"], 3)
        self.assertEqual(payload["summary"]["visibility_edges"]["blocked_edge_count"], 9)

    def test_report_and_preflight_record_goal1972(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("partner_metric_table_reduce_by_key", report)
        self.assertIn("no longer a one-off RawKernel", report)
        self.assertIn("does not add graph semantics to the native engine", report)
        self.assertIn("0.000003x", report)
        self.assertIn("general graph traversal acceleration claim", report)
        self.assertIn("tests.goal1972_graph_metric_table_partner_reduction_test", preflight)

    def test_pod_artifact_records_graph_metric_table_correctness(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        row = payload["results"][0]

        self.assertEqual(row["app"], "graph_analytics")
        self.assertTrue(payload["all_match_v1_8_python_rtdl_oracle"])
        self.assertTrue(row["matches_v1_8_python_rtdl_oracle"])
        self.assertLess(row["v2_vs_v1_8_ratio"], 0.001)


if __name__ == "__main__":
    unittest.main()
