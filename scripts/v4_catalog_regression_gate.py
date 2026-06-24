from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_CLAIM_FLAGS = (
    "release_claim_authorized",
    "broad_v4_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "tier3_callback_claim_authorized",
    "cupy_performance_claim_authorized",
    "embedding_c_abi_claim_authorized",
    "non_python_host_binding_claim_authorized",
    "app_specific_native_kernel_authorized",
)


def _run_json(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not return JSON: {' '.join(command)}\n{proc.stdout}") from exc


def _git_value(*args: str) -> str | None:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _forbidden_claim_true_paths(value: Any, path: str = "payload") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_CLAIM_FLAGS and item is not False:
                failures.append(child_path)
            failures.extend(_forbidden_claim_true_paths(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            failures.extend(_forbidden_claim_true_paths(item, f"{path}[{index}]"))
    return failures


def _example_commands(mode: str, copies: int, ray_count: int) -> list[tuple[str, list[str]]]:
    python = sys.executable
    dry = mode == "dry-run"
    commands: list[tuple[str, list[str]]] = [
        (
            "fixed_radius",
            [
                python,
                "future/v4/examples/fixed_radius_torch_device_arrays.py",
                "--copies",
                str(copies),
            ],
        ),
        (
            "closest_hit_grouped_argmin",
            [
                python,
                "future/v4/examples/closest_hit_grouped_argmin_torch_device_arrays.py",
                "--ray-count",
                str(ray_count),
            ],
        ),
        (
            "ray_triangle_any_hit_flags",
            [
                python,
                "future/v4/examples/ray_triangle_any_hit_flags_torch_device_arrays.py",
                "--ray-count",
                str(ray_count),
            ],
        ),
        (
            "v4_frontdoor_quickstart",
            [python, "future/v4/examples/v4_frontdoor_quickstart.py"],
        ),
        (
            "operator_callback_planning_tier2",
            [python, "future/v4/examples/operator_callback_planning.py", "--case", "tier2"],
        ),
        (
            "operator_callback_planning_scalar_callback",
            [python, "future/v4/examples/operator_callback_planning.py", "--case", "scalar-callback"],
        ),
        (
            "operator_callback_planning_complex_callback",
            [python, "future/v4/examples/operator_callback_planning.py", "--case", "complex-callback"],
        ),
    ]
    if dry:
        for _, command in commands[:3]:
            command.append("--dry-run")
    return commands


def _validate_payload(name: str, payload: dict[str, Any], mode: str) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if payload.get("release_claim_authorized") is not False:
        failures.append("release_claim_authorized_missing_or_not_false")
    if payload.get("tier3_callback_claim_authorized") is not False:
        failures.append("tier3_callback_claim_authorized_missing_or_not_false")
    for path in _forbidden_claim_true_paths(payload):
        failures.append(f"forbidden_claim_flag_true:{path}")
    if name in {"fixed_radius", "closest_hit_grouped_argmin", "ray_triangle_any_hit_flags"}:
        expected_status = "dry_run" if mode == "dry-run" else "measured"
        if payload.get("status") != expected_status:
            failures.append(f"status_not_{expected_status}")
        if mode == "gpu" and payload.get("correctness_passed") is not True:
            failures.append("correctness_not_true")
    elif name == "v4_frontdoor_quickstart":
        if payload.get("status") != "ok":
            failures.append("quickstart_status_not_ok")
        if payload.get("measured_surface_count") != 3:
            failures.append("quickstart_surface_count_not_3")
    elif name == "operator_callback_planning_tier2":
        if payload.get("status") != "tier2_measured_ready":
            failures.append("tier2_planner_not_ready")
        if payload.get("api_surface") not in {
            "v4_fixed_radius_count_threshold_2d_device_arrays",
            "v4_closest_hit_grouped_argmin_3d_device_arrays",
            "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        }:
            failures.append("tier2_planner_surface_not_measured")
        if payload.get("measured_partner") is not True:
            failures.append("tier2_planner_partner_not_measured")
    elif name == "operator_callback_planning_scalar_callback":
        if payload.get("status") != "tier3_spike_only_not_v4_0_release_surface":
            failures.append("scalar_callback_not_tier3_spike_only")
        if payload.get("api_surface") is not None:
            failures.append("scalar_callback_has_api_surface")
        if payload.get("tier3_spike_authorized") is not True:
            failures.append("scalar_callback_spike_not_marked")
    elif name == "operator_callback_planning_complex_callback":
        if payload.get("status") != "rejected_action_shaped_callback_deferred":
            failures.append("complex_callback_not_rejected")
        if payload.get("api_surface") is not None:
            failures.append("complex_callback_has_api_surface")
    return (not failures, failures)


def _write_markdown(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V4 Catalog Regression Gate",
        "",
        "Status: generated development gate, not a release authorization",
        "",
        f"- mode: `{result['mode']}`",
        f"- status: `{result['status']}`",
        f"- release authorized: `{result['release_authorized']}`",
        "",
        "| Example | Status | Passed |",
        "| --- | --- | --- |",
    ]
    for row in result["examples"]:
        lines.append(f"| `{row['name']}` | `{row['payload_status']}` | `{row['passed']}` |")
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "This gate does not authorize V4 release, broad speedup wording, Tier-3 callback/PTX support, raw OptiX callbacks, CuPy performance claims, embedding/C-ABI, non-Python host binding claims, or app-specific native kernels.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V4 catalog example regression gate.")
    parser.add_argument("--mode", choices=("dry-run", "gpu"), default="dry-run")
    parser.add_argument("--copies", type=int, default=8192)
    parser.add_argument("--ray-count", type=int, default=8192)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for name, command in _example_commands(args.mode, int(args.copies), int(args.ray_count)):
        payload = _run_json(command)
        passed, failures = _validate_payload(name, payload, args.mode)
        rows.append(
            {
                "name": name,
                "command": command,
                "payload_status": payload.get("status"),
                "passed": passed,
                "failures": failures,
                "payload": payload,
            }
        )
    all_passed = all(row["passed"] for row in rows)
    result = {
        "schema": "rtdl.v4.catalog_regression_gate.v1",
        "mode": args.mode,
        "status": "passed" if all_passed else "failed",
        "git_commit": _git_value("rev-parse", "HEAD"),
        "git_branch": _git_value("rev-parse", "--abbrev-ref", "HEAD"),
        "native_library": os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB"),
        "release_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "non_python_host_binding_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
        "examples": rows,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(args.md_out, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
