from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5410_statused_large_cell_deferral_stream_probe.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5410_statused_large_cell_deferral_stream_probe.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5410_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load Goal5410 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5410StatusedLargeCellDeferralStreamProbeTest(unittest.TestCase):
    def test_synthetic_gate_emits_offload_completed_miss_and_abort(self) -> None:
        module = _load_module()
        payload = module.build_payload()
        self.assertTrue(payload["matched"])
        self.assertEqual("statused_large_cell_deferral_stream", payload["generic_semantic"]["name"])
        self.assertEqual("none", payload["generic_semantic"]["app_semantics"])
        telemetry = payload["observed_telemetry"]
        self.assertEqual(2, telemetry["offload_row_count"])
        self.assertEqual(2, telemetry["completed_row_count"])
        self.assertEqual(1, telemetry["miss_row_count"])
        self.assertEqual(1, telemetry["aborted_row_count"])
        self.assertEqual(1, telemetry["pruned_by_radius_or_current_best_count"])

    def test_offload_rows_are_deferred_large_cell_rows(self) -> None:
        module = _load_module()
        payload = module.build_payload()
        rows = payload["offload_rows"]
        self.assertEqual([11, 11], rows["active_queue_indices"])
        self.assertEqual([101, 101], rows["source_ids"])
        self.assertEqual([51, 52], rows["cell_ids"])
        self.assertEqual([9, 8], rows["work_counts"])
        self.assertEqual(2, payload["trace_summary"]["row_count"])
        self.assertEqual(2, payload["trace_summary"]["status_count_offloading"])

    def test_terminal_rows_preserve_distinct_statuses(self) -> None:
        module = _load_module()
        payload = module.build_payload()
        import rtdsl as rt

        self.assertEqual([10, 14], payload["completed_rows"]["active_queue_indices"])
        self.assertEqual(
            [rt.ACTIVE_QUERY_STATUS_KIND_CODES["miss"]],
            payload["miss_rows"]["status_codes"],
        )
        self.assertEqual(
            [rt.ACTIVE_QUERY_STATUS_KIND_CODES["aborted"]],
            payload["aborted_rows"]["status_codes"],
        )

    def test_generic_reference_source_remains_app_neutral(self) -> None:
        import rtdsl as rt

        source = inspect.getsource(rt.active_query_status_machine_reference_numpy_columns).lower()
        summary_source = inspect.getsource(rt.active_query_status_trace_summary_numpy_columns).lower()
        for text in (source, summary_source):
            for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
                self.assertNotIn(forbidden, text)

    def test_claim_boundary_keeps_lb_and_paper_claims_closed(self) -> None:
        module = _load_module()
        payload = module.build_payload()
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["synthetic_status_stream_claimed"])
        self.assertFalse(boundary["bounded_xhd_author_sample_recovery_claimed"])
        self.assertFalse(boundary["explicit_lb_support_claimed"])
        self.assertFalse(boundary["figure7_reproduction_claimed"])
        self.assertFalse(boundary["figure11_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        decision = payload["decision"]
        self.assertFalse(decision["bounded_xhd_author_sample_row_gate_passed"])
        self.assertEqual(
            "Goal5411_bounded_xhd_statused_deferral_sample_row_gate",
            decision["recommended_next_goal"],
        )

    @unittest.skipUnless(ARTIFACT.exists(), "Goal5410 artifact not present")
    def test_written_artifact_matches_synthetic_gate(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "rtdl.paper_reproduction.xhd.goal5410.statused_large_cell_deferral_stream_probe.v1",
            payload["schema"],
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(
            "synthetic_app_neutral_status_stream_gate_passed__bounded_xhd_gate_pending",
            payload["status"],
        )


if __name__ == "__main__":
    unittest.main()
