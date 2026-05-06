from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1305V15GroupedReductionContractTest(unittest.TestCase):
    def test_grouped_reduction_contracts_validate(self) -> None:
        contracts = rt.validate_v1_5_grouped_reduction_contracts()
        self.assertGreaterEqual(len(contracts), 5)

    def test_grouped_pose_flags_do_not_invent_new_primitive(self) -> None:
        contracts = rt.validate_v1_5_grouped_reduction_contracts()
        by_row = {(row["app"], row["subpath"]): row for row in contracts}
        pose = by_row[("robot_collision_screening", "prepared_pose_flags")]

        self.assertEqual(pose["input_primitive"], "ANY_HIT")
        self.assertEqual(pose["status"], "pod_verified_generic_non_public")
        self.assertEqual(pose["reduction_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(pose["result_layout"], rt.V1_5_GROUPED_THRESHOLD_BOOL_RESULT_LAYOUT)
        self.assertIn("count > 0", pose["dtype_policy"])

    def test_grouped_result_layouts_are_registered(self) -> None:
        contracts = rt.validate_v1_5_grouped_reduction_contracts()
        valid_layouts = set(rt.V1_5_GROUPED_REDUCTION_RESULT_LAYOUTS)
        self.assertIn(rt.V1_5_GROUPED_THRESHOLD_BOOL_RESULT_LAYOUT, valid_layouts)
        self.assertTrue(valid_layouts)
        for contract in contracts:
            with self.subTest(contract=contract["subpath"]):
                self.assertIn(contract["result_layout"], valid_layouts)

    def test_grouped_contracts_block_broad_claims(self) -> None:
        for contract in rt.validate_v1_5_grouped_reduction_contracts():
            with self.subTest(contract=contract["subpath"]):
                self.assertIn("grouped reduction metadata only", contract["claim_boundary"])
                self.assertIn("not a new GROUPED_* primitive", contract["claim_boundary"])
                self.assertIn("not public speedup wording", contract["claim_boundary"])

    def test_db_rows_are_verified_and_split_count_and_sum_primitives(self) -> None:
        contracts = rt.validate_v1_5_grouped_reduction_contracts()
        db_rows = {
            row["subpath"]: row
            for row in contracts
            if row["app"] == "database_analytics"
        }

        self.assertEqual(db_rows["sales_risk_grouped_count"]["status"], "pod_verified_generic_non_public")
        self.assertEqual(db_rows["sales_risk_grouped_count"]["reduction_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(db_rows["sales_risk_grouped_sum"]["status"], "pod_verified_generic_non_public")
        self.assertEqual(db_rows["sales_risk_grouped_sum"]["reduction_primitive"], "REDUCE_INT(SUM)")

    def test_collect_k_stays_experimental_diagnostic_but_verified_non_public(self) -> None:
        contracts = rt.validate_v1_5_grouped_reduction_contracts()
        jaccard = [
            row for row in contracts if row["input_primitive"] == "COLLECT_K_BOUNDED"
        ]
        self.assertEqual(len(jaccard), 1)
        self.assertEqual(jaccard[0]["status"], "pod_verified_generic_non_public")
        self.assertIn("truncation", jaccard[0]["dtype_policy"])

    def test_inventory_no_longer_uses_grouped_as_primitive_name(self) -> None:
        inventory = rt.validate_v1_5_generic_migration_inventory()
        joined = "\n".join(
            f"{row['generic_primitive']} {row['summary_primitive']}" for row in inventory
        )
        self.assertNotIn("GROUPED_ANY_BOOL", joined)
        self.assertNotIn("GROUPED_", joined)


if __name__ == "__main__":
    unittest.main()
