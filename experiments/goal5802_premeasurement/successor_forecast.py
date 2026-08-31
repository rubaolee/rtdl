"""Strict Goal5802 final-successor subjective forecast authority.

This module deliberately does not contain forecast probabilities.  A caller
must supply all six task/regime rows and the joint probability explicitly.
The builder only validates, binds, and seals those manual judgements.  The
historical v1 document is retained as a calibration predecessor and can never
be accepted as the operative v2 forecast.

The forecast has no inferential weight and authorizes no execution.  Its only
purpose is falsifiable, pre-result self-calibration against the exact final
product, workloads, operation contract, schedules, and instrument.
"""

from __future__ import annotations

import copy
import hashlib
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

from .workload import RELATION_TASK, TRIANGLE_TASK, canonical, digest


SCHEMA = "rtdl.goal5802.final_successor_subjective_forecast.v2"
STATUS = (
    "FINAL_PRODUCT_TASK_AND_INSTRUMENT_BOUND__SUBJECTIVE_NO_INFERENTIAL_"
    "WEIGHT__FORMAL_EXECUTION_LOCKED"
)
SEAL_DOMAIN = b"RTDL-GOAL5802-FINAL-SUCCESSOR-FORECAST-V2"

DIRECT = "A_DIRECT_CUDA_OPTIX"
PYOPTIX = "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY"
RTDL = "D_RTDL_CLEAN_INSTALLED_RTLEXE"
ARMS = (DIRECT, PYOPTIX, RTDL)
TASKS = (RELATION_TASK, TRIANGLE_TASK)
REGIMES = ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E")

THRESHOLDS = {
    "DEPLOYMENT_COLD": 1.10,
    "PREPARE": 1.10,
    "STEADY_E2E": 1.05,
}
GATES = {
    regime: f"CI_UPPER_LE_{threshold:.2f}"
    for regime, threshold in THRESHOLDS.items()
}

PREDECESSOR_PROBABILITIES = {
    (RELATION_TASK, "DEPLOYMENT_COLD"): 0.55,
    (RELATION_TASK, "PREPARE"): 0.75,
    (RELATION_TASK, "STEADY_E2E"): 0.60,
    (TRIANGLE_TASK, "DEPLOYMENT_COLD"): 0.60,
    (TRIANGLE_TASK, "PREPARE"): 0.80,
    (TRIANGLE_TASK, "STEADY_E2E"): 0.70,
}

PREDECESSOR_AUTHORITY = {
    "schema": "rtdl.goal5802.three_survival_question_prediction_freeze.v1",
    "path": (
        "history/internal_docs/"
        "goal5802_premeasurement_three_survival_question_prediction_freeze_"
        "20260824.json"
    ),
    "authority_commit": "c064fab001469a69e29219e24d2059c75316d0c2",
    "git_blob_sha1": "a3818a4bce842d7ab30986c2cd0b5c8f11a1a654",
    "canonical_utf8_lf_bytes": 10_538,
    "canonical_utf8_lf_sha256": (
        "45812c3a5a371615752096e95f5156ded5ac7d19ed53466ed03239d6622855b6"
    ),
    "role": "CALIBRATION_PREDECESSOR_ONLY__NOT_CURRENT_FORECAST",
}

IDENTITY_KEYS = {
    "complete_product_binding_sha256",
    "workload_authority_sha256",
    "operation_contract_sha256",
    "comparative_schedule_sha256",
    "build_cold_absolute_schedule_sha256",
    "complete_instrument_source_manifest_sha256",
    "goal5799_repaired_contract_sha256",
}

