from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl import optix_runtime as optix_rt


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal2568_partner_resident_dispatcher_grouped_contract_2026-05-23.md"


class _Query:
    group_keys = ("region_id",)
    value_field = "revenue"
    predicates = ()


class Goal2568PartnerResidentDispatcherGroupedContractTest(unittest.TestCase):
    def test_dispatcher_metadata_embeds_grouped_reduction_contract(self) -> None:
        metadata = optix_rt._partner_resident_grouped_i64_reduction_metadata(
            _Query(),
            reduction_name="sum_count",
            semantic_aggregate="avg_as_sum_count",
            group_capacity=8,
            row_count=3,
        )
        contract = metadata["grouped_reduction_contract"]
        capacity = metadata["grouped_reduction_capacity_status"]

        self.assertEqual(contract["contract_version"], "rtdl.grouped_reduction.v1")
        self.assertEqual(contract["operation"], "group_sum_count_i64")
        self.assertEqual(contract["group_keys"], ("region_id",))
        self.assertEqual(contract["value_field"], "revenue")
        self.assertEqual(contract["group_capacity"], 8)
        self.assertEqual(capacity["group_capacity"], 8)
        self.assertEqual(capacity["row_count"], 3)
        self.assertEqual(capacity["required_capacity"], 3)
        self.assertFalse(capacity["overflowed"])
        self.assertEqual(metadata["semantic_aggregate"], "avg_as_sum_count")
        self.assertEqual(metadata["reduction"], "sum_count")

    def test_count_contract_has_no_value_field(self) -> None:
        metadata = optix_rt._partner_resident_grouped_i64_reduction_metadata(
            _Query(),
            reduction_name="count",
            semantic_aggregate=None,
            group_capacity=8,
            row_count=2,
        )
        contract = metadata["grouped_reduction_contract"]
        self.assertEqual(contract["operation"], "group_count")
        self.assertIsNone(contract["value_field"])
        self.assertEqual(metadata["result_fields"], ["region_id", "count"])

    def test_runtime_source_preserves_legacy_metadata_keys(self) -> None:
        text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn('"partner_resident_grouped_i64_dispatcher"', text)
        self.assertIn('"native_reduction_symbol"', text)
        self.assertIn('"grouped_reduction_contract"', text)
        self.assertIn('"grouped_reduction_capacity_status"', text)
        self.assertIn("GroupedReductionSpec", text)
        self.assertIn("GroupedReductionCapacityStatus", text)

    def test_report_records_dispatcher_contract_bridge(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2568", text)
        self.assertIn("partner-resident grouped i64 dispatcher", text)
        self.assertIn("GroupedReductionSpec", text)
        self.assertIn("GroupedReductionCapacityStatus", text)
        self.assertIn("keeps existing metadata keys", text)


if __name__ == "__main__":
    unittest.main()
