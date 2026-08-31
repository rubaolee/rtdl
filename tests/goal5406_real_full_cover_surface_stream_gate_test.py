from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5406_real_full_cover_surface_stream_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5406_real_full_cover_surface_stream_gate_pod.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5406_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load Goal5406 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5406RealFullCoverSurfaceStreamGateTest(unittest.TestCase):
    def test_offload_filter_keeps_only_kind2_rows(self) -> None:
        module = _load_module()
        table = {
            "columns": {
                "frontier_kind_codes": np.asarray([1, 2, 3, 2], dtype=np.int64),
                "query_point_ids": np.asarray([10, 11, 12, 13], dtype=np.int64),
                "query_row_ids": np.asarray([0, 1, 2, 3], dtype=np.int64),
                "cell_ids": np.asarray([100, 101, 102, 103], dtype=np.int64),
            }
        }
        rows = module.offload_rows_from_frontier_row_table(table)
        self.assertEqual([11, 13], rows["source_ids"].tolist())
        self.assertEqual([101, 103], rows["cell_ids"].tolist())
        self.assertEqual([1, 3], rows["query_row_ids"].tolist())

    def test_summary_uses_generic_active_query_trace_contract(self) -> None:
        module = _load_module()
        frontier = {
            "row_table": {
                "columns": {
                    "frontier_kind_codes": np.asarray([2, 2, 1], dtype=np.int64),
                    "query_point_ids": np.asarray([4, 5, 6], dtype=np.int64),
                    "query_row_ids": np.asarray([0, 1, 2], dtype=np.int64),
                    "cell_ids": np.asarray([40, 50, 60], dtype=np.int64),
                }
            }
        }
        summary = module.summarize_full_cover_frontier(frontier=frontier, active_count=7)
        self.assertEqual("rtdl.generic.active_query_status_trace_summary.v1", summary["schema"])
        self.assertEqual(2, summary["row_count"])
        self.assertEqual(2, summary["status_count_offloading"])
        self.assertEqual(7, summary["active_query_count"])
        self.assertEqual(["source_ids", "cell_ids"], summary["hash_columns"])
        self.assertEqual([4, 5], summary["samples"]["source_ids"])
        self.assertEqual([40, 50], summary["samples"]["cell_ids"])
        self.assertEqual("none", summary["app_semantics"])

    def test_runner_does_not_claim_full_lb_or_figures(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"explicit_lb_support_claimed": False', source)
        self.assertIn('"figure7_reproduction_claimed": False', source)
        self.assertIn('"figure11_reproduction_claimed": False', source)
        self.assertIn('"full_xhd_paper_reproduction_claimed": False', source)
        self.assertNotIn("hard-code 62", source.lower())

    @unittest.skipUnless(ARTIFACT.exists(), "Goal5406 POD artifact not present")
    def test_pod_artifact_records_real_full_cover_delta_without_lb_claim(self) -> None:
        import json

        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "rtdl.paper_reproduction.xhd.goal5406.real_full_cover_surface_stream_gate.v1",
            payload["schema"],
        )
        comparison = payload["comparison"]
        self.assertTrue(comparison["active_query_count_parity"])
        self.assertEqual(24508120, comparison["rtdl_full_cover_rows"])
        self.assertTrue(comparison["full_cover_count_matched_goal5365"])
        self.assertEqual(27133990, comparison["author_raw_offload_rows"])
        self.assertEqual(2625870, comparison["row_delta_author_minus_rtdl_full_cover"])
        self.assertFalse(comparison["row_count_parity_with_author"])
        self.assertFalse(payload["claim_boundary"]["explicit_lb_support_claimed"])
        self.assertFalse(payload["claim_boundary"]["figure7_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()
