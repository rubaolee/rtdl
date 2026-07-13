from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "build_xhd_goal5385_author_trace_v2_spec.py"
ARTIFACT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5385_author_trace_v2_spec.json"


class Goal5385AuthorTraceV2SpecTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(SCRIPT), "--output", str(ARTIFACT)], check=True)
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_carries_forward_goal5374_and_goal5384_evidence(self) -> None:
        artifact = self.artifact

        self.assertEqual(artifact["status"], "implemented_review_pending")
        self.assertEqual(
            artifact["exit_label"],
            "author_trace_v2_spec_ready__next_patch_author_or_native_stream",
        )
        current = artifact["current_author_oracle"]
        self.assertTrue(current["available"])
        self.assertEqual(current["active_in_queue_size"], 437645)
        self.assertEqual(current["raw_offload_rows_before_sort_reduce"], 27133990)
        self.assertEqual(current["raw_offload_rows_author_width_bytes"], 217071920)
        self.assertEqual(current["limitation"], "counts_only_no_row_identity_no_cmin2_vectors_no_load_balance_feedback")

        multiround = artifact["goal5384_multiround_requirement"]
        self.assertEqual(multiround["contract"], "generic_active_query_multiround_status_reference_v1")
        self.assertIn("raw_offload_rows_before_sort_reduce", multiround["required_fields"])
        self.assertIn("row_count_parity_against_goal5374", multiround["required_fields"])

    def test_v2_schema_requires_state_hashes_samples_and_load_balance_fields(self) -> None:
        schema = self.artifact["author_trace_v2_schema"]
        required = set(schema["required_batch_fields"])

        for field in (
            "cmax2_before_ray",
            "cmax2_after_ray",
            "cmax2_after_load_balance",
            "cmin2_initial_hash",
            "cmin2_after_ray_hash",
            "cmin2_after_load_balance_hash",
            "raw_offload_row_hash",
            "raw_offload_row_sample_point_ids",
            "raw_offload_row_sample_cell_ids",
            "status_count_miss",
            "status_count_completed",
            "load_balance_group_count",
            "load_balance_feedback_update_count",
        ):
            self.assertIn(field, required)

        policy = schema["dump_policy"]
        self.assertFalse(policy["full_raw_rows_required_for_default_gate"])
        self.assertTrue(policy["hash_and_sample_required"])
        self.assertTrue(policy["full_dump_allowed_under_explicit_flag"])
        self.assertIn("27133990", policy["reason"])
        self.assertIn("217071920", policy["reason"])

    def test_patch_targets_are_author_only_and_marker_is_distinct(self) -> None:
        targets = self.artifact["patch_targets"]

        self.assertTrue(targets["must_not_patch_rtdl_core"])
        self.assertEqual(targets["instrumentation_marker"], "RTDL_GOAL5385_LB_STATUS_TRACE_V2")
        self.assertEqual(
            targets["author_files"],
            [
                "src/rt/launch_parameters.h",
                "src/rt/shaders/shaders_nn_uniform_grid.cu",
                "src/hd_impl/hausdorff_distance_rt.h",
            ],
        )
        self.assertTrue(any("loadBalanceProcessing" in hook for hook in targets["expected_hook_points"]))

    def test_claim_boundary_forbids_premature_lb_and_paper_claims(self) -> None:
        boundary = self.artifact["claim_boundary"]

        for key in (
            "author_v2_trace_implemented",
            "author_v2_trace_executed_on_pod",
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "rtdl_author_performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(boundary[key])

    def test_comparison_gate_requires_row_hash_and_state_hash_checks(self) -> None:
        gate = self.artifact["comparison_gate_requirements"]

        self.assertEqual(gate["must_compare_same_input_pair"], "Dragon -> AsianDragon Level-B lb=256 diagnostic")
        self.assertIn("raw_offload_row_hash_parity_if_full_or_hash_available", gate["must_report"])
        self.assertIn("cmin2_state_hash_comparison", gate["must_report"])
        self.assertIn("load_balance_feedback_count_comparison", gate["must_report"])
        self.assertIn("raw_offload_row_count_parity=true", gate["minimum_success_for_native_counterpart"])


if __name__ == "__main__":
    unittest.main()
