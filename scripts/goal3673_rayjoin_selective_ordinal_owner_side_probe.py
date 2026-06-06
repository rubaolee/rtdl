from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())


def _json_pairs(pairs: list[tuple[int, int]], *, limit: int = 20) -> list[list[int]]:
    return [[int(left), int(right)] for left, right in pairs[:limit]]


def _gpu_name() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
        ).strip()
    except Exception:
        return "not-recorded"


def _commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "not-recorded"


def _dirty() -> bool:
    try:
        return bool(subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip())
    except Exception:
        return True


def run_probe(
    *,
    dataset_path: Path,
    selected_point_ids: tuple[int, ...],
    output_path: Path,
    max_rows: int,
) -> dict[str, Any]:
    import cupy as cp  # type: ignore
    import rtdsl as rt
    from rtdsl.datasets import chains_to_polygons
    from rtdsl.datasets import chains_to_probe_points
    from rtdsl.datasets import load_cdb
    from rtdsl.optix_runtime import pack_points
    from rtdsl.optix_runtime import pack_polygons
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    dataset = load_cdb(dataset_path)
    points = chains_to_probe_points(dataset)
    polygons = chains_to_polygons(dataset)
    point_chains = tuple(chain for chain in dataset.chains if chain.points)
    polygon_chains = tuple(chain for chain in dataset.chains if len(chain.points) >= 3)
    if len(points) != len(point_chains):
        raise ValueError("probe point sequence does not match point chain sequence")
    if len(polygons) != len(polygon_chains):
        raise ValueError("polygon sequence does not match polygon chain sequence")

    selected_ordinals = [index for index, point in enumerate(points) if int(point.id) in selected_point_ids]
    packed_points = pack_points(records=points, dimension=2)
    packed_shapes = pack_polygons(records=polygons)
    prepared = prepare_point_closed_shape_membership_2d_optix(packed_shapes)
    try:
        exact_start = time.perf_counter()
        exact_rows = prepared.run(packed_points)
        exact_sec = time.perf_counter() - exact_start
        exact_pairs = Counter((int(row["point_id"]), int(row["shape_id"])) for row in exact_rows)

        candidate_start = time.perf_counter()
        columns = prepared.candidate_device_columns(packed_points, max_rows=max_rows)
        candidate_sec = time.perf_counter() - candidate_start
        try:
            column_map = columns.as_cupy_columns()
            candidate_pairs = Counter(
                zip(
                    cp.asnumpy(column_map["point_id"]).astype(int).tolist(),
                    cp.asnumpy(column_map["shape_id"]).astype(int).tolist(),
                )
            )
            owner_face_ids: list[int] = []
            owner_side_codes: list[str] = []
            for chain in point_chains:
                if int(chain.left_face_id) != 0:
                    owner_face_ids.append(int(chain.left_face_id))
                    owner_side_codes.append("left")
                elif int(chain.right_face_id) != 0:
                    owner_face_ids.append(int(chain.right_face_id))
                    owner_side_codes.append("right")
                else:
                    owner_face_ids.append(-1)
                    owner_side_codes.append("either")

            filter_start = time.perf_counter()
            filtered = rt.run_selective_closed_shape_owner_face_side_membership_pipeline_cupy(
                candidate_point_ids=column_map["point_id"],
                candidate_shape_ids=column_map["shape_id"],
                candidate_point_ordinals=column_map["point_ordinal"],
                candidate_shape_ordinals=column_map["shape_ordinal"],
                selected_point_ordinals=cp.asarray(selected_ordinals, dtype=cp.int64),
                topology_shape_ids=cp.asarray([int(poly.id) for poly in polygons], dtype=cp.int64),
                topology_shape_ordinals=cp.arange(len(polygons), dtype=cp.int64),
                topology_left_face_ids=cp.asarray([int(chain.left_face_id) for chain in polygon_chains], dtype=cp.int64),
                topology_right_face_ids=cp.asarray([int(chain.right_face_id) for chain in polygon_chains], dtype=cp.int64),
                owner_point_ids=cp.asarray([int(point.id) for point in points], dtype=cp.int64),
                owner_point_ordinals=cp.arange(len(points), dtype=cp.int64),
                owner_face_ids=cp.asarray(owner_face_ids, dtype=cp.int64),
                owner_side_codes=owner_side_codes,
                missing_owner_policy="drop",
            )
            cp.cuda.Stream.null.synchronize()
            filter_sec = time.perf_counter() - filter_start
            filtered_pairs = Counter(
                zip(
                    cp.asnumpy(filtered["point_id"]).astype(int).tolist(),
                    cp.asnumpy(filtered["shape_id"]).astype(int).tolist(),
                )
            )
            before_extra = sorted((candidate_pairs - exact_pairs).elements())
            before_missing = sorted((exact_pairs - candidate_pairs).elements())
            after_extra = sorted((filtered_pairs - exact_pairs).elements())
            after_missing = sorted((exact_pairs - filtered_pairs).elements())
            removed = sorted((candidate_pairs - filtered_pairs).elements())

            return {
                "schema": "rtdl.goal3673.rayjoin_full_county_selective_ordinal_owner_side_route_probe.v1",
                "commit": _commit(),
                "has_uncommitted_patch": _dirty(),
                "dataset": str(dataset_path.resolve()),
                "gpu": _gpu_name(),
                "device_predicate_eps": os.environ.get("RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS"),
                "point_count": len(points),
                "shape_count": len(polygons),
                "exact_row_count": len(exact_rows),
                "exact_sec": exact_sec,
                "candidate_native_row_count": int(columns.row_count),
                "candidate_counter_row_count": sum(candidate_pairs.values()),
                "candidate_traversal_seconds": float(columns.traversal_seconds),
                "candidate_call_sec": candidate_sec,
                "before_extra_count": len(before_extra),
                "before_missing_count": len(before_missing),
                "filtered_row_count": sum(filtered_pairs.values()),
                "filter_sec": filter_sec,
                "after_extra_count": len(after_extra),
                "after_missing_count": len(after_missing),
                "matches_exact_multiset": filtered_pairs == exact_pairs,
                "before_extra_sample": _json_pairs(before_extra),
                "removed_extra_rows": _json_pairs(removed),
                "extra_sample": _json_pairs(after_extra),
                "missing_sample": _json_pairs(after_missing),
                "selected_point_ids": [int(value) for value in selected_point_ids],
                "selected_point_ordinals": [int(value) for value in selected_ordinals],
                "selected_candidate_row_count": int(filtered["selected_candidate_row_count"]),
                "passthrough_candidate_row_count": int(filtered["passthrough_candidate_row_count"]),
                "selected_filter_key_mode": filtered["selected_filter_key_mode"],
                "owner_derivation_policy": (
                    "per_input_ordinal for selected ambiguity set: left_face_id if nonzero "
                    "else right_face_id if nonzero else drop/either"
                ),
                "native_engine_boundary": (
                    "RTDL/OptiX emits generic candidate id plus ordinal columns; caller supplies "
                    "selected ambiguity ordinals and owner face/side policy; CuPy continuation "
                    "filters only selected rows."
                ),
                "claim_boundary": {
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "rayjoin_paper_reproduction_claim_authorized": False,
                    "rtdl_beats_rayjoin_claim_authorized": False,
                    "rt_core_speedup_claim_authorized": False,
                    "true_zero_copy_claim_authorized": False,
                    "native_default_route_authorized": False,
                },
            }
        finally:
            columns.close()
    finally:
        prepared.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Goal3673 selective ordinal owner-side probe.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--selected-point-id", type=int, action="append", required=True)
    parser.add_argument("--max-rows", type=int, default=1_000_000)
    args = parser.parse_args()

    payload = run_probe(
        dataset_path=args.dataset,
        selected_point_ids=tuple(args.selected_point_id),
        output_path=args.output,
        max_rows=int(args.max_rows),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
