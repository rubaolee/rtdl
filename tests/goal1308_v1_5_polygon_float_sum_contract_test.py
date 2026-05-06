from __future__ import annotations

import unittest

import rtdsl as rt


def _summary(_left, _right, _candidate_pairs):
    return {
        "total_intersection_area": 7,
        "total_union_area": 11,
        "overlap_pair_count": 2,
    }


class Goal1308V15PolygonFloatSumContractTest(unittest.TestCase):
    def test_float_sum_contracts_validate(self) -> None:
        contracts = rt.validate_v1_5_float_sum_reduction_contracts()
        self.assertEqual(len(contracts), 2)

    def test_float_sum_contract_layouts_are_registered(self) -> None:
        contracts = rt.validate_v1_5_float_sum_reduction_contracts()
        valid_layouts = set(rt.V1_5_POLYGON_FLOAT_SUM_RESULT_LAYOUTS)
        self.assertEqual(
            valid_layouts,
            {"summary_float64_sums", "summary_float64_sums_plus_ratio"},
        )
        for contract in contracts:
            with self.subTest(contract=contract["subpath"]):
                self.assertIn(contract["result_layout"], valid_layouts)

    def test_polygon_pair_exact_area_contract_is_verified_non_public(self) -> None:
        contracts = rt.validate_v1_5_float_sum_reduction_contracts()
        by_row = {(row["app"], row["subpath"]): row for row in contracts}
        contract = by_row[("polygon_pair_overlap_area_rows", "exact_area_sum")]

        self.assertEqual(contract["status"], "pod_verified_generic_non_public")
        self.assertEqual(contract["reduction_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(contract["dtype"], "float64")
        self.assertEqual(contract["value_fields"], ("intersection_area", "union_area"))
        self.assertIn("exact integer parity", contract["current_oracle_policy"])
        self.assertIn("backend-neutral native polygon-pair area summary", contract["current_oracle_policy"])

    def test_jaccard_float_sum_contract_remains_non_public_after_generic_route(self) -> None:
        contracts = rt.validate_v1_5_float_sum_reduction_contracts()
        by_row = {(row["app"], row["subpath"]): row for row in contracts}
        contract = by_row[("polygon_set_jaccard", "exact_score_sum")]

        self.assertEqual(contract["status"], "pod_verified_generic_non_public")
        self.assertIn("complete bounded collection", contract["current_oracle_policy"])
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
        self.assertEqual(jaccard["status"], "pod_verified_generic")

    def test_polygon_pair_runtime_exposes_float_sum_summary_contract(self) -> None:
        result = rt.run_generic_polygon_pair_exact_area_summary(
            left=(),
            right=(),
            candidate_pairs=((1, 2), (1, 2), (3, 4)),
            backend="embree",
            exact_summary_fn=_summary,
        )

        self.assertEqual(result["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(result["result_layout"], "summary_float64_sums")
        self.assertEqual(result["summary_contract"]["summary_primitive"], "REDUCE_FLOAT(SUM)")
        self.assertEqual(result["summary_contract"]["result_layout"], "summary_float64_sums")
        self.assertEqual(
            result["summary_contract"]["value_fields"],
            ("total_intersection_area", "total_union_area"),
        )
        self.assertTrue(result["summary_contract"]["integer_parity_required"])
        self.assertFalse(result["summary_contract"]["scalar_helper_direct_use"])
        self.assertIn(result["summary_contract"]["result_layout"], rt.V1_5_POLYGON_FLOAT_SUM_RESULT_LAYOUTS)
        self.assertEqual(result["integer_parity_values"]["total_intersection_area"], 7)
        self.assertEqual(result["candidate_pair_count"], 2)


if __name__ == "__main__":
    unittest.main()
