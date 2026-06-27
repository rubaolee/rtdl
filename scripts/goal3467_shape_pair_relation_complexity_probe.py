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
from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
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

    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    row_counts: list[int] = []
    relation_times: list[float] = []
    complexity_times: list[float] = []
    general_overlay_counts: list[int] = []
    nonconvex_counts: list[int] = []
    both_convex_counts: list[int] = []
    rows_above_threshold_counts: list[int] = []
    max_pair_vertex_counts: list[int] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3467 relation complexity probe before exact overlay-area continuation.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            relation_start = time.perf_counter()
            with prepared.active_relation_device_columns(
                packed_left,
                max_rows=int(args.max_rows),
            ) as columns:
                cp.cuda.Stream.null.synchronize()
                relation_sec = time.perf_counter() - relation_start

                complexity_start = time.perf_counter()
                complexity = rt.shape_pair_relation_complexity_cupy(
                    columns,
                    simple_vertex_threshold=int(args.simple_vertex_threshold),
                )
                cp.cuda.Stream.null.synchronize()
                complexity_sec = time.perf_counter() - complexity_start
                metadata = complexity.to_metadata()

                row_counts.append(int(columns.row_count))
                relation_times.append(relation_sec)
                complexity_times.append(complexity_sec)
                general_overlay_counts.append(int(metadata["general_overlay_required_row_count"]))
                nonconvex_counts.append(int(metadata["nonconvex_row_count"]))
                both_convex_counts.append(int(metadata["both_convex_row_count"]))
                rows_above_threshold_counts.append(int(metadata["rows_above_simple_vertex_threshold"]))
                max_pair_vertex_counts.append(int(metadata["max_pair_vertex_count"]))
                run = {
                    "iteration": index,
                    "row_count": int(columns.row_count),
                    "relation_columns_sec": relation_sec,
                    "complexity_classification_sec": complexity_sec,
                    "complexity_metadata": metadata,
                    "claim_boundary": _claim_boundary(),
                }
                runs.append(run)
                print(
                    "[goal3467] "
                    f"iteration={index} rows={run['row_count']} "
                    f"general_overlay_required={metadata['general_overlay_required_row_count']} "
                    f"nonconvex_rows={metadata['nonconvex_row_count']} "
                    f"above_threshold={metadata['rows_above_simple_vertex_threshold']} "
                    f"max_pair_vertices={metadata['max_pair_vertex_count']} "
                    f"relation={relation_sec:.6f}s complexity={complexity_sec:.6f}s",
                    flush=True,
                )

    return {
        "schema": "rtdl.goal3467.shape_pair_relation_complexity_probe.v1",
        "goal": 3467,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "iterations": int(args.iterations),
        "max_rows": int(args.max_rows),
        "simple_vertex_threshold": int(args.simple_vertex_threshold),
        "row_counts": row_counts,
        "general_overlay_required_row_counts": general_overlay_counts,
        "nonconvex_row_counts": nonconvex_counts,
        "both_convex_row_counts": both_convex_counts,
        "rows_above_simple_vertex_threshold_counts": rows_above_threshold_counts,
        "max_pair_vertex_counts": max_pair_vertex_counts,
        "all_row_counts_stable": len(set(row_counts)) == 1,
        "all_general_overlay_counts_stable": len(set(general_overlay_counts)) == 1,
        "simple_clip_sufficient_for_all_rows": all(count == 0 for count in general_overlay_counts),
        "relation_columns_sec": _stats(relation_times),
        "complexity_classification_sec": _stats(complexity_times),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3467 relation-complexity probe before exact overlay area.")
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
    parser.add_argument("--simple-vertex-threshold", type=int, default=64)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not payload["all_row_counts_stable"] or not payload["all_general_overlay_counts_stable"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