REQUIRED_CHANGE_ROWS = (
    {
        "change_id": "FINAL_PRODUCT_IDENTITY_BOUND",
        "description": (
            "The successor binds the complete final clean-installed product "
            "rather than the predecessor product commit."
        ),
        "expected_ratio_pressure": "AMBIGUOUS",
    },
    {
        "change_id": "V2_MATCHED_TASK_IDENTITIES_BOUND",
        "description": (
            "Both final V2 matched workloads replace the predecessor V1 task "
            "identities."
        ),
        "expected_ratio_pressure": "AMBIGUOUS",
    },
    {
        "change_id": "RELATION_SEMANTIC_COMPACTION_CAPACITY_AND_SCRATCH_INCLUDED",
        "description": (
            "The relation forecast includes device semantic compaction, its "
            "exact key capacity, and exact scratch allocation projected from "
            "the final operation contract."
        ),
        "expected_ratio_pressure": "UPWARD_RTDL_OVER_PYOPTIX",
    },
    {
        "change_id": "RTDL_HELPER_KERNEL_MEMSET_AND_PARAMETER_H2D_COSTS_INCLUDED",
        "description": (
            "The forecast includes each arm's helper launches, memsets, and "
            "execution-parameter H2D bytes."
        ),
        "expected_ratio_pressure": "UPWARD_RTDL_OVER_PYOPTIX",
    },
    {
        "change_id": "RTDL_TRIANGLE_DYNAMIC_UPLOAD_COST_INCLUDED",
        "description": (
            "The RTDL and baseline triangle first-execute upload counts and "
            "bytes are projected separately from the final operation contract."
        ),
        "expected_ratio_pressure": "UPWARD_RTDL_OVER_PYOPTIX",
    },
    {
        "change_id": "NATIVE_27_FIELD_OPERATION_RECEIPT_INCLUDED",
        "description": (
            "The exact native 27-field operation receipt is represented and "
            "its serialization remains outside the primary timer."
        ),
        "expected_ratio_pressure": "NO_PRIMARY_TIMER_EFFECT",
    },
    {
        "change_id": "RTDLEXE_DEPLOYMENT_VALIDATION_INCLUDED",
        "description": (
            "The .rtdlexe authority and artifact validation cost is included "
            "in deployment-cold load/deploy."
        ),
        "expected_ratio_pressure": "UPWARD_RTDL_OVER_PYOPTIX",
    },
    {
        "change_id": "COMPLETE_SYMMETRIC_INSTRUMENT_BOUND",
        "description": (
            "The successor binds the complete symmetric final instrument "
            "rather than an earlier partial harness."
        ),
        "expected_ratio_pressure": "AMBIGUOUS",
    },
)
REQUIRED_CHANGE_IDS = tuple(row["change_id"] for row in REQUIRED_CHANGE_ROWS)

OPERATION_FORECAST_PROJECTION = {
    "rtdl_native_operation_receipt_schema": (
        "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2"
    ),
    "rtdl_native_operation_receipt_field_count": 27,
    "rtdlexe_deployment_validation_inside_deployment_cold_primary_timer": True,
    "rtdlexe_deployment_validation_inside_prepare_or_steady_primary_timer": False,
}


class SuccessorForecastError(RuntimeError):
    """Fail-closed validation error for the v2 successor forecast."""


def _exact_keys(value: Any, expected: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise SuccessorForecastError(f"{label} keys differ")
    return value


def _strict_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise SuccessorForecastError(f"{label} must be an integer >= {minimum}")
    return value


def _finite_number(
        value: Any, label: str, *, minimum: float | None = None,
        maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SuccessorForecastError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise SuccessorForecastError(f"{label} must be finite")
    if minimum is not None and result < minimum:
        raise SuccessorForecastError(f"{label} is below its allowed range")
    if maximum is not None and result > maximum:
        raise SuccessorForecastError(f"{label} is above its allowed range")
    return result


def _interval(
        value: Any, label: str, *, minimum: float,
        maximum: float | None = None) -> list[float]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) \
            or len(value) != 2:
        raise SuccessorForecastError(f"{label} must contain two endpoints")
    lower = _finite_number(value[0], f"{label}[0]", minimum=minimum,
                           maximum=maximum)
    upper = _finite_number(value[1], f"{label}[1]", minimum=minimum,
                           maximum=maximum)
    if lower > upper:
        raise SuccessorForecastError(f"{label} endpoints are reversed")
    return [lower, upper]


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise SuccessorForecastError(f"{label} must be a lowercase SHA-256")
    return value


def _ordered_change_ids(value: Any, label: str) -> list[str]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) \
            or not value:
        raise SuccessorForecastError(f"{label} must be a nonempty change-id list")
    result = list(value)
    if any(not isinstance(item, str) for item in result) \
            or len(set(result)) != len(result) \
            or any(item not in REQUIRED_CHANGE_IDS for item in result):
        raise SuccessorForecastError(f"{label} contains an invalid change id")
    expected_order = [item for item in REQUIRED_CHANGE_IDS if item in result]
    if result != expected_order:
        raise SuccessorForecastError(f"{label} change ids are not canonical")
    return result


