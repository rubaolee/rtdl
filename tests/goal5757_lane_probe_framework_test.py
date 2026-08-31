from __future__ import annotations

import copy
import unittest

from scripts.goal5757_lane_probe_framework import (
    LaneClassification,
    LaneProbeContractError,
    PROBE_SCHEMA,
    validate_lane_probe,
)


DIGEST = "a" * 64


def base() -> dict[str, object]:
    return {
        "schema": PROBE_SCHEMA,
        "app_id": "neutral_consumer",
        "lane_id": "semantic.lane.v1",
        "qualification": "AUTHORIZED_PAPER_APP",
        "classification": "SUPPORTED_NOW",
        "contract_freeze_sha256": DIGEST,
        "callback_source_sha256": DIGEST,
        "callback_ir_sha256": DIGEST,
        "cpu_oracle_sha256": DIGEST,
        "cpu_differential_case_count": 4,
        "cpu_differential_mismatch_count": 0,
        "typed_schema_sha256": DIGEST,
        "canonical_plan_sha256": DIGEST,
        "canonical_plan_count": 1,
        "partner_preflight_sha256": DIGEST,
        "target_compile_preflight_sha256": DIGEST,
        "forbidden_identity_dispatch_hits": 0,
        "fail_closed_stage": None,
        "fail_closed_code": None,
        "minimal_counterexample_sha256": None,
        "required_missing_contract": None,
        "paper_semantic_evidence_sha256": None,
        "existing_composition_insufficient_reason": None,
        "cross_app_reuse_candidates": [],
    }


class Goal5757LaneProbeFrameworkTest(unittest.TestCase):
    def test_supported_requires_complete_executable_chain(self):
        self.assertEqual(validate_lane_probe(base()), LaneClassification.SUPPORTED_NOW)
        for field in (
            "callback_source_sha256", "callback_ir_sha256", "cpu_oracle_sha256",
            "typed_schema_sha256", "canonical_plan_sha256", "partner_preflight_sha256",
            "target_compile_preflight_sha256",
        ):
            attacked = base(); attacked[field] = None
            with self.assertRaisesRegex(LaneProbeContractError, "supported_evidence"):
                validate_lane_probe(attacked)

    def test_partner_gap_requires_semantics_complete_and_partner_failure(self):
        payload = base()
        payload.update({
            "classification": "PARTNER_ONLY_GAP",
            "partner_preflight_sha256": None,
            "target_compile_preflight_sha256": None,
            "fail_closed_stage": "partner_boundary",
            "fail_closed_code": "missing_stream_ownership_contract",
            "minimal_counterexample_sha256": DIGEST,
            "required_missing_contract": "cross-library stream and lifetime ownership",
            "paper_semantic_evidence_sha256": DIGEST,
            "existing_composition_insufficient_reason": "current partner accepts only one owner",
            "cross_app_reuse_candidates": ["other_consumer"],
        })
        self.assertEqual(validate_lane_probe(payload), LaneClassification.PARTNER_ONLY_GAP)
        attacked = copy.deepcopy(payload); attacked["typed_schema_sha256"] = None
        with self.assertRaisesRegex(LaneProbeContractError, "partner_gap_semantic_evidence"):
            validate_lane_probe(attacked)

    def test_missing_semantic_requires_minimal_counterexample_and_stable_code(self):
        payload = base()
        payload.update({
            "classification": "MISSING_GENERIC_SEMANTIC",
            "callback_ir_sha256": None,
            "typed_schema_sha256": None,
            "canonical_plan_sha256": None,
            "canonical_plan_count": 0,
            "partner_preflight_sha256": None,
            "target_compile_preflight_sha256": None,
            "fail_closed_stage": "verifier",
            "fail_closed_code": "global_atomic_effect_not_in_closed_set",
            "minimal_counterexample_sha256": DIGEST,
            "required_missing_contract": "checked commutative U64 accumulation effect",
            "paper_semantic_evidence_sha256": DIGEST,
            "existing_composition_insufficient_reason": "payload is per ray and cannot join launches",
            "cross_app_reuse_candidates": ["second_consumer"],
        })
        self.assertEqual(validate_lane_probe(payload), LaneClassification.MISSING_GENERIC_SEMANTIC)
        attacked = copy.deepcopy(payload); attacked["fail_closed_code"] = ""
        with self.assertRaisesRegex(LaneProbeContractError, "nonempty_string"):
            validate_lane_probe(attacked)

    def test_unknown_override_and_app_dispatch_fail_closed(self):
        for classification in ("UNKNOWN", "MANUAL_OVERRIDE", "APP_PATCH"):
            attacked = base(); attacked["classification"] = classification
            with self.assertRaisesRegex(LaneProbeContractError, "classification"):
                validate_lane_probe(attacked)
        attacked = base(); attacked["forbidden_identity_dispatch_hits"] = 1
        with self.assertRaisesRegex(LaneProbeContractError, "identity_dispatch"):
            validate_lane_probe(attacked)

    def test_closed_shape_rejects_result_gaming_metadata(self):
        attacked = base(); attacked["paper_name_override"] = "easy_app"
        with self.assertRaisesRegex(LaneProbeContractError, "closed_shape"):
            validate_lane_probe(attacked)


if __name__ == "__main__":
    unittest.main()
