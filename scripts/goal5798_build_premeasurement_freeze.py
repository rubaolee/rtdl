"""Build Goal5798's non-executing premeasurement design freeze."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from experiments.goal5798_premeasurement.contract_runtime import validate_freeze
from experiments.goal5798_premeasurement.workload import workload_authority


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
PREACTION = HISTORY / "goal5798_s0_premeasurement_design_preaction_20260823.json"
AMENDMENT = HISTORY / (
    "goal5798_s0_premeasurement_design_preaction_amendment_a1_20260823.json")
A2 = HISTORY / (
    "goal5798_s0_premeasurement_design_preaction_amendment_a2_20260823.json")
A3 = HISTORY / (
    "goal5798_s0_premeasurement_design_preaction_amendment_a3_20260823.json")
WORKLOAD = HISTORY / "goal5798_s0_matched_workload_authority_20260823.json"
PREDECESSOR = HISTORY / "goal5798_s0_premeasurement_design_freeze_v3_20260823.json"
OUTPUT = HISTORY / "goal5798_s0_premeasurement_design_freeze_v4_20260823.json"

ARMS = (
    "A_DIRECT_CUDA_OPTIX",
    "B_STOCK_CURRENT_PYOPTIX_9_1",
    "D_RTDL_PUBLIC",
)
TASKS = (
    "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1",
    "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
)
MODES = ("COLD_FRESH_PROCESS", "PREPARED_EXECUTION")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha_file(path),
    }


def source_paths() -> list[Path]:
    exact = [
        ROOT / "Makefile",
        ROOT / "pyproject.toml",
        ROOT / "experiments/goal5796_matched/build_direct.sh",
        ROOT / "experiments/goal5796_matched/direct_optix.cpp",
        ROOT / "experiments/goal5796_matched/independent_oracle.py",
        ROOT / "experiments/goal5796_matched/matched_device.cu",
        ROOT / "experiments/goal5796_matched/pyoptix_baseline.py",
        ROOT / "experiments/goal5796_matched/rtdl_baseline.py",
        ROOT / "experiments/goal5796_matched/semantic_spec.json",
        ROOT / "experiments/goal5798_premeasurement/contract_runtime.py",
        ROOT / "experiments/goal5798_premeasurement/workload.py",
    ]
    exact.extend(sorted((ROOT / "src/rtdsl").rglob("*.py")))
    exact.extend(sorted(path for path in (ROOT / "src/native/optix").rglob("*")
                        if path.is_file()))
    unique = {path.resolve(): path for path in exact}
    return sorted(unique.values(), key=lambda path: path.relative_to(ROOT).as_posix())


def build_performance_schedule(permutations: list[list[str]]) -> list[dict[str, object]]:
    schedule: list[dict[str, object]] = []
    row_counts: defaultdict[tuple[str, str, str], int] = defaultdict(int)
    sequence = 0
    for superblock in range(24):
        task_order = list(TASKS if superblock % 2 == 0 else reversed(TASKS))
        mode_order = list(MODES if (superblock // 2) % 2 == 0 else reversed(MODES))
        for task_position, task in enumerate(task_order):
            for mode_position, mode in enumerate(mode_order):
                permutation_index = (
                    superblock + 2 * TASKS.index(task) + 3 * MODES.index(mode)) % 6
                arm_order = permutations[permutation_index]
                for arm_position, arm in enumerate(arm_order):
                    key = (task, mode, arm)
                    sample = row_counts[key]
                    schedule.append({
                        "sequence_index": sequence,
                        "superblock": superblock,
                        "task": task,
                        "task_position": task_position,
                        "mode": mode,
                        "mode_position": mode_position,
                        "arm": arm,
                        "arm_position": arm_position,
                        "permutation_index": permutation_index,
                        "row_sample_index": sample,
                        "worker_id": (
                            f"P{sequence:03d}__B{superblock:02d}__{task}__{mode}__{arm}"),
                    })
                    row_counts[key] += 1
                    sequence += 1
    if Counter(row_counts.values()) != {24: len(TASKS) * len(MODES) * len(ARMS)}:
        raise RuntimeError(f"performance schedule imbalance: {row_counts}")
    return schedule


def build_memory_schedule(permutations: list[list[str]]) -> list[dict[str, object]]:
    schedule: list[dict[str, object]] = []
    row_counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    sequence = 0
    for block in range(5):
        task_order = list(TASKS if block % 2 == 0 else reversed(TASKS))
        for task_position, task in enumerate(task_order):
            arm_order = permutations[(block + 2 * TASKS.index(task)) % 6]
            for arm_position, arm in enumerate(arm_order):
                key = (task, arm)
                sample = row_counts[key]
                schedule.append({
                    "sequence_index": sequence,
                    "memory_block": block,
                    "task": task,
                    "task_position": task_position,
                    "mode": "MEMORY_SEPARATE_NON_TIMED",
                    "arm": arm,
                    "arm_position": arm_position,
                    "row_sample_index": sample,
                    "timing_eligible": False,
                    "worker_id": f"M{sequence:02d}__{task}__{arm}",
                })
                row_counts[key] += 1
                sequence += 1
    if Counter(row_counts.values()) != {5: len(TASKS) * len(ARMS)}:
        raise RuntimeError(f"memory schedule imbalance: {row_counts}")
    return schedule


def main() -> None:
    preaction = json.loads(PREACTION.read_text(encoding="utf-8"))
    amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    a2 = json.loads(A2.read_text(encoding="utf-8"))
    a3 = json.loads(A3.read_text(encoding="utf-8"))
    if amendment["preaction"] != pin(PREACTION):
        raise RuntimeError("A1 does not pin the exact preaction")
    if amendment["old_value"]["vram_bytes_minimum"] != preaction[
            "designated_host"]["vram_bytes_minimum"]:
        raise RuntimeError("A1 old VRAM value mismatch")
    if amendment["new_value"]["vram_bytes_minimum"] != 20_000_000_000:
        raise RuntimeError("A1 new VRAM value mismatch")
    if a2["predecessors"] != {"preaction": pin(PREACTION), "a1": pin(AMENDMENT)}:
        raise RuntimeError("A2 predecessor pins mismatch")
    if a2["controlling_formula"]["formal_relation_value"] != 8194:
        raise RuntimeError("A2 relation raw-event capacity mismatch")
    if a3["predecessor_a2"] != pin(A2):
        raise RuntimeError("A3 predecessor pin mismatch")
    if a3["controlling_metric"]["name"] != "gpu_process_sampled_peak_bytes":
        raise RuntimeError("A3 sampled-peak metric mismatch")
    workload_file = json.loads(WORKLOAD.read_text(encoding="utf-8"))
    rebuilt_workload = workload_authority()
    if workload_file != rebuilt_workload:
        raise RuntimeError("workload authority does not rebuild exactly")
    for arm in ("A_DIRECT_CUDA_OPTIX", "B_STOCK_CURRENT_PYOPTIX_9_1",
                "D_RTDL_PUBLIC"):
        arm_spec = preaction["exact_arms"][arm]
        source = ROOT / arm_spec["source_path"]
        if sha_file(source) != arm_spec["source_sha256"]:
            raise RuntimeError(f"frozen arm source drift: {arm}")
    device = preaction["exact_arms"]["B_STOCK_CURRENT_PYOPTIX_9_1"]
    if sha_file(ROOT / device["device_source_path"]) != device[
            "device_source_sha256"]:
        raise RuntimeError("matched device source drift")

    manifest = [pin(path) for path in source_paths()]
    manifest_sha = digest(manifest)
    permutations = preaction["run_order"]["arm_permutations"]
    performance_schedule = build_performance_schedule(permutations)
    memory_schedule = build_memory_schedule(permutations)
    measurement_modes = json.loads(json.dumps(preaction["measurement_modes"]))
    memory_metrics = measurement_modes["MEMORY_SEPARATE_NON_TIMED"]["primary_metrics"]
    memory_metrics[memory_metrics.index("gpu_process_peak_bytes")] = (
        "gpu_process_sampled_peak_bytes")
    result: dict[str, object] = {
        "schema": "rtdl.goal5798.premeasurement_freeze.v4",
        "date": "2026-08-23",
        "status": (
            "LOCAL_DESIGN_FROZEN__PHYSICAL_HOST_AND_MEASUREMENT_HARNESS_UNBOUND__"
            "EXECUTION_FORBIDDEN"),
        "preaction": pin(PREACTION),
        "preaction_amendment_a1": pin(AMENDMENT),
        "preaction_amendment_a2": pin(A2),
        "preaction_amendment_a3": pin(A3),
        "supersedes_pre_amendment_freeze": pin(PREDECESSOR),
        "authorization": dict(preaction["authorization"]),
        "scientific_question": (
            "On two fixed non-rendering OptiX tasks, what lifecycle-separated "
            "performance and memory cost does the public RTDL Callback-Protocol "
            "abstraction add relative to hand-written Direct CUDA/OptiX and stock "
            "current-source PyOptiX 9.1 on the same RTX 4000 Ada host?"),
        "claim_ceiling": {
            "two_designed_tasks_only": True,
            "new_application_generalization": False,
            "usability_or_productivity": False,
            "owl_performance": False,
            "universal_performance": False,
            "stock_pyoptix_9_1_required_for_B_label": True,
            "cross_version_optix90_compatibility_timing_eligible": False,
            "descriptive_exact_host_and_phase_only": True,
        },
        "designated_host": {
            **preaction["designated_host"],
            "vram_bytes_minimum": amendment["new_value"]["vram_bytes_minimum"],
            "physical_host_binding": None,
            "execution_admission": False,
        },
        "dependencies": {
            "pyoptix_distribution_version": "9.1.0",
            "pyoptix_commit": "3144f224c0fd18733925faf3d8fb82c7376b8dcf",
            "pyoptix_tree": "0bf0ec24efb4a43f129aee25dd265aa8149374e3",
            "optix_api_version": "9.1.0",
            "optix_header_commit": "f1f6dd803f3159992d248178f6e09421c6eb8b6d",
            "python_major_minor": "3.12",
            "host_binary_and_native_build_timing_eligible": False,
            "exact_cuda_nvrtc_compiler_and_package_versions": (
                "MUST_BE_BOUND_IN_CREATE_ONLY_HOST_RECEIPT_BEFORE_EXECUTION_GATE"),
        },
        "arms": preaction["exact_arms"],
        "source_manifest": manifest,
        "source_manifest_file_count": len(manifest),
        "source_manifest_sha256": manifest_sha,
        "workload_authority": pin(WORKLOAD) | {
            "authority_sha256": workload_file["authority_sha256"],
        },
        "tasks": preaction["tasks"],
        "matched_resource_budget": {
            "relation_raw_event_capacity_formula": a2["controlling_formula"][
                "all_arms"],
            "relation_raw_event_capacity": 8194,
            "relation_semantic_capacity": 4096,
            "relation_device_overflow_flag_required": True,
            "identical_for_A_B_D": True,
            "triangle_event_capacity": 16384,
        },
        "measurement_modes": measurement_modes,
        "phase_boundaries": preaction["phase_boundaries"],
        "performance_schedule": performance_schedule,
        "performance_schedule_sha256": digest(performance_schedule),
        "memory_schedule": memory_schedule,
        "memory_schedule_sha256": digest(memory_schedule),
        "statistics": {
            "primary_estimator": preaction["statistics"]["primary_estimator"],
            "primary_comparisons": preaction["statistics"]["primary_comparisons"],
            "ratio_greater_than_one_favors_rtdl": True,
            "bootstrap_draw_count": 10000,
            "bootstrap_indices": [249, 9749],
            "bootstrap_seed_base": 57980000,
            "row_index_order": [
                f"{task}__{mode}__{baseline}_OVER_D"
                for task in TASKS for mode in MODES
                for baseline in ("A", "B")
            ],
            "success_ratio_threshold": None,
            "descriptive_no_p_value": True,
            "unfavorable_and_mixed_results_retained": True,
        },
        "correctness_and_failure_policy": preaction["failure_policy"],
        "future_worker_receipt_required_fields": [
            "schema", "worker_id", "arm", "task", "mode", "row_sample_index",
            "source_manifest_sha256", "workload_authority_sha256", "host_binding_sha256",
            "correctness", "timing_eligible", "durations_ns", "memory", "raw_output_sha256",
            "receipt_sha256",
        ],
        "required_phase_keys": [
            "input_materialization_ns", "protocol_validation_and_codegen_ns",
            "device_compile_ns", "module_program_pipeline_sbt_ns",
            "gas_and_static_prepare_ns", "common_preparation_total_ns",
            "complete_execute_ns", "close_ns", "controller_process_wall_ns",
        ],
        "timing_semantics": {
            "clock": "CLOCK_MONOTONIC_RAW_OR_PERF_COUNTER_NS_WITH_IMPLEMENTATION_RECORDED",
            "gpu_sync_before_duration_end": True,
            "complete_execute_includes_output_readback_postprocess_and_validation": True,
            "prepared_primary_sample": "median_of_64_complete_execute_ns_after_8_warmups",
            "cold_primary_sample": "controller_process_wall_ns",
            "process_sample_is_statistical_unit": True,
            "within_process_repetitions_are_not_independent_samples": True,
        },
        "memory_semantics": {
            "separate_from_timing_workers": True,
            "host_peak": "RUSAGE_SELF_MAXRSS_NORMALIZED_TO_BYTES",
            "gpu_sampled_peak": "NVML_PROCESS_USED_MEMORY_POLLED_EVERY_10_MS",
            "gpu_sampled_peak_ceiling": (
                "LOWER_BOUND_ON_ANY_TRANSIENT_SHORTER_THAN_POLL_INTERVAL"),
            "gpu_steady": "NVML_PROCESS_USED_MEMORY_AT_PREPARED_POST_WARMUP_BARRIER",
            "memory_failure_makes_goal5798_incomplete": True,
        },
        "no_substitution_rules": [
            "no lx1 or GTX1070 performance row",
            "no OptiX-9.0 compatibility arm relabelled stock PyOptiX 9.1",
            "no legacy or mock PyOptiX",
            "no old V2/V4 cohort",
            "no cross-machine ratio",
            "no OWL timing while C remains analysed-not-implemented",
            "no private RTDL provider, loader, PTX, SBT or pipeline escape",
            "no timing reuse from Goal5795, Goal5796 or Goal5797",
        ],
        "later_execution_gate_prerequisites": [
            "phase-instrumented A/B/D measurement harness implemented and exact-byte frozen",
            "create-only exact RTX 4000 Ada host/environment binding",
            "stock PyOptiX 9.1 source-clean build and import on that host",
            "non-timed A/B/D exact correctness on both Goal5798 workloads on that host",
            "independent source/schedule/receipt validator PASS",
            "single external Checkpoint-A ruling explicitly authorizes worker zero",
            "owner explicitly authorizes the exact host transaction",
        ],
        "implementation_status": {
            "workload_generator": "IMPLEMENTED_AND_FROZEN",
            "design_and_receipt_validator": "IMPLEMENTED_AND_FROZEN",
            "phase_instrumented_workers": "NOT_YET_IMPLEMENTED",
            "controller": "NOT_YET_IMPLEMENTED",
            "physical_host_binding": "ABSENT",
            "worker_zero_ready": False,
        },
        "registered_performance_timing_count": 0,
        "gpu_execution_count": 0,
        "network_call_count": 0,
    }
    result["freeze_sha256"] = digest(result)
    validate_freeze(result)
    OUTPUT.write_bytes(json.dumps(
        result, indent=2, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"],
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "file_sha256": sha_file(OUTPUT),
        "freeze_sha256": result["freeze_sha256"],
        "source_manifest_file_count": len(manifest),
        "performance_worker_count": len(performance_schedule),
        "memory_worker_count": len(memory_schedule),
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