def _validate_identity_binding(value: Any) -> dict[str, str]:
    binding = _exact_keys(value, IDENTITY_KEYS, "identity_binding")
    return {key: _sha256(binding[key], f"identity_binding.{key}")
            for key in sorted(IDENTITY_KEYS)}


def _operation_row(
        operation_contract: Mapping[str, Any], task_name: str,
        task_key: str, arm: str) -> dict[str, object]:
    task = operation_contract.get(task_key)
    unmatched = operation_contract.get("unmatched_internal_work")
    lifecycle = operation_contract.get("dynamic_input_lifecycle")
    if not isinstance(task, Mapping) or arm not in task \
            or not isinstance(task[arm], Mapping) \
            or not isinstance(unmatched, Mapping) \
            or not isinstance(unmatched.get("exact_per_arm_success_path"), Mapping) \
            or arm not in unmatched["exact_per_arm_success_path"] \
            or not isinstance(unmatched["exact_per_arm_success_path"][arm], Mapping) \
            or not isinstance(lifecycle, Mapping) \
            or not isinstance(lifecycle.get("first_execute_by_arm"), Mapping) \
            or arm not in lifecycle["first_execute_by_arm"] \
            or not isinstance(lifecycle["first_execute_by_arm"][arm], Mapping) \
            or task_key not in lifecycle["first_execute_by_arm"][arm] \
            or not isinstance(
                lifecycle["first_execute_by_arm"][arm][task_key], Mapping):
        raise SuccessorForecastError(
            f"operation_contract lacks the {task_key}/{arm} cost path")
    common = task[arm]
    internal = unmatched["exact_per_arm_success_path"][arm]
    dynamic = lifecycle["first_execute_by_arm"][arm][task_key]
    prefix = "relation" if task_key == "relation" else "triangle"
    optix = _strict_int(common.get("optix_launch_count"),
                        f"{task_key}.{arm}.optix_launch_count")
    auxiliary = _strict_int(
        internal.get(f"{prefix}_auxiliary_cuda_kernel_launch_count"),
        f"{task_key}.{arm}.auxiliary_cuda_kernel_launch_count")
    if task_key == "relation":
        # These three fields are load-bearing relation costs.  Missing may not
        # silently project to zero.
        compaction = _strict_int(
            common.get("semantic_compaction_launch_count"),
            f"{task_key}.{arm}.semantic_compaction_launch_count")
        capacity = _strict_int(
            common.get("semantic_compaction_key_capacity"),
            f"{task_key}.{arm}.semantic_compaction_key_capacity")
        scratch = _strict_int(
            common.get("semantic_compaction_scratch_bytes"),
            f"{task_key}.{arm}.semantic_compaction_scratch_bytes")
    else:
        for field in (
                "semantic_compaction_launch_count",
                "semantic_compaction_key_capacity",
                "semantic_compaction_scratch_bytes"):
            if field in common and _strict_int(
                    common[field], f"{task_key}.{arm}.{field}") != 0:
                raise SuccessorForecastError(
                    "triangle semantic-compaction cost must be zero")
        compaction = capacity = scratch = 0
    return {
        "task": task_name,
        "arm": arm,
        "optix_traversal_launch_count": optix,
        "auxiliary_cuda_kernel_launch_count": auxiliary,
        "total_explicit_gpu_launch_count": optix + auxiliary,
        "semantic_compaction_launch_count": compaction,
        "semantic_compaction_key_capacity": capacity,
        "semantic_compaction_scratch_bytes": scratch,
        "stream_ordered_memset_call_count": _strict_int(
            internal.get(f"{prefix}_stream_ordered_memset_call_count"),
            f"{task_key}.{arm}.stream_ordered_memset_call_count"),
        "execution_parameter_h2d_bytes": _strict_int(
            internal.get(f"{prefix}_execution_parameter_h2d_bytes"),
            f"{task_key}.{arm}.execution_parameter_h2d_bytes"),
        "compact_status_control_d2h_bytes": _strict_int(
            common.get("compact_status_control_d2h_bytes"),
            f"{task_key}.{arm}.compact_status_control_d2h_bytes"),
        "status_output_commit_blocking_boundary_count": _strict_int(
            common.get("status_output_commit_blocking_boundary_count"),
            f"{task_key}.{arm}.status_output_commit_blocking_boundary_count"),
        "first_execute_dynamic_upload_call_count": _strict_int(
            dynamic.get("dynamic_device_upload_call_count"),
            f"{task_key}.{arm}.dynamic_device_upload_call_count"),
        "first_execute_dynamic_upload_bytes": _strict_int(
            dynamic.get("dynamic_device_upload_bytes"),
            f"{task_key}.{arm}.dynamic_device_upload_bytes"),
        "first_execute_dynamic_accel_build_count": _strict_int(
            dynamic.get("dynamic_accel_build_count"),
            f"{task_key}.{arm}.dynamic_accel_build_count"),
    }


