"""Pure experiment contract for Goal5842.

This module deliberately imports neither RTDL nor a GPU package.  It owns the
pre-result schedule and validation rules used by the preregistration builder,
workers, controller, and independent recount.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

PREDECESSOR_PREREGISTRATION_SCHEMA = (
    "rtdl.goal5842.causal_admission_preregistration.v1"
)
PREREGISTRATION_SCHEMA = "rtdl.goal5842.causal_admission_preregistration.v2"
PREDECESSOR_PREREGISTRATION_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION.json"
)
PREDECESSOR_PREREGISTRATION_SHA256 = (
    "6f4cc3123e51d3a1d37193673fb943fca1610ab6536043c3cff774ed4d7f2536"
)
PREDECESSOR_PREREGISTRATION_FILE_SHA256 = (
    "1546e6977e3e7a6bfb43206973e98774af8fa666343c4d5b9f2bf5aa369a397b"
)
EXECUTION_AUTHORITY_SCHEMA = "rtdl.goal5842.execution_authority.v1"
WORKER_RECEIPT_SCHEMA = "rtdl.goal5842.causal_admission_worker.v1"
CONTROLLER_RESULT_SCHEMA = "rtdl.goal5842.causal_admission_controller.v1"
BASELINE_SUBWORKER_SCHEMA = "rtdl.goal5842.baseline_subworker.v1"
BASELINE_CONTROLLER_SCHEMA = "rtdl.goal5842.baseline_controller.v1"
GPU_IDENTITY_WITNESS_SCHEMA = "rtdl.goal5842.gpu_identity_witness.v1"
INDEPENDENT_RECOUNT_SCHEMA = "rtdl.goal5842.independent_recount.v1"
CROSS_GENERATION_AUTHORITY_SCHEMA = "rtdl.goal5842.cross_generation_authority.v1"

CHECK_ON = "CHECK_ON_COLD_PUBLIC_ADMISSION"
CHECK_OFF = "CHECK_OFF_COLD_UNCHECKED_CONSTRUCTION"
CAUSAL_ARMS = (CHECK_ON, CHECK_OFF)

RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"
SPHERE_TASK = "BUILTIN_SPHERE_ANY_HIT_COUNT_V1"
ADMISSION_TASKS = (RELATION_TASK, TRIANGLE_TASK, SPHERE_TASK)
BASELINE_TASKS = (RELATION_TASK, TRIANGLE_TASK)

DIRECT_ARM = "A_DIRECT_CUDA_OPTIX"
PYOPTIX_ARM = "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API"
RTDL_ARM = "D_RTDL_PUBLIC_CHECK_ON"
BASELINE_ARMS = (DIRECT_ARM, PYOPTIX_ARM, RTDL_ARM)

CAUSAL_BLOCKS = 18
BASELINE_BLOCKS = 18
STEADY_WARMUPS = 8
STEADY_REPETITIONS = 64
FIRST_MODE = "FIRST_COMPLETE_EXECUTION"
STEADY_MODE = "STEADY_COMPLETE_EXECUTION"
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_LOWER_INDEX = 249
BOOTSTRAP_UPPER_INDEX = 9_749
BOOTSTRAP_SEED_BASE = 58_420_000

ABBA = (CHECK_ON, CHECK_OFF, CHECK_OFF, CHECK_ON)
BAAB = (CHECK_OFF, CHECK_ON, CHECK_ON, CHECK_OFF)
BASELINE_PERMUTATIONS = (
    (DIRECT_ARM, PYOPTIX_ARM, RTDL_ARM),
    (DIRECT_ARM, RTDL_ARM, PYOPTIX_ARM),
    (PYOPTIX_ARM, DIRECT_ARM, RTDL_ARM),
    (PYOPTIX_ARM, RTDL_ARM, DIRECT_ARM),
    (RTDL_ARM, DIRECT_ARM, PYOPTIX_ARM),
    (RTDL_ARM, PYOPTIX_ARM, DIRECT_ARM),
)
CAUSAL_PHASE_BOUNDARIES = (
    "route_declaration_and_artifact_binding",
    "provider_projection_and_public_admission_or_unchecked_construction",
)
BASELINE_PHASE_BOUNDARIES = (
    "deterministic_input_materialization",
    "route_declaration_and_artifact_binding",
    "provider_projection_and_generic_family_admission",
    "runtime_target_and_toolchain_binding",
    "device_compile",
    "module_program_pipeline_sbt",
    "target_materialization",
    "native_prepare",
    "first_complete_execution",
    "steady_complete_execution",
    "close",
)
TASK_CONTRACTS = (
    {
        "task": RELATION_TASK,
        "input_sha256": "8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e",
        "full_oracle_sha256": "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77",
        "public_output_sha256": "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77",
        "primitive_count": 4_096,
        "query_count": 4_096,
        "three_arm_baseline_included": True,
    },
    {
        "task": TRIANGLE_TASK,
        "input_sha256": "d994f80418995342d0faa4bda84b42c2ef3604b2798de413a2813dd28dc039a7",
        "full_oracle_sha256": "24f4651b65f2abc93ffae0a8a9603c6eff9e9c6acdc24b65fb20937d6f416d93",
        "public_output_sha256": "2df49102543561c678ce39e05cc6c79ce92c0ea919ad45134d53d19bb67174ef",
        "primitive_count": 16_384,
        "query_count": 16_384,
        "three_arm_baseline_included": True,
    },
    {
        "task": SPHERE_TASK,
        "input_sha256": "66f66867b86440659a769580018b59078af71435444c9539c38986ecd74492cb",
        "full_oracle_sha256": "10f12038f6836614e72c78a707cfc4202f2566cd3aae7390a854c7fcc86e3329",
        "public_output_sha256": "10f12038f6836614e72c78a707cfc4202f2566cd3aae7390a854c7fcc86e3329",
        "primitive_count": 16_384,
        "query_count": 16_384,
        "three_arm_baseline_included": False,
    },
)
REQUIRED_SOURCE_PATHS = (
    "experiments/goal5798_premeasurement/direct_measurement.cpp",
    "experiments/goal5798_premeasurement/build_direct_measurement.sh",
    "experiments/goal5798_premeasurement/pyoptix_worker.py",
    "experiments/goal5798_premeasurement/workload.py",
    "experiments/goal5796_matched/direct_optix.cpp",
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5842_causal_admission/__init__.py",
    "experiments/goal5842_causal_admission/admission_worker.py",
    "experiments/goal5842_causal_admission/baseline_controller.py",
    "experiments/goal5842_causal_admission/baseline_worker.py",
    "experiments/goal5842_causal_admission/controller.py",
    "experiments/goal5842_causal_admission/contracts.py",
    "experiments/goal5842_causal_admission/runtime.py",
    "experiments/goal5842_causal_admission/tasks.py",
    "scripts/goal5842_bind_execution_authority.py",
    "scripts/goal5842_build_cross_generation_authority.py",
    "scripts/goal5842_build_preregistration.py",
    "scripts/goal5842_gpu_identity_witness.py",
    "scripts/goal5842_independent_recount.py",
    "scripts/goal5842_run_one_generation.py",
    "src/rtdsl/v4_callback_lifecycle.py",
    "src/rtdsl/v4_family_route_adapters.py",
    "src/rtdsl/v4_family_schema.py",
    "src/rtdsl/v4_generic_family_lifecycle.py",
    "src/rtdsl/v4_sphere_any_hit_count_family_route.py",
    "tests/goal5842_causal_admission_cost_test.py",
    "history/internal_docs/goal5842_causal_admission_cost_20260903/DESIGN.md",
    PREDECESSOR_PREREGISTRATION_PATH,
    (
        "history/internal_docs/goal5842_causal_admission_cost_20260903/"
        "PRE_WORKER_ZERO_REPAIR_01.md"
    ),
)


class Goal5842ContractError(ValueError):
    """Raised when preregistered Goal5842 evidence is structurally invalid."""


def preregistration_supersession() -> dict[str, object]:
    """Return the append-only pre-worker-zero repair chain for v2."""

    return {
        "predecessor_path": PREDECESSOR_PREREGISTRATION_PATH,
        "predecessor_schema": PREDECESSOR_PREREGISTRATION_SCHEMA,
        "predecessor_preregistration_sha256": (
            PREDECESSOR_PREREGISTRATION_SHA256
        ),
        "predecessor_file_sha256": PREDECESSOR_PREREGISTRATION_FILE_SHA256,
        "reason_code": (
            "PRE_WORKER_ZERO_VENV_LAUNCHER_SYMLINK_RESOLUTION_DEFECT"
        ),
        "failed_stage": "00_bind_execution_authority",
        "worker_zero_reached": False,
        "registered_timing_observation_count": 0,
        "gpu_execution_count": 0,
        "scientific_design_changed": False,
        "schedule_workload_statistics_changed": False,
        "repair_scope": "preserve_validated_virtualenv_python_entrypoint",
    }


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    block = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            block.update(chunk)
    return block.hexdigest()


def pin_file(root: Path, path: Path) -> dict[str, object]:
    resolved_root = root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise Goal5842ContractError(f"pin outside repository: {resolved}") from exc
    if not resolved.is_file():
        raise Goal5842ContractError(f"pin is not a file: {relative}")
    return {
        "path": relative.as_posix(),
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def verify_pin(root: Path, row: Mapping[str, object]) -> None:
    if set(row) != {"path", "bytes", "sha256"}:
        raise Goal5842ContractError("file pin has unexpected fields")
    relative = row["path"]
    if not isinstance(relative, str):
        raise Goal5842ContractError("file pin path must be a string")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise Goal5842ContractError(f"unsafe file pin: {relative}")
    target = root.resolve() / path
    if not target.is_file():
        raise Goal5842ContractError(f"pinned file missing: {relative}")
    if target.stat().st_size != row["bytes"]:
        raise Goal5842ContractError(f"pinned file byte drift: {relative}")
    if sha256_file(target) != row["sha256"]:
        raise Goal5842ContractError(f"pinned file digest drift: {relative}")


def build_causal_schedule() -> list[dict[str, object]]:
    schedule: list[dict[str, object]] = []
    sequence = 0
    for task_index, task in enumerate(ADMISSION_TASKS):
        for block in range(CAUSAL_BLOCKS):
            order = ABBA if (task_index + block) % 2 == 0 else BAAB
            seen: defaultdict[str, int] = defaultdict(int)
            for position, arm in enumerate(order):
                sample_index = 2 * block + seen[arm]
                seen[arm] += 1
                schedule.append(
                    {
                        "sequence_index": sequence,
                        "task": task,
                        "task_index": task_index,
                        "block": block,
                        "position": position,
                        "arm": arm,
                        "arm_sample_index": sample_index,
                        "worker_id": (
                            f"C{sequence:03d}__T{task_index}__B{block:02d}__"
                            f"P{position}__{arm}"
                        ),
                    }
                )
                sequence += 1
    return schedule


def build_baseline_schedule() -> list[dict[str, object]]:
    schedule: list[dict[str, object]] = []
    counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    sequence = 0
    for block in range(BASELINE_BLOCKS):
        task_order = (
            BASELINE_TASKS if block % 2 == 0 else tuple(reversed(BASELINE_TASKS))
        )
        for task_position, task in enumerate(task_order):
            permutation_index = (block + 2 * BASELINE_TASKS.index(task)) % 6
            for arm_position, arm in enumerate(
                BASELINE_PERMUTATIONS[permutation_index]
            ):
                key = (task, arm)
                sample_index = counts[key]
                counts[key] += 1
                schedule.append(
                    {
                        "sequence_index": sequence,
                        "block": block,
                        "task": task,
                        "task_position": task_position,
                        "arm": arm,
                        "arm_position": arm_position,
                        "permutation_index": permutation_index,
                        "arm_sample_index": sample_index,
                        "worker_id": (f"B{sequence:03d}__K{block:02d}__{task}__{arm}"),
                    }
                )
                sequence += 1
    return schedule


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Goal5842ContractError(message)


def validate_causal_schedule(schedule: object) -> None:
    _require(isinstance(schedule, list), "causal schedule must be a list")
    expected = build_causal_schedule()
    _require(
        schedule == expected, "causal schedule differs from the frozen ABBA design"
    )
    ids = [row["worker_id"] for row in schedule]
    _require(len(ids) == len(set(ids)), "causal worker ids are not unique")
    counts = Counter((row["task"], row["arm"]) for row in schedule)
    _require(
        set(counts.values()) == {CAUSAL_BLOCKS * 2}
        and len(counts) == len(ADMISSION_TASKS) * len(CAUSAL_ARMS),
        "causal schedule is imbalanced",
    )


def validate_baseline_schedule(schedule: object) -> None:
    _require(isinstance(schedule, list), "baseline schedule must be a list")
    expected = build_baseline_schedule()
    _require(schedule == expected, "baseline schedule differs from frozen permutations")
    ids = [row["worker_id"] for row in schedule]
    _require(len(ids) == len(set(ids)), "baseline worker ids are not unique")
    counts = Counter((row["task"], row["arm"]) for row in schedule)
    _require(
        set(counts.values()) == {BASELINE_BLOCKS}
        and len(counts) == len(BASELINE_TASKS) * len(BASELINE_ARMS),
        "baseline schedule is imbalanced",
    )


def validate_preregistration(value: object, root: Path, *, verify_files: bool) -> None:
    _require(isinstance(value, dict), "preregistration must be an object")
    prereg: dict[str, Any] = value
    seal = prereg.get("preregistration_sha256")
    unsealed = dict(prereg)
    unsealed.pop("preregistration_sha256", None)
    _require(
        isinstance(seal, str) and digest(unsealed) == seal,
        "preregistration seal mismatch",
    )
    _require(
        prereg.get("schema") == PREREGISTRATION_SCHEMA,
        "preregistration schema mismatch",
    )
    _require(
        prereg.get("supersession") == preregistration_supersession(),
        "preregistration supersession chain mismatch",
    )
    _require(
        prereg.get("status") == "FROZEN_BEFORE_TIMING", "preregistration is not frozen"
    )
    _require(
        prereg.get("registered_timing_observation_count") == 0,
        "pre-freeze timing exists",
    )
    _require(prereg.get("gpu_execution_count") == 0, "pre-freeze GPU execution exists")
    _require(
        prereg.get("admission_tasks") == list(ADMISSION_TASKS),
        "admission task set drift",
    )
    _require(
        prereg.get("baseline_tasks") == list(BASELINE_TASKS), "baseline task set drift"
    )
    _require(
        prereg.get("task_contracts") == [dict(row) for row in TASK_CONTRACTS],
        "task input/oracle contract drift",
    )
    _require(prereg.get("causal_arms") == list(CAUSAL_ARMS), "causal arm set drift")
    _require(
        prereg.get("baseline_arms") == list(BASELINE_ARMS), "baseline arm set drift"
    )
    _require(
        prereg.get("causal_phase_boundaries") == list(CAUSAL_PHASE_BOUNDARIES),
        "causal phase boundary drift",
    )
    _require(
        prereg.get("baseline_phase_boundaries") == list(BASELINE_PHASE_BOUNDARIES),
        "baseline phase boundary drift",
    )
    cold = prereg.get("cold_counterfactual_design")
    _require(isinstance(cold, dict), "cold counterfactual design missing")
    _require(
        cold.get("route_factory_first_call_in_both_arms") is True,
        "causal arms are not both cold",
    )
    _require(
        cold.get("pre_timing_public_admission") is False,
        "pre-timing admission would warm the causal experiment",
    )
    _require(
        cold.get("materialization_revalidation_remains_outside_causal_estimand")
        is True,
        "materialization revalidation boundary missing",
    )
    reference = prereg.get("post_estimand_reference_admission")
    _require(isinstance(reference, dict), "post-estimand reference missing")
    _require(
        reference.get("included_in_causal_estimand") is False
        and reference.get("performed_after_registered_interval_in_both_arms") is True
        and reference.get("cannot_warm_registered_timing") is True,
        "post-estimand reference timing boundary drift",
    )
    validate_causal_schedule(prereg.get("causal_schedule"))
    validate_baseline_schedule(prereg.get("baseline_schedule"))
    _require(
        prereg.get("causal_schedule_sha256") == digest(prereg["causal_schedule"]),
        "causal schedule seal mismatch",
    )
    _require(
        prereg.get("baseline_schedule_sha256") == digest(prereg["baseline_schedule"]),
        "baseline schedule seal mismatch",
    )
    statistics = prereg.get("statistics")
    _require(isinstance(statistics, dict), "statistics missing")
    _require(
        statistics.get("causal_block_count") == CAUSAL_BLOCKS,
        "causal block count drift",
    )
    _require(
        statistics.get("baseline_block_count") == BASELINE_BLOCKS,
        "baseline block count drift",
    )
    _require(statistics.get("steady_warmups") == STEADY_WARMUPS, "warmup count drift")
    _require(
        statistics.get("steady_repetitions") == STEADY_REPETITIONS,
        "repetition count drift",
    )
    _require(
        statistics.get("bootstrap_draws") == BOOTSTRAP_DRAWS, "bootstrap count drift"
    )
    _require(
        statistics.get("bootstrap_lower_index") == BOOTSTRAP_LOWER_INDEX
        and statistics.get("bootstrap_upper_index") == BOOTSTRAP_UPPER_INDEX
        and statistics.get("bootstrap_seed_base") == BOOTSTRAP_SEED_BASE,
        "bootstrap procedure drift",
    )
    _require(
        statistics.get("primary_summary")
        == (
            "median_of_provider_projection_and_admission_phase_block_deltas_"
            "absolute_nanoseconds"
        ),
        "primary causal statistic drift",
    )
    _require(
        statistics.get("ratio_to_near_zero_control_is_forbidden") is True,
        "unsafe causal ratio enabled",
    )
    _require(
        statistics.get("success_threshold") is None,
        "post-result success threshold forbidden",
    )
    identity = prereg.get("byte_identity_invariant")
    _require(isinstance(identity, dict), "byte identity invariant missing")
    for key in (
        "family_plan",
        "family_artifacts",
        "provider_projection",
        "generated_executable",
        "composed_ptx",
        "native_library",
        "input",
        "output",
    ):
        _require(
            identity.get(key) == "EXACT_SHA256_EQUAL",
            f"identity invariant missing: {key}",
        )
    ceiling = prereg.get("claim_ceiling")
    _require(isinstance(ceiling, dict), "claim ceiling missing")
    for key in (
        "checker_off_is_public_api",
        "checker_off_is_safe_for_users",
        "checker_off_is_supported_optimization",
        "admission_delta_explains_entire_setup_gap",
        "two_task_baseline_result_generalizes_to_all_rt",
        "sphere_has_direct_pyoptix_or_owl_performance_claim",
        "cross_generation_equivalence",
        "one_generation_is_goal5842_complete",
        "external_review_or_consensus",
    ):
        _require(ceiling.get(key) is False, f"claim ceiling widened: {key}")
    _require(
        ceiling.get("checker_off_is_experiment_only_counterfactual") is True
        and ceiling.get("materialization_still_revalidates_identity") is True,
        "counterfactual boundary drift",
    )
    hardware = prereg.get("hardware_design")
    _require(
        isinstance(hardware, dict)
        and hardware.get("minimum_distinct_gpu_architecture_generations") == 2
        and hardware.get("cross_machine_raw_time_ratio_forbidden") is True,
        "hardware evidence gate weakened",
    )
    pins = prereg.get("source_manifest")
    _require(isinstance(pins, list) and pins, "source manifest missing")
    _require(
        len({row.get("path") for row in pins}) == len(pins), "duplicate source pin"
    )
    _require(
        [row.get("path") for row in pins] == list(REQUIRED_SOURCE_PATHS),
        "required source manifest path set or order drift",
    )
    _require(
        prereg.get("source_manifest_sha256") == digest(pins),
        "source manifest seal mismatch",
    )
    if verify_files:
        for row in pins:
            verify_pin(root, row)


def load_preregistration(
    path: Path, root: Path, *, verify_files: bool
) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_preregistration(value, root, verify_files=verify_files)
    return value


__all__ = [
    "ADMISSION_TASKS",
    "BASELINE_ARMS",
    "BASELINE_BLOCKS",
    "BASELINE_CONTROLLER_SCHEMA",
    "BASELINE_PHASE_BOUNDARIES",
    "BASELINE_SUBWORKER_SCHEMA",
    "BASELINE_TASKS",
    "BOOTSTRAP_DRAWS",
    "BOOTSTRAP_LOWER_INDEX",
    "BOOTSTRAP_SEED_BASE",
    "BOOTSTRAP_UPPER_INDEX",
    "CAUSAL_ARMS",
    "CAUSAL_BLOCKS",
    "CAUSAL_PHASE_BOUNDARIES",
    "CHECK_OFF",
    "CHECK_ON",
    "CONTROLLER_RESULT_SCHEMA",
    "CROSS_GENERATION_AUTHORITY_SCHEMA",
    "DIRECT_ARM",
    "EXECUTION_AUTHORITY_SCHEMA",
    "FIRST_MODE",
    "GPU_IDENTITY_WITNESS_SCHEMA",
    "INDEPENDENT_RECOUNT_SCHEMA",
    "PREDECESSOR_PREREGISTRATION_FILE_SHA256",
    "PREDECESSOR_PREREGISTRATION_PATH",
    "PREDECESSOR_PREREGISTRATION_SCHEMA",
    "PREDECESSOR_PREREGISTRATION_SHA256",
    "PREREGISTRATION_SCHEMA",
    "PYOPTIX_ARM",
    "RELATION_TASK",
    "REQUIRED_SOURCE_PATHS",
    "RTDL_ARM",
    "SPHERE_TASK",
    "STEADY_MODE",
    "STEADY_REPETITIONS",
    "STEADY_WARMUPS",
    "TASK_CONTRACTS",
    "TRIANGLE_TASK",
    "WORKER_RECEIPT_SCHEMA",
    "Goal5842ContractError",
    "build_baseline_schedule",
    "build_causal_schedule",
    "canonical_bytes",
    "digest",
    "load_preregistration",
    "pin_file",
    "preregistration_supersession",
    "sha256_file",
    "validate_baseline_schedule",
    "validate_causal_schedule",
    "validate_preregistration",
    "verify_pin",
]
