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
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from scripts import goal1467_v1_5_3_typed_host_buffer_parity as goal1467
from scripts import goal1610_v1_6_1_phase_copy_measurement as goal1610
from scripts import goal1611_v1_6_2_prepared_host_output_measurement as goal1611


REPORT_STEM = "goal1615_v1_6_4_collect_k_reduced_copy_benchmark_2026-05-09"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"

SUPPORTED_BACKENDS = ("fake_native", "embree", "optix")
CLAIM_FLAGS = dict(goal1610.CLAIM_FLAGS)


@dataclass(frozen=True)
class BenchmarkScale:
    unique_rows: int
    repeats: int
    iterations: int


DEFAULT_SCALES = (
    BenchmarkScale(unique_rows=32, repeats=4, iterations=4),
    BenchmarkScale(unique_rows=128, repeats=4, iterations=4),
    BenchmarkScale(unique_rows=512, repeats=2, iterations=4),
)


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


def _symbol_name(backend: str) -> str:
    if backend == "fake_native":
        return "rtdl_fake_collect_k_bounded_i64"
    return goal1467.symbol_name_for_backend(backend)


def _library(backend: str) -> Any:
    if backend == "fake_native":
        return goal1611._fake_library(_symbol_name(backend))
    return goal1467.load_backend_library(backend)


def _output_buffer(capacity: int) -> Any:
    if capacity <= 0:
        return None
    return (ctypes.c_int64 * (capacity * 2))()


def _claim_boundary() -> str:
    return (
        "Goal1615 is a collect-k reduced-copy/prepared-output benchmark evidence "
        "package. The accepted evidence is copy/materialization-count reduction "
        "under the measured same-contract wrapper paths. Timing is diagnostic "
        "only and does not authorize public speedup wording, whole-app speedup "
        "claims, broad RTX/GPU wording, true zero-copy wording, stable "
        "COLLECT_K_BOUNDED promotion, release tags, or release action."
    )


def build_manifest() -> dict[str, Any]:
    return {
        "goal": "Goal1615",
        "version_slot": "v1.6.4_reduced_copy_benchmark_addendum",
        "purpose": "collect-k reduced-copy/prepared-output benchmark evidence",
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


def _skip_record(backend: str, scale: BenchmarkScale, reason: str) -> dict[str, Any]:
    return {
        "case_id": f"collect_k_{backend}_{scale.unique_rows}_rows_reduced_copy_benchmark",
        "status": "skipped",
        "backend": backend,
        "mode": "collect_k_reduced_copy_prepared_output_benchmark",
        "output_contract": "goal1610_phase_copy_record",
        "unique_rows": scale.unique_rows,
        "candidate_row_count": scale.unique_rows * scale.repeats,
        "repeats": scale.repeats,
        "iterations": scale.iterations,
        "git_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "phase_times_sec": _blank_phases(),
        "copy_counts": _blank_copy_counts(),
        "skip_reason": reason,
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": _claim_boundary(),
    }


def _fail_record(backend: str, scale: BenchmarkScale, error: str) -> dict[str, Any]:
    record = _skip_record(backend, scale, "")
    record["status"] = "fail"
    record.pop("skip_reason", None)
    record["error"] = error
    return record


def run_backend_scale(backend: str, scale: BenchmarkScale, *, library: Any | None = None) -> dict[str, Any]:
    if backend not in SUPPORTED_BACKENDS:
        raise ValueError(f"unsupported Goal1615 backend: {backend}")
    input_start = time.perf_counter()
    candidate_rows = goal1611.build_candidate_rows(unique_rows=scale.unique_rows, repeats=scale.repeats)
    input_sec = time.perf_counter() - input_start
    capacity = scale.unique_rows
    output_buffer = _output_buffer(capacity)
    try:
        active_library = library if library is not None else _library(backend)
        symbol_name = _symbol_name(backend)
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
            library=active_library,
            symbol_name=symbol_name,
            backend=backend,
            row_width=2,
            iterations=scale.iterations,
        )
    except Exception as exc:
        if goal1467.is_backend_unavailable(exc):
            return validate_record(_skip_record(backend, scale, f"{type(exc).__name__}: {exc}"))
        return validate_record(_fail_record(backend, scale, f"{type(exc).__name__}: {exc}"))

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
    counts["output_materialization_count"] = int(scale.iterations)
    counts["host_to_device_copy_count"] = 0
    counts["device_to_host_copy_count"] = 0
    counts["python_row_count"] = len(candidate_rows)
    counts["thin_view_count"] = 0
    counts["prepared_buffer_reuse_count"] = int(scale.iterations)
    record = {
        "case_id": f"collect_k_{backend}_{scale.unique_rows}_rows_reduced_copy_benchmark",
        "status": "pass",
        "backend": backend,
        "mode": "collect_k_reduced_copy_prepared_output_benchmark",
        "output_contract": "goal1610_phase_copy_record",
        "unique_rows": scale.unique_rows,
        "candidate_row_count": len(candidate_rows),
        "repeats": scale.repeats,
        "iterations": scale.iterations,
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
            "stable_typed_input_buffer_address": len(
                {row.get("input_buffer_address") for row in measurement["typed_runs"]}
            )
            == 1,
            "prepared_output_buffer_address": measurement["prepared_output_buffer_address"],
            "timing_recorded_for_diagnostics_only": True,
            "accepted_metric": "input_materialization_count_delta",
        },
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": _claim_boundary(),
    }
    return validate_record(record)


