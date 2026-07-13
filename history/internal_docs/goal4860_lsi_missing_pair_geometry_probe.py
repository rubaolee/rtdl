from __future__ import annotations

import argparse
import json
from math import hypot
from pathlib import Path

from rtdsl.datasets import chains_to_planar_map_segments
from rtdsl.datasets import load_cdb


def _params(left, right):
    px, py, x1, y1 = left["x0"], left["y0"], left["x1"], left["y1"]
    qx, qy, x2, y2 = right["x0"], right["y0"], right["x1"], right["y1"]
    rx, ry = x1 - px, y1 - py
    sx, sy = x2 - qx, y2 - qy
    denom = rx * sy - ry * sx
    scale = hypot(rx, ry) * hypot(sx, sy)
    out = {"denom": denom, "scale": scale}
    if denom != 0.0:
        qpx, qpy = qx - px, qy - py
        t = (qpx * sy - qpy * sx) / denom
        u = (qpx * ry - qpy * rx) / denom
        out.update(
            {
                "t": t,
                "u": u,
                "t_below_zero": min(t, 0.0),
                "u_below_zero": min(u, 0.0),
                "t_above_one": max(t - 1.0, 0.0),
                "u_above_one": max(u - 1.0, 0.0),
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--diff", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    diff = json.loads(Path(args.diff).read_text(encoding="utf-8"))
    missing = [tuple(pair) for pair in diff["missing_from_rows_first"][: args.limit]]
    base_segments = {int(seg["id"]): seg for seg in chains_to_planar_map_segments(load_cdb(args.base))}
    query_segments = {int(seg["id"]): seg for seg in chains_to_planar_map_segments(load_cdb(args.query))}

    samples = []
    for left_id, right_id in missing:
        left = query_segments[left_id]
        right = base_segments[right_id]
        samples.append(
            {
                "left_id": left_id,
                "right_id": right_id,
                "left": left,
                "right": right,
                "params": _params(left, right),
            }
        )

    summary = {
        "schema": "rtdl.goal4860.planar_map_lsi_missing_pair_geometry_probe.v1",
        "base": args.base,
        "query": args.query,
        "source_diff": args.diff,
        "sample_count": len(samples),
        "samples": samples,
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
