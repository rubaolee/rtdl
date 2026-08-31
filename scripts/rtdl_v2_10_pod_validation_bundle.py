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


def _parse_json_text(text: str) -> tuple[Any | None, str | None]:
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


def _load_json_artifact(path: Path | None) -> tuple[Any | None, str | None]:
    if path is None:
        return None, None
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"artifact not found: {path}"
    except json.JSONDecodeError as exc:
        return None, str(exc)


def _run_step(
    name: str,
    command: list[str],
    *,
    output_path: Path | None,
    timeout_sec: int,
    json_artifact_path: Path | None = None,
) -> dict[str, Any]:
    print(f"[v2.10-pod-bundle] start {name}", flush=True)
    start = time.perf_counter()
    import os
    env = os.environ.copy()
    for k in list(env.keys()):
        if k.upper() == "PYTHONPATH":
            pythonpath = env.pop(k)
            break
    else:
        pythonpath = ""
    src_path = str(ROOT / "src")
    root_path = str(ROOT)
    if pythonpath:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{root_path}{os.pathsep}{pythonpath}"
    else:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{root_path}"

    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
        check=False,
    )
    elapsed = time.perf_counter() - start

    stdout_parsed, stdout_parse_error = _parse_json_text(completed.stdout)
    artifact_parsed, artifact_parse_error = _load_json_artifact(json_artifact_path)
    if stdout_parsed is not None:
        parsed = stdout_parsed
        json_source = "stdout"
        json_error = None
    elif artifact_parsed is not None:
        parsed = artifact_parsed
        json_source = "artifact"
        json_error = None
    else:
        parsed = None
        json_source = None
        json_error = artifact_parse_error or stdout_parse_error

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if stdout_parsed is not None:
            output_path.write_text(json.dumps(stdout_parsed, indent=2, sort_keys=True), encoding="utf-8")
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
        "json_artifact_path": str(json_artifact_path) if json_artifact_path is not None else None,
        "stdout_json_parseable": stdout_parsed is not None,
        "stdout_json_error": stdout_parse_error,
        "json_parseable": parsed is not None,
        "json_source": json_source,
        "json_error": json_error,
        "claim_flag_violations": tuple(claim_violations),
        "stdout_tail": _tail(completed.stdout),
        "stderr_tail": _tail(completed.stderr),
    }


def _rayjoin_public_cdb_args(args: argparse.Namespace) -> list[str]:
    fixture_args: list[str] = []
    if args.materialize_rayjoin_public_cdb:
        fixture_args.append("--materialize-rayjoin-public-cdb")
    if args.rayjoin_public_cdb_dir is not None:
        fixture_args.extend(["--rayjoin-public-cdb-dir", str(args.rayjoin_public_cdb_dir)])
    return fixture_args


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
    parser.add_argument(
        "--materialize-rayjoin-public-cdb",
        action="store_true",
        help=(
            "Explicitly download/materialize the bounded RayJoin public-CDB fixture "
            "before scale-profile hardware runs."
        ),
    )
    parser.add_argument(
        "--rayjoin-public-cdb-dir",
        type=Path,
        default=None,
        help="Directory containing or receiving the bounded RayJoin public-CDB fixture.",
    )
    parser.add_argument("--timeout-scale", type=float, default=1.0)
    args = parser.parse_args(argv)

    out = args.output_dir
    py = sys.executable
    rayjoin_fixture_args = _rayjoin_public_cdb_args(args)
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
            json_artifact_path=out / "front_door_dry_run.json",
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
            ]
            + rayjoin_fixture_args,
            output_path=None,
            json_artifact_path=out / "scale_profile_dry_run.json",
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
                json_artifact_path=out / "front_door_hardware_summary.json",
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
                ]
                + rayjoin_fixture_args,
                output_path=None,
                json_artifact_path=out / "scale_profile_summary.json",
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
                json_artifact_path=out / "large_scale_partner_comparison.json",
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
        "rayjoin_public_cdb_fixture_request": {
            "materialize_requested": bool(args.materialize_rayjoin_public_cdb),
            "data_dir": str(args.rayjoin_public_cdb_dir) if args.rayjoin_public_cdb_dir is not None else None,
            "download_hidden_by_bundle": False,
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
