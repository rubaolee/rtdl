from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np

import rtdsl
from rtdsl import ACTIVE_QUERY_STATUS_KIND_CODES
from rtdsl import payload_transition_trace_summary_numpy_columns


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5414_synthetic_payload_transition_trace_fixture.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5414_synthetic_payload_transition_trace_fixture.json"
)


def _load_runner():
    spec = importlib.util.spec_from_file_location("goal5414_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load Goal5414 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5414SyntheticPayloadTransitionTraceFixtureTest(unittest.TestCase):
    def test_summary_accepts_synthetic_non_app_trace(self) -> None:
        module = _load_runner()
        columns = module.synthetic_non_app_trace_columns()
        summary = payload_transition_trace_summary_numpy_columns(
            columns,
            active_queue_indices=np.asarray([0, 1, 2], dtype=np.int64),
            row_capacity=8,
            sample_indices=np.asarray([0, 2, 4], dtype=np.int64),
            return_metadata=True,
        )
        self.assertEqual("accept", summary["status"])
        self.assertEqual("none", summary["app_semantics"])
        self.assertEqual(5, summary["raw_transition_row_count"])
        self.assertEqual(3, summary["active_query_count"])
        self.assertEqual(2, summary["status_count_offloading"])
        self.assertEqual(1, summary["status_count_completed"])
        self.assertEqual(1, summary["status_count_miss"])
        self.assertEqual(1, summary["status_count_aborted"])
        self.assertEqual([0, 1, 2], summary["samples"]["active_queue_indices"])
        self.assertEqual([7, 3, 6], summary["samples"]["primitive_or_cell_ids"])
        self.assertEqual(
            "not_called_cpu_reference_only",
            summary["metadata"]["native_engine_row_contract"],
        )
        self.assertFalse(summary["metadata"]["external_option_support_claimed"])
        self.assertFalse(summary["metadata"]["rt_core_speedup_claim_authorized"])

    def test_summary_rejects_overflow_unknown_status_and_bad_shape(self) -> None:
        module = _load_runner()
        columns = module.synthetic_non_app_trace_columns()

        rejected = payload_transition_trace_summary_numpy_columns(
            columns,
            row_capacity=4,
            return_metadata=True,
        )
        self.assertEqual("reject", rejected["status"])
        self.assertIn("row_capacity", rejected["reason"])

        overflowed = payload_transition_trace_summary_numpy_columns(
            columns,
            row_capacity=8,
            overflowed=True,
            return_metadata=True,
        )
        self.assertEqual("reject", overflowed["status"])
        self.assertIn("overflowed", overflowed["reason"])

        bad_status = {name: value.copy() for name, value in columns.items()}
        bad_status["status_codes"][0] = 999
        rejected = payload_transition_trace_summary_numpy_columns(bad_status)
        self.assertEqual("reject", rejected["status"])
        self.assertIn("unknown payload transition status codes", rejected["reason"])

        bad_namespace = {name: value.copy() for name, value in columns.items()}
        bad_namespace["cell_namespace_codes"][1] = -1
        rejected = payload_transition_trace_summary_numpy_columns(bad_namespace)
        self.assertEqual("reject", rejected["status"])
        self.assertIn("cell namespace codes", rejected["reason"])

        bad_shape = {name: value.copy() for name, value in columns.items()}
        bad_shape["work_counts"] = bad_shape["work_counts"][:-1]
        rejected = payload_transition_trace_summary_numpy_columns(bad_shape)
        self.assertEqual("reject", rejected["status"])
        self.assertIn("same shape", rejected["reason"])

    def test_runner_artifact_is_synthetic_and_claim_bounded(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["matched"])
        self.assertEqual(
            "synthetic_non_app_payload_transition_trace_fixture_passed",
            payload["status"],
        )
        self.assertTrue(payload["claim_boundary"]["synthetic_non_app_payload_transition_trace_claimed"])
        self.assertFalse(payload["claim_boundary"]["bounded_xhd_sample_row_recovery_claimed"])
        self.assertFalse(payload["claim_boundary"]["explicit_lb_support_claimed"])
        self.assertFalse(payload["claim_boundary"]["native_backend_implementation_claimed"])
        self.assertFalse(payload["claim_boundary"]["figure7_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["figure11_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])
        self.assertEqual(
            "Goal5415_decide_stop_or_bounded_xhd_payload_transition_sample_gate",
            payload["recommended_next_goal"],
        )

    def test_public_exports_include_summary_helper(self) -> None:
        self.assertIs(
            rtdsl.payload_transition_trace_summary_numpy_columns,
            payload_transition_trace_summary_numpy_columns,
        )
        self.assertEqual(
            "generic_native_payload_transition_trace_summary_v1",
            rtdsl.ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_SUMMARY_CONTRACT,
        )

    def test_core_helper_has_no_external_app_identity_tokens(self) -> None:
        source = (ROOT / "src" / "rtdsl" / "active_query_status.py").read_text(encoding="utf-8")
        window_start = source.index("def payload_transition_trace_summary_numpy_columns")
        window_end = source.index("def apply_active_query_feedback_numpy_columns")
        window = source[window_start:window_end].lower()
        for token in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
            self.assertNotIn(token, window)
        self.assertIn(str(ACTIVE_QUERY_STATUS_KIND_CODES["offload"]), str(ACTIVE_QUERY_STATUS_KIND_CODES))


if __name__ == "__main__":
    unittest.main()
