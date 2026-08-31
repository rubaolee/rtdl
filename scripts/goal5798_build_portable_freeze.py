#!/usr/bin/env python3
"""Build the append-only Goal5798 portable-environment successor freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "experiments" / "goal5798_premeasurement"
sys.path.insert(0, str(GOAL))
from compatibility import (
    PYOPTIX_COMMIT,
    PYOPTIX_REPOSITORY,
    PYOPTIX_TAG,
    PYOPTIX_TREE,
    frozen_registry,
)
from contract_runtime import digest, validate_freeze


HISTORY = ROOT / "history" / "internal_docs"
PREACTION = HISTORY / "goal5798_a1_environment_portability_preaction_20260823.json"
PREDECESSOR = HISTORY / "goal5798_s0_premeasurement_design_freeze_v4_20260823.json"
OUTPUT = HISTORY / "goal5798_a1_portable_premeasurement_freeze_v5_20260823.json"
OLD_B = "B_STOCK_CURRENT_PYOPTIX_9_1"
NEW_B = "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
    }


def replace_arm(row: dict[str, object]) -> dict[str, object]:
    result = json.loads(json.dumps(row))
    if result.get("arm") == OLD_B:
        result["arm"] = NEW_B
        result["worker_id"] = str(result["worker_id"]).replace(OLD_B, NEW_B)
    return result


def source_manifest(predecessor: dict[str, object]) -> list[dict[str, object]]:
    relative_paths = {str(row["path"]) for row in predecessor["source_manifest"]}
    relative_paths.add("experiments/goal5798_premeasurement/compatibility.py")
    rows = []
    for relative in sorted(relative_paths):
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha(path)})
    return rows


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    preaction = json.loads(PREACTION.read_text(encoding="utf-8"))
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    manifest = source_manifest(predecessor)
    performance = [replace_arm(row) for row in predecessor["performance_schedule"]]
    memory = [replace_arm(row) for row in predecessor["memory_schedule"]]
    arms = json.loads(json.dumps(predecessor["arms"]))
    pyoptix = arms.pop(OLD_B)
    pyoptix.update({
        "name": NEW_B,
        "baseline_kind": "python_host_plus_hand_written_cuda_cpp_device",
        "selection": "current NVIDIA PyOptiX source built without edits against the "
                     "newest frozen OptiX API supported by the actual driver",
        "optix_api_version": "SELECTED_BEFORE_TASK_FROM_FROZEN_REGISTRY",
        "pyoptix_repository_commit": PYOPTIX_COMMIT,
        "pyoptix_distribution_version": "9.1.0",
        "stock_wheel_claimed": False,
        "source_edit_count": 0,
        "timing_eligible_after_exact_stack_binding": True,
    })
    arms[NEW_B] = pyoptix
    result = {
        "schema": "rtdl.goal5798.portable_premeasurement_freeze.v5",
        "date": "2026-08-23",
        "status": "PORTABLE_SUCCESSOR_FROZEN__PHYSICAL_HOST_UNBOUND__EXECUTION_FORBIDDEN",
        "portability_preaction": pin(PREACTION),
        "supersedes_exact_host_freeze": pin(PREDECESSOR),
        "supersedes_exact_host_candidate": {
            "path": preaction["defect_admission"]["old_candidate"],
            "sha256": preaction["defect_admission"]["old_candidate_sha256"],
            "disposition": preaction["defect_admission"]["disposition"],
        },
        "authorization": dict(preaction["authorization"]),
        "scientific_question": (
            "On two fixed non-rendering OptiX tasks and the actual provided NVIDIA "
            "Linux host, what lifecycle-separated performance and memory cost does "
            "the public RTDL Callback-Protocol abstraction add relative to hand-written "
            "Direct CUDA/OptiX and current NVIDIA PyOptiX source using one identical, "
            "pre-result selected compatible OptiX API?"),
        "claim_ceiling": {
            "two_designed_tasks_only": True,
            "new_application_generalization": False,
            "usability_or_productivity": False,
            "owl_performance": False,
            "universal_performance": False,
            "descriptive_actual_host_and_selected_stack_only": True,
            "rt_core_claim_requires_observed_rt_capable_gpu": True,
            "stock_pyoptix_wheel": False,
            "current_nvidia_pyoptix_source": True,
        },
        "designated_host": {
            "gpu_model_allowlist": None,
            "gpu_model_denylist": None,
            "fixed_compute_capability": None,
            "fixed_vram_minimum": None,
            "fixed_driver_branch": None,
            "linux_x86_64_non_wsl_required": True,
            "visible_gpu_ordinal": 0,
            "physical_host_binding": None,
            "execution_admission": False,
            "status": "ANY_NVIDIA_HOST_WITH_A_FROZEN_SUPPORTED_OPTIX_STACK",
        },
        "compatible_stacks": frozen_registry(),
        "stack_selection": {
            "algorithm": "NEWEST_STACK_WITH_MINIMUM_DRIVER_LEQ_OBSERVED_DRIVER",
            "inputs": ["driver_version"],
            "result_dependent": False,
            "gpu_model_dependent": False,
            "performance_dependent": False,
            "fallback_after_selected_stack_failure": False,
        },
        "dependencies": {
            "pyoptix_repository": PYOPTIX_REPOSITORY,
            "pyoptix_tag": PYOPTIX_TAG,
            "pyoptix_commit": PYOPTIX_COMMIT,
            "pyoptix_tree": PYOPTIX_TREE,
            "pyoptix_source_edit_count": 0,
            "optix_api_version": "SELECTED_FROM_COMPATIBLE_STACKS",
            "optix_header_commit": "SELECTED_FROM_COMPATIBLE_STACKS",
            "python_major_minor": "3.12",
            "host_binary_and_native_build_timing_eligible": False,
            "exact_cuda_nvrtc_compiler_and_package_versions": (
                "BOUND_IN_CREATE_ONLY_HOST_RECEIPT_BEFORE_EXECUTION"),
        },
        "arms": arms,
        "source_manifest": manifest,
        "source_manifest_file_count": len(manifest),
        "source_manifest_sha256": digest(manifest),
        "workload_authority": predecessor["workload_authority"],
        "tasks": predecessor["tasks"],
        "matched_resource_budget": predecessor["matched_resource_budget"],
        "measurement_modes": predecessor["measurement_modes"],
        "phase_boundaries": predecessor["phase_boundaries"],
        "performance_schedule": performance,
        "performance_schedule_sha256": digest(performance),
        "memory_schedule": memory,
        "memory_schedule_sha256": digest(memory),
        "statistics": predecessor["statistics"],
        "correctness_and_failure_policy": predecessor["correctness_and_failure_policy"],
        "future_worker_receipt_required_fields": predecessor[
            "future_worker_receipt_required_fields"],
        "required_phase_keys": predecessor["required_phase_keys"],
        "timing_semantics": predecessor["timing_semantics"],
        "memory_semantics": predecessor["memory_semantics"],
        "no_substitution_rules": [
            "no GPU-model, compute-capability, VRAM, or preferred-driver host filter",
            "no stack choice from task, correctness, timing, memory, or output",
            "no fallback after the selected stack fails build, import, or function",
            "no cross-machine ratio",
            "no private RTDL provider, loader, PTX, SBT or pipeline escape",
            "no timing reuse from any predecessor",
        ],
        "later_execution_gate_prerequisites": [
            "bind actual host and deterministic selected stack before task materialization",
            "build A/B/D against the identical selected OptiX headers",
            "non-timed exact correctness and memory workers all pass before timing",
            "owner explicitly authorizes the exact created transaction",
        ],
        "implementation_status": {
            "workload_generator": "IMPLEMENTED_AND_FROZEN",
            "design_and_receipt_validator": "IMPLEMENTED",
            "phase_instrumented_workers": "IMPLEMENTED",
            "controller": "IMPLEMENTED",
            "physical_host_binding": "ABSENT",
            "worker_zero_ready": False,
        },
        "registered_performance_timing_count": 0,
        "gpu_execution_count": 0,
        "network_call_count": 0,
    }
    result["freeze_sha256"] = digest(result)
    validate_freeze(result)
    OUTPUT.write_bytes(json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"],
        "path": OUTPUT.relative_to(ROOT).as_posix(),
        "bytes": OUTPUT.stat().st_size,
        "file_sha256": sha(OUTPUT),
        "freeze_sha256": result["freeze_sha256"],
        "source_manifest_file_count": len(manifest),
        "performance_worker_count": len(performance),
        "memory_worker_count": len(memory),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
