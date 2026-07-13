from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def _rows(row_view):
    rows = row_view.to_dict_rows()
    row_view.close()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--start-point-index", type=int, required=True)
    parser.add_argument("--end-point-index", type=int, required=True)
    parser.add_argument("--query-map-id", type=int, default=0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    import numpy as np
    from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points
    from rtdsl.optix_runtime import prepare_directed_segment_point_location_2d_optix
    from rtdsl.rayjoin_overlay import _rayjoin_author_scale_array
    from rtdsl.rayjoin_overlay import _rayjoin_cdb_point_location_env
    from rtdsl.rayjoin_overlay import _rayjoin_scaling_constants
    from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds
    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs

    load_start = time.perf_counter()
    left_inputs = load_cdb_overlay_packed_inputs(args.left)
    right_inputs = load_cdb_overlay_packed_inputs(args.right)
    load_sec = time.perf_counter() - load_start
    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)
    rx_scale, ry_scale, deltax, deltay, *_ = _rayjoin_scaling_constants(scale_bounds)

    indices = list(range(args.start_point_index, args.end_point_index + 1))
    xs = np.asarray(left_inputs.point_coords[0])[indices].astype(np.float64, copy=False)
    ys = np.asarray(left_inputs.point_coords[1])[indices].astype(np.float64, copy=False)
    sx = _rayjoin_author_scale_array(xs, rx_scale, deltax).astype(np.int64)
    sy = _rayjoin_author_scale_array(ys, ry_scale, deltay).astype(np.int64)
    points = pack_rayjoin_cdb_scaled_points(
        ids=[index + 1 for index in indices],
        x=xs,
        y=ys,
        sx=sx,
        sy=sy,
    )

    prepare_start = time.perf_counter()
    with _rayjoin_cdb_point_location_env(args.query_map_id, scale_bounds):
        prepared = prepare_directed_segment_point_location_2d_optix(right_inputs.cdb_segments)
    prepare_sec = time.perf_counter() - prepare_start
    try:
        with _rayjoin_cdb_point_location_env(args.query_map_id, scale_bounds):
            result_rows = _rows(prepared.run_raw(points))
    finally:
        prepared.close()

    by_point_id = {int(row["point_id"]): row for row in result_rows}
    records = []
    for local, point_index in enumerate(indices):
        point_id = point_index + 1
        row = by_point_id[point_id]
        records.append(
            {
                "point_index": point_index,
                "point_id": point_id,
                "point": [float(xs[local]), float(ys[local])],
                "point_text": f"{float(xs[local]):.6f} {float(ys[local]):.6f}",
                "scaled": [int(sx[local]), int(sy[local])],
                "face_id": int(row["face_id"]),
                "segment_id": int(row["segment_id"]),
                "hit_t": float(row["hit_t"]),
            }
        )

    payload = {
        "schema": "rtdl.goal4867.point_window_pip_probe.v1",
        "left": args.left,
        "right": args.right,
        "query_map_id": args.query_map_id,
        "load_cached_inputs_sec": load_sec,
        "prepare_sec": prepare_sec,
        "records": records,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
