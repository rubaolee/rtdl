from __future__ import annotations

import unittest

from examples import rtdl_graph_analytics_app
from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count


class Goal1129GraphPhaseSplitContractTest(unittest.TestCase):
    def test_bfs_summary_reports_query_and_summary_phases(self) -> None:
        payload = rtdl_graph_bfs.run_backend(
            "cpu_python_reference",
            copies=2,
            output_mode="summary",
        )

        self.assertEqual(payload["rows"], [])
        self.assertIn("input_construction_sec", payload["run_phases"])
        self.assertIn("query_and_materialize_sec", payload["run_phases"])
        self.assertIn("native_summary_postprocess_sec", payload["run_phases"])
        self.assertGreaterEqual(payload["run_phases"]["query_and_materialize_sec"], 0.0)

    def test_triangle_summary_reports_query_and_summary_phases(self) -> None:
        payload = rtdl_graph_triangle_count.run_backend(
            "cpu_python_reference",
            copies=2,
            output_mode="summary",
        )

        self.assertEqual(payload["rows"], [])
        self.assertIn("input_construction_sec", payload["run_phases"])
        self.assertIn("query_and_materialize_sec", payload["run_phases"])
        self.assertIn("native_summary_postprocess_sec", payload["run_phases"])
        self.assertGreaterEqual(payload["run_phases"]["native_summary_postprocess_sec"], 0.0)

    def test_visibility_summary_reports_observable_phase_split(self) -> None:
        payload = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            scenario="visibility_edges",
            copies=3,
            output_mode="summary",
        )
        section = payload["sections"]["visibility_edges"]

        self.assertEqual(section["rows"], [])
        self.assertIn("input_construction_sec", section["run_phases"])
        self.assertIn("query_visibility_pair_rows_sec", section["run_phases"])
        self.assertIn("summary_postprocess_sec", section["run_phases"])
        self.assertIn("query_visibility_pair_rows_sec", payload["graph_phase_totals_sec"])
        self.assertIn("not public RTX speedup claims", payload["phase_contract"])

    def test_unified_graph_phase_totals_include_all_sections(self) -> None:
        payload = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            scenario="all",
            copies=2,
            output_mode="summary",
        )

        self.assertIn("query_and_materialize_sec", payload["graph_phase_totals_sec"])
        self.assertIn("query_visibility_pair_rows_sec", payload["graph_phase_totals_sec"])
        self.assertIn("native_summary_postprocess_sec", payload["graph_phase_totals_sec"])
        self.assertTrue(payload["native_continuation_active"])


if __name__ == "__main__":
    unittest.main()
