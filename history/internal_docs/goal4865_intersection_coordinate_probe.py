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
from rtdsl.rayjoin_overlay import _run_lsi_rows
from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--target-x", type=float, default=-144.125743)
    parser.add_argument("--target-y", type=float, default=64.796193)
    parser.add_argument("--tol", type=float, default=2.0e-6)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    start = time.time()
    left = load_cdb(args.left)
    right = load_cdb(args.right)
    left_inputs = _packed_overlay_inputs(left)
    right_inputs = _packed_overlay_inputs(right)
    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)
    rows, timings = _run_lsi_rows(
        "optix",
        left_inputs.segments,
        right_inputs.segments,
        left,
        right,
        left_coords=left_inputs.segment_coords,
        right_coords=right_inputs.segment_coords,
        scale_bounds=scale_bounds,
    )
    matches = []
    for index, row in enumerate(rows):
        x = float(row["intersection_point_x"])
        y = float(row["intersection_point_y"])
        if abs(x - float(args.target_x)) <= float(args.tol) and abs(y - float(args.target_y)) <= float(args.tol):
            matches.append(
                {
                    "row_index": int(index),
                    "left_id": int(row["left_id"]),
                    "right_id": int(row["right_id"]),
                    "x": x,
                    "y": y,
                    "formatted": f"{x:.6f} {y:.6f}",
                    "scaled_x": int(row["intersection_scaled_x"]),
                    "scaled_y": int(row["intersection_scaled_y"]),
                    "scaled_x_rational": str(row["intersection_scaled_x_rational"]),
                    "scaled_y_rational": str(row["intersection_scaled_y_rational"]),
                }
            )
            if len(matches) >= 20:
                break
    payload = {
        "schema": "rtdl.goal4865.intersection_coordinate_probe.v1",
        "target": {"x": float(args.target_x), "y": float(args.target_y), "tol": float(args.tol)},
        "scale_bounds": list(scale_bounds),
        "row_count": int(len(rows)),
        "match_count_returned": len(matches),
        "matches": matches,
        "timings": timings,
        "elapsed_sec": time.time() - start,
    }
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
