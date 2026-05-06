import unittest

import rtdsl as rt


class V15InternalReadinessGateTest(unittest.TestCase):
    def test_gate_validates_expected_contract_counts(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertEqual(gate["status"], "internal_v1_5_contract_gate_passing_non_public")
        self.assertEqual(gate["inventory_rows"], 14)
        self.assertEqual(gate["grouped_contracts"], 5)
        self.assertEqual(gate["db_contracts"], 3)
        self.assertEqual(gate["float_sum_contracts"], 2)
        self.assertEqual(gate["bounded_collection_contracts"], 1)

    def test_gate_keeps_public_release_and_speedup_blocked(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertFalse(gate["public_release_authorized"])
        self.assertFalse(gate["public_speedup_wording_authorized"])
        self.assertFalse(gate["release_tag_action_authorized"])
        self.assertEqual(gate["requires_external_consensus_for_public_claims"], "3-AI")

        boundary = gate["claim_boundary"]
        self.assertIn("not public v1.5 release wording", boundary)
        self.assertIn("not public speedup wording", boundary)
        self.assertIn("v1.0 tag remains unchanged", boundary)

    def test_gate_represents_all_hardened_validators(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertEqual(
            set(gate["validators"]),
            {
                "validate_v1_5_generic_migration_inventory",
                "validate_v1_5_grouped_reduction_contracts",
                "validate_v1_5_db_compact_summary_contracts",
                "validate_v1_5_float_sum_reduction_contracts",
                "validate_v1_5_collect_k_bounded_contracts",
            },
        )
        self.assertIn("COLLECT_K_BOUNDED", gate["experimental_primitives"])

    def test_gate_exposes_remaining_blockers_and_consensus_requirement(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertGreater(len(gate["blockers"]), 0)
        self.assertTrue(any("3-AI" in blocker for blocker in gate["blockers"]))
        self.assertTrue(any("whole-app speedup wording" in blocker for blocker in gate["blockers"]))


if __name__ == "__main__":
    unittest.main()
