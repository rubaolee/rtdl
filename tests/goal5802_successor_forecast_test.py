from __future__ import annotations

import copy
import math
import unittest

from experiments.goal5802_premeasurement.contract import operation_contract
from experiments.goal5802_premeasurement.successor_forecast import (
    ARMS,
    DIRECT,
    OPERATION_FORECAST_PROJECTION,
    PREDECESSOR_AUTHORITY,
    PREDECESSOR_PROBABILITIES,
    PYOPTIX,
    REGIMES,
    REQUIRED_CHANGE_IDS,
    RTDL,
    SCHEMA,
    TASKS,
    THRESHOLDS,
    SuccessorForecastError,
    build_final_cost_inventory,
    build_successor_forecast,
    validate_successor_forecast,
)
from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    digest,
)


def _operation_contract() -> dict[str, object]:
    value = operation_contract()
    value["forecast_cost_projection"] = copy.deepcopy(
        OPERATION_FORECAST_PROJECTION)
    return value


def _identity(value: dict[str, object]) -> dict[str, str]:
    return {
        "complete_product_binding_sha256": "1" * 64,
        "workload_authority_sha256": "2" * 64,
        "operation_contract_sha256": digest(value),
        "comparative_schedule_sha256": "4" * 64,
        "build_cold_absolute_schedule_sha256": "5" * 64,
        "complete_instrument_source_manifest_sha256": "6" * 64,
        "goal5799_repaired_contract_sha256": "7" * 64,
    }


def _primary() -> list[dict[str, object]]:
    rows = []
    for index, (task, regime) in enumerate(
            (pair for task in TASKS for pair in
             ((task, regime) for regime in REGIMES))):
        threshold = THRESHOLDS[regime]
        rows.append({
            "task": task,
            "regime": regime,
            "gate": f"CI_UPPER_LE_{threshold:.2f}",
            "noninferiority_threshold": threshold,
            "predicted_median_interval": [0.90 + index / 100, 1.10 + index / 100],
            "predicted_95_percent_ci_upper_interval": [1.00, 1.20 + index / 100],
            "subjective_gate_pass_probability": 0.41 + index / 100,
            "predecessor_subjective_gate_pass_probability": (
                PREDECESSOR_PROBABILITIES[(task, regime)]),
            "manual_successor_probability_entry": True,
            "probability_copied_or_defaulted_from_predecessor": False,
            "change_reason_ids": list(REQUIRED_CHANGE_IDS),
        })
    return rows


def _joint() -> dict[str, object]:
    return {
        "all_six_gates_pass_probability_interval": [0.10, 0.22],
        "predecessor_all_six_gates_pass_probability_interval": [0.25, 0.40],
        "manual_successor_probability_entry": True,
        "probability_copied_or_defaulted_from_predecessor": False,
        "independence_assumed": False,
        "highest_risk_regime": "DEPLOYMENT_COLD",
        "change_reason_ids": list(REQUIRED_CHANGE_IDS),
    }


def _direct() -> list[dict[str, object]]:
    return [
        {
            "task": RELATION_TASK,
            "regime": "STEADY_E2E",
            "metric": "PYOPTIX_OVER_DIRECT",
            "predicted_median_interval": [4.5, 6.5],
            "manual_interval_entry": True,
            "change_reason_ids": list(REQUIRED_CHANGE_IDS),
        },
        {
            "task": TRIANGLE_TASK,
            "regime": "STEADY_E2E",
            "metric": "PYOPTIX_OVER_DIRECT",
            "predicted_median_interval": [8.0, 13.0],
            "manual_interval_entry": True,
            "change_reason_ids": list(REQUIRED_CHANGE_IDS),
        },
    ]


def _build() -> tuple[dict[str, object], dict[str, object], dict[str, str]]:
    operation = _operation_contract()
    identity = _identity(operation)
    forecast = build_successor_forecast(
        identity_binding=identity,
        operation_contract=operation,
        primary_predictions=_primary(),
        joint_prediction=_joint(),
        direct_context_predictions=_direct(),
    )
    return forecast, operation, identity


