from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.datasets import load_cdb
from rtdsl.rayjoin_overlay import _packed_overlay_inputs
from rtdsl.rayjoin_overlay import _prepared_point_location_pair
from rtdsl.rayjoin_overlay import _rayjoin_cdb_point_location_env
from rtdsl.rayjoin_overlay import _rayjoin_scaling_constants
from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds
from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--sx", type=int, required=True)
    parser.add_argument("--sy", type=int, required=True)
    parser.add_argument("--query-map-id", type=int, default=0)
    parser.add_argument("--scale-bounds", nargs=4, type=float)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    base = load_cdb(args.base)
    base_inputs = _packed_overlay_inputs(base)
    if args.scale_bounds is not None:
        scale_bounds = tuple(float(value) for value in args.scale_bounds)
    else:
        # The query point is inside the base-map bounds; use base twice only to recover
        # scaling constants from bbox anchors in compact windows.
        scale_bounds = _shared_rayjoin_bounds(base_inputs, base_inputs)
    *_, rrx, rry, ddeltax, ddeltay = _rayjoin_scaling_constants(scale_bounds)
    x = int(args.sx) * rrx + ddeltax
    y = int(args.sy) * rry + ddeltay
    query_points = pack_rayjoin_cdb_scaled_points(
        ids=[1],
        x=[x],
        y=[y],
        sx=[int(args.sx)],
        sy=[int(args.sy)],
    )
    with _prepared_point_location_pair(
        "optix",
        base_inputs.cdb_segments,
        base_inputs.cdb_segments,
        scale_bounds,
        point_counts=(1, int(base_inputs.points.count)),
    ) as (query_in_base, _unused, prepare_wall):
        with _rayjoin_cdb_point_location_env(int(args.query_map_id), scale_bounds):
            rows = query_in_base.prepared.run_raw(query_points)
            cols = rows.to_numpy_columns(copy=True)
    payload = {
        "base": args.base,
        "scale_bounds": scale_bounds,
        "query": {"sx": int(args.sx), "sy": int(args.sy), "x": x, "y": y},
        "prepare_wall_sec": float(prepare_wall),
        "face_id": int(cols["face_id"][0]),
        "segment_id": int(cols["segment_id"][0]),
        "hit_t": float(cols["hit_t"][0]),
    }
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
