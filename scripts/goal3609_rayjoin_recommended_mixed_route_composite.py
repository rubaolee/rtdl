#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402
from rtdsl.datasets import CdbDataset  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_cupy_baseline  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_rtdl_optix  # noqa: E402


SCHEMA = "rtdl.goal3609.rayjoin_recommended_mixed_route_composite.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal3609_rayjoin_recommended_mixed_route_composite_a5000" / "summary.json"
WORKLOADS = ("pip", "lsi", "overlay_seed")


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
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


def _parse_counts(value: str) -> tuple[int, ...]:
    counts = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not counts:
        raise ValueError("--counts must not be empty")
    for count in counts:
        if count <= 0:
            raise ValueError("--counts values must be positive")
    return counts


def _materialize_slice(source: Path, output: Path, *, start: int, count: int) -> Path:
    if output.exists():
        return output
    source_dataset = rt.load_cdb(source)
    sliced = CdbDataset(
        name=f"{source.stem}_start{start}_count{count}",
        chains=tuple(source_dataset.chains[start : start + count]),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    rt.write_cdb(sliced, output)
    return output


def _datasets_for_count(*, data_dir: Path, county_source: Path, soil_source: Path, start: int, count: int) -> dict[str, str]:
    county = _materialize_slice(
        county_source,
        data_dir / f"br_county_start{start}_count{count}.cdb",
        start=start,
        count=count,
    )
    soil = _materialize_slice(
        soil_source,
        data_dir / f"br_soil_start{start}_count{count}.cdb",
        start=start,
        count=count,
    )
    return {
        "pip": str(county),
        "lsi": f"{county} + {soil}",
        "overlay_seed": f"{county} + {soil}",
    }


def run_composite(args: argparse.Namespace) -> dict[str, object]:
    counts = _parse_counts(args.counts)
    rows = []
    for count in counts:
        print(f"[goal3609] materialize count={count}", flush=True)
        datasets = _datasets_for_count(
            data_dir=args.data_dir,
            county_source=args.county_source_cdb,
            soil_source=args.soil_source_cdb,
            start=args.start,
            count=count,
        )
        cupy_rows: dict[str, dict[str, object]] = {}
        recommended_rows: dict[str, dict[str, object]] = {}
        for workload in WORKLOADS:
            print(f"[goal3609] count={count} workload={workload} CuPy baseline start", flush=True)
            cupy_rows[workload] = run_cupy_baseline(
                workload,
                datasets[workload],
                repeat=args.repeat,
                warmup=args.warmup,
            )
        recommended_rows["pip"] = {
            **cupy_rows["pip"],
            "execution_route": "recommended_cupy_dense_pip_scalar_count",
            "recommended_route_reason": "Goal3604/3606 show current boundary-event RT route is slow and not robust.",
        }
        for workload in ("lsi", "overlay_seed"):
            print(f"[goal3609] count={count} workload={workload} RTDL/OptiX recommended route start", flush=True)
            recommended_rows[workload] = run_rtdl_optix(
                workload,
                datasets[workload],
                repeat=args.repeat,
                warmup=args.warmup,
            )
        workload_rows = []
        for workload in WORKLOADS:
            cupy = cupy_rows[workload]
            recommended = recommended_rows[workload]
            counts_match = int(cupy["row_count"]) == int(recommended["row_count"])
            if not counts_match:
                raise RuntimeError(
                    f"{workload} count mismatch at count={count}: "
                    f"CuPy={cupy['row_count']} recommended={recommended['row_count']}"
                )
            speedup = float(cupy["hot_median_sec"]) / float(recommended["hot_median_sec"])
            workload_rows.append(
                {
                    "workload": workload,
                    "dataset": datasets[workload],
                    "all_cupy_baseline": cupy,
                    "recommended_route": recommended,
                    "counts_match": counts_match,
                    "recommended_speedup_vs_cupy": speedup,
                    "recommended_backend": recommended.get("backend", "cupy"),
                    "recommended_route_kind": (
                        "cupy_dense_cuda_core"
                        if workload == "pip"
                        else "rtdl_optix"
                    ),
                    "claim_boundary": _claim_boundary(),
                }
            )
        cupy_total = sum(float(row["all_cupy_baseline"]["hot_median_sec"]) for row in workload_rows)
        recommended_total = sum(float(row["recommended_route"]["hot_median_sec"]) for row in workload_rows)
        rows.append(
            {
                "chain_count": count,
                "datasets": datasets,
                "workloads": workload_rows,
                "all_cupy_sum_median_sec": cupy_total,
                "recommended_mixed_sum_median_sec": recommended_total,
                "recommended_mixed_speedup_vs_all_cupy": cupy_total / recommended_total,
                "all_counts_match": all(bool(row["counts_match"]) for row in workload_rows),
                "mix_definition": "unweighted sum of PIP, LSI, and overlay_seed hot median seconds",
                "claim_boundary": _claim_boundary(),
            }
        )
    ratios = [float(row["recommended_mixed_speedup_vs_all_cupy"]) for row in rows]
    return {
        "schema": SCHEMA,
        "goal": 3609,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "start": int(args.start),
        "counts": list(counts),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_counts_match": all(bool(row["all_counts_match"]) for row in rows),
            "geomean_recommended_mixed_speedup_vs_all_cupy": (
                math.prod(ratios) ** (1.0 / len(ratios)) if ratios else None
            ),
            "min_recommended_mixed_speedup_vs_all_cupy": min(ratios) if ratios else None,
        },
        "interpretation": (
            "Internal RayJoin mixed-route composite: compare all-CuPy dense same-contract "
            "baseline against the recommended v2.9 route mix, using CuPy for PIP scalar count "
            "and RTDL/OptiX for LSI and overlay_seed. This is not RayJoin paper reproduction "
            "or a public speedup claim."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3609 RayJoin recommended mixed-route composite.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "rayjoin_public_cdb")
    parser.add_argument("--county-source-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb")
    parser.add_argument("--soil-source-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_soil.cdb")
    parser.add_argument("--start", type=int, default=256)
    parser.add_argument("--counts", default="512")
    parser.add_argument("--repeat", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    return args


def main() -> int:
    args = parse_args()
    payload = run_composite(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3609] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
