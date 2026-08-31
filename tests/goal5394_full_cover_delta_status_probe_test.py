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
    / "build_xhd_goal5394_full_cover_delta_status_probe.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5394_full_cover_delta_status_probe.json"
)


class Goal5394FullCoverDeltaStatusProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_author_target_and_selected_surface_are_pinned(self) -> None:
        payload = self.payload
        self.assertEqual(payload["goal"], "Goal5394")
        self.assertEqual(
            payload["exit_label"],
            "generic_full_cover_delta_probe_ready__native_or_fail_closed_next",
        )

        author = payload["author_target"]
        self.assertEqual(author["active_in_queue_size"], 437645)
        self.assertEqual(author["raw_offload_rows_before_sort_reduce"], 27133990)
        self.assertEqual(author["rows_per_active"], 62)
        self.assertEqual(author["raw_offload_row_hash"], 4333109858711462591)

        surface = payload["selected_surface"]
        self.assertEqual(surface["name"], "full_cover_lb256_behavior_gate_surface")
        self.assertEqual(surface["row_count"], 24508120)
        self.assertEqual(surface["rows_per_active"], 56)
        self.assertEqual(surface["missing_rows_to_author"], 2625870)
        self.assertEqual(surface["missing_rows_per_active"], 6)
        self.assertEqual(surface["missing_rows_per_active_remainder"], 0)
        self.assertFalse(surface["full_cover_is_correctness_claim"])

    def test_synthetic_multiround_probe_is_generic_shape_demo_only(self) -> None:
        synthetic = self.payload["synthetic_generic_probe"]
        self.assertEqual(
            synthetic["contract"], "generic_active_query_multiround_status_reference_v1"
        )
        self.assertEqual(synthetic["app_semantics"], "none")
        self.assertFalse(synthetic["author_semantics_claimed"])
        self.assertFalse(synthetic["hardcoded_author_fanout_claimed"])

        self.assertEqual(synthetic["synthetic_active_query_count"], 2)
        self.assertEqual(synthetic["base_rows_per_active"], 56)
        self.assertEqual(synthetic["delta_rows_per_active"], 6)
        self.assertEqual(synthetic["target_rows_per_active"], 62)
        self.assertEqual(synthetic["base_round_offload_rows"], 112)
        self.assertEqual(synthetic["delta_round_offload_rows"], 12)
        self.assertEqual(synthetic["raw_offload_rows_before_sort_reduce"], 124)

        rounds = synthetic["rounds"]
        self.assertEqual([round_["round_index"] for round_ in rounds], [0, 1])
        self.assertEqual([round_["offload_row_count"] for round_ in rounds], [112, 12])
        self.assertEqual([round_["active_query_count"] for round_ in rounds], [2, 2])
        self.assertEqual(self.payload["synthetic_probe_assessment"]["shape_matches_selected_target"], True)
        self.assertFalse(self.payload["synthetic_probe_assessment"]["proves_author_parity"])
        self.assertFalse(
            self.payload["synthetic_probe_assessment"][
                "proves_native_backend_completion"
            ]
        )

    def test_native_probe_spec_requires_real_author_comparison_without_hardcoding(self) -> None:
        spec = self.payload["native_probe_spec"]
        self.assertEqual(spec["name"], "generic_full_cover_delta_status_probe")
        self.assertEqual(spec["recommended_goal"], "Goal5395")
        self.assertEqual(
            spec["contract_kind"], "generic_native_multi_round_active_query_status_stream"
        )
        self.assertEqual(spec["start_surface"], "full_cover_lb256_behavior_gate_surface")

        self.assertIn("6 missing rows per active", spec["must_not_hardcode"])
        self.assertIn("62 author rows per active", spec["must_not_hardcode"])
        self.assertIn(
            "X-HD option or figure names in RTDL core/native code",
            spec["must_not_hardcode"],
        )

        required_columns = set(spec["required_output_columns"])
        self.assertIn("status_code", required_columns)
        self.assertIn("transition_phase_code", required_columns)
        self.assertIn("current_best_before_sq", required_columns)

        telemetry = set(spec["required_telemetry"])
        self.assertIn("raw_offload_rows_before_sort_reduce", telemetry)
        self.assertIn("status_count_offloading", telemetry)
        self.assertIn("miss_count", telemetry)
        self.assertIn("completed_count", telemetry)
        self.assertIn("aborted_count", telemetry)

        comparisons = set(spec["must_compare_against_author"])
        self.assertIn("row_count", comparisons)
        self.assertIn("hash_or_samples", comparisons)
        self.assertIn("status_count_offloading", comparisons)

    def test_claim_boundary_keeps_lb_unsupported(self) -> None:
        decision = self.payload["decision"]
        self.assertFalse(decision["native_code_implemented_by_goal5394"])
        self.assertTrue(decision["native_probe_ready_for_implementation"])
        self.assertTrue(decision["explicit_lb_support_remains_unsupported"])
        self.assertTrue(decision["next_gate_requires_pod_if_native_code_is_changed"])

        forbidden_true = [
            "author_parity_claimed",
            "native_backend_completion_claimed",
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
        boundary = self.payload["claim_boundary"]
        for key in forbidden_true:
            self.assertIs(boundary[key], False, key)


if __name__ == "__main__":
    unittest.main()