def validate_record(record: dict[str, Any], *, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or build_manifest()
    for field in manifest["required_metadata_fields"]:
        if field not in record:
            raise ValueError(f"Goal1615 record missing required metadata field: {field}")
    goal1610.validate_record(record, manifest=manifest)
    if record["status"] == "skipped":
        if not record.get("skip_reason"):
            raise ValueError("Goal1615 skipped record requires skip_reason")
        return record
    if record["status"] == "fail":
        if not record.get("error"):
            raise ValueError("Goal1615 failed record requires error")
        return record
    if record["status"] != "pass":
        raise ValueError("Goal1615 record status must be pass, skipped, or fail")
    comparison = record.get("path_comparison")
    if not isinstance(comparison, dict):
        raise ValueError("Goal1615 pass record missing path_comparison")
    if int(comparison["baseline_input_materialization_count"]) != int(record["iterations"]):
        raise ValueError("Goal1615 baseline materialization count must equal iterations")
    if int(comparison["prepared_input_materialization_count"]) != 1:
        raise ValueError("Goal1615 prepared typed input path must materialize once")
    if int(comparison["input_materialization_count_delta"]) != int(record["iterations"]) - 1:
        raise ValueError("Goal1615 input materialization delta mismatch")
    if comparison["prepared_host_output_buffer_reused"] is not True:
        raise ValueError("Goal1615 prepared host output buffer must be reused")
    if comparison["stable_typed_input_buffer_address"] is not True:
        raise ValueError("Goal1615 typed input buffer address must be stable")
    if comparison["timing_recorded_for_diagnostics_only"] is not True:
        raise ValueError("Goal1615 timing must remain diagnostic only")
    if comparison["accepted_metric"] != "input_materialization_count_delta":
        raise ValueError("Goal1615 accepted metric must remain materialization-count delta")
    return record


def run_package(
    *,
    backends: tuple[str, ...] = ("fake_native",),
    required_backends: tuple[str, ...] = ("fake_native",),
    scales: tuple[BenchmarkScale, ...] = DEFAULT_SCALES,
    backend_libraries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    libraries = dict(backend_libraries or {})
    records = tuple(
        run_backend_scale(backend, scale, library=libraries.get(backend))
        for backend in backends
        for scale in scales
    )
    failed = tuple(record for record in records if record["status"] == "fail")
    skipped_required = tuple(
        record for record in records if record["backend"] in required_backends and record["status"] == "skipped"
    )
    passed = tuple(record for record in records if record["status"] == "pass")
    accepted = not failed and not skipped_required and bool(passed)
    return {
        "goal": "Goal1615",
        "version_slot": "v1.6.4_reduced_copy_benchmark_addendum",
        "status": "accepted_reduced_copy_benchmark_evidence" if accepted else "not_accepted",
        "accepted": accepted,
        "primitive": "COLLECT_K_BOUNDED",
        "scope": "same_contract_input_materialization_delta_with_prepared_host_output",
        "manifest": build_manifest(),
        "backends": backends,
        "required_backends": required_backends,
        "scale_count": len(scales),
        "records": records,
        "failed": failed,
        "skipped_required": skipped_required,
        "claim_flags": dict(CLAIM_FLAGS),
        "claim_boundary": _claim_boundary(),
    }


def validate_package(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["goal"] != "Goal1615":
        raise ValueError("Goal1615 payload must identify Goal1615")
    if payload["primitive"] != "COLLECT_K_BOUNDED":
        raise ValueError("Goal1615 must target COLLECT_K_BOUNDED")
    if payload["accepted"] is not True:
        raise ValueError("Goal1615 accepted package cannot contain failures or required skips")
    if not payload["records"]:
        raise ValueError("Goal1615 accepted package requires records")
    for record in payload["records"]:
        validate_record(record, manifest=payload["manifest"])
    for flag, value in payload["claim_flags"].items():
        if value is not False:
            raise ValueError(f"Goal1615 claim flag must remain false: {flag}")
    boundary = payload["claim_boundary"]
    for phrase in (
        "copy/materialization-count reduction",
        "Timing is diagnostic only",
        "does not authorize public speedup wording",
        "true zero-copy wording",
        "stable COLLECT_K_BOUNDED promotion",
    ):
        if phrase not in boundary:
            raise ValueError("Goal1615 claim boundary is incomplete")
    return payload


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1615 v1.6.4 COLLECT_K_BOUNDED Reduced-Copy Benchmark",
        "",
        "## Verdict",
        "",
        "ACCEPTED as reduced-copy/prepared-output benchmark evidence."
        if payload["accepted"]
        else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        f"- Primitive: `{payload['primitive']}`",
        f"- Scope: `{payload['scope']}`",
        f"- Backends: `{', '.join(payload['backends'])}`",
        f"- Required backends: `{', '.join(payload['required_backends'])}`",
        "- Accepted metric: `input_materialization_count_delta`",
        "- Timing is diagnostic only.",
        "",
        "## Records",
        "",
        "| Backend | Unique rows | Candidate rows | Iterations | Baseline materializations | Prepared materializations | Delta | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for record in payload["records"]:
        comparison = record.get("path_comparison") or {}
        lines.append(
            "| {backend} | {unique} | {rows} | {iters} | {base} | {prepared} | {delta} | {status} |".format(
                backend=record["backend"],
                unique=record["unique_rows"],
                rows=record["candidate_row_count"],
                iters=record["iterations"],
                base=comparison.get("baseline_input_materialization_count", ""),
                prepared=comparison.get("prepared_input_materialization_count", ""),
                delta=comparison.get("input_materialization_count_delta", ""),
                status=record["status"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _parse_scales(raw: list[str] | None) -> tuple[BenchmarkScale, ...]:
    if not raw:
        return DEFAULT_SCALES
    scales = []
    for item in raw:
        unique, repeats, iterations = (int(part) for part in item.split(":"))
        scales.append(BenchmarkScale(unique_rows=unique, repeats=repeats, iterations=iterations))
    return tuple(scales)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1615 collect-k reduced-copy benchmark evidence.")
    parser.add_argument("--backends", nargs="+", default=["fake_native"])
    parser.add_argument("--required-backends", nargs="*", default=["fake_native"])
    parser.add_argument(
        "--scale",
        action="append",
        help="Scale as unique_rows:repeats:iterations. May be supplied multiple times.",
    )
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = validate_package(
        run_package(
            backends=tuple(args.backends),
            required_backends=tuple(args.required_backends),
            scales=_parse_scales(args.scale),
        )
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "accepted": payload["accepted"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
