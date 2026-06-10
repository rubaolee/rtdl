from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _stats(values: list[float]) -> dict[str, float]:
    return {"min": min(values), "median": statistics.median(values), "max": max(values)}


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    left_dataset = load_cdb(args.left_cdb)
    right_dataset = load_cdb(args.right_cdb)
    left_shapes = tuple(chains_to_polygons(left_dataset))
    right_shapes = tuple(chains_to_polygons(right_dataset))

    relation_times: list[float] = []
    continuation_times: list[float] = []
    row_counts: list[int] = []
    group_counts: list[int] = []
    area_sums: list[float] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3459 large bounds-overlap continuation probe.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            relation_start = time.perf_counter()
            columns = prepared.active_relation_device_columns(
                packed_left,
                max_rows=int(args.max_rows),
            )
            cp.cuda.Stream.null.synchronize()
            relation_sec = time.perf_counter() - relation_start
            try:
                continuation_start = time.perf_counter()
                result = rt.shape_pair_relation_bounds_overlap_area_cupy(columns, group_by="left")
                cp.cuda.Stream.null.synchronize()
                continuation_sec = time.perf_counter() - continuation_start
                row_area_sum = float(cp.sum(result.row_areas).get()) if int(columns.row_count) else 0.0
                group_count = int(result.group_keys.size) if result.group_keys is not None else 0
                nonnegative = bool(cp.all(result.row_areas >= 0.0).get()) if int(columns.row_count) else True
                relation_times.append(relation_sec)
                continuation_times.append(continuation_sec)
                row_counts.append(int(columns.row_count))
                group_counts.append(group_count)
                area_sums.append(row_area_sum)
                run = {
                    "iteration": index,
                    "relation_columns_sec": relation_sec,
                    "bounds_overlap_area_continuation_sec": continuation_sec,
                    "row_count": int(columns.row_count),
                    "active_relation_count": int(columns.active_relation_count),
                    "group_count": group_count,
                    "bounds_overlap_area_sum": row_area_sum,
                    "all_row_areas_nonnegative": nonnegative,
                    "continuation_metadata": result.to_metadata(),
                    "relation_metadata_geometry_payload_device_resident": bool(
                        columns.to_metadata()["runtime"]["geometry_payload"]["device_resident"]
                    ),
                    "relation_metadata_ordinal_columns_device_resident": bool(
                        columns.to_metadata()["runtime"]["ordinal_columns"]["device_resident"]
                    ),
                    "claim_boundary": _claim_boundary(),
                }
                runs.append(run)
                print(
                    "[goal3459] "
                    f"iteration={index} rows={run['row_count']} groups={group_count} "
                    f"area_sum={row_area_sum:.6f} relation={relation_sec:.6f}s "
                    f"bounds_area={continuation_sec:.6f}s nonnegative={nonnegative}",
                    flush=True,
                )
            finally:
                columns.close()

    return {
        "schema": "rtdl.goal3459.shape_pair_bounds_overlap_area_large.v1",
        "goal": 3459,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "iterations": int(args.iterations),
        "max_rows": int(args.max_rows),
        "row_counts": row_counts,
        "group_counts": group_counts,
        "bounds_overlap_area_sums": area_sums,
        "all_row_counts_stable": len(set(row_counts)) == 1,
        "all_group_counts_stable": len(set(group_counts)) == 1,
        "all_area_sums_stable": max(area_sums) - min(area_sums) <= 1.0e-6 if area_sums else True,
        "all_nonnegative": all(run["all_row_areas_nonnegative"] for run in runs),
        "relation_columns_sec": _stats(relation_times),
        "bounds_overlap_area_continuation_sec": _stats(continuation_times),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3459 large shape-pair bounds-overlap area continuation probe.")
    parser.add_argument(
        "--left-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--iterations", type=int, default=4)
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not payload["all_row_counts_stable"] or not payload["all_group_counts_stable"] or not payload["all_nonnegative"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
