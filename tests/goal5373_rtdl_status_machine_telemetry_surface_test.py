from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5373_rtdl_status_machine_telemetry_surface.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5373_rtdl_status_machine_telemetry_surface.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5373_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5373RtdlStatusMachineTelemetrySurfaceTest(unittest.TestCase):
    def test_current_surface_is_audited_and_not_ready_for_lb_trace(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "rtdl_status_machine_telemetry_surface_audited__author_lb_trace_fields_missing",
            payload["status"],
        )
        self.assertEqual(
            "current_surface_insufficient__native_status_probe_or_author_instrumentation_required",
            payload["exit_label"],
        )
        summary = payload["coverage_summary"]
        self.assertFalse(summary["ready_for_author_shader_status_machine_lb_trace"])
        self.assertGreaterEqual(summary["missing_count"], 8)
        self.assertIn("status_count_offloading", summary["missing_fields"])
        self.assertIn("cmax2_mbr_abort_count", summary["missing_fields"])
        self.assertIn("raw_offload_rows_before_sort_reduce", summary["partial_fields"])

    def test_existing_generic_surface_is_real_but_only_partial(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        checks = payload["source_evidence"]["surface_checks"]
        self.assertTrue(checks["native_v3_memory_telemetry_symbol"])
        self.assertTrue(checks["raw_frontier_kind_counts"])
        self.assertTrue(checks["global_bound_early_break"])
        available = payload["current_available_surface"]
        for key in (
            "raw_frontier_kind_counts",
            "raw_frontier_kind2_rows",
            "global_bound_early_break_count",
            "native_memory_telemetry",
        ):
            self.assertTrue(available[key])

        coverage = payload["field_coverage"]
        self.assertEqual("partial", coverage["raw_offload_rows_before_sort_reduce"]["status"])
        self.assertEqual("partial", coverage["point_loop_early_break_count"]["status"])
        self.assertEqual("partial", coverage["current_best_state_source"]["status"])

    def test_author_status_machine_fields_are_not_silently_present(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        missing_tokens = payload["source_evidence"]["missing_status_machine_tokens"]
        self.assertTrue(all(missing_tokens.values()), missing_tokens)
        for field in (
            "active_in_queue_size",
            "status_count_init",
            "status_count_offloading",
            "status_count_aborted",
            "miss_queue_count",
            "cmax2_mbr_abort_count",
            "raw_offload_rows_author_width_bytes",
            "row_count_parity_against_author_offloading_size",
        ):
            self.assertEqual("missing", payload["field_coverage"][field]["status"], field)

    def test_claim_boundary_keeps_lb_and_full_reproduction_unclaimed(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        claims = payload["claim_boundary"]
        self.assertTrue(claims["telemetry_surface_audit_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "same_denominator_memory_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "rtdl_author_performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(claims[key], key)

    def test_goal5372_gate_fields_are_preserved(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        required = set(payload["required_gate_fields"])
        for field in (
            "active_in_queue_size",
            "raw_offload_rows_before_sort_reduce",
            "raw_offload_rows_author_width_bytes",
            "status_count_offloading",
            "status_count_aborted",
            "miss_queue_count",
            "cmax2_mbr_abort_count",
            "point_loop_early_break_count",
            "current_best_state_source",
            "row_count_parity_against_author_offloading_size",
        ):
            self.assertIn(field, required)
            self.assertIn(field, payload["field_coverage"])


if __name__ == "__main__":
    unittest.main()
