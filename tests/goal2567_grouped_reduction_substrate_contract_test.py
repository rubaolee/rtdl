from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
GROUPED_REDUCTION = ROOT / "src/rtdsl/grouped_reduction.py"
REPORT = ROOT / "docs/reports/goal2567_grouped_reduction_substrate_contract_2026-05-23.md"


class Goal2567GroupedReductionSubstrateContractTest(unittest.TestCase):
    def test_public_grouped_reduction_contract_exports(self) -> None:
        self.assertEqual(rt.GROUPED_REDUCTION_CONTRACT_VERSION, "rtdl.grouped_reduction.v1")
        self.assertIn("group_any", rt.GROUPED_REDUCTION_OPERATIONS)
        self.assertIn("group_sum_count_i64", rt.GROUPED_REDUCTION_OPERATIONS)
        self.assertIn("GroupedReductionSpec", rt.__all__)
        self.assertIn("GroupedReductionCapacityStatus", rt.__all__)

    def test_spec_validation_and_metadata(self) -> None:
        spec = rt.normalize_grouped_reduction_spec(
            {
                "operation": "group_sum_count_i64",
                "group_keys": ["region_id"],
                "value_field": "revenue",
                "group_capacity": 4,
            }
        )
        self.assertIsInstance(spec, rt.GroupedReductionSpec)
        self.assertEqual(spec.operation, "group_sum_count_i64")
        self.assertEqual(spec.group_keys, ("region_id",))
        self.assertEqual(spec.value_field, "revenue")
        self.assertEqual(spec.group_capacity, 4)
        metadata = spec.to_metadata()
        self.assertEqual(metadata["output_mode"], "compact_rows")
        self.assertEqual(metadata["overflow_policy"], "fail_closed")
        self.assertIn("does not authorize", metadata["claim_boundary"])

    def test_spec_rejects_invalid_value_field_shapes(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires a value_field"):
            rt.GroupedReductionSpec(operation="group_sum_i64", group_keys=("g",))
        with self.assertRaisesRegex(ValueError, "does not accept a value_field"):
            rt.GroupedReductionSpec(operation="group_count", group_keys=("g",), value_field="v")
        with self.assertRaisesRegex(ValueError, "at least one group key"):
            rt.GroupedReductionSpec(operation="group_count", group_keys=())

    def test_columnar_aggregate_maps_to_shared_grouped_reduction_spec(self) -> None:
        count_spec = rt.columnar_plan_to_grouped_reduction_spec(
            {"aggregate": "count", "group_keys": ("region_id",)}
        )
        self.assertEqual(count_spec.operation, "group_count")
        self.assertIsNone(count_spec.value_field)

        avg_spec = rt.columnar_plan_to_grouped_reduction_spec(
            {"aggregate": "avg_as_sum_count", "group_keys": ("region_id",), "value_field": "revenue"}
        )
        self.assertEqual(avg_spec.operation, "group_sum_count_i64")
        self.assertEqual(avg_spec.value_field, "revenue")

    def test_capacity_status_is_fail_closed(self) -> None:
        ok = rt.GroupedReductionCapacityStatus(group_capacity=3, row_count=3, required_capacity=3)
        self.assertFalse(ok.overflowed)
        overflowed = rt.GroupedReductionCapacityStatus(
            group_capacity=3,
            row_count=0,
            required_capacity=4,
            overflowed=True,
        )
        self.assertEqual(overflowed.to_metadata()["overflow_policy"], "fail_closed")
        with self.assertRaisesRegex(RuntimeError, "overflowed group_capacity=3"):
            overflowed.raise_if_overflowed(operation="group_count")
        with self.assertRaisesRegex(ValueError, "must not expose partial rows"):
            rt.GroupedReductionCapacityStatus(
                group_capacity=3,
                row_count=3,
                required_capacity=4,
                overflowed=True,
            )

    def test_shared_contract_has_no_app_vocabulary(self) -> None:
        text = GROUPED_REDUCTION.read_text(encoding="utf-8").lower()
        for forbidden in ("dbscan", "raydb", "robot", "collision", "barnes", "inverse_square"):
            self.assertNotIn(forbidden, text)

    def test_report_records_contract_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2567", text)
        self.assertIn("GroupedReductionSpec", text)
        self.assertIn("GroupedReductionCapacityStatus", text)
        self.assertIn("does not migrate native call paths", text)
        self.assertIn("no public speedup claim", text)


if __name__ == "__main__":
    unittest.main()
