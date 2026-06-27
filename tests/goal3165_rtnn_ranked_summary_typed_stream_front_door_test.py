from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

import rtdsl as rt
from examples.benchmark_apps.rtnn import rtdl_rtnn_benchmark_app as rtnn


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = REPO_ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3165_rtnn_ranked_summary_typed_stream_front_door_2026-06-03.md"


def _to_host(value):
    if hasattr(value, "detach") and hasattr(value, "cpu"):
        return value.detach().cpu().tolist()
    if hasattr(value, "copy_to_host"):
        return value.copy_to_host().tolist()
    if hasattr(value, "get"):
        return value.get().tolist()
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


class Goal3165RtnnRankedSummaryTypedStreamFrontDoorTest(unittest.TestCase):
    def test_generic_ranked_summary_front_door_is_exported_and_non_authorizing(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("def execute_ranked_summary_typed_stream_partner_columns", adapter)
        self.assertIn("caller_supplied_partner_columns_no_hidden_host_rows", adapter)
        self.assertTrue(hasattr(rt, "execute_ranked_summary_typed_stream_partner_columns"))

        request = rt.execute_ranked_summary_typed_stream_partner_columns(
            group_ids=np.asarray([0, 0, 1], dtype=np.int64),
            item_ids=np.asarray([7, 3, 9], dtype=np.int64),
            scores=np.asarray([0.5, 1.25, 0.75], dtype=np.float64),
            group_count=2,
            operation="grouped_argmin_f64",
            partner="numba",
            stream_id="goal3165_dry_run",
            dry_run=True,
        )
        self.assertEqual(request["status"], "dry_run_partner_consumer_request")
        self.assertEqual(request["typed_stream"]["stream_kind"], "ranked_summary_stream")
        self.assertEqual(request["continuation_plan"]["operation"], "grouped_argmin_f64")
        self.assertEqual(request["continuation_plan"]["item_column"], "item_ids")
        self.assertEqual(request["source_materialization"], "caller_supplied_partner_columns_no_hidden_host_rows")
        self.assertFalse(request["automatic_partner_selection_allowed"])
        self.assertFalse(request["release_authorized"])
        self.assertFalse(request["true_zero_copy_claim_authorized"])

        with self.assertRaisesRegex(ValueError, "explicit partner"):
            rt.execute_ranked_summary_typed_stream_partner_columns(
                group_ids=np.asarray([0], dtype=np.int64),
                item_ids=np.asarray([1], dtype=np.int64),
                scores=np.asarray([1.0], dtype=np.float64),
                group_count=1,
                operation="grouped_argmin_f64",
                partner="auto",
                stream_id="goal3165_auto_reject",
                dry_run=True,
            )

    def test_rtnn_descriptor_uses_generic_ranked_summary_front_door(self) -> None:
        descriptor = rtnn.describe_rtnn_v2_8_ranked_summary_typed_stream(
            operation="grouped_topk_f64",
            partner="torch",
            k=2,
        )
        self.assertEqual(descriptor["contract_version"], rtnn.RTNN_V2_8_RANKED_SUMMARY_TYPED_STREAM_VERSION)
        self.assertEqual(descriptor["execution_path"], rtnn.RTNN_V2_8_RANKED_SUMMARY_EXECUTION_PATH)
        self.assertEqual(descriptor["typed_stream"]["stream_kind"], "ranked_summary_stream")
        self.assertEqual(descriptor["continuation_plan"]["operation"], "grouped_topk_f64")
        self.assertEqual(descriptor["continuation_plan"]["user_selected_partner"], "torch")
        self.assertTrue(descriptor["requires_caller_supplied_partner_columns"])
        self.assertFalse(descriptor["claim_boundary"]["full_rtnn_paper_reproduction"])
        self.assertFalse(descriptor["claim_boundary"]["public_speedup_claim_authorized"])

        app = APP.read_text(encoding="utf-8")
        self.assertIn("describe_rtnn_v2_8_ranked_summary_typed_stream", app)
        self.assertIn("run_rtnn_v2_8_ranked_summary_typed_stream_preview", app)
        self.assertIn(rtnn.RTNN_V2_8_RANKED_SUMMARY_EXECUTION_PATH, app)

    def test_torch_topk_preview_matches_deterministic_ranked_summary_when_available(self) -> None:
        try:
            import torch
        except Exception as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"torch is not available: {exc}")

        inputs = {
            "group_ids": torch.tensor([0, 0, 0, 1, 1], dtype=torch.int64),
            "item_ids": torch.tensor([7, 3, 5, 9, 8], dtype=torch.int64),
            "scores": torch.tensor([1.0, 1.0, 0.5, 2.0, 2.0], dtype=torch.float64),
            "group_count": 2,
        }
        payload = rtnn.run_rtnn_v2_8_ranked_summary_typed_stream_preview(
            inputs,
            operation="grouped_topk_f64",
            partner="torch",
            k=2,
        )
        self.assertEqual(payload["execution_path"], rtnn.RTNN_V2_8_RANKED_SUMMARY_EXECUTION_PATH)
        self.assertEqual(payload["typed_stream"]["stream_kind"], "ranked_summary_stream")
        self.assertEqual(_to_host(payload["outputs"]["group_ids"]), [0, 0, 1, 1])
        self.assertEqual(_to_host(payload["outputs"]["item_ids"]), [5, 3, 8, 9])
        self.assertEqual(_to_host(payload["outputs"]["scores"]), [0.5, 1.0, 2.0, 2.0])
        self.assertEqual(_to_host(payload["outputs"]["ranks"]), [1, 2, 1, 2])
        self.assertEqual(_to_host(payload["outputs"]["row_offsets"]), [0, 2, 4])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "execute_ranked_summary_typed_stream_partner_columns",
            "run_rtnn_v2_8_ranked_summary_typed_stream_preview",
            "ranked_summary_stream",
            "`automatic_partner_selection_allowed: False`",
            "does not claim full RTNN paper reproduction",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
