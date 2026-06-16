from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4432_v3_0_m35_aggregate_frontier_device_columns_contract_2026-06-16.md"
REFERENCE = ROOT / "src/rtdsl/aggregate_tree_reference.py"
INIT = ROOT / "src/rtdsl/__init__.py"

sys.path.insert(0, str(ROOT / "src"))


class Goal4432V30M35AggregateFrontierDeviceColumnsContractTest(unittest.TestCase):
    def test_contract_is_exported_and_implemented_by_m36(self) -> None:
        import rtdsl as rt

        contract = rt.validate_aggregate_frontier_device_columns_native_abi_contract()
        self.assertEqual(contract["primitive"], rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PRIMITIVE)
        self.assertEqual(contract["contract"], rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_NATIVE_ABI_CONTRACT)
        self.assertEqual(contract["logical_contract"], rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CONTRACT)
        self.assertEqual(contract["status"], "implemented_optix_device_columns")
        self.assertTrue(contract["executable"])
        self.assertTrue(contract["app_generic"])
        self.assertEqual(
            tuple(contract["required_native_symbols"]),
            rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_REQUIRED_SYMBOLS,
        )

    def test_handoff_contract_forbids_host_frontier_rows_before_partner(self) -> None:
        import rtdsl as rt

        contract = rt.aggregate_frontier_device_columns_native_abi_contract()
        handoff = contract["handoff_contract"]
        self.assertTrue(handoff["device_resident_payload_required"])
        self.assertTrue(handoff["same_stream_or_explicit_event_required"])
        self.assertTrue(handoff["partner_can_consume_without_frontier_d2h"])
        self.assertTrue(handoff["host_row_materialization_before_partner_forbidden"])
        forbidden_outputs = tuple(contract["hot_path_forbidden_outputs"])
        self.assertIn("frontier_i64_rows_host_tuple", forbidden_outputs)
        self.assertIn("frontier_rows_host_dicts", forbidden_outputs)

    def test_contract_is_app_generic_and_keeps_claims_false(self) -> None:
        import rtdsl as rt

        contract = rt.validate_aggregate_frontier_device_columns_native_abi_contract()
        payload = json.dumps(contract, sort_keys=True).lower()
        for forbidden in ("barnes", "dbscan", "collision", "contact", "rayjoin", "paper_specific"):
            self.assertNotIn(forbidden, payload)
        for key, value in contract["claim_boundary"].items():
            with self.subTest(key=key):
                if key == "implementation_claim_authorized":
                    self.assertTrue(value)
                else:
                    self.assertFalse(value)
        self.assertIn("force_law", contract["engine_exclusions"])
        self.assertIn("app_reduction", contract["engine_exclusions"])

    def test_source_and_init_expose_contract_names(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        for phrase in (
            "AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D",
            "AGGREGATE_FRONTIER_DEVICE_COLUMNS_REQUIRED_SYMBOLS",
            "aggregate_frontier_device_columns_native_abi_contract",
            "validate_aggregate_frontier_device_columns_native_abi_contract",
        ):
            self.assertIn(phrase, reference)
            self.assertIn(phrase, init)

    def test_report_records_m34_motivation_and_next_step(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "M34 showed",
            "3,440,003 rows",
            "specified_not_implemented",
            "device-resident",
            "same-stream or event-ordered",
            "AGGREGATE_FRONTIER_DEVICE_COLUMNS_REQUIRED_SYMBOLS",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
