from __future__ import annotations

import copy
import json
import unittest

from scripts import goal5799_build_local_completion as goal


class Goal5799LocalCompletionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        goal.verify_pinned_inputs()
        cls.absorption = goal.build_absorption()
        cls.ledger = goal.build_phase_ledger()
        cls.contract = goal.build_contract()

    def test_01_review_and_locked_authority_absorbed(self) -> None:
        self.assertEqual(self.absorption["verdict"], {"P0": 0, "P1": 4, "P2": 4, "P3": 2, "label": "APPROVE_WITH_CONDITIONS"})
        authorization = self.absorption["authorization"]
        self.assertTrue(authorization["goal5800_local_untimed_implementation_after_this_freeze"])
        self.assertTrue(authorization["goal5801_local_untimed_implementation_after_this_freeze"])
        for key in ("goal5802_formal_measurement", "goal5803_external_evidence", "network_provider_query", "ssh_pod_gpu", "submission_claim"):
            self.assertFalse(authorization[key])

    def test_02_exact_200_work_exposure_and_19_leaf_evidence(self) -> None:
        p1 = self.absorption["p1_absorption"]["P1_3_200_observed_works_unregistered"]
        self.assertEqual(p1["observed_rows"], 200)
        self.assertEqual(p1["selection_eligible_rows"], 0)
        self.assertEqual(
            self.absorption["goal5797_a1"]["local_status"],
            "19_OF_19_POPULATED_LEAVES_DECISION_BEARING__EXTERNAL_REVIEW_PENDING",
        )

    def test_03_144_cold_receipts_are_exhaustively_named_without_new_timing(self) -> None:
        self.assertEqual(self.ledger["counts"]["cold_receipts"], 144)
        self.assertEqual(self.ledger["counts"]["cells"], 6)
        self.assertEqual(self.ledger["counts"]["samples_per_cell"], [24])
        self.assertEqual(self.ledger["counts"]["negative_residual_rows"], 0)
        self.assertEqual(self.ledger["counts"]["named_accounting_fraction_below_one_rows"], 0)
        self.assertEqual(self.ledger["scope"]["new_registered_timing_count"], 0)
        for row in self.ledger["rows"]:
            self.assertEqual(sum(row["phases_ns"].values()), row["wall_ns"])
            self.assertEqual(row["named_accounting_fraction"], 1.0)

    def test_04_old_ledger_does_not_fake_direct_95_percent_attribution(self) -> None:
        self.assertGreater(self.ledger["counts"]["directly_metered_fraction_below_0_95_rows"], 0)
        self.assertFalse(self.ledger["claim_boundary"]["all_wall_time_directly_metered"])
        self.assertFalse(self.ledger["claim_boundary"]["envelope_residual_is_safety_or_checker_tax"])

    def test_05_contract_accepts_only_three_falsifiable_comparative_gates(self) -> None:
        gates = self.contract["comparative_gates"]
        self.assertTrue(gates["STEADY_E2E"]["enabled"])
        self.assertTrue(gates["PREPARE"]["enabled"])
        self.assertTrue(gates["DEPLOYMENT_COLD"]["enabled"])
        self.assertFalse(gates["ON_BYPASS"]["enabled"])
        self.assertFalse(gates["GPU_KERNEL"]["enabled"])
        self.assertFalse(gates["BUILD_COLD"]["enabled"])

    def test_06_tautology_asymmetry_and_claim_expansion_attacks_reject(self) -> None:
        attacks = []
        on = copy.deepcopy(self.contract)
        on["comparative_gates"]["ON_BYPASS"]["enabled"] = True
        attacks.append(on)
        kernel = copy.deepcopy(self.contract)
        kernel["comparative_gates"]["GPU_KERNEL"]["enabled"] = True
        attacks.append(kernel)
        direct = copy.deepcopy(self.contract)
        direct["baselines"]["DIRECT_CUDA_OPTIX"]["first_class_publication_row"] = False
        attacks.append(direct)
        loops = copy.deepcopy(self.contract)
        loops["baselines"]["PYOPTIX"]["idiomatic_requirements"] = ["public API"]
        attacks.append(loops)
        speedup = copy.deepcopy(self.contract)
        speedup["claim_ceiling"]["rtdl_speedup_over_same_backend"] = "SCIENTIFIC_WIN"
        attacks.append(speedup)
        authorization = copy.deepcopy(self.contract)
        authorization["authorization"]["goal5802_formal_worker_zero"] = True
        attacks.append(authorization)
        for attack in attacks:
            with self.assertRaises(goal.Goal5799Error):
                goal.validate_contract(attack)

    def test_07_five_rtdlexe_attacks_and_two_anonymity_gates_frozen(self) -> None:
        self.assertEqual(len(self.contract["mandatory_rtdlexe_attacks"]), 5)
        anonymity = self.contract["anonymity"]
        self.assertFalse(anonymity["one_gate_may_substitute_for_the_other"])
        self.assertIn("artifact_evidence_gate", anonymity)
        self.assertIn("manuscript_gate", anonymity)

    def test_08_stored_outputs_if_present_are_byte_exact_and_one_cfr(self) -> None:
        if not goal.CFR.exists():
            self.skipTest("create-only outputs have not been written")
        result = goal.verify_stored()
        self.assertEqual(result["status"], "POSTWRITE_VERIFY_PASS")
        cfr = goal.CFR.read_text(encoding="utf-8", errors="strict")
        self.assertTrue(cfr.startswith("# SEND ONLY THIS FILE"))
        self.assertIn(goal.PINNED_INPUTS[goal.X3_JOURNAL][1], cfr)
        self.assertIn(goal.PINNED_INPUTS[goal.A1_CFR][1], cfr)
        self.assertIn("Goal5802 formal workers", cfr)


if __name__ == "__main__":
    unittest.main()
