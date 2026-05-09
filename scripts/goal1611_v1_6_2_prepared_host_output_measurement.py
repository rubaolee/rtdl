#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from scripts import goal1610_v1_6_1_phase_copy_measurement as goal1610


REPORT_STEM = "goal1611_v1_6_2_prepared_host_output_measurement_preflight_2026-05-09"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"

CLAIM_FLAGS = dict(goal1610.CLAIM_FLAGS)


class _CollectKBoundedI64Symbol:
    def __call__(
        self,
        candidate_rows,
        candidate_count,
        row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        rows = []
        for row_index in range(int(candidate_count)):
            start = row_index * int(row_width)
            rows.append(tuple(int(candidate_rows[start + column]) for column in range(int(row_width))))
        canonical = tuple(sorted(set(rows)))
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = len(canonical)
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        if len(canonical) > int(row_capacity):
            ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1
            return 0
        for row_index, row in enumerate(canonical):
            for column_index, value in enumerate(row):
                rows_out[row_index * int(row_width) + column_index] = int(value)
        return 0


def _fake_library(symbol_name: str = "rtdl_fake_collect_k_bounded_i64") -> Any:
    return type("FakeCollectKLibrary", (), {symbol_name: _CollectKBoundedI64Symbol()})()


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def build_candidate_rows(*, unique_rows: int, repeats: int) -> tuple[tuple[int, int], ...]:
    if unique_rows <= 0:
        raise ValueError("unique_rows must be positive")
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    base = tuple((index, (index * 31) % unique_rows) for index in range(unique_rows))
    return tuple(row for _ in range(repeats) for row in base)


def _output_buffer(capacity: int) -> Any:
    if capacity <= 0:
        return None
    return (ctypes.c_int64 * (capacity * 2))()


def build_manifest() -> dict[str, Any]:
    return {
        "goal": "Goal1611",
        "version_slot": "v1.6.2",
        "purpose": "prepared host-output measurement preflight using the Goal1610 phase/copy schema",
        "phase_fields": goal1610.PHASE_FIELDS,
        "copy_count_fields": goal1610.COPY_COUNT_FIELDS,
        "required_metadata_fields": (
            "case_id",
            "status",
            "backend",
            "mode",
            "output_contract",
            "git_commit",
            "host",
            "platform",
            "python",
            "phase_times_sec",
            "copy_counts",
            "claim_flags",
        ),
        "cases": {
            "collect_k_fake_prepared_host_output_smoke": {
                "description": (
                    "Deterministic local fake-native preflight for compatibility rows versus "
                    "prepared host-output plus typed host input."
                ),
                "backend": "fake_native",
                "mode": "compatibility_rows_vs_prepared_host_output",
                "output_contract": "goal1610_phase_copy_record",
                "requires_pod": False,
                "requires_optix": False,
            }
        },
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": (
            "Goal1611 is a local prepared-host-output measurement preflight. "
            "It uses a deterministic fake native symbol to validate schema, "
            "materialization counters, and prepared-buffer measurement plumbing. "
            "It does not authorize performance claims, public speedup wording, "
            "whole-app speedup claims, broad RTX wording, true zero-copy wording, "
            "stable COLLECT_K_BOUNDED promotion, partner tensor handoff, package "
            "install claims, release tags, or release action."
        ),
    }


def _blank_phases() -> dict[str, float | None]:
    return {field: None for field in goal1610.PHASE_FIELDS}


def _blank_copy_counts() -> dict[str, int | None]:
    return {field: None for field in goal1610.COPY_COUNT_FIELDS}


