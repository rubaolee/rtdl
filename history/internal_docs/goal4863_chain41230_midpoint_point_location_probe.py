from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.datasets import load_cdb
from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points
from rtdsl.rayjoin_overlay import _intersections_from_lsi_rows
from rtdsl.rayjoin_overlay import _packed_overlay_inputs
from rtdsl.rayjoin_overlay import _prepared_point_location_pair
from rtdsl.rayjoin_overlay import _rayjoin_author_rational_to_internal
from rtdsl.rayjoin_overlay import _rayjoin_cdb_point_location_env
from rtdsl.rayjoin_overlay import _rayjoin_scaling_constants
from rtdsl.rayjoin_overlay import _rayjoin_trunc_div2
from rtdsl.rayjoin_overlay import _run_lsi_rows
from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds
from rtdsl.rayjoin_overlay import _sort_xsects_for_map


def _scaled_to_float(sx: int, sy: int, scale_bounds):
    *_, rrx, rry, ddeltax, ddeltay = _rayjoin_scaling_constants(scale_bounds)
    return sx * rrx + ddeltax, sy * rry + ddeltay


def _query_face(locator, sx: int, sy: int, scale_bounds, query_map_id: int) -> dict[str, object]:
    x, y = _scaled_to_float(sx, sy, scale_bounds)
    points = pack_rayjoin_cdb_scaled_points(ids=[1], x=[x], y=[y], sx=[sx], sy=[sy])
    with _rayjoin_cdb_point_location_env(query_map_id, scale_bounds):
        faces, timings = locator.faces(points, 1)
    return {
        "sx": int(sx),
        "sy": int(sy),
        "x": float(x),
        "y": float(y),
        "face_id": int(faces[0]),
        "timings": timings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--edge-id", type=int, default=43212)
    parser.add_argument("--right-eid-a", type=int, default=8522815)
    parser.add_argument("--right-eid-b", type=int, default=8522816)
    parser.add_argument("--expected-face", type=int, default=10950)
    args = parser.parse_args()

    start = time.time()
    left = load_cdb(args.left)
    right = load_cdb(args.right)
    left_inputs = _packed_overlay_inputs(left)
    right_inputs = _packed_overlay_inputs(right)
    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)

    lsi_rows, lsi_timings = _run_lsi_rows(
        "optix",
        left_inputs.segments,
        right_inputs.segments,
        left,
        right,
        left_coords=left_inputs.segment_coords,
        right_coords=right_inputs.segment_coords,
        scale_bounds=scale_bounds,
    )
    xsects = _intersections_from_lsi_rows(lsi_rows)
    xsects_sorted_map0 = _sort_xsects_for_map(
        xsects,
        left_inputs.edge_starts,
        0,
        scale_bounds=scale_bounds,
    )
    edge_xsects = [x for x in xsects_sorted_map0 if int(x.eid0) == int(args.edge_id)]
    target_pair = None
    for left_xsect, right_xsect in zip(edge_xsects, edge_xsects[1:]):
        if {int(left_xsect.eid1), int(right_xsect.eid1)} == {int(args.right_eid_a), int(args.right_eid_b)}:
            target_pair = (left_xsect, right_xsect)
            break
    if target_pair is None:
        raise RuntimeError("target adjacent xsect pair not found")

    a, b = target_pair
    rational_sx = _rayjoin_author_rational_to_internal((a.scaled_x_rational + b.scaled_x_rational) / 2)
    rational_sy = _rayjoin_author_rational_to_internal((a.scaled_y_rational + b.scaled_y_rational) / 2)
    trunc_sx = _rayjoin_trunc_div2(int(a.scaled_x) + int(b.scaled_x))
    trunc_sy = _rayjoin_trunc_div2(int(a.scaled_y) + int(b.scaled_y))

    variants: dict[str, tuple[int, int]] = {
        "rational_midpoint_current": (rational_sx, rational_sy),
        "trunc_scaled_endpoint_midpoint": (trunc_sx, trunc_sy),
    }
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            variants[f"rational_plus_{dx}_{dy}"] = (rational_sx + dx, rational_sy + dy)

    right_cdb_segments = right_inputs.cdb_segments
    left_cdb_segments = left_inputs.cdb_segments
    queried: dict[str, object] = {}
    with _prepared_point_location_pair(
        "optix",
        right_cdb_segments,
        left_cdb_segments,
        scale_bounds,
        point_counts=(1, 1),
    ) as (map0_in_map1, _map1_in_map0, prepare_wall):
        for name, (sx, sy) in variants.items():
            queried[name] = _query_face(map0_in_map1, int(sx), int(sy), scale_bounds, query_map_id=0)

    payload = {
        "schema": "rtdl.goal4863.chain41230_midpoint_point_location_probe.v1",
        "left": args.left,
        "right": args.right,
        "edge_id": int(args.edge_id),
        "right_eids": [int(args.right_eid_a), int(args.right_eid_b)],
        "expected_face_from_author_output": int(args.expected_face),
        "scale_bounds": list(scale_bounds),
        "lsi_timings": lsi_timings,
        "prepare_wall_sec": float(prepare_wall),
        "elapsed_sec": time.time() - start,
        "target_xsects": [
            {
                "eid0": int(x.eid0),
                "eid1": int(x.eid1),
                "x": float(x.x),
                "y": float(x.y),
                "scaled_x": None if x.scaled_x is None else int(x.scaled_x),
                "scaled_y": None if x.scaled_y is None else int(x.scaled_y),
                "scaled_x_rational": str(x.scaled_x_rational),
                "scaled_y_rational": str(x.scaled_y_rational),
            }
            for x in target_pair
        ],
        "variants": queried,
        "matching_variants": [
            name for name, result in queried.items() if int(result["face_id"]) == int(args.expected_face)
        ],
    }
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
