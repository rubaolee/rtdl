#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_ID = "v4_0_m1_linux_gpu_release_gate_2026-06-19"
ARTIFACT_DIR_NAME = REPORT_ID
DEFAULT_BENCHMARK_COUNT = 262_144
DEFAULT_BENCHMARK_REPEATS = 3
DEFAULT_BENCHMARK_WARMUPS = 1
DEFAULT_COMMAND_TIMEOUT_SEC = 900
STDOUT_TAIL_CHARS = 12000
STDERR_TAIL_CHARS = 8000


@dataclass(frozen=True)
class GateCommand:
    name: str
    command: tuple[str, ...]
    output_path: Path | None = None
    required: bool = True


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _git_value(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _hardware() -> dict[str, object]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,compute_cap",
        "--format=csv,noheader",
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return {"nvidia_smi_available": False}
    line = (completed.stdout or "").strip().splitlines()
    if not line:
        return {"nvidia_smi_available": False, "stderr": completed.stderr}
    parts = [part.strip() for part in line[0].split(",")]
    return {
        "nvidia_smi_available": True,
        "gpu": parts[0] if len(parts) > 0 else "unknown",
        "driver": parts[1] if len(parts) > 1 else "unknown",
        "memory": parts[2] if len(parts) > 2 else "unknown",
        "compute_capability": parts[3] if len(parts) > 3 else "unknown",
    }


def _build_env() -> dict[str, str]:
    env = os.environ.copy()
    pythonpath_key = next((key for key in env if key.upper() == "PYTHONPATH"), "PYTHONPATH")
    entries = [str(ROOT / "src"), str(ROOT)]
    existing = env.get(pythonpath_key)
    if existing:
        entries.append(existing)
    env[pythonpath_key] = os.pathsep.join(entries)
    env.setdefault("RTDL_OPTIX_LIBRARY", str(ROOT / "build" / "librtdl_optix.so"))
    return env


def build_command_plan(
    artifact_dir: Path,
    *,
    include_benchmark: bool = True,
    benchmark_count: int = DEFAULT_BENCHMARK_COUNT,
    benchmark_repeats: int = DEFAULT_BENCHMARK_REPEATS,
    benchmark_warmups: int = DEFAULT_BENCHMARK_WARMUPS,
    python_executable: str | None = None,
) -> tuple[GateCommand, ...]:
    py = python_executable or sys.executable
    artifact_dir = Path(artifact_dir)

    commands: list[GateCommand] = [
        GateCommand("build_optix", ("make", "build-optix")),
        GateCommand(
            "source_tree_runtime_preflight",
            (
                py,
                "scripts/v4_0_source_tree_runtime_preflight.py",
                "--require-v4-gpu-runtime",
                "--output",
                str(artifact_dir / "source_tree_runtime_preflight.json"),
            ),
            artifact_dir / "source_tree_runtime_preflight.json",
        ),
        GateCommand(
            "cupy_stream_smoke",
            (
                py,
                "scripts/v4_0_m1_fixed_radius_cupy_stream_smoke.py",
                "--output",
                str(artifact_dir / "cupy_stream_smoke.json"),
            ),
            artifact_dir / "cupy_stream_smoke.json",
        ),
        GateCommand(
            "cupy_no_host_stage",
            (
                py,
                "scripts/v4_0_m1_fixed_radius_cupy_no_host_stage_probe.py",
                "--output",
                str(artifact_dir / "cupy_no_host_stage.json"),
            ),
            artifact_dir / "cupy_no_host_stage.json",
        ),
        GateCommand(
            "cupy_stream_ordering",
            (
                py,
                "scripts/v4_0_m1_fixed_radius_cupy_stream_ordering_probe.py",
                "--output",
                str(artifact_dir / "cupy_stream_ordering.json"),
            ),
            artifact_dir / "cupy_stream_ordering.json",
        ),
        GateCommand(
            "numba_partner_surface",
            (
                py,
                "scripts/v4_0_m1_fixed_radius_numba_partner_surface_probe.py",
                "--output",
                str(artifact_dir / "numba_partner_surface.json"),
            ),
            artifact_dir / "numba_partner_surface.json",
        ),
        GateCommand(
            "dlpack_capsule",
            (
                py,
                "scripts/v4_0_m1_fixed_radius_dlpack_capsule_probe.py",
                "--output",
                str(artifact_dir / "dlpack_capsule.json"),
            ),
            artifact_dir / "dlpack_capsule.json",
        ),
        GateCommand(
            "pytorch_cuda_tensor",
            (
                py,
                "scripts/v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe.py",
                "--output",
                str(artifact_dir / "pytorch_cuda_tensor.json"),
            ),
            artifact_dir / "pytorch_cuda_tensor.json",
        ),
    ]
    if include_benchmark:
        commands.append(
            GateCommand(
                "cupy_benchmark",
                (
                    py,
                    "scripts/v4_0_m1_fixed_radius_cupy_benchmark_probe.py",
                    "--count",
                    str(int(benchmark_count)),
                    "--repeats",
                    str(int(benchmark_repeats)),
                    "--warmups",
                    str(int(benchmark_warmups)),
                    "--output",
                    str(artifact_dir / "cupy_benchmark.json"),
                ),
                artifact_dir / "cupy_benchmark.json",
            )
        )
    commands.extend(
        [
            GateCommand(
                "v4_release_candidate",
                (py, "scripts/run_test_matrix.py", "--group", "v4_release_candidate"),
            ),
            GateCommand(
                "claim_boundary_scan",
                (
                    py,
                    "scripts/v4_0_current_front_door_claim_boundary_scan.py",
                    "--output",
                    str(artifact_dir / "claim_boundary_scan.json"),
                ),
                artifact_dir / "claim_boundary_scan.json",
            ),
            GateCommand("git_diff_check", ("git", "diff", "--check")),
            GateCommand("clean_worktree", ("git", "status", "--short")),
        ]
    )
    return tuple(commands)


def _tail(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def run_gate_command(command: GateCommand, *, timeout_sec: int) -> dict[str, object]:
    started = time.monotonic()
    completed = subprocess.run(
        list(command.command),
        cwd=ROOT,
        env=_build_env(),
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    elapsed = time.monotonic() - started
    clean_worktree_ok = True
    if command.name == "clean_worktree":
        clean_worktree_ok = completed.stdout.strip() == ""
    ok = completed.returncode == 0 and clean_worktree_ok
    return {
        "name": command.name,
        "command": " ".join(command.command),
        "returncode": completed.returncode,
        "status": "pass" if ok else "fail",
        "ok": ok,
        "elapsed_sec": elapsed,
        "output_path": _repo_relative(command.output_path) if command.output_path else None,
        "stdout_tail": _tail(completed.stdout or "", STDOUT_TAIL_CHARS),
        "stderr_tail": _tail(completed.stderr or "", STDERR_TAIL_CHARS),
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _claim_flags_false(payload: dict[str, Any], keys: tuple[str, ...]) -> bool:
    boundaries = payload.get("claim_boundaries", {})
    return all(boundaries.get(key) is False for key in keys)


def _all_values_true(values: object) -> bool:
    if isinstance(values, dict):
        return all(_all_values_true(value) for value in values.values())
    if isinstance(values, list):
        return all(_all_values_true(value) for value in values)
    return values is True


def summarize_probe_outputs(
    artifact_dir: Path,
    *,
    include_benchmark: bool,
    min_benchmark_count: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    artifact_dir = Path(artifact_dir)
    failures: list[dict[str, object]] = []

    def require(condition: bool, probe: str, check: str, detail: object = None) -> None:
        if not condition:
            failures.append({"probe": probe, "check": check, "detail": detail})

    def load(probe: str, filename: str) -> dict[str, Any]:
        path = artifact_dir / filename
        if not path.exists():
            failures.append({"probe": probe, "check": "missing_output_json", "detail": str(path)})
            return {}
        try:
            return _read_json(path)
        except json.JSONDecodeError as exc:
            failures.append({"probe": probe, "check": "invalid_output_json", "detail": str(exc)})
            return {}

    summaries: dict[str, object] = {}

    smoke = load("cupy_stream_smoke", "cupy_stream_smoke.json")
    summaries["cupy_stream_smoke"] = {
        "status": smoke.get("status"),
        "route_id": smoke.get("route_id"),
        "caller_stream_handle_nonzero": smoke.get("caller_stream_handle_nonzero"),
    }
    require(smoke.get("status") == "pass-with-boundary", "cupy_stream_smoke", "status")
    require(smoke.get("route_id") == "fixed_radius_count_threshold_2d", "cupy_stream_smoke", "route")
    require(_all_values_true(smoke.get("pointer_identity", {})), "cupy_stream_smoke", "pointer_identity")
    require(_all_values_true(smoke.get("pointer_echo_identity", {})), "cupy_stream_smoke", "pointer_echo_identity")
    require(
        _claim_flags_false(
            smoke,
            (
                "public_speedup_claim_authorized",
                "rt_core_speedup_claim_authorized",
                "v4_true_zero_copy_claim_authorized",
                "async_claim_authorized",
            ),
        ),
        "cupy_stream_smoke",
        "claim_boundaries",
    )

    no_host = load("cupy_no_host_stage", "cupy_no_host_stage.json")
    classification = no_host.get("transfer_counter_classification", {})
    summaries["cupy_no_host_stage"] = {
        "status": no_host.get("status"),
        "point_count": no_host.get("point_count"),
        "no_host_stage_ready": classification.get("no_host_stage_ready"),
    }
    require(no_host.get("status") == "pass-with-boundary", "cupy_no_host_stage", "status")
    require(classification.get("no_host_stage_ready") is True, "cupy_no_host_stage", "no_host_stage_ready")
    require(
        no_host.get("metadata_subset", {}).get("v4_true_zero_copy_claim_authorized") is False,
        "cupy_no_host_stage",
        "public_true_zero_copy_blocked",
    )

    ordering = load("cupy_stream_ordering", "cupy_stream_ordering.json")
    summaries["cupy_stream_ordering"] = {
        "status": ordering.get("status"),
        "ordering_scope": ordering.get("ordering_scope"),
    }
    require(ordering.get("status") == "pass-with-boundary", "cupy_stream_ordering", "status")
    require(
        ordering.get("validation", {}).get("device_consumer_checksum_match") is True,
        "cupy_stream_ordering",
        "same_stream_checksum",
    )
    require(
        ordering.get("validation", {}).get("cross_stream_device_consumer_checksum_match") is True,
        "cupy_stream_ordering",
        "cross_stream_checksum",
    )
    require(
        ordering.get("cross_stream_prepare_query_contract", {}).get("cross_stream_event_wait_validated") is True,
        "cupy_stream_ordering",
        "cross_stream_event_wait",
    )
    require(
        ordering.get("metadata_subset", {}).get("native_async_ready") is False,
        "cupy_stream_ordering",
        "async_blocked",
    )

    numba = load("numba_partner_surface", "numba_partner_surface.json")
    summaries["numba_partner_surface"] = {
        "status": numba.get("status"),
        "case_count": numba.get("case_count"),
        "pass_count": numba.get("pass_count"),
    }
    require(numba.get("status") == "pass-with-boundary", "numba_partner_surface", "status")
    require(numba.get("case_count") == numba.get("pass_count"), "numba_partner_surface", "case_pass_count")
    require(
        numba.get("claim_boundaries", {}).get("numba_m1_devicearray_partner_surface_claim_authorized") is True,
        "numba_partner_surface",
        "exact_m1_claim",
    )
    require(
        numba.get("claim_boundaries", {}).get("numba_full_partner_surface_claim_authorized") is False,
        "numba_partner_surface",
        "full_surface_blocked",
    )

    dlpack = load("dlpack_capsule", "dlpack_capsule.json")
    summaries["dlpack_capsule"] = {
        "status": dlpack.get("status"),
        "protocol": dlpack.get("protocol"),
    }
    require(dlpack.get("status") == "pass-with-boundary", "dlpack_capsule", "status")
    require(dlpack.get("validation", {}).get("output_match") is True, "dlpack_capsule", "output_match")
    require(
        dlpack.get("dlpack_stream_contract", {}).get("all_requested_streams_match_caller_stream") is True,
        "dlpack_capsule",
        "stream_contract",
    )
    require(
        dlpack.get("claim_boundaries", {}).get("fixed_radius_m1_dlpack_capsule_route_claim_authorized") is True,
        "dlpack_capsule",
        "exact_m1_claim",
    )
    require(
        dlpack.get("claim_boundaries", {}).get("framework_neutral_dlpack_route_claim_authorized") is False,
        "dlpack_capsule",
        "framework_neutral_blocked",
    )

    pytorch = load("pytorch_cuda_tensor", "pytorch_cuda_tensor.json")
    summaries["pytorch_cuda_tensor"] = {
        "status": pytorch.get("status"),
        "accepted_case_count": pytorch.get("validation", {}).get("accepted_case_count"),
        "rejected_case_count": pytorch.get("validation", {}).get("rejected_case_count"),
    }
    require(pytorch.get("status") == "pass-with-boundary", "pytorch_cuda_tensor", "status")
    require(
        pytorch.get("validation", {}).get("compatibility_matrix_all_expected") is True,
        "pytorch_cuda_tensor",
        "compatibility_matrix",
    )
    require(
        pytorch.get("stream_contract", {}).get("cross_stream_event_wait_validated") is True,
        "pytorch_cuda_tensor",
        "cross_stream_event_wait",
    )
    require(
        pytorch.get("claim_boundaries", {}).get("pytorch_fixed_radius_m1_cuda_tensor_route_claim_authorized") is True,
        "pytorch_cuda_tensor",
        "exact_m1_claim",
    )
    require(
        pytorch.get("claim_boundaries", {}).get("pytorch_full_partner_surface_claim_authorized") is False,
        "pytorch_cuda_tensor",
        "full_surface_blocked",
    )

    if include_benchmark:
        benchmark = load("cupy_benchmark", "cupy_benchmark.json")
        summaries["cupy_benchmark"] = {
            "status": benchmark.get("status"),
            "count": benchmark.get("parameters", {}).get("count"),
            "median_seconds": benchmark.get("median_seconds", {}),
        }
        require(benchmark.get("status") == "pass-with-boundary", "cupy_benchmark", "status")
        require(
            int(benchmark.get("parameters", {}).get("count", 0)) >= int(min_benchmark_count),
            "cupy_benchmark",
            "serious_scale_count",
        )
        require(benchmark.get("validation", {}).get("output_match") is True, "cupy_benchmark", "output_match")
        require(
            _claim_flags_false(
                benchmark,
                (
                    "public_speedup_claim_authorized",
                    "rt_core_speedup_claim_authorized",
                    "v4_true_zero_copy_claim_authorized",
                    "async_claim_authorized",
                ),
            ),
            "cupy_benchmark",
            "claim_boundaries",
        )

    return summaries, failures


def build_report(
    *,
    artifact_dir: Path,
    command_results: list[dict[str, object]],
    include_benchmark: bool,
    min_benchmark_count: int,
    initial_git_status_short: str,
) -> dict[str, object]:
    probe_summaries, probe_failures = summarize_probe_outputs(
        artifact_dir,
        include_benchmark=include_benchmark,
        min_benchmark_count=min_benchmark_count,
    )
    command_failures = [
        {
            "name": result["name"],
            "status": result["status"],
            "returncode": result["returncode"],
            "stdout_tail": result.get("stdout_tail", ""),
            "stderr_tail": result.get("stderr_tail", ""),
        }
        for result in command_results
        if not result.get("ok")
    ]
    ok = not command_failures and not probe_failures and not initial_git_status_short.strip()
    return {
        "report_id": REPORT_ID,
        "date": "2026-06-19",
        "status": "pass" if ok else "fail",
        "ok": ok,
        "host": platform.node(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "hardware": _hardware(),
        "git": {
            "head": _git_value("rev-parse", "HEAD"),
            "tree": _git_value("rev-parse", "HEAD^{tree}"),
            "initial_status_short": initial_git_status_short,
        },
        "route_id": "fixed_radius_count_threshold_2d",
        "scope": "current-head Linux GPU V4 M1 release evidence gate",
        "artifact_dir": _repo_relative(Path(artifact_dir)),
        "include_benchmark": bool(include_benchmark),
        "min_benchmark_count": int(min_benchmark_count),
        "commands": command_results,
        "probe_summaries": probe_summaries,
        "command_failures": command_failures,
        "probe_failures": probe_failures,
        "release_reading": {
            "m1_route_release_evidence_ready": ok,
            "front_door_switch_authorized": False,
            "current_user_release_may_change": False,
            "release_action_required": True,
            "release_action_gate": "front_door_docs_switch_plus_explicit_user_release_approval",
        },
        "claim_boundaries": {
            "fixed_radius_m1_python_gpu_operator_claim_authorized": ok,
            "v4_current_front_door_authorized": False,
            "package_install_claim_authorized": False,
            "pypi_claim_authorized": False,
            "wheel_claim_authorized": False,
            "stable_sdk_claim_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "full_pytorch_surface_claim_authorized": False,
            "full_numba_surface_claim_authorized": False,
            "full_dlpack_surface_claim_authorized": False,
        },
    }


def run_gate(
    *,
    artifact_dir: Path,
    output: Path,
    include_benchmark: bool,
    benchmark_count: int,
    benchmark_repeats: int,
    benchmark_warmups: int,
    timeout_sec: int,
) -> dict[str, object]:
    artifact_dir = Path(artifact_dir)
    output = Path(output)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    initial_status = _git_value("status", "--short")
    command_results: list[dict[str, object]] = []
    plan = build_command_plan(
        artifact_dir,
        include_benchmark=include_benchmark,
        benchmark_count=benchmark_count,
        benchmark_repeats=benchmark_repeats,
        benchmark_warmups=benchmark_warmups,
    )
    for command in plan:
        result = run_gate_command(command, timeout_sec=timeout_sec)
        command_results.append(result)
        if not result["ok"]:
            break

    report = build_report(
        artifact_dir=artifact_dir,
        command_results=command_results,
        include_benchmark=include_benchmark,
        min_benchmark_count=benchmark_count if include_benchmark else 0,
        initial_git_status_short=initial_status,
    )
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    tmp_root = Path(tempfile.gettempdir())
    parser = argparse.ArgumentParser(description="Run the current-head V4 M1 Linux GPU release evidence gate.")
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=tmp_root / ARTIFACT_DIR_NAME,
        help="directory for child probe JSON outputs; use /tmp for clean worktree validation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=tmp_root / f"{REPORT_ID}.json",
        help="aggregate JSON report path",
    )
    parser.add_argument("--skip-benchmark", action="store_true", help="skip the serious-scale benchmark probe")
    parser.add_argument("--benchmark-count", type=int, default=DEFAULT_BENCHMARK_COUNT)
    parser.add_argument("--benchmark-repeats", type=int, default=DEFAULT_BENCHMARK_REPEATS)
    parser.add_argument("--benchmark-warmups", type=int, default=DEFAULT_BENCHMARK_WARMUPS)
    parser.add_argument("--timeout-sec", type=int, default=DEFAULT_COMMAND_TIMEOUT_SEC)
    args = parser.parse_args()

    report = run_gate(
        artifact_dir=args.artifact_dir,
        output=args.output,
        include_benchmark=not args.skip_benchmark,
        benchmark_count=args.benchmark_count,
        benchmark_repeats=args.benchmark_repeats,
        benchmark_warmups=args.benchmark_warmups,
        timeout_sec=args.timeout_sec,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
