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
    / "build_xhd_goal5391_lb_fanout_semantics.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5391_lb_fanout_semantics.json"
)


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_goal5391_lb_fanout_semantics",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5391LbFanoutSemanticsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_builder()
        cls.artifact = cls.module.build(output=ARTIFACT)

    def test_aggregate_fanout_denominator_is_exact_and_mismatched(self) -> None:
        payload = self.artifact
        self.assertEqual(
            "lb_fanout_semantics_mismatch__bridge_runtime_not_next_target",
            payload["exit_label"],
        )
        self.assertTrue(payload["comparison"]["active_query_count_parity"])
        self.assertFalse(payload["comparison"]["row_count_parity"])
        self.assertFalse(payload["comparison"]["hash_parity"])
        self.assertTrue(payload["comparison"]["denominator_mismatch_confirmed"])
        self.assertEqual(437645, payload["author_denominator"]["active_in_queue_size"])
        self.assertEqual(437645, payload["rtdl_denominator"]["active_query_count"])

        author_division = payload["author_denominator"]["division"]
        rtdl_division = payload["rtdl_denominator"]["division"]
        self.assertTrue(author_division["integer_multiple"])
        self.assertTrue(rtdl_division["integer_multiple"])
        self.assertEqual(62, author_division["rows_per_active_integer_if_exact"])
        self.assertEqual(5, rtdl_division["rows_per_active_integer_if_exact"])
        self.assertEqual(57.0, payload["comparison"]["author_rows_per_active_minus_rtdl_rows_per_active"])

    def test_classification_rejects_bridge_runtime_as_next_main_path(self) -> None:
        payload = self.artifact
        classification = payload["classification"]
        self.assertEqual(
            "status_stream_fanout_or_transition_semantics",
            classification["primary_mismatch"],
        )
        self.assertIn("per-query uniform fanout distribution", classification["not_proven"])
        decision = payload["decision"]
        self.assertTrue(decision["explicit_lb_support_remains_unsupported"])
        self.assertTrue(decision["bridge_runtime_optimization_rejected_as_next_main_path"])
        self.assertTrue(decision["source_limited_smoke_rejected_as_next_main_path"])
        self.assertEqual(
            "generic_native_multiround_status_stream_or_fail_closed_lb_closeout",
            decision["next_gate"],
        )

    def test_requirements_are_generic_and_claims_stay_closed(self) -> None:
        payload = self.artifact
        requirements = payload["next_native_status_stream_requirements"]
        self.assertEqual(
            "generic_native_multi_round_active_query_status_stream",
            requirements["required_contract_kind"],
        )
        self.assertTrue(requirements["must_change_denominator"])
        self.assertIn(
            "hard-code 62 rows per active query",
            requirements["forbidden_implementation_shortcuts"],
        )
        self.assertIn(
            "X-HD-specific native primitive names or paper semantics in RTDL core",
            requirements["forbidden_implementation_shortcuts"],
        )

        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["fanout_diagnostic_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "hash_sample_parity_claimed",
            "per_query_distribution_claimed",
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