class FinalCostInventoryTest(unittest.TestCase):
    def test_machine_projection_covers_every_redteam_cost(self) -> None:
        inventory = build_final_cost_inventory(_operation_contract())
        self.assertEqual(
            [(row["task"], row["arm"]) for row in inventory["rows"]],
            [(task, arm) for task in TASKS for arm in ARMS])
        rows = {(row["task"], row["arm"]): row
                for row in inventory["rows"]}

        relation = rows[(RELATION_TASK, RTDL)]
        self.assertEqual(relation["optix_traversal_launch_count"], 2)
        self.assertEqual(relation["auxiliary_cuda_kernel_launch_count"], 7)
        self.assertEqual(relation["total_explicit_gpu_launch_count"], 9)
        self.assertEqual(relation["semantic_compaction_launch_count"], 1)
        self.assertEqual(relation["semantic_compaction_key_capacity"], 8192)
        self.assertEqual(relation["semantic_compaction_scratch_bytes"], 98312)
        self.assertEqual(relation["stream_ordered_memset_call_count"], 9)
        self.assertEqual(relation["execution_parameter_h2d_bytes"], 224)
        self.assertEqual(relation["compact_status_control_d2h_bytes"], 16)
        self.assertEqual(relation["first_execute_dynamic_upload_call_count"], 2)
        self.assertEqual(relation["first_execute_dynamic_upload_bytes"], 212992)

        triangle = rows[(TRIANGLE_TASK, RTDL)]
        self.assertEqual(triangle["optix_traversal_launch_count"], 1)
        self.assertEqual(triangle["auxiliary_cuda_kernel_launch_count"], 6)
        self.assertEqual(triangle["total_explicit_gpu_launch_count"], 7)
        self.assertEqual(triangle["stream_ordered_memset_call_count"], 4)
        self.assertEqual(triangle["execution_parameter_h2d_bytes"], 200)
        self.assertEqual(triangle["compact_status_control_d2h_bytes"], 4)
        self.assertEqual(triangle["first_execute_dynamic_upload_call_count"], 8)
        self.assertEqual(triangle["first_execute_dynamic_upload_bytes"], 589824)

        for arm in (DIRECT, PYOPTIX):
            baseline = rows[(TRIANGLE_TASK, arm)]
            self.assertEqual(baseline["first_execute_dynamic_upload_call_count"], 2)
            self.assertEqual(baseline["first_execute_dynamic_upload_bytes"], 524288)
        self.assertEqual(
            inventory["regime_receipt_counts"],
            [
                {"regime": "DEPLOYMENT_COLD", "operation_receipt_count": 1},
                {"regime": "PREPARE", "operation_receipt_count": 1},
                {"regime": "STEADY_E2E", "operation_receipt_count": 72},
            ])
        overhead = inventory["receipt_and_deployment_overheads"]
        self.assertEqual(overhead["rtdl_native_operation_receipt_field_count"], 27)
        self.assertIs(
            overhead[
                "rtdlexe_deployment_validation_inside_deployment_cold_primary_timer"],
            True)
        self.assertIs(overhead["operation_receipt_serialization_inside_primary_timer"],
                      False)

    def test_cost_projection_is_mandatory_and_exact(self) -> None:
        missing = operation_contract()
        del missing["forecast_cost_projection"]
        with self.assertRaises(SuccessorForecastError):
            build_final_cost_inventory(missing)
        malformed = _operation_contract()
        malformed["forecast_cost_projection"][
            "rtdl_native_operation_receipt_field_count"] = 26
        with self.assertRaises(SuccessorForecastError):
            build_final_cost_inventory(malformed)

    def test_bool_cannot_masquerade_as_an_integer_cost(self) -> None:
        value = _operation_contract()
        value["unmatched_internal_work"]["exact_per_arm_success_path"][RTDL][
            "relation_auxiliary_cuda_kernel_launch_count"] = True
        with self.assertRaises(SuccessorForecastError):
            build_final_cost_inventory(value)

    def test_relation_compaction_cost_cannot_disappear_into_zero_default(self) -> None:
        value = _operation_contract()
        del value["relation"][RTDL]["semantic_compaction_scratch_bytes"]
        with self.assertRaises(SuccessorForecastError):
            build_final_cost_inventory(value)

    def test_changed_contract_is_projected_not_hidden(self) -> None:
        first = _operation_contract()
        second = copy.deepcopy(first)
        second["dynamic_input_lifecycle"]["first_execute_by_arm"][RTDL][
            "triangle"]["dynamic_device_upload_bytes"] = 600000
        first_inventory = build_final_cost_inventory(first)
        second_inventory = build_final_cost_inventory(second)
        self.assertNotEqual(first_inventory["operation_contract_sha256"],
                            second_inventory["operation_contract_sha256"])
        self.assertEqual(second_inventory["rows"][5][
            "first_execute_dynamic_upload_bytes"], 600000)


