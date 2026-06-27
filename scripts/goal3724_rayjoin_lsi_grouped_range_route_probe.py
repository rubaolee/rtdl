#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _phase_time,
)
from rtdsl.baseline_runner import segments_from_records  # noqa: E402
from rtdsl.datasets import chains_to_segments  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402
from rtdsl.optix_runtime import pack_segments  # noqa: E402
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix  # noqa: E402
from rtdsl.optix_runtime import prepare_segment_pair_left_set_optix  # noqa: E402
from scripts.goal3691_rayjoin_original_same_source_probe import _run_rayjoin_query  # noqa: E402


SCHEMA = "rtdl.goal3724.rayjoin_lsi_grouped_range_route_probe.v1"
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3724_rayjoin_lsi_grouped_range_route_a5000"
    / "summary.json"
)


def _command_output(args: list[str], *, cwd: Path = ROOT) -> str:
    try:
        return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _claim_boundary() -> dict[str, bool]:
    return {
        "diagnostic_only": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_default_route_authorized": False,
    }


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot summarize empty timings")
    return float(statistics.median(values))


def _time_route(prepared, prepared_left, *, route: str, repeat: int, warmup: int) -> dict[str, Any]:
    measured: list[float] = []
    counts: list[int] = []
    group_counts: list[int] = []
    runs: list[dict[str, Any]] = []
    for index in range(warmup + repeat):
        start = time.perf_counter()
        if route == "existing_anyhit_exact_count":
            result: dict[str, Any] = {"count": int(prepared.count_prepared_left(prepared_left))}
        elif route == "grouped_range_direct_intersection_exact_count":
            result = prepared.count_prepared_left_grouped_range_direct_intersection(prepared_left)
        else:
            raise ValueError(f"unknown route: {route}")
        elapsed = time.perf_counter() - start
        count_value = int(result["count"])
        group_count = int(result.get("right_group_count", 0))
        is_warmup = index < warmup
        print(
            f"[goal3724] {route} {'warmup' if is_warmup else 'repeat'} "
            f"{index + 1}/{warmup + repeat} elapsed={elapsed:.9f}s "
            f"count={count_value} groups={group_count}",
            flush=True,
        )
        runs.append(
            {
                "iteration": index,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "count": count_value,
                "right_group_count": group_count,
                "result": result,
                "native_phase_timings": prepared.last_phase_timings(),
            }
        )
        if not is_warmup:
            measured.append(elapsed)
            counts.append(count_value)
            if group_count:
                group_counts.append(group_count)
    if len(set(counts)) != 1:
        raise RuntimeError(f"{route} count changed across repeats: {counts}")
    if group_counts and len(set(group_counts)) != 1:
        raise RuntimeError(f"{route} group count changed across repeats: {group_counts}")
    return {
        "route": route,
        "repeat": repeat,
        "warmup": warmup,
        "count": counts[-1],
        "right_group_count": group_counts[-1] if group_counts else None,
        "median_sec": _median(measured),
        "min_sec": min(measured),
        "max_sec": max(measured),
        "total_sec": sum(measured),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    phases: dict[str, float] = {}
    print("[goal3724] loading RayJoin source datasets", flush=True)
    county_dataset = _phase_time(phases, "load_county_sec", lambda: load_cdb(args.county))
    soil_dataset = _phase_time(phases, "load_soil_sec", lambda: load_cdb(args.soil))
    county_segments = _phase_time(
        phases,
        "county_chains_to_segments_sec",
        lambda: segments_from_records(chains_to_segments(county_dataset)),
    )
    soil_segments = _phase_time(
        phases,
        "soil_chains_to_segments_sec",
        lambda: segments_from_records(chains_to_segments(soil_dataset)),
    )
    # Match RayJoin's logged LSI orientation: query rays are soil edges, and
    # the prepared base set is county edges.
    packed_left_query = _phase_time(phases, "pack_left_query_soil_sec", lambda: pack_segments(records=soil_segments))
    packed_right_base = _phase_time(phases, "pack_right_base_county_sec", lambda: pack_segments(records=county_segments))
    print(
        f"[goal3724] query_left_soil_segments={len(soil_segments)} "
        f"base_right_county_segments={len(county_segments)}",
        flush=True,
    )

    os.environ["RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_MAX_SIZE"] = str(args.group_max_size)
    os.environ["RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_AREA_ENLARGE"] = str(args.group_area_enlarge)
    print(
        "[goal3724] preparing RTDL/OptiX base right scene and query left set "
        f"group_max_size={args.group_max_size} group_area_enlarge={args.group_area_enlarge}",
        flush=True,
    )
    prepared = _phase_time(
        phases,
        "prepare_static_scene_county_sec",
        lambda: prepare_segment_pair_intersection_optix(packed_right_base),
    )
    prepared_left = None
    try:
        prepared_left = _phase_time(
            phases,
            "prepare_left_query_soil_set_sec",
            lambda: prepare_segment_pair_left_set_optix(packed_left_query),
        )
        existing = _time_route(
            prepared,
            prepared_left,
            route="existing_anyhit_exact_count",
            repeat=args.repeat,
            warmup=args.warmup,
        )
        grouped = _time_route(
            prepared,
            prepared_left,
            route="grouped_range_direct_intersection_exact_count",
            repeat=args.repeat,
            warmup=args.warmup,
        )
    finally:
        if prepared_left is not None:
            prepared_left.close()
        prepared.close()

    rayjoin_lsi = None
    if not args.skip_rayjoin:
        rayjoin_lsi = _run_rayjoin_query(
            rayjoin_root=args.rayjoin_root,
            county=args.county,
            soil=args.soil,
            query="lsi",
            repeat=args.rayjoin_repeat,
            warmup=args.rayjoin_warmup,
            check=False,
            xsect_factor=args.xsect_factor,
            timeout_seconds=args.timeout_seconds,
        )

    counts_match = (
        int(existing["count"]) == int(grouped["count"])
        and (
            rayjoin_lsi is None
            or rayjoin_lsi.get("intersections") is None
            or int(grouped["count"]) == int(rayjoin_lsi["intersections"])
        )
    )
    if not counts_match:
        raise RuntimeError(
            "count mismatch in Goal3724 probe: "
            f"existing={existing['count']} grouped={grouped['count']} "
            f"rayjoin={None if rayjoin_lsi is None else rayjoin_lsi.get('intersections')}"
        )
    rayjoin_query_sec = None if rayjoin_lsi is None else rayjoin_lsi.get("query_sec")
    return {
        "schema": SCHEMA,
        "goal": 3724,
        "generated_at_unix": time.time(),
        "rtdl_git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "rtdl_source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "rtdl_git_status_short": _command_output(["git", "status", "--short"]),
        "rayjoin_git_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=args.rayjoin_root),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county": str(args.county),
        "soil": str(args.soil),
        "segment_counts": {
            "query_left_soil": len(soil_segments),
            "base_right_county": len(county_segments),
        },
        "grouping_policy": {
            "max_size": int(args.group_max_size),
            "area_enlarge": float(args.group_area_enlarge),
            "env_max_size": os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_MAX_SIZE"),
            "env_area_enlarge": os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_GROUPED_RANGE_AREA_ENLARGE"),
        },
        "phase_seconds": phases,
        "rayjoin_lsi": rayjoin_lsi,
        "rtdl_existing_anyhit_exact_count_same_orientation": existing,
        "rtdl_grouped_range_direct_intersection_exact_count": grouped,
        "comparison": {
            "counts_match": counts_match,
            "rayjoin_lsi_intersections": None if rayjoin_lsi is None else rayjoin_lsi.get("intersections"),
            "rtdl_count": int(grouped["count"]),
            "right_group_count": grouped["right_group_count"],
            "right_segment_count": len(county_segments),
            "right_group_compression_ratio": (
                1.0 - float(grouped["right_group_count"]) / float(len(county_segments))
                if grouped["right_group_count"]
                else None
            ),
            "existing_anyhit_median_sec": float(existing["median_sec"]),
            "grouped_range_median_sec": float(grouped["median_sec"]),
            "grouped_range_speedup_vs_existing_anyhit": (
                float(existing["median_sec"]) / float(grouped["median_sec"])
            ),
            "rayjoin_query_sec": rayjoin_query_sec,
            "grouped_range_speedup_vs_rayjoin": (
                float(rayjoin_query_sec) / float(grouped["median_sec"])
                if rayjoin_query_sec
                else None
            ),
            "existing_anyhit_speedup_vs_rayjoin": (
                float(rayjoin_query_sec) / float(existing["median_sec"])
                if rayjoin_query_sec
                else None
            ),
        },
        "interpretation_boundary": (
            "This probe tests generic grouped/ranged right-primitive exact counting. It is diagnostic only, "
            "not a RayJoin reproduction and not a public default-route claim."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3724 RayJoin LSI grouped/ranged route probe.")
    parser.add_argument("--rayjoin-root", type=Path, default=Path("/root/RayJoin"))
    parser.add_argument(
        "--county",
        type=Path,
        default=Path("/root/RayJoin/test/dataset/br_county_clean_25_odyssey_final.txt"),
    )
    parser.add_argument(
        "--soil",
        type=Path,
        default=Path("/root/RayJoin/test/dataset/br_soil_ascii_odyssey_final.txt"),
    )
    parser.add_argument("--rayjoin-repeat", type=int, default=3)
    parser.add_argument("--rayjoin-warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--group-max-size", type=int, default=1)
    parser.add_argument("--group-area-enlarge", type=float, default=1.5)
    parser.add_argument("--xsect-factor", type=float, default=0.1)
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--skip-rayjoin", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    for name in ("rayjoin_repeat", "repeat"):
        if int(getattr(args, name)) <= 0:
            raise ValueError(f"--{name.replace('_', '-')} must be positive")
    for name in ("rayjoin_warmup", "warmup"):
        if int(getattr(args, name)) < 0:
            raise ValueError(f"--{name.replace('_', '-')} must be non-negative")
    if args.group_max_size <= 0:
        raise ValueError("--group-max-size must be positive")
    if args.group_area_enlarge <= 1.0:
        raise ValueError("--group-area-enlarge must be greater than 1.0")
    return args


def main() -> int:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3724] wrote {args.output}", flush=True)
    print(json.dumps(payload["comparison"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
