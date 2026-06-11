from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any

from rtdsl.current_embree_cpu_partner_reference import (
    CURRENT_EMBREE_CPU_PARTNER_REFERENCE_CLAIM_BOUNDARY,
    CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
    current_embree_cpu_partner_reference_rows,
    summarize_current_embree_cpu_partner_reference,
    validate_current_embree_cpu_partner_reference,
)


FORBIDDEN_TRUE_FLAGS = (
    "release_authorized",
    "v2_0_release_authorized",
    "v2_6_release_authorized",
    "v2_8_release_authorized",
    "v2_9_release_authorized",
    "v2_10_release_authorized",
    "v2_11_release_authorized",
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
    "intel_gpu_performance_claim_authorized",
)


def _tail(text: str | bytes | None, limit: int) -> str:
    if text is None:
        return ""
    decoded = text.decode(errors="replace") if isinstance(text, bytes) else text
    if len(decoded) <= limit:
        return decoded
    return decoded[-limit:]


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


def _semantic_stdout_check(stdout: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {
            "stdout_json_parseable": False,
            "stdout_json_error": str(exc),
            "claim_flag_violations": (),
        }
    return {
        "stdout_json_parseable": True,
        "stdout_json_error": None,
        "claim_flag_violations": tuple(_find_forbidden_true_flags(payload)),
    }


def _cpu_thread_env(*, threads: int | None) -> dict[str, str]:
    selected = threads if threads and threads > 0 else (os.cpu_count() or 1)
    value = str(selected)
    return {
        "OMP_NUM_THREADS": value,
        "TBB_NUM_THREADS": value,
        "MKL_NUM_THREADS": value,
        "OPENBLAS_NUM_THREADS": value,
        "NUMEXPR_NUM_THREADS": value,
        "RTDL_EMBREE_THREADS": value,
    }


def _run_row(
    row: dict[str, Any],
    *,
    timeout_scale: float,
    stdout_tail: int,
    stderr_tail: int,
    use_current_python: bool,
    cpu_env: dict[str, str],
) -> dict[str, Any]:
    command = _row_command(row, use_current_python=use_current_python)
    timeout_sec = max(1, int(float(row["timeout_sec"]) * timeout_scale))
    env = os.environ.copy()
    env.update(cpu_env)
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=Path.cwd(),
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            check=False,
        )
        elapsed = time.perf_counter() - start
        semantic = _semantic_stdout_check(completed.stdout)
        status = "pass" if completed.returncode == 0 else "fail"
        if not semantic["stdout_json_parseable"] or semantic["claim_flag_violations"]:
            status = "fail"
        return {
            "app": row["app"],
            "row_id": row["row_id"],
            "route_class": row["route_class"],
            "uses_embree": row["uses_embree"],
            "uses_numba": row["uses_numba"],
            "status": status,
            "returncode": completed.returncode,
            "elapsed_sec": elapsed,
            "timeout_sec": timeout_sec,
            "command": command,
            "cpu_thread_env": cpu_env,
            "semantic_stdout_check": semantic,
            "stdout_tail": _tail(completed.stdout, stdout_tail),
            "stderr_tail": _tail(completed.stderr, stderr_tail),
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        return {
            "app": row["app"],
            "row_id": row["row_id"],
            "route_class": row["route_class"],
            "uses_embree": row["uses_embree"],
            "uses_numba": row["uses_numba"],
            "status": "timeout",
            "returncode": None,
            "elapsed_sec": elapsed,
            "timeout_sec": timeout_sec,
            "command": command,
            "cpu_thread_env": cpu_env,
            "semantic_stdout_check": {
                "stdout_json_parseable": False,
                "stdout_json_error": "timeout before complete stdout was available",
                "claim_flag_violations": (),
            },
            "stdout_tail": _tail(exc.stdout, stdout_tail),
            "stderr_tail": _tail(exc.stderr, stderr_tail),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--only", action="append", default=[], help="App or row_id to run; repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="Only emit the selected registry rows.")
    parser.add_argument("--timeout-scale", type=float, default=1.0)
    parser.add_argument("--stdout-tail", type=int, default=4000)
    parser.add_argument("--stderr-tail", type=int, default=4000)
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        help="CPU thread count for OMP/TBB/MKL/OPENBLAS/NUMEXPR/RTDL_EMBREE_THREADS.",
    )
    parser.add_argument(
        "--literal-python",
        action="store_true",
        help="Use the literal python command from the registry instead of sys.executable.",
    )
    args = parser.parse_args()

    validation = validate_current_embree_cpu_partner_reference()
    rows = list(current_embree_cpu_partner_reference_rows())
    if args.only:
        selected = set(args.only)
        rows = [row for row in rows if row["app"] in selected or row["row_id"] in selected]
    if not rows:
        raise SystemExit("no benchmark rows selected")

    cpu_env = _cpu_thread_env(threads=args.threads)
    result: dict[str, Any] = {
        "version": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
        "claim_boundary": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_CLAIM_BOUNDARY,
        "validation": validation,
        "summary": summarize_current_embree_cpu_partner_reference(tuple(rows)),
        "dry_run": bool(args.dry_run),
        "runtime_environment": {
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_thread_env": cpu_env,
        },
        "release_authorized": False,
        "v2_11_release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "intel_gpu_performance_claim_authorized": False,
        "rows": [],
    }

    if args.dry_run:
        result["rows"] = [
            {
                "app": row["app"],
                "row_id": row["row_id"],
                "purpose": row["purpose"],
                "route_class": row["route_class"],
                "command": list(row["command"]),
                "timeout_sec": row["timeout_sec"],
                "evidence_refs": list(row["evidence_refs"]),
                "uses_embree": row["uses_embree"],
                "uses_numba": row["uses_numba"],
                "requires_embree_library": row["requires_embree_library"],
                "requires_numba": row["requires_numba"],
            }
            for row in rows
        ]
    else:
        for index, row in enumerate(rows, start=1):
            print(
                f"[v2.11-embree-cpu] {index}/{len(rows)} start {row['row_id']} "
                f"timeout={row['timeout_sec']}s threads={cpu_env['RTDL_EMBREE_THREADS']}",
                flush=True,
            )
            row_result = _run_row(
                row,
                timeout_scale=args.timeout_scale,
                stdout_tail=args.stdout_tail,
                stderr_tail=args.stderr_tail,
                use_current_python=not args.literal_python,
                cpu_env=cpu_env,
            )
            print(
                f"[v2.11-embree-cpu] {index}/{len(rows)} done {row['row_id']} "
                f"status={row_result['status']} elapsed={row_result['elapsed_sec']:.3f}s",
                flush=True,
            )
            result["rows"].append(row_result)

    statuses = [row.get("status") for row in result["rows"]]
    result["all_pass"] = None if args.dry_run else all(status == "pass" for status in statuses)

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if args.dry_run or result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
