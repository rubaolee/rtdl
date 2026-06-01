from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GOAL2855_RUNNER_VERSION = "rtdl.goal2855.v2_5_current_canonical_harness_packet_runner.v1"
TOOLCHAIN_PROVENANCE_VERSION = "rtdl.goal2916.toolchain_provenance.v1"

DEFAULT_OUTPUT_DIR = Path(tempfile.gettempdir()) / "goal2855_current_canonical_harness_runner_pod"
FALSE_CLAIM_KEYS = (
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "paper_reproduction_claim_authorized",
    "paper_speedup_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "true_zero_copy_claim_authorized",
    "triton_speedup_claim_authorized",
    "rtdl_beats_rayjoin_claim_authorized",
    "rtdl_beats_rtnn_claim_authorized",
    "rtdl_beats_xhd_claim_authorized",
    "rtdl_beats_cupy_grid_claim_authorized",
    "native_engine_customization",
)


@dataclass(frozen=True)
class HarnessSpec:
    goal: str
    app: str
    script: str
    artifact_name: str
    boundary: str
    fail_fast_supported: bool = False
    work_dir_supported: bool = False
    raw_output_dir_supported: bool = False


HARNESS_SPECS: tuple[HarnessSpec, ...] = (
    HarnessSpec(
        goal="Goal2797",
        app="triangle_counting",
        script="scripts/goal2797_triangle_counting_v25_canonical_harness.py",
        artifact_name="goal2797_triangle_counting.json",
        boundary="canonical app harness only",
        fail_fast_supported=True,
        work_dir_supported=True,
    ),
    HarnessSpec(
        goal="Goal2798",
        app="librts_spatial_index",
        script="scripts/goal2798_librts_v25_warm_median_harness.py",
        artifact_name="goal2798_librts.json",
        boundary="Tier C no-regression harness; no partner or public RT claim",
    ),
    HarnessSpec(
        goal="Goal2799",
        app="spatial_rayjoin",
        script="scripts/goal2799_spatial_rayjoin_v25_prepared_count_harness.py",
        artifact_name="goal2799_spatial_rayjoin.json",
        boundary="prepared OptiX count/parity route, not full RayJoin reproduction",
        fail_fast_supported=True,
    ),
    HarnessSpec(
        goal="Goal2800",
        app="rtnn",
        script="scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py",
        artifact_name="goal2800_rtnn.json",
        boundary="Tier B exact ranked-summary opponent; distribution-dependent",
        fail_fast_supported=True,
        work_dir_supported=True,
    ),
    HarnessSpec(
        goal="Goal2801",
        app="hausdorff_xhd",
        script="scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py",
        artifact_name="goal2801_hausdorff_xhd.json",
        boundary="exact RTDL/OptiX path; no claim to beat optimized CuPy grid",
    ),
    HarnessSpec(
        goal="Goal2802",
        app="rt_dbscan",
        script="scripts/goal2802_rt_dbscan_v25_live_grouped_stream_harness.py",
        artifact_name="goal2802_rt_dbscan.json",
        boundary="grouped stream continuation evidence; no paper reproduction claim",
        raw_output_dir_supported=True,
    ),
    HarnessSpec(
        goal="Goal2803",
        app="barnes_hut",
        script="scripts/goal2803_barnes_hut_v25_consolidated_harness.py",
        artifact_name="goal2803_barnes_hut.json",
        boundary="membership and vector-sum harness; Triton vector path not promoted",
    ),
)


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _path_exists(value: str | None) -> bool:
    return bool(value) and Path(str(value)).exists()