def build_final_cost_inventory(
        operation_contract: Mapping[str, Any]) -> dict[str, object]:
    """Derive the forecast cost inventory from one exact operation contract.

    ``forecast_cost_projection`` is intentionally mandatory in the passed
    contract.  The 27-field native receipt and deployment-validation placement
    must therefore be frozen in the same authority as launches and transfers;
    they cannot be added as unbound prose in a forecast.
    """

    if not isinstance(operation_contract, Mapping) \
            or operation_contract.get("schema") \
            != "rtdl.goal5802.three_arm_operation_contract.v1":
        raise SuccessorForecastError("operation_contract schema differs")
    projection = _exact_keys(
        operation_contract.get("forecast_cost_projection"),
        set(OPERATION_FORECAST_PROJECTION),
        "operation_contract.forecast_cost_projection")
    if dict(projection) != OPERATION_FORECAST_PROJECTION:
        raise SuccessorForecastError("operation forecast-cost projection differs")

    common = operation_contract.get("common_semantics")
    lifecycle = operation_contract.get("dynamic_input_lifecycle")
    if not isinstance(common, Mapping) \
            or common.get("receipt_serialization_inside_timer") is not False \
            or common.get("forensic_hashing_inside_timer") is not False \
            or not isinstance(lifecycle, Mapping) \
            or lifecycle.get("machine_receipt_and_exact_source_guard_required") \
            is not True:
        raise SuccessorForecastError("operation receipt/timer contract differs")
    receipt_counts = lifecycle.get("regime_receipt_counts")
    if not isinstance(receipt_counts, Mapping) or set(receipt_counts) != set(REGIMES):
        raise SuccessorForecastError("operation regime receipt counts differ")

    rows = [
        _operation_row(operation_contract, task, task_key, arm)
        for task, task_key in (
            (RELATION_TASK, "relation"), (TRIANGLE_TASK, "triangle"))
        for arm in ARMS
    ]
    result = {
        "schema": "rtdl.goal5802.final_cost_inventory.v1",
        "status": "MACHINE_DERIVED_FROM_EXACT_OPERATION_CONTRACT",
        "operation_contract_sha256": digest(dict(operation_contract)),
        "rows": rows,
        "regime_receipt_counts": [
            {
                "regime": regime,
                "operation_receipt_count": _strict_int(
                    receipt_counts.get(regime),
                    f"regime_receipt_counts.{regime}", minimum=1),
            }
            for regime in REGIMES
        ],
        "receipt_and_deployment_overheads": {
            **OPERATION_FORECAST_PROJECTION,
            "operation_receipt_serialization_inside_primary_timer": False,
            "forensic_hashing_inside_primary_timer": False,
        },
    }
    return result


