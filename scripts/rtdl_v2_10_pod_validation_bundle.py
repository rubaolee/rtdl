#!/usr/bin/env python3
"""Run the current v2.10 pod-validation preflight and optional hardware packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_TRUE_FLAGS = (
    "release_authorized",
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


def _tail(text: str, limit: int = 4000) -> str:
    return text if len(text) <= limit else text[-limit:]


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


def _run_step(name: str, command: list[str], *, output_path: Path | None, timeout_sec: int) -> dict[str, Any]:
    print(f"[v2.10-pod-bundle] start {name}", flush=True)
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
        check=False,
    )
    elapsed = time.perf_counter() - start

    parsed: Any | None = None
    parse_error: str | None = None
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        parse_error = str(exc)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if parsed is not None:
            output_path.write_text(json.dumps(parsed, indent=2, sort_keys=True), encoding="utf-8")
        else:
            output_path.write_text(completed.stdout, encoding="utf-8")

    claim_violations = _find_forbidden_true_flags(parsed) if parsed is not None else []
    status = "pass" if completed.returncode == 0 and not claim_violations else "fail"
    print(
        f"[v2.10-pod-bundle] done {name} status={status} elapsed={elapsed:.3f}s",
        flush=True,
    )
    return {
        "name": name,
        "status": status,
        "returncode": completed.returncode,
        "elapsed_sec": elapsed,
        "command": command,
        "output_path": str(output_path) if output_path is not None else None,
        "stdout_json_parseable": parsed is not None,
        "stdout_json_error": parse_error,
        "claim_flag_violations": tuple(claim_violations),
        "stdout_tail": _tail(completed.stdout),
        "stderr_tail": _tail(completed.stderr),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/reports/v2_10_pod_validation_bundle_current"),
    )
    parser.add_argument("--run-front-door", action="store_true", help="run all ten front-door commands")
    parser.add_argument("--run-scale-profile", action="store_true", help="run the scale-profile packet")
    parser.add_argument(
        "--run-partner-comparison",
        action="store_true",
        help="run large-scale CuPy-vs-Numba partner comparison",
    )
    parser.add_argument("--timeout-scale", type=float, default=1.0)
    args = parser.parse_args(argv)

    out = args.output_dir
    py = sys.executable
    steps: list[dict[str, Any]] = []

    steps.append(
        _run_step(
            "source_tree_doctor",
            [py, "scripts/rtdl_source_tree_doctor.py", "--json", "--run-smoke"],
            output_path=out / "source_tree_doctor.json",
            timeout_sec=60,
        )
    )
    steps.append(
        _run_step(
            "benchmark_evidence_index",
            [py, "scripts/rtdl_benchmark_evidence_index.py", "--json"],
            output_path=out / "benchmark_evidence_index.json",
            timeout_sec=60,
        )
    )
    steps.append(
        _run_step(
            "front_door_dry_run",
            [
                py,
                "scripts/goal3823_current_benchmark_front_door_runner.py",
                "--dry-run",
                "--output-json",
                str(out / "front_door_dry_run.json"),
            ],
            output_path=None,
            timeout_sec=60,
        )
    )
    steps.append(
        _run_step(
            "scale_profile_dry_run",
            [
                py,
                "scripts/goal3828_current_benchmark_scale_profile_runner.py",
                "--dry-run",
                "--output-json",
                str(out / "scale_profile_dry_run.json"),
            ],
            output_path=None,
            timeout_sec=60,
        )
    )

    if args.run_front_door:
        steps.append(
            _run_step(
                "front_door_hardware_run",
                [
                    py,
                    "scripts/goal3823_current_benchmark_front_door_runner.py",
                    "--output-json",
                    str(out / "front_door_hardware_summary.json"),
                    "--timeout-scale",
                    str(args.timeout_scale),
                ],
                output_path=None,
                timeout_sec=max(1, int(1600 * args.timeout_scale)),
            )
        )

    if args.run_scale_profile:
        steps.append(
            _run_step(
                "scale_profile_hardware_run",
                [
                    py,
                    "scripts/goal3828_current_benchmark_scale_profile_runner.py",
                    "--output-json",
                    str(out / "scale_profile_summary.json"),
                    "--output-dir",
                    str(out / "scale_profile_outputs"),
                    "--heartbeat-sec",
                    "20",
                    "--timeout-scale",
                    str(args.timeout_scale),
                ],
                output_path=None,
                timeout_sec=max(1, int(3600 * args.timeout_scale)),
            )
        )

    if args.run_partner_comparison:
        steps.append(
            _run_step(
                "large_scale_partner_comparison",
                [
                    py,
                    "scripts/goal4266_large_scale_partner_comparison.py",
                    "--output",
                    str(out / "large_scale_partner_comparison.json"),
                    "--progress-every",
                    "10",
                ],
                output_path=None,
                timeout_sec=3600,
            )
        )

    summary = {
        "status": "pass" if all(step["status"] == "pass" for step in steps) else "fail",
        "output_dir": str(out),
        "hardware_steps_requested": {
            "front_door": args.run_front_door,
            "scale_profile": args.run_scale_profile,
            "partner_comparison": args.run_partner_comparison,
        },
        "steps": steps,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
    }

    out.mkdir(parents=True, exist_ok=True)
    (out / "bundle_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
