from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.datasets import load_cdb
from rtdsl.rayjoin_overlay import _packed_overlay_inputs
from rtdsl.rayjoin_overlay import _rows_from_segment_pairs
from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds
from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--left-id", type=int, default=172803)
    parser.add_argument("--right-id", type=int, default=23714604)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    start = time.time()
    left = load_cdb(args.left)
    right = load_cdb(args.right)
    left_inputs = _packed_overlay_inputs(left)
    right_inputs = _packed_overlay_inputs(right)
    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)

    with prepare_planar_map_lsi_2d_optix(left_inputs.segments) as prepared:
        rows = prepared.run_raw(right_inputs.segments)
        try:
            columns = rows.to_numpy_columns(copy=True)
        finally:
            rows.close()

    # Public LSI rows are (query/right, base/left). Overlay rows are (left, right).
    query_ids = columns["left_id"]
    base_ids = columns["right_id"]
    matches = []
    for index, (query_id, base_id) in enumerate(zip(query_ids, base_ids)):
        if int(base_id) == int(args.left_id) and int(query_id) == int(args.right_id):
            pairs = [[int(base_id), int(query_id)]]
            projected = _rows_from_segment_pairs(
                pairs,
                left,
                right,
                left_coords=left_inputs.segment_coords,
                right_coords=right_inputs.segment_coords,
                scale_bounds=scale_bounds,
            )
            row = projected[0]
            li = int(base_id) - 1
            ri = int(query_id) - 1
            matches.append(
                {
                    "public_row_index": int(index),
                    "public_row": {
                        "left_id_query": int(query_id),
                        "right_id_base": int(base_id),
                        "intersection_point_x": float(columns["intersection_point_x"][index]),
                        "intersection_point_y": float(columns["intersection_point_y"][index]),
                    },
                    "left_segment_from_full_arrays": [float(a[li]) for a in left_inputs.segment_coords],
                    "right_segment_from_full_arrays": [float(a[ri]) for a in right_inputs.segment_coords],
                    "reprojected_row": {name: str(row[name]) for name in projected.dtype.names},
                    "reprojected_formatted": (
                        f"{float(row['intersection_point_x']):.6f} "
                        f"{float(row['intersection_point_y']):.6f}"
                    ),
                }
            )
            break

    payload = {
        "schema": "rtdl.goal4865.pair_id_endpoint_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
        "target_pair_overlay_order": {"left_id": int(args.left_id), "right_id": int(args.right_id)},
        "row_count": int(len(query_ids)),
        "match_count": int(len(matches)),
        "matches": matches,
        "scale_bounds": list(scale_bounds),
        "elapsed_sec": time.time() - start,
    }
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
