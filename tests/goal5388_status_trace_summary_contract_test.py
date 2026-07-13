from __future__ import annotations

import importlib.util
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
    / "build_xhd_goal5388_status_trace_summary_contract.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5388_status_trace_summary_contract.json"
)


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_goal5388_status_trace_summary_contract",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5388StatusTraceSummaryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_builder()
        cls.artifact = cls.module.build(output=ARTIFACT)

    def test_artifact_links_generic_api_to_goal5387_author_trace_v2(self) -> None:
        payload = self.artifact
        self.assertEqual("Goal5388", payload["goal"])
        self.assertEqual(
            "status_trace_summary_api_ready__next_native_stream_must_emit_summary",
            payload["exit_label"],
        )

        system_api = payload["system_api"]
        self.assertEqual("active_query_status_trace_summary_numpy_columns", system_api["function"])
        self.assertEqual("generic_active_query_status_trace_summary_v1", system_api["contract"])
        self.assertEqual("none", system_api["app_semantics"])
        self.assertEqual(4, system_api["demo_summary"]["row_count"])
        self.assertEqual([0, 2, 3], system_api["demo_summary"]["sample_indices"])

        target = payload["author_trace_v2_target"]
        self.assertEqual("rtdl.goal5385.author.lb_status_trace.v2", target["schema"])
        self.assertEqual(437645, target["active_in_queue_size"])
        self.assertEqual(27133990, target["raw_offload_rows_before_sort_reduce"])
        self.assertEqual(27133990, target["status_count_offloading_append"])
        self.assertIsInstance(target["raw_offload_row_hash"], int)
        self.assertEqual(3, len(target["raw_offload_row_sample_point_ids"]))
        self.assertEqual(3, len(target["raw_offload_row_sample_cell_ids"]))

    def test_current_rtdl_gap_remains_explicit(self) -> None:
        gap = self.artifact["current_rtdl_candidate_gap"]
        self.assertFalse(gap["any_row_count_parity"])
        self.assertFalse(gap["any_hash_sample_comparable"])
        by_source = {item["source"]: item for item in gap["candidates"]}
        self.assertEqual(2188225, by_source["Goal5381 full bridge probe"]["offload_rows"])
        self.assertEqual(
            2188225,
            by_source["Goal5383 active-initial-best full bridge probe"]["offload_rows"],
        )
        for item in gap["candidates"]:
            self.assertFalse(item["row_count_parity"])
            self.assertFalse(item["hash_sample_comparable"])

    def test_claim_boundary_keeps_paper_and_lb_claims_false(self) -> None:
        boundary = self.artifact["claim_boundary"]
        self.assertTrue(boundary["generic_status_trace_summary_api_claimed"])
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

    def test_builder_cli_writes_artifact(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn(str(ARTIFACT), completed.stdout)
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(self.artifact["schema"], payload["schema"])


if __name__ == "__main__":
    unittest.main()
