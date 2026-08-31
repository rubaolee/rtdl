#!/usr/bin/env python3
"""Launch the RTDL and PyOptiX two-app pilots in two fresh processes.

The controller reports descriptive, unregistered ratios only.  It defines no
threshold, pass/fail gate, confidence interval, or paper claim.  Each arm runs
once in its own child process and receives the same target manifest and task
order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Mapping

from scripts.goal5809_execution_identity import (
    admit_execution_identity,
    controlled_python_command,
    controlled_python_environment,
    verify_loaded_modules,
)
from scripts.goal5809_runtime_session_two_app_pilot import (
    TASK_KEYS,
    _admit_target,
    _canonical,
    _digest,
)


SCHEMA = "rtdl.goal5809.two_app_fresh_process_controller.v2"
STATUS = (
    "COMPLETE__DIAGNOSTIC_TWO_ARM_TWO_APPLICATION_"
    "FRESH_PROCESS_PILOT")
ARMS = ("rtdl", "pyoptix")


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _phase_ns(result: Mapping[str, Any], phase: str) -> int:
    value = result["phase_times_absolute"]["phases"][phase]["duration_ns"]
    if type(value) is not int or value <= 0:
        raise RuntimeError(f"invalid child phase duration: {phase}")
    return value


def _phase_edge_ns(
    result: Mapping[str, Any], phase: str, edge: str,
) -> int:
    if edge not in {"start", "end"}:
        raise RuntimeError(f"invalid phase edge: {edge}")
    key = f"{edge}_perf_counter_ns"
    value = result["phase_times_absolute"]["phases"][phase][key]
    if type(value) is not int or value < 0:
        raise RuntimeError(f"invalid child phase {edge}: {phase}")
    return value


def _continuous_ns(
    result: Mapping[str, Any], *,
    start_phase: str, start_edge: str,
    end_phase: str, end_edge: str,
) -> int:
    start = _phase_edge_ns(result, start_phase, start_edge)
    end = _phase_edge_ns(result, end_phase, end_edge)
    if end <= start:
        raise RuntimeError({
            "invalid_continuous_boundary": {
                "start_phase": start_phase,
                "start_edge": start_edge,
                "start_ns": start,
                "end_phase": end_phase,
                "end_edge": end_edge,
                "end_ns": end,
            },
        })
    return end - start


def _child_sha(result: Mapping[str, Any], *path: str) -> str:
    value: Any = result
    for key in path:
        if not isinstance(value, Mapping) or key not in value:
            raise RuntimeError(f"missing child identity: {'.'.join(path)}")
        value = value[key]
    if not isinstance(value, str) or len(value) != 64 \
            or any(character not in "0123456789abcdef" for character in value):
        raise RuntimeError(f"invalid child SHA-256: {'.'.join(path)}")
    return value


def _comparison_identity(
    *, rtdl: Mapping[str, Any], pyoptix: Mapping[str, Any],
    target_matched_ptx_sha256: str,
    target_relation_compaction_cubin_sha256: str,
) -> dict[str, Any]:
    target_ptx = target_matched_ptx_sha256
    if _child_sha(
            rtdl, "inputs", "pyoptix_matched_baseline_ptx_sha256") \
            != target_ptx \
            or _child_sha(pyoptix, "inputs", "matched_ptx_sha256") \
            != target_ptx:
        raise RuntimeError("child target PTX identity differs")
    workload_source = {
        "rtdl": _child_sha(rtdl, "inputs", "workload_source_sha256"),
        "pyoptix": _child_sha(pyoptix, "inputs", "workload_source_sha256"),
    }
    workload_bundle = {
        "rtdl": _child_sha(rtdl, "inputs", "workload_bundle_sha256"),
        "pyoptix": _child_sha(pyoptix, "inputs", "workload_bundle_sha256"),
    }
    if len(set(workload_source.values())) != 1 \
            or len(set(workload_bundle.values())) != 1:
        raise RuntimeError("RTDL and PyOptiX workload identities differ")

    rtdl_ptx: dict[str, str] = {}
    pyoptix_ptx: dict[str, str] = {}
    byte_identical: dict[str, bool] = {}
    for task_key in TASK_KEYS:
        for arm_name, child in (("rtdl", rtdl), ("pyoptix", pyoptix)):
            app = child.get("applications", {}).get(task_key, {})
            if app.get("exact_oracle_passed") is not True \
                    or app.get("device_status_ok") is not True:
                raise RuntimeError(
                    f"{arm_name} {task_key} lacks exact successful output")
        rtdl_ptx[task_key] = _child_sha(
            rtdl, "applications", task_key, "composed_ptx_sha256")
        pyoptix_ptx[task_key] = _child_sha(
            pyoptix, "applications", task_key,
            "observed_loaded_matched_ptx_sha256")
        if pyoptix_ptx[task_key] != target_ptx:
            raise RuntimeError(f"PyOptiX {task_key} PTX identity differs")
        byte_identical[task_key] = rtdl_ptx[task_key] == pyoptix_ptx[task_key]
    observed_relation_cubin = _child_sha(
        pyoptix, "applications", "relation",
        "observed_loaded_relation_compaction_cubin_sha256")
    if observed_relation_cubin != target_relation_compaction_cubin_sha256:
        raise RuntimeError("PyOptiX retained relation cubin identity differs")

    return {
        "same_task_inputs_and_exact_oracles": True,
        "same_workload_source_sha256": workload_source["rtdl"],
        "same_workload_bundle_sha256": workload_bundle["rtdl"],
        "pyoptix_matched_baseline_ptx_sha256": target_ptx,
        "rtdl_composed_ptx_sha256_by_task": rtdl_ptx,
        "pyoptix_ptx_sha256_by_task": pyoptix_ptx,
        "pyoptix_observed_relation_compaction_cubin_sha256": (
            observed_relation_cubin),
        "byte_identical_ptx_by_task": byte_identical,
        "all_arm_ptx_byte_identical": all(byte_identical.values()),
        "comparison_basis": (
            "FUNCTIONALLY_MATCHED_TASK_INPUT_ORACLE__DISTINCT_IMPLEMENTATION_"
            "PTX_ALLOWED__RTDL_COMPOSED_PTX_CARRIES_PROTOCOL_MECHANISMS"),
        "same_ptx_claim_authorized": False,
    }


def _launch_child(
    *, arm: str, script: Path, target_manifest: Path,
    expected_target_manifest_sha256: str, first_app: str, output: Path,
    execution_identity_manifest: Path,
    expected_execution_identity_manifest_sha256: str,
    cwd: Path, runtime_environment: Mapping[str, Any],
    popen_factory: Callable[..., Any],
) -> dict[str, Any]:
    command = [
        *controlled_python_command(runtime_environment, script=script),
        "--target-manifest", str(target_manifest),
        "--expected-target-manifest-sha256",
        expected_target_manifest_sha256,
        "--execution-identity-manifest", str(execution_identity_manifest),
        "--expected-execution-identity-manifest-sha256",
        expected_execution_identity_manifest_sha256,
        "--first-app", first_app,
        "--output", str(output),
    ]
    environment = controlled_python_environment(
        runtime_environment, base=os.environ)
    sanitized_environment_keys = (
        "RTDL_DUMP_PTX_DIR",
        "RTDL_GOAL5807_PROFILE_NATIVE",
        "RTDL_OPTIX_LOG_LEVEL",
    )
    for key in sanitized_environment_keys:
        environment.pop(key, None)
    cache_root = output.parent / f"{arm}_isolated_caches"
    cache_paths = {
        "CUDA_CACHE_PATH": cache_root / "cuda",
        "CUPY_CACHE_DIR": cache_root / "cupy",
        "NUMBA_CACHE_DIR": cache_root / "numba",
        "OPTIX_CACHE_PATH": cache_root / "optix",
        "TMPDIR": cache_root / "tmp",
        "XDG_CACHE_HOME": cache_root / "xdg",
    }
    for path in cache_paths.values():
        path.mkdir(parents=True, exist_ok=False)
    environment.update({
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "CUDA_CACHE_DISABLE": "1",
        "OPTIX_CACHE_ENABLED": "0",
        "OPTIX_CACHE_MAXSIZE": "0",
        "RTDL_DISABLE_CUBIN_CACHE": "1",
        "RTDL_OPTIX_DISABLE_CUBIN_CACHE": "1",
        **{key: str(path) for key, path in cache_paths.items()},
    })
    process = popen_factory(
        command, cwd=str(cwd), env=environment, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError({
            "two_app_pilot_child_failed": arm,
            "pid": process.pid,
            "returncode": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
        })
    resolved_output = output.resolve(strict=True)
    result = json.loads(resolved_output.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise RuntimeError(f"{arm} child result is not an object")
    expected_child_identity = {
        "rtdl": (
            "rtdl.goal5809.runtime_session_two_app_pilot.v2",
            "COMPLETE__DIAGNOSTIC_TWO_APPLICATION_"
            "RUNTIME_SESSION_PILOT"),
        "pyoptix": (
            "rtdl.goal5809.pyoptix_two_app_pilot.v2",
            "COMPLETE__DIAGNOSTIC_IDIOMATIC_PYOPTIX_"
            "TWO_APPLICATION_PILOT"),
    }[arm]
    if (result.get("schema"), result.get("status")) \
            != expected_child_identity:
        raise RuntimeError(f"{arm} child schema/status differs")
    child_unsigned = dict(result)
    child_seal = child_unsigned.pop("pilot_sha256", None)
    if child_seal != _digest(child_unsigned):
        raise RuntimeError(f"{arm} child semantic seal differs")
    if result.get("process_pid") != process.pid:
        raise RuntimeError(f"{arm} child PID binding differs")
    if result.get("registered_performance_timing_count") != 0 \
            or result.get("formal_worker_count") != 0:
        raise RuntimeError(f"{arm} child escaped non-formal scope")
    if result.get("lifecycle", {}).get("app_order") != [
            first_app,
            "triangle" if first_app == "relation" else "relation"]:
        raise RuntimeError(f"{arm} child task order differs")
    return {
        "arm": arm,
        "pid": process.pid,
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
        "output_path": str(resolved_output),
        "output_bytes": resolved_output.stat().st_size,
        "output_sha256": _sha(resolved_output),
        "isolated_cache_policy": {
            "cache_root": str(cache_root.resolve(strict=True)),
            "cuda_cache_disabled": True,
            "optix_cache_disabled": True,
            "rtdl_cubin_cache_disabled": True,
            "profiling_logging_and_dump_overrides_sanitized": list(
                sanitized_environment_keys),
            "python_user_site_disabled": True,
            "isolated_tmpdir": str(
                cache_paths["TMPDIR"].resolve(strict=True)),
            "cache_paths": {
                key: str(path.resolve(strict=True))
                for key, path in cache_paths.items()
            },
        },
        "result": result,
    }


def _descriptive_ratios(
    rtdl: Mapping[str, Any], pyoptix: Mapping[str, Any],
) -> dict[str, Any]:
    def continuous_pair(
        *, start_phase: str, start_edge: str,
        end_phase: str, end_edge: str,
    ) -> tuple[int, int]:
        arguments = {
            "start_phase": start_phase,
            "start_edge": start_edge,
            "end_phase": end_phase,
            "end_edge": end_edge,
        }
        return (
            _continuous_ns(rtdl, **arguments),
            _continuous_ns(pyoptix, **arguments),
        )

    numerator_denominator = {
        "runtime_preload": (
            _phase_ns(rtdl, "runtime_preload"),
            _phase_ns(pyoptix, "runtime_preload")),
        "workload_materialization": (
            _phase_ns(rtdl, "workload_materialization"),
            _phase_ns(pyoptix, "workload_materialization")),
        "load_relation": (
            _phase_ns(rtdl, "load_relation"),
            _phase_ns(pyoptix, "load_relation")),
        "load_triangle": (
            _phase_ns(rtdl, "load_triangle"),
            _phase_ns(pyoptix, "load_triangle")),
        "first_session_admission": (
            _phase_ns(rtdl, "first_session_admission"),
            _phase_ns(pyoptix, "first_session_admission")),
        "first_use_through_first_exact_output": continuous_pair(
            start_phase="first_session_admission", start_edge="start",
            end_phase="first_app_first_exact_execute", end_edge="end"),
        "first_app_prepare": (
            _phase_ns(rtdl, "first_app_prepare"),
            _phase_ns(pyoptix, "first_app_prepare")),
        "first_app_first_exact_execute": (
            _phase_ns(rtdl, "first_app_first_exact_execute"),
            _phase_ns(pyoptix, "first_app_first_exact_execute")),
        "second_app_prepare": (
            _phase_ns(rtdl, "second_app_prepare"),
            _phase_ns(pyoptix, "second_app_prepare")),
        "second_app_first_exact_execute": (
            _phase_ns(rtdl, "second_app_first_exact_execute"),
            _phase_ns(pyoptix, "second_app_first_exact_execute")),
        "first_app_prepare_to_first_exact_output": continuous_pair(
            start_phase="first_app_prepare", start_edge="start",
            end_phase="first_app_first_exact_execute", end_edge="end"),
        "second_app_prepare_to_first_exact_output": continuous_pair(
            start_phase="second_app_prepare", start_edge="start",
            end_phase="second_app_first_exact_execute", end_edge="end"),
        "post_runtime_preload_to_first_exact_output": continuous_pair(
            start_phase="runtime_preload", start_edge="end",
            end_phase="first_app_first_exact_execute", end_edge="end"),
        "post_runtime_preload_to_second_exact_output": continuous_pair(
            start_phase="runtime_preload", start_edge="end",
            end_phase="second_app_first_exact_execute", end_edge="end"),
        "first_exact_output_to_second_exact_output": continuous_pair(
            start_phase="first_app_first_exact_execute", start_edge="end",
            end_phase="second_app_first_exact_execute", end_edge="end"),
        "application_lifecycle_start_to_second_exact_output": continuous_pair(
            start_phase="runtime_preload", start_edge="start",
            end_phase="second_app_first_exact_execute", end_edge="end"),
    }
    rows = {
        name: {
            "rtdl_ns": numerator,
            "pyoptix_ns": denominator,
            "rtdl_over_pyoptix": numerator / denominator,
        }
        for name, (numerator, denominator)
        in numerator_denominator.items()
    }
    return {
        "label": (
            "UNREGISTERED_DIAGNOSTIC_DESCRIPTIVE_RATIOS__"
            "NO_THRESHOLD_OR_INFERENCE"),
        "ratio_direction": "RTDL_NS_DIVIDED_BY_PYOPTIX_NS",
        "first_use_definition": {
            "rtdl": (
                "continuous shared_provider_admission.start -> "
                "first_app_first_exact_execute.end"),
            "pyoptix": (
                "continuous shared_context_admission.start -> "
                "first_app_first_exact_execute.end"),
        },
        "continuous_boundary_definitions": {
            "first_use_through_first_exact_output": (
                "first_session_admission.start -> "
                "first_app_first_exact_execute.end"),
            "first_app_prepare_to_first_exact_output": (
                "first_app_prepare.start -> "
                "first_app_first_exact_execute.end"),
            "second_app_prepare_to_first_exact_output": (
                "second_app_prepare.start -> "
                "second_app_first_exact_execute.end"),
            "post_runtime_preload_to_first_exact_output": (
                "runtime_preload.end -> "
                "first_app_first_exact_execute.end; "
                "includes workload materialization, both application loads, "
                "shared provider/context admission, and first exact output"),
            "post_runtime_preload_to_second_exact_output": (
                "runtime_preload.end -> "
                "second_app_first_exact_execute.end; "
                "includes workload materialization, both application loads, "
                "shared provider/context admission, and both exact outputs"),
            "first_exact_output_to_second_exact_output": (
                "first_app_first_exact_execute.end -> "
                "second_app_first_exact_execute.end"),
            "application_lifecycle_start_to_second_exact_output": (
                "runtime_preload.start -> "
                "second_app_first_exact_execute.end; "
                "includes runtime imports and excludes experiment-only input "
                "custody admission and close on both arms"),
        },
        "rows": rows,
        "noncomparative_absolute_phases": {
            "input_admission": {
                "rtdl_ns": _phase_ns(rtdl, "input_admission"),
                "pyoptix_ns": _phase_ns(pyoptix, "input_admission"),
                "rtdl_over_pyoptix": None,
                "comparison_authorized": False,
                "reason": (
                    "experiment-only target/candidate custody validation is "
                    "not an application lifecycle and rehashes RTDL artifacts "
                    "for both children"),
            },
            "close": {
                "rtdl_ns": _phase_ns(rtdl, "close"),
                "pyoptix_ns": _phase_ns(pyoptix, "close"),
                "rtdl_over_pyoptix": None,
                "comparison_authorized": False,
                "reason": (
                    "RTDL session.close releases its provider capability; "
                    "PyOptiX retains the shared OptixDeviceContext, pipelines, "
                    "and SBTs to process teardown"),
            },
        },
        "threshold_defined": False,
        "pass_fail_decision_defined": False,
        "confidence_interval_computed": False,
        "statistics_computed": False,
    }


def _run(
    args: argparse.Namespace, *,
    popen_factory: Callable[..., Any] = subprocess.Popen,
) -> dict[str, Any]:
    target_path = args.target_manifest.resolve(strict=True)
    admitted = _admit_target(
        target_path,
        expected_file_sha256=args.expected_target_manifest_sha256)
    execution_identity_path = args.execution_identity_manifest.resolve(
        strict=True)
    admitted_execution_identity = admit_execution_identity(
        execution_identity_path,
        expected_file_sha256=(
            args.expected_execution_identity_manifest_sha256),
        require_runtime_environment=True)
    controller_loaded_identity = verify_loaded_modules(
        admitted_execution_identity,
        modules_by_role={
            "goal5809_execution_identity_helper": sys.modules[
                "scripts.goal5809_execution_identity"],
            "goal5809_two_app_controller": sys.modules[__name__],
            "goal5809_rtdl_worker": sys.modules[
                "scripts.goal5809_runtime_session_two_app_pilot"],
            "goal5805_protocol_source": sys.modules[
                "experiments.goal5805_successor.protocol"],
        })
    if args.first_app not in TASK_KEYS:
        raise RuntimeError("unsupported first application")
    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    scripts_root = Path(__file__).resolve(strict=True).parent
    repo_root = scripts_root.parent
    script_paths = {
        "rtdl": scripts_root / "goal5809_runtime_session_two_app_pilot.py",
        "pyoptix": scripts_root / "goal5809_pyoptix_two_app_pilot.py",
    }
    for script in script_paths.values():
        script.resolve(strict=True)
    arm_order = (
        ARMS if args.arm_order == "rtdl-first" else tuple(reversed(ARMS)))
    children: dict[str, dict[str, Any]] = {}
    for arm in arm_order:
        children[arm] = _launch_child(
            arm=arm, script=script_paths[arm],
            target_manifest=target_path,
            expected_target_manifest_sha256=(
                args.expected_target_manifest_sha256),
            execution_identity_manifest=execution_identity_path,
            expected_execution_identity_manifest_sha256=(
                args.expected_execution_identity_manifest_sha256),
            first_app=args.first_app,
            output=output_root / f"{arm}.json",
            cwd=repo_root,
            runtime_environment=admitted_execution_identity[
                "runtime_environment_admission"],
            popen_factory=popen_factory)

    child_pids = [children[arm]["pid"] for arm in ARMS]
    if len(set(child_pids)) != 2 or os.getpid() in child_pids:
        raise RuntimeError("two-arm controller did not use two fresh children")
    rtdl = children["rtdl"]["result"]
    pyoptix = children["pyoptix"]["result"]
    expected_identity_file_sha256 = admitted_execution_identity[
        "manifest_file_sha256"]
    expected_identity_semantic_sha256 = admitted_execution_identity[
        "execution_identity_sha256"]
    expected_runtime_environment = admitted_execution_identity[
        "runtime_environment_admission"]
    if not isinstance(expected_runtime_environment, Mapping):
        raise RuntimeError("controller runtime environment identity is absent")
    expected_runtime_environment_sha256 = expected_runtime_environment[
        "environment_identity_sha256"]
    for arm, child_result in (("rtdl", rtdl), ("pyoptix", pyoptix)):
        child_identity = child_result.get("execution_identity")
        if not isinstance(child_identity, Mapping) \
                or child_identity.get("manifest_file_sha256") \
                != expected_identity_file_sha256 \
                or child_identity.get("execution_identity_sha256") \
                != expected_identity_semantic_sha256 \
                or child_identity.get("files_rehashed") is not True \
                or not isinstance(child_identity.get(
                    "runtime_environment_admission"), Mapping) \
                or child_identity["runtime_environment_admission"].get(
                    "environment_identity_sha256") \
                != expected_runtime_environment_sha256:
            raise RuntimeError(f"{arm} execution identity differs")
    ratios = _descriptive_ratios(rtdl, pyoptix)
    comparison_identity = _comparison_identity(
        rtdl=rtdl, pyoptix=pyoptix,
        target_matched_ptx_sha256=admitted["target"]["files"][
            "matched_ptx"]["sha256"],
        target_relation_compaction_cubin_sha256=admitted["target"]["files"][
            "relation_compaction_cubin"]["sha256"])
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "controller_pid": os.getpid(),
        "scope": {
            "diagnostic_pilot_only": True,
            "nonformal_diagnostic": True,
            "paper_evidence": False,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "paper_claim_authorized": False,
            "inferential_claim_authorized": False,
            "threshold_or_noninferiority_claim_authorized": False,
            "descriptive_ratio_only": True,
            "direct_arm_count": 0,
            "direct_arm_present": False,
            "host_language_control_present": False,
            "design_attribution_authorized": False,
        },
        "execution": {
            "arm_order": list(arm_order),
            "fresh_child_process_count": 2,
            "one_fresh_process_per_arm": True,
            "distinct_child_pids": child_pids,
            "same_target_manifest": True,
            "same_task_order": True,
            "first_app": args.first_app,
            "second_app": (
                "triangle" if args.first_app == "relation" else "relation"),
            "one_runtime_preload_per_child": True,
            "one_execute_per_app_per_child": True,
            "warmup_execute_count": 0,
            "boundary_scope": (
                "POST_CUSTODY_ADMISSION__FILE_BYTES_ALREADY_REHASHED__"
                "CUDA_PROVIDER_OR_CONTEXT_FIRST_USE_PRESERVED"),
            "cold_file_or_process_deployment_claim_authorized": False,
            "isolated_empty_cache_roots_per_arm": True,
            "cuda_optix_and_rtdl_cubin_caches_disabled_for_both_arms": True,
        },
        "target": {
            "path": str(admitted["target_path"]),
            "file_sha256": admitted["target_file_sha256"],
            "semantic_sha256": admitted["target"][
                "target_manifest_sha256"],
        },
        "execution_identity": {
            "path": str(execution_identity_path),
            "manifest_file_sha256": expected_identity_file_sha256,
            "execution_identity_sha256": expected_identity_semantic_sha256,
            "file_count": admitted_execution_identity["file_count"],
            "files_rehashed_by_controller_and_both_children": True,
            "runtime_environment_admission": expected_runtime_environment,
            "same_exact_runtime_environment_in_controller_and_both_children": (
                True),
            "loaded_identity_verified_by_each_child": True,
            "controller_loaded_modules": controller_loaded_identity[
                "loaded_modules"],
            "controller_loaded_identity_verified": True,
        },
        "children": {
            arm: {
                key: value for key, value in children[arm].items()
                if key != "result"
            }
            for arm in ARMS
        },
        "descriptive_ratios_nonformal": ratios,
        "comparison_identity": comparison_identity,
        "direct_arm_count": 0,
        "direct_arm_present": False,
        "host_language_control_present": False,
        "design_attribution_authorized": False,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    result = {**body, "controller_sha256": _digest(body)}
    summary = output_root / "summary.json"
    payload = _canonical(result) + b"\n"
    with summary.open("xb") as handle:
        handle.write(payload)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument(
        "--expected-target-manifest-sha256", required=True)
    parser.add_argument(
        "--execution-identity-manifest", type=Path, required=True)
    parser.add_argument(
        "--expected-execution-identity-manifest-sha256", required=True)
    parser.add_argument(
        "--first-app", choices=TASK_KEYS, default="relation")
    parser.add_argument(
        "--arm-order", choices=("rtdl-first", "pyoptix-first"),
        default="rtdl-first")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = _run(args)
    sys.stdout.write(json.dumps({
        "output": str((args.output_dir / "summary.json").resolve()),
        "controller_sha256": result["controller_sha256"],
        "label": result["descriptive_ratios_nonformal"]["label"],
        "registered_performance_timing_count": 0,
    }, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