def _validate_primary_predictions(value: Any) -> list[dict[str, object]]:
    if not isinstance(value, list) or len(value) != len(TASKS) * len(REGIMES):
        raise SuccessorForecastError("primary_predictions must contain six rows")
    expected_pairs = [(task, regime) for task in TASKS for regime in REGIMES]
    expected_keys = {
        "task", "regime", "gate", "noninferiority_threshold",
        "predicted_median_interval",
        "predicted_95_percent_ci_upper_interval",
        "subjective_gate_pass_probability",
        "predecessor_subjective_gate_pass_probability",
        "manual_successor_probability_entry",
        "probability_copied_or_defaulted_from_predecessor",
        "change_reason_ids",
    }
    result: list[dict[str, object]] = []
    for index, (row_value, pair) in enumerate(zip(value, expected_pairs)):
        row = _exact_keys(row_value, expected_keys,
                          f"primary_predictions[{index}]")
        task, regime = pair
        if row.get("task") != task or row.get("regime") != regime:
            raise SuccessorForecastError("primary prediction row order differs")
        if row.get("gate") != GATES[regime] \
                or isinstance(row.get("noninferiority_threshold"), bool) \
                or row.get("noninferiority_threshold") != THRESHOLDS[regime]:
            raise SuccessorForecastError("registered threshold or gate changed")
        if row.get("manual_successor_probability_entry") is not True \
                or row.get("probability_copied_or_defaulted_from_predecessor") \
                is not False:
            raise SuccessorForecastError(
                "successor probability was not explicitly entered")
        predecessor = _finite_number(
            row.get("predecessor_subjective_gate_pass_probability"),
            "predecessor probability", minimum=0.0, maximum=1.0)
        if predecessor != PREDECESSOR_PROBABILITIES[pair]:
            raise SuccessorForecastError("predecessor row probability differs")
        result.append({
            "task": task,
            "regime": regime,
            "gate": row["gate"],
            "noninferiority_threshold": float(row["noninferiority_threshold"]),
            "predicted_median_interval": _interval(
                row.get("predicted_median_interval"),
                "predicted_median_interval", minimum=0.0),
            "predicted_95_percent_ci_upper_interval": _interval(
                row.get("predicted_95_percent_ci_upper_interval"),
                "predicted_95_percent_ci_upper_interval", minimum=0.0),
            "subjective_gate_pass_probability": _finite_number(
                row.get("subjective_gate_pass_probability"),
                "subjective_gate_pass_probability", minimum=0.0, maximum=1.0),
            "predecessor_subjective_gate_pass_probability": predecessor,
            "manual_successor_probability_entry": True,
            "probability_copied_or_defaulted_from_predecessor": False,
            "change_reason_ids": _ordered_change_ids(
                row.get("change_reason_ids"), "primary change_reason_ids"),
        })
    return result


def _validate_joint_prediction(value: Any) -> dict[str, object]:
    row = _exact_keys(value, {
        "all_six_gates_pass_probability_interval",
        "predecessor_all_six_gates_pass_probability_interval",
        "manual_successor_probability_entry",
        "probability_copied_or_defaulted_from_predecessor",
        "independence_assumed", "highest_risk_regime", "change_reason_ids",
    }, "joint_prediction")
    if row.get("manual_successor_probability_entry") is not True \
            or row.get("probability_copied_or_defaulted_from_predecessor") \
            is not False or row.get("independence_assumed") is not False:
        raise SuccessorForecastError("joint forecast is not a manual dependent forecast")
    predecessor = _interval(
        row.get("predecessor_all_six_gates_pass_probability_interval"),
        "predecessor joint interval", minimum=0.0, maximum=1.0)
    if predecessor != [0.25, 0.40]:
        raise SuccessorForecastError("predecessor joint interval differs")
    if row.get("highest_risk_regime") not in REGIMES:
        raise SuccessorForecastError("joint highest-risk regime is invalid")
    return {
        "all_six_gates_pass_probability_interval": _interval(
            row.get("all_six_gates_pass_probability_interval"),
            "joint probability interval", minimum=0.0, maximum=1.0),
        "predecessor_all_six_gates_pass_probability_interval": predecessor,
        "manual_successor_probability_entry": True,
        "probability_copied_or_defaulted_from_predecessor": False,
        "independence_assumed": False,
        "highest_risk_regime": row["highest_risk_regime"],
        "change_reason_ids": _ordered_change_ids(
            row.get("change_reason_ids"), "joint change_reason_ids"),
    }