def run_fake_prepared_host_output_case(
    *,
    unique_rows: int = 64,
    repeats: int = 4,
    iterations: int = 5,
) -> dict[str, Any]:
    case_id = "collect_k_fake_prepared_host_output_smoke"
    symbol_name = "rtdl_fake_collect_k_bounded_i64"
    input_start = time.perf_counter()
    candidate_rows = build_candidate_rows(unique_rows=unique_rows, repeats=repeats)
    input_sec = time.perf_counter() - input_start
    capacity = unique_rows
    output_buffer = _output_buffer(capacity)
    descriptor = rt.prepare_collect_k_result_buffer_descriptor(
        capacity=capacity,
        row_width=2,
        backend="fake_native",
        device="cpu",
        owner="rtdl",
        mutability="mutable",
        copy_boundary="prepared_host_buffer_reuse",
    )
    measurement = rt.measure_collect_k_typed_host_input_reuse(
        candidate_rows,
        descriptor,
        output_buffer=output_buffer,
        library=_fake_library(symbol_name),
        symbol_name=symbol_name,
        backend="fake_native",
        row_width=2,
        iterations=iterations,
    )
    phases = _blank_phases()
    baseline_times = [float(row["elapsed_s"]) for row in measurement["baseline_runs"]]
    typed_times = [float(row["elapsed_s"]) for row in measurement["typed_runs"]]
    phases["input_construction_sec"] = input_sec
    phases["probe_packing_sec"] = float(measurement["baseline_elapsed_total_s"])
    phases["launch_sec"] = float(measurement["typed_elapsed_total_s"])
    phases["output_materialization_sec"] = 0.0
    phases["validation_sec"] = 0.0
    phases["total_wrapper_sec"] = float(measurement["baseline_elapsed_total_s"]) + float(
        measurement["typed_elapsed_total_s"]
    )

    counts = _blank_copy_counts()
    counts["input_materialization_count"] = int(measurement["baseline_input_materialization_count"])
    counts["output_materialization_count"] = int(iterations)
    counts["host_to_device_copy_count"] = 0
    counts["device_to_host_copy_count"] = 0
    counts["python_row_count"] = len(candidate_rows)
    counts["thin_view_count"] = 0
    counts["prepared_buffer_reuse_count"] = int(iterations)

    record = {
        "case_id": case_id,
        "status": "pass",
        "backend": "fake_native",
        "mode": "compatibility_rows_vs_prepared_host_output",
        "output_contract": "goal1610_phase_copy_record",
        "unique_rows": unique_rows,
        "candidate_row_count": len(candidate_rows),
        "repeats": repeats,
        "iterations": iterations,
        "git_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "phase_times_sec": phases,
        "copy_counts": counts,
        "path_comparison": {
            "baseline_path": measurement["baseline_path"],
            "prepared_path": measurement["typed_path"],
            "baseline_input_materialization_count": measurement["baseline_input_materialization_count"],
            "prepared_input_materialization_count": measurement["typed_input_materialization_count"],
            "input_materialization_count_delta": measurement["input_materialization_count_delta"],
            "baseline_elapsed_total_s": measurement["baseline_elapsed_total_s"],
            "prepared_elapsed_total_s": measurement["typed_elapsed_total_s"],
            "baseline_elapsed_median_s": statistics.median(baseline_times),
            "prepared_elapsed_median_s": statistics.median(typed_times),
            "prepared_host_output_buffer_reused": all(
                bool(row["output_buffer_reused"]) for row in measurement["typed_runs"]
            ),
            "prepared_output_buffer_address": measurement["prepared_output_buffer_address"],
            "stable_typed_input_buffer_address": len(
                {row.get("input_buffer_address") for row in measurement["typed_runs"]}
            )
            == 1,
            "timing_recorded_for_diagnostics_only": True,
        },
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": build_manifest()["claim_boundary"],
    }
    return validate_record(record)


def validate_record(record: dict[str, Any], *, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or build_manifest()
    for field in manifest["required_metadata_fields"]:
        if field not in record:
            raise ValueError(f"Goal1611 record missing required metadata field: {field}")
    goal1610.validate_record(record, manifest=manifest)
    comparison = record.get("path_comparison")
    if not isinstance(comparison, dict):
        raise ValueError("Goal1611 record missing path_comparison")
    if int(comparison["input_materialization_count_delta"]) < 0:
        raise ValueError("Goal1611 input materialization delta must be non-negative")
    if comparison["timing_recorded_for_diagnostics_only"] is not True:
        raise ValueError("Goal1611 timing must remain diagnostic only")
    if comparison["prepared_host_output_buffer_reused"] is not True:
        raise ValueError("Goal1611 prepared host output buffer must be reused in the preflight path")
    return record


def run_package(*, unique_rows: int = 64, repeats: int = 4, iterations: int = 5) -> dict[str, Any]:
    manifest = build_manifest()
    record = run_fake_prepared_host_output_case(
        unique_rows=unique_rows,
        repeats=repeats,
        iterations=iterations,
    )
    accepted = record["status"] == "pass"
    return {
        "goal": "Goal1611",
        "version_slot": "v1.6.2",
        "status": "accepted_local_prepared_host_output_preflight" if accepted else "not_accepted",
        "accepted": accepted,
        "manifest": manifest,
        "records": (record,),
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": manifest["claim_boundary"],
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1611 v1.6.2 Prepared Host-Output Measurement Preflight",
        "",
        "## Verdict",
        "",
        "ACCEPTED as local prepared-host-output measurement preflight."
        if payload["accepted"]
        else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        "- Version slot: `v1.6.2`",
        "- Hardware: local only; no paid pod or OptiX required for this preflight.",
        "- Backend: deterministic fake native symbol; real Embree/OptiX evidence must be collected separately.",
        "- Timing: recorded for diagnostics only.",
        "",
        "## Records",
        "",
        "| Case | Status | Rows | Iterations | Baseline input materializations | Prepared input materializations | Delta | Prepared buffer reuse count |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for record in payload["records"]:
        comparison = record["path_comparison"]
        counts = record["copy_counts"]
        lines.append(
            "| {case} | {status} | {rows} | {iters} | {base} | {prep} | {delta} | {reuse} |".format(
                case=record["case_id"],
                status=record["status"],
                rows=record["candidate_row_count"],
                iters=record["iterations"],
                base=comparison["baseline_input_materialization_count"],
                prep=comparison["prepared_input_materialization_count"],
                delta=comparison["input_materialization_count_delta"],
                reuse=counts["prepared_buffer_reuse_count"],
            )
        )
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1611 prepared host-output measurement preflight.")
    parser.add_argument("--unique-rows", type=int, default=64)
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_package(unique_rows=args.unique_rows, repeats=args.repeats, iterations=args.iterations)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "accepted": payload["accepted"]}, indent=2))
    return 0 if payload["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
