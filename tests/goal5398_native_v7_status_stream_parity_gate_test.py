from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5398_native_v7_status_stream_parity_gate.py"
)
POD_ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5398_native_v7_status_stream_parity_gate_pod.json"
)


class Goal5398NativeV7StatusStreamParityGateTest(unittest.TestCase):
    def test_script_uses_native_v7_frontdoor_and_not_bridge_lowering(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("collect_active_query_status_stream_3d_optix", source)
        self.assertIn("rtdl.paper_reproduction.xhd.goal5398.native_v7_status_stream_parity_gate.v1", source)
        self.assertIn("active_query_status_trace_summary_numpy_columns", source)
        self.assertNotIn("active_query_status_from_frontier_row_table_numpy_columns(", source)
        self.assertIn("explicit_lb_support_claimed", source)
        self.assertIn("hash_sample_parity_claimed", source)

    def test_summarizer_detects_author_mismatch_without_claiming_lb_support(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("goal5398_gate", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)

        native_status = {
            "columns": {
                "active_queue_indices": np.asarray([0, 1, 0], dtype=np.int64),
                "query_row_ids": np.asarray([0, 1, 0], dtype=np.int64),
                "source_ids": np.asarray([10, 11, 10], dtype=np.int64),
                "cell_ids": np.asarray([100, 100, 101], dtype=np.int64),
                "status_codes": np.asarray([2, 2, 3], dtype=np.int64),
                "transition_phase_codes": np.asarray([2, 2, 3], dtype=np.int64),
                "current_best_before_sq": np.asarray([1.0, 2.0, 3.0], dtype=np.float64),
                "current_best_after_sq": np.asarray([1.0, 2.0, 3.0], dtype=np.float64),
            },
            "contract": "generic_active_query_status_stream_native_abi_v1",
            "native_generic_symbol": "rtdl_optix_collect_active_query_status_stream_3d_v1",
        }
        author = {
            "active_in_queue_size": 2,
            "raw_offload_rows_before_sort_reduce": 3,
            "status_count_offloading_append": 3,
            "feedback_update_count": 1,
            "batch_0": {
                "raw_offload_row_hash": 12345,
                "raw_offload_row_sample_point_ids": [10],
                "raw_offload_row_sample_cell_ids": [100],
            },
        }
        summary = module.summarize_v7_status_stream(
            native_status=native_status,
            active_query_count=2,
            author_trace_v2=author,
        )
        comparison = summary["comparison_to_author"]
        self.assertTrue(comparison["active_query_count_parity"])
        self.assertEqual(comparison["rtdl_v7_offload_rows"], 2)
        self.assertFalse(comparison["row_count_parity"])
        self.assertFalse(comparison["status_count_offloading_parity"])
        self.assertFalse(comparison["hash_parity"])
        self.assertIs(summary["claim_boundary"]["explicit_lb_support_claimed"], False)
        self.assertIs(summary["claim_boundary"]["row_count_parity_claimed"], False)

    def test_author_trace_reader_requires_v2_batch_fields(self) -> None:
        import importlib.util
        import tempfile

        spec = importlib.util.spec_from_file_location("goal5398_gate", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.json"
            path.write_text(json.dumps({"author_lb_trace": {}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "author_lb_trace_v2"):
                module._read_author_trace_v2(path)

    def test_pod_artifact_if_present_keeps_claim_boundary(self) -> None:
        if not POD_ARTIFACT.exists():
            self.skipTest("Goal5398 POD artifact has not been generated yet")
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal5398")
        self.assertIn("native_v7_status_stream", payload)
        boundary = payload["claim_boundary"]
        for key in (
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "hash_sample_parity_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertIs(boundary[key], False, key)

    def test_frontdoor_source_remains_app_neutral(self) -> None:
        import rtdsl as rt
        from rtdsl import optix_runtime

        self.assertIn("collect_active_query_status_stream_3d_optix", rt.__all__)
        source = inspect.getsource(optix_runtime.collect_active_query_status_stream_3d_optix).lower()
        for forbidden in ("xhd", "x-hd", "hd_exec", "figure7", "figure11"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
