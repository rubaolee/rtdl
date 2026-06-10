from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from examples.current.research_benchmarks.raydb_style import (
    rtdl_raydb_style_benchmark_app as raydb,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3802_raydb_current_helper_alias_cleanup_2026-06-07.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal3802RaydbCurrentHelperAliasCleanupTest(unittest.TestCase):
    def test_primitive_first_alias_preserves_legacy_plan(self) -> None:
        current = raydb.describe_raydb_primitive_first_plan("sum")
        legacy = raydb.describe_raydb_v2_5_primitive_first_plan("sum")

        self.assertEqual(current["legacy_helper_alias"], "describe_raydb_v2_5_primitive_first_plan")
        self.assertEqual(current["current_helper"], "describe_raydb_primitive_first_plan")
        for key in (
            "selected_backend",
            "selected_path",
            "selected_generic_primitive",
            "selected_reduction",
            "partner_continuation_required",
            "typed_hit_stream_forced",
        ):
            self.assertEqual(current[key], legacy[key])
        self.assertFalse(current["public_speedup_claim_authorized"])
        self.assertFalse(current["true_zero_copy_authorized"])

    def test_numba_grouped_reduction_alias_preserves_legacy_descriptor(self) -> None:
        current = raydb.describe_raydb_numba_grouped_reduction_continuation("avg_as_sum_count")
        legacy = raydb.describe_raydb_v2_6_numba_neutral_continuation("avg_as_sum_count")

        self.assertEqual(current["legacy_helper_alias"], "describe_raydb_v2_6_numba_neutral_continuation")
        self.assertEqual(current["current_contract_name"], "numba_grouped_reduction_continuation")
        self.assertEqual(current["selected_partner"], "numba")
        self.assertEqual(current["operations"], legacy["operations"])
        self.assertTrue(current["uses_v2_6_neutral_partner_handoff"])
        self.assertFalse(current["uses_legacy_torch_carrier"])
        self.assertFalse(current["public_speedup_claim_authorized"])

    def test_grouped_reduction_typed_stream_alias_preserves_legacy_descriptor(self) -> None:
        current = raydb.describe_raydb_grouped_reduction_typed_stream_continuation(
            "avg_as_sum_count",
            partner="numba",
        )
        legacy = raydb.describe_raydb_v2_8_typed_stream_continuation(
            "avg_as_sum_count",
            partner="numba",
        )

        self.assertEqual(current["legacy_helper_alias"], "describe_raydb_v2_8_typed_stream_continuation")
        self.assertEqual(current["current_contract_name"], "grouped_reduction_typed_stream_continuation")
        self.assertEqual(current["selected_partner"], "numba")
        self.assertEqual(current["execution_path"], legacy["execution_path"])
        self.assertEqual(current["operations"], legacy["operations"])
        self.assertTrue(current["uses_v2_8_grouped_reduction_front_door"])
        self.assertFalse(current["true_zero_copy_claim_authorized"])

    def test_current_preview_aliases_fail_closed_on_host_numpy_arrays(self) -> None:
        inputs = {
            "group_ids": np.asarray([0, 1], dtype=np.int64),
            "values": np.asarray([1.0, 2.0], dtype=np.float64),
            "group_count": 2,
        }

        with self.assertRaisesRegex(ValueError, "device-resident CUDA column is required"):
            raydb.run_raydb_numba_grouped_reduction_continuation_preview("sum", inputs)
        with self.assertRaisesRegex(ValueError, "device-resident CUDA column is required"):
            raydb.run_raydb_grouped_reduction_typed_stream_continuation_preview("sum", inputs)

    def test_report_and_todo_record_raydb_scope_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3802",
            "describe_raydb_primitive_first_plan",
            "run_raydb_grouped_reduction_typed_stream_continuation_preview",
            "No native engine code changed",
            "Historical protocol names remain",
        ):
            self.assertIn(phrase, text)
        todo = TODO.read_text(encoding="utf-8")
        self.assertIn("Goal3802 applied the same pattern", todo)
        self.assertIn("RayDB's app-facing helper layer", todo)


if __name__ == "__main__":
    unittest.main()
