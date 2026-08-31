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
    / "build_xhd_goal5372_author_shader_status_machine_gap.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5372_author_shader_status_machine_gap.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5372_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5372AuthorShaderStatusMachineGapTest(unittest.TestCase):
    def test_author_source_checks_and_status_machine_are_pinned(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "author_shader_status_machine_gap_matrix_ready__implementation_or_author_instrumentation_next",
            payload["status"],
        )
        self.assertEqual(
            "status_machine_requirements_ready__lb_support_still_unauthorized",
            payload["exit_label"],
        )
        checks = payload["source_evidence"]["checks"]
        self.assertTrue(checks)
        self.assertTrue(all(checks.values()), checks)

        status_bits = payload["author_status_machine"]["status_bits"]
        self.assertEqual({"kInit": 1, "kOffloading": 2, "kAborted": 4}, status_bits)
        payload_fields = {item["name"]: item for item in payload["author_status_machine"]["payload_fields"]}
        for name in ("in_q_idx", "n_hits", "n_compared_pairs", "status", "cmin2"):
            self.assertIn(name, payload_fields)

        branches = {item["name"]: item for item in payload["author_status_machine"]["critical_branches"]}
        for name in (
            "radius_or_cmin2_prune",
            "cmax2_mbr_abort",
            "heavy_cell_offload",
            "point_loop_early_break",
            "valid_complete_source",
            "miss_source",
        ):
            self.assertIn(name, branches)

    def test_current_rtdl_evidence_keeps_lb_denominator_unmatched(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        evidence = payload["rtdl_current_evidence"]
        self.assertEqual(27_133_990, evidence["author_offloading_size_rows"])
        self.assertEqual(21_006_960, evidence["rtdl_author_radius_inline_count_only_kind2_rows"])
        self.assertEqual(21_006_960, evidence["rtdl_author_radius_inline_global_bound_kind2_rows"])
        self.assertEqual(304_981_889, evidence["rtdl_author_radius_noinline_raw_kind2_rows"])
        self.assertEqual(0, evidence["global_bound_early_break_count"])
        self.assertAlmostEqual(0.7741935483870968, evidence["inline_div_author"])
        self.assertGreater(evidence["noinline_div_author"], 11.0)
        self.assertTrue(evidence["queue_state_reference_available"])
        self.assertEqual("author_queue_aligned_lb_trace", evidence["queue_requirements_gate_available"])

    def test_gap_matrix_and_next_gate_require_status_machine_fields(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        gaps = {item["author_semantic"]: item for item in payload["gap_matrix"]}
        for semantic in (
            "active in_queue index namespace",
            "dynamic per-source cmin2",
            "cmax2 abort status",
            "heavy-cell offload append",
            "loadBalanceProcessing grouping",
            "miss queue",
        ):
            self.assertIn(semantic, gaps)
            self.assertIn("needed_next", gaps[semantic])

        contract = payload["next_gate_contract"]
        self.assertEqual("author_shader_status_machine_lb_trace", contract["name"])
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
            self.assertIn(field, contract["minimum_fields"])

    def test_claim_boundary_does_not_promote_lb_or_full_reproduction(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        claims = payload["claim_boundary"]
        self.assertTrue(claims["status_machine_gap_matrix_claimed"])
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


if __name__ == "__main__":
    unittest.main()
