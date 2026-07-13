from __future__ import annotations

import argparse
import json
from pathlib import Path


def _parse_edges(raw: str) -> list[int]:
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--edges", required=True)
    parser.add_argument("--query-map-id", type=int, default=0)
    parser.add_argument("--target-point-index", type=int)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    import numpy as np
    from rtdsl.rayjoin_overlay import _rayjoin_author_scale_array
    from rtdsl.rayjoin_overlay import _rayjoin_scaling_constants
    from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds
    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs

    left_inputs = load_cdb_overlay_packed_inputs(args.left)
    right_inputs = load_cdb_overlay_packed_inputs(args.right)
    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)
    rx_scale, ry_scale, deltax, deltay, *_ = _rayjoin_scaling_constants(scale_bounds)

    point_payload = None
    if args.target_point_index is not None:
        px = float(np.asarray(left_inputs.point_coords[0])[args.target_point_index])
        py = float(np.asarray(left_inputs.point_coords[1])[args.target_point_index])
        psx = int(_rayjoin_author_scale_array([px], rx_scale, deltax)[0])
        psy = int(_rayjoin_author_scale_array([py], ry_scale, deltay)[0])
        point_payload = {
            "point_index": int(args.target_point_index),
            "point": [px, py],
            "scaled": [psx, psy],
        }

    segments = right_inputs.cdb_segments.owner[1]
    rows: list[dict[str, object]] = []
    for edge_index in _parse_edges(args.edges):
        segment = segments[edge_index]
        sx0 = int(_rayjoin_author_scale_array([float(segment["x0"])], rx_scale, deltax)[0])
        sy0 = int(_rayjoin_author_scale_array([float(segment["y0"])], ry_scale, deltay)[0])
        sx1 = int(_rayjoin_author_scale_array([float(segment["x1"])], rx_scale, deltax)[0])
        sy1 = int(_rayjoin_author_scale_array([float(segment["y1"])], ry_scale, deltay)[0])
        a = sy0 - sy1
        b = sx1 - sx0
        c = -(sx0 * a) - (sy0 * b)
        if b < 0:
            a, b, c = -a, -b, -c
        forward = sx0 < sx1
        face = int(segment["right_face_id"]) if forward else int(segment["left_face_id"])
        rows.append(
            {
                "edge_index": int(edge_index),
                "segment_id": int(segment["id"]),
                "left_face_id": int(segment["left_face_id"]),
                "right_face_id": int(segment["right_face_id"]),
                "face_by_direction": face,
                "forward_x": bool(forward),
                "a": int(a),
                "b": int(b),
                "c": int(c),
                "slope": (float(a) / float(b)) if b else None,
                "scaled_x0": sx0,
                "scaled_y0": sy0,
                "scaled_x1": sx1,
                "scaled_y1": sy1,
                "x0": float(segment["x0"]),
                "y0": float(segment["y0"]),
                "x1": float(segment["x1"]),
                "y1": float(segment["y1"]),
            }
        )

    payload = {
        "schema": "rtdl.goal4867.edge_metadata_dump.v1",
        "left": args.left,
        "right": args.right,
        "query_map_id": int(args.query_map_id),
        "point": point_payload,
        "rows": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
