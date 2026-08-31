"""Frozen scientific protocol for the Goal5817 three-arm experiment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "rtdl.goal5817.three_arm_freeze.v2"
AUTHORITY_SCHEMA = "rtdl.goal5817.three_arm_execution_authority.v1"
ARMS = ("DIRECT", "PYOPTIX", "RTDL")
TASKS = ("relation", "triangle")
REGIMES = ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E")
COMPARISONS = (
    ("RTDL", "PYOPTIX"),
    ("PYOPTIX", "DIRECT"),
    ("RTDL", "DIRECT"),
)
BLOCK_COUNT = 18
STEADY_WARMUPS = 8
STEADY_REPETITIONS = 64
BOOTSTRAP_DRAWS = 10_000
PERMUTATIONS = (
    ("DIRECT", "PYOPTIX", "RTDL"),
    ("DIRECT", "RTDL", "PYOPTIX"),
    ("PYOPTIX", "DIRECT", "RTDL"),
    ("PYOPTIX", "RTDL", "DIRECT"),
    ("RTDL", "DIRECT", "PYOPTIX"),
    ("RTDL", "PYOPTIX", "DIRECT"),
)
RTDL_OVER_PYOPTIX_THRESHOLDS = {
    "DEPLOYMENT_COLD": 1.10,
    "PREPARE": 1.10,
    "STEADY_E2E": 1.05,
}
GOAL5805_SOURCE_BUNDLE_SHA256 = (
    "91d2df6f126f885cd82372a82ee700f96614a1b778b8fa197eb77a11e2082b30"
)
GOAL5805_SOURCE_BUNDLE_BYTES = 8_694_236
DIRECT_WORKER_SHA256 = (
    "078570a19000221890bd5421676c8d4857fd2196c5b7daae60eec7d511ffd165"
)
PREDECESSOR_PRE_GPU_FREEZE_PATH = (
    "history/internal_docs/"
    "goal5817_current_source_three_arm_scientific_freeze_v3_20260829.json"
)
PREDECESSOR_PRE_GPU_FREEZE_SHA256 = (
    "17dbad4bc35b792b64fe4f959ee9d56627afbf5f6aa1e5539918d417af7dcc2e"
)
PREDECESSOR_PRE_GPU_INTERNAL_SEAL = (
    "0aad2bfa23a1d6bd8e660346bd5d0b29d33bd2440a3d7f3cb7f61601f0f54011"
)
HARNESS_PATHS = (
    "experiments/goal5817_three_arm/__init__.py",
    "experiments/goal5817_three_arm/controller.py",
    "experiments/goal5817_three_arm/evaluate.py",
    "experiments/goal5817_three_arm/formal_python_worker.py",
    "experiments/goal5817_three_arm/protocol.py",
    "scripts/goal5817_build_execution_authority.py",
    "scripts/goal5817_build_runtime_preflight_receipt.py",
    "scripts/goal5817_build_three_arm_freeze.py",
    "scripts/goal5817_target_untimed_kats.py",
    "tests/goal5817_three_arm_protocol_test.py",
)


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_record(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    payload = resolved.read_bytes()
    return {
        "path": str(resolved),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def schedule() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    ordinal = 0
    for task in TASKS:
        for regime in REGIMES:
            for block in range(BLOCK_COUNT):
                order = PERMUTATIONS[block % len(PERMUTATIONS)]
                for position, arm in enumerate(order):
                    rows.append({
                        "ordinal": ordinal,
                        "worker_id": (
                            f"{task}_{regime.lower()}_b{block:02d}_"
                            f"p{position}_{arm.lower()}"
                        ),
                        "task": task,
                        "regime": regime,
                        "block": block,
                        "position": position,
                        "arm": arm,
                    })
                    ordinal += 1
    return rows


def build_freeze(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    bundle = root / (
        "history/internal_docs/"
        "goal5805_performance_repair_source_bundle_v5_20260828.tar.gz"
    )
    direct = root / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"
    bundle_record = file_record(bundle)
    direct_record = file_record(direct)
    predecessor_path = root / PREDECESSOR_PRE_GPU_FREEZE_PATH
    predecessor_record = file_record(predecessor_path)
    if bundle_record["sha256"] != GOAL5805_SOURCE_BUNDLE_SHA256 \
            or bundle_record["bytes"] != GOAL5805_SOURCE_BUNDLE_BYTES:
        raise RuntimeError("Goal5817 Goal5805 source bundle identity differs")
    if direct_record["sha256"] != DIRECT_WORKER_SHA256:
        raise RuntimeError("Goal5817 Direct worker identity differs")
    predecessor = json.loads(predecessor_path.read_text(encoding="utf-8"))
    if predecessor_record["sha256"] != PREDECESSOR_PRE_GPU_FREEZE_SHA256 \
            or predecessor.get("freeze_sha256") \
            != PREDECESSOR_PRE_GPU_INTERNAL_SEAL \
            or predecessor.get("status") \
            != "FROZEN_BEFORE_ANY_GOAL5817_GPU_OR_CLOCK_OBSERVATION" \
            or predecessor.get("formal_worker_count") != 0 \
            or predecessor.get("registered_performance_timing_count") != 0:
        raise RuntimeError("Goal5817 pre-GPU predecessor identity differs")
    bundle_record["path"] = (
        "history/internal_docs/"
        "goal5805_performance_repair_source_bundle_v5_20260828.tar.gz"
    )
    direct_record["path"] = (
        "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"
    )
    predecessor_record["path"] = PREDECESSOR_PRE_GPU_FREEZE_PATH
    harness_sources = []
    for relative in HARNESS_PATHS:
        row = file_record(root / relative)
        row["path"] = relative
        harness_sources.append(row)
    value: dict[str, Any] = {
        "schema": SCHEMA,
        "status": (
            "SCIENTIFIC_ESTIMAND_INHERITED_FROM_V3__KAT_ISOLATION_AND_"
            "IMPORT_ROOT_REPAIR_AFTER_ZERO_TIMING_PREFLIGHT_FAILURES"
        ),
        "purpose": (
            "CURRENT_SOURCE_SAME_TARGET_THREE_ARM_COST_DECOMPOSITION__"
            "UNCONDITIONAL_RESULT_ACCEPTANCE"
        ),
        "arms": list(ARMS),
        "tasks": list(TASKS),
        "regimes": list(REGIMES),
        "comparisons": [list(row) for row in COMPARISONS],
        "block_count": BLOCK_COUNT,
        "schedule": schedule(),
        "steady_warmups": STEADY_WARMUPS,
        "steady_repetitions": STEADY_REPETITIONS,
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "primary_point_estimator": "MEDIAN_OF_18_PAIRED_BLOCK_RATIOS",
        "interval": "FIXED_SEED_PERCENTILE_BOOTSTRAP_OVER_BLOCK_RATIOS",
        "rtdl_over_pyoptix_thresholds": RTDL_OVER_PYOPTIX_THRESHOLDS,
        "direct_comparisons": "DESCRIPTIVE__NO_PASS_FAIL_THRESHOLD",
        "ratio_orientation": "NUMERATOR_ARM_OVER_DENOMINATOR_ARM",
        "result_acceptance": "UNCONDITIONAL_INCLUDING_ALL_UNFAVORABLE_ROWS",
        "retry_replacement_row_drop": False,
        "prior_goal5805_rows_reused_as_current_measurements": False,
        "prior_goal5802_direct_rows_reused_as_current_measurements": False,
        "same_target_all_three_arms_required": True,
        "target_gpu_model_or_driver_preselected": False,
        "scientific_estimand_predecessor": predecessor_record,
        "scientific_estimand_changed_after_predecessor": False,
        "successor_change_scope": (
            "KAT_FRESH_PROCESS_AND_EXACT_CURRENT_SOURCE_IMPORT_ROOT_ONLY"
        ),
        "predecessor_preformal_failures": [
            {
                "lineage": "V3_SHARED_PROCESS_KAT",
                "gpu_observation_occurred": True,
                "performance_clock_observation_occurred": False,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "failure": "RTDL_ADMISSION_REJECTED_PRELOADED_BASELINE_MODULE",
            },
            {
                "lineage": "V5_FRESH_PROCESS_MISSING_IMPORT_ROOT_KAT",
                "gpu_observation_occurred": True,
                "performance_clock_observation_occurred": False,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "failure": "RTDL_CURRENT_SOURCE_PACKAGE_IMPORT_ROOT_ABSENT",
            },
        ],
        "source_bundle": bundle_record,
        "direct_worker_source": direct_record,
        "harness_sources": harness_sources,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "owner_execution_authorized": False,
        "pod_execution_authorized": False,
    }
    value["freeze_sha256"] = digest(value)
    return value


def validate_freeze(
        value: Mapping[str, Any], *, rehash: bool = False,
        root: Path | None = None) -> None:
    unsigned = dict(value)
    observed = unsigned.pop("freeze_sha256", None)
    if value.get("schema") != SCHEMA or observed != digest(unsigned):
        raise RuntimeError("Goal5817 freeze seal differs")
    required = {
        "status": (
            "SCIENTIFIC_ESTIMAND_INHERITED_FROM_V3__KAT_ISOLATION_AND_"
            "IMPORT_ROOT_REPAIR_AFTER_ZERO_TIMING_PREFLIGHT_FAILURES"
        ),
        "arms": list(ARMS),
        "tasks": list(TASKS),
        "regimes": list(REGIMES),
        "comparisons": [list(row) for row in COMPARISONS],
        "block_count": BLOCK_COUNT,
        "schedule": schedule(),
        "steady_warmups": STEADY_WARMUPS,
        "steady_repetitions": STEADY_REPETITIONS,
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "rtdl_over_pyoptix_thresholds": RTDL_OVER_PYOPTIX_THRESHOLDS,
        "result_acceptance": "UNCONDITIONAL_INCLUDING_ALL_UNFAVORABLE_ROWS",
        "retry_replacement_row_drop": False,
        "prior_goal5805_rows_reused_as_current_measurements": False,
        "prior_goal5802_direct_rows_reused_as_current_measurements": False,
        "same_target_all_three_arms_required": True,
        "target_gpu_model_or_driver_preselected": False,
        "scientific_estimand_predecessor": {
            "path": PREDECESSOR_PRE_GPU_FREEZE_PATH,
            "bytes": 71_520,
            "sha256": PREDECESSOR_PRE_GPU_FREEZE_SHA256,
        },
        "scientific_estimand_changed_after_predecessor": False,
        "successor_change_scope": (
            "KAT_FRESH_PROCESS_AND_EXACT_CURRENT_SOURCE_IMPORT_ROOT_ONLY"
        ),
        "predecessor_preformal_failures": [
            {
                "lineage": "V3_SHARED_PROCESS_KAT",
                "gpu_observation_occurred": True,
                "performance_clock_observation_occurred": False,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "failure": "RTDL_ADMISSION_REJECTED_PRELOADED_BASELINE_MODULE",
            },
            {
                "lineage": "V5_FRESH_PROCESS_MISSING_IMPORT_ROOT_KAT",
                "gpu_observation_occurred": True,
                "performance_clock_observation_occurred": False,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "failure": "RTDL_CURRENT_SOURCE_PACKAGE_IMPORT_ROOT_ABSENT",
            },
        ],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "owner_execution_authorized": False,
        "pod_execution_authorized": False,
    }
    for key, expected in required.items():
        if value.get(key) != expected:
            raise RuntimeError(f"Goal5817 freeze field differs: {key}")
    if rehash:
        if root is None:
            raise RuntimeError("Goal5817 freeze rehash root is absent")
        root = root.resolve(strict=True)
        for key in (
                "source_bundle", "direct_worker_source",
                "scientific_estimand_predecessor"):
            row = value.get(key)
            if not isinstance(row, Mapping) \
                    or dict(row) != {
                        **file_record(root / str(row.get("path"))),
                        "path": str(row.get("path")),
                    }:
                raise RuntimeError(f"Goal5817 frozen file differs: {key}")
        rows = value.get("harness_sources")
        if not isinstance(rows, list) \
                or [row.get("path") for row in rows] != list(HARNESS_PATHS):
            raise RuntimeError("Goal5817 harness source inventory differs")
        expected_rows = []
        for relative in HARNESS_PATHS:
            row = file_record(root / relative)
            row["path"] = relative
            expected_rows.append(row)
        if rows != expected_rows:
            raise RuntimeError("Goal5817 harness source bytes differ")


def build_authority(
        freeze_path: Path, target_manifest_path: Path, direct_binary_path: Path,
        *, owner_directive: str) -> dict[str, Any]:
    if not owner_directive.strip():
        raise RuntimeError("Goal5817 owner directive is empty")
    value: dict[str, Any] = {
        "schema": AUTHORITY_SCHEMA,
        "status": "AUTHORIZED_FOR_ONE_CREATE_ONLY_GOAL5817_FORMAL_MATRIX",
        "freeze_file": file_record(freeze_path),
        "target_manifest_file": file_record(target_manifest_path),
        "direct_binary_file": file_record(direct_binary_path),
        "owner_directive_sha256": hashlib.sha256(
            owner_directive.encode("utf-8")).hexdigest(),
        "owner_execution_authorized": True,
        "formal_worker_zero_authorized": True,
        "pod_gpu_timing_authorized": True,
        "unconditional_result_acceptance": True,
        "retry_replacement_row_drop": False,
        "one_matrix_only": True,
        "formal_worker_count_before_authority": 0,
        "registered_performance_timing_count_before_authority": 0,
    }
    value["authority_sha256"] = digest(value)
    return value


def validate_authority(
        value: Mapping[str, Any], *, freeze_path: Path,
        target_manifest_path: Path, direct_binary_path: Path) -> None:
    unsigned = dict(value)
    observed = unsigned.pop("authority_sha256", None)
    if value.get("schema") != AUTHORITY_SCHEMA or observed != digest(unsigned):
        raise RuntimeError("Goal5817 authority seal differs")
    expected_files = {
        "freeze_file": file_record(freeze_path),
        "target_manifest_file": file_record(target_manifest_path),
        "direct_binary_file": file_record(direct_binary_path),
    }
    for key, expected in expected_files.items():
        if value.get(key) != expected:
            raise RuntimeError(f"Goal5817 authority file binding differs: {key}")
    required = {
        "status": "AUTHORIZED_FOR_ONE_CREATE_ONLY_GOAL5817_FORMAL_MATRIX",
        "owner_execution_authorized": True,
        "formal_worker_zero_authorized": True,
        "pod_gpu_timing_authorized": True,
        "unconditional_result_acceptance": True,
        "retry_replacement_row_drop": False,
        "one_matrix_only": True,
        "formal_worker_count_before_authority": 0,
        "registered_performance_timing_count_before_authority": 0,
    }
    for key, expected in required.items():
        if value.get(key) != expected:
            raise RuntimeError(f"Goal5817 authority field differs: {key}")
    directive = value.get("owner_directive_sha256")
    if not isinstance(directive, str) or len(directive) != 64:
        raise RuntimeError("Goal5817 owner directive identity differs")
