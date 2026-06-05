from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    prepare_rayjoin_optix_cupy_refined_pip,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import chains_to_probe_points  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _stats(values: list[float]) -> dict[str, float]:
    return {
        "min": min(values),
        "median": statistics.median(values),
        "max": max(values),
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    dataset = load_cdb(args.county_cdb)
    points = tuple(chains_to_probe_points(dataset))
    shapes = tuple(chains_to_polygons(dataset))
    runs: list[dict[str, object]] = []
    row_counts: list[int] = []
    candidate_counts: list[int] = []
    candidate_times: list[float] = []
    refine_times: list[float] = []

    with prepare_rayjoin_optix_cupy_refined_pip(
        points,
        shapes,
        dataset=str(args.county_cdb),
        dataset_note="Goal3435 full public CDB repeated-handle probe.",
        candidate_max_rows=int(args.candidate_max_rows),
    ) as prepared:
        prepare_phases = dict(prepared.prepare_phases_sec)
        for index in range(int(args.iterations)):
            payload = prepared.run(result_mode="count", include_rows=False)
            row_counts.append(int(payload["row_count"]))
            candidate_count = int(payload["candidate_columns"]["capacity_status"]["row_count"])
            candidate_counts.append(candidate_count)
            candidate_times.append(float(payload["phases_sec"]["candidate_device_columns_sec"]))
            refine_times.append(float(payload["phases_sec"]["prepared_cupy_refine_sec"]))
            runs.append(
                {
                    "iteration": index,
                    "row_count": int(payload["row_count"]),
                    "candidate_row_count": candidate_count,
                    "phases_sec": payload["phases_sec"],
                    "prepared_reuse": payload["prepared_reuse"],
                    "partner_refinement": payload["partner_refinement"],
                    "claim_boundary": payload["claim_boundary"],
                }
            )
            print(
                "[goal3435] iteration "
                f"{index} candidates={candidate_count} rows={payload['row_count']} "
                f"candidate={candidate_times[-1]:.6f}s refine={refine_times[-1]:.6f}s",
                flush=True,
            )

    return {
        "schema": "rtdl.goal3435.spatial_rayjoin_prepared_cupy_pip_reuse.v1",
        "goal": 3435,
        "route": "prepared_optix_cupy_refined_pip_reuse_handle",
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county_cdb": str(args.county_cdb),
        "point_count": len(points),
        "shape_count": len(shapes),
        "candidate_max_rows": int(args.candidate_max_rows),
        "iterations": int(args.iterations),
        "prepare_phases_sec": prepare_phases,
        "row_counts": row_counts,
        "candidate_row_counts": candidate_counts,
        "candidate_device_columns_sec": _stats(candidate_times),
        "prepared_cupy_refine_sec": _stats(refine_times),
        "runs": runs,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3435 Spatial RayJoin prepared CuPy PIP reuse probe.")
    parser.add_argument(
        "--county-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument("--candidate-max-rows", type=int, default=60000)
    parser.add_argument("--iterations", type=int, default=4)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
