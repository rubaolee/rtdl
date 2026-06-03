from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as rayjoin_app


GOAL3220_HARNESS_VERSION = "rtdl.goal3220.spatial_rayjoin_current_best_count_harness.v1"
DEFAULT_WORKLOADS = ("pip", "lsi", "overlay_seed")
GENERIC_PRIMITIVE_BY_WORKLOAD = {
    "pip": "POINT_CLOSED_SHAPE_MEMBERSHIP_2D",
    "lsi": "SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_2D",
    "overlay_seed": "SHAPE_PAIR_RELATION_FLAGS_2D",
}
CLAIM_BOUNDARY = {
    "canonical_harness_candidate": True,
    "tier_a_count_or_parity_only": True,
    "row_overlay_continuation_deferred_tier_b": True,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "rtdl_beats_rayjoin_claim_authorized": False,
    "native_engine_customization": False,
}


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _run_metadata() -> dict[str, Any]:
    gpu = _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"])
    if gpu is None and Path("/usr/bin/nvidia-smi").exists():
        gpu = _check_output(["/usr/bin/nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"])
    return {
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": gpu,
    }


def _summary_count(workload: str, summary: dict[str, Any]) -> int:
    if workload == "pip":
        return int(summary["positive_assignment_count"])
    if workload == "lsi":
        return int(summary["intersection_count"])
    if workload == "overlay_seed":
        return int(summary["pair_dependency_row_count"])
    raise ValueError(f"unsupported workload: {workload}")


def _phase_medians_ms(phases: tuple[dict[str, float], ...]) -> dict[str, float]:
    labels = sorted({label for phase in phases for label in phase})
    return {
        label: statistics.median(float(phase.get(label, 0.0)) for phase in phases) * 1000.0
        for label in labels
    }


def _phase_min_ms(phases: tuple[dict[str, float], ...]) -> dict[str, float]:
    labels = sorted({label for phase in phases for label in phase})
    return {label: min(float(phase.get(label, 0.0)) for phase in phases) * 1000.0 for label in labels}


def _phase_max_ms(phases: tuple[dict[str, float], ...]) -> dict[str, float]:
    labels = sorted({label for phase in phases for label in phase})
    return {label: max(float(phase.get(label, 0.0)) for phase in phases) * 1000.0 for label in labels}


def _run_best_count_route(workload: str, *, dataset: str | None, include_rows: bool) -> dict[str, Any]:
    if workload == "lsi":
        return rayjoin_app.run_rayjoin_prepared_optix_left_id_dense_count_workload(
            workload,
            dataset=dataset,
            include_rows=include_rows,
        )
    return rayjoin_app.run_rayjoin_prepared_optix_workload(
        workload,
        dataset=dataset,
        result_mode="count",
        include_rows=include_rows,
    )


def run_goal3220_spatial_rayjoin_current_best_count_harness(
    *,
    workloads: tuple[str, ...] = DEFAULT_WORKLOADS,
    dataset: str | None = None,
    warmup: int = 2,
    repeat: int = 7,
    fail_fast: bool = False,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for workload in workloads:
        if workload not in DEFAULT_WORKLOADS:
            raise ValueError(f"unsupported Goal3220 workload: {workload}")
        row_started = time.perf_counter()
        try:
            cpu_payload = rayjoin_app.run_rayjoin_workload(
                workload,
                backend="cpu_python_reference",
                dataset=dataset,
                include_rows=False,
            )
            expected_count = _summary_count(workload, cpu_payload["summary"])
            expected_contract = str(cpu_payload["summary"]["output_contract"])
            for _ in range(max(0, int(warmup))):
                _run_best_count_route(workload, dataset=dataset, include_rows=False)
            prepared_payloads = tuple(
                _run_best_count_route(workload, dataset=dataset, include_rows=False)
                for _ in range(int(repeat))
            )
            observed_counts = tuple(int(payload["row_count"]) for payload in prepared_payloads)
            observed_count = observed_counts[-1] if observed_counts else -1
            phases = tuple(dict(payload["phases_sec"]) for payload in prepared_payloads)
            prepared_summary = dict(prepared_payloads[-1]["summary"]) if prepared_payloads else {}
            status = "pass" if observed_counts and all(count == expected_count for count in observed_counts) else "mismatch"
            execution_route = (
                "prepared_optix_left_id_dense_count"
                if workload == "lsi"
                else "prepared_optix"
            )
            row = {
                "workload": workload,
                "status": status,
                "expected_count": int(expected_count),
                "observed_count": int(observed_count),
                "observed_counts": observed_counts,
                "matches_cpu_reference": status == "pass",
                "cpu_output_contract": expected_contract,
                "prepared_output_contract": prepared_summary.get("output_contract"),
                "backend": "optix",
                "execution_route": execution_route,
                "result_mode": "count",
                "include_rows": False,
                "warmup": int(warmup),
                "repeat": int(repeat),
                "generic_primitive": GENERIC_PRIMITIVE_BY_WORKLOAD[workload],
                "uses_prepared_optix_rt_backend": True,
                "phase_medians_ms": _phase_medians_ms(phases),
                "phase_min_ms": _phase_min_ms(phases),
                "phase_max_ms": _phase_max_ms(phases),
                "dataset": prepared_payloads[-1]["dataset"] if prepared_payloads else cpu_payload["dataset"],
                "dataset_note": prepared_payloads[-1]["dataset_note"] if prepared_payloads else cpu_payload["dataset_note"],
                "native_engine_boundary": (
                    "The native engine sees generic prepared point/shape, segment-pair, "
                    "segment-pair left-id count, or shape-pair contracts; RayJoin workload "
                    "interpretation stays in Python."
                ),
                "elapsed_sec": time.perf_counter() - row_started,
            }
        except Exception as exc:
            if fail_fast:
                raise
            row = {
                "workload": workload,
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "elapsed_sec": time.perf_counter() - row_started,
            }
        rows.append(row)
    status = "pass" if rows and all(row["status"] == "pass" for row in rows) else "fail"
    return {
        "goal": "Goal3220",
        "harness_version": GOAL3220_HARNESS_VERSION,
        "status": status,
        "app": "spatial_rayjoin",
        "benchmark_track": "current_best_primitive_first_rt_count_or_parity",
        "workloads": workloads,
        "backend": "optix",
        "execution_route_policy": "lsi_dense_count_else_prepared_optix_count",
        "result_mode": "count",
        "include_rows": False,
        "warmup": int(warmup),
        "repeat": int(repeat),
        "rows": tuple(rows),
        "row_count": len(rows),
        "elapsed_sec": time.perf_counter() - started,
        **_run_metadata(),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _parse_csv_strings(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3220 Spatial RayJoin current-best count harness.")
    parser.add_argument("--workloads", default=",".join(DEFAULT_WORKLOADS))
    parser.add_argument("--dataset")
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args(argv)

    payload = run_goal3220_spatial_rayjoin_current_best_count_harness(
        workloads=_parse_csv_strings(args.workloads),
        dataset=args.dataset,
        warmup=args.warmup,
        repeat=args.repeat,
        fail_fast=args.fail_fast,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
