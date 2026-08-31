#!/usr/bin/env python3
"""Run the ten-worker Goal5811 Home causal diagnostic matrix."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

from scripts import goal5811_home_rtdl_session_causal_diagnostic as probe


SCHEMA = "rtdl.goal5811.home_rtdl_session_causal_matrix.v3"
STATUS = "COMPLETE__HOME_PASCAL_NONFORMAL_CAUSAL_MATRIX"


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _file_row(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": _sha(resolved),
    }


def _read_worker(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Goal5811 worker output is not an object")
    unsigned = dict(value)
    seal = unsigned.pop("diagnostic_sha256", None)
    if seal != _digest(unsigned):
        raise RuntimeError("Goal5811 worker seal differs")
    scope = value.get("scope")
    if value.get("schema") != probe.SCHEMA or value.get("status") != probe.STATUS \
            or value.get("formal_worker_count") != 0 \
            or value.get("registered_performance_timing_count") != 0 \
            or not isinstance(scope, Mapping) \
            or scope.get("threshold_or_pass_fail_gate_present") is not False \
            or scope.get("claim_authorized") is not False \
            or scope.get("a4500_relabeling_authorized") is not False \
            or value.get("cuda", {}).get("gpu_name") \
            != "NVIDIA GeForce GTX 1070" \
            or value.get("cuda", {}).get("compute_capability") != [6, 1]:
        raise RuntimeError("Goal5811 worker scope differs")
    if tuple(value.get("phase_times_absolute", {}).get("phase_order", ())) \
            != probe.PHASES:
        raise RuntimeError("Goal5811 phase order differs")
    bridge = value.get("actual_loaded_driver_bridge")
    if not isinstance(bridge, list) \
            or not any("libcuda.so" in str(row.get("path")) for row in bridge) \
            or not any("libnvoptix.so" in str(row.get("path")) for row in bridge):
        raise RuntimeError("Goal5811 actual loaded driver bridge differs")
    for task in ("relation", "triangle"):
        row = value.get("applications", {}).get(task)
        if not isinstance(row, Mapping) \
                or row.get("exact_oracle_passed") is not True \
                or row.get("device_status_ok") is not True:
            raise RuntimeError(f"Goal5811 exact/status evidence differs: {task}")
    return value


def _events(
    value: Mapping[str, Any], *, category: str, phase: str,
) -> list[Mapping[str, Any]]:
    rows = value["selected_call_trace"]["events"]
    return [
        row for row in rows
        if row["category"] == category and row["phase"] == phase
    ]


def _validate_causal_structure(value: Mapping[str, Any]) -> None:
    treatment = value["treatment"]
    native_owned = treatment == "native_primary_after_python_cuinit"
    context_preplaced = treatment in {
        "primary_context_preplaced",
        "primary_context_and_sealed_dso_preplaced",
    }
    dso_preplaced = treatment in {
        "sealed_dso_preplaced",
        "primary_context_and_sealed_dso_preplaced",
    }
    accounting = value["causal_accounting"]
    if accounting.get("native_provider_owned_readiness_bypass_active") \
            is not native_owned \
            or accounting.get("native_provider_owned_readiness_is_product_api") \
            is not False \
            or accounting.get(
                "causal_result_must_use_total_through_second_exact_output") \
            is not True \
            or accounting.get(
                "native_provider_owned_treatment_retains_exact_native_cuda_optix_work") \
            is not True:
        raise RuntimeError("Goal5811 causal-treatment declaration differs")
    expected_counts = {
        ("cuda_primary_context_readiness", "causal_preplacement"):
            int(context_preplaced),
        ("sealed_native_dso_acquisition", "causal_preplacement"):
            int(dso_preplaced),
        ("cuda_primary_context_readiness", "first_session_admission"): 1,
        ("sealed_native_dso_acquisition", "first_session_admission"): 1,
        ("native_producer_descriptor_verification",
         "first_session_admission"): 1,
        ("native_producer_descriptor_verification",
         "second_app_prepare"): 1,
    }
    for (category, phase), expected in expected_counts.items():
        observed = _events(value, category=category, phase=phase)
        if len(observed) != expected \
                or any(row["outcome"] != "RETURNED" for row in observed):
            raise RuntimeError({
                "Goal5811_causal_event_count_differs": [category, phase],
                "expected": expected,
                "observed": observed,
            })
    for phase in ("load_relation", "load_triangle"):
        for category in (
                "trust_slot_admission", "artifact_authority_verification"):
            observed = _events(value, category=category, phase=phase)
            if len(observed) != 1 or observed[0]["outcome"] != "RETURNED":
                raise RuntimeError({
                    "Goal5811_trust_or_artifact_event_differs": [
                        category, phase],
                    "observed": observed,
                })
    observed_multiset = Counter(
        (str(row["category"]), str(row["phase"]), str(row["outcome"]))
        for row in value["selected_call_trace"]["events"])
    expected_multiset = Counter({
        (category, phase, "RETURNED"): count
        for (category, phase), count in expected_counts.items()
    })
    expected_multiset.update({
        ("trust_slot_admission", "load_relation", "RETURNED"): 1,
        ("artifact_authority_verification", "load_relation", "RETURNED"): 1,
        ("trust_slot_admission", "load_triangle", "RETURNED"): 1,
        ("artifact_authority_verification", "load_triangle", "RETURNED"): 1,
    })
    if observed_multiset != expected_multiset:
        raise RuntimeError({
            "Goal5811_complete_selected_trace_multiset_differs": True,
            "expected": sorted((list(key), count)
                               for key, count in expected_multiset.items()),
            "observed": sorted((list(key), count)
                               for key, count in observed_multiset.items()),
        })
    state = value["provider_state"]
    before = state["before_preplacement"]
    after = state["after_preplacement_before_public_session"]
    final = state["after_public_session_and_close"]
    if before["cuda_primary_readiness_published"] is not False \
            or before["target_native_image_cached"] is not False \
            or after["cuda_primary_readiness_published"] is not context_preplaced \
            or after["target_native_image_cached"] is not dso_preplaced \
            or final["cuda_primary_readiness_published"] is not (not native_owned) \
            or final["target_native_image_cached"] is not True:
        raise RuntimeError("Goal5811 causal provider-state transition differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--expected-target-manifest-sha256", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output_root.exists() or args.output.exists():
        raise RuntimeError("Goal5811 controller output already exists")
    args.output_root.mkdir(parents=True)
    worker_path = args.worker.resolve(strict=True)
    target_path = args.target_manifest.resolve(strict=True)
    if _sha(target_path) != args.expected_target_manifest_sha256:
        raise RuntimeError("Goal5811 target manifest SHA-256 differs")

    schedule: list[tuple[str, str]] = []
    for first_app, treatments in (
        ("relation", probe.TREATMENTS),
        ("triangle", tuple(reversed(probe.TREATMENTS))),
    ):
        schedule.extend((first_app, treatment) for treatment in treatments)

    journal: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for index, (first_app, treatment) in enumerate(schedule):
        stem = f"worker_{index:02d}_{first_app}_first_{treatment}"
        output = args.output_root / f"{stem}.json"
        cache = args.output_root / f"{stem}_cache"
        stdout = args.output_root / f"{stem}.stdout"
        stderr = args.output_root / f"{stem}.stderr"
        command = [
            sys.executable, "-B", str(worker_path),
            "--treatment", treatment,
            "--target-manifest", str(target_path),
            "--expected-target-manifest-sha256",
            args.expected_target_manifest_sha256,
            "--first-app", first_app,
            "--cache-root", str(cache),
            "--output", str(output),
        ]
        process = subprocess.run(
            command, text=True, capture_output=True, check=False)
        stdout.write_text(process.stdout, encoding="utf-8")
        stderr.write_text(process.stderr, encoding="utf-8")
        row: dict[str, Any] = {
            "worker_index": index,
            "first_app": first_app,
            "treatment": treatment,
            "returncode": process.returncode,
            "stdout": _file_row(stdout),
            "stderr": _file_row(stderr),
        }
        journal.append(row)
        if process.returncode != 0:
            raise RuntimeError({"Goal5811_worker_failed": row})
        value = _read_worker(output)
        if value["treatment"] != treatment \
                or value["app_order"][0] != first_app:
            raise RuntimeError("Goal5811 worker condition differs")
        _validate_causal_structure(value)
        row["output"] = _file_row(output)
        row["process_pid"] = value["process_pid"]
        results.append(value)

    if len({row["process_pid"] for row in journal}) != len(schedule):
        raise RuntimeError("Goal5811 workers did not use fresh processes")
    if len({_canonical(row["actual_loaded_driver_bridge"])
            for row in results}) != 1:
        raise RuntimeError("Goal5811 workers used different driver bridges")
    condition_rows = {
        f"{row['app_order'][0]}_first/{row['treatment']}": {
            "process_pid": row["process_pid"],
            "two_artifact_load_phase_wall_ns": sum(
                int(row["phase_times_absolute"]["phases"][phase][
                    "duration_ns"])
                for phase in ("load_relation", "load_triangle")),
            "selected_trust_and_artifact_call_wall_sum_ns": sum(
                int(event["duration_ns"])
                for event in row["selected_call_trace"]["events"]
                if event["category"] in {
                    "trust_slot_admission",
                    "artifact_authority_verification",
                }),
            "causal_preplacement_wall_ns": row["causal_accounting"][
                "causal_preplacement_wall_ns"],
            "public_first_session_admission_wall_ns": row[
                "causal_accounting"]["public_first_session_admission_wall_ns"],
            "first_app_prepare_wall_ns": row["phase_times_absolute"][
                "phases"]["first_app_prepare"]["duration_ns"],
            "preplacement_start_through_public_session_end_wall_ns": row[
                "causal_accounting"][
                    "preplacement_start_through_public_session_end_wall_ns"],
            "preplacement_start_through_second_exact_output_end_wall_ns": (
                int(row["phase_times_absolute"]["phases"][
                    "second_app_first_exact_execute"]["end_perf_counter_ns"])
                - int(row["phase_times_absolute"]["phases"][
                    "causal_preplacement"]["start_perf_counter_ns"])),
            "preplacement_start_through_first_app_prepare_end_wall_ns": (
                int(row["phase_times_absolute"]["phases"][
                    "first_app_prepare"]["end_perf_counter_ns"])
                - int(row["phase_times_absolute"]["phases"][
                    "causal_preplacement"]["start_perf_counter_ns"])),
            "overall_run_wall_ns": row["causal_accounting"][
                "overall_run_wall_ns"],
            "descriptive_only": True,
        }
        for row in results
    }
    body = {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "diagnostic_only": True,
            "home_pascal_only": True,
            "formal_evidence": False,
            "paper_evidence": False,
            "claim_authorized": False,
            "threshold_or_pass_fail_gate_present": False,
            "a4500_relabeling_authorized": False,
            "all_ten_structurally_valid_results_retained": True,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
        },
        "design": {
            "treatments": list(probe.TREATMENTS),
            "first_app_orders": ["relation", "triangle"],
            "four_treatment_factorial_worker_count": 8,
            "native_owned_readiness_worker_count": 2,
            "total_worker_count": len(schedule),
            "fresh_process_per_condition": True,
            "fresh_cache_root_per_condition": True,
            "triangle_schedule_reverses_relation_schedule": True,
            "preplacement_plus_public_session_wall_always_reported": True,
            "three_preplacement_treatments_shift_without_erasure": True,
            "native_owned_treatment_removes_python_readiness_but_retains_native_cuda_optix_initialization":
                True,
            "causal_decision_uses_total_through_second_exact_output": True,
            "native_owned_readiness_is_diagnostic_bypass_not_product_api": True,
        },
        "inputs": {
            "controller": _file_row(Path(__file__)),
            "worker": _file_row(worker_path),
            "target_manifest": _file_row(target_path),
            "python_executable": _file_row(Path(sys.executable)),
        },
        "conditions": condition_rows,
        "journal": journal,
        "unique_process_pid_count": len(schedule),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    result = {**body, "matrix_sha256": _digest(body)}
    with args.output.open("xb") as handle:
        handle.write(_canonical(result) + b"\n")
    print(json.dumps({
        "status": STATUS,
        "worker_count": len(schedule),
        "unique_process_pid_count": len(schedule),
        "matrix_sha256": result["matrix_sha256"],
        "output": str(args.output.resolve(strict=True)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
