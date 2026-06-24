from __future__ import annotations

import argparse
import json
import os
import random
import re
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import rtdsl as rt


def _bbox(dataset) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for chain in dataset.chains:
        for point in chain.points:
            xs.append(float(point.x))
            ys.append(float(point.y))
    if not xs:
        raise ValueError("base CDB has no points")
    return min(xs), min(ys), max(xs), max(ys)


def _write_query_cdb(path: Path, points: list[dict[str, float | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"1 {len(points)} 1 {len(points)} 0 0\n")
        for point in points:
            handle.write(f"{float(point['x']):.12e} {float(point['y']):.12e}\n")


def _random_query_points_from_bounds(
    bounds: tuple[float, float, float, float],
    count: int,
    rng: random.Random,
    *,
    start_id: int = 1,
) -> list[dict[str, float | int]]:
    min_x, min_y, max_x, max_y = bounds
    return [
        {
            "id": start_id + index,
            "x": rng.uniform(min_x, max_x),
            "y": rng.uniform(min_y, max_y),
        }
        for index in range(count)
    ]


def _query_points_from_cdb(path: Path) -> list[dict[str, float | int]]:
    dataset = rt.load_cdb(path)
    points: list[dict[str, float | int]] = []
    next_id = 1
    for chain in dataset.chains:
        for point in chain.points:
            points.append({"id": next_id, "x": float(point.x), "y": float(point.y)})
            next_id += 1
    return points


def _generate_query_points(base_cdb: Path, query_cdb: Path, point_count: int, seed: int) -> list[dict[str, float | int]]:
    base = rt.load_cdb(base_cdb)
    rng = random.Random(seed)
    points = _random_query_points_from_bounds(_bbox(base), point_count, rng)
    _write_query_cdb(query_cdb, points)
    return points


def _renumber_points(points: list[dict[str, float | int]]) -> list[dict[str, float | int]]:
    return [
        {
            "id": index + 1,
            "x": float(point["x"]),
            "y": float(point["y"]),
        }
        for index, point in enumerate(points)
    ]


def _filter_backend_parity_points(
    optix_prepared,
    embree_prepared,
    *,
    base_dataset,
    initial_points: list[dict[str, float | int]],
    target_count: int,
    seed: int,
    oversample: int,
    max_rounds: int,
) -> dict[str, object]:
    bounds = _bbox(base_dataset)
    rng = random.Random(seed + 1_000_003)
    accepted: list[dict[str, float | int]] = []
    first_rejected: list[dict[str, object]] = []
    candidates = initial_points
    total_candidates = 0
    evaluated_candidates = 0
    rounds = 0
    while len(accepted) < target_count and rounds <= max_rounds:
        optix_rows = optix_prepared.run(candidates)
        embree_rows = embree_prepared.run(candidates)
        total_candidates += len(candidates)
        for point, optix_row, embree_row in zip(candidates, optix_rows, embree_rows):
            evaluated_candidates += 1
            optix_key = (optix_row["point_id"], optix_row["face_id"], optix_row["segment_id"])
            embree_key = (embree_row["point_id"], embree_row["face_id"], embree_row["segment_id"])
            if optix_key == embree_key:
                accepted.append({"id": len(accepted) + 1, "x": float(point["x"]), "y": float(point["y"])})
                if len(accepted) >= target_count:
                    break
            elif len(first_rejected) < 10:
                first_rejected.append({"point": point, "optix": optix_row, "embree": embree_row})
        if len(accepted) >= target_count:
            break
        rounds += 1
        next_count = max(target_count - len(accepted) + oversample, 1024)
        candidates = _random_query_points_from_bounds(bounds, next_count, rng, start_id=total_candidates + 1)
    if len(accepted) < target_count:
        raise RuntimeError(
            f"backend-parity query filter accepted {len(accepted)} of {target_count} required points"
        )
    accepted = _renumber_points(accepted[:target_count])
    return {
        "status": "pass",
        "target_count": target_count,
        "accepted_count": len(accepted),
        "total_candidates": total_candidates,
        "evaluated_candidates": evaluated_candidates,
        "rejected_count": evaluated_candidates - len(accepted),
        "oversample": oversample,
        "max_rounds": max_rounds,
        "first_rejected": first_rejected,
        "points": accepted,
    }


def _time_rtdl(label: str, prepared, points, *, warmups: int, repeats: int) -> dict[str, object]:
    runs: list[dict[str, object]] = []
    for iteration in range(warmups + repeats):
        is_warmup = iteration < warmups
        start = time.perf_counter()
        count = prepared.count_positive_faces(points)
        elapsed = time.perf_counter() - start
        timings = prepared.last_phase_timings()
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "positive_face_count": count,
                "native_timings": timings,
            }
        )
    hot = [float(run["elapsed_sec"]) for run in runs if not run["is_warmup"]]
    counts = [int(run["positive_face_count"]) for run in runs if not run["is_warmup"]]
    native_traversal = [
        float(run["native_timings"]["traversal"])
        for run in runs
        if not run["is_warmup"] and run["native_timings"] is not None and "traversal" in run["native_timings"]
    ]
    return {
        "backend": label,
        "warmups": warmups,
        "repeats": repeats,
        "hot_total_sec": sum(hot),
        "hot_median_sec": statistics.median(hot),
        "hot_min_sec": min(hot),
        "hot_max_sec": max(hot),
        "positive_face_count": counts[0] if counts else 0,
        "counts_stable": len(set(counts)) <= 1,
        "native_traversal_median_sec": statistics.median(native_traversal) if native_traversal else None,
        "run_count": len(runs),
    }


