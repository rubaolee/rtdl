from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import goal5789_a2_adversarial_binding_audit_v2 as audit_v2


ROOT = Path(__file__).resolve().parents[1]
V1_MATRIX = (
    ROOT
    / "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_BINDING_ADVERSARIAL_MATRIX.json"
)


class Goal5789A2AdversarialBindingAuditV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v1_before = hashlib.sha256(V1_MATRIX.read_bytes()).hexdigest()
        cls.result = audit_v2.audit()

    @classmethod
    def tearDownClass(cls) -> None:
        assert hashlib.sha256(V1_MATRIX.read_bytes()).hexdigest() == cls.v1_before

    def test_preserves_all_159_case_ids_and_exactly_strengthens_126(self) -> None:
        predecessor = json.loads(V1_MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(self.result["case_count"], 159)
        self.assertEqual(self.result["passed_count"], 159)
        self.assertEqual(self.result["failed_count"], 0)
        self.assertEqual(
            {row["attack_id"] for row in self.result["cases"]},
            {row["attack_id"] for row in predecessor["cases"]},
        )
        exact = [
            row
            for row in self.result["cases"]
            if row["attack_id"].startswith("certificate_only::")
        ]
        self.assertEqual(len(exact), 126)
        self.assertTrue(all(row["reason_set_exact"] is True for row in exact))
        self.assertTrue(
            all(
                row["expected_normalized_reason_set"]
                == row["actual_normalized_reason_set"]
                for row in exact
            )
        )
        self.assertTrue(all("required_reason_fragment" not in row for row in exact))
        self.assertEqual(
            self.result["case_accounting"][
                "certificate_only_generic_substring_oracle_count_in_v2"
            ],
            0,
        )

    def test_mutation_semantics_select_exact_reason_sets(self) -> None:
        mismatch = ["callback_contract_authority_mismatch"]
        self.assertEqual(
            audit_v2._certificate_only_oracle(
                "certificate_only::unit::empty_effects"
            ),
            ("callback_contract_authority_mismatch", mismatch),
        )
        boundary, payload = audit_v2._certificate_only_oracle(
            "certificate_only::unit::resource::payload_u32_slots::bool_alias"
        )
        self.assertEqual(
            boundary,
            "callback_authority_invalid_nonnegative_integer:"
            "callback_contract.payload_u32_slots",
        )
        self.assertEqual(
            payload,
            sorted(
                [
                    boundary,
                    "callback_contract_authority_mismatch",
                    "invalid_callback_budget:payload_u32_slots",
                ]
            ),
        )
        helper_boundary, helper = audit_v2._certificate_only_oracle(
            "certificate_only::unit::resource::helper_call_depth::float_alias"
        )
        self.assertEqual(
            helper,
            sorted([helper_boundary, "callback_contract_authority_mismatch"]),
        )

    def test_exact_reason_distribution_is_hard_coded_54_plus_six_by_12(self) -> None:
        mismatch = "callback_contract_authority_mismatch"
        expected: Counter[tuple[str, ...]] = Counter({(mismatch,): 54})
        for field in sorted(audit_v2.RESOURCE_FIELDS):
            strict = (
                "callback_authority_invalid_nonnegative_integer:"
                f"callback_contract.{field}"
            )
            reasons = [strict, mismatch]
            if field != "helper_call_depth":
                reasons.append(f"invalid_callback_budget:{field}")
            expected[tuple(sorted(reasons))] = 12
        exact_rows = [
            row
            for row in self.result["cases"]
            if row["attack_id"].startswith("certificate_only::")
        ]
        self.assertEqual(
            Counter(tuple(row["expected_normalized_reason_set"]) for row in exact_rows),
            expected,
        )
        self.assertEqual(
            Counter(tuple(row["actual_normalized_reason_set"]) for row in exact_rows),
            expected,
        )

    def test_callback_shaped_but_wrong_reason_cannot_pass(self) -> None:
        source = next(
            row
            for row in self.result["cases"]
            if row["attack_id"].endswith("resource::payload_u32_slots::bool_alias")
        )
        predecessor_shape = {
            key: deepcopy(value)
            for key, value in source.items()
            if key
            not in {
                "expected_boundary_id",
                "expected_normalized_reason_set",
                "actual_normalized_reason_set",
                "reason_normalization",
                "reason_set_exact",
                "predecessor_v1_required_reason_fragment",
                "predecessor_v1_passed",
            }
        }
        predecessor_shape["required_reason_fragment"] = "callback_contract"
        predecessor_shape["passed"] = True
        predecessor_shape["reasons"] = ["callback_contract_authority_mismatch"]
        strengthened = audit_v2._strengthen_certificate_only_row(predecessor_shape)
        self.assertFalse(strengthened["reason_set_exact"])
        self.assertFalse(strengthened["passed"])

    def test_reason_normalization_is_order_and_duplicate_insensitive_only(self) -> None:
        source = next(
            row
            for row in self.result["cases"]
            if row["attack_id"].endswith("resource::trace_depth::float_alias")
        )
        predecessor_shape = {
            key: deepcopy(value)
            for key, value in source.items()
            if key
            not in {
                "expected_boundary_id",
                "expected_normalized_reason_set",
                "actual_normalized_reason_set",
                "reason_normalization",
                "reason_set_exact",
                "predecessor_v1_required_reason_fragment",
                "predecessor_v1_passed",
            }
        }
        predecessor_shape["required_reason_fragment"] = "callback_contract"
        predecessor_shape["passed"] = True
        predecessor_shape["reasons"] = list(reversed(source["reasons"])) + [
            source["reasons"][0]
        ]
        strengthened = audit_v2._strengthen_certificate_only_row(predecessor_shape)
        self.assertTrue(strengthened["reason_set_exact"])
        self.assertTrue(strengthened["passed"])

    def test_v1_lineage_and_no_goal5793_or_pod_authorization(self) -> None:
        lineage = self.result["predecessor_lineage"]
        identities = {row["role"]: row for row in lineage["files"]}
        self.assertEqual(
            identities["hostile_matrix_v1"]["file_sha256"],
            "ec3de9782d5587f944d0872d25cfc8a8703b0963ad2e2109de1455b742c340ea",
        )
        self.assertEqual(
            identities["owner_returned_external_review"]["file_sha256"],
            "88e0aff9fcc0579c4721a8a3422517beff9146acfcef7862f9dd7e880da1bd3a",
        )
        self.assertEqual(
            identities["postreview_absorption_work_authority"]["file_sha256"],
            "96be56ab7f450664fa2d2c27f3df3e9be667eacf9cc45ee0d45725924520e3a0",
        )
        self.assertTrue(lineage["v1_rerun_byte_identical_to_frozen_matrix"])
        self.assertEqual(
            lineage["postreview_work_authority_internal_sha256"],
            "d37051d04ff5b3ed99abd11f7469de5fc79bbbac59301ad6fd7b210946961e25",
        )
        self.assertTrue(all(value is False for value in self.result["authorization"].values()))
        self.assertFalse(self.result["authorization"]["authorizes_goal5793"])
        self.assertFalse(self.result["authorization"]["authorizes_pod"])

    def test_main_is_create_only(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5789_a2_matrix_v2_") as temporary:
            output = Path(temporary) / "matrix_v2.json"
            with mock.patch.object(audit_v2, "OUTPUT", output):
                self.assertEqual(audit_v2.main(), 0)
                emitted = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(emitted["case_count"], 159)
                with self.assertRaisesRegex(RuntimeError, "create-only"):
                    audit_v2.main()


if __name__ == "__main__":
    unittest.main()
