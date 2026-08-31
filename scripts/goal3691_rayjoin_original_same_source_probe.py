#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402
from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix  # noqa: E402
from scripts.goal3612_rayjoin_safe_mixed_route_composite import _run_exact_lsi_prepared_optix  # noqa: E402


SCHEMA = "rtdl.goal3691.rayjoin_original_same_source_probe.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal3691_rayjoin_original_same_source_probe_a5000" / "summary.json"
TIME_LINE_RE = re.compile(r"^\s*-\s*([^:]+):\s*([0-9.]+)\s*ms\s*$")
INTERSECTIONS_RE = re.compile(r"Intersections:\s*([0-9]+)")
SCOPED_SOURCE_PATHS = (
    "scripts/goal3691_rayjoin_original_same_source_probe.py",
    "tests/goal3691_rayjoin_original_same_source_probe_test.py",
    "scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py",
    "scripts/goal3612_rayjoin_safe_mixed_route_composite.py",
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


def _parse_rayjoin_output(text: str) -> dict[str, Any]:
    timings_ms: dict[str, float] = {}
    for line in text.splitlines():
        match = TIME_LINE_RE.match(line)
        if match:
            timings_ms[match.group(1).strip()] = float(match.group(2))
    intersections = None
    for match in INTERSECTIONS_RE.finditer(text):
        intersections = int(match.group(1))
    return {
        "timings_ms": timings_ms,
        "query_sec": timings_ms.get("Query", 0.0) / 1000.0 if "Query" in timings_ms else None,
        "intersections": intersections,
        "raw_tail": "\n".join(text.splitlines()[-40:]),
    }


def _run_rayjoin_query(
    *,
    rayjoin_root: Path,
    county: Path,
    soil: Path,
    query: str,
    repeat: int,
    warmup: int,
    check: bool,
    xsect_factor: float,
    timeout_seconds: int,
) -> dict[str, Any]:
    binary = rayjoin_root / "release" / "bin" / "query_exec"
    cmd = [
        str(binary),
        "-poly1",
        str(county),
        "-poly2",
        str(soil),
        "-mode=rt",
        f"-query={query}",
        f"-check={'true' if check else 'false'}",
        f"-xsect_factor={xsect_factor}",
        f"-warmup={warmup}",
        f"-repeat={repeat}",
        "-v=1",
    ]
    print(f"[goal3691] RayJoin {query} check={check} start", flush=True)
    proc = subprocess.run(
        cmd,
        cwd=rayjoin_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout_seconds,
        check=False,
    )
    parsed = _parse_rayjoin_output(proc.stdout)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "check": check,
        "query": query,
        **parsed,
    }


