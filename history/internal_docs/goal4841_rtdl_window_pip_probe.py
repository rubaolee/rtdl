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
from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    query = load_cdb(args.query)
    base = load_cdb(args.base)
    query_inputs = _packed_overlay_inputs(query)
    base_inputs = _packed_overlay_inputs(base)
    scale_bounds = _shared_rayjoin_bounds(query_inputs, base_inputs)
    with _prepared_point_location_pair(
        "optix",
        base_inputs.cdb_segments,
        query_inputs.cdb_segments,
        scale_bounds,
        point_counts=(int(query_inputs.points.count), int(base_inputs.points.count)),
    ) as (query_in_base, _base_in_query, _prepare_wall):
        with _rayjoin_cdb_point_location_env(0, scale_bounds):
            rows = query_in_base.prepared.run_raw(query_inputs.points)
            cols = rows.to_numpy_columns(copy=True)
    points = []
    point_index = 0
    for chain in query.chains:
        for point in chain.points:
            points.append(
                {
                    "point_idx": point_index,
                    "x": float(point.x),
                    "y": float(point.y),
                    "face_id": int(cols["face_id"][point_index]),
                    "segment_id": int(cols["segment_id"][point_index]),
                    "hit_t": float(cols["hit_t"][point_index]),
                }
            )
            point_index += 1
    summary = {
        "query": args.query,
        "base": args.base,
        "scale_bounds": scale_bounds,
        "points": points,
    }
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
