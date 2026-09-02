"""Hostile tests for the Goal5837 owner-grouped classification authority."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5837_freeze_owner_grouped_classification as goal5837


class Goal5837OwnerGroupedClassificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = goal5837.verify_stored()

    @staticmethod
    def _reseal(document: dict) -> dict:
        document["authority_sha256"] = goal5837._seal(document)
        return document

    def test_01_stored_authority_rebuilds_exactly(self) -> None:
        self.assertEqual(self.authority, goal5837.build_authority())
        self.assertEqual(
            self.authority["authority_sha256"],
            goal5837._seal(self.authority),
        )

    def test_02_classification_keeps_heterogeneous_counts_separate(self) -> None:
        classification = self.authority["classification"]
        self.assertEqual(classification["exact_verdict"], goal5837.EXACT_CLASSIFICATION)
        self.assertEqual(
            classification["stable_v4_fixed_constructor_count_before_goal5837"], 2)
        self.assertEqual(
            classification["stable_v4_fixed_constructor_count_after_goal5837"], 2)
        self.assertEqual(classification["root_exported_closed_successor_route_count"], 1)
        self.assertEqual(classification["goal5832_registered_successor_family_shape_count"], 0)
        self.assertEqual(classification["prospective_frozen_core_new_shape_exam_count"], 0)
        self.assertTrue(classification["heterogeneous_count_sum_forbidden"])

    def test_03_stable_surface_and_root_surface_are_distinct(self) -> None:
        surface = self.authority["surface_observation"]
        self.assertEqual(surface["stable_protocol_family_values"], list(goal5837.STABLE_CONSTRUCTORS))
        self.assertEqual(
            surface["compile_protocol_program_admitted_types"],
            ["BoundedRelationProtocol", "TriangleReductionProtocol"],
        )
        self.assertEqual(surface["stable_v4_successor_export_count"], 0)
        self.assertEqual(surface["root_successor_exports"], list(goal5837.SUCCESSOR_EXPORTS))
        self.assertEqual(surface["root_successor_export_count"], 5)
        self.assertEqual(surface["generic_engine_application_vocabulary_matches"], 0)

    def test_04_closed_lifecycle_is_complete(self) -> None:
        lifecycle = self.authority["surface_observation"]["public_lifecycle"]
        self.assertEqual(lifecycle, {
            name: list(methods)
            for name, methods in goal5837.SUCCESSOR_LIFECYCLE.items()
        })

    def test_05_functional_evidence_is_exactly_bounded(self) -> None:
        evidence = self.authority["evidence_summary"]
        local = evidence["local_reference"]
        gpu = evidence["optix8_functional"]
        self.assertEqual(local["matching_local_case_count"], 9)
        self.assertEqual(gpu["matching_gpu_execution_count"], 30)
        self.assertEqual(gpu["true_optix_launch_count"], 30)
        self.assertEqual(gpu["registered_performance_timing_count"], 0)
        self.assertFalse(gpu["performance_claimed"])
        self.assertEqual(evidence["paper_app_result_count"], 0)
        self.assertEqual(evidence["external_review_count"], 0)

    def test_06_claim_matrix_has_exact_denominator_and_sources(self) -> None:
        rows = self.authority["claim_source_matrix"]
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({row["claim_id"] for row in rows}), 12)
        self.assertEqual(
            {source for row in rows for source in row["source_ids"]},
            set(self.authority["source_registry"]),
        )
        by_id = {row["claim_id"]: row for row in rows}
        self.assertTrue(by_id["C04_OPTIX8_FUNCTIONAL_PARITY"]["authorized"])
        for claim_id in (
            "C06_THIRD_STABLE_CONSTRUCTOR",
            "C07_REGISTERED_GOAL5832_SHAPE_INSTANCE",
            "C08_PROSPECTIVE_GENERALIZATION",
            "C09_PERFORMANCE_OR_SPEEDUP",
            "C10_PAPER_APP_OR_FULL_REPRODUCTION",
            "C11_EXTERNAL_CONSENSUS",
            "C12_OPTIX9_FUNCTIONAL_COVERAGE",
        ):
            self.assertFalse(by_id[claim_id]["authorized"], claim_id)

    def test_07_coordinated_reseal_cannot_create_third_constructor(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["classification"]["stable_v4_fixed_constructor_count_after_goal5837"] = 3
        changed["claim_boundary"]["third_stable_v4_fixed_constructor"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(goal5837.Goal5837Error, "CLASSIFICATION_POLICY_MISMATCH"):
            goal5837.validate_policy(changed)

    def test_08_coordinated_reseal_cannot_relabel_prospective_success(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["classification"]["prospective_frozen_core_new_shape_exam_count"] = 1
        changed["claim_boundary"]["prospective_generalization_success"] = True
        self._reseal(changed)
        with self.assertRaisesRegex(goal5837.Goal5837Error, "CLASSIFICATION_POLICY_MISMATCH"):
            goal5837.validate_policy(changed)

    def test_09_coordinated_reseal_cannot_promote_claims(self) -> None:
        mutations = (
            ("performance_result_count", "PERFORMANCE_RESULT_PROMOTION"),
            ("paper_app_result_count", "PAPER_APP_PROMOTION"),
            ("external_review_count", "EXTERNAL_REVIEW_PROMOTION"),
        )
        for field, error in mutations:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.authority)
                changed["evidence_summary"][field] = 1
                self._reseal(changed)
                with self.assertRaisesRegex(goal5837.Goal5837Error, error):
                    goal5837.validate_policy(changed)

    def test_10_source_identity_mutation_is_rejected_even_when_resealed(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["source_inventory"]["generic_behavior"][0]["sha256"] = "0" * 64
        self._reseal(changed)
        with self.assertRaisesRegex(goal5837.Goal5837Error, "AUTHORITY_CURRENT_INPUT_MISMATCH"):
            goal5837.validate_authority(changed)

    def test_11_gpu_count_mutation_is_rejected_even_when_resealed(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["evidence_summary"]["optix8_functional"]["true_optix_launch_count"] = 31
        self._reseal(changed)
        with self.assertRaisesRegex(goal5837.Goal5837Error, "AUTHORITY_CURRENT_INPUT_MISMATCH"):
            goal5837.validate_authority(changed)

    def test_12_unsealed_mutation_is_rejected(self) -> None:
        changed = copy.deepcopy(self.authority)
        changed["status"] = "promoted"
        with self.assertRaisesRegex(goal5837.Goal5837Error, "AUTHORITY_SEAL_MISMATCH"):
            goal5837.validate_authority(changed)

    def test_13_frozen_goal5835_goal5836_identities_are_exact(self) -> None:
        rows = self.authority["historical_inputs"]
        for label in (
            "goal5835_result",
            "goal5836_a1_authority",
            "goal5835_goal5836_strict_audit",
        ):
            self.assertEqual(
                rows[label]["sha256"],
                goal5837.HISTORICAL_INPUTS[label]["sha256"],
            )

    def test_14_optix9_unavailability_sources_are_hash_bound(self) -> None:
        rows = self.authority["historical_inputs"]
        for label in ("optix9_failure_log", "optix9_failure_exit_code"):
            self.assertEqual(
                rows[label]["sha256"],
                goal5837.HISTORICAL_INPUTS[label]["sha256"],
            )

    def test_15_final_bundle_and_manifest_are_verified(self) -> None:
        bundle = self.authority["bundle_verification"]
        self.assertEqual(bundle["checksum_entry_count"], 6)
        self.assertTrue(bundle["all_checksum_targets_match"])
        self.assertTrue(bundle["bundle_paths_safe_and_unique"])
        self.assertGreater(bundle["bundle_member_count"], 6)

    def test_16_preexisting_goal5832_custody_debt_is_not_hidden(self) -> None:
        context = self.authority["historical_validator_context"]
        self.assertEqual(
            context["status"],
            "PREEXISTING_HISTORICAL_CUSTODY_CHECK_NOT_COMPOSITIONAL_WITH_LATER_ROOT_EXPORTS",
        )
        self.assertTrue(context["identities_differ"])
        self.assertFalse(context["goal5832_full_current_repository_validation_claimed"])
        self.assertFalse(context["historical_manifest_rewritten"])

    def test_17_duplicate_json_keys_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text('{"a":1,"a":2}\n', encoding="ascii")
            with self.assertRaisesRegex(goal5837.Goal5837Error, "DUPLICATE_JSON_KEY"):
                goal5837.load_json_exact(path)

    def test_18_authority_writes_and_verifies_at_another_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "authority.json"
            written = goal5837.write_authority(path)
            loaded = goal5837.load_json_exact(path)
            self.assertEqual(written, loaded)
            goal5837.validate_authority(loaded)


if __name__ == "__main__":
    unittest.main()
