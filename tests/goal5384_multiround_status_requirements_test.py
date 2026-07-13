from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5384_multiround_status_requirements.json"
SCRIPT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "build_xhd_goal5384_multiround_status_requirements.py"


class Goal5384MultiroundStatusRequirementsArtifactTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(SCRIPT), "--output", str(ARTIFACT)], check=True)
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_carries_forward_author_oracle_and_goal5383_no_go(self) -> None:
        artifact = self.artifact

        self.assertEqual(artifact["status"], "implemented_review_pending")
        self.assertEqual(
            artifact["exit_label"],
            "multiround_status_reference_ready__native_or_author_trace_required_for_lb_parity",
        )
        self.assertEqual(artifact["author_oracle_carry_forward"]["offload_rows"], 27133990)
        self.assertEqual(artifact["latest_rejected_probe_carry_forward"]["offload_rows"], 2188225)
        self.assertAlmostEqual(
            artifact["latest_rejected_probe_carry_forward"]["row_ratio_rtdl_div_author"],
            0.08064516129032258,
        )
        self.assertFalse(artifact["latest_rejected_probe_carry_forward"]["row_count_parity"])

    def test_generic_contract_and_synthetic_multiround_demo_are_present(self) -> None:
        artifact = self.artifact

        system = artifact["generic_system_addition"]
        self.assertEqual(system["contract"], "generic_active_query_multiround_status_reference_v1")
        self.assertEqual(system["app_semantics"], "none")
        self.assertFalse(system["native_backend_complete"])
        self.assertFalse(system["explicit_app_option_support_claimed"])

        demo = artifact["synthetic_multiround_demo"]
        self.assertEqual(demo["contract"], "generic_active_query_multiround_status_reference_v1")
        self.assertEqual(demo["telemetry"]["round_count"], 2)
        self.assertEqual(demo["telemetry"]["raw_offload_rows_before_sort_reduce"], 1)
        self.assertEqual(demo["telemetry"]["feedback_updates_applied"], 1)
        self.assertEqual(demo["offload_active_queue_indices"], [11])
        self.assertEqual(demo["completed_active_queue_indices"], [10, 12, 11])

    def test_claim_boundary_keeps_lb_and_full_reproduction_unclaimed(self) -> None:
        boundary = self.artifact["claim_boundary"]

        for key in (
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

    def test_next_requirements_reject_more_single_pass_prune_modes(self) -> None:
        requirements = self.artifact["requirements_for_next_native_or_author_gate"]

        self.assertTrue(requirements["must_compare_against_goal5374_author_oracle"])
        self.assertIn("raw_offload_rows_before_sort_reduce", requirements["required_fields"])
        self.assertIn("row_count_parity_against_goal5374", requirements["required_fields"])
        self.assertIn("single_pass_prune_mode_variants", requirements["rejected_next_work"])
        self.assertIn("bridge_vectorization_before_row_parity", requirements["rejected_next_work"])


if __name__ == "__main__":
    unittest.main()