class SuccessorForecastContractTest(unittest.TestCase):
    def test_valid_successor_is_exactly_bound_and_locked(self) -> None:
        forecast, operation, identity = _build()
        self.assertEqual(forecast["schema"], SCHEMA)
        self.assertEqual(
            [(row["task"], row["regime"])
             for row in forecast["primary_predictions"]],
            [(task, regime) for task in TASKS for regime in REGIMES])
        self.assertIs(forecast["authorization"]["formal_worker_zero_authorized"],
                      False)
        self.assertEqual(forecast["predecessor_authority"], PREDECESSOR_AUTHORITY)
        self.assertEqual(forecast["identity_binding"], {
            key: identity[key] for key in sorted(identity)})
        self.assertEqual(
            validate_successor_forecast(
                forecast, expected_identity_binding=identity,
                expected_operation_contract=operation),
            forecast)

    def test_strict_validation_requires_external_expected_authorities(self) -> None:
        forecast, operation, identity = _build()
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(forecast)
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(
                forecast, expected_identity_binding=identity)
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(
                forecast, expected_operation_contract=operation)

    def test_old_v1_cannot_masquerade_as_successor(self) -> None:
        fake = {
            "schema": PREDECESSOR_AUTHORITY["schema"],
            "status": "PREMEASUREMENT_PREDICTION_FROZEN",
        }
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(fake)

    def test_top_level_extra_or_missing_key_rejects(self) -> None:
        forecast, operation, identity = _build()
        extra = copy.deepcopy(forecast)
        extra["comment"] = "looks harmless"
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(
                extra, expected_identity_binding=identity,
                expected_operation_contract=operation)
        missing = copy.deepcopy(forecast)
        del missing["joint_prediction"]
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(
                missing, expected_identity_binding=identity,
                expected_operation_contract=operation)

    def test_forecast_seal_detects_tampering(self) -> None:
        forecast, operation, identity = _build()
        forecast["primary_predictions"][0][
            "subjective_gate_pass_probability"] = 0.99
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(
                forecast, expected_identity_binding=identity,
                expected_operation_contract=operation)

    def test_product_workload_operation_schedule_instrument_and_goal5799_bind(self) -> None:
        forecast, operation, identity = _build()
        for key in identity:
            hostile = copy.deepcopy(identity)
            hostile[key] = "a" * 64
            with self.subTest(key=key), self.assertRaises(SuccessorForecastError):
                validate_successor_forecast(
                    forecast, expected_identity_binding=hostile,
                    expected_operation_contract=operation)
        other_operation = copy.deepcopy(operation)
        other_operation["status"] = "CHANGED"
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(
                forecast, expected_identity_binding=identity,
                expected_operation_contract=other_operation)

    def test_builder_rejects_operation_digest_mismatch(self) -> None:
        operation = _operation_contract()
        identity = _identity(operation)
        identity["operation_contract_sha256"] = "f" * 64
        with self.assertRaises(SuccessorForecastError):
            build_successor_forecast(
                identity_binding=identity,
                operation_contract=operation,
                primary_predictions=_primary(), joint_prediction=_joint(),
                direct_context_predictions=_direct())

    def test_all_six_rows_and_exact_order_are_mandatory(self) -> None:
        operation = _operation_contract()
        identity = _identity(operation)
        short = _primary()[:-1]
        with self.assertRaises(SuccessorForecastError):
            build_successor_forecast(
                identity_binding=identity, operation_contract=operation,
                primary_predictions=short, joint_prediction=_joint(),
                direct_context_predictions=_direct())
        shuffled = _primary()
        shuffled[0], shuffled[1] = shuffled[1], shuffled[0]
        with self.assertRaises(SuccessorForecastError):
            build_successor_forecast(
                identity_binding=identity, operation_contract=operation,
                primary_predictions=shuffled, joint_prediction=_joint(),
                direct_context_predictions=_direct())

    def test_thresholds_and_gates_cannot_move(self) -> None:
        operation = _operation_contract()
        identity = _identity(operation)
        for field, value in (
                ("noninferiority_threshold", 1.11),
                ("noninferiority_threshold", True),
                ("gate", "CI_UPPER_LE_1.11")):
            rows = _primary()
            rows[0][field] = value
            with self.subTest(field=field, value=value), \
                    self.assertRaises(SuccessorForecastError):
                build_successor_forecast(
                    identity_binding=identity, operation_contract=operation,
                    primary_predictions=rows, joint_prediction=_joint(),
                    direct_context_predictions=_direct())

    def test_manual_probability_fields_cannot_be_missing_or_defaulted(self) -> None:
        operation = _operation_contract()
        identity = _identity(operation)
        hostile_rows = []
        missing = _primary()
        del missing[0]["subjective_gate_pass_probability"]
        hostile_rows.append(missing)
        nonmanual = _primary()
        nonmanual[0]["manual_successor_probability_entry"] = False
        hostile_rows.append(nonmanual)
        copied = _primary()
        copied[0]["probability_copied_or_defaulted_from_predecessor"] = True
        hostile_rows.append(copied)
        boolean_probability = _primary()
        boolean_probability[0]["subjective_gate_pass_probability"] = True
        hostile_rows.append(boolean_probability)
        for index, rows in enumerate(hostile_rows):
            with self.subTest(index=index), self.assertRaises(SuccessorForecastError):
                build_successor_forecast(
                    identity_binding=identity, operation_contract=operation,
                    primary_predictions=rows, joint_prediction=_joint(),
                    direct_context_predictions=_direct())

    def test_numbers_must_be_finite_in_range_and_intervals_ordered(self) -> None:
        operation = _operation_contract()
        identity = _identity(operation)
        hostile = (
            ("subjective_gate_pass_probability", -0.01),
            ("subjective_gate_pass_probability", 1.01),
            ("subjective_gate_pass_probability", math.nan),
            ("subjective_gate_pass_probability", math.inf),
            ("predicted_median_interval", [1.1, 0.9]),
            ("predicted_95_percent_ci_upper_interval", [0.9, math.inf]),
        )
        for field, value in hostile:
            rows = _primary()
            rows[0][field] = value
            with self.subTest(field=field, value=value), \
                    self.assertRaises(SuccessorForecastError):
                build_successor_forecast(
                    identity_binding=identity, operation_contract=operation,
                    primary_predictions=rows, joint_prediction=_joint(),
                    direct_context_predictions=_direct())

    def test_predecessor_values_and_authority_are_immutable(self) -> None:
        operation = _operation_contract()
        identity = _identity(operation)
        rows = _primary()
        rows[0]["predecessor_subjective_gate_pass_probability"] = 0.56
        with self.assertRaises(SuccessorForecastError):
            build_successor_forecast(
                identity_binding=identity, operation_contract=operation,
                primary_predictions=rows, joint_prediction=_joint(),
                direct_context_predictions=_direct())
        forecast, operation, identity = _build()
        forecast["predecessor_authority"]["canonical_utf8_lf_bytes"] += 1
        with self.assertRaises(SuccessorForecastError):
            validate_successor_forecast(
                forecast, expected_identity_binding=identity,
                expected_operation_contract=operation)

    def test_every_required_change_id_must_be_accounted_for(self) -> None:
        operation = _operation_contract()
        identity = _identity(operation)
        omitted = REQUIRED_CHANGE_IDS[-1]
        rows = _primary()
        for row in rows:
            row["change_reason_ids"].remove(omitted)
        joint = _joint()
        joint["change_reason_ids"].remove(omitted)
        direct = _direct()
        for row in direct:
            row["change_reason_ids"].remove(omitted)
        with self.assertRaises(SuccessorForecastError):
            build_successor_forecast(
                identity_binding=identity, operation_contract=operation,
                primary_predictions=rows, joint_prediction=joint,
                direct_context_predictions=direct)

    def test_joint_and_direct_context_are_manual_and_ordered(self) -> None:
        operation = _operation_contract()
        identity = _identity(operation)
        joint = _joint()
        joint["manual_successor_probability_entry"] = False
        with self.assertRaises(SuccessorForecastError):
            build_successor_forecast(
                identity_binding=identity, operation_contract=operation,
                primary_predictions=_primary(), joint_prediction=joint,
                direct_context_predictions=_direct())
        direct = list(reversed(_direct()))
        with self.assertRaises(SuccessorForecastError):
            build_successor_forecast(
                identity_binding=identity, operation_contract=operation,
                primary_predictions=_primary(), joint_prediction=_joint(),
                direct_context_predictions=direct)


if __name__ == "__main__":
    unittest.main()
