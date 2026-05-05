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
        self.assertEqual(pose["reduction_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(pose["result_layout"], "grouped_threshold_bool")
        self.assertIn("count > 0", pose["dtype_policy"])

    def test_deferred_db_rows_split_count_and_sum_primitives(self) -> None:
        contracts = rt.validate_v1_5_grouped_reduction_contracts()
        db_rows = {
            row["subpath"]: row["reduction_primitive"]
            for row in contracts
            if row["app"] == "database_analytics"
        }

        self.assertEqual(db_rows["sales_risk_grouped_count"], "REDUCE_INT(COUNT)")
        self.assertEqual(db_rows["sales_risk_grouped_sum"], "REDUCE_INT(SUM)")

    def test_experimental_collect_k_stays_blocked(self) -> None:
        contracts = rt.validate_v1_5_grouped_reduction_contracts()
        jaccard = [
            row for row in contracts if row["input_primitive"] == "COLLECT_K_BOUNDED"
        ]
        self.assertEqual(len(jaccard), 1)
        self.assertEqual(jaccard[0]["status"], "experimental_blocked")
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
