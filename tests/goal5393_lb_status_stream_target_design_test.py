from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5393_lb_status_stream_target_design.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5393_lb_status_stream_target_design.json"
)


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_goal5393_lb_status_stream_target_design",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5393LbStatusStreamTargetDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_builder()
        cls.artifact = cls.module.build(output=ARTIFACT)

    def test_selects_full_cover_as_starting_surface_but_not_correctness(self) -> None:
        payload = self.artifact
        self.assertEqual(
            "lb_status_stream_target_selected__implement_generic_full_cover_delta_probe_next",
            payload["exit_label"],
        )
        selection = payload["target_selection"]
        self.assertEqual("full_cover_lb256_behavior_gate_surface", selection["selected_starting_surface"])
        self.assertEqual(24508120, selection["selected_surface_rows"])
        self.assertEqual(56.0, selection["selected_rows_per_active"])
        self.assertEqual(62.0, selection["author_rows_per_active"])
        self.assertEqual(2625870, selection["missing_rows_to_author"])
        self.assertEqual(6, selection["missing_rows_per_active_if_exact"])
        self.assertEqual(0, selection["missing_rows_per_active_remainder"])
        self.assertFalse(selection["full_cover_promoted_to_correctness"])
        self.assertTrue(selection["bridge_surface_rejected_as_implementation_target"])
        self.assertTrue(selection["hardcoded_fanout_rejected"])

    def test_next_gate_is_generic_delta_probe_not_native_completion_claim(self) -> None:
        gate = self.artifact["selected_next_gate"]
        self.assertEqual("generic_full_cover_delta_status_probe", gate["name"])
        self.assertEqual("Goal5394", gate["goal_hint"])
        self.assertIn("row_count against author 27,133,990", gate["must_compare"])
        self.assertIn("raw offload row hash or deterministic samples", gate["must_compare"])
        self.assertEqual("generic_status_stream_moves_denominator_toward_author", gate["success_label"])
        self.assertEqual(
            "generic_status_stream_target_not_author_compatible__lb_fail_closed_candidate",
            gate["failure_label"],
        )
        decision = self.artifact["decision"]
        self.assertFalse(decision["native_code_authorized_by_this_goal"])
        self.assertTrue(decision["next_work_is_design_to_implementation_transition"])
        self.assertTrue(decision["fail_closed_if_requires_xhd_specific_logic"])

    def test_semantic_gap_hypotheses_are_generic(self) -> None:
        hypotheses = self.artifact["semantic_gap_hypotheses"]
        names = {item["name"] for item in hypotheses}
        self.assertIn("multi_round_feedback_or_reactivation_delta", names)
        self.assertIn("author_current_best_restore_delta", names)
        self.assertIn("miss_completed_aborted_transition_delta", names)
        self.assertIn("load_balance_processing_feedback_delta", names)
        self.assertTrue(all(item["generic"] for item in hypotheses))

        contracts = self.artifact["existing_generic_contracts_to_reuse"]
        self.assertEqual("generic_active_query_multiround_status_reference_v1", contracts["multiround_status_contract"])
        self.assertEqual("generic_active_query_status_trace_summary_v1", contracts["trace_summary_contract"])
        self.assertEqual("none", contracts["app_semantics"])

    def test_goal5365_behavior_gate_is_supporting_not_sufficient(self) -> None:
        gate = self.artifact["supporting_behavior_gate"]
        self.assertTrue(gate["goal5365_value_match"])
        self.assertEqual(27133990, gate["goal5365_author_offloading_size"])
        self.assertEqual(24508120, gate["goal5365_rtdl_heavy_offload_peak_rows"])
        self.assertFalse(gate["goal5365_explicit_lb_support_authorized"])
        self.assertIn("does not establish row-count denominator parity", gate["why_not_enough"])

    def test_claim_boundary_stays_closed(self) -> None:
        boundary = self.artifact["claim_boundary"]
        self.assertTrue(boundary["status_stream_target_selection_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "hash_sample_parity_claimed",
            "full_cover_surface_promoted_to_author_semantics",
            "native_backend_completion_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "same_denominator_memory_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
