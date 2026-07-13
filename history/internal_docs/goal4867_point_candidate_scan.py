from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--target-point-index", type=int, required=True)
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
    rx_scale, ry_scale, deltax, deltay, _rrx, rry, _ddeltax, _ddeltay = (
        _rayjoin_scaling_constants(scale_bounds)
    )
    sx = int(_rayjoin_author_scale_array([x], rx_scale, deltax)[0])
    sy = int(_rayjoin_author_scale_array([y], ry_scale, deltay)[0])
    segments = right_inputs.cdb_segments.owner[1]

    best_num: int | None = None
    best_den: int | None = None
    records: list[dict[str, object]] = []
    chunk_size = 2_000_000
    for start in range(0, len(segments), chunk_size):
        end = min(start + chunk_size, len(segments))
        chunk = segments[start:end]
        sx0 = _rayjoin_author_scale_array(
            chunk["x0"].astype(np.float64, copy=False), rx_scale, deltax
        ).astype(np.int64)
        sy0 = _rayjoin_author_scale_array(
            chunk["y0"].astype(np.float64, copy=False), ry_scale, deltay
        ).astype(np.int64)
        sx1 = _rayjoin_author_scale_array(
            chunk["x1"].astype(np.float64, copy=False), rx_scale, deltax
        ).astype(np.int64)
        sy1 = _rayjoin_author_scale_array(
            chunk["y1"].astype(np.float64, copy=False), ry_scale, deltay
        ).astype(np.int64)
        xmin = np.minimum(sx0, sx1)
        xmax = np.maximum(sx0, sx1)
        excluded_x = xmin if args.query_map_id == 0 else xmax
        mask = (sx >= xmin) & (sx <= xmax) & (sx != excluded_x) & (sx1 != sx0)
        for local_index in np.nonzero(mask)[0].tolist():
            a = int(sy0[local_index]) - int(sy1[local_index])
            b = int(sx1[local_index]) - int(sx0[local_index])
            c = -(int(sx0[local_index]) * a) - (int(sy0[local_index]) * b)
            if b < 0:
                a, b, c = -a, -b, -c
            if b == 0:
                continue
            numerator = -(a * sx) - c
            diff_numerator = sy * b - numerator
            if diff_numerator == 0:
                diff_numerator = -a if args.query_map_id == 0 else a
                if diff_numerator == 0:
                    diff_numerator = -b if args.query_map_id == 0 else b
            if diff_numerator > 0:
                continue
            if best_num is None or numerator * best_den < best_num * b:  # type: ignore[operator]
                best_num = numerator
                best_den = b
                records = []
            if best_num is not None and numerator * best_den == best_num * b:
                edge_index = start + local_index
                segment = chunk[local_index]
                forward = int(sx0[local_index]) < int(sx1[local_index])
                face = int(segment["right_face_id"]) if forward else int(segment["left_face_id"])
                records.append(
                    {
                        "edge_index": int(edge_index),
                        "segment_id": int(segment["id"]),
                        "left_face_id": int(segment["left_face_id"]),
                        "right_face_id": int(segment["right_face_id"]),
                        "face_by_direction": face,
                        "forward_x": bool(forward),
                        "slope": a / b,
                        "a": int(a),
                        "b": int(b),
                        "x0": float(segment["x0"]),
                        "y0": float(segment["y0"]),
                        "x1": float(segment["x1"]),
                        "y1": float(segment["y1"]),
                    }
                )

    records_sorted = sorted(records, key=lambda row: (row["slope"], row["edge_index"]))
    payload = {
        "schema": "rtdl.goal4867.point_candidate_scan.v1",
        "left": args.left,
        "right": args.right,
        "target_point_index": args.target_point_index,
        "query_map_id": args.query_map_id,
        "point": [x, y],
        "scaled_point": [sx, sy],
        "best_xsect_y_num": best_num,
        "best_xsect_y_den": best_den,
        "tie_count": len(records_sorted),
        "records": records_sorted,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
