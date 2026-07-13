from __future__ import annotations

import argparse
import json
from pathlib import Path


def _rows(row_view):
    rows = row_view.to_dict_rows()
    row_view.close()
    return rows


def _canonical_duplicate_segment_id(case: dict[str, list[float] | list[int]]) -> int:
    # Candidate Goal4868 contract: exact duplicate half-edges share an unordered
    # endpoint key and normalize to the smallest stable source segment id.
    return int(min(case["ids"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    import numpy as np
    from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points
    from rtdsl.embree_runtime import pack_rayjoin_cdb_segments
    from rtdsl.optix_runtime import prepare_rayjoin_cdb_point_location_2d_optix
    from rtdsl.rayjoin_overlay import _rayjoin_author_scale_array
    from rtdsl.rayjoin_overlay import _rayjoin_cdb_point_location_env
    from rtdsl.rayjoin_overlay import _rayjoin_scaling_constants

    bounds = (0.0, 10.0, 0.0, 10.0)
    rx_scale, ry_scale, deltax, deltay, *_ = _rayjoin_scaling_constants(bounds)
    px = np.asarray([5.0], dtype=np.float64)
    py = np.asarray([1.0], dtype=np.float64)
    sx = _rayjoin_author_scale_array(px, rx_scale, deltax).astype(np.int64)
    sy = _rayjoin_author_scale_array(py, ry_scale, deltay).astype(np.int64)
    points = pack_rayjoin_cdb_scaled_points(ids=[1], x=px, y=py, sx=sx, sy=sy)

    cases = [
        {
            "name": "forward_then_reverse",
            "ids": [100, 200],
            "x0": [0.0, 10.0],
            "y0": [5.0, 5.0],
            "x1": [10.0, 0.0],
            "y1": [5.0, 5.0],
            "left_face_ids": [11, 22],
            "right_face_ids": [0, 0],
        },
        {
            "name": "reverse_then_forward",
            "ids": [200, 100],
            "x0": [10.0, 0.0],
            "y0": [5.0, 5.0],
            "x1": [0.0, 10.0],
            "y1": [5.0, 5.0],
            "left_face_ids": [22, 11],
            "right_face_ids": [0, 0],
        },
    ]

    records = []
    for case in cases:
        segments = pack_rayjoin_cdb_segments(
            ids=np.asarray(case["ids"], dtype=np.int64),
            x0=np.asarray(case["x0"], dtype=np.float64),
            y0=np.asarray(case["y0"], dtype=np.float64),
            x1=np.asarray(case["x1"], dtype=np.float64),
            y1=np.asarray(case["y1"], dtype=np.float64),
            left_face_ids=np.asarray(case["left_face_ids"], dtype=np.uint32),
            right_face_ids=np.asarray(case["right_face_ids"], dtype=np.uint32),
        )
        with _rayjoin_cdb_point_location_env(0, bounds):
            prepared = prepare_rayjoin_cdb_point_location_2d_optix(segments)
        try:
            with _rayjoin_cdb_point_location_env(0, bounds):
                result = _rows(prepared.run_raw(points))[0]
        finally:
            prepared.close()
        records.append(
            {
                "case": case["name"],
                "input_segment_ids": case["ids"],
                "face_id": int(result["face_id"]),
                "segment_id": int(result["segment_id"]),
                "hit_t": float(result["hit_t"]),
                "goal4868_canonical_segment_id": _canonical_duplicate_segment_id(case),
                "native_matches_goal4868_canonical": int(result["segment_id"])
                == _canonical_duplicate_segment_id(case),
            }
        )

    payload = {
        "schema": "rtdl.goal4867.duplicate_half_edge_micro_probe.v1",
        "bounds": bounds,
        "point": [float(px[0]), float(py[0])],
        "query_map_id": 0,
        "records": records,
        "interpretation": (
            "If the selected face/segment changes when only duplicate half-edge input order changes, "
            "the remaining Section 5.7 issue is a missing duplicate-half-edge contract, not LSI or writer formatting. "
            "Goal4868 tests source-edge canonicalization as one deterministic contract candidate."
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