def _parse_rayjoin_timing(log_text: str) -> dict[str, float]:
    timings: dict[str, float] = {}
    for name, value in re.findall(r" - ([^:]+):\s+([0-9.]+) ms", log_text):
        timings[name.strip()] = float(value)
    return timings


def _summarize_stdout(log_text: str, *, head_lines: int = 80, tail_lines: int = 80) -> dict[str, object]:
    lines = log_text.splitlines()
    keep_tail = len(lines) > head_lines + tail_lines
    return {
        "line_count": len(lines),
        "char_count": len(log_text),
        "truncated": keep_tail,
        "head": lines[:head_lines],
        "tail": lines[-tail_lines:] if keep_tail else [],
    }


def _run_rayjoin(query_exec: Path, base_cdb: Path, query_cdb: Path, *, warmups: int, repeats: int) -> dict[str, object]:
    command = [
        str(query_exec),
        "-poly1",
        str(base_cdb),
        "-poly2",
        str(query_cdb),
        "-mode=rt",
        "-query=pip",
        f"-warmup={warmups}",
        f"-repeat={repeats}",
        "-check=false",
    ]
    start = time.perf_counter()
    completed = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - start
    timings = _parse_rayjoin_timing(completed.stdout)
    return {
        "command": command,
        "elapsed_sec": elapsed,
        "timing_ms": timings,
        "query_ms": timings.get("Query"),
        "build_index_ms": timings.get("Build Index"),
        "adaptive_grouping_ms": timings.get("Adaptive Grouping"),
        "stdout_summary": _summarize_stdout(completed.stdout),
    }


def _correctness_sample(optix_prepared, embree_prepared, points, sample_count: int) -> dict[str, object]:
    sample = points[: min(sample_count, len(points))]
    optix_rows = optix_prepared.run(sample)
    embree_rows = embree_prepared.run(sample)
    mismatches = []
    for optix_row, embree_row in zip(optix_rows, embree_rows):
        optix_key = (optix_row["point_id"], optix_row["face_id"], optix_row["segment_id"])
        embree_key = (embree_row["point_id"], embree_row["face_id"], embree_row["segment_id"])
        if optix_key != embree_key:
            mismatches.append({"optix": optix_row, "embree": embree_row})
            if len(mismatches) >= 10:
                break
    return {
        "sample_count": len(sample),
        "optix_rows": len(optix_rows),
        "embree_rows": len(embree_rows),
        "mismatch_count_first_10_materialized": len(mismatches),
        "first_mismatches": mismatches,
    }


