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
    / "build_xhd_goal5390_full_trace_summary_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5390_full_trace_summary_gate.json"
)


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_goal5390_full_trace_summary_gate",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5390FullTraceSummaryGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_builder()
        cls.artifact = cls.module.build(output=ARTIFACT)

    def test_full_gate_not_source_limited_and_emits_trace_summary(self) -> None:
        payload = self.artifact
        self.assertEqual(
            "native_status_stream_denominator_mismatch__lb_remains_unsupported",
            payload["exit_label"],
        )
        self.assertFalse(payload["run_scope"]["source_limit_applied"])
        self.assertIsNone(payload["run_scope"]["source_limit"])
        self.assertEqual(437645, payload["run_scope"]["point_count_a"])
        summary = payload["rtdl_trace_summary"]
        self.assertEqual("generic_active_query_status_trace_summary_v1", summary["contract"])
        self.assertEqual("none", summary["app_semantics"])
        self.assertEqual(437645, summary["active_query_count"])
        self.assertEqual(2188225, summary["row_count"])
        self.assertEqual(2188225, summary["status_count_offloading"])
        self.assertEqual(10510374331443640811, summary["raw_offload_row_hash"])
        self.assertEqual([0, 1094112, 2188224], summary["sample_indices"])

    def test_active_count_matches_but_author_row_hash_parity_fails(self) -> None:
        comparison = self.artifact["comparison_to_author"]
        self.assertTrue(comparison["active_query_count_parity"])
        self.assertFalse(comparison["row_count_parity"])
        self.assertFalse(comparison["hash_parity"])
        self.assertTrue(comparison["hash_comparable_to_author"])
        self.assertTrue(comparison["sample_comparable_to_author"])
        self.assertEqual(2188225, comparison["rtdl_bridge_offload_rows"])
        self.assertEqual(27133990, comparison["author_raw_offload_rows_before_sort_reduce"])
        self.assertEqual(24945765, comparison["row_delta_author_minus_rtdl_bridge"])
        self.assertEqual(10510374331443640811, comparison["rtdl_raw_offload_row_hash"])
        self.assertEqual(4333109858711462591, comparison["author_raw_offload_row_hash"])
        self.assertEqual([18080, 219488, 437599], comparison["rtdl_sample_source_ids"])
        self.assertEqual([11168, 210712, 437119], comparison["author_raw_offload_row_sample_point_ids"])

    def test_claim_boundary_keeps_lb_and_figure_claims_false(self) -> None:
        boundary = self.artifact["claim_boundary"]
        self.assertTrue(boundary["full_trace_summary_gate_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "rtdl_row_count_parity_claimed",
            "rtdl_hash_sample_parity_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "same_denominator_memory_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "rtdl_author_performance_ratio_claimed",
            "exact_paper_dataset_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
