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
    }


def _device_column_summary(columns) -> dict[str, object]:
    summary: dict[str, object] = {
        "cupy_wrap_available": False,
        "cupy_flag_rows_all_active": None,
        "cupy_row_count": None,
    }
    try:
        cupy_columns = columns.as_cupy_columns()
        import cupy as cp  # type: ignore

        flags = (
            cupy_columns["requires_segment_intersection"].astype(cp.uint32)
            | cupy_columns["requires_point_containment"].astype(cp.uint32)
        )
        cp.cuda.Stream.null.synchronize()
        summary.update(
            {
                "cupy_wrap_available": True,
                "cupy_flag_rows_all_active": bool(cp.all(flags != 0).get()) if flags.size else True,
                "cupy_row_count": int(cupy_columns["left_id"].size),
            }
        )
    except Exception as exc:  # pragma: no cover - pod dependency diagnostic
        summary["cupy_wrap_error"] = str(exc)
    return summary


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    left_dataset = load_cdb(args.left_cdb)
    right_dataset = load_cdb(args.right_cdb)
    left_shapes = tuple(chains_to_polygons(left_dataset))
    right_shapes = tuple(chains_to_polygons(right_dataset))

    host_times: list[float] = []
    scalar_device_times: list[float] = []
    column_device_times: list[float] = []
    host_counts: list[int] = []
    scalar_device_counts: list[int] = []
    column_counts: list[int] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3447 generic shape-pair active relation device-column probe.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            host_payload = prepared.run_packed_left_host_exact(packed_left)
            scalar_device_payload = prepared.run_packed_left_device_continuation(packed_left)
            column_payload = prepared.run_packed_left_active_relation_device_columns(
                packed_left,
                max_rows=int(args.max_rows),
            )
            with prepared.active_relation_device_columns(
                packed_left,
                max_rows=int(args.max_rows),
            ) as columns:
                column_device_summary = _device_column_summary(columns)
                column_metadata = columns.to_metadata()

            host_count = int(host_payload["row_count"])
            scalar_count = int(scalar_device_payload["row_count"])
            column_count = int(column_payload["row_count"])
            host_time = float(host_payload["phases_sec"]["active_count_sec"])
            scalar_time = float(scalar_device_payload["phases_sec"]["active_count_device_continuation_sec"])
            column_time = float(column_payload["phases_sec"]["active_relation_device_columns_sec"])
            host_counts.append(host_count)
            scalar_device_counts.append(scalar_count)
            column_counts.append(column_count)
            host_times.append(host_time)
            scalar_device_times.append(scalar_time)
            column_device_times.append(column_time)
            counts_match = host_count == scalar_count == column_count
            runs.append(
                {
                    "iteration": index,
                    "host_count": host_count,
                    "scalar_device_count": scalar_count,
                    "column_row_count": column_count,
                    "counts_match": counts_match,
                    "host_active_count_sec": host_time,
                    "scalar_device_active_count_sec": scalar_time,
                    "active_relation_device_columns_sec": column_time,
                    "column_speedup_vs_host": host_time / column_time if column_time > 0.0 else None,
                    "scalar_device_native_phase_timings": scalar_device_payload["native_phase_timings"],
                    "column_native_phase_timings": column_payload["native_phase_timings"],
                    "column_metadata": column_metadata,
                    "column_device_summary": column_device_summary,
                    "claim_boundary": _claim_boundary(),
                }
            )
            print(
                "[goal3447] "
                f"iteration={index} host={host_count} scalar={scalar_count} columns={column_count} "
                f"match={counts_match} host={host_time:.6f}s scalar={scalar_time:.6f}s "
                f"columns={column_time:.6f}s speedup={(host_time / column_time if column_time > 0.0 else 0.0):.3f}x",
                flush=True,
            )

    return {
        "schema": "rtdl.goal3447.shape_pair_active_relation_device_columns.v1",
        "goal": 3447,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "iterations": int(args.iterations),
        "max_rows": int(args.max_rows),
        "all_counts_match": all(
            h == s == c for h, s, c in zip(host_counts, scalar_device_counts, column_counts)
        ),
        "host_counts": host_counts,
        "scalar_device_counts": scalar_device_counts,
        "column_counts": column_counts,
        "host_active_count_sec": _stats(host_times),
        "scalar_device_active_count_sec": _stats(scalar_device_times),
        "active_relation_device_columns_sec": _stats(column_device_times),
        "column_speedup_vs_host": _stats(
            [h / c for h, c in zip(host_times, column_device_times) if c > 0.0]
        ),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3447 shape-pair active relation device-column probe.")
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


if __name__ == "__main__":
    main()
