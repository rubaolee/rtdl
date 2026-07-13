from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def _row_dicts(row_view):
    rows = row_view.to_dict_rows()
    row_view.close()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--target-point-index", type=int, required=True)
    parser.add_argument("--query-map-id", type=int, default=0)
    args = parser.parse_args()

    import numpy as np
    from rtdsl.embree_runtime import pack_points
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

    x = float(np.asarray(left_inputs.point_coords[0])[args.target_point_index])
    y = float(np.asarray(left_inputs.point_coords[1])[args.target_point_index])
    point_id = int(args.target_point_index) + 1

    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)
    rx_scale, ry_scale, deltax, deltay, *_ = _rayjoin_scaling_constants(scale_bounds)
    sx = int(_rayjoin_author_scale_array([x], rx_scale, deltax)[0])
    sy = int(_rayjoin_author_scale_array([y], ry_scale, deltay)[0])

    ordinary_points = pack_points(ids=[point_id], x=[x], y=[y], dimension=2)
    scaled_points = pack_rayjoin_cdb_scaled_points(
        ids=[point_id],
        x=[x],
        y=[y],
        sx=[sx],
        sy=[sy],
    )

    prepare_start = time.perf_counter()
    with _rayjoin_cdb_point_location_env(args.query_map_id, scale_bounds):
        prepared = prepare_directed_segment_point_location_2d_optix(right_inputs.cdb_segments)
    prepare_sec = time.perf_counter() - prepare_start

    try:
        with _rayjoin_cdb_point_location_env(args.query_map_id, scale_bounds):
            ordinary_rows = _row_dicts(prepared.run_raw(ordinary_points))
            scaled_rows = _row_dicts(prepared.run_raw(scaled_points))
    finally:
        prepared.close()

    payload = {
        "schema": "rtdl.goal4867.block_water.single_point_pip_probe.v1",
        "left": args.left,
        "right": args.right,
        "target_point_index": int(args.target_point_index),
        "point_id": point_id,
        "query_map_id": int(args.query_map_id),
        "point_world": [x, y],
        "point_scaled": [sx, sy],
        "scale_bounds": list(scale_bounds),
        "load_cached_inputs_sec": load_sec,
        "prepare_sec": prepare_sec,
        "ordinary_point_rows": ordinary_rows,
        "scaled_point_rows": scaled_rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
