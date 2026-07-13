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
    parser.add_argument("--top-n", type=int, default=32)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    import numpy as np
    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs

    left_inputs = load_cdb_overlay_packed_inputs(args.left)
    right_inputs = load_cdb_overlay_packed_inputs(args.right)
    px = float(np.asarray(left_inputs.point_coords[0])[args.target_point_index])
    py = float(np.asarray(left_inputs.point_coords[1])[args.target_point_index])
    segments = right_inputs.cdb_segments.owner[1]

    top: list[tuple[float, int]] = []
    chunk_size = 2_000_000
    for start in range(0, len(segments), chunk_size):
        end = min(start + chunk_size, len(segments))
        chunk = segments[start:end]
        x0 = chunk["x0"].astype(np.float64, copy=False)
        y0 = chunk["y0"].astype(np.float64, copy=False)
        x1 = chunk["x1"].astype(np.float64, copy=False)
        y1 = chunk["y1"].astype(np.float64, copy=False)
        xmin = np.minimum(x0, x1)
        xmax = np.maximum(x0, x1)
        excluded_x = xmin if args.query_map_id == 0 else xmax
        dx = x1 - x0
        mask = (dx != 0.0) & (px >= xmin) & (px <= xmax) & (px != excluded_x)
        if not np.any(mask):
            continue
        idx = np.nonzero(mask)[0]
        u = (px - x0[idx]) / dx[idx]
        hit_y = y0[idx] + u * (y1[idx] - y0[idx])
        valid = hit_y >= py
        if not np.any(valid):
            continue
        idx = idx[valid]
        hit_y = hit_y[valid]
        count = min(args.top_n, hit_y.size)
        local_order = np.argpartition(hit_y, count - 1)[:count]
        for local in local_order.tolist():
            top.append((float(hit_y[local]), int(start + idx[local])))
        top = sorted(top, key=lambda item: (item[0], item[1]))[: args.top_n]

    records = []
    for hit_y, edge_index in top:
        seg = segments[edge_index]
        forward = float(seg["x0"]) < float(seg["x1"])
        face = int(seg["right_face_id"]) if forward else int(seg["left_face_id"])
        records.append(
            {
                "edge_index": int(edge_index),
                "segment_id": int(seg["id"]),
                "hit_y": hit_y,
                "dy": hit_y - py,
                "face_by_direction_world": face,
                "left_face_id": int(seg["left_face_id"]),
                "right_face_id": int(seg["right_face_id"]),
                "forward_x_world": bool(forward),
                "x0": float(seg["x0"]),
                "y0": float(seg["y0"]),
                "x1": float(seg["x1"]),
                "y1": float(seg["y1"]),
            }
        )
    payload = {
        "schema": "rtdl.goal4867.fast_candidate_rank.v1",
        "left": args.left,
        "right": args.right,
        "target_point_index": int(args.target_point_index),
        "query_map_id": int(args.query_map_id),
        "point": [px, py],
        "records": records,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
