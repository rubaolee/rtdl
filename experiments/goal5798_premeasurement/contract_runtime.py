"""Fail-closed runtime validation for the Goal5798 design freeze.

The module validates design and future evidence bytes.  It never executes a
GPU workload and exposes no API that can authorize worker zero.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


ARMS = (
    "A_DIRECT_CUDA_OPTIX",
    "B_STOCK_CURRENT_PYOPTIX_9_1",
    "D_RTDL_PUBLIC",
)
PORTABLE_ARMS = (
    "A_DIRECT_CUDA_OPTIX",
    "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API",
    "D_RTDL_PUBLIC",
)
TASKS = (
    "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1",
    "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
)
TIMED_MODES = ("COLD_FRESH_PROCESS", "PREPARED_EXECUTION")
MEMORY_MODE = "MEMORY_SEPARATE_NON_TIMED"


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_freeze(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_freeze(value)
    return value


def validate_freeze(value: dict[str, Any]) -> None:
    schema = value.get("schema")
    require(schema in {
        "rtdl.goal5798.premeasurement_freeze.v4",
        "rtdl.goal5798.portable_premeasurement_freeze.v5",
    }, "freeze schema mismatch")
    seal = value.get("freeze_sha256")
    require(isinstance(seal, str) and len(seal) == 64, "freeze seal missing")
    unsealed = dict(value)
    del unsealed["freeze_sha256"]
    require(digest(unsealed) == seal, "freeze seal mismatch")
    authorization = value["authorization"]
    require(all(flag is False for flag in authorization.values()),
            "design freeze contains an authorization")
    host = value["designated_host"]
    if schema == "rtdl.goal5798.premeasurement_freeze.v4":
        require(host["gpu_model"] == "NVIDIA RTX 4000 Ada Generation",
                "wrong designated GPU")
        require(host["compute_capability"] == "8.9", "wrong compute capability")
        require(host["driver_branch_minimum"] == 590, "wrong driver floor")
        arms = ARMS
    else:
        try:
            from .compatibility import frozen_registry
        except ImportError:
            from compatibility import frozen_registry

        require(host["gpu_model_allowlist"] is None, "portable freeze has GPU allowlist")
        require(host["gpu_model_denylist"] is None, "portable freeze has GPU denylist")
        require(host["fixed_compute_capability"] is None,
                "portable freeze fixes compute capability")
        require(host["fixed_vram_minimum"] is None,
                "portable freeze fixes VRAM")
        require(host["fixed_driver_branch"] is None,
                "portable freeze fixes driver branch")
        require(value["compatible_stacks"] == frozen_registry(),
                "portable compatible-stack registry drift")
        require(value["stack_selection"]["result_dependent"] is False,
                "portable stack selection is result-dependent")
        require(value["stack_selection"]["gpu_model_dependent"] is False,
                "portable stack selection is GPU-model-dependent")
        arms = PORTABLE_ARMS
    require(host["physical_host_binding"] is None, "unexpected host binding")
    require(host["execution_admission"] is False, "host admitted prematurely")

    schedule = value["performance_schedule"]
    require(len(schedule) == 288, "performance schedule must have 288 workers")
    ids = [row["worker_id"] for row in schedule]
    require(len(ids) == len(set(ids)), "duplicate performance worker id")
    expected_rows = Counter(
        (task, mode, arm) for task in TASKS for mode in TIMED_MODES for arm in arms)
    actual_rows = Counter((row["task"], row["mode"], row["arm"]) for row in schedule)
    require(set(actual_rows) == set(expected_rows), "performance row set mismatch")
    require(all(count == 24 for count in actual_rows.values()),
            "each performance row must have 24 workers")
    for key in actual_rows:
        samples = sorted(row["row_sample_index"] for row in schedule if (
            row["task"], row["mode"], row["arm"]) == key)
        require(samples == list(range(24)), f"sample index mismatch for {key}")
        positions = Counter(row["arm_position"] for row in schedule if (
            row["task"], row["mode"], row["arm"]) == key)
        require(positions == {0: 8, 1: 8, 2: 8},
                f"arm-position imbalance for {key}: {positions}")

    memory = value["memory_schedule"]
    require(len(memory) == 30, "memory schedule must have 30 workers")
    memory_rows = Counter((row["task"], row["arm"]) for row in memory)
    require(set(memory_rows) == {
        (task, arm) for task in TASKS for arm in arms},
        "memory row set mismatch")
    require(all(count == 5 for count in memory_rows.values()),
            "each memory row must have five workers")
    require(all(row["mode"] == MEMORY_MODE and row["timing_eligible"] is False
                for row in memory), "memory worker marked timing-eligible")

    statistics = value["statistics"]
    require(statistics["success_ratio_threshold"] is None,
            "post-hoc success threshold present")
    require(statistics["bootstrap_draw_count"] == 10000,
            "bootstrap draw count drift")
    require(statistics["bootstrap_indices"] == [249, 9749],
            "bootstrap indices drift")
    require(value["registered_performance_timing_count"] == 0,
            "design freeze contains timing")
    budget = value["matched_resource_budget"]
    require(budget["relation_raw_event_capacity"] == 8194,
            "relation raw-event budget drift")
    require(budget["identical_for_A_B_D"] is True,
            "relation raw-event budget is not matched")
    memory_metrics = value["measurement_modes"]["MEMORY_SEPARATE_NON_TIMED"][
        "primary_metrics"]
    require("gpu_process_sampled_peak_bytes" in memory_metrics,
            "GPU sampled-peak ceiling not controlling")
    require("gpu_process_peak_bytes" not in memory_metrics,
            "unqualified GPU peak metric remains")


def validate_host_binding(
    freeze: dict[str, Any], binding: dict[str, Any] | None,
) -> list[str]:
    """Return fail-closed reasons; an empty list means structurally admissible.

    This does not authorize execution.  A separately reviewed owner closure is
    still required even after an exact binding is structurally admissible.
    """
    reasons: list[str] = []
    if binding is None:
        return ["HOST_BINDING_ABSENT"]
    schema = freeze.get("schema")
    required = {
        "schema", "hostname", "gpu_model", "gpu_uuid", "compute_capability",
        "vram_bytes", "driver_version", "driver_branch", "kernel", "os_release",
        "wsl", "cuda_toolkit", "nvrtc", "python", "gxx", "optix_api_version",
        "optix_header_commit", "pyoptix_commit", "source_manifest_sha256",
        "other_compute_process_count", "binding_sha256",
    }
    if schema == "rtdl.goal5798.portable_premeasurement_freeze.v5":
        required |= {
            "visible_gpu_ordinal", "visible_gpu_count", "selected_stack",
            "pyoptix_distribution_name", "pyoptix_distribution_version",
            "stack_selection_inputs", "stack_selection_before_task_materialization",
        }
    if set(binding) != required:
        reasons.append("HOST_BINDING_SCHEMA_KEYS_MISMATCH")
        return reasons
    unsealed = dict(binding)
    seal = unsealed.pop("binding_sha256")
    if digest(unsealed) != seal:
        reasons.append("HOST_BINDING_SEAL_MISMATCH")
    host = freeze["designated_host"]
    if schema == "rtdl.goal5798.premeasurement_freeze.v4":
        if binding["gpu_model"] != host["gpu_model"]:
            reasons.append("GPU_MODEL_MISMATCH")
        if binding["compute_capability"] != host["compute_capability"]:
            reasons.append("COMPUTE_CAPABILITY_MISMATCH")
        if type(binding["vram_bytes"]) is not int or binding["vram_bytes"] < host[
                "vram_bytes_minimum"]:
            reasons.append("VRAM_BELOW_MINIMUM")
        if type(binding["driver_branch"]) is not int or binding["driver_branch"] < host[
                "driver_branch_minimum"]:
            reasons.append("DRIVER_BRANCH_BELOW_MINIMUM")
    else:
        try:
            from .compatibility import (
                PYOPTIX_COMMIT,
                select_compatible_stack,
                validate_selected_stack,
            )
        except ImportError:
            from compatibility import (
                PYOPTIX_COMMIT,
                select_compatible_stack,
                validate_selected_stack,
            )

        if not isinstance(binding["gpu_model"], str) or not binding["gpu_model"]:
            reasons.append("GPU_MODEL_NOT_RECORDED")
        capability = str(binding["compute_capability"]).split(".")
        if len(capability) != 2 or any(not part.isdigit() for part in capability):
            reasons.append("COMPUTE_CAPABILITY_INVALID")
        if type(binding["vram_bytes"]) is not int or binding["vram_bytes"] <= 0:
            reasons.append("VRAM_NOT_RECORDED")
        if type(binding["driver_branch"]) is not int:
            reasons.append("DRIVER_BRANCH_INVALID")
        reasons.extend(validate_selected_stack(
            binding["driver_version"], binding["selected_stack"]))
        try:
            expected_stack = select_compatible_stack(binding["driver_version"])
        except (RuntimeError, ValueError):
            expected_stack = None
        if expected_stack is not None:
            if binding["optix_api_version"] != expected_stack["optix_api_version"]:
                reasons.append("OPTIX_API_VERSION_MISMATCH")
            if binding["optix_header_commit"] != expected_stack["optix_header_commit"]:
                reasons.append("OPTIX_HEADER_COMMIT_MISMATCH")
            if binding["pyoptix_distribution_name"] != expected_stack[
                    "pyoptix_distribution_name"]:
                reasons.append("PYOPTIX_DISTRIBUTION_NAME_MISMATCH")
            if binding["pyoptix_distribution_version"] != expected_stack[
                    "pyoptix_distribution_version"]:
                reasons.append("PYOPTIX_DISTRIBUTION_VERSION_MISMATCH")
        if binding["pyoptix_commit"] != PYOPTIX_COMMIT:
            reasons.append("PYOPTIX_COMMIT_MISMATCH")
        if binding["visible_gpu_ordinal"] != 0:
            reasons.append("VISIBLE_GPU_ORDINAL_NOT_ZERO")
        if type(binding["visible_gpu_count"]) is not int or binding[
                "visible_gpu_count"] < 1:
            reasons.append("VISIBLE_GPU_COUNT_INVALID")
        if binding["stack_selection_inputs"] != ["driver_version"]:
            reasons.append("STACK_SELECTION_INPUTS_INVALID")
        if binding["stack_selection_before_task_materialization"] is not True:
            reasons.append("STACK_SELECTION_ORDER_UNPROVEN")
    if binding["wsl"] is not False:
        reasons.append("WSL_FORBIDDEN")
    if schema == "rtdl.goal5798.premeasurement_freeze.v4":
        if binding["optix_api_version"] != "9.1.0":
            reasons.append("OPTIX_API_VERSION_MISMATCH")
        if binding["optix_header_commit"] != freeze["dependencies"][
                "optix_header_commit"]:
            reasons.append("OPTIX_HEADER_COMMIT_MISMATCH")
        if binding["pyoptix_commit"] != freeze["dependencies"]["pyoptix_commit"]:
            reasons.append("PYOPTIX_COMMIT_MISMATCH")
    if binding["source_manifest_sha256"] != freeze["source_manifest_sha256"]:
        reasons.append("SOURCE_MANIFEST_MISMATCH")
    if binding["other_compute_process_count"] != 0:
        reasons.append("OTHER_GPU_PROCESS_PRESENT")
    return reasons


def validate_future_worker_receipt(
    freeze: dict[str, Any], receipt: dict[str, Any],
) -> list[str]:
    """Validate a future receipt without granting permission to create it."""
    reasons: list[str] = []
    schedule = {
        row["worker_id"]: row
        for row in freeze["performance_schedule"] + freeze["memory_schedule"]
    }
    worker_id = receipt.get("worker_id")
    planned = schedule.get(worker_id)
    if planned is None:
        return ["WORKER_NOT_IN_FROZEN_SCHEDULE"]
    for key in ("arm", "task", "mode", "row_sample_index"):
        if receipt.get(key) != planned.get(key):
            reasons.append(f"SCHEDULE_{key.upper()}_MISMATCH")
    if receipt.get("source_manifest_sha256") != freeze["source_manifest_sha256"]:
        reasons.append("WORKER_SOURCE_MANIFEST_MISMATCH")
    if receipt.get("workload_authority_sha256") != freeze[
            "workload_authority"]["authority_sha256"]:
        reasons.append("WORKLOAD_AUTHORITY_MISMATCH")
    correctness = receipt.get("correctness")
    if not isinstance(correctness, dict) or correctness.get("oracle_exact") is not True:
        reasons.append("CORRECTNESS_NOT_EXACT")
    mode = planned["mode"]
    if mode == MEMORY_MODE:
        if receipt.get("timing_eligible") is not False:
            reasons.append("MEMORY_RECEIPT_TIMING_ELIGIBLE")
    else:
        if receipt.get("timing_eligible") is not True:
            reasons.append("TIMED_RECEIPT_NOT_ELIGIBLE")
        durations = receipt.get("durations_ns")
        if not isinstance(durations, dict) or any(
                type(item) is not int or item < 0 for item in durations.values()):
            reasons.append("DURATION_SCHEMA_INVALID")
    return reasons
