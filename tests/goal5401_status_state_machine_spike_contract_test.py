from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5401StatusStateMachineSpikeContractTest(unittest.TestCase):
    def test_contract_is_public_and_valid(self) -> None:
        import rtdsl as rt

        self.assertIn("ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT", rt.__all__)
        self.assertIn("active_query_status_state_machine_native_spike_contract", rt.__all__)
        self.assertIn("validate_active_query_status_state_machine_native_spike_contract", rt.__all__)

        validation = rt.validate_active_query_status_state_machine_native_spike_contract()
        self.assertEqual(validation["status"], "accept")
        contract = validation["contract"]

        self.assertEqual(
            contract["contract"],
            rt.ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT,
        )
        self.assertFalse(contract["executable"])
        self.assertTrue(contract["app_generic"])
        self.assertFalse(contract["explicit_app_option_support_claimed"])
        self.assertFalse(contract["native_engine_app_specific"])

    def test_contract_requires_raw_offload_before_feedback_and_feedback_telemetry(self) -> None:
        import rtdsl as rt

        contract = rt.active_query_status_state_machine_native_spike_contract()
        points = {point["name"]: point for point in contract["required_emission_points"]}

        self.assertIn("raw_offload_before_continuation_reduce", points)
        raw = points["raw_offload_before_continuation_reduce"]
        self.assertIn("continuation feedback", raw["must_happen_before"])
        self.assertIn("sort or unique", raw["must_happen_before"])
        self.assertIn("status_code", raw["required_columns"])
        self.assertIn("transition_phase_code", raw["required_columns"])
        self.assertIn("current_best_before_sq", raw["required_columns"])

        self.assertIn("post_continuation_feedback", points)
        feedback = points["post_continuation_feedback"]
        self.assertIn("feedback_applied", feedback["required_columns"])

        telemetry = set(contract["required_telemetry"])
        self.assertIn("raw_offload_row_count", telemetry)
        self.assertIn("raw_offload_row_hash_or_deterministic_samples", telemetry)
        self.assertIn("feedback_update_count", telemetry)
        self.assertIn("overflowed", telemetry)

    def test_contract_gates_are_stronger_than_existing_row_remaps(self) -> None:
        import rtdsl as rt

        contract = rt.active_query_status_state_machine_native_spike_contract()

        gates = set(contract["success_gates"])
        self.assertIn("synthetic_non_app_raw_offload_rows", gates)
        self.assertIn("bounded_app_oracle_row_count_and_hash", gates)
        self.assertIn("full_external_oracle_row_count_hash_status_and_feedback", gates)

        forbidden = set(contract["forbidden_backend_behavior"])
        self.assertIn("hard_coded_row_fanout_per_active_query", forbidden)
        self.assertIn("app_option_names_in_native_symbols", forbidden)
        self.assertIn("external_result_claim_without_row_hash_feedback_gate", forbidden)

        fail_closed = set(contract["required_fail_closed_rules"])
        self.assertIn("row_count_mismatch_keeps_external_option_unsupported", fail_closed)
        self.assertIn("feedback_mismatch_keeps_external_option_unsupported", fail_closed)

    def test_contract_rejects_missing_emission_or_feedback_requirements(self) -> None:
        import rtdsl as rt

        contract = rt.active_query_status_state_machine_native_spike_contract()
        broken = dict(contract)
        broken["required_emission_points"] = tuple(
            point
            for point in contract["required_emission_points"]
            if point["name"] != "raw_offload_before_continuation_reduce"
        )
        rejected = rt.validate_active_query_status_state_machine_native_spike_contract(broken)
        self.assertEqual(rejected["status"], "reject")
        self.assertIn("raw offload", rejected["reason"])

        broken = dict(contract)
        broken["required_telemetry"] = tuple(
            value for value in contract["required_telemetry"] if value != "feedback_update_count"
        )
        rejected = rt.validate_active_query_status_state_machine_native_spike_contract(broken)
        self.assertEqual(rejected["status"], "reject")
        self.assertIn("feedback_update_count", rejected["reason"])

    def test_contract_is_app_neutral_in_source_and_payload(self) -> None:
        import rtdsl as rt

        source = inspect.getsource(rt.active_query_status_state_machine_native_spike_contract).lower()
        validation_source = inspect.getsource(
            rt.validate_active_query_status_state_machine_native_spike_contract
        ).lower()
        payload = str(rt.active_query_status_state_machine_native_spike_contract()).lower()
        for text in (source, validation_source, payload):
            for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
                self.assertNotIn(forbidden, text)

        broken = dict(rt.active_query_status_state_machine_native_spike_contract())
        broken["success_gates"] = tuple(broken["success_gates"]) + ("paper_specific_gate",)
        rejected = rt.validate_active_query_status_state_machine_native_spike_contract(broken)
        self.assertEqual(rejected["status"], "reject")
        self.assertIn("app identity token", rejected["reason"])


if __name__ == "__main__":
    unittest.main()
