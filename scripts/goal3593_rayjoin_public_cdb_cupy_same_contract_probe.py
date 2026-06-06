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

from scripts.goal3589_rayjoin_cupy_same_contract_baseline import SCHEMA as GOAL3589_SCHEMA  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _claim_boundary  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_cupy_baseline  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_rtdl_optix  # noqa: E402


SCHEMA = "rtdl.goal3593.rayjoin_public_cdb_cupy_same_contract_probe.v1"
DEFAULT_ARTIFACT = ROOT / "docs" / "reports" / "goal3593_rayjoin_public_cdb_cupy_same_contract_a5000" / "summary.json"
CASE_ORDER = ("pip_county512", "lsi_county512_soil512", "overlay_county512_soil512")


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _case_dataset(case_id: str, data_dir: Path) -> tuple[str, str]:
    county = data_dir / "br_county_start256_count512.cdb"
    soil = data_dir / "br_soil_start256_count512.cdb"
    if case_id == "pip_county512":
        return "pip", str(county)
    if case_id == "lsi_county512_soil512":
        return "lsi", f"{county} + {soil}"
    if case_id == "overlay_county512_soil512":
        return "overlay_seed", f"{county} + {soil}"
    raise ValueError(f"unknown case id: {case_id}")


def _selected_cases(value: str) -> tuple[str, ...]:
    if value == "all":
        return CASE_ORDER
    selected = tuple(part.strip() for part in value.split(",") if part.strip())
    if not selected:
        raise ValueError("case list is empty")
    for case_id in selected:
        if case_id not in CASE_ORDER:
            raise ValueError(f"unknown case id: {case_id}")
    return selected


def build_dry_run(*, data_dir: Path, cases: tuple[str, ...], repeat: int, warmup: int) -> dict[str, object]:
    rows = []
    for case_id in cases:
        workload, dataset = _case_dataset(case_id, data_dir)
        rows.append(
            {
                "case_id": case_id,
                "workload": workload,
                "dataset": dataset,
                "planned_cupy_baseline": "Goal3589 dense CUDA-core same-contract baseline",
                "planned_rtdl_optix": "Goal3589 hot prepared RTDL/OptiX route",
            }
        )
    return {
        "schema": SCHEMA,
        "dry_run": True,
        "goal3589_schema": GOAL3589_SCHEMA,
        "data_dir": str(data_dir),
        "repeat": repeat,
        "warmup": warmup,
        "rows": rows,
        "claim_boundary": _claim_boundary(),
    }


def run_probe(*, data_dir: Path, cases: tuple[str, ...], repeat: int, warmup: int) -> dict[str, object]:
    rows = []
    for case_id in cases:
        workload, dataset = _case_dataset(case_id, data_dir)
        for part in [piece.strip() for piece in dataset.split("+")]:
            if part and not Path(part).exists():
                raise FileNotFoundError(part)
        print(f"[goal3593] {case_id} CuPy baseline start", flush=True)
        cupy = run_cupy_baseline(workload, dataset, repeat=repeat, warmup=warmup)
        print(f"[goal3593] {case_id} RTDL/OptiX route start", flush=True)
        rtdl_optix = run_rtdl_optix(workload, dataset, repeat=repeat, warmup=warmup)
        counts_match = int(cupy["row_count"]) == int(rtdl_optix["row_count"])
        if not counts_match:
            raise RuntimeError(
                f"{case_id} count mismatch: CuPy={cupy['row_count']} RTDL/OptiX={rtdl_optix['row_count']}"
            )
        speedup = float(cupy["hot_median_sec"]) / float(rtdl_optix["hot_median_sec"])
        rows.append(
            {
                "case_id": case_id,
                "workload": workload,
                "dataset": dataset,
                "cupy_cuda_core_baseline": cupy,
                "rtdl_optix": rtdl_optix,
                "counts_match": counts_match,
                "rtdl_optix_speedup_vs_cupy_cuda_core": speedup,
                "interpretation": (
                    "RTDL/OptiX faster than bounded public-CDB dense CuPy baseline"
                    if speedup > 1.0
                    else "CuPy faster or tied on this bounded public-CDB same-contract row"
                ),
                "claim_boundary": _claim_boundary(),
            }
        )
    ratios = [float(row["rtdl_optix_speedup_vs_cupy_cuda_core"]) for row in rows]
    return {
        "schema": SCHEMA,
        "dry_run": False,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "data_dir": str(data_dir),
        "repeat": repeat,
        "warmup": warmup,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_counts_match": all(bool(row["counts_match"]) for row in rows),
            "min_rtdl_optix_speedup_vs_cupy_cuda_core": min(ratios) if ratios else None,
            "geomean_rtdl_optix_speedup_vs_cupy_cuda_core": (
                math.prod(ratios) ** (1.0 / len(ratios)) if ratios else None
            ),
        },
        "boundary": (
            "Bounded public-CDB same-contract probe only. This is not a RayJoin paper "
            "reproduction, not a public RT-core speedup claim, and not release evidence."
        ),
        "claim_boundary": _claim_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3593 bounded public-CDB RayJoin same-contract probe.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--cases", default="all")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args(argv)
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    cases = _selected_cases(args.cases)
    payload = (
        build_dry_run(data_dir=args.data_dir, cases=cases, repeat=args.repeat, warmup=args.warmup)
        if args.dry_run
        else run_probe(data_dir=args.data_dir, cases=cases, repeat=args.repeat, warmup=args.warmup)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3593] wrote {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
