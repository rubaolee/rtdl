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
from scripts import goal1467_v1_5_3_typed_host_buffer_parity as goal1467
from scripts import goal1610_v1_6_1_phase_copy_measurement as goal1610
from scripts import goal1611_v1_6_2_prepared_host_output_measurement as goal1611


REPORT_STEM = "goal1612_v1_6_3_backend_prepared_host_output_bridge_2026-05-09"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"

SUPPORTED_BACKENDS = ("fake_native", "embree", "optix")
CLAIM_FLAGS = dict(goal1610.CLAIM_FLAGS)


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


def _blank_phases() -> dict[str, float | None]:
    return {field: None for field in goal1610.PHASE_FIELDS}


def _blank_copy_counts() -> dict[str, int | None]:
    return {field: None for field in goal1610.COPY_COUNT_FIELDS}


def _backend_symbol_name(backend: str) -> str:
    if backend == "fake_native":
        return "rtdl_fake_collect_k_bounded_i64"
    return goal1467.symbol_name_for_backend(backend)


def _backend_library(backend: str) -> Any:
    if backend == "fake_native":
        return goal1611._fake_library(_backend_symbol_name(backend))
    return goal1467.load_backend_library(backend)


def _output_buffer(capacity: int) -> Any:
    if capacity <= 0:
        return None
    return (ctypes.c_int64 * (capacity * 2))()


def _claim_boundary() -> str:
    return (
        "Goal1612 is a backend bridge for the prepared host-output measurement "
        "path. It may record fake-native, Embree, or OptiX execution/skip "
        "records under the Goal1610/Goal1611 schema. It does not authorize "
        "performance claims, public speedup wording, whole-app speedup claims, "
        "broad RTX wording, true zero-copy wording, stable COLLECT_K_BOUNDED "
        "promotion, partner tensor handoff, package install claims, release "
        "tags, or release action."
    )


def build_manifest() -> dict[str, Any]:
    return {
        "goal": "Goal1612",
        "version_slot": "v1.6.3",
        "purpose": "backend-ready prepared host-output measurement bridge",
        "supported_backends": SUPPORTED_BACKENDS,
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
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": _claim_boundary(),
    }


def _skip_record(backend: str, reason: str, *, unique_rows: int, repeats: int, iterations: int) -> dict[str, Any]:
    return {
        "case_id": f"collect_k_{backend}_prepared_host_output_bridge",
        "status": "skipped",
        "backend": backend,
        "mode": "backend_prepared_host_output_bridge",
        "output_contract": "goal1610_phase_copy_record",
        "unique_rows": unique_rows,
        "candidate_row_count": unique_rows * repeats,
        "repeats": repeats,
        "iterations": iterations,
        "git_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "phase_times_sec": _blank_phases(),
        "copy_counts": _blank_copy_counts(),
        "skip_reason": reason,
        "path_comparison": None,
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": _claim_boundary(),
    }


def _fail_record(backend: str, error: str, *, unique_rows: int, repeats: int, iterations: int) -> dict[str, Any]:
    record = _skip_record(
        backend,
        "",
        unique_rows=unique_rows,
        repeats=repeats,
        iterations=iterations,
    )
    record["status"] = "fail"
    record.pop("skip_reason", None)
    record["error"] = error
    return record


def run_backend_case(
    backend: str,
    *,
    unique_rows: int = 64,
    repeats: int = 4,
    iterations: int = 5,
    backend_library: Any | None = None,
) -> dict[str, Any]:
    if backend not in SUPPORTED_BACKENDS:
        raise ValueError(f"unsupported Goal1612 backend: {backend}")
    input_start = time.perf_counter()
    candidate_rows = goal1611.build_candidate_rows(unique_rows=unique_rows, repeats=repeats)
    input_sec = time.perf_counter() - input_start
    capacity = unique_rows
    output_buffer = _output_buffer(capacity)
    try:
        library = backend_library if backend_library is not None else _backend_library(backend)
        symbol_name = _backend_symbol_name(backend)
        descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=capacity,
            row_width=2,
            backend=backend,
            device="cpu",
            owner="rtdl",
            mutability="mutable",
            copy_boundary="prepared_host_buffer_reuse",
        )
        measurement = rt.measure_collect_k_typed_host_input_reuse(
            candidate_rows,
            descriptor,
            output_buffer=output_buffer,
            library=library,
            symbol_name=symbol_name,
            backend=backend,
            row_width=2,
            iterations=iterations,
        )
    except Exception as exc:
        if goal1467.is_backend_unavailable(exc):
            return validate_record(
                _skip_record(
                    backend,
                    f"{type(exc).__name__}: {exc}",
                    unique_rows=unique_rows,
                    repeats=repeats,
                    iterations=iterations,
                )
            )
        return validate_record(
            _fail_record(
                backend,
                f"{type(exc).__name__}: {exc}",
                unique_rows=unique_rows,
                repeats=repeats,
                iterations=iterations,
            )
        )

    baseline_times = [float(row["elapsed_s"]) for row in measurement["baseline_runs"]]
    typed_times = [float(row["elapsed_s"]) for row in measurement["typed_runs"]]
    phases = _blank_phases()
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
        "case_id": f"collect_k_{backend}_prepared_host_output_bridge",
        "status": "pass",
        "backend": backend,
        "mode": "backend_prepared_host_output_bridge",
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
            "backend_symbol_name": symbol_name,
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
        "claim_boundary": _claim_boundary(),
    }
    return validate_record(record)


