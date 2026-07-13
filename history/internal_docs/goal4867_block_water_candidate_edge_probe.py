from __future__ import annotations

import argparse
import json
from pathlib import Path


def _line_from_scaled_endpoints(sx0: int, sy0: int, sx1: int, sy1: int) -> tuple[int, int, int]:
    a = int(sy0) - int(sy1)
    b = int(sx1) - int(sx0)
    c = -(int(sx0) * a) - (int(sy0) * b)
    if b < 0:
        a, b, c = -a, -b, -c
    return a, b, c


def _candidate_metrics(
    *,
    edge_sx0: int,
    edge_sy0: int,
    edge_sx1: int,
    edge_sy1: int,
    sx: int,
    sy: int,
    query_map_id: int,
    scale_rry: float,
) -> dict[str, object]:
    a, b, c = _line_from_scaled_endpoints(edge_sx0, edge_sy0, edge_sx1, edge_sy1)
    x_min = min(edge_sx0, edge_sx1)
    x_max = max(edge_sx0, edge_sx1)
    excluded_x = x_min if query_map_id == 0 else x_max
    in_x = x_min <= sx <= x_max and sx != excluded_x
    if b == 0 or not in_x:
        return {
            "candidate": False,
            "reason": "vertical_or_outside_x",
            "a": a,
            "b": b,
            "c": c,
            "x_min": x_min,
            "x_max": x_max,
            "excluded_x": excluded_x,
        }
    numerator = -(a * sx) - c
    xsect_y = numerator / b
    diff_y = sy - xsect_y
    if diff_y == 0:
        diff_y = -a if query_map_id == 0 else a
    if diff_y == 0:
        diff_y = -b if query_map_id == 0 else b
    return {
        "candidate": diff_y <= 0,
        "a": a,
        "b": b,
        "c": c,
        "x_min": x_min,
        "x_max": x_max,
        "excluded_x": excluded_x,
        "xsect_y": xsect_y,
        "xsect_y_num": int(numerator),
        "xsect_y_den": int(b),
        "diff_y": diff_y,
        "slope": a / b,
        "report_t": max(0.0, (xsect_y - sy) * scale_rry),
        "face_direction": "right" if edge_sx0 < edge_sx1 else "left",
    }


def _record(
    seg,
    edge_index: int,
    *,
    sx: int,
    sy: int,
    query_map_id: int,
    scale_rry: float,
    scale_x,
    scale_y,
) -> dict[str, object]:
    sx0 = int(scale_x([float(seg["x0"])])[0])
    sy0 = int(scale_y([float(seg["y0"])])[0])
    sx1 = int(scale_x([float(seg["x1"])])[0])
    sy1 = int(scale_y([float(seg["y1"])])[0])
    return {
        "edge_index_0_based": int(edge_index),
        "segment_id": int(seg["id"]),
        "x0": float(seg["x0"]),
        "y0": float(seg["y0"]),
        "x1": float(seg["x1"]),
        "y1": float(seg["y1"]),
        "sx0": sx0,
        "sy0": sy0,
        "sx1": sx1,
        "sy1": sy1,
        "left_face_id": int(seg["left_face_id"]),
        "right_face_id": int(seg["right_face_id"]),
        "face_by_direction": int(seg["right_face_id"]) if sx0 < sx1 else int(seg["left_face_id"]),
        "metrics": _candidate_metrics(
            edge_sx0=sx0,
            edge_sy0=sy0,
            edge_sx1=sx1,
            edge_sy1=sy1,
            sx=sx,
            sy=sy,
            query_map_id=query_map_id,
            scale_rry=scale_rry,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--target-point-index", type=int, required=True)
    parser.add_argument("--edge-index", type=int, action="append", required=True)
    parser.add_argument("--query-map-id", type=int, default=0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    import numpy as np
    from rtdsl.rayjoin_overlay import _rayjoin_author_scale_array
    from rtdsl.rayjoin_overlay import _rayjoin_scaling_constants
    from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds
    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs

    left_inputs = load_cdb_overlay_packed_inputs(args.left)
    right_inputs = load_cdb_overlay_packed_inputs(args.right)
    x = float(np.asarray(left_inputs.point_coords[0])[args.target_point_index])
    y = float(np.asarray(left_inputs.point_coords[1])[args.target_point_index])
    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)
    rx_scale, ry_scale, deltax, deltay, _rrx, rry, _ddeltax, _ddeltay = _rayjoin_scaling_constants(scale_bounds)
    sx = int(_rayjoin_author_scale_array([x], rx_scale, deltax)[0])
    sy = int(_rayjoin_author_scale_array([y], ry_scale, deltay)[0])

    cdb_array = right_inputs.cdb_segments.owner[1]
    scale_x = lambda values: _rayjoin_author_scale_array(values, rx_scale, deltax)
    scale_y = lambda values: _rayjoin_author_scale_array(values, ry_scale, deltay)
    records = [
        _record(
            cdb_array[int(edge_index)],
            int(edge_index),
            sx=sx,
            sy=sy,
            query_map_id=args.query_map_id,
            scale_rry=float(rry),
            scale_x=scale_x,
            scale_y=scale_y,
        )
        for edge_index in args.edge_index
    ]
    payload = {
        "schema": "rtdl.goal4867.block_water.candidate_edge_probe.v1",
        "target_point_index": int(args.target_point_index),
        "point_world": [x, y],
        "point_scaled": [sx, sy],
        "query_map_id": int(args.query_map_id),
        "records": records,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
