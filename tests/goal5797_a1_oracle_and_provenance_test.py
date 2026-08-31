"""Tests for Goal5797's post-review oracle/provenance correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "history/internal_docs" / (
    "goal5797_a1_oracle_counterfactual_and_source_provenance_result_"
    "20260823.json")
VERIFY = ROOT / "history/internal_docs" / (
    "goal5797_a1_oracle_counterfactual_and_source_provenance_independent_"
    "verification_20260823.json")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal5797A1OracleAndProvenanceTest(unittest.TestCase):
    def test_result_seal_and_exhaustive_leaf_closure(self) -> None:
        result = load(RESULT)
        expected = result.pop("result_sha256")
        self.assertEqual(hashlib.sha256(canonical(result)).hexdigest(), expected)
        leaf = result["p1_closure"]["P1_1_every_populated_contract_leaf"]
        self.assertEqual(leaf["populated_leaf_count"], 19)
        self.assertEqual(leaf["decision_bearing_count"], 19)
        self.assertEqual(
            leaf["require_status_ok_leaf"]["verdict_delta"], "ACCEPT_TO_REJECT")

    def test_oracle_platform_and_gate_counts_are_explicit(self) -> None:
        result = load(RESULT)
        counterfactual = result["p1_closure"]["P1_2_oracle_counterfactual"]
        self.assertEqual(
            counterfactual["developer_oracle_detection_count_on_registered_inputs"], 5)
        self.assertEqual(counterfactual["platform_automatic_check_detection_count"], 0)
        self.assertEqual(counterfactual["rtdl_prelaunch_gate_rejection_count"], 5)
        self.assertTrue(all(row["oracle_detects"] for row in counterfactual["rows"]))
        self.assertTrue(all(
            row["optix_validation"] == "PASS" for row in counterfactual["rows"]))

    def test_source_origin_and_claim_ceiling_are_not_ambiguous(self) -> None:
        result = load(RESULT)
        provenance = result["device_source_provenance"]
        self.assertTrue(provenance["classification"].endswith("NOT_RTDL_GENERATED"))
        self.assertIs(provenance["goal5797_valid_a_device_sha256_matches_base"], True)
        claims = result["claims"]
        self.assertEqual(claims["new_application_generalization_exam_count"], 0)
        self.assertEqual(claims["registered_performance_timing_count"], 0)
        self.assertIs(claims["goal5798_timing_authorized"], False)
        self.assertEqual(load(VERIFY)["status"], "PASS")
