from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1308V15PolygonFloatSumContractTest(unittest.TestCase):
    def test_float_sum_contracts_validate(self) -> None:
        contracts = rt.validate_v1_5_float_sum_reduction_contracts()
        self.assertEqual(len(contracts), 2)

    def test_polygon_pair_exact_area_contract_is_design_required(self) -> None:
        contracts = rt.validate_v1_5_float_sum_reduction_contracts()
        by_row = {(row["app"], row["subpath"]): row for row in contracts}
        contract = by_row[("polygon_pair_overlap_area_rows", "exact_area_sum")]

        self.assertEqual(contract["status"], "design_required")
        self.assertEqual(contract["reduction_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(contract["dtype"], "float64")
        self.assertEqual(contract["value_fields"], ("intersection_area", "union_area"))
        self.assertIn("exact integer parity", contract["current_oracle_policy"])

    def test_jaccard_float_sum_remains_blocked_by_collect_k(self) -> None:
        contracts = rt.validate_v1_5_float_sum_reduction_contracts()
        by_row = {(row["app"], row["subpath"]): row for row in contracts}
        contract = by_row[("polygon_set_jaccard", "exact_score_sum")]

        self.assertEqual(contract["status"], "blocked_by_collect_k_bounded")
        self.assertIn("no silent bounded-collection truncation", contract["current_oracle_policy"])
        self.assertIn("diagnostic only", contract["claim_boundary"])

    def test_inventory_remaining_polygon_rows_match_float_contract(self) -> None:
        inventory = {
            (row["app"], row["subpath"]): row
            for row in rt.validate_v1_5_generic_migration_inventory()
        }
        polygon = inventory[("polygon_pair_overlap_area_rows", "candidate_discovery_and_exact_area")]
        jaccard = inventory[("polygon_set_jaccard", "chunked_candidate_scoring")]

        self.assertEqual(polygon["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(polygon["status"], "pod_verified_generic")
        self.assertEqual(jaccard["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(jaccard["status"], "diagnostic_blocked")


if __name__ == "__main__":
    unittest.main()
