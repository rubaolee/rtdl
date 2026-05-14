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
REPORT = ROOT / "docs" / "reports" / "goal2022_graph_compressed_metric_pattern_perf_2026-05-14.md"
ARTIFACT_1000 = ROOT / "docs" / "reports" / "goal2022_pod_graph_host_compressed_metric_pattern_1000.json"
ARTIFACT_100K = ROOT / "docs" / "reports" / "goal2022_pod_graph_host_compressed_metric_pattern_100000_v2only.json"


class Goal2022GraphCompressedMetricPatternPerfTest(unittest.TestCase):
    def test_generic_repeated_metric_pattern_helper_is_public(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def partner_metric_table_reduce_repeated_pattern", adapters)
        self.assertIn("repeat_count must be non-negative", adapters)
        self.assertIn("assume_aligned_output", adapters)
        self.assertIn("aligned repeated metric pattern requires one value per output metric key", adapters)
        self.assertIn("from .partner_adapters import partner_metric_table_reduce_repeated_pattern", init_text)
        self.assertIn('"partner_metric_table_reduce_repeated_pattern"', init_text)

    def test_graph_cupy_path_uses_compressed_repeated_metric_pattern(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("partner_metric_table_reduce_repeated_pattern", text)
        self.assertIn("GRAPH_SUM_METRIC_VALUES", text)
        self.assertIn("GRAPH_MAX_METRIC_VALUES", text)
        self.assertIn("assume_aligned_output=True", text)
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

    def test_pod_artifacts_record_correctness_and_scale_behavior(self) -> None:
        payload_1000 = json.loads(ARTIFACT_1000.read_text(encoding="utf-8"))
        row_1000 = payload_1000["results"][0]

        self.assertEqual(row_1000["app"], "graph_analytics")
        self.assertTrue(payload_1000["all_match_v1_8_python_rtdl_oracle"])
        self.assertTrue(row_1000["matches_v1_8_python_rtdl_oracle"])
        self.assertLess(row_1000["v2_vs_v1_8_ratio"], 0.0001)

        payload_100k = json.loads(ARTIFACT_100K.read_text(encoding="utf-8"))
        row_100k = payload_100k["results"][0]
        self.assertEqual(row_100k["copies"], 100000)
        self.assertIsNone(row_100k["v1_8_python_rtdl_wall"])
        self.assertLess(row_100k["v2_rawkernel_wall"]["median_s"], 0.001)
        summary_100k = row_100k["v2_payload_signature"]["summary"]
        self.assertEqual(summary_100k["bfs"]["discovered_edge_count"], 200000)
        self.assertEqual(summary_100k["triangle_count"]["triangle_count"], 100000)

    def test_report_keeps_graph_boundary_tight(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("not broad graph traversal acceleration", text)
        self.assertIn("does not add BFS", text)
        self.assertIn("not merely device-side materialization", text)
        self.assertIn("v2.0 release authorization still requires", text)


if __name__ == "__main__":
    unittest.main()
