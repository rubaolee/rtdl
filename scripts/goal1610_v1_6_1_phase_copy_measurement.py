#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_STEM = "goal1610_v1_6_1_phase_copy_measurement_smoke_2026-05-09"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"

PHASE_FIELDS = (
    "input_construction_sec",
    "scene_preparation_sec",
    "probe_packing_sec",
    "host_to_device_transfer_sec",
    "launch_sec",
    "traversal_sec",
    "device_to_host_transfer_sec",
    "output_materialization_sec",
    "validation_sec",
    "python_continuation_sec",
    "query_and_materialize_sec",
    "total_wrapper_sec",
)

COPY_COUNT_FIELDS = (
    "input_materialization_count",
    "output_materialization_count",
    "host_to_device_copy_count",
    "device_to_host_copy_count",
    "python_row_count",
    "thin_view_count",
    "prepared_buffer_reuse_count",
)

CLAIM_FLAGS = {
    "public_speedup_wording_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "broad_rtx_wording_authorized": False,
    "true_zero_copy_authorized": False,
    "stable_collect_k_promotion_authorized": False,
    "partner_tensor_handoff_authorized": False,
    "package_install_claim_authorized": False,
    "release_action_authorized": False,
}


def _python_command(*args: str) -> list[str]:
    return [sys.executable, *args]


def build_manifest() -> dict[str, Any]:
    return {
        "goal": "Goal1610",
        "version_slot": "v1.6.1",
        "purpose": "phase/copy measurement foundation before v1.6.x performance tuning",
        "phase_fields": PHASE_FIELDS,
        "copy_count_fields": COPY_COUNT_FIELDS,
        "required_metadata_fields": (
            "case_id",
            "backend",
            "mode",
            "output_contract",
            "command",
            "git_commit",
            "host",
            "platform",
            "python",
            "claim_flags",
            "status",
            "phase_times_sec",
            "copy_counts",
        ),
        "cases": {
            "hausdorff_cpu_reference_smoke": {
                "description": "Portable local CPU-reference smoke case with app-reported run_phases.",
                "backend": "cpu_python_reference",
                "mode": "compatibility_rows",
                "output_contract": "dict_json_with_run_phases",
                "requires_pod": False,
                "requires_optix": False,
                "command": _python_command(
                    "examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
                    "--backend",
                    "cpu_python_reference",
                ),
            }
        },
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": (
            "Goal1610 defines local phase/copy measurement schema and smoke "
            "execution only. It does not authorize public speedup wording, "
            "whole-app speedup claims, broad RTX wording, true zero-copy wording, "
            "stable COLLECT_K_BOUNDED promotion, partner tensor handoff, package "
            "install claims, release tags, or release action."
        ),
    }


def _run_git_head() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except Exception:
        return "unknown"
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def _blank_phases() -> dict[str, float | None]:
    return {field: None for field in PHASE_FIELDS}


def _blank_copy_counts() -> dict[str, int | None]:
    return {field: None for field in COPY_COUNT_FIELDS}


def _extract_json(stdout: str) -> dict[str, Any] | None:
    stripped = stdout.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            return json.loads(stripped[start : end + 1])
    return None


def _normalize_phases(app_payload: dict[str, Any] | None, elapsed_sec: float) -> dict[str, float | None]:
    phases = _blank_phases()
    if app_payload:
        run_phases = app_payload.get("run_phases")
        if isinstance(run_phases, dict):
            for key, value in run_phases.items():
                if key in phases and isinstance(value, (int, float)):
                    phases[key] = float(value)
    phases["total_wrapper_sec"] = elapsed_sec
    return phases


def _normalize_copy_counts(app_payload: dict[str, Any] | None) -> dict[str, int | None]:
    counts = _blank_copy_counts()
    if not app_payload:
        return counts
    for source_key, target_key in [
        ("row_count", "python_row_count"),
        ("point_count_a", "input_materialization_count"),
    ]:
        value = app_payload.get(source_key)
        if isinstance(value, int):
            counts[target_key] = int(value)
    if isinstance(app_payload.get("directed_a_to_b"), dict):
        row_count = app_payload["directed_a_to_b"].get("row_count")
        if isinstance(row_count, int):
            counts["python_row_count"] = int(row_count)
            counts["output_materialization_count"] = int(row_count)
    return counts