def _validate_direct_context(value: Any) -> list[dict[str, object]]:
    if not isinstance(value, list) or len(value) != len(TASKS):
        raise SuccessorForecastError("direct_context_predictions must have two rows")
    keys = {
        "task", "regime", "metric", "predicted_median_interval",
        "manual_interval_entry", "change_reason_ids",
    }
    result = []
    for index, (row_value, task) in enumerate(zip(value, TASKS)):
        row = _exact_keys(row_value, keys,
                          f"direct_context_predictions[{index}]")
        if row.get("task") != task or row.get("regime") != "STEADY_E2E" \
                or row.get("metric") != "PYOPTIX_OVER_DIRECT" \
                or row.get("manual_interval_entry") is not True:
            raise SuccessorForecastError("direct context row identity differs")
        result.append({
            "task": task,
            "regime": "STEADY_E2E",
            "metric": "PYOPTIX_OVER_DIRECT",
            "predicted_median_interval": _interval(
                row.get("predicted_median_interval"),
                "direct context interval", minimum=0.0),
            "manual_interval_entry": True,
            "change_reason_ids": _ordered_change_ids(
                row.get("change_reason_ids"), "direct context change_reason_ids"),
        })
    return result


def _authorization() -> dict[str, object]:
    return {
        "formal_worker_zero_authorized": False,
        "registered_gpu_timing_authorized": False,
        "pod_execution_authorized": False,
        "performance_claim_authorized": False,
        "forecast_generation_without_manual_probabilities_allowed": False,
        "postresult_probability_change_allowed": False,
        "required_at_seal_registered_performance_observation_count": 0,
        "formal_execution_requires_this_seal_before_worker_zero": True,
    }


def _calibration_policy() -> dict[str, object]:
    return {
        "probability_semantics": (
            "SUBJECTIVE_ENGINEERING_FORECAST__NO_INFERENTIAL_WEIGHT"),
        "primary_metric": (
            "RTDL_BLOCK_NS_OVER_PYOPTIX_BLOCK_NS__GREATER_THAN_ONE_MEANS_"
            "RTDL_SLOWER"),
        "gate_statistic": "PAIRED_BLOCK_BOOTSTRAP_95_PERCENT_CI_UPPER",
        "predecessor_use": "CALIBRATION_RECORD_ONLY__NOT_CURRENT_FORECAST",
        "registered_thresholds_unchanged": True,
        "row_by_row_calibration_after_result_required": True,
        "brier_score_or_p_value_claimed": False,
        "all_valid_results_including_all_losses_accepted": True,
        "postresult_rewrite_allowed": False,
    }


def _forecast_seal(unsigned: Mapping[str, Any]) -> str:
    return hashlib.sha256(SEAL_DOMAIN + b"\0" + canonical(dict(unsigned))).hexdigest()


def build_successor_forecast(
        *, identity_binding: Mapping[str, Any],
        operation_contract: Mapping[str, Any],
        primary_predictions: list[Mapping[str, Any]],
        joint_prediction: Mapping[str, Any],
        direct_context_predictions: list[Mapping[str, Any]]) -> dict[str, object]:
    """Build a sealed forecast without inventing any probability or interval."""

    binding = _validate_identity_binding(identity_binding)
    operation_sha = digest(dict(operation_contract))
    if binding["operation_contract_sha256"] != operation_sha:
        raise SuccessorForecastError(
            "identity binding does not bind the supplied operation contract")
    primary = _validate_primary_predictions(primary_predictions)
    joint = _validate_joint_prediction(joint_prediction)
    direct = _validate_direct_context(direct_context_predictions)
    referenced = {
        item
        for row in [*primary, joint, *direct]
        for item in row["change_reason_ids"]
    }
    if referenced != set(REQUIRED_CHANGE_IDS):
        raise SuccessorForecastError(
            "predictions do not account for every required successor change")
    unsigned: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "authorization": _authorization(),
        "predecessor_authority": copy.deepcopy(PREDECESSOR_AUTHORITY),
        "identity_binding": binding,
        "final_cost_inventory": build_final_cost_inventory(operation_contract),
        "changes_since_predecessor": copy.deepcopy(list(REQUIRED_CHANGE_ROWS)),
        "primary_predictions": primary,
        "joint_prediction": joint,
        "direct_context_predictions": direct,
        "calibration_policy": _calibration_policy(),
    }
    result = {**unsigned, "forecast_sha256": _forecast_seal(unsigned)}
    return validate_successor_forecast(
        result, expected_identity_binding=identity_binding,
        expected_operation_contract=operation_contract)


