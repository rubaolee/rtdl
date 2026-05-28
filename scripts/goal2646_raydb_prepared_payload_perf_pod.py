#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb
from scripts.goal2645_raydb_rt_perf_pod import _environment_snapshot
from scripts.goal2645_raydb_rt_perf_pod import _parse_csv_ints
from scripts.goal2645_raydb_rt_perf_pod import _parse_csv_text


DEFAULT_JSON = ROOT / "docs/reports/goal2646_raydb_prepared_payload_query_perf_2026-05-27.json"
DEFAULT_MD = ROOT / "docs/reports/goal2646_raydb_prepared_payload_query_perf_2026-05-27.md"


def _measure_mode(
    mode: str,
    copies: int,
    repeat: int,
    warmup: int,
    ray_batch_mode: str,
    args: argparse.Namespace,
    *,
    fixture: dict[str, Any] | None = None,
    table_descriptor: dict[str, Any] | None = None,
    table_descriptor_prepare_sec: float = 0.0,
) -> dict[str, Any]:
    if ray_batch_mode not in {"none", "host", "cupy", "torch"}:
        raise ValueError("ray_batch_mode must be one of: none, host, cupy, torch")
    if args.backend == "embree" and ray_batch_mode in {"cupy", "torch"}:
        raise ValueError("Embree prepared timing supports ray_batch_mode 'none' or 'host'")
    if fixture is None:
        fixture = raydb.make_benchmark_fixture(
            fixture_kind=args.fixture_kind,
            copies=copies,
            generated_rows=args.generated_rows,
            generated_groups=args.generated_groups,
            generated_revenue_mod=args.generated_revenue_mod,
        )
    plan = raydb.make_plan(mode)

    workload_start = time.perf_counter()
    workload = raydb._make_paper_rt_encoded_packed_workload(
        fixture,
        plan,
        mode,
        table_descriptor=table_descriptor,
    )
    workload_sec = time.perf_counter() - workload_start

    prepare_start = time.perf_counter()
    prepared = rt.prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
        workload["triangles"],
        primitive_group_ids=workload["primitive_group_ids"],
        primitive_values=workload["primitive_values"],
        group_count=len(workload["group_tuples"]),
        backend=args.backend,
    )
    prepare_sec = time.perf_counter() - prepare_start
    prepared_rays = None
    prepared_rays_sec = 0.0
    partner_ray_column_build_sec = 0.0
    if ray_batch_mode == "host":
        ray_prepare_start = time.perf_counter()
        prepared_rays = prepared.prepare_ray_batch(workload["rays"])
        prepared_rays_sec = time.perf_counter() - ray_prepare_start
    elif ray_batch_mode in {"cupy", "torch"}:
        partner_start = time.perf_counter()
        ray_columns = raydb._make_paper_rt_partner_ray_columns(workload, partner=ray_batch_mode)
        partner_ray_column_build_sec = time.perf_counter() - partner_start
        ray_prepare_start = time.perf_counter()
        prepared_rays = prepared.prepare_ray_batch_device_columns(ray_columns)
        prepared_rays_sec = time.perf_counter() - ray_prepare_start
    cpu_rows = tuple(rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows)
    query_values: list[float] = []
    first_sample: dict[str, Any] = {}
    all_match_cpu_reference = True
    target_query_seconds = float(getattr(args, "target_query_seconds", 0.0) or 0.0)
    try:
        iteration = 0
        measured_query_total_sec = 0.0
        last_progress_print = 0.0
        while True:
            if target_query_seconds > 0.0:
                if iteration >= warmup and measured_query_total_sec >= target_query_seconds:
                    break
                total_iterations = "duration"
            else:
                if iteration >= warmup + repeat:
                    break
                total_iterations = str(warmup + repeat)
            now = time.perf_counter()
            should_print = target_query_seconds <= 0.0 or iteration <= warmup
            if target_query_seconds > 0.0 and not should_print and now - last_progress_print >= 2.0:
                should_print = True
            if should_print:
                print(
                    "running",
                    f"backend=paper_rt_{args.backend}_prepared_payload",
                    f"mode={mode}",
                    f"copies={copies}",
                    f"fixture={args.fixture_kind}",
                    f"ray_batch_mode={ray_batch_mode}",
                    f"iteration={iteration + 1}/{total_iterations}",
                    f"measured_query_total={measured_query_total_sec:.3f}s",
                    flush=True,
                )
                last_progress_print = now
            query_start = time.perf_counter()
            if prepared_rays is None:
                result = prepared.run(
                    workload["rays"],
                    reduction="sum_count" if mode == "avg_as_sum_count" else mode,
                )
            else:
                result = prepared.run_prepared_rays(
                    prepared_rays,
                    reduction="sum_count" if mode == "avg_as_sum_count" else mode,
                )
            query_sec = time.perf_counter() - query_start
            if iteration >= warmup:
                measured_query_total_sec += query_sec
                query_values.append(float(query_sec))
                rows = raydb._paper_rows_from_generic_grouped_rows(
                    result["rows"],
                    group_keys=workload["group_keys"],
                    group_tuples=workload["group_tuples"],
                )
                all_match_cpu_reference = all_match_cpu_reference and tuple(rows) == cpu_rows
                if not first_sample:
                    first_sample = {
                        "timings": result.get("phase_timing_seconds", {}),
                        "native_symbol": result.get("native_symbol"),
                        "rt_core_accelerated": bool(result.get("rt_core_accelerated", False)),
                        "transfer_metadata": result.get("transfer_metadata", {}),
                        "hit_event_count_before_dedup": result.get("hit_event_count_before_dedup"),
                    }
            iteration += 1
    finally:
        if prepared_rays is not None:
            prepared_rays.close()
        prepared.close()

    first = first_sample
    return {
        "backend": f"paper_rt_{args.backend}_prepared_payload",
        "mode": mode,
        "copies": copies,
        "row_count": len(fixture["row_ids"]),
        "fixture": fixture.get("fixture_kind", args.fixture_kind),
        "fixture_generation": fixture.get("generation", {}),
        "triangle_count": raydb._packed_or_sequence_count(workload["triangles"]),
        "ray_count": raydb._packed_or_sequence_count(workload["rays"]),
        "workload_build_sec": workload_sec,
        "table_descriptor_prepare_sec": float(table_descriptor_prepare_sec),
        "prepared_table_descriptor_used": bool(workload.get("prepared_table_descriptor_used", False)),
        "table_descriptor_contract": workload.get("table_descriptor_contract"),
        "prepare_scene_and_payload_sec": prepare_sec,
        "ray_batch_mode": ray_batch_mode,
        "partner_ray_column_build_sec": partner_ray_column_build_sec,
        "prepare_ray_batch_sec": prepared_rays_sec,
        "target_query_seconds": target_query_seconds,
        "measured_query_total_sec": float(sum(query_values)),
        "measured_query_iterations": len(query_values),
        "query_sec_mean": float(statistics.mean(query_values)),
        "query_sec_median": float(statistics.median(query_values)),
        "query_sec_min": float(min(query_values)),
        "query_sec_max": float(max(query_values)),
        "all_match_cpu_reference": bool(all_match_cpu_reference),
        "rt_core_accelerated": bool(first.get("rt_core_accelerated", False)),
        "native_symbol": first.get("native_symbol"),
        "hit_event_count_before_dedup": first.get("hit_event_count_before_dedup"),
        "timings_first_sample": first.get("timings"),
        "transfer_metadata_first_sample": first.get("transfer_metadata"),
        "claim_boundary": (
            "Prepared query timing only. Python owns RayDB lowering; native code owns only "
            "generic rays, triangles, primitive group ids, primitive values, deduplication, "
            "and grouped reductions. Public speedup wording is not authorized."
        ),
    }


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal2646 RayDB Prepared Payload Query Timing",
        "",
        "Status: internal evidence only; public speedup wording remains unauthorized pending review.",
        "",
        "## Provenance",
        "",
        f"- timestamp UTC: `{payload['environment'].get('timestamp_utc')}`",
        f"- host: `{payload['environment'].get('hostname')}`",
        f"- git commit: `{payload['environment'].get('git_commit')}`",
        f"- script: `{payload['script']}`",
        f"- output JSON: `{payload['output_json']}`",
        "",
        "## Matrix",
        "",
        "| mode | fixture | copies | ray batch | rows | triangles | rays | table descriptor s | workload build s | prepare scene/payload s | partner ray cols s | prepare rays s | query iterations | query total s | query median s | query mean s | RT core | correct |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["matrix"]:
        lines.append(
            "| {mode} | {fixture} | {copies} | {ray_batch_mode} | {row_count} | {triangle_count} | {ray_count} | "
            "{table_descriptor_prepare_sec:.6f} | {workload_build_sec:.6f} | {prepare_scene_and_payload_sec:.6f} | "
            "{partner_ray_column_build_sec:.6f} | {prepare_ray_batch_sec:.6f} | "
            "{measured_query_iterations} | {measured_query_total_sec:.6f} | "
            "{query_sec_median:.6f} | {query_sec_mean:.6f} | "
            "{rt_core_accelerated} | {all_match_cpu_reference} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This runner measures prepared query time after workload construction and prepared scene/payload creation.",
            "- With table descriptor reuse enabled, dense predicate/group encoding is prepared once per fixture and reused across modes.",
            "- The prepared primitive payload keeps primitive group ids and primitive values device-resident across repeated runs.",
            "- `ray_batch=host` prepares the generic 3-D ray batch once from host packed rays.",
            "- `ray_batch=cupy` and `ray_batch=torch` create partner-owned CUDA ray columns, then pack them on device into a prepared generic 3-D ray batch.",
            "- Both prepared-ray modes avoid query-ray upload on each repeated run.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copies-ladder", type=_parse_csv_ints, default=(100000,))
    parser.add_argument("--fixture-kind", choices=("repeated", "generated"), default="repeated")
    parser.add_argument("--generated-rows", type=int, default=raydb.DEFAULT_GENERATED_ROW_COUNT)
    parser.add_argument("--generated-groups", type=int, default=raydb.DEFAULT_GENERATED_GROUP_COUNT)
    parser.add_argument("--generated-revenue-mod", type=int, default=raydb.DEFAULT_GENERATED_REVENUE_MOD)
    parser.add_argument("--modes", type=_parse_csv_text, default=raydb.PAPER_RT_RESULT_MODES)
    parser.add_argument("--backend", choices=("embree", "optix"), default="optix")
    parser.add_argument("--ray-batch-mode", choices=("none", "host", "cupy", "torch"), default="host")
    parser.add_argument(
        "--no-reuse-table-descriptor",
        action="store_true",
        help="Disable app-owned reusable RayDB dense scan/group descriptor across modes.",
    )
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument(
        "--target-query-seconds",
        type=float,
        default=0.0,
        help="If >0, run measured prepared queries until this total query duration is reached per row.",
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    if args.generated_rows <= 0:
        parser.error("--generated-rows must be positive")
    if args.generated_groups <= 0:
        parser.error("--generated-groups must be positive")
    if args.generated_revenue_mod <= 0:
        parser.error("--generated-revenue-mod must be positive")
    matrix = []
    for copies in args.copies_ladder:
        fixture = raydb.make_benchmark_fixture(
            fixture_kind=args.fixture_kind,
            copies=copies,
            generated_rows=args.generated_rows,
            generated_groups=args.generated_groups,
            generated_revenue_mod=args.generated_revenue_mod,
        )
        table_descriptor = None
        table_descriptor_prepare_sec = 0.0
        if not args.no_reuse_table_descriptor:
            descriptor_plan = raydb.make_plan(args.modes[0])
            descriptor_start = time.perf_counter()
            table_descriptor = raydb.prepare_paper_rt_encoded_table_descriptor(fixture, descriptor_plan)
            table_descriptor_prepare_sec = time.perf_counter() - descriptor_start
        for mode in args.modes:
            matrix.append(
                _measure_mode(
                    mode,
                    copies,
                    args.repeat,
                    args.warmup,
                    args.ray_batch_mode,
                    args,
                    fixture=fixture,
                    table_descriptor=table_descriptor,
                    table_descriptor_prepare_sec=table_descriptor_prepare_sec,
                )
            )
    payload = {
        "goal": "Goal2646 RayDB prepared payload query timing",
        "script": str(Path(__file__).resolve()),
        "arguments": {
            "copies_ladder": list(args.copies_ladder),
            "fixture_kind": args.fixture_kind,
            "generated_rows": args.generated_rows,
            "generated_groups": args.generated_groups,
            "generated_revenue_mod": args.generated_revenue_mod,
            "modes": list(args.modes),
            "backend": args.backend,
            "ray_batch_mode": args.ray_batch_mode,
            "reuse_table_descriptor": not args.no_reuse_table_descriptor,
            "repeat": args.repeat,
            "warmup": args.warmup,
            "target_query_seconds": args.target_query_seconds,
        },
        "environment": _environment_snapshot(),
        "performance_claim_authorized": False,
        "matrix": matrix,
        "output_json": str(args.output_json),
        "output_markdown": str(args.output_markdown),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(payload, args.output_markdown)
    print(json.dumps({"output_json": str(args.output_json)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
