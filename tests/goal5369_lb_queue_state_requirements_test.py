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
    / "build_xhd_goal5369_lb_queue_state_requirements.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5369_lb_queue_state_requirements.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5369_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5369LbQueueStateRequirementsTest(unittest.TestCase):
    def test_builder_records_next_gate_status_and_denominator_numbers(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "lb_queue_state_requirements_ready__implementation_requires_queue_state_reconstruction_or_author_instrumentation",
            payload["status"],
        )
        self.assertEqual(
            "lb_queue_state_requirements_ready__no_explicit_lb_support_yet",
            payload["exit_label"],
        )
        author = payload["evidence_summary"]["author_lb256_reference"]
        self.assertEqual(27_133_990, author["offloading_size_rows"])
        self.assertEqual(217_071_920, author["wl_heavy_peak_bytes"])
        self.assertEqual(79.2156982421875, author["radius"])

        raw = payload["evidence_summary"]["raw_kind_count_from_goal5368"]
        self.assertEqual(304_981_889, raw["raw_kind2_rows"])
        self.assertGreater(raw["raw_kind2_div_author"], 11.0)
        self.assertTrue(raw["raw_kind2_greater_than_author"])
        self.assertTrue(raw["overflow_telemetry_only"])
        self.assertEqual(0, raw["frontier_row_capacity"])

        radius_probe = payload["evidence_summary"]["scalar_radius_probe_from_goal5367"]
        self.assertEqual(21_006_960, radius_probe["author_radius_rtdl_rows"])
        self.assertFalse(radius_probe["author_radius_closes_denominator_gap"])
        self.assertLess(radius_probe["author_radius_rtdl_div_author"], 1.0)

    def test_rejected_hypotheses_and_required_state_are_explicit(self) -> None:
        payload = _load_module().build_artifact()
        hypotheses = {item["hypothesis"]: item["rejected_by"] for item in payload["rejected_hypotheses"]}
        self.assertIn("scalar radius mismatch alone explains OffloadingSize", hypotheses)
        self.assertIn("author OffloadingSize equals all raw same-radius kind2 rows", hypotheses)
        self.assertIn("11.24x", hypotheses["author OffloadingSize equals all raw same-radius kind2 rows"])

        required = {
            item["name"]: item["current_status"]
            for item in payload["required_runtime_state_for_next_gate"]
        }
        self.assertEqual("missing_for_lb_trace", required["active_in_queue_indices"])
        self.assertEqual("missing_for_lb_trace", required["per_source_current_best_or_cmin2"])
        self.assertEqual("partially_available", required["per_iteration_radius_schedule"])
        self.assertEqual(
            "source_semantics_available_runtime_rows_missing",
            required["raw_offload_row_shape"],
        )
        self.assertEqual("formula_available", required["author_width_memory_view"])

        missing = set(payload["missing_author_runtime_state"])
        self.assertIn("per-source cmin2/current-best vector for iteration 3", missing)
        self.assertIn("raw author offloading rows before sort/reduce", missing)

    def test_next_gate_contract_is_precise_and_claim_boundary_blocks_support_claims(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        contract = payload["next_gate_contract"]
        self.assertEqual("author_queue_aligned_lb_trace", contract["name"])
        criteria = contract["minimum_acceptance_criteria"]
        self.assertTrue(criteria["same_input_pair"])
        self.assertTrue(criteria["same_preprocessing"])
        self.assertEqual(256, criteria["same_lb_threshold"])
        self.assertEqual(437_645, criteria["active_queue_size_matches_author_num_input_points"])
        self.assertEqual(27_133_990, criteria["author_offloading_size_rows"])
        for field in (
            "active_in_queue_size",
            "current_best_state_source",
            "raw_offload_rows_before_sort_reduce",
            "author_width_bytes",
            "row_count_parity",
        ):
            self.assertIn(field, criteria["must_report"])

        claims = payload["claim_boundary"]
        self.assertTrue(claims["requirements_gate_claimed"])
        self.assertTrue(claims["generic_system_requirement_claimed"])
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