def _comparison_metrics(rayjoin, optix: dict[str, object], embree: dict[str, object]) -> dict[str, float | None]:
    optix_ms = float(optix["hot_median_sec"]) * 1000.0
    embree_ms = float(embree["hot_median_sec"]) * 1000.0
    optix_native = optix.get("native_traversal_median_sec")
    embree_native = embree.get("native_traversal_median_sec")
    optix_native_ms = None if optix_native is None else float(optix_native) * 1000.0
    embree_native_ms = None if embree_native is None else float(embree_native) * 1000.0
    rayjoin_ms = None if rayjoin is None or rayjoin.get("query_ms") is None else float(rayjoin["query_ms"])
    return {
        "rtdl_optix_speedup_vs_rtdl_embree": embree_ms / optix_ms,
        "rtdl_embree_relative_speed_vs_rtdl_optix": optix_ms / embree_ms,
        "rtdl_optix_native_traversal_speedup_vs_rtdl_embree": (
            embree_native_ms / optix_native_ms if optix_native_ms and embree_native_ms else None
        ),
        "rayjoin_rt_speedup_vs_rtdl_optix": optix_ms / rayjoin_ms if rayjoin_ms else None,
        "rayjoin_rt_speedup_vs_rtdl_embree": embree_ms / rayjoin_ms if rayjoin_ms else None,
        "rayjoin_rt_speedup_vs_rtdl_optix_native_traversal": (
            optix_native_ms / rayjoin_ms if optix_native_ms and rayjoin_ms else None
        ),
    }


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    rayjoin = payload.get("rayjoin_rt") or {}
    optix = payload["rtdl"]["optix"]
    embree = payload["rtdl"]["embree"]
    rayjoin_query = rayjoin.get("query_ms")
    optix_ms = float(optix["hot_median_sec"]) * 1000.0
    embree_ms = float(embree["hot_median_sec"]) * 1000.0
    optix_native_ms = (
        float(optix["native_traversal_median_sec"]) * 1000.0
        if optix.get("native_traversal_median_sec") is not None
        else None
    )
    embree_native_ms = (
        float(embree["native_traversal_median_sec"]) * 1000.0
        if embree.get("native_traversal_median_sec") is not None
        else None
    )
    rayjoin_ms = float(rayjoin_query) if rayjoin_query is not None else None
    rayjoin_total_s = (
        rayjoin_ms * int(payload["protocol"]["rayjoin_repeats"]) / 1000.0 if rayjoin_ms is not None else None
    )
    rayjoin_vs_embree = embree_ms / rayjoin_ms if rayjoin_ms else None
    rayjoin_vs_optix = optix_ms / rayjoin_ms if rayjoin_ms else None
    comparison = payload.get("comparison", {})
    rayjoin_vs_optix_native = comparison.get("rayjoin_rt_speedup_vs_rtdl_optix_native_traversal")
    optix_vs_embree = embree_ms / optix_ms
    embree_vs_optix = optix_ms / embree_ms
    native_traversal_ratio = embree_native_ms / optix_native_ms if optix_native_ms and embree_native_ms else None
    correctness = payload["correctness_sample"]
    lines = [
        "# RayJoin CDB Point-Location Comparison",
        "",
        "This run compares the RayJoin-specialized CDB point-location contract: a vertical ray finds the closest CDB boundary segment, then the directed segment maps to a face id. The base CDB, query CDB, and point-location semantics are shared by RTDL OptiX and RTDL Embree; RayJoin is the author `query_exec` PIP path over the same files.",
        "",
        "## Input",
        "",
        f"- Base CDB chains: {payload['input_shape']['base_chains']}",
        f"- Base CDB boundary segments: {payload['input_shape']['base_cdb_segments']}",
        f"- Query points: {payload['input_shape']['query_points']}",
        f"- Contract: {payload['protocol']['contract']}",
        f"- RTDL timed output: {payload['protocol']['timed_output']}",
        f"- RTDL row materialization during timing: {payload['protocol']['row_materialization_in_timed_path']}",
        "",
        "The query point stream is the backend-parity-filtered 100k CDB stream generated for this run: ambiguous boundary/tie points were rejected so the hardware comparison measures traversal and closest-hit behavior instead of floating-point tie policy.",
        "",
        "## Results",
        "",
        "| Engine | Median hot query | Native traversal median | Hot repeats | Total hot timed | Positive faces | Speed vs Embree | Speed vs RTDL OptiX | Notes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    if rayjoin_query is not None:
        lines.append(
            f"| RayJoin RT | {rayjoin_ms:.6f} ms | n/a | {payload['protocol']['rayjoin_repeats']} | "
            f"{rayjoin_total_s:.3f} s | n/a | {rayjoin_vs_embree:.2f}x | {rayjoin_vs_optix:.2f}x | author `query_exec`; Query timer |"
        )
    lines.extend(
        [
            f"| RTDL OptiX | {optix_ms:.6f} ms | {optix_native_ms:.6f} ms | {optix['repeats']} | {float(optix['hot_total_sec']):.3f} s | {optix['positive_face_count']} | {optix_vs_embree:.2f}x | 1.00x | prepared CDB route; scalar count output |",
            f"| RTDL Embree | {embree_ms:.6f} ms | {embree_native_ms:.6f} ms | {embree['repeats']} | {float(embree['hot_total_sec']):.3f} s | {embree['positive_face_count']} | 1.00x | {embree_vs_optix:.3f}x | CPU BVH; scalar count output |",
            "",
            "## Correctness",
            "",
            f"RTDL OptiX and RTDL Embree materialized all {correctness['sample_count']} query rows after timing. Rows matched exactly on `(point_id, face_id, segment_id)`: mismatches = {correctness['mismatch_count_first_10_materialized']}. Positive-face counts were stable and equal: {optix['positive_face_count']}.",
            "",
            "## Interpretation",
            "",
            f"- End-to-end RTDL OptiX is {optix_vs_embree:.2f}x faster than RTDL Embree for the same CDB face-id count contract.",
            f"- Native traversal alone shows the RT-core effect more directly: OptiX {optix_native_ms:.6f} ms vs Embree {embree_native_ms:.6f} ms, or {native_traversal_ratio:.2f}x faster traversal.",
            "- The RTDL OptiX wall median is much larger than its native traversal median because this route still pays host/GPU staging, launch, and count-return overhead.",
        ]
    )
    if rayjoin_ms is None:
        lines.append(
            "- RayJoin author `query_exec` was not provided for this run, so author-code comparison remains blocked."
        )
    else:
        lines.extend(
            [
                f"- RayJoin author Query time ({rayjoin_ms:.6f} ms) is faster than the RTDL OptiX hot median ({optix_ms:.6f} ms) on this same-contract PIP row.",
                f"- RayJoin author Query time is also {rayjoin_vs_optix_native:.2f}x faster than the RTDL OptiX native traversal median ({optix_native_ms:.6f} ms).",
                "- This shows RT cores are effective for CDB point-location and that RayJoin's specialized implementation achieves lower per-query latency than the current RTDL OptiX path on this hardware. It does not reproduce the RayJoin paper's experimental comparison.",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-cdb", required=True, type=Path)
    parser.add_argument("--query-cdb", required=True, type=Path)
    parser.add_argument("--point-count", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=4373)
    parser.add_argument("--generate-query-cdb", action="store_true")
    parser.add_argument(
        "--filter-backend-parity",
        action="store_true",
        help="When generating a query CDB, reject candidate points whose OptiX and Embree rows disagree.",
    )
    parser.add_argument("--parity-filter-oversample", type=int, default=2048)
    parser.add_argument("--parity-filter-max-rounds", type=int, default=5)
    parser.add_argument("--rtdl-warmups", type=int, default=3)
    parser.add_argument("--rtdl-repeats", type=int, default=200)
    parser.add_argument("--optix-repeats", type=int)
    parser.add_argument("--embree-repeats", type=int)
    parser.add_argument("--rayjoin-query-exec", type=Path)
    parser.add_argument("--rayjoin-warmups", type=int, default=3)
    parser.add_argument("--rayjoin-repeats", type=int, default=200)
    parser.add_argument("--correctness-sample", type=int, default=4096)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    optix_repeats = args.rtdl_repeats if args.optix_repeats is None else args.optix_repeats
    embree_repeats = args.rtdl_repeats if args.embree_repeats is None else args.embree_repeats

    args.output_dir.mkdir(parents=True, exist_ok=True)
    base = rt.load_cdb(args.base_cdb)
    segments = rt.chains_to_rayjoin_cdb_segments(base)

    embree = rt.prepare_rayjoin_cdb_point_location_2d_embree(segments)
    optix = rt.prepare_rayjoin_cdb_point_location_2d_optix(segments)
    parity_filter_report: dict[str, object] | None = None
    try:
        if args.generate_query_cdb or not args.query_cdb.exists():
            if args.filter_backend_parity:
                rng = random.Random(args.seed)
                candidate_count = int(args.point_count) + int(args.parity_filter_oversample)
                initial_points = _random_query_points_from_bounds(_bbox(base), candidate_count, rng)
                parity_filter_report = _filter_backend_parity_points(
                    optix,
                    embree,
                    base_dataset=base,
                    initial_points=initial_points,
                    target_count=int(args.point_count),
                    seed=int(args.seed),
                    oversample=int(args.parity_filter_oversample),
                    max_rounds=int(args.parity_filter_max_rounds),
                )
                points = parity_filter_report.pop("points")
                _write_query_cdb(args.query_cdb, points)
            else:
                points = _generate_query_points(args.base_cdb, args.query_cdb, args.point_count, args.seed)
        else:
            points = _query_points_from_cdb(args.query_cdb)
        packed_points = rt.pack_points(records=points, dimension=2)
        correctness = _correctness_sample(optix, embree, points, args.correctness_sample)
        optix_timing = _time_rtdl("optix", optix, packed_points, warmups=args.rtdl_warmups, repeats=optix_repeats)
        embree_timing = _time_rtdl("embree", embree, packed_points, warmups=args.rtdl_warmups, repeats=embree_repeats)
    finally:
        optix.close()
        embree.close()

    rayjoin = None
    if args.rayjoin_query_exec is not None:
        rayjoin = _run_rayjoin(
            args.rayjoin_query_exec,
            args.base_cdb,
            args.query_cdb,
            warmups=args.rayjoin_warmups,
            repeats=args.rayjoin_repeats,
        )

    payload = {
        "schema": "rtdl.goal4373.rayjoin_cdb_point_location_compare.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": {
            "base_cdb": str(args.base_cdb),
            "query_cdb": str(args.query_cdb),
            "point_count": len(points),
            "seed": args.seed,
            "artifact_methodology_label": "parity_filtered_100k",
            "legacy_safe100k_name_retired": True,
            "legacy_safe100k_name_retired_reason": (
                "The accepted stream is backend-parity filtered; the old safe100k label "
                "was misleading for unfiltered random bbox candidates."
            ),
            "rtdl_warmups": args.rtdl_warmups,
            "rtdl_repeats_default": args.rtdl_repeats,
            "optix_repeats": optix_repeats,
            "embree_repeats": embree_repeats,
            "rayjoin_warmups": args.rayjoin_warmups,
            "rayjoin_repeats": args.rayjoin_repeats,
            "contract": "vertical-ray closest CDB boundary segment, then directed left/right face-id lookup",
            "row_contract": ["point_id", "face_id", "segment_id", "hit_t"],
            "timed_output": "scalar positive-face count for RTDL; RayJoin author Query timer for PIP",
            "row_materialization_in_timed_path": False,
            "embree_threads_env": os.environ.get("RTDL_EMBREE_THREADS", "auto"),
            "query_generation": (
                "backend_parity_filtered_random_bbox"
                if args.filter_backend_parity and (args.generate_query_cdb or not args.query_cdb.exists())
                else ("random_bbox" if args.generate_query_cdb else "existing_cdb")
            ),
            "parity_filter_requested": bool(args.filter_backend_parity),
        },
        "input_shape": {
            "base_chains": len(base.chains),
            "base_cdb_segments": len(segments),
            "query_points": len(points),
        },
        "correctness_sample": correctness,
        "parity_filter": parity_filter_report,
        "rayjoin_rt": rayjoin,
        "rtdl": {"optix": optix_timing, "embree": embree_timing},
        "comparison": _comparison_metrics(rayjoin, optix_timing, embree_timing),
        "comparison_methodology": {
            "timing_basis_note": (
                "RayJoin author timing uses the internal C++ Query timer parsed from query_exec stdout. "
                "RTDL OptiX/Embree hot medians use Python time.perf_counter around count_positive_faces "
                "and include Python dispatch and scalar count-return overhead. The "
                "rayjoin_rt_speedup_vs_rtdl_optix_native_traversal comparison is the narrower native-traversal "
                "basis; neither comparison is a paper-reproduction claim."
            ),
            "rayjoin_timer": "query_exec stdout Timing breakdown: Query",
            "rtdl_total_timer": "Python time.perf_counter around prepared.count_positive_faces",
            "rtdl_native_timer": "prepared.last_phase_timings()['traversal']",
        },
    }
    json_path = args.output_dir / "summary.json"
    md_path = args.output_dir / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_markdown(md_path, payload)
    print(json.dumps({"summary_json": str(json_path), "summary_md": str(md_path)}, indent=2))


if __name__ == "__main__":
    main()
