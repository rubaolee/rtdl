from __future__ import annotations

import unittest

import rtdsl
from rtdsl.active_query_status import (
    ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT,
    ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_ROW_SCHEMA,
    ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_TELEMETRY_SCHEMA,
    native_payload_transition_trace_stream_contract,
    validate_native_payload_transition_trace_stream_contract,
)


class Goal5413NativePayloadTransitionTraceContractTest(unittest.TestCase):
    def test_contract_is_design_only_and_app_neutral(self) -> None:
        contract = native_payload_transition_trace_stream_contract()
        self.assertEqual(ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT, contract["contract"])
        self.assertFalse(contract["executable"])
        self.assertTrue(contract["app_generic"])
        self.assertFalse(contract["native_engine_app_specific"])
        self.assertFalse(contract["external_option_support_claimed"])
        self.assertFalse(contract["rt_core_speedup_claim_authorized"])
        self.assertFalse(contract["whole_app_speedup_claim_authorized"])

        lowered = str(contract).lower()
        for token in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
            self.assertNotIn(token, lowered)

    def test_contract_schema_contains_payload_transition_fields(self) -> None:
        contract = native_payload_transition_trace_stream_contract()
        self.assertEqual(ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_ROW_SCHEMA, contract["row_schema"])
        self.assertEqual(
            ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_TELEMETRY_SCHEMA,
            contract["telemetry_schema"],
        )
        for field in (
            "primitive_or_cell_id",
            "cell_namespace_code",
            "status_code",
            "transition_phase_code",
            "current_best_before_sq",
            "current_best_after_sq",
            "payload_event_ordinal",
        ):
            self.assertIn(field, contract["row_schema"])

    def test_contract_requires_evidence_ladder_before_external_claims(self) -> None:
        contract = native_payload_transition_trace_stream_contract()
        self.assertIn("synthetic_non_app_payload_transition_trace_behavior", contract["success_gates"])
        self.assertIn("bounded_external_oracle_sample_row_recovery", contract["success_gates"])
        self.assertIn("full_external_oracle_row_count_hash_status_feedback", contract["success_gates"])
        self.assertIn("overflow_returns_no_partial_success_claim", contract["required_fail_closed_rules"])
        self.assertIn("hard_coded_oracle_sample_rows", contract["forbidden_backend_behavior"])

    def test_validator_accepts_default_contract_and_rejects_claim_drift(self) -> None:
        accepted = validate_native_payload_transition_trace_stream_contract()
        self.assertEqual("accept", accepted["status"])

        executable = native_payload_transition_trace_stream_contract()
        executable["executable"] = True
        rejected = validate_native_payload_transition_trace_stream_contract(executable)
        self.assertEqual("reject", rejected["status"])
        self.assertIn("must not claim backend execution", rejected["reason"])

        leaky = native_payload_transition_trace_stream_contract()
        leaky["note"] = "paper-specific shortcut"
        rejected = validate_native_payload_transition_trace_stream_contract(leaky)
        self.assertEqual("reject", rejected["status"])
        self.assertIn("app identity token leaked", rejected["reason"])

    def test_validator_rejects_missing_bounded_sample_gate(self) -> None:
        contract = native_payload_transition_trace_stream_contract()
        contract["success_gates"] = tuple(
            gate for gate in contract["success_gates"]
            if gate != "bounded_external_oracle_sample_row_recovery"
        )
        rejected = validate_native_payload_transition_trace_stream_contract(contract)
        self.assertEqual("reject", rejected["status"])
        self.assertIn("bounded sample-row recovery", rejected["reason"])

    def test_public_rtdsl_exports_contract(self) -> None:
        self.assertIs(
            rtdsl.native_payload_transition_trace_stream_contract,
            native_payload_transition_trace_stream_contract,
        )
        self.assertIs(
            rtdsl.validate_native_payload_transition_trace_stream_contract,
            validate_native_payload_transition_trace_stream_contract,
        )
        self.assertEqual(
            ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT,
            rtdsl.ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT,
        )


if __name__ == "__main__":
    unittest.main()
