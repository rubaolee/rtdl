from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import goal5799_a2_final_authority_and_matcher as a2


class Goal5799A2FinalAuthorityAndMatcherTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract_payload = a2._verify_local_pin(a2.A1_CONTRACT, "contract")
        cls.contract = json.loads(cls.contract_payload)
        cls.registry_payload = a2._verify_local_pin(a2.A1_REGISTRY, "registry")
        cls.registry = json.loads(cls.registry_payload)
        cls.bridge_payload = a2._verify_local_pin(a2.A1_BRIDGE, "bridge")
        cls.ledger_payload = a2._verify_local_pin(a2.V1_LEDGER, "ledger")

    def test_01_authorized_contract_passes_and_names_coverage_correctly(self) -> None:
        result = a2.verify_contract_payload(self.contract_payload, a2.AUTHORIZED["contract"][1])
        self.assertEqual(result["identity_bound_leaf_count"], 170)
        self.assertEqual(result["declared_identity_exemption_count"], 0)
        self.assertFalse(result["independent_liveness_claim_for_all_170_leaves"])

    def test_02_all_170_changed_expected_attacks_reject(self) -> None:
        matrix = a2.run_changed_expected_attack_matrix(self.contract_payload)
        self.assertEqual(matrix["attack_count"], 170)
        self.assertEqual(matrix["rejected_count"], 170)
        self.assertEqual(matrix["accepted_count"], 0)

    def test_03_exact_subagent_counterexample_reproduces_and_rejects(self) -> None:
        forged = copy.deepcopy(self.contract)
        forged["publication"]["v11_withdrawal_sentence"] = ""
        payload = a2._rebuild_contract_authorities(forged)
        self.assertEqual(len(payload), 48_998)
        self.assertEqual(a2.sha(payload), "eee7d44667d05345c0e15d5673902a176e6c32c1e4d5f4425099ffe0ad0f9678")
        with self.assertRaisesRegex(a2.A2Error, "CONTRACT_EXPECTED_IDENTITY_NOT_AUTHORIZED"):
            a2.verify_contract_payload(payload, a2.sha(payload))

    def test_04_four_related_changed_authority_attacks_reject(self) -> None:
        paths = [
            (("baselines", "OWL", "minimum_residual_mechanisms_required"), 0),
            (("structural_cache_hit_assertions", "cache_hit_imports_numba"), True),
            (("anonymity", "artifact_evidence_gate", "owner"), "ATTACKER"),
            (("goal5802_not_yet_frozen__all_block_formal_worker_zero", 0), "ARBITRARY"),
        ]
        for path, value in paths:
            forged = copy.deepcopy(self.contract)
            a2._set_path(forged, path, value)
            payload = a2._rebuild_contract_authorities(forged)
            with self.assertRaisesRegex(a2.A2Error, "CONTRACT_EXPECTED_IDENTITY_NOT_AUTHORIZED"):
                a2.verify_contract_payload(payload, a2.sha(payload))

    def test_05_original_expected_sha_also_rejects_any_mutated_payload(self) -> None:
        forged = copy.deepcopy(self.contract)
        forged["publication"]["v11_withdrawal_sentence"] = ""
        payload = a2._rebuild_contract_authorities(forged)
        with self.assertRaisesRegex(a2.A2Error, "CONTRACT_ACTUAL_IDENTITY_MISMATCH"):
            a2.verify_contract_payload(payload, a2.AUTHORIZED["contract"][1])

    def test_06_registry_and_matcher_cover_all_200_rows(self) -> None:
        verified = a2.verify_registry_payload(self.registry_payload, a2.AUTHORIZED["registry"][1])
        self.assertEqual(verified["provider_records"], 200)
        self.assertEqual(verified["unique_openalex_ids"], 200)
        self.assertEqual(verified["selection_eligible_records"], 0)
        for row in self.registry["rows"]:
            match = a2.match_exposure({"openalex": [row["openalex"]]}, self.registry)
            self.assertTrue(match["exposed"])
            self.assertFalse(match["selection_eligible"])

    def test_07_matcher_normalizes_doi_arxiv_openalex_and_fallback(self) -> None:
        self.assertTrue(
            a2.match_exposure(
                {"doi": ["https://doi.org/10.1051/0004-6361/201936150/pdf"]}, self.registry
            )["exposed"]
        )
        first = self.registry["rows"][0]
        fallback = next(alias["value"] for alias in first["matching_aliases"] if alias["kind"] == "fallback_sha256")
        self.assertTrue(a2.match_exposure({"fallback_sha256": [fallback]}, self.registry)["exposed"])
        self.assertFalse(a2.match_exposure({"openalex": ["W999999999999999999"]}, self.registry)["exposed"])
        with self.assertRaises(a2.A2Error):
            a2.match_exposure({"doi": ["not-a-doi"]}, self.registry)

    def test_08_bridge_rebuilds_144_rows_without_archive_or_helper(self) -> None:
        verified = a2.verify_bridge_payload(
            self.bridge_payload,
            a2.AUTHORIZED["bridge"][1],
            self.ledger_payload,
        )
        self.assertEqual(verified["raw_receipts"], 144)
        self.assertEqual(verified["cells"], 6)
        self.assertEqual(verified["coverage_below_0_95"], 144)
        self.assertEqual(verified["new_timing_samples"], 0)

    def test_09_changed_expected_registry_and_bridge_authorities_reject(self) -> None:
        with self.assertRaisesRegex(a2.A2Error, "REGISTRY_EXPECTED_IDENTITY_NOT_AUTHORIZED"):
            a2.verify_registry_payload(self.registry_payload, "0" * 64)
        with self.assertRaisesRegex(a2.A2Error, "BRIDGE_EXPECTED_IDENTITY_NOT_AUTHORIZED"):
            a2.verify_bridge_payload(self.bridge_payload, "0" * 64, self.ledger_payload)

    def test_10_result_keeps_every_formal_external_lock_false(self) -> None:
        result = a2.build_result()
        for key in (
            "goal5802_formal_worker_zero",
            "goal5802_gpu_pod_timing",
            "goal5803",
            "network",
            "participant",
            "submission_or_public_claim",
        ):
            self.assertFalse(result["authorization"][key])

    def test_11_sole_cfr_if_present_is_self_contained(self) -> None:
        if not a2.CFR.exists():
            self.skipTest("A2 CFR not written")
        verified = a2.verify_sole_cfr_payload(a2.CFR.read_bytes())
        self.assertTrue(verified["standard_library_only"])
        self.assertFalse(verified["requires_repository_files"])
        self.assertFalse(verified["requires_shared_canonical_helper"])
        self.assertEqual(verified["bridge"]["raw_receipts"], 144)

    def test_12_stored_outputs_if_present_are_exact(self) -> None:
        if not a2.CFR.exists():
            self.skipTest("A2 outputs not written")
        self.assertEqual(a2.verify_stored()["status"], "POSTWRITE_VERIFY_PASS")


if __name__ == "__main__":
    unittest.main()