def validate_record(record: dict[str, Any], *, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or build_manifest()
    for field in manifest["required_metadata_fields"]:
        if field not in record:
            raise ValueError(f"Goal1612 record missing required metadata field: {field}")
    goal1610.validate_record(record, manifest=manifest)
    if record["status"] == "skipped":
        if not record.get("skip_reason"):
            raise ValueError("Goal1612 skipped record requires skip_reason")
        return record
    if record["status"] == "fail":
        if not record.get("error"):
            raise ValueError("Goal1612 failed record requires error")
        return record
    if record["status"] != "pass":
        raise ValueError("Goal1612 record status must be pass, skipped, or fail")
    comparison = record.get("path_comparison")
    if not isinstance(comparison, dict):
        raise ValueError("Goal1612 pass record missing path_comparison")
    if int(comparison["input_materialization_count_delta"]) < 0:
        raise ValueError("Goal1612 input materialization delta must be non-negative")
    if comparison["timing_recorded_for_diagnostics_only"] is not True:
        raise ValueError("Goal1612 timing must remain diagnostic only")
    if comparison["prepared_host_output_buffer_reused"] is not True:
        raise ValueError("Goal1612 prepared host output buffer must be reused")
    return record


def run_package(
    *,
    backends: tuple[str, ...] = ("fake_native", "embree", "optix"),
    required_backends: tuple[str, ...] = ("fake_native",),
    unique_rows: int = 64,
    repeats: int = 4,
    iterations: int = 5,
    backend_libraries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    libraries = dict(backend_libraries or {})
    records = tuple(
        run_backend_case(
            backend,
            unique_rows=unique_rows,
            repeats=repeats,
            iterations=iterations,
            backend_library=libraries.get(backend),
        )
        for backend in backends
    )
    failed = tuple(record for record in records if record["status"] == "fail")
    skipped_required = tuple(
        record for record in records if record["backend"] in required_backends and record["status"] == "skipped"
    )
    accepted = not failed and not skipped_required and any(record["status"] == "pass" for record in records)
    manifest = build_manifest()
    return {
        "goal": "Goal1612",
        "version_slot": "v1.6.3",
        "status": "accepted_backend_bridge" if accepted else "not_accepted",
        "accepted": accepted,
        "backends": backends,
        "required_backends": required_backends,
        "manifest": manifest,
        "records": records,
        "failed": failed,
        "skipped_required": skipped_required,
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": manifest["claim_boundary"],
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1612 v1.6.3 Backend Prepared Host-Output Bridge",
        "",
        "## Verdict",
        "",
        "ACCEPTED as backend bridge evidence." if payload["accepted"] else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        "- Version slot: `v1.6.3`",
        f"- Backends: `{', '.join(payload['backends'])}`",
        f"- Required backends: `{', '.join(payload['required_backends'])}`",
        "- Real backend skips are allowed only when the backend is not required.",
        "- Timing is diagnostic only.",
        "",
        "## Records",
        "",
        "| Backend | Status | Rows | Iterations | Baseline input materializations | Prepared input materializations | Delta | Skip reason |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for record in payload["records"]:
        comparison = record.get("path_comparison") or {}
        lines.append(
            "| {backend} | {status} | {rows} | {iters} | {base} | {prep} | {delta} | {skip} |".format(
                backend=record["backend"],
                status=record["status"],
                rows=record["candidate_row_count"],
                iters=record["iterations"],
                base=comparison.get("baseline_input_materialization_count", ""),
                prep=comparison.get("prepared_input_materialization_count", ""),
                delta=comparison.get("input_materialization_count_delta", ""),
                skip=str(record.get("skip_reason", "")).replace("\n", " ")[:120],
            )
        )
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1612 backend prepared host-output bridge.")
    parser.add_argument("--backends", nargs="+", default=list(("fake_native", "embree", "optix")))
    parser.add_argument("--required-backends", nargs="*", default=["fake_native"])
    parser.add_argument("--unique-rows", type=int, default=64)
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_package(
        backends=tuple(args.backends),
        required_backends=tuple(args.required_backends),
        unique_rows=args.unique_rows,
        repeats=args.repeats,
        iterations=args.iterations,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "accepted": payload["accepted"]}, indent=2))
    return 0 if payload["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
