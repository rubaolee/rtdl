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

import rtdsl as rt  # noqa: E402
from examples.v2_0.research_benchmarks.raydb_style import (  # noqa: E402
    rtdl_raydb_style_benchmark_app as raydb,
)


CLAIM_BOUNDARY = {
    "internal_diagnostic_only": True,
    "release_authorized": False,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "broad_rt_core_speedup_claim_authorized": False,
    "true_zero_copy_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "automatic_partner_selection_claim_authorized": False,
    "native_engine_customization": False,
}


def _parse_csv_ints(value: str) -> tuple[int, ...]:
    result = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not result or any(item <= 0 for item in result):
        raise argparse.ArgumentTypeError("expected a comma-separated list of positive integers")
    return result


def _parse_csv_modes(value: str) -> tuple[str, ...]:
    result = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(result) - {"count", "sum"})
    if unknown:
        raise argparse.ArgumentTypeError(f"unsupported modes for Goal2950: {unknown}")
    if not result:
        raise argparse.ArgumentTypeError("expected at least one mode")
    return result


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _sequence(value: Any) -> list[Any]:
    if hasattr(value, "detach"):
        return value.detach().cpu().tolist()
    if hasattr(value, "cpu") and hasattr(value.cpu(), "tolist"):
        return value.cpu().tolist()
    if hasattr(value, "tolist"):
        result = value.tolist()
        return result if isinstance(result, list) else [result]
    return list(value)


def _run_payload_front_door_case(
    *,
    row_count: int,
    mode: str,
    generated_groups: int,
    generated_revenue_mod: int,
    warmups: int,
    repeats: int,
    compare_primitive_first: bool,
) -> dict[str, Any]:
    print(
        "[goal2950] case "
        f"rows={row_count} mode={mode} groups={generated_groups} repeats={repeats}",
        flush=True,
    )
    fixture = raydb.make_benchmark_fixture(
        fixture_kind="generated",
        generated_rows=row_count,
        generated_groups=generated_groups,
        generated_revenue_mod=generated_revenue_mod,
    )
    plan = raydb.make_plan(mode)
    table_started = time.perf_counter()
    table_descriptor = raydb.prepare_paper_rt_encoded_table_descriptor(fixture, plan)
    table_prepare_sec = time.perf_counter() - table_started
    workload_started = time.perf_counter()
    workload = raydb._make_paper_rt_encoded_packed_workload(  # noqa: SLF001 - benchmark harness.
        fixture,
        plan,
        mode,
        table_descriptor=table_descriptor,
    )
    workload_build_sec = time.perf_counter() - workload_started
    group_count = len(workload["group_tuples"])
    triangle_count = raydb._packed_or_sequence_count(workload["triangles"])  # noqa: SLF001
    ray_count = raydb._packed_or_sequence_count(workload["rays"])  # noqa: SLF001
    cpu_rows = tuple(rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows)

    prepare_started = time.perf_counter()
    prepared = rt.prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(
        workload["triangles"],
        primitive_group_ids=workload["primitive_group_ids"],
        primitive_values=workload["primitive_values"],
        group_count=group_count,
        partner="cupy",
        group_id_bounds_validation="caller_asserted",
    )
    prepare_sec = time.perf_counter() - prepare_started
    max_rows = triangle_count
    measured: list[dict[str, Any]] = []
    warmup_results: list[dict[str, Any]] = []
    try:
        for index in range(warmups):
            print(f"[goal2950] warmup rows={row_count} mode={mode} {index + 1}/{warmups}", flush=True)
            warmup_results.append(
                _run_once(
                    prepared,
                    workload,
                    mode=mode,
                    max_rows=max_rows,
                    group_count=group_count,
                    cpu_rows=cpu_rows,
                )
            )
        for index in range(repeats):
            print(f"[goal2950] repeat rows={row_count} mode={mode} {index + 1}/{repeats}", flush=True)
            measured.append(
                _run_once(
                    prepared,
                    workload,
                    mode=mode,
                    max_rows=max_rows,
                    group_count=group_count,
                    cpu_rows=cpu_rows,
                )
            )
    finally:
        prepared.close()

    elapsed_values = [float(result["elapsed_sec"]) for result in measured]
    phase_keys = sorted(
        {
            key
            for result in measured
            for key in result["metadata"].get("phase_timing_seconds", {})
        }
    )
    phase_medians = {
        key: _median([float(result["metadata"]["phase_timing_seconds"].get(key, 0.0)) for result in measured])
        for key in phase_keys
    }
    primitive_first: dict[str, Any] | None = None
    if compare_primitive_first:
        print(f"[goal2950] primitive-first comparison rows={row_count} mode={mode}", flush=True)
        primitive = raydb.run_result_mode(
            mode,
            backend=raydb.PAPER_RT_OPTIX_V2_5_PRIMITIVE_FIRST_BACKEND,
            fixture_kind="generated",
            generated_rows=row_count,
            generated_groups=generated_groups,
            generated_revenue_mod=generated_revenue_mod,
            repeat=repeats,
            warmup=warmups,
        )
        primitive_first = {
            "backend": primitive["backend"],
            "elapsed_sec": float(primitive["elapsed_sec"]),
            "matches_cpu_reference": bool(primitive["matches_cpu_reference"]),
            "timings": primitive.get("metadata", {}).get("timings", {}),
        }

    payload_median = _median(elapsed_values)
    primitive_ratio = None
    if primitive_first is not None and primitive_first["elapsed_sec"] > 0.0:
        primitive_ratio = payload_median / float(primitive_first["elapsed_sec"])

    return {
        "row_count": int(row_count),
        "mode": mode,
        "status": "pass" if measured and all(result["matches_cpu_reference"] for result in measured) else "fail",
        "fixture": "generated",
        "generated_groups": int(generated_groups),
        "generated_revenue_mod": int(generated_revenue_mod),
        "table_prepare_sec": float(table_prepare_sec),
        "workload_build_sec": float(workload_build_sec),
        "prepare_scene_payload_sec": float(prepare_sec),
        "triangle_count": int(triangle_count),
        "ray_count": int(ray_count),
        "group_count": int(group_count),
        "max_rows": int(max_rows),
        "deduplicate_primitives": True,
        "payload_front_door_median_sec": payload_median,
        "payload_front_door_min_sec": float(min(elapsed_values)),
        "payload_front_door_max_sec": float(max(elapsed_values)),
        "phase_medians_sec": phase_medians,
        "matches_cpu_reference": all(result["matches_cpu_reference"] for result in measured),
        "primitive_first_comparison": primitive_first,
        "payload_front_door_vs_primitive_first_ratio": primitive_ratio,
        "timed_results": measured,
        "warmup_results": warmup_results,
        "interpretation": (
            "Use this payload-mapped front door when the user needs a generic partner "
            "continuation after RT hit streams. For RayDB count/sum specifically, "
            "primitive-first fused grouped reduction is still expected to win."
        ),
    }


