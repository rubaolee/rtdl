from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import goal5793_x1_readiness_gate as gate
from scripts import goal5793_x1_validate_owner_exposure_disclosure as disclosure
from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


class X1ReadinessGateTest(unittest.TestCase):
    def test_current_fixed_roots_rehash_and_internal_seals_rederive(self) -> None:
        rows = gate._verify_fixed_roots()
        self.assertEqual(set(rows), set(gate.FIXED_ROOTS))

    def test_current_state_is_ready_for_review_with_conservative_boundary(self) -> None:
        result = gate.readiness()
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["status"], "READY_FOR_SINGLE_FILE_X1_EXTERNAL_REVIEW_WITH_NO_MEMORY_ATTESTATION")
        self.assertTrue(result["mechanism_and_historical_evidence_ready"])
        self.assertFalse(result["x2_authorized"])
        self.assertFalse(result["owner_memory_attestation_used_as_eligibility_evidence"])

    def test_valid_external_inputs_only_unlock_review_not_x2(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_ready_") as td:
            root = Path(td)
            disclosure_path = root / "disclosure.json"
            disclosure_path.write_bytes(canonical_json_bytes(disclosure.build_none_template()) + b"\n")
            exact_env = {
                "schema": "rtdl.goal5793.x1.exact_environment_capture.v2",
                "status": "EXACT_TARGET_EXECUTION_ENVIRONMENT_CAPTURED__REVIEW_REQUIRED__NO_EXECUTION_AUTHORIZATION",
                "scope": {
                    "network_calls": 0,
                    "gpu_calls": 0,
                    "candidate_work": 0,
                    "registered_timing": 0,
                    "native_build_performed_by_collector": False,
                    "execution_authorized": False,
                    "search_entropy_selection_authorized": False,
                    "publication_authorized": False,
                },
                "claim_boundary": {
                    "exact_target_execution_environment_frozen": True,
                    "generality_exam_count": 0,
                    "usability_evidence_count": 0,
                },
                "authority_sha256": "",
            }
            exact_env["authority_sha256"] = seal_document(
                exact_env,
                seal_field="authority_sha256",
                domain="rtdl.goal5793.x1.exact_environment_capture",
                version=2,
            )
            env_path = root / "env.json"
            env_path.write_bytes(canonical_json_bytes(exact_env) + b"\n")
            with patch.object(gate, "DISCLOSURE_PATH", disclosure_path), patch.object(
                gate, "EXACT_ENV_PATH", env_path
            ), patch.object(gate, "ROOT", root), patch.object(
                gate, "_verify_fixed_roots", return_value={}
            ), patch.object(
                gate, "_verify_environment_capsule", return_value={
                    "status": "INDEPENDENT_EXACT_ENVIRONMENT_CAPSULE_VERIFICATION_PASS",
                    "archive": {"bytes": 1, "sha256": "0" * 64},
                    "manifest": {"bytes": 1, "sha256": "1" * 64},
                    "audit": {"bytes": 1, "sha256": "2" * 64},
                    "payload_count": 1, "payload_bytes": 1, "payload_set_sha256": "3" * 64,
                }
            ), patch.object(
                gate, "DISCLOSURE_VALIDATOR_SHA256", gate._sha256(gate.DISCLOSURE_VALIDATOR_PATH)
            ):
                result = gate.readiness()
        self.assertEqual(result["status"], "READY_FOR_SINGLE_FILE_X1_EXTERNAL_REVIEW")
        self.assertEqual(result["blockers"], [])
        self.assertFalse(result["x1_complete"])
        self.assertFalse(result["x2_authorized"])

    def test_resealed_environment_execution_escalation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_env_escalation_") as td:
            root = Path(td)
            disclosure_path = root / "disclosure.json"
            disclosure_path.write_bytes(canonical_json_bytes(disclosure.build_none_template()) + b"\n")
            exact_env = {
                "schema": "rtdl.goal5793.x1.exact_environment_capture.v2",
                "status": "EXACT_TARGET_EXECUTION_ENVIRONMENT_CAPTURED__REVIEW_REQUIRED__NO_EXECUTION_AUTHORIZATION",
                "scope": {
                    "network_calls": 0,
                    "gpu_calls": 0,
                    "candidate_work": 0,
                    "registered_timing": 0,
                    "native_build_performed_by_collector": False,
                    "execution_authorized": True,
                    "search_entropy_selection_authorized": False,
                    "publication_authorized": False,
                },
                "claim_boundary": {
                    "exact_target_execution_environment_frozen": True,
                    "generality_exam_count": 0,
                    "usability_evidence_count": 0,
                },
                "authority_sha256": "",
            }
            exact_env["authority_sha256"] = seal_document(
                exact_env,
                seal_field="authority_sha256",
                domain="rtdl.goal5793.x1.exact_environment_capture",
                version=2,
            )
            env_path = root / "env.json"
            env_path.write_bytes(canonical_json_bytes(exact_env) + b"\n")
            with patch.object(gate, "DISCLOSURE_PATH", disclosure_path), patch.object(
                gate, "EXACT_ENV_PATH", env_path
            ), patch.object(gate, "ROOT", root), patch.object(
                gate, "_verify_fixed_roots", return_value={}
            ), patch.object(
                gate, "_verify_environment_capsule", return_value={
                    "status": "INDEPENDENT_EXACT_ENVIRONMENT_CAPSULE_VERIFICATION_PASS",
                    "archive": {"bytes": 1, "sha256": "0" * 64},
                    "manifest": {"bytes": 1, "sha256": "1" * 64},
                    "audit": {"bytes": 1, "sha256": "2" * 64},
                    "payload_count": 1, "payload_bytes": 1, "payload_set_sha256": "3" * 64,
                }
            ), patch.object(
                gate, "DISCLOSURE_VALIDATOR_SHA256", gate._sha256(gate.DISCLOSURE_VALIDATOR_PATH)
            ):
                with self.assertRaisesRegex(gate.ReadinessError, "execution_escalation"):
                    gate.readiness()


if __name__ == "__main__":
    unittest.main()