def _time_rtdl_cross_map_pip(
    *,
    county: Path,
    soil: Path,
    repeat: int,
    warmup: int,
    point_eps: float,
) -> dict[str, Any]:
    print("[goal3691] RTDL cross-map PIP load", flush=True)
    county_dataset = rt.load_cdb(county)
    soil_dataset = rt.load_cdb(soil)
    points = tuple(rt.chains_to_probe_points(soil_dataset))
    shapes = tuple(rt.chains_to_polygons(county_dataset))

    scene_start = time.perf_counter()
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    prepare_static_scene_sec = time.perf_counter() - scene_start

    points_start = time.perf_counter()
    prepared_points = prepared.prepare_point_probe_columns(points)
    prepare_point_columns_sec = time.perf_counter() - points_start

    executor_start = time.perf_counter()
    executor = prepared.prepare_relation_status_corrected_scalar_count_executor(
        prepared_points,
        point_eps=point_eps,
    )
    prepare_executor_sec = time.perf_counter() - executor_start

    try:
        measured: list[float] = []
        row_counts: list[int] = []
        runs: list[dict[str, Any]] = []
        for index in range(warmup + repeat):
            start = time.perf_counter()
            result = executor.run()
            elapsed = time.perf_counter() - start
            row_count = int(result["row_count"])
            is_warmup = index < warmup
            print(
                f"[goal3691] RTDL PIP {'warmup' if is_warmup else 'repeat'} "
                f"{index + 1}/{warmup + repeat} elapsed={elapsed:.6f}s row_count={row_count}",
                flush=True,
            )
            runs.append(
                {
                    "iteration": index,
                    "is_warmup": is_warmup,
                    "elapsed_sec": elapsed,
                    "row_count": row_count,
                    "native_traversal_seconds": float(result["traversal_seconds"]),
                    "candidate_row_count": int(result["candidate_row_count"]),
                    "boundary_candidate_row_count": int(result["boundary_candidate_row_count"]),
                    "dropped_candidate_row_count": int(result["dropped_candidate_row_count"]),
                }
            )
            if not is_warmup:
                measured.append(elapsed)
                row_counts.append(row_count)
        if len(set(row_counts)) != 1:
            raise RuntimeError(f"RTDL PIP row count changed across repeats: {row_counts}")
        return {
            "backend": "optix",
            "execution_route": "rtdl_cross_map_native_relation_status_corrected_scalar_count_executor",
            "county_chains": len(county_dataset.chains),
            "soil_chains": len(soil_dataset.chains),
            "point_count": len(points),
            "shape_count": len(shapes),
            "prepare_sec": {
                "prepare_static_scene_sec": prepare_static_scene_sec,
                "prepare_point_columns_sec": prepare_point_columns_sec,
                "prepare_executor_sec": prepare_executor_sec,
            },
            "hot_median_sec": _median(measured),
            "hot_repeat_secs": measured,
            "row_count": row_counts[-1],
            "runs": runs,
            "claim_boundary": _claim_boundary(),
        }
    finally:
        executor.close()
        prepared.close()


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    rayjoin_pip = _run_rayjoin_query(
        rayjoin_root=args.rayjoin_root,
        county=args.county,
        soil=args.soil,
        query="pip",
        repeat=args.rayjoin_repeat,
        warmup=args.rayjoin_warmup,
        check=False,
        xsect_factor=args.xsect_factor,
        timeout_seconds=args.timeout_seconds,
    )
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
    rayjoin_lsi_check = _run_rayjoin_query(
        rayjoin_root=args.rayjoin_root,
        county=args.county,
        soil=args.soil,
        query="lsi",
        repeat=1,
        warmup=1,
        check=True,
        xsect_factor=args.xsect_factor,
        timeout_seconds=args.timeout_seconds,
    )
    rtdl_pip = _time_rtdl_cross_map_pip(
        county=args.county,
        soil=args.soil,
        repeat=args.rtdl_repeat,
        warmup=args.rtdl_warmup,
        point_eps=args.point_eps,
    )
    rtdl_lsi = _run_exact_lsi_prepared_optix(
        f"{args.county} + {args.soil}",
        repeat=args.rtdl_repeat,
        warmup=args.rtdl_warmup,
    )

    rayjoin_pip_sec = rayjoin_pip.get("query_sec")
    rayjoin_lsi_sec = rayjoin_lsi.get("query_sec")
    return {
        "schema": SCHEMA,
        "goal": 3691,
        "generated_at_unix": time.time(),
        "rtdl_git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "rtdl_source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "rtdl_git_status_short": _command_output(["git", "status", "--short"]),
        "goal3691_scoped_source_paths": list(SCOPED_SOURCE_PATHS),
        "goal3691_scoped_source_status_short": _command_output(
            ["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS]
        ),
        "goal3691_scoped_source_dirty": bool(
            _command_output(["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS])
        ),
        "rayjoin_git_commit": _command_output(["git", "rev-parse", "HEAD"], cwd=args.rayjoin_root),
        "rayjoin_source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"], cwd=args.rayjoin_root),
        "rayjoin_git_status_short": _command_output(["git", "status", "--short"], cwd=args.rayjoin_root),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county": str(args.county),
        "soil": str(args.soil),
        "rayjoin": {
            "pip": rayjoin_pip,
            "lsi": rayjoin_lsi,
            "lsi_check": rayjoin_lsi_check,
        },
        "rtdl": {
            "pip": rtdl_pip,
            "lsi": rtdl_lsi,
        },
        "comparison": {
            "pip_query_speedup_rtdl_vs_rayjoin": (
                float(rayjoin_pip_sec) / float(rtdl_pip["hot_median_sec"]) if rayjoin_pip_sec else None
            ),
            "lsi_query_speedup_rtdl_vs_rayjoin": (
                float(rayjoin_lsi_sec) / float(rtdl_lsi["hot_median_sec"]) if rayjoin_lsi_sec else None
            ),
            "rayjoin_lsi_intersections": rayjoin_lsi.get("intersections"),
            "rayjoin_lsi_check_intersections": rayjoin_lsi_check.get("intersections"),
            "rtdl_lsi_row_count": int(rtdl_lsi["row_count"]),
            "lsi_count_delta_rtdl_minus_rayjoin": (
                int(rtdl_lsi["row_count"]) - int(rayjoin_lsi["intersections"])
                if rayjoin_lsi.get("intersections") is not None
                else None
            ),
            "pip_count_comparable_to_rayjoin": False,
            "pip_count_comparison_note": "RayJoin query_exec timing output does not print the PIP hit count.",
        },
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3691 RayJoin original same-source probe.")
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
    parser.add_argument("--rtdl-repeat", type=int, default=5)
    parser.add_argument("--rtdl-warmup", type=int, default=3)
    parser.add_argument("--xsect-factor", type=float, default=0.1)
    parser.add_argument("--point-eps", type=float, default=1.0e-9)
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3691] wrote {args.output}", flush=True)
    print(json.dumps(payload["comparison"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