def _run_once(
    prepared: Any,
    workload: dict[str, Any],
    *,
    mode: str,
    max_rows: int,
    group_count: int,
    cpu_rows: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    started = time.perf_counter()
    result = prepared.run(
        workload["rays"],
        max_rows=max_rows,
        deduplicate_primitives=True,
    )
    elapsed = time.perf_counter() - started
    if mode == "count":
        outputs = {"counts": result["group_hit_counts"]}
    elif mode == "sum":
        outputs = {"sums": result["group_payload_sums"]}
    else:  # pragma: no cover - parser blocks this.
        raise ValueError(f"unsupported mode: {mode}")
    rows = raydb._paper_rows_from_v2_5_outputs(  # noqa: SLF001 - benchmark harness.
        mode,
        outputs,
        group_keys=workload["group_keys"],
        group_tuples=workload["group_tuples"],
    )
    return {
        "elapsed_sec": elapsed,
        "summary": result["summary"],
        "metadata": result["metadata"],
        "group_hit_counts": [int(value) for value in result["group_hit_counts"]],
        "group_payload_sums": [float(value) for value in result["group_payload_sums"]],
        "nonzero_groups": sum(1 for value in _sequence(outputs[next(iter(outputs))]) if float(value) != 0.0),
        "matches_cpu_reference": raydb._rows_match_cpu_reference(rows, cpu_rows),  # noqa: SLF001
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    cases = [
        _run_payload_front_door_case(
            row_count=row_count,
            mode=mode,
            generated_groups=args.generated_groups,
            generated_revenue_mod=args.generated_revenue_mod,
            warmups=args.warmups,
            repeats=args.repeats,
            compare_primitive_first=not args.no_compare_primitive_first,
        )
        for row_count in args.row_counts
        for mode in args.modes
    ]
    return {
        "goal": "Goal2950",
        "schema": "rtdl.goal2950.raydb_payload_grouped_sum_front_door_probe.v1",
        "status": "pass" if cases and all(case["status"] == "pass" for case in cases) else "fail",
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "row_counts": list(args.row_counts),
        "modes": list(args.modes),
        "warmups": int(args.warmups),
        "repeats": int(args.repeats),
        "cases": cases,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Goal2950 RayDB use of generic payload-mapped hit-stream grouped-sum front door."
    )
    parser.add_argument("--row-counts", type=_parse_csv_ints, default=(250_000, 1_000_000))
    parser.add_argument("--modes", type=_parse_csv_modes, default=("count", "sum"))
    parser.add_argument("--generated-groups", type=int, default=128)
    parser.add_argument("--generated-revenue-mod", type=int, default=64)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--no-compare-primitive-first", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.generated_groups <= 0 or args.generated_revenue_mod <= 0:
        raise ValueError("generated-groups and generated-revenue-mod must be positive")
    if args.warmups < 0 or args.repeats <= 0:
        raise ValueError("warmups must be non-negative and repeats must be positive")

    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"[goal2950] wrote {args.output} status={payload['status']} cases={len(payload['cases'])}",
        flush=True,
    )
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
