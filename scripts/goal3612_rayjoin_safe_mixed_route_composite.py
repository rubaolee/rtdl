#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    run_rayjoin_prepared_optix_workload,
)
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_cupy_baseline  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_rtdl_optix  # noqa: E402
from scripts.goal3609_rayjoin_recommended_mixed_route_composite import (  # noqa: E402
    _claim_boundary,
)
from scripts.goal3609_rayjoin_recommended_mixed_route_composite import (  # noqa: E402
    _command_output,
)
from scripts.goal3609_rayjoin_recommended_mixed_route_composite import (  # noqa: E402
    _datasets_for_count,
)
from scripts.goal3609_rayjoin_recommended_mixed_route_composite import (  # noqa: E402
    _parse_counts,
)


SCHEMA = "rtdl.goal3612.rayjoin_safe_mixed_route_composite.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal3612_rayjoin_safe_mixed_route_composite_a5000" / "summary.json"
WORKLOADS = ("pip", "lsi", "overlay_seed")


def _run_exact_lsi_prepared_optix(dataset: str, *, repeat: int, warmup: int) -> dict[str, object]:
    payload = run_rayjoin_prepared_optix_workload(
        "lsi",
        dataset=dataset,
        result_mode="count",
        include_rows=False,
        query_repeat=repeat,
        warmup=warmup,
        prepare_left_for_count=True,
    )
    phases = payload["phases_sec"]
    return {
        "backend": payload.get("backend", "optix"),
        "execution_route": "prepared_optix_exact_segment_pair_count",
        "rt_core_accelerated": True,
        "partner_accelerated": False,
        "dataset": dataset,
        "output_contract": payload["summary"]["output_contract"],
        "prepare_sec": {
            key: value
            for key, value in phases.items()
            if key.startswith("prepare_") or key.endswith("_pack_sec")
        },
        "hot_median_sec": float(phases["prepared_query_sec"]),
        "hot_total_sec": float(phases["prepared_query_sec_total_sec"]),
        "hot_repeat": int(phases["prepared_query_sec_repeat"]),
        "hot_warmup": int(phases["prepared_query_sec_warmup"]),
        "row_count": int(payload["row_count"]),
        "native_phase_timings": payload.get("native_phase_timings", {}),
        "prepared_left_for_count": bool(payload["summary"].get("prepared_left_for_count")),
        "segment_policy": "device_double_exact_count_during_optix_intersection_program_identity_range",
        "segment_pair_count_route": payload["summary"].get("segment_pair_count_route"),
        "same_contract_repair_reason": (
            "Goal3610 showed the pure device left-id dense count route counts eight extra "
            "near-degenerate 4096-chain LSI candidates; this exact prepared route applies "
            "the refined segment-pair contract and matches the CuPy dense baseline."
        ),
        "claim_boundary": payload.get("claim_boundary", _claim_boundary()),
    }


def run_composite(args: argparse.Namespace) -> dict[str, object]:
    counts = _parse_counts(args.counts)
    rows = []
    for count in counts:
        print(f"[goal3612] materialize count={count}", flush=True)
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
            print(f"[goal3612] count={count} workload={workload} CuPy baseline start", flush=True)
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
        print(f"[goal3612] count={count} workload=lsi exact RTDL/OptiX route start", flush=True)
        recommended_rows["lsi"] = _run_exact_lsi_prepared_optix(
            datasets["lsi"],
            repeat=args.repeat,
            warmup=args.warmup,
        )
        print(f"[goal3612] count={count} workload=overlay_seed RTDL/OptiX active-count route start", flush=True)
        recommended_rows["overlay_seed"] = run_rtdl_optix(
            "overlay_seed",
            datasets["overlay_seed"],
            repeat=args.repeat,
            warmup=args.warmup,
        )

        workload_rows = []
        for workload in WORKLOADS:
            cupy = cupy_rows[workload]
            recommended = recommended_rows[workload]
            recommended["claim_boundary"] = {
                **_claim_boundary(),
                **dict(recommended.get("claim_boundary", {})),
            }
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
                        else (
                            "rtdl_optix_exact_refined_count"
                            if workload == "lsi"
                            else "rtdl_optix_active_count"
                        )
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
                "recommended_safe_mixed_sum_median_sec": recommended_total,
                "recommended_safe_mixed_speedup_vs_all_cupy": cupy_total / recommended_total,
                "all_counts_match": all(bool(row["counts_match"]) for row in workload_rows),
                "mix_definition": "unweighted sum of PIP, LSI, and overlay_seed hot median seconds",
                "claim_boundary": _claim_boundary(),
            }
        )
    ratios = [float(row["recommended_safe_mixed_speedup_vs_all_cupy"]) for row in rows]
    return {
        "schema": SCHEMA,
        "goal": 3612,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short", "--untracked-files=no"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "start": int(args.start),
        "counts": list(counts),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_counts_match": all(bool(row["all_counts_match"]) for row in rows),
            "geomean_recommended_safe_mixed_speedup_vs_all_cupy": (
                math.prod(ratios) ** (1.0 / len(ratios)) if ratios else None
            ),
            "min_recommended_safe_mixed_speedup_vs_all_cupy": min(ratios) if ratios else None,
        },
        "interpretation": (
            "Internal RayJoin safe mixed-route composite: PIP uses CuPy dense scalar count, "
            "LSI uses exact prepared RTDL/OptiX count with a device-side double predicate "
            "inside the custom intersection program over identity-range primitive records, "
            "and overlay_seed uses RTDL/OptiX active-count. This repairs "
            "the Goal3610 4096-chain LSI mismatch by choosing the exact same-contract route."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3612 RayJoin safe mixed-route composite.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "rayjoin_public_cdb")
    parser.add_argument("--county-source-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb")
    parser.add_argument("--soil-source-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_soil.cdb")
    parser.add_argument("--start", type=int, default=256)
    parser.add_argument("--counts", default="4096")
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
    print(f"[goal3612] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
