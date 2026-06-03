from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

import rtdsl as rt
from examples.v2_0.research_benchmarks.barnes_hut import rtdl_barnes_hut_benchmark_app as bh


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = REPO_ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
APP = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "rtdl_barnes_hut_benchmark_app.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3169_barnes_hut_grouped_vector_typed_stream_front_door_2026-06-03.md"


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


class Goal3169BarnesHutGroupedVectorTypedStreamFrontDoorTest(unittest.TestCase):
    def test_generic_grouped_vector_front_door_is_exported_and_non_authorizing(self) -> None:
        adapter = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("def execute_grouped_vector_sum_typed_stream_partner_columns", adapter)
        self.assertIn("caller_supplied_partner_columns_no_hidden_host_rows", adapter)
        self.assertTrue(hasattr(rt, "execute_grouped_vector_sum_typed_stream_partner_columns"))

        request = rt.execute_grouped_vector_sum_typed_stream_partner_columns(
            group_ids=np.asarray([0, 0, 1], dtype=np.int64),
            values_x=np.asarray([1.0, 2.0, -4.0], dtype=np.float64),
            values_y=np.asarray([-1.0, 0.5, 3.0], dtype=np.float64),
            row_offsets=np.asarray([0, 2, 3], dtype=np.int64),
            group_count=2,
            partner="cupy",
            stream_id="goal3169_dry_run",
            dry_run=True,
        )
        self.assertEqual(request["status"], "dry_run_partner_consumer_request")
        self.assertEqual(request["typed_stream"]["stream_kind"], "grouped_reduction_stream")
        self.assertEqual(request["continuation_plan"]["operation"], "grouped_vector_sum_f64x2")
        self.assertEqual(request["continuation_plan"]["value_columns"], ("values_x", "values_y"))
        self.assertTrue(request["row_offsets_provided"])
        self.assertEqual(
            {column["name"]: column["role"] for column in request["typed_stream"]["columns"]}["row_offsets"],
            "row_offset",
        )
        self.assertFalse(request["automatic_partner_selection_allowed"])
        self.assertFalse(request["release_authorized"])
        self.assertFalse(request["true_zero_copy_claim_authorized"])

        with self.assertRaisesRegex(ValueError, "explicit partner"):
            rt.execute_grouped_vector_sum_typed_stream_partner_columns(
                group_ids=np.asarray([0], dtype=np.int64),
                values_x=np.asarray([1.0], dtype=np.float64),
                values_y=np.asarray([2.0], dtype=np.float64),
                group_count=1,
                partner="auto",
                stream_id="goal3169_auto_reject",
                dry_run=True,
            )

    def test_barnes_hut_descriptor_uses_generic_grouped_vector_front_door(self) -> None:
        descriptor = bh.describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream(partner="cupy")

        self.assertEqual(descriptor["contract_version"], bh.BH_V2_8_GROUPED_VECTOR_TYPED_STREAM_VERSION)
        self.assertEqual(descriptor["execution_path"], bh.BH_V2_8_GROUPED_VECTOR_EXECUTION_PATH)
        self.assertEqual(descriptor["typed_stream"]["stream_kind"], "grouped_reduction_stream")
        self.assertEqual(descriptor["continuation_plan"]["operation"], "grouped_vector_sum_f64x2")
        self.assertEqual(descriptor["continuation_plan"]["user_selected_partner"], "cupy")
        self.assertTrue(descriptor["presegmented_offsets"])
        self.assertTrue(descriptor["requires_caller_supplied_partner_columns"])
        self.assertFalse(descriptor["claim_boundary"]["full_rt_barneshut_paper_reproduction"])
        self.assertFalse(descriptor["claim_boundary"]["native_force_law_embedded"])

        app = APP.read_text(encoding="utf-8")
        self.assertIn("describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream", app)
        self.assertIn("run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview", app)
        self.assertIn(bh.BH_V2_8_GROUPED_VECTOR_EXECUTION_PATH, app)

    def test_torch_vector_sum_preview_matches_componentwise_reference_when_available(self) -> None:
        try:
            import torch
        except Exception as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"torch is not available: {exc}")

        inputs = {
            "group_ids": torch.tensor([0, 0, 1, 1, 1], dtype=torch.int64),
            "values_x": torch.tensor([1.0, 2.0, -1.0, 4.0, 5.0], dtype=torch.float64),
            "values_y": torch.tensor([0.5, 1.0, 2.0, 3.0, -1.0], dtype=torch.float64),
            "group_count": 2,
        }
        payload = bh.run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview(
            inputs,
            partner="torch",
        )
        self.assertEqual(payload["execution_path"], bh.BH_V2_8_GROUPED_VECTOR_EXECUTION_PATH)
        self.assertEqual(payload["typed_stream"]["stream_kind"], "grouped_reduction_stream")
        self.assertEqual(_to_host(payload["outputs"]["group_ids"]), [0, 1])
        self.assertEqual(_to_host(payload["outputs"]["sum_x"]), [3.0, 8.0])
        self.assertEqual(_to_host(payload["outputs"]["sum_y"]), [1.5, 4.0])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "execute_grouped_vector_sum_typed_stream_partner_columns",
            "run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview",
            "grouped_vector_sum_f64x2",
            "`automatic_partner_selection_allowed: False`",
            "does not embed Barnes-Hut force law",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
