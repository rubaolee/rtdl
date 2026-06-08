from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

from rtdsl.current_benchmark_scale_profiles import (
    CURRENT_BENCHMARK_SCALE_PROFILE_CLAIM_BOUNDARY,
    CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
    current_benchmark_scale_profiles,
    summarize_current_benchmark_scale_profiles,
    validate_current_benchmark_scale_profiles,
)
from rtdsl.current_prepared_session_residency_profiles import (
    current_prepared_session_residency_profiles,
    summarize_current_prepared_session_residency_profiles,
    validate_current_prepared_session_residency_profiles,
)


FORBIDDEN_TRUE_FLAGS = (
    "release_authorized",
    "v2_0_release_authorized",
    "v2_6_release_authorized",
    "v2_8_release_authorized",
    "v2_9_release_authorized",
    "v2_10_release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "paper_reproduction_claim_authorized",
    "true_zero_copy_claim_authorized",
    "true_zero_copy_authorized",
    "automatic_partner_selection_authorized",
    "app_specific_native_engine_logic_allowed",
    "amd_performance_claim_authorized",
)


def _safe_file_stem(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "row"


def _tail(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def _row_command(row: dict[str, Any], *, use_current_python: bool) -> list[str]:
    command = list(row["command"])
    if use_current_python and command and command[0] == "python":
        command[0] = sys.executable
    return command


def _find_forbidden_true_flags(value: Any, *, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FLAGS and child is True:
                hits.append(child_path)
            hits.extend(_find_forbidden_true_flags(child, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_find_forbidden_true_flags(child, path=f"{path}[{index}]"))
    return hits


def _looks_like_timing_key(key: str) -> bool:
    lower = key.lower()
    if lower in {"elapsed_sec", "wrapper_elapsed_sec"}:
        return True
    return (
        lower.endswith("_sec")
        or lower.endswith("_ms")
        or lower.endswith("_ms_median")
        or lower.endswith("_sec_median")
        or lower.endswith("_median_sec")
        or lower.endswith("_total_sec")
    )


def _collect_timing_scalars(value: Any, *, path: str = "$", limit: int = 80) -> list[dict[str, Any]]:
    scalars: list[dict[str, Any]] = []

    def visit(child: Any, child_path: str, key: str | None = None) -> None:
        if len(scalars) >= limit:
            return
        if isinstance(child, dict):
            for item_key, item_value in child.items():
                visit(item_value, f"{child_path}.{item_key}", str(item_key))
                if len(scalars) >= limit:
                    break
        elif isinstance(child, list):
            for index, item_value in enumerate(child[:8]):
                visit(item_value, f"{child_path}[{index}]", key)
                if len(scalars) >= limit:
                    break
        elif key is not None and _looks_like_timing_key(key) and isinstance(child, (int, float)):
            scalars.append({"path": child_path, "value": float(child)})

    visit(value, path)
    return scalars


def _payload_timing_summary(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "payload_json_object": False,
            "timing_scalar_count": 0,
            "timing_scalars_sample": (),
        }
    timing_scalars = _collect_timing_scalars(payload)
    hot_summary = payload.get("representative_hot_path_summary")
    hot_scope = hot_summary.get("metric_scope") if isinstance(hot_summary, dict) else None
    return {
        "payload_json_object": True,
        "top_level_elapsed_sec": payload.get("elapsed_sec"),
        "top_level_wrapper_elapsed_sec": payload.get("wrapper_elapsed_sec"),
        "representative_hot_path_metric_scope": hot_scope,
        "scale_runner_elapsed_sec_is_not_hot_path_metric": (
            bool(hot_summary.get("scale_runner_elapsed_sec_is_not_hot_path_metric"))
            if isinstance(hot_summary, dict)
            else False
        ),
        "timing_scalar_count": len(timing_scalars),
        "timing_scalars_sample": tuple(timing_scalars),
    }


def _semantic_file_check(stdout_path: Path) -> dict[str, Any]:
    try:
        stdout = stdout_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "stdout_json_parseable": False,
            "stdout_json_error": "stdout file missing",
            "claim_flag_violations": (),
            "parsed_keys": (),
            "payload_timing_summary": {
                "payload_json_object": False,
                "timing_scalar_count": 0,
                "timing_scalars_sample": (),
            },
        }
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {
            "stdout_json_parseable": False,
            "stdout_json_error": str(exc),
            "claim_flag_violations": (),
            "parsed_keys": (),
            "payload_timing_summary": {
                "payload_json_object": False,
                "timing_scalar_count": 0,
                "timing_scalars_sample": (),
            },
        }
    return {
        "stdout_json_parseable": True,
        "stdout_json_error": None,
        "claim_flag_violations": tuple(_find_forbidden_true_flags(payload)),
        "parsed_keys": tuple(sorted(payload)) if isinstance(payload, dict) else (),
        "payload_timing_summary": _payload_timing_summary(payload),
    }


def _read_tail(path: Path, limit: int) -> str:
    try:
        return _tail(path.read_text(encoding="utf-8", errors="replace"), limit)
    except FileNotFoundError:
        return ""


def _run_metadata_command(command: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            command,
            cwd=Path.cwd(),
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = completed.stdout.strip()
    if text:
        return text
    err = completed.stderr.strip()
    return err or None


def _runtime_environment_metadata() -> dict[str, Any]:
    git_status = _run_metadata_command(["git", "status", "--short"]) or ""
    source_commit = _run_metadata_command(["git", "rev-parse", "HEAD"])
    return {
        "source_commit": source_commit,
        "source_commit_short": source_commit[:8] if source_commit else None,
        "git_status_short": tuple(line for line in git_status.splitlines() if line.strip()),
        "working_tree_clean": not bool(git_status.strip()),
        "python_executable": sys.executable,
        "python_version": sys.version.replace("\n", " "),
        "cwd": str(Path.cwd()),
        "rt_library_env": {
            "RTDL_OPTIX_LIBRARY": os.environ.get("RTDL_OPTIX_LIBRARY"),
            "RTDL_OPTIX_LIB": os.environ.get("RTDL_OPTIX_LIB"),
            "RTDL_EMBREE_LIBRARY": os.environ.get("RTDL_EMBREE_LIBRARY"),
            "RTDL_HIPRT_LIBRARY": os.environ.get("RTDL_HIPRT_LIBRARY"),
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "nvidia_smi": _run_metadata_command(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ]
        ),
    }


def _run_row(
    row: dict[str, Any],
    *,
    output_dir: Path,
    timeout_scale: float,
    heartbeat_sec: float,
    stdout_tail: int,
    stderr_tail: int,
    use_current_python: bool,
) -> dict[str, Any]:
    command = _row_command(row, use_current_python=use_current_python)
    timeout_sec = max(1, int(float(row["timeout_sec"]) * timeout_scale))
    stem = _safe_file_stem(str(row["row_id"]))
    stdout_path = output_dir / f"{stem}.stdout.json"
    stderr_path = output_dir / f"{stem}.stderr.txt"
    start = time.perf_counter()
    with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr_file:
        process = subprocess.Popen(
            command,
            cwd=Path.cwd(),
            env=os.environ.copy(),
            text=True,
            stdout=stdout_file,
            stderr=stderr_file,
        )
        last_heartbeat = start
        timed_out = False
        while True:
            returncode = process.poll()
            now = time.perf_counter()
            elapsed = now - start
            if returncode is not None:
                break
            if elapsed >= timeout_sec:
                timed_out = True
                process.kill()
                returncode = process.wait()
                break
            if now - last_heartbeat >= heartbeat_sec:
                print(
                    f"[goal3828] heartbeat {row['row_id']} elapsed={elapsed:.1f}s "
                    f"timeout={timeout_sec}s",
                    flush=True,
                )
                last_heartbeat = now
            time.sleep(0.25)

    elapsed = time.perf_counter() - start
    stdout_bytes = stdout_path.stat().st_size if stdout_path.exists() else 0
    stderr_bytes = stderr_path.stat().st_size if stderr_path.exists() else 0
    semantic = _semantic_file_check(stdout_path)
    if timed_out:
        status = "timeout"
    else:
        status = "pass" if returncode == 0 else "fail"
        if not semantic["stdout_json_parseable"] or semantic["claim_flag_violations"]:
            status = "fail"
    return {
        "app": row["app"],
        "row_id": row["row_id"],
        "profile_kind": row["profile_kind"],
        "status": status,
        "returncode": returncode,
        "elapsed_sec": elapsed,
        "timeout_sec": timeout_sec,
        "command": command,
        "expected_runtime_class": row["expected_runtime_class"],
        "stdout_policy": row["stdout_policy"],
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
        "semantic_stdout_check": semantic,
        "stdout_tail": _read_tail(stdout_path, stdout_tail),
        "stderr_tail": _read_tail(stderr_path, stderr_tail),
    }


def _prepared_session_profile_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected_row_ids = {str(row["row_id"]) for row in rows}
    return {
        str(profile["scale_profile_row_id"]): profile
        for profile in current_prepared_session_residency_profiles()
        if str(profile["scale_profile_row_id"]) in selected_row_ids
    }


def _attach_prepared_session_profile(
    row_result: dict[str, Any],
    *,
    profile_by_scale_row: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    profile = profile_by_scale_row.get(str(row_result["row_id"]))
    row_result["prepared_session_residency_profile"] = profile
    row_result["prepared_session_residency_profiled"] = profile is not None
    return row_result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--only", action="append", default=[], help="App or row_id to run; repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="Only emit the selected scale-profile rows.")
    parser.add_argument("--timeout-scale", type=float, default=1.0)
    parser.add_argument("--heartbeat-sec", type=float, default=30.0)
    parser.add_argument("--stdout-tail", type=int, default=4000)
    parser.add_argument("--stderr-tail", type=int, default=4000)
    parser.add_argument(
        "--literal-python",
        action="store_true",
        help="Use the literal python command from the registry instead of sys.executable.",
    )
    args = parser.parse_args()

    validation = validate_current_benchmark_scale_profiles()
    rows = list(current_benchmark_scale_profiles())
    if args.only:
        selected = set(args.only)
        rows = [row for row in rows if row["app"] in selected or row["row_id"] in selected]

    if not rows:
        raise SystemExit("no benchmark scale-profile rows selected")

    runtime_environment = _runtime_environment_metadata()
    output_dir = args.output_dir
    if output_dir is None:
        if args.output_json is not None:
            output_dir = args.output_json.parent / "outputs"
        else:
            output_dir = Path("docs/reports/goal3828_current_benchmark_scale_profiles_a5000/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    prepared_profile_by_scale_row = _prepared_session_profile_map(rows)
    prepared_profile_rows = tuple(prepared_profile_by_scale_row.values())

    result: dict[str, Any] = {
        "version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
        "claim_boundary": CURRENT_BENCHMARK_SCALE_PROFILE_CLAIM_BOUNDARY,
        "validation": validation,
        "summary": summarize_current_benchmark_scale_profiles(tuple(rows)),
        "runtime_environment": runtime_environment,
        "prepared_session_residency_validation": validate_current_prepared_session_residency_profiles(),
        "prepared_session_residency_summary": summarize_current_prepared_session_residency_profiles(
            prepared_profile_rows
        ),
        "selected_prepared_session_residency_profile_count": len(prepared_profile_rows),
        "dry_run": bool(args.dry_run),
        "file_backed_stdout_probe": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rows": [],
    }

    if args.dry_run:
        result["rows"] = [
            {
                "app": row["app"],
                "row_id": row["row_id"],
                "profile_kind": row["profile_kind"],
                "purpose": row["purpose"],
                "command": list(row["command"]),
                "timeout_sec": row["timeout_sec"],
                "stdout_policy": row["stdout_policy"],
                "expected_runtime_class": row["expected_runtime_class"],
                "evidence_refs": list(row["evidence_refs"]),
            }
            for row in rows
        ]
        result["rows"] = [
            _attach_prepared_session_profile(row_result, profile_by_scale_row=prepared_profile_by_scale_row)
            for row_result in result["rows"]
        ]
    else:
        for index, row in enumerate(rows, start=1):
            print(
                f"[goal3828] {index}/{len(rows)} start {row['row_id']} "
                f"timeout={row['timeout_sec']}s stdout=file",
                flush=True,
            )
            row_result = _run_row(
                row,
                output_dir=output_dir,
                timeout_scale=args.timeout_scale,
                heartbeat_sec=max(1.0, args.heartbeat_sec),
                stdout_tail=args.stdout_tail,
                stderr_tail=args.stderr_tail,
                use_current_python=not args.literal_python,
            )
            print(
                f"[goal3828] {index}/{len(rows)} done {row['row_id']} "
                f"status={row_result['status']} elapsed={row_result['elapsed_sec']:.3f}s "
                f"stdout_bytes={row_result['stdout_bytes']}",
                flush=True,
            )
            result["rows"].append(
                _attach_prepared_session_profile(
                    row_result,
                    profile_by_scale_row=prepared_profile_by_scale_row,
                )
            )

    statuses = [row.get("status") for row in result["rows"]]
    result["all_pass"] = None if args.dry_run else all(status == "pass" for status in statuses)
    result["json_pass_count"] = None if args.dry_run else sum(
        1
        for row in result["rows"]
        if row.get("semantic_stdout_check", {}).get("stdout_json_parseable") is True
    )
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if args.dry_run or result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
