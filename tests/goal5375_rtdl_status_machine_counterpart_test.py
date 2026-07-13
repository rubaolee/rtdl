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
    / "build_xhd_goal5375_rtdl_status_machine_counterpart.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5375_rtdl_status_machine_counterpart_assessment.json"
)


def _load_artifact() -> dict:
    if not ARTIFACT.exists():
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal5375RtdlStatusMachineCounterpartTest(unittest.TestCase):
    def test_current_rtdl_candidates_do_not_match_author_oracle_rows(self) -> None:
        payload = _load_artifact()
        self.assertEqual("Goal5375", payload["goal"])
        self.assertEqual(
            "rtdl_status_machine_counterpart_assessed__row_parity_not_established",
            payload["status"],
        )
        self.assertEqual(
            "current_rtdl_surface_fails_author_lb_oracle__need_status_machine_implementation",
            payload["exit_label"],
        )
        self.assertEqual(27133990, payload["author_oracle"]["offloading_size_rows"])
        self.assertFalse(payload["assessment"]["any_candidate_row_count_parity"])
        self.assertFalse(payload["assessment"]["minimum_gate_passed"])
        self.assertFalse(payload["decision"]["explicit_lb_support_authorized"])

        by_name = {item["name"]: item for item in payload["candidate_counterparts"]}
        self.assertEqual(
            21006960,
            by_name["author_radius_inline_kind2_current_surface"][
                "raw_offload_rows_before_sort_reduce"
            ],
        )
        self.assertEqual(
            21006960,
            by_name["author_radius_inline_global_bound_kind2_current_surface"][
                "raw_offload_rows_before_sort_reduce"
            ],
        )
        self.assertEqual(
            304981889,
            by_name["author_radius_noinline_raw_kind2_current_surface"][
                "raw_offload_rows_before_sort_reduce"
            ],
        )
        self.assertEqual(
            24508120,
            by_name["goal5365_full_cover_lb256_behavior_gate_surface"][
                "raw_offload_rows_before_sort_reduce"
            ],
        )
        for candidate in by_name.values():
            self.assertFalse(candidate["row_count_parity"], candidate["name"])

    def test_best_current_candidate_is_still_not_enough(self) -> None:
        payload = _load_artifact()
        best = payload["best_current_candidate"]
        self.assertEqual("goal5365_full_cover_lb256_behavior_gate_surface", best["name"])
        self.assertEqual(2625870, best["absolute_row_delta"])
        self.assertAlmostEqual(24508120 / 27133990, best["row_ratio_rtdl_div_author"])
        self.assertFalse(best["row_count_parity"])

        missing = set(payload["assessment"]["missing_or_unproven_semantics"])
        self.assertIn("author cmin2/current-best restoration by in_q_idx", missing)
        self.assertIn("author cmax2 MBR abort status counter", missing)
        self.assertIn("author miss_queue append/count semantics", missing)
        self.assertIn("row-count parity against Goal5374 OffloadingSize", missing)

    def test_claim_boundary_keeps_lb_and_paper_claims_false(self) -> None:
        payload = _load_artifact()
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["rtdl_counterpart_assessment_claimed"])
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
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
