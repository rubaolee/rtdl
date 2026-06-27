from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from examples.benchmark_apps.barnes_hut import (
    rtdl_barnes_hut_benchmark_app as barnes_hut,
)
from examples.benchmark_apps.rtnn import rtdl_rtnn_benchmark_app as rtnn


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3804_typed_stream_benchmark_alias_cleanup_2026-06-07.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
BH_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "barnes_hut"
    / "rtdl_barnes_hut_benchmark_app.py"
)
RTNN_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "rtnn"
    / "rtdl_rtnn_benchmark_app.py"
)


class Goal3804TypedStreamBenchmarkAliasCleanupTest(unittest.TestCase):
    def test_barnes_hut_current_descriptor_alias_preserves_legacy_contract(self) -> None:
        current = barnes_hut.describe_barnes_hut_grouped_vector_sum_typed_stream(partner="cupy")
        legacy = barnes_hut.describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream(partner="cupy")

        self.assertEqual(current["legacy_helper_alias"], "describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream")
        self.assertEqual(current["current_helper"], "describe_barnes_hut_grouped_vector_sum_typed_stream")
        self.assertEqual(current["current_mode_alias"], "grouped_vector_sum_typed_stream_plan")
        self.assertEqual(current["contract_version"], legacy["contract_version"])
        self.assertEqual(current["execution_path"], legacy["execution_path"])
        self.assertEqual(current["operation"], "grouped_vector_sum_f64x2")
        self.assertFalse(current["claim_boundary"]["automatic_partner_selection_allowed"])
        self.assertFalse(current["claim_boundary"]["public_speedup_claim_authorized"])

    def test_barnes_hut_current_runner_alias_preserves_dry_run_contract(self) -> None:
        inputs = {
            "group_ids": (0, 0, 1),
            "values_x": (1.0, 2.0, -3.0),
            "values_y": (0.5, 1.5, -2.0),
            "group_count": 2,
            "row_offsets": (0, 2, 3),
        }
        payload = barnes_hut.run_barnes_hut_grouped_vector_sum_typed_stream_preview(
            inputs,
            partner="cupy",
            dry_run=True,
        )
        self.assertEqual(payload["legacy_helper_alias"], "run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview")
        self.assertEqual(payload["current_helper"], "run_barnes_hut_grouped_vector_sum_typed_stream_preview")
        self.assertEqual(payload["typed_stream"]["stream_kind"], "grouped_reduction_stream")
        self.assertFalse(payload["claim_boundary"]["release_authorized"])

    def test_rtnn_current_descriptor_alias_preserves_legacy_contract(self) -> None:
        current = rtnn.describe_rtnn_ranked_summary_typed_stream(
            operation="grouped_topk_f64",
            partner="torch",
            k=4,
        )
        legacy = rtnn.describe_rtnn_v2_8_ranked_summary_typed_stream(
            operation="grouped_topk_f64",
            partner="torch",
            k=4,
        )

        self.assertEqual(current["legacy_helper_alias"], "describe_rtnn_v2_8_ranked_summary_typed_stream")
        self.assertEqual(current["current_helper"], "describe_rtnn_ranked_summary_typed_stream")
        self.assertEqual(current["current_mode_alias"], "ranked_summary_typed_stream_plan")
        self.assertEqual(current["contract_version"], legacy["contract_version"])
        self.assertEqual(current["execution_path"], legacy["execution_path"])
        self.assertEqual(current["operation"], "grouped_topk_f64")
        self.assertFalse(current["partner_policy"]["automatic_partner_selection_allowed"])
        self.assertFalse(current["claim_boundary"]["public_speedup_claim_authorized"])

    def test_rtnn_current_runner_alias_preserves_dry_run_contract(self) -> None:
        inputs = {
            "group_ids": (0, 0, 1),
            "item_ids": (7, 3, 9),
            "scores": (0.5, 1.25, 0.75),
            "group_count": 2,
        }
        payload = rtnn.run_rtnn_ranked_summary_typed_stream_preview(
            inputs,
            operation="grouped_topk_f64",
            partner="torch",
            k=2,
            dry_run=True,
        )
        self.assertEqual(payload["legacy_helper_alias"], "run_rtnn_v2_8_ranked_summary_typed_stream_preview")
        self.assertEqual(payload["current_helper"], "run_rtnn_ranked_summary_typed_stream_preview")
        self.assertEqual(payload["typed_stream"]["stream_kind"], "ranked_summary_stream")
        self.assertFalse(payload["claim_boundary"]["release_authorized"])

    def test_cli_current_modes_are_available(self) -> None:
        bh = subprocess.run(
            [sys.executable, str(BH_APP), "--mode", "grouped_vector_sum_typed_stream_plan"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        bh_payload = json.loads(bh.stdout)
        self.assertEqual(
            bh_payload["benchmark_metadata"]["mode"],
            "grouped_vector_sum_typed_stream_plan",
        )
        self.assertEqual(
            bh_payload["current_helper"],
            "describe_barnes_hut_grouped_vector_sum_typed_stream",
        )

        rtnn_completed = subprocess.run(
            [sys.executable, str(RTNN_APP), "--mode", "ranked_summary_typed_stream_plan"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        rtnn_payload = json.loads(rtnn_completed.stdout)
        self.assertEqual(rtnn_payload["current_helper"], "describe_rtnn_ranked_summary_typed_stream")
        self.assertEqual(rtnn_payload["current_mode_alias"], "ranked_summary_typed_stream_plan")

    def test_report_and_todo_record_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3804",
            "Barnes-Hut grouped vector sum",
            "RTNN ranked summary",
            "No native engine code changed",
            "Historical versioned protocol constants remain stable",
        ):
            self.assertIn(phrase, text)
        todo = TODO.read_text(encoding="utf-8")
        self.assertIn("Goal3804 added current aliases", todo)
        self.assertIn("RTNN ranked-summary typed-stream", todo)


if __name__ == "__main__":
    unittest.main()
