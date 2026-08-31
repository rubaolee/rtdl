#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _phase_time,
)
from rtdsl.baseline_runner import segments_from_records  # noqa: E402
from rtdsl.datasets import chains_to_segments  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402
from rtdsl.optix_runtime import pack_segments  # noqa: E402
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix  # noqa: E402
from rtdsl.optix_runtime import prepare_segment_pair_left_set_optix  # noqa: E402
from scripts.goal3691_rayjoin_original_same_source_probe import _run_rayjoin_query  # noqa: E402


SCHEMA = "rtdl.goal3722.rayjoin_lsi_direct_intersection_route_probe.v1"
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3722_rayjoin_lsi_direct_intersection_route_a5000"
    / "summary.json"
)
SCOPED_SOURCE_PATHS = (
    "scripts/goal3722_rayjoin_lsi_direct_intersection_route_probe.py",
    "tests/goal3722_rayjoin_lsi_direct_intersection_route_probe_test.py",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/rtdsl/optix_runtime.py",
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
    runs: list[dict[str, Any]] = []
    for index in range(warmup + repeat):
        start = time.perf_counter()
        if route == "existing_anyhit_exact_count":
            count_value = int(prepared.count_prepared_left(prepared_left))
            result: dict[str, Any] = {"count": count_value}
        elif route == "direct_intersection_exact_count":
            result = prepared.count_prepared_left_direct_intersection(prepared_left)
            count_value = int(result["count"])
        else:
            raise ValueError(f"unknown route: {route}")
        elapsed = time.perf_counter() - start
        is_warmup = index < warmup
        print(
            f"[goal3722] {route} {'warmup' if is_warmup else 'repeat'} "
            f"{index + 1}/{warmup + repeat} elapsed={elapsed:.9f}s count={count_value}",
            flush=True,
        )
        runs.append(
            {
                "iteration": index,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "count": count_value,
                "result": result,
                "native_phase_timings": prepared.last_phase_timings(),
            }
        )
        if not is_warmup:
            measured.append(elapsed)
            counts.append(count_value)
    if len(set(counts)) != 1:
        raise RuntimeError(f"{route} count changed across repeats: {counts}")
    return {
        "route": route,
        "repeat": repeat,
        "warmup": warmup,
        "count": counts[-1],
        "median_sec": _median(measured),
        "min_sec": min(measured),
        "max_sec": max(measured),
        "total_sec": sum(measured),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    phases: dict[str, float] = {}
    print("[goal3722] loading RayJoin source datasets", flush=True)
    left_dataset = _phase_time(phases, "load_left_sec", lambda: load_cdb(args.county))
    right_dataset = _phase_time(phases, "load_right_sec", lambda: load_cdb(args.soil))
    left_segments = _phase_time(
        phases,
        "left_chains_to_segments_sec",
        lambda: segments_from_records(chains_to_segments(left_dataset)),
    )
    right_segments = _phase_time(
        phases,
        "right_chains_to_segments_sec",
        lambda: segments_from_records(chains_to_segments(right_dataset)),
    )
    packed_left = _phase_time(phases, "pack_left_sec", lambda: pack_segments(records=left_segments))
    packed_right = _phase_time(phases, "pack_right_sec", lambda: pack_segments(records=right_segments))
    print(
        f"[goal3722] left_segments={len(left_segments)} right_segments={len(right_segments)}",
        flush=True,
    )

    print("[goal3722] preparing RTDL/OptiX right scene and left set", flush=True)
    prepared = _phase_time(phases, "prepare_static_scene_sec", lambda: prepare_segment_pair_intersection_optix(packed_right))
    prepared_left = None
    try:
        prepared_left = _phase_time(phases, "prepare_left_set_sec", lambda: prepare_segment_pair_left_set_optix(packed_left))
        existing = _time_route(
            prepared,
            prepared_left,
            route="existing_anyhit_exact_count",
            repeat=args.repeat,
            warmup=args.warmup,
        )
        direct = _time_route(
            prepared,
            prepared_left,
            route="direct_intersection_exact_count",
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
        int(existing["count"]) == int(direct["count"])
        and (
            rayjoin_lsi is None
            or rayjoin_lsi.get("intersections") is None
            or int(direct["count"]) == int(rayjoin_lsi["intersections"])
        )
    )
    if not counts_match:
        raise RuntimeError(
            "count mismatch in Goal3722 probe: "
            f"existing={existing['count']} direct={direct['count']} "
            f"rayjoin={None if rayjoin_lsi is None else rayjoin_lsi.get('intersections')}"
        )
    rayjoin_query_sec = None if rayjoin_lsi is None else rayjoin_lsi.get("query_sec")
    return {
        "schema": SCHEMA,
        "goal": 3722,
        "generated_at_unix": time.time(),
        "rtdl_git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "rtdl_source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "rtdl_git_status_short": _command_output(["git", "status", "--short"]),
        "goal3722_scoped_source_paths": list(SCOPED_SOURCE_PATHS),
        "goal3722_scoped_source_status_short": _command_output(
            ["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS]
        ),
        "rayjoin_git_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=args.rayjoin_root),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county": str(args.county),
        "soil": str(args.soil),
        "segment_counts": {
            "left": len(left_segments),
            "right": len(right_segments),
        },
        "phase_seconds": phases,
        "rayjoin_lsi": rayjoin_lsi,
        "rtdl_existing_anyhit_exact_count": existing,
        "rtdl_direct_intersection_exact_count": direct,
        "comparison": {
            "counts_match": counts_match,
            "rayjoin_lsi_intersections": None if rayjoin_lsi is None else rayjoin_lsi.get("intersections"),
            "rtdl_count": int(direct["count"]),
            "existing_anyhit_median_sec": float(existing["median_sec"]),
            "direct_intersection_median_sec": float(direct["median_sec"]),
            "direct_intersection_speedup_vs_existing_anyhit": (
                float(existing["median_sec"]) / float(direct["median_sec"])
            ),
            "rayjoin_query_sec": rayjoin_query_sec,
            "direct_intersection_speedup_vs_rayjoin": (
                float(rayjoin_query_sec) / float(direct["median_sec"])
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
            "This probe tests a generic direct custom-intersection-program exact count route "
            "against the existing generic any-hit exact count route. It is diagnostic only "
            "and does not authorize default-route, RayJoin reproduction, or RTDL-beats-RayJoin claims."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3722 RayJoin LSI direct-intersection route probe.")
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
    return args


def main() -> int:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3722] wrote {args.output}", flush=True)
    print(json.dumps(payload["comparison"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