def run_case(case_id: str, *, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or build_manifest()
    cases = manifest["cases"]
    if case_id not in cases:
        raise KeyError(f"unknown Goal1610 case: {case_id}")
    case = cases[case_id]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"src{os.pathsep}."
    start = time.perf_counter()
    completed = subprocess.run(
        case["command"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    elapsed = time.perf_counter() - start
    app_payload = _extract_json(completed.stdout) if completed.returncode == 0 else None
    record = {
        "case_id": case_id,
        "status": "pass" if completed.returncode == 0 else "fail",
        "backend": case["backend"],
        "mode": case["mode"],
        "output_contract": case["output_contract"],
        "requires_pod": bool(case["requires_pod"]),
        "requires_optix": bool(case["requires_optix"]),
        "command": case["command"],
        "returncode": completed.returncode,
        "stdout_excerpt": completed.stdout[:1000],
        "stderr_excerpt": completed.stderr[:1000],
        "git_commit": _run_git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "phase_times_sec": _normalize_phases(app_payload, elapsed),
        "copy_counts": _normalize_copy_counts(app_payload),
        "parsed_app_status": {
            "json_detected": app_payload is not None,
            "matches_oracle": app_payload.get("matches_oracle") if isinstance(app_payload, dict) else None,
            "rt_core_accelerated": app_payload.get("rt_core_accelerated") if isinstance(app_payload, dict) else None,
            "native_continuation_active": app_payload.get("native_continuation_active") if isinstance(app_payload, dict) else None,
        },
        "claim_flags": dict(CLAIM_FLAGS),
    }
    validate_record(record, manifest=manifest)
    return record


def validate_record(record: dict[str, Any], *, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or build_manifest()
    for field in manifest["required_metadata_fields"]:
        if field not in record:
            raise ValueError(f"Goal1610 record missing required metadata field: {field}")
    phases = record.get("phase_times_sec")
    if not isinstance(phases, dict):
        raise ValueError("Goal1610 record missing phase_times_sec")
    for field in PHASE_FIELDS:
        if field not in phases:
            raise ValueError(f"Goal1610 record missing phase field: {field}")
        value = phases[field]
        if value is not None and float(value) < 0.0:
            raise ValueError(f"Goal1610 phase must be non-negative: {field}")
    counts = record.get("copy_counts")
    if not isinstance(counts, dict):
        raise ValueError("Goal1610 record missing copy_counts")
    for field in COPY_COUNT_FIELDS:
        if field not in counts:
            raise ValueError(f"Goal1610 record missing copy-count field: {field}")
        value = counts[field]
        if value is not None and int(value) < 0:
            raise ValueError(f"Goal1610 copy count must be non-negative: {field}")
    flags = record.get("claim_flags")
    if not isinstance(flags, dict):
        raise ValueError("Goal1610 record missing claim_flags")
    for flag in CLAIM_FLAGS:
        if flag not in flags:
            raise ValueError(f"Goal1610 claim_flags missing required flag: {flag}")
    for flag, value in flags.items():
        if value is not False:
            raise ValueError(f"Goal1610 claim flag must remain false: {flag}")
    return record


def run_package(case_ids: tuple[str, ...]) -> dict[str, Any]:
    manifest = build_manifest()
    records = tuple(run_case(case_id, manifest=manifest) for case_id in case_ids)
    accepted = all(record["status"] == "pass" for record in records)
    return {
        "goal": "Goal1610",
        "version_slot": "v1.6.1",
        "status": "accepted_local_measurement_foundation" if accepted else "not_accepted",
        "accepted": accepted,
        "manifest": manifest,
        "records": records,
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": manifest["claim_boundary"],
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1610 v1.6.1 Phase/Copy Measurement Foundation",
        "",
        "## Verdict",
        "",
        "ACCEPTED as local measurement-foundation evidence." if payload["accepted"] else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        "- Version slot: `v1.6.1`",
        "- Purpose: standardize phase timing, copy/materialization counters, command metadata, and claim flags before optimization or pod work.",
        "- Hardware: local only; no paid pod required for this smoke package.",
        "",
        "## Records",
        "",
        "| Case | Backend | Status | Total wrapper sec | Python rows | Input materializations | Output materializations |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for record in payload["records"]:
        phases = record["phase_times_sec"]
        counts = record["copy_counts"]
        lines.append(
            "| {case} | {backend} | {status} | {total:.6f} | {rows} | {inputs} | {outputs} |".format(
                case=record["case_id"],
                backend=record["backend"],
                status=record["status"],
                total=float(phases["total_wrapper_sec"] or 0.0),
                rows=counts["python_row_count"],
                inputs=counts["input_materialization_count"],
                outputs=counts["output_materialization_count"],
            )
        )
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1610 v1.6.1 phase/copy measurement foundation.")
    parser.add_argument("--list", action="store_true", help="List available measurement cases.")
    parser.add_argument("--case", action="append", dest="cases", help="Case id to run; may be repeated.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = build_manifest()
    if args.list:
        print(json.dumps({"cases": sorted(manifest["cases"])}, indent=2))
        return 0
    case_ids = tuple(args.cases or ("hausdorff_cpu_reference_smoke",))
    payload = run_package(case_ids)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "accepted": payload["accepted"]}, indent=2))
    return 0 if payload["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
