from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5396_v6_remap_no_go.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5396_v6_remap_no_go.json"
)


class Goal5396V6RemapNoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_author_target_and_best_surface_delta_are_pinned(self) -> None:
        payload = self.payload
        self.assertEqual(payload["goal"], "Goal5396")
        self.assertEqual(
            payload["exit_label"],
            "v6_remap_no_go__implement_real_v7_or_keep_lb_fail_closed",
        )

        author = payload["author_oracle"]
        self.assertEqual(author["active_count"], 437645)
        self.assertEqual(author["raw_offload_rows_before_sort_reduce"], 27133990)
        self.assertEqual(author["rows_per_active"], 62)
        self.assertEqual(author["rows_per_active_remainder"], 0)
        self.assertEqual(author["feedback_update_count"], 294)

        surfaces = payload["known_rtdl_surfaces"]
        self.assertEqual(surfaces["full_cover_rows"], 24508120)
        self.assertEqual(surfaces["full_cover_rows_per_active"], 56.0)
        self.assertFalse(surfaces["any_surface_has_row_count_parity"])
        self.assertFalse(surfaces["any_surface_has_hash_parity"])

        remap = payload["v6_remap_assessment"]
        self.assertEqual(remap["row_delta_author_minus_best_v6_like"], 2625870)
        self.assertEqual(remap["row_delta_per_active"], 6)
        self.assertEqual(remap["row_delta_remainder"], 0)

    def test_v6_remap_is_rejected_not_promoted(self) -> None:
        remap = self.payload["v6_remap_assessment"]
        self.assertEqual(remap["verdict"], "reject_v6_remap_as_native_status_stream_backend")
        self.assertFalse(remap["would_change_denominator"])
        self.assertFalse(remap["would_add_missing_rows"])
        self.assertFalse(remap["would_add_transition_semantics"])
        self.assertFalse(remap["would_add_feedback_semantics"])
        self.assertFalse(remap["would_add_before_after_current_best_per_row"])
        self.assertTrue(remap["would_only_relabel_existing_rows"])

        decision = self.payload["decision"]
        self.assertFalse(decision["v6_column_remap_authorized"])
        self.assertFalse(decision["native_status_stream_backend_implemented_by_goal5396"])
        self.assertTrue(decision["explicit_lb_remains_fail_closed"])
        self.assertTrue(decision["real_v7_backend_required"])
        self.assertTrue(decision["pod_required_for_next_goal"])

    def test_goal5395_abi_gap_is_carried_forward(self) -> None:
        gap = self.payload["goal5395_abi_gap"]
        self.assertEqual(gap["contract"], "generic_active_query_status_stream_native_abi_v1")
        self.assertEqual(gap["current_v6_symbol"], "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6")
        self.assertTrue(gap["current_surface_is_single_launch_frontier_probe"])
        self.assertFalse(gap["current_surface_satisfies_goal5394_native_probe"])
        self.assertFalse(gap["existing_native_v6_is_sufficient"])
        self.assertIn("transition_phase_code", gap["missing_required_output_columns"])
        self.assertIn("current_best_before_sq", gap["missing_required_output_columns"])
        self.assertIn("current_best_after_sq", gap["missing_required_output_columns"])
        self.assertIn("multi-round feedback state", gap["missing_required_semantics"])

    def test_claim_boundary_blocks_fake_success(self) -> None:
        boundary = self.payload["claim_boundary"]
        forbidden_true = [
            "native_backend_completion_claimed",
            "existing_native_v6_parity_claimed",
            "v6_column_remap_claimed_sufficient",
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "hash_sample_parity_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "same_denominator_memory_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ]
        for key in forbidden_true:
            self.assertIs(boundary[key], False, key)


if __name__ == "__main__":
    unittest.main()
