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
    / "build_xhd_goal5389_bridge_trace_summary_smoke.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5389_bridge_trace_summary_smoke.json"
)


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_goal5389_bridge_trace_summary_smoke",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5389BridgeTraceSummarySmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_builder()
        cls.artifact = cls.module.build(output=ARTIFACT)

    def test_source_limited_pod_smoke_emits_generic_trace_summary(self) -> None:
        payload = self.artifact
        self.assertEqual(
            "bridge_trace_summary_smoke_ready__full_native_stream_parity_still_required",
            payload["exit_label"],
        )
        self.assertTrue(payload["run_scope"]["source_limit_applied"])
        self.assertEqual(64, payload["run_scope"]["source_limit"])
        summary = payload["rtdl_trace_summary"]
        self.assertEqual("generic_active_query_status_trace_summary_v1", summary["contract"])
        self.assertEqual("none", summary["app_semantics"])
        self.assertEqual(320, summary["row_count"])
        self.assertEqual(320, summary["status_count_offloading"])
        self.assertEqual(64, summary["active_query_count"])
        self.assertIsInstance(summary["raw_offload_row_hash"], int)
        self.assertEqual(["source_ids", "cell_ids"], summary["hash_columns"])
        self.assertEqual([0, 160, 319], summary["sample_indices"])
        self.assertEqual([0, 32, 63], summary["samples"]["source_ids"])
        self.assertEqual([6279, 6286, 6145], summary["samples"]["cell_ids"])

    def test_author_comparison_is_comparable_but_not_parity(self) -> None:
        comparison = self.artifact["comparison_to_author"]
        self.assertFalse(comparison["active_query_count_parity"])
        self.assertFalse(comparison["row_count_parity"])
        self.assertTrue(comparison["hash_comparable_to_author"])
        self.assertFalse(comparison["hash_parity"])
        self.assertTrue(comparison["sample_comparable_to_author"])
        self.assertEqual(320, comparison["rtdl_bridge_offload_rows"])
        self.assertEqual(27133990, comparison["author_raw_offload_rows_before_sort_reduce"])

    def test_claim_boundary_keeps_source_limited_smoke_narrow(self) -> None:
        boundary = self.artifact["claim_boundary"]
        self.assertTrue(boundary["trace_summary_plumbing_claimed"])
        for key in (
            "source_limited_smoke_claimed_as_author_parity",
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
