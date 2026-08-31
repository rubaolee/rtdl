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
    / "build_xhd_goal5374_author_lb_status_trace_oracle.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5374_author_lb_status_trace_oracle.json"
)


def _load_artifact() -> dict:
    if not ARTIFACT.exists():
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal5374AuthorLbStatusTraceOracleTest(unittest.TestCase):
    def test_author_oracle_trace_is_internally_consistent(self) -> None:
        payload = _load_artifact()
        self.assertEqual("Goal5374", payload["goal"])
        self.assertEqual(
            "author_lb_status_trace_oracle_ready__rtdl_status_machine_counterpart_missing",
            payload["status"],
        )
        self.assertEqual(
            "author_oracle_ready__next_rtdl_status_machine_counterpart",
            payload["exit_label"],
        )

        patch = payload["author_instrumentation"]
        self.assertTrue(patch["patched"])
        self.assertEqual("RTDL_GOAL5374_LB_STATUS_TRACE", patch["marker"])
        self.assertEqual(
            {"launch_parameters": True, "rt_impl": True, "shader": True},
            patch["changed"],
        )
        self.assertFalse(patch["rtdl_core_modified"])

        iteration = payload["author_result"]["iteration_3"]
        trace = payload["author_lb_trace"]
        self.assertEqual(437645, iteration["NumInputPoints"])
        self.assertEqual(0, iteration["NumOutputPoints"])
        self.assertEqual(27133990, iteration["OffloadingSize"])
        self.assertEqual(27133990, trace["raw_offload_rows_before_sort_reduce"])
        self.assertEqual(27133990, trace["status_count_offloading_append"])
        self.assertEqual(437645, trace["active_in_queue_size"])
        self.assertEqual(437645, trace["status_count_init"])
        self.assertEqual(217071920, trace["raw_offload_rows_author_width_bytes"])
        self.assertEqual(
            trace["raw_offload_rows_before_sort_reduce"] * 2 * 4,
            trace["raw_offload_rows_author_width_bytes"],
        )
        self.assertEqual(0, trace["status_count_cmax2_mbr_abort"])
        self.assertEqual(0, trace["status_count_point_loop_early_break"])

    def test_artifact_keeps_rtdl_counterpart_missing(self) -> None:
        payload = _load_artifact()
        comparison = payload["comparison"]
        self.assertTrue(comparison["author_trace_row_parity"])
        self.assertTrue(comparison["author_width_parity"])
        self.assertTrue(comparison["active_in_queue_parity"])
        self.assertEqual(27133990, comparison["author_offloading_size_rows"])
        self.assertEqual(21006960, comparison["rtdl_inline_kind2_rows_from_goal5371"])
        self.assertEqual(304981889, comparison["rtdl_noinline_kind2_rows_from_goal5371"])
        self.assertFalse(comparison["rtdl_counterpart_row_parity"])
        self.assertFalse(comparison["rtdl_surface_ready_from_goal5373"])
        self.assertAlmostEqual(
            21006960 / 27133990,
            comparison["rtdl_inline_div_author_trace_rows"],
            places=12,
        )
        self.assertAlmostEqual(
            304981889 / 27133990,
            comparison["rtdl_noinline_div_author_trace_rows"],
            places=12,
        )

        decision = payload["decision"]
        self.assertTrue(decision["author_oracle_ready"])
        self.assertFalse(decision["explicit_lb_support_authorized"])
        self.assertEqual(
            "rtdl_status_machine_counterpart_against_author_oracle",
            decision["next_gate"],
        )

    def test_claim_boundary_forbids_lb_and_paper_claims(self) -> None:
        payload = _load_artifact()
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["author_oracle_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "rtdl_row_count_parity_claimed",
            "same_denominator_memory_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "rtdl_author_performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
