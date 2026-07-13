from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--base-ids", nargs="+", type=int, default=[328, 329])
    args = parser.parse_args()

    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs
    from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix

    left_inputs = load_cdb_overlay_packed_inputs(args.left)
    right_inputs = load_cdb_overlay_packed_inputs(args.right)

    prepared = prepare_planar_map_lsi_2d_optix(left_inputs.segments)
    rows = None
    try:
        rows = prepared.run_raw(right_inputs.segments)
        columns = rows.to_numpy_columns(copy=True)
    finally:
        if rows is not None:
            rows.close()
        prepared.close()

    base_ids = set(args.base_ids)
    matches = []
    for i, (query_id, base_id) in enumerate(zip(columns["left_id"], columns["right_id"])):
        if int(base_id) in base_ids:
            matches.append(
                {
                    "row_index": int(i),
                    "query_id_map1": int(query_id),
                    "base_id_map0": int(base_id),
                    "x": float(columns["intersection_point_x"][i]),
                    "y": float(columns["intersection_point_y"][i]),
                    "formatted": f"{float(columns['intersection_point_x'][i]):.6f} {float(columns['intersection_point_y'][i]):.6f}",
                }
            )

    summary = {
        "schema": "rtdl.goal4865.native_lsi_row_probe.v1",
        "row_count": int(len(columns["left_id"])),
        "base_ids": sorted(base_ids),
        "match_count": len(matches),
        "matches": matches,
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("schema", "row_count", "match_count")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
