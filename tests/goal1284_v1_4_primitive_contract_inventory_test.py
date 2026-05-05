from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1284V14PrimitiveContractInventoryTest(unittest.TestCase):
    def test_inventory_covers_supported_app_rows(self) -> None:
        contracts = rt.validate_v1_4_primitive_contract_inventory()

        app_rows = {contract["app_row"] for contract in contracts}
        self.assertEqual(
            app_rows,
            {
                "graph_analytics.visibility_edges",
                "database_analytics.sales_risk",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
            },
        )

    def test_active_backend_scope_is_embree_and_optix_only(self) -> None:
        contracts = rt.validate_v1_4_primitive_contract_inventory()

        active_by_row: dict[str, set[str]] = {}
        for contract in contracts:
            if contract["active_v1_4_backend"]:
                active_by_row.setdefault(contract["app_row"], set()).add(contract["backend"])

        self.assertEqual(
            active_by_row,
            {
                "graph_analytics.visibility_edges": {"embree", "optix"},
                "database_analytics.sales_risk": {"embree", "optix"},
                "polygon_pair_overlap_area_rows": {"embree", "optix"},
                "polygon_set_jaccard": {"embree", "optix"},
            },
        )

    def test_frozen_backends_remain_inactive_before_v2_1(self) -> None:
        contracts = rt.validate_v1_4_primitive_contract_inventory()
        frozen = set(rt.FROZEN_BEFORE_V2_1_BACKENDS)
        frozen_contracts = [contract for contract in contracts if contract["backend"] in frozen]

        self.assertEqual(len(frozen_contracts), 12)
        for contract in frozen_contracts:
            with self.subTest(app_row=contract["app_row"], backend=contract["backend"]):
                self.assertFalse(contract["active_v1_4_backend"])
                self.assertEqual(contract["backend_contract_role"], "compatibility_or_inactive")
                self.assertFalse(contract["same_contract_baseline_required"])

    def test_jaccard_inventory_remains_diagnostic(self) -> None:
        contracts = rt.validate_v1_4_primitive_contract_inventory()
        jaccard_contracts = [
            contract for contract in contracts if contract["app_row"] == "polygon_set_jaccard"
        ]

        for contract in jaccard_contracts:
            with self.subTest(backend=contract["backend"]):
                self.assertEqual(contract["status"], "optix_still_slower_with_reason")
                self.assertFalse(contract["public_wording_allowed"])
                self.assertEqual(contract["migration_status"], "diagnostic_metadata_only")


if __name__ == "__main__":
    unittest.main()
