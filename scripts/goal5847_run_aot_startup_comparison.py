#!/usr/bin/env python3
"""Run the preregistered Goal5847 AOT-vs-precompiled comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

from experiments.goal5798_premeasurement.workload import relation_workload
from experiments.goal5847_aot_startup.contracts import (
    ARMS,
    PYOPTIX_ARM,
    PYOPTIX_COMMIT,
    PYOPTIX_TREE,
    RELATION_TASK,
    RTDL_ARM,
    digest,
    expected_schedule,
)

ROOT = Path(__file__).resolve().parents[1]
BLOCKS = 8
WARMUPS = 16
REPETITIONS = 128
PRIMARY_MEDIAN_RATIO_LIMIT = 0.50
PRIMARY_WORST_RATIO_LIMIT = 0.75
POST_IMPORT_MEDIAN_RATIO_LIMIT = 3.0
POST_IMPORT_WORST_RATIO_LIMIT = 4.0
STEADY_RATIO_LIMIT = 0.20
RTDL_STEADY_REFERENCE_NS = 366_340
RTDL_STEADY_REGRESSION_LIMIT = 1.25


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _sealed_json(path: Path, seal_field: str, label: str) -> dict[str, object]:
    value = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Goal5847 {label} must be an object")
    body = dict(value)
    observed = body.pop(seal_field, None)
    if observed != digest(body):
        raise RuntimeError(f"Goal5847 {label} seal differs")
    return value


def _validate_preregistration(
    path: Path,
    args: argparse.Namespace,
    candidate: dict[str, object],
) -> dict[str, object]:
    value = _sealed_json(path, "preregistration_sha256", "preregistration")
    design = value.get("design")
    gates = value.get("pass_gates")
    bindings = value.get("frozen_bindings")
    candidate_rows = candidate.get("rows")
    candidate_sha = _sha256_file(args.candidate_manifest.resolve(strict=True))
    ptx_sha = _sha256_file(args.precompiled_ptx.resolve(strict=True))
    receipt_path = args.pyoptix_build_receipt.resolve(strict=True)
    from experiments.goal5844_compact_execution.provenance import (
        validate_pyoptix_build_receipt,
    )

    receipt = validate_pyoptix_build_receipt(receipt_path)
    workload = relation_workload()
    expected = tuple(tuple(row) for row in workload["expected_rows"])
    expected_task = {
        "id": RELATION_TASK,
        "indexed_count": 4096,
        "query_count": 4096,
        "canonical_row_count": 4096,
        "input_sha256": digest(
            {
                "indexed": workload["indexed"],
                "sources": workload["sources"],
                "minimum_overlap": workload["minimum_overlap"],
                "capacity": workload["capacity"],
            }
        ),
        "output_sha256": digest(expected),
        "output_contract": "canonical_u32_relation_rows",
    }
    expected_required_facts = {
        "runtime_compiler_attempt_count_before_and_after_zero": True,
        "nvrtc_mapping_absent": True,
        "compiler_modules_absent": True,
        "actual_optix_launch_count_per_execution": 2,
        "full_generic_family_identity_match": True,
        "exact_output_required": True,
        "application_specific_native_logic_added": False,
        "prepared_steady_regression_forbidden": True,
        "optional_batch_oracle_disabled_in_timed_path": True,
        "diagnostic_execution_occurs_after_steady_samples": True,
    }
    expected_comparison_boundary = {
        "both_arms_consume_precompiled_device_programs": True,
        "rtdl_arm_verifies_signed_artifact_authority_and_provider": True,
        "pyoptix_validation_mode": "OFF",
        "pyoptix_harness_calls_source_compiler": False,
        "pyoptix_dependency_stack_may_map_nvrtc": True,
        "primary_includes_interpreter_and_dependency_import": True,
        "secondary_excludes_implementation_import": True,
        "git_and_hardware_instrumentation_excluded_from_primary": True,
        "exact_result_validation_included_in_primary_endpoint": True,
        "steady_result_validation_outside_timed_action_for_both_arms": True,
        "storage_page_cache_state_not_controlled": True,
        "block_device_cold_io_claimed": False,
        "test_only_signing_not_production_key_custody": True,
    }
    expected_claim_boundary = {
        "internal_engineering_evidence_only": True,
        "public_or_manuscript_claim_authorized": False,
        "external_review_complete": False,
        "cross_hardware_generalization_authorized": False,
        "arbitrary_workload_claim_authorized": False,
        "production_signing_claim_authorized": False,
    }
    if not isinstance(design, dict) or not isinstance(gates, dict) \
            or not isinstance(bindings, dict) \
            or not isinstance(candidate_rows, dict) \
            or set(candidate_rows) != {"relation", "triangle"} \
            or not all(
                isinstance(candidate_rows.get(label), dict)
                for label in ("relation", "triangle")
            ) \
            or value.get("schema") \
                != "rtdl.goal5847.aot_startup_preregistration.v1" \
            or value.get("status") != "FROZEN_BEFORE_FORMAL_GPU_TRANSACTION" \
            or value.get("implementation_source_commit") \
                != args.expected_source_commit \
            or value.get("implementation_source_tree") \
                != _git("rev-parse", "HEAD^{tree}") \
            or value.get("task") != expected_task \
            or value.get("arms") != list(ARMS) \
            or design != {
                "blocks": BLOCKS,
                "balanced_alternating_order": True,
                "fresh_process_per_arm_per_block": True,
                "warmups_per_worker": WARMUPS,
                "samples_per_worker": REPETITIONS,
                "samples_per_arm": BLOCKS * REPETITIONS,
                "sample_discard_count": 0,
                "primary_estimand": "parent_pre_spawn_to_first_correct_result_ns",
                "secondary_estimand": "implementation_import_end_to_first_correct_result_ns",
                "steady_estimand": "complete_same_contract_execution_ns",
            } \
            or gates != {
                "all_workers_and_exact_oracles_pass": True,
                "all_registered_samples_retained": True,
                "primary_median_within_block_ratio_at_most": (
                    PRIMARY_MEDIAN_RATIO_LIMIT
                ),
                "primary_worst_block_ratio_at_most": (
                    PRIMARY_WORST_RATIO_LIMIT
                ),
                "post_import_median_within_block_ratio_at_most": (
                    POST_IMPORT_MEDIAN_RATIO_LIMIT
                ),
                "post_import_worst_block_ratio_at_most": (
                    POST_IMPORT_WORST_RATIO_LIMIT
                ),
                "pooled_steady_rtdl_to_pyoptix_ratio_at_most": (
                    STEADY_RATIO_LIMIT
                ),
                "goal5845_rtdl_steady_reference_ns": RTDL_STEADY_REFERENCE_NS,
                "pooled_rtdl_steady_regression_at_most": (
                    RTDL_STEADY_REGRESSION_LIMIT
                ),
            } \
            or bindings.get("candidate_manifest_sha256") != candidate_sha \
            or bindings.get("candidate_manifest_seal") \
                != candidate.get("manifest_sha256") \
            or bindings.get("native_library_sha256") \
                != candidate.get("native_sha256") \
            or bindings.get("relation_artifact_sha256") \
                != candidate_rows["relation"].get("artifact_sha256") \
            or bindings.get("triangle_artifact_sha256") \
                != candidate_rows["triangle"].get("artifact_sha256") \
            or bindings.get("precompiled_ptx_sha256") != ptx_sha \
            or bindings.get("pyoptix_build_receipt_sha256") \
                != _sha256_file(receipt_path) \
            or bindings.get("pyoptix_build_receipt_internal_seal") \
                != receipt["receipt_sha256"] \
            or bindings.get("pyoptix_commit") != PYOPTIX_COMMIT \
            or bindings.get("pyoptix_tree") != PYOPTIX_TREE \
            or value.get("required_rtdl_facts") != expected_required_facts \
            or value.get("comparison_boundary") \
                != expected_comparison_boundary \
            or value.get("claim_boundary") != expected_claim_boundary \
            or candidate.get("optix_sdk") != args.optix_sdk \
            or candidate.get("compute_capability") != [
                int(item) for item in args.compute_capability.split(".")
            ]:
        raise RuntimeError("Goal5847 execution differs from frozen design")
    return value


def _outside_repository(path: Path) -> Path:
    candidate = path.expanduser().absolute()
    try:
        candidate.relative_to(ROOT.resolve(strict=True))
    except ValueError:
        return candidate
    raise RuntimeError("Goal5847 formal output must remain outside Git")


def _validate_samples(value: object, expected_count: int, label: str) -> list[int]:
    fields = {
        "sample_count", "samples_ns", "minimum_ns", "median_ns", "maximum_ns",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise RuntimeError(f"Goal5847 {label} timing schema differs")
    samples = value.get("samples_ns")
    if not isinstance(samples, list) \
            or len(samples) != expected_count \
            or value.get("sample_count") != expected_count \
            or any(type(item) is not int or item <= 0 for item in samples) \
            or value.get("minimum_ns") != min(samples) \
            or value.get("median_ns") != int(statistics.median(samples)) \
            or value.get("maximum_ns") != max(samples):
        raise RuntimeError(f"Goal5847 {label} timing values differ")
    return [int(item) for item in samples]


def _validate_worker(
    path: Path,
    *,
    arm: str,
    block: int,
    source_commit: str,
    source_tree: str,
    hardware: dict[str, object] | None,
    candidate: dict[str, object],
    precompiled_ptx_sha256: str,
    pyoptix_build_receipt: dict[str, object],
    pyoptix_build_receipt_file_sha256: str,
) -> tuple[dict[str, object], dict[str, object]]:
    value = _sealed_json(path, "result_sha256", "worker")
    exact = {
        "schema": "rtdl.goal5847.aot_startup.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "arm": arm,
        "block": block,
        "task": RELATION_TASK,
        "query_count": 4096,
        "row_count": 4096,
        "warmups": WARMUPS,
        "repetitions": REPETITIONS,
    }
    if any(value.get(field) != expected for field, expected in exact.items()) \
            or value.get("claim_boundary") != {
                "internal_engineering_evidence_only": True,
                "public_or_manuscript_claim_authorized": False,
                "external_review_complete": False,
            }:
        raise RuntimeError("Goal5847 worker exact fields differ")
    observed_hardware = value.get("hardware")
    if not isinstance(observed_hardware, dict) \
            or set(observed_hardware) != {
                "gpu_name",
                "gpu_uuid",
                "driver_version",
                "memory_mib",
                "compute_capability",
            } \
            or not all(
                isinstance(observed_hardware.get(field), str)
                and bool(observed_hardware[field])
                for field in (
                    "gpu_name",
                    "gpu_uuid",
                    "driver_version",
                    "compute_capability",
                )
            ) \
            or type(observed_hardware.get("memory_mib")) is not int \
            or observed_hardware["memory_mib"] <= 0 \
            or hardware is not None and observed_hardware != hardware:
        raise RuntimeError("Goal5847 worker hardware differs")
    measurements = value.get("measurements")
    if not isinstance(measurements, dict):
        raise TypeError("Goal5847 worker measurements are absent")
    process_ns = measurements.get("process_spawn_to_correct_result_ns")
    post_import_ns = measurements.get("post_import_to_correct_result_ns")
    phases = measurements.get("phases_ns")
    identity = measurements.get("identity")
    evidence = measurements.get("evidence")
    if type(process_ns) is not int or process_ns <= 0 \
            or type(post_import_ns) is not int or post_import_ns <= 0 \
            or process_ns <= post_import_ns \
            or not all(isinstance(item, dict)
                       for item in (phases, identity, evidence)):
        raise RuntimeError("Goal5847 worker phase structure differs")
    if any(type(item) is not int or item <= 0 for item in phases.values()) \
            or post_import_ns < sum(
                item
                for name, item in phases.items()
                if name != "implementation_import"
            ):
        raise RuntimeError("Goal5847 worker phase timing differs")
    _validate_samples(
        measurements.get("steady_complete_execution"),
        REPETITIONS,
        f"{arm}.steady",
    )
    expected_output = digest(tuple(
        tuple(row) for row in relation_workload()["expected_rows"]
    ))
    if evidence.get("output_sha256") != expected_output \
            or evidence.get("row_count") != 4096:
        raise RuntimeError("Goal5847 worker output evidence differs")
    if arm == RTDL_ARM:
        relation = candidate["rows"]["relation"]
        if set(phases) != {
            "implementation_import",
            "deterministic_input_materialization",
            "signed_deployment_install",
            "provider_initialization_start",
            "artifact_authority_load",
            "provider_bind_and_initialization_join",
            "deploy_static_input",
            "deploy_dynamic_input",
            "native_prepare",
            "first_complete_execution",
        } \
                or evidence.get("runtime_compiler_attempt_count_before") != 0 \
                or evidence.get("runtime_compiler_attempt_count_after") != 0 \
                or evidence.get("runtime_compiler_modules") != [] \
                or evidence.get("nvrtc_mappings") != [] \
                or evidence.get("full_generic_family_identity_matched") is not True \
                or identity.get("artifact_sha256") \
                    != relation["artifact_sha256"] \
                or identity.get("authority_sha256") \
                    != relation["authority_sha256"] \
                or identity.get("native_library_sha256") \
                    != candidate["native_sha256"] \
                or identity.get("family_executable_identity_sha256") \
                    != relation["family_executable_identity_sha256"]:
            raise RuntimeError("Goal5847 RTDL AOT evidence differs")
        receipt = evidence.get("diagnostic_traversal_receipt")
        if not isinstance(receipt, dict) \
                or receipt.get("successful_launch_count") != 2 \
                or receipt.get("raygen_invocation_count") != 8192:
            raise RuntimeError("Goal5847 RTDL traversal receipt differs")
    else:
        source = identity.get("pyoptix_repository")
        if set(phases) != {
            "implementation_import",
            "deterministic_input_materialization",
            "precompiled_ptx_load",
            "cuda_optix_context",
            "module_program_pipeline_sbt",
            "native_prepare",
            "first_complete_execution",
        } \
                or not isinstance(source, dict) \
                or source.get("commit") != PYOPTIX_COMMIT \
                or source.get("tree") != PYOPTIX_TREE \
                or source.get("clean") is not True \
                or identity.get("precompiled_ptx_sha256") \
                    != precompiled_ptx_sha256 \
                or identity.get("pyoptix_build_receipt_file_sha256") \
                    != pyoptix_build_receipt_file_sha256 \
                or identity.get("pyoptix_build_receipt_internal_seal") \
                    != pyoptix_build_receipt["receipt_sha256"] \
                or identity.get("pyoptix_distribution") \
                    != pyoptix_build_receipt["installed"][
                        "distribution_name"
                    ] \
                or identity.get("pyoptix_distribution_version") \
                    != pyoptix_build_receipt["installed"][
                        "distribution_version"
                    ] \
                or not isinstance(identity.get("loaded_extension"), dict) \
                or identity["loaded_extension"].get("sha256") \
                    != pyoptix_build_receipt["installed"][
                        "loaded_extension"
                    ]["sha256"] \
                or evidence.get("device_status") != 0 \
                or evidence.get("device_overflow") != 0 \
                or evidence.get("raw_event_count") != 8192 \
                or evidence.get(
                    "precompiled_ptx_means_harness_did_not_compile_source"
                ) is not True \
                or evidence.get("stack_wide_no_runtime_compiler_claimed") \
                    is not False:
            raise RuntimeError("Goal5847 PyOptix AOT evidence differs")
    return value, observed_hardware


def _median(values: list[int]) -> int:
    return int(statistics.median(values))


def _write_create(path: Path, value: dict[str, object]) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(
                json.dumps(value, indent=2, sort_keys=True).encode("utf-8")
                + b"\n"
            )
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--precompiled-ptx", type=Path, required=True)
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    source_commit = _git("rev-parse", "HEAD")
    source_tree = _git("rev-parse", "HEAD^{tree}")
    if source_commit != args.expected_source_commit \
            or _git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("Goal5847 controller requires exact clean source")
    output_root = _outside_repository(args.output_root)
    if output_root.exists() or output_root.is_symlink():
        raise FileExistsError(output_root)
    output_root.mkdir(parents=True)
    candidate = _sealed_json(
        args.candidate_manifest, "manifest_sha256", "candidate manifest"
    )
    if candidate.get("source_commit") != source_commit:
        raise RuntimeError("Goal5847 candidate source differs")
    preregistration = _validate_preregistration(
        args.preregistration, args, candidate
    )
    from experiments.goal5844_compact_execution.provenance import (
        validate_pyoptix_build_receipt,
    )
    pyoptix_build_receipt = validate_pyoptix_build_receipt(
        args.pyoptix_build_receipt.resolve(strict=True)
    )
    pyoptix_build_receipt_file_sha256 = _sha256_file(
        args.pyoptix_build_receipt.resolve(strict=True)
    )
    ptx_sha = _sha256_file(args.precompiled_ptx.resolve(strict=True))
    schedule = expected_schedule(BLOCKS)
    workers = []
    hardware = None
    environment_base = dict(os.environ)
    environment_base["PYTHONPATH"] = (
        str(ROOT) + os.pathsep + str(ROOT / "src") + os.pathsep
        + environment_base.get("PYTHONPATH", "")
    )
    for block, position, arm in schedule:
        output = output_root / f"block-{block:02d}-position-{position}-{arm}.json"
        stdout_path = output.with_suffix(".stdout")
        stderr_path = output.with_suffix(".stderr")
        command = [
            str(args.python.resolve(strict=True)),
            "-m",
            "experiments.goal5847_aot_startup.worker",
            "--arm", arm,
            "--block", str(block),
            "--expected-source-commit", source_commit,
            "--candidate-manifest", str(args.candidate_manifest.resolve(strict=True)),
            "--precompiled-ptx", str(args.precompiled_ptx.resolve(strict=True)),
            "--pyoptix-source", str(args.pyoptix_source.resolve(strict=True)),
            "--pyoptix-build-receipt",
            str(args.pyoptix_build_receipt.resolve(strict=True)),
            "--pyoptix-distribution", args.pyoptix_distribution,
            "--optix-sdk", args.optix_sdk,
            "--compute-capability", args.compute_capability,
            "--warmups", str(WARMUPS),
            "--repetitions", str(REPETITIONS),
            "--output", str(output),
        ]
        environment = dict(environment_base)
        environment["GOAL5847_CONTROLLER_START_NS"] = str(
            time.perf_counter_ns()
        )
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        if completed.returncode:
            raise RuntimeError(
                f"Goal5847 worker failed: block={block} arm={arm}; "
                f"see {stderr_path}"
            )
        worker, observed_hardware = _validate_worker(
            output,
            arm=arm,
            block=block,
            source_commit=source_commit,
            source_tree=source_tree,
            hardware=hardware,
            candidate=candidate,
            precompiled_ptx_sha256=ptx_sha,
            pyoptix_build_receipt=pyoptix_build_receipt,
            pyoptix_build_receipt_file_sha256=(
                pyoptix_build_receipt_file_sha256
            ),
        )
        hardware = observed_hardware
        workers.append({
            "block": block,
            "position": position,
            "arm": arm,
            "path": output.name,
            "sha256": _sha256_file(output),
            "result_sha256": worker["result_sha256"],
        })

    worker_values = {
        (row["block"], row["arm"]): _sealed_json(
            output_root / row["path"], "result_sha256", "worker recount"
        )
        for row in workers
    }
    primary_ratios = []
    post_import_ratios = []
    block_rows = []
    steady: dict[str, list[int]] = {arm: [] for arm in ARMS}
    for block in range(BLOCKS):
        rtdl = worker_values[(block, RTDL_ARM)]["measurements"]
        pyoptix = worker_values[(block, PYOPTIX_ARM)]["measurements"]
        rtdl_primary = int(rtdl["process_spawn_to_correct_result_ns"])
        pyoptix_primary = int(pyoptix["process_spawn_to_correct_result_ns"])
        rtdl_post = int(rtdl["post_import_to_correct_result_ns"])
        pyoptix_post = int(pyoptix["post_import_to_correct_result_ns"])
        primary_ratio = rtdl_primary / pyoptix_primary
        post_ratio = rtdl_post / pyoptix_post
        primary_ratios.append(primary_ratio)
        post_import_ratios.append(post_ratio)
        block_rows.append({
            "block": block,
            "first_arm": schedule[2 * block][2],
            "rtdl_process_spawn_to_correct_result_ns": rtdl_primary,
            "pyoptix_process_spawn_to_correct_result_ns": pyoptix_primary,
            "primary_rtdl_to_pyoptix_ratio": primary_ratio,
            "rtdl_post_import_to_correct_result_ns": rtdl_post,
            "pyoptix_post_import_to_correct_result_ns": pyoptix_post,
            "post_import_rtdl_to_pyoptix_ratio": post_ratio,
        })
        for arm, measurement in ((RTDL_ARM, rtdl), (PYOPTIX_ARM, pyoptix)):
            steady[arm].extend(
                measurement["steady_complete_execution"]["samples_ns"]
            )
    primary_median = statistics.median(primary_ratios)
    primary_worst = max(primary_ratios)
    post_median = statistics.median(post_import_ratios)
    post_worst = max(post_import_ratios)
    steady_medians = {arm: _median(values) for arm, values in steady.items()}
    steady_ratio = steady_medians[RTDL_ARM] / steady_medians[PYOPTIX_ARM]
    steady_regression = steady_medians[RTDL_ARM] / RTDL_STEADY_REFERENCE_NS
    gates = {
        "worker_count_exact": len(workers) == 2 * BLOCKS,
        "all_registered_samples_retained": all(
            len(steady[arm]) == BLOCKS * REPETITIONS for arm in ARMS
        ),
        "primary_median_ratio_pass": (
            primary_median <= PRIMARY_MEDIAN_RATIO_LIMIT
        ),
        "primary_worst_ratio_pass": primary_worst <= PRIMARY_WORST_RATIO_LIMIT,
        "post_import_median_ratio_pass": (
            post_median <= POST_IMPORT_MEDIAN_RATIO_LIMIT
        ),
        "post_import_worst_ratio_pass": (
            post_worst <= POST_IMPORT_WORST_RATIO_LIMIT
        ),
        "steady_ratio_pass": steady_ratio <= STEADY_RATIO_LIMIT,
        "rtdl_steady_regression_pass": (
            steady_regression <= RTDL_STEADY_REGRESSION_LIMIT
        ),
    }
    passed = all(gates.values())
    result: dict[str, object] = {
        "schema": "rtdl.goal5847.aot_startup.controller.v1",
        "status": (
            "PASS__GOAL5847_PREREGISTERED_AOT_PERFORMANCE_GATES"
            if passed else
            "FAIL__GOAL5847_PREREGISTERED_AOT_PERFORMANCE_GATES"
        ),
        "source_commit": source_commit,
        "source_tree": source_tree,
        "preregistration": {
            "path": str(args.preregistration.resolve(strict=True)),
            "sha256": _sha256_file(args.preregistration.resolve(strict=True)),
            "preregistration_sha256": preregistration["preregistration_sha256"],
        },
        "candidate_manifest_sha256": _sha256_file(
            args.candidate_manifest.resolve(strict=True)
        ),
        "precompiled_ptx_sha256": ptx_sha,
        "hardware": hardware,
        "design": {
            "blocks": BLOCKS,
            "warmups_per_worker": WARMUPS,
            "samples_per_worker": REPETITIONS,
            "samples_per_arm": BLOCKS * REPETITIONS,
            "discarded_samples": 0,
            "schedule": [list(row) for row in schedule],
        },
        "workers": workers,
        "block_comparisons": block_rows,
        "summary": {
            "median_within_block_primary_ratio": primary_median,
            "worst_block_primary_ratio": primary_worst,
            "median_within_block_post_import_ratio": post_median,
            "worst_block_post_import_ratio": post_worst,
            "pooled_steady_median_ns": steady_medians,
            "pooled_steady_rtdl_to_pyoptix_ratio": steady_ratio,
            "rtdl_steady_vs_goal5845_reference_ratio": steady_regression,
        },
        "gates": gates,
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
            "cross_hardware_generalization_authorized": False,
            "arbitrary_workload_claim_authorized": False,
        },
    }
    result["result_sha256"] = digest(result)
    _write_create(output_root / "controller.json", result)
    print(json.dumps(result, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