def validate_successor_forecast(
        value: Mapping[str, Any], *,
        expected_identity_binding: Mapping[str, Any] | None = None,
        expected_operation_contract: Mapping[str, Any] | None = None,
        require_execution_locked: bool = True) -> dict[str, object]:
    """Strictly validate a complete v2 successor forecast and its domain seal."""

    top = _exact_keys(value, {
        "schema", "status", "authorization", "predecessor_authority",
        "identity_binding", "final_cost_inventory",
        "changes_since_predecessor", "primary_predictions",
        "joint_prediction", "direct_context_predictions",
        "calibration_policy", "forecast_sha256",
    }, "successor forecast")
    if top.get("schema") != SCHEMA or top.get("status") != STATUS:
        raise SuccessorForecastError("successor forecast envelope differs")
    if expected_identity_binding is None or expected_operation_contract is None:
        raise SuccessorForecastError(
            "strict successor validation requires the expected identity and "
            "operation contract authorities")
    authorization = _exact_keys(
        top.get("authorization"), set(_authorization()), "authorization")
    if dict(authorization) != _authorization():
        raise SuccessorForecastError("successor forecast authorization differs")
    if require_execution_locked \
            and authorization.get("formal_worker_zero_authorized") is not False:
        raise SuccessorForecastError("successor forecast is not execution locked")
    predecessor = _exact_keys(
        top.get("predecessor_authority"), set(PREDECESSOR_AUTHORITY),
        "predecessor_authority")
    if dict(predecessor) != PREDECESSOR_AUTHORITY:
        raise SuccessorForecastError("predecessor authority differs")
    binding = _validate_identity_binding(top.get("identity_binding"))
    if binding != _validate_identity_binding(expected_identity_binding):
        raise SuccessorForecastError("successor identity binding differs")

    changes = top.get("changes_since_predecessor")
    if changes != list(REQUIRED_CHANGE_ROWS):
        raise SuccessorForecastError("required successor change ledger differs")
    primary = _validate_primary_predictions(top.get("primary_predictions"))
    joint = _validate_joint_prediction(top.get("joint_prediction"))
    direct = _validate_direct_context(top.get("direct_context_predictions"))
    referenced = {
        item
        for row in [*primary, joint, *direct]
        for item in row["change_reason_ids"]
    }
    if referenced != set(REQUIRED_CHANGE_IDS):
        raise SuccessorForecastError(
            "validated predictions omit a required successor change")
    calibration = _exact_keys(
        top.get("calibration_policy"), set(_calibration_policy()),
        "calibration_policy")
    if dict(calibration) != _calibration_policy():
        raise SuccessorForecastError("calibration policy differs")

    inventory = top.get("final_cost_inventory")
    expected_inventory = build_final_cost_inventory(expected_operation_contract)
    if inventory != expected_inventory:
        raise SuccessorForecastError("final cost inventory differs from contract")
    if binding["operation_contract_sha256"] \
            != expected_inventory["operation_contract_sha256"]:
        raise SuccessorForecastError("operation contract binding differs")

    unsigned = dict(top)
    observed_seal = unsigned.pop("forecast_sha256")
    if _sha256(observed_seal, "forecast_sha256") != _forecast_seal(unsigned):
        raise SuccessorForecastError("successor forecast domain seal differs")
    return copy.deepcopy(dict(top))


__all__ = [
    "ARMS", "DIRECT", "GATES", "IDENTITY_KEYS", "OPERATION_FORECAST_PROJECTION",
    "PREDECESSOR_AUTHORITY", "PREDECESSOR_PROBABILITIES", "PYOPTIX", "REGIMES",
    "REQUIRED_CHANGE_IDS", "REQUIRED_CHANGE_ROWS", "RTDL", "SCHEMA", "STATUS",
    "SuccessorForecastError", "TASKS", "THRESHOLDS", "build_final_cost_inventory",
    "build_successor_forecast", "validate_successor_forecast",
]
