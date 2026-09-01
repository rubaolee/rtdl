from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5836_build_sui_same_input_preaction as preaction


class Goal5836SuiSameInputPreactionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = preaction.build_authority()

    def _reseal(self, document: dict) -> dict:
        document["preaction_authority_sha256"] = preaction._seal(document)
        return document

    def test_01_authority_is_deterministic_and_self_sealed(self) -> None:
        self.assertEqual(self.document, preaction.build_authority())
        self.assertEqual(
            self.document["preaction_authority_sha256"],
            preaction._seal(self.document),
        )

    def test_02_only_preaction_document_creation_is_authorized(self) -> None:
        authorization = self.document["authorization"]
        self.assertEqual(
            [key for key, value in authorization.items() if value],
            ["preaction_document_creation_authorized"],
        )
        self.assertFalse(any(row["authorized_now"] for row in self.document["stages"]))
        self.assertEqual(
            self.document["next_owner_gate"]["requested_decision"],
            "AUTHORIZE_STAGE_A0_SOURCE_ACQUISITION_AND_HASHING_ONLY",
        )

    def test_03_source_values_are_unobserved_planning_claims(self) -> None:
        planned = self.document["planned_source"]
        self.assertEqual(
            planned["observation_status"],
            "PLANNING_CLAIMS_ONLY__NO_BYTES_ACQUIRED",
        )
        self.assertTrue(planned["paper"]["planning_claim_only"])
        self.assertFalse(planned["paper"]["local_bytes_present"])
        self.assertIsNone(planned["paper"]["sha256"])
        self.assertTrue(planned["author_repository"]["planning_claim_only"])
        self.assertFalse(planned["author_repository"]["git_object_observed"])
        self.assertFalse(planned["author_repository"]["license_bytes_observed"])
        self.assertIsNone(planned["author_repository"]["tree_sha256"])
        self.assertIsNone(planned["author_repository"]["license_sha256"])

    def test_04_stage_order_and_separate_gates_are_exact(self) -> None:
        self.assertEqual(
            [row["stage_id"] for row in self.document["stages"]],
            list(preaction.STAGE_ORDER),
        )
        self.assertTrue(
            all("OWNER" in row["entry_gate"] for row in self.document["stages"])
        )
        self.assertTrue(
            all(row["result_observed_at_preaction_freeze"] is False for row in self.document["stages"])
        )

    def test_05_same_input_route_and_independence_contract_is_frozen(self) -> None:
        contract = self.document["same_input_contract"]
        self.assertEqual(
            contract["required_routes"],
            [
                "AUTHOR_SOURCE_ADAPTER",
                "RTDL_PUBLIC_LIFECYCLE_ADAPTER",
                "STDLIB_ONLY_CPU_ORACLE",
            ],
        )
        self.assertTrue(contract["same_exact_input_for_all_routes"])
        self.assertFalse(contract["author_and_rtdl_workers_receive_expected_output"])
        self.assertFalse(contract["oracle_imports_rtdl_or_author_runtime"])
        self.assertTrue(contract["raw_outputs_sealed_before_evaluation"])
        self.assertFalse(contract["input_replacement_after_output_allowed"])
        self.assertFalse(contract["threshold_or_margin_change_after_output_allowed"])
        self.assertFalse(contract["output_predicate_change_after_output_allowed"])

    def test_06_unconditional_negative_outcomes_are_complete(self) -> None:
        self.assertEqual(
            self.document["unconditional_outcomes"], preaction.TERMINAL_OUTCOMES
        )
        self.assertIn("source_fidelity_material_difference", preaction.TERMINAL_OUTCOMES)
        self.assertIn("functional_mismatch", preaction.TERMINAL_OUTCOMES)
        self.assertIn("author_build_or_run_failure", preaction.TERMINAL_OUTCOMES)
        self.assertIn("infrastructure_invalid", preaction.TERMINAL_OUTCOMES)

    def test_07_identity_paths_are_relative_and_hash_bound(self) -> None:
        rows = self.document["predecessors"] + self.document["implementation_and_tests"]
        for row in rows:
            path = Path(row["path"])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)
            self.assertEqual(len(row["sha256"]), 64)
            self.assertGreater(row["bytes"], 0)

    def test_08_coordinated_reseal_cannot_enable_source_acquisition(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["authorization"]["source_acquisition_authorized"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(preaction.PreactionError, "AUTHORIZATION_MISMATCH"):
            preaction.validate_policy(changed)

    def test_09_coordinated_reseal_cannot_preauthorize_a_stage(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["stages"][0]["authorized_now"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(preaction.PreactionError, "STAGE_PREAUTHORIZED"):
            preaction.validate_policy(changed)

    def test_10_coordinated_reseal_cannot_inject_observed_source_hash(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["planned_source"]["paper"]["sha256"] = "0" * 64
        self._reseal(changed)
        with self.assertRaisesRegex(preaction.PreactionError, "UNAUTHORIZED_PAPER_HASH"):
            preaction.validate_policy(changed)

    def test_11_coordinated_reseal_cannot_enable_input_replacement(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["same_input_contract"]["input_replacement_after_output_allowed"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(preaction.PreactionError, "INPUT_REPLACEMENT_ALLOWED"):
            preaction.validate_policy(changed)

    def test_12_absolute_identity_path_fails_closed(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["predecessors"][0]["path"] = "/tmp/review.md"
        self._reseal(changed)
        with self.assertRaisesRegex(preaction.PreactionError, "ABSOLUTE_IDENTITY_PATH"):
            preaction.validate_policy(changed)

    def test_13_exact_stored_document_verifier_rejects_resealed_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["planned_source"]["paper"]["venue"] = "Convenient Venue"
        self._reseal(changed)
        with tempfile.TemporaryDirectory(prefix="goal5836_preaction_attack_") as temp:
            path = Path(temp) / "authority.json"
            path.write_text(
                json.dumps(changed, indent=2, sort_keys=True) + "\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(
                preaction.PreactionError,
                "STORED_AUTHORITY_EXACT_DOCUMENT_MISMATCH",
            ):
                preaction.verify_stored(path)


if __name__ == "__main__":
    unittest.main()
