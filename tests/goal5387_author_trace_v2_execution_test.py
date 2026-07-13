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
    / "build_xhd_goal5387_author_trace_v2_execution.py"
)
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5387_author_trace_v2_execution.json"
)


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_goal5387_author_trace_v2_execution",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5387AuthorTraceV2ExecutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_builder()
        cls.artifact = cls.module.build(output=RESULT)

    def test_author_trace_v2_pod_execution_counts_match_goal5374(self) -> None:
        artifact = self.artifact
        self.assertEqual(
            "rtdl.paper_reproduction.xhd.goal5387.author_trace_v2_execution.v1",
            artifact["schema"],
        )
        self.assertEqual(
            "author_trace_v2_oracle_ready__native_counterpart_next",
            artifact["exit_label"],
        )

        trace = artifact["author_lb_trace_v2"]
        self.assertEqual("rtdl.goal5385.author.lb_status_trace.v2", trace["schema"])
        self.assertEqual(437645, trace["active_in_queue_size"])
        self.assertEqual(27133990, trace["raw_offload_rows_before_sort_reduce"])
        self.assertEqual(27133990, trace["status_count_offloading_append"])
        self.assertEqual(437645, trace["status_count_init"])

        comparison = artifact["comparison_to_goal5374"]
        self.assertTrue(comparison["all_core_counts_match_goal5374"])
        for key, value in comparison["count_parity"].items():
            self.assertIs(value, True, key)

    def test_author_trace_v2_exposes_state_hashes_samples_and_feedback(self) -> None:
        validation = self.artifact["field_validation"]
        self.assertTrue(validation["all_required_batch_fields_present"])
        self.assertTrue(validation["hash_fields_present"])
        self.assertTrue(validation["sample_fields_present"])
        for field, present in validation["batch_field_presence"].items():
            self.assertIs(present, True, field)

        batch = self.artifact["author_lb_trace_v2"]["batch_0"]
        for field in (
            "cmin2_initial_hash",
            "cmin2_after_ray_hash",
            "cmin2_after_load_balance_hash",
            "raw_offload_row_hash",
        ):
            self.assertIsInstance(batch[field], int, field)
        self.assertEqual([0, 218822, 437644], batch["cmin2_sample_indices"])
        self.assertEqual(3, len(batch["cmin2_after_load_balance_samples"]))
        self.assertEqual(3, len(batch["raw_offload_row_sample_point_ids"]))
        self.assertEqual(3, len(batch["raw_offload_row_sample_cell_ids"]))
        self.assertEqual(437645, batch["load_balance_group_count"])
        self.assertEqual(27133990, batch["load_balance_input_row_count"])
        self.assertEqual(294, batch["load_balance_feedback_update_count"])

    def test_claim_boundary_keeps_rtdl_and_paper_claims_false(self) -> None:
        boundary = self.artifact["claim_boundary"]
        self.assertTrue(boundary["author_v2_trace_implemented"])
        self.assertTrue(boundary["author_v2_trace_executed_on_pod"])
        self.assertTrue(boundary["author_v2_trace_oracle_claimed"])

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
            self.assertIs(boundary[key], False, key)

    def test_author_instrumentation_is_author_tree_only(self) -> None:
        info = self.artifact["author_instrumentation"]
        self.assertTrue(info["source_modified_in_pod_only"])
        self.assertFalse(info["rtdl_core_modified"])
        self.assertTrue(info["goal5386_all_hooks_found"])
        self.assertTrue(info["goal5386_all_required_fields_covered"])
        self.assertIn("/tmp/xhd-goal5387/author", info["source_copy"])
        self.assertIn("hd_exec", info["binary"])


if __name__ == "__main__":
    unittest.main()
