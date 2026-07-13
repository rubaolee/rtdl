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
    / "build_xhd_goal5376_status_machine_candidate_contract.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5376_status_machine_candidate_contract.json"
)


def _load_artifact() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class Goal5376StatusMachineCandidateContractArtifactTest(unittest.TestCase):
    def test_contract_is_ready_but_author_lb_parity_is_not_claimed(self) -> None:
        payload = _load_artifact()
        self.assertEqual("Goal5376", payload["goal"])
        self.assertEqual(
            "rtdl_status_machine_candidate_contract_implemented__author_lb_row_parity_not_established",
            payload["status"],
        )
        self.assertTrue(payload["source_contract"]["runtime_contract_present"])
        self.assertTrue(payload["source_contract"]["partner_passthrough_present"])
        self.assertTrue(payload["assessment"]["status_candidate_contract_ready"])
        self.assertFalse(payload["assessment"]["author_lb_row_parity_established"])
        self.assertFalse(payload["assessment"]["explicit_lb_support_authorized"])

        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["status_candidate_contract_claimed"])
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

    def test_author_oracle_numbers_and_missing_semantics_are_preserved(self) -> None:
        payload = _load_artifact()
        author = payload["author_oracle"]
        self.assertEqual(437645, author["active_in_queue_size"])
        self.assertEqual(27133990, author["offloading_size_rows"])
        self.assertEqual(217071920, author["raw_offload_rows_author_width_bytes"])

        comparison = payload["comparison_to_goal5375_best_existing_candidate"]
        self.assertEqual(
            "goal5365_full_cover_lb256_behavior_gate_surface",
            comparison["best_candidate_name"],
        )
        self.assertEqual(2625870, comparison["best_candidate_absolute_row_delta"])
        self.assertFalse(comparison["best_candidate_row_count_parity"])

        missing = set(payload["assessment"]["still_missing_or_analog_semantics"])
        self.assertIn("author cmin2/current-best restoration by in_q_idx", missing)
        self.assertIn("author cmax2 MBR abort status counter", missing)
        self.assertIn("author miss_queue append/count semantics", missing)
        self.assertIn("row-count parity against Goal5374 OffloadingSize", missing)


if __name__ == "__main__":
    unittest.main()
