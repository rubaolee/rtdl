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

from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_compact_grouped_count_left_segments,
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_compact_grouped_count_segments,
    prepare_rayjoin_optix_cupy_refined_pip,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import chains_to_probe_points  # noqa: E402
from rtdsl.datasets import chains_to_segment_columns  # noqa: E402
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


def _false_claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
    }


def _run_pip(args: argparse.Namespace, county_dataset) -> dict[str, object]:
    points = tuple(chains_to_probe_points(county_dataset))
    shapes = tuple(chains_to_polygons(county_dataset))
    runs: list[dict[str, object]] = []
    row_counts: list[int] = []
    candidate_counts: list[int] = []
    candidate_times: list[float] = []
    refine_times: list[float] = []

    with prepare_rayjoin_optix_cupy_refined_pip(
        points,
        shapes,
        dataset=str(args.county_cdb),
        dataset_note="Goal3438 prepared subroute probe: PIP.",
        candidate_max_rows=int(args.candidate_max_rows),
    ) as prepared:
        prepare_phases = dict(prepared.prepare_phases_sec)
        for index in range(int(args.iterations)):
            payload = prepared.run(result_mode="count", include_rows=False)
            row_count = int(payload["row_count"])
            candidate_count = int(payload["candidate_columns"]["capacity_status"]["row_count"])
            row_counts.append(row_count)
            candidate_counts.append(candidate_count)
            candidate_times.append(float(payload["phases_sec"]["candidate_device_columns_sec"]))
            refine_times.append(float(payload["phases_sec"]["prepared_cupy_refine_sec"]))
            runs.append(
                {
                    "iteration": index,
                    "row_count": row_count,
                    "candidate_row_count": candidate_count,
                    "phases_sec": payload["phases_sec"],
                    "prepared_reuse": payload["prepared_reuse"],
                    "claim_boundary": payload["claim_boundary"],
                }
            )
            print(
                "[goal3438:pip] "
                f"iteration={index} candidates={candidate_count} rows={row_count} "
                f"candidate={candidate_times[-1]:.6f}s refine={refine_times[-1]:.6f}s",
                flush=True,
            )

    return {
        "route": "prepared_optix_cupy_refined_pip_reuse_handle",
        "point_count": len(points),
        "shape_count": len(shapes),
        "candidate_max_rows": int(args.candidate_max_rows),
        "prepare_phases_sec": prepare_phases,
        "row_counts": row_counts,
        "candidate_row_counts": candidate_counts,
        "candidate_device_columns_sec": _stats(candidate_times),
        "prepared_cupy_refine_sec": _stats(refine_times),
        "runs": runs,
    }


def _run_lsi(args: argparse.Namespace, county_dataset, soil_dataset) -> dict[str, object]:
    left = chains_to_segment_columns(county_dataset)
    right = chains_to_segment_columns(soil_dataset)
    runs: list[dict[str, object]] = []
    row_counts: list[int] = []
    count_times: list[float] = []

    with prepare_rayjoin_optix_compact_grouped_count_segments(
        right,
        dataset=f"{args.county_cdb} + {args.soil_cdb}",
        dataset_note="Goal3438 prepared subroute probe: LSI.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_compact_grouped_count_left_segments(left)
        for index in range(int(args.iterations)):
            payload = prepared.run_packed_left_dense_count(packed_left, include_rows=False)
            row_count = int(payload["row_count"])
            phase = float(payload["phases_sec"]["left_id_count_device_columns_sec"])
            row_counts.append(row_count)
            count_times.append(phase)
            runs.append(
                {
                    "iteration": index,
                    "row_count": row_count,
                    "phases_sec": payload["phases_sec"],
                    "prepared_reuse": payload["prepared_reuse"],
                    "packed_left_reuse": payload["packed_left_reuse"],
                    "claim_boundary": payload["claim_boundary"],
                }
            )
            print(
                "[goal3438:lsi] "
                f"iteration={index} rows={row_count} dense_count={phase:.6f}s",
                flush=True,
            )

        return {
            "route": "prepared_optix_left_id_dense_count_reuse",
            "left_segment_count": int(packed_left.count),
            "right_segment_count": int(prepared._right_segment_count),
            "prepare_static_scene_sec": float(prepared.prepare_static_scene_sec),
            "pack_left_sec": float(packed_left.pack_seconds),
            "row_counts": row_counts,
            "left_id_count_device_columns_sec": _stats(count_times),
            "runs": runs,
        }


def _run_overlay(args: argparse.Namespace, county_dataset, soil_dataset) -> dict[str, object]:
    left = tuple(chains_to_polygons(county_dataset))
    right = tuple(chains_to_polygons(soil_dataset))
    runs: list[dict[str, object]] = []
    row_counts: list[int] = []
    active_count_times: list[float] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right,
        dataset=f"{args.county_cdb} + {args.soil_cdb}",
        dataset_note="Goal3438 prepared subroute probe: overlay-seed active count.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left)
        for index in range(int(args.iterations)):
            payload = prepared.run_packed_left(packed_left)
            row_count = int(payload["row_count"])
            phase = float(
                payload["phases_sec"].get(
                    "active_count_device_continuation_sec",
                    payload["phases_sec"].get("active_count_sec", 0.0),
                )
            )
            row_counts.append(row_count)
            active_count_times.append(phase)
            runs.append(
                {
                    "iteration": index,
                    "row_count": row_count,
                    "phases_sec": payload["phases_sec"],
                    "native_phase_timings": payload["native_phase_timings"],
                    "prepared_reuse": payload["prepared_reuse"],
                    "packed_left_reuse": payload["packed_left_reuse"],
                    "claim_boundary": payload["claim_boundary"],
                }
            )
            print(
                "[goal3438:overlay] "
                f"iteration={index} active_count={row_count} active_count_sec={phase:.6f}s",
                flush=True,
            )

        return {
            "route": "prepared_optix_shape_pair_active_count_reuse",
            "left_shape_count": int(packed_left.count),
            "right_shape_count": len(right),
            "prepare_static_scene_sec": float(prepared.prepare_static_scene_sec),
            "pack_left_sec": float(packed_left.pack_seconds),
            "row_counts": row_counts,
            "active_count_sec": _stats(active_count_times),
            "last_native_phase_timings": runs[-1]["native_phase_timings"] if runs else None,
            "runs": runs,
        }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    county_dataset = load_cdb(args.county_cdb)
    soil_dataset = load_cdb(args.soil_cdb)
    routes = {
        "pip": _run_pip(args, county_dataset),
        "lsi_dense_count": _run_lsi(args, county_dataset, soil_dataset),
        "overlay_active_count": _run_overlay(args, county_dataset, soil_dataset),
    }
    return {
        "schema": "rtdl.goal3438.spatial_rayjoin_prepared_subroute_reuse.v1",
        "goal": 3438,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county_cdb": str(args.county_cdb),
        "soil_cdb": str(args.soil_cdb),
        "iterations": int(args.iterations),
        "routes": routes,
        "claim_boundary": _false_claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3438 Spatial RayJoin prepared subroute reuse probe.")
    parser.add_argument(
        "--county-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument(
        "--soil-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_soil.cdb",
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