def _env_path(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _cuda_home() -> str | None:
    return _env_path("CUDA_HOME", "CUDA_PREFIX")


def _nvcc_path() -> str:
    explicit = _env_path("RTDL_NVCC", "NVCC")
    if explicit:
        return explicit
    cuda_home = _cuda_home()
    if cuda_home:
        return str(Path(cuda_home) / "bin" / ("nvcc.exe" if os.name == "nt" else "nvcc"))
    return "nvcc"


def _python_module_version(module: str) -> str | None:
    return _check_output(
        [
            sys.executable,
            "-c",
            (
                f"import {module}; "
                f"print(getattr({module}, '__version__', 'unknown'))"
            ),
        ]
    )


def _toolchain_metadata() -> dict[str, Any]:
    nvcc = _nvcc_path()
    cxx = _env_path("RTDL_NVCC_CCBIN", "CXX") or "g++"
    optix_prefix = _env_path("OPTIX_PREFIX")
    optix_header = str(Path(optix_prefix) / "include" / "optix.h") if optix_prefix else None
    optix_library = _env_path("RTDL_OPTIX_LIBRARY", "RTDL_OPTIX_LIB")
    return {
        "metadata_version": TOOLCHAIN_PROVENANCE_VERSION,
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "cuda_home": _cuda_home(),
        "optix_prefix": optix_prefix,
        "optix_header": optix_header,
        "optix_header_exists": _path_exists(optix_header),
        "rtdl_optix_library": optix_library,
        "rtdl_optix_library_exists": _path_exists(optix_library),
        "rtdl_optix_ptx_arch": os.environ.get("RTDL_OPTIX_PTX_ARCH"),
        "rtdl_optix_ptx_compiler": os.environ.get("RTDL_OPTIX_PTX_COMPILER"),
        "rtdl_nvcc": os.environ.get("RTDL_NVCC"),
        "nvcc_probe_path": nvcc,
        "nvcc_version": _check_output([nvcc, "--version"]),
        "cxx_compiler": cxx,
        "cxx_version": _check_output([cxx, "--version"]),
        "triton_version": _python_module_version("triton"),
        "torch_version": _python_module_version("torch"),
        "cupy_version": _python_module_version("cupy"),
        "numba_version": _python_module_version("numba"),
        "nvidia_smi_topology": _check_output(["nvidia-smi", "--query-gpu=name,uuid,driver_version", "--format=csv,noheader"]),
        "claim_boundary": {
            "compiler_provenance_index_only": True,
            "compiler_fairness_claim_authorized": False,
            "multivendor_claim_authorized": False,
            "v2_5_release_authorized": False,
            "public_speedup_claim_authorized": False,
        },
    }


def _run_metadata() -> dict[str, Any]:
    return {
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "toolchain": _toolchain_metadata(),
    }


def build_harness_command(
    spec: HarnessSpec,
    *,
    python_exe: str,
    output_dir: Path,
    work_dir: Path,
    raw_output_dir: Path,
    fail_fast: bool,
) -> tuple[str, ...]:
    command = [
        str(python_exe),
        spec.script,
        "--output",
        str(output_dir / spec.artifact_name),
    ]
    if spec.fail_fast_supported and fail_fast:
        command.append("--fail-fast")
    if spec.work_dir_supported:
        command.extend(["--work-dir", str(work_dir / spec.goal.lower())])
    if spec.raw_output_dir_supported:
        command.extend(["--raw-output-dir", str(raw_output_dir / spec.goal.lower())])
    return tuple(command)


def packet_plan(
    *,
    python_exe: str,
    output_dir: Path,
    work_dir: Path,
    raw_output_dir: Path,
    fail_fast: bool,
    compact_child_output: bool = False,
    stdout_dir: Path | None = None,
) -> list[dict[str, Any]]:
    return [
        {
            "goal": spec.goal,
            "app": spec.app,
            "script": spec.script,
            "artifact_name": spec.artifact_name,
            "boundary": spec.boundary,
            "command": list(
                build_harness_command(
                    spec,
                    python_exe=python_exe,
                    output_dir=output_dir,
                    work_dir=work_dir,
                    raw_output_dir=raw_output_dir,
                    fail_fast=fail_fast,
                )
            ),
            "compact_child_output": bool(compact_child_output),
            "stdout_log_name": f"{spec.goal.lower()}_{spec.app}.stdout" if compact_child_output else None,
            "stdout_log_path": str((stdout_dir or output_dir / "_stdout") / f"{spec.goal.lower()}_{spec.app}.stdout")
            if compact_child_output
            else None,
        }
        for spec in HARNESS_SPECS
    ]


def run_packet(
    *,
    python_exe: str,
    output_dir: Path,
    work_dir: Path,
    raw_output_dir: Path,
    summary_name: str,
    timeout_seconds: int,
    fail_fast: bool,
    compact_child_output: bool = False,
    stdout_dir: Path | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    stdout_root = Path(stdout_dir) if stdout_dir is not None else output_dir / "_stdout"
    if compact_child_output:
        stdout_root.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    env = os.environ.copy()
    python_path_entries = [str(ROOT / "src"), str(ROOT)]
    if env.get("PYTHONPATH"):
        python_path_entries.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(python_path_entries)

    executions: list[dict[str, Any]] = []
    for index, spec in enumerate(HARNESS_SPECS, start=1):
        command = build_harness_command(
            spec,
            python_exe=python_exe,
            output_dir=output_dir,
            work_dir=work_dir,
            raw_output_dir=raw_output_dir,
            fail_fast=fail_fast,
        )
        _log(
            f"starting {index}/{len(HARNESS_SPECS)} {spec.goal} "
            f"({spec.app}) -> {spec.artifact_name}"
        )
        step_started = time.perf_counter()
        stdout_log_path = stdout_root / f"{spec.goal.lower()}_{spec.app}.stdout" if compact_child_output else None
        if compact_child_output:
            returncode, timed_out, error = _run_child_compact(
                command=command,
                env=env,
                timeout_seconds=int(timeout_seconds),
                stdout_log_path=stdout_log_path,
            )
        else:
            try:
                completed = subprocess.run(
                    list(command),
                    cwd=ROOT,
                    env=env,
                    timeout=int(timeout_seconds),
                    check=False,
                )
                returncode = int(completed.returncode)
                timed_out = False
                error = None
            except subprocess.TimeoutExpired as exc:
                returncode = 124
                timed_out = True
                error = f"timeout after {exc.timeout} seconds"
        elapsed = time.perf_counter() - step_started
        artifact_path = output_dir / spec.artifact_name
        execution = {
            "goal": spec.goal,
            "app": spec.app,
            "artifact_name": spec.artifact_name,
            "artifact_path": str(artifact_path),
            "command": list(command),
            "returncode": returncode,
            "timed_out": timed_out,
            "error": error,
            "elapsed_sec": elapsed,
            "compact_child_output": bool(compact_child_output),
            "stdout_log_path": str(stdout_log_path) if stdout_log_path is not None else None,
        }
        executions.append(execution)
        _log(f"finished {spec.goal}: returncode={returncode}, elapsed={elapsed:.2f}s")
        if fail_fast and returncode != 0:
            _log(f"fail-fast stopping after {spec.goal}")
            break

    summary = summarize_packet(
        output_dir=output_dir,
        executions=executions,
        elapsed_sec=time.perf_counter() - started,
    )
    summary_path = output_dir / summary_name
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    _log(f"summary written to {summary_path}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def summarize_packet(
    *,
    output_dir: Path,
    executions: list[dict[str, Any]],
    elapsed_sec: float,
) -> dict[str, Any]:
    artifact_summaries: dict[str, Any] = {}
    source_commits: set[str] = set()
    dirty_artifacts: dict[str, list[str]] = {}
    claim_violations: dict[str, dict[str, Any]] = {}
    artifact_status_ok = True

    for spec in HARNESS_SPECS:
        artifact_path = output_dir / spec.artifact_name
        if not artifact_path.exists():
            artifact_summaries[spec.artifact_name] = {
                "goal": spec.goal,
                "app": spec.app,
                "exists": False,
                "status": "missing",
                "boundary": spec.boundary,
            }
            artifact_status_ok = False
            continue
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        status = str(payload.get("status"))
        source_commit = payload.get("source_commit")
        source_dirty = list(payload.get("source_dirty") or [])
        boundary = dict(payload.get("claim_boundary") or {})
        violations = {
            key: boundary[key]
            for key in FALSE_CLAIM_KEYS
            if key in boundary and boundary[key] is not False
        }
        if source_commit:
            source_commits.add(str(source_commit))
        if source_dirty:
            dirty_artifacts[spec.artifact_name] = source_dirty
        if violations:
            claim_violations[spec.artifact_name] = violations
        if status != "pass":
            artifact_status_ok = False
        artifact_summaries[spec.artifact_name] = {
            "goal": spec.goal,
            "app": spec.app,
            "exists": True,
            "status": status,
            "source_commit": source_commit,
            "source_dirty": source_dirty,
            "gpu": payload.get("gpu"),
            "claim_boundary_keys": sorted(boundary),
            "claim_boundary_violations": violations,
            "boundary": spec.boundary,
        }

    completed_by_artifact = {execution["artifact_name"]: execution for execution in executions}
    returncode_ok = all(
        int(completed_by_artifact.get(spec.artifact_name, {}).get("returncode", -1)) == 0
        for spec in HARNESS_SPECS
    )
    artifact_count_ok = len([item for item in artifact_summaries.values() if item["exists"]]) == len(HARNESS_SPECS)
    source_commit_consistent = len(source_commits) == 1
    all_pass = (
        returncode_ok
        and artifact_status_ok
        and artifact_count_ok
        and source_commit_consistent
        and not dirty_artifacts
        and not claim_violations
    )
    metadata = _run_metadata()
    return {
        "goal": "Goal2855",
        "runner_version": GOAL2855_RUNNER_VERSION,
        "status": "pass" if all_pass else "fail",
        "all_pass": all_pass,
        "artifact_count": len([item for item in artifact_summaries.values() if item["exists"]]),
        "expected_artifact_count": len(HARNESS_SPECS),
        "returncode_ok": returncode_ok,
        "artifact_status_ok": artifact_status_ok,
        "artifact_count_ok": artifact_count_ok,
        "source_commit_consistent": source_commit_consistent,
        "source_commit": sorted(source_commits)[0] if len(source_commits) == 1 else None,
        "source_commits": sorted(source_commits),
        "dirty_artifacts": dirty_artifacts,
        "claim_boundary_violations": claim_violations,
        "artifacts": artifact_summaries,
        "executions": executions,
        "claim_boundary": {
            "canonical_packet_runner": True,
            "compact_child_output_safe_to_use": True,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v2_5_release_authorized": False,
        },
        "runner_metadata": metadata,
        "elapsed_sec": float(elapsed_sec),
    }


def _run_child_compact(
    *,
    command: tuple[str, ...],
    env: dict[str, str],
    timeout_seconds: int,
    stdout_log_path: Path,
) -> tuple[int, bool, str | None]:
    stdout_log_path.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        list(command),
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    lines: queue.Queue[str | None] = queue.Queue()

    def _reader() -> None:
        try:
            for line in process.stdout:
                lines.put(line)
        finally:
            lines.put(None)

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()
    started = time.perf_counter()
    timed_out = False
    error: str | None = None
    reader_done = False

    with stdout_log_path.open("w", encoding="utf-8") as log:
        while not reader_done:
            try:
                line = lines.get(timeout=1.0)
            except queue.Empty:
                if process.poll() is not None:
                    continue
                if time.perf_counter() - started > timeout_seconds:
                    timed_out = True
                    error = f"timeout after {timeout_seconds} seconds"
                    process.kill()
                continue
            if line is None:
                reader_done = True
                continue
            log.write(line)
            log.flush()
            if _should_echo_child_line(line):
                print(line, end="", flush=True)

    returncode = int(process.wait())
    if timed_out:
        returncode = 124
    return returncode, timed_out, error


def _should_echo_child_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("["):
        return True
    if stripped.startswith(("Traceback", "ERROR", "FAILED", "OK", "Ran ", "usage:")):
        return True
    if "error:" in stripped.lower():
        return True
    return False


def _log(message: str) -> None:
    print(f"[goal2855] {message}", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2855 v2.5 current canonical harness packet runner.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--raw-output-dir", type=Path)
    parser.add_argument("--summary-name", default="goal2855_summary.json")
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument(
        "--compact-child-output",
        action="store_true",
        help="Save each child harness stdout to a log file while echoing only progress and error lines.",
    )
    parser.add_argument("--stdout-dir", type=Path)
    parser.add_argument("--list", action="store_true", help="Print the seven-harness plan without running it.")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    work_dir = Path(args.work_dir) if args.work_dir else output_dir / "_work"
    raw_output_dir = Path(args.raw_output_dir) if args.raw_output_dir else output_dir / "_raw"

    if args.list:
        plan = {
            "goal": "Goal2855",
            "runner_version": GOAL2855_RUNNER_VERSION,
            "harness_count": len(HARNESS_SPECS),
            "output_dir": str(output_dir),
            "work_dir": str(work_dir),
            "raw_output_dir": str(raw_output_dir),
            "stdout_dir": str(Path(args.stdout_dir) if args.stdout_dir else output_dir / "_stdout"),
            "fail_fast": bool(args.fail_fast),
            "compact_child_output": bool(args.compact_child_output),
            "plan": packet_plan(
                python_exe=str(args.python),
                output_dir=output_dir,
                work_dir=work_dir,
                raw_output_dir=raw_output_dir,
                fail_fast=bool(args.fail_fast),
                compact_child_output=bool(args.compact_child_output),
                stdout_dir=Path(args.stdout_dir) if args.stdout_dir else output_dir / "_stdout",
            ),
            "claim_boundary": {
                "plan_only": True,
                "v2_5_release_authorized": False,
                "public_speedup_claim_authorized": False,
            },
        }
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0

    summary = run_packet(
        python_exe=str(args.python),
        output_dir=output_dir,
        work_dir=work_dir,
        raw_output_dir=raw_output_dir,
        summary_name=str(args.summary_name),
        timeout_seconds=int(args.timeout_seconds),
        fail_fast=bool(args.fail_fast),
        compact_child_output=bool(args.compact_child_output),
        stdout_dir=Path(args.stdout_dir) if args.stdout_dir else None,
    )
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
