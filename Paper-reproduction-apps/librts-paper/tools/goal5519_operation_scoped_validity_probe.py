from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import rtdsl as rt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    box64 = np.asarray(
        [[-69.73984, -89.967841, -69.734454, -89.967839]],
        dtype=np.float64,
    )
    box32 = box64.astype(np.float32)
    if not (box64[0, 1] < box64[0, 3] and box32[0, 1] == box32[0, 3]):
        raise RuntimeError("fixture must be valid in float64 and collapsed in float32")

    indexed = rt.Aabb2DColumns(
        ids=np.asarray([17], dtype=np.uint32),
        min_x=box64[:, 0],
        min_y=box64[:, 1],
        max_x=box64[:, 2],
        max_y=box64[:, 3],
    )
    query_box = rt.Aabb2D(
        float(box32[0, 0]),
        float(box32[0, 1]),
        float(box32[0, 2]),
        float(box32[0, 3]),
    )
    query_point = (
        0.5 * (float(box32[0, 0]) + float(box32[0, 2])),
        float(box32[0, 1]),
    )

    prepared = rt.prepare_aabb_index_2d_columns(indexed, backend="optix")
    try:
        counts = {
            "point_contains": int(
                prepared.count(point_queries=(query_point,), operation="point_contains")["counts"]["point_contains"]
            ),
            "range_contains": int(
                prepared.count(box_queries=(query_box,), operation="range_contains")["counts"]["range_contains"]
            ),
            "range_intersects": int(
                prepared.count(box_queries=(query_box,), operation="range_intersects")["counts"]["range_intersects"]
            ),
        }
    finally:
        prepared.close()

    expected = {"point_contains": 1, "range_contains": 1, "range_intersects": 0}
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5519_operation_scoped_validity_probe.v1",
        "status": "operation_scoped_validity_contract_matched" if counts == expected else "operation_scoped_validity_contract_mismatch",
        "float64_box": box64[0].tolist(),
        "float32_box": box32[0].tolist(),
        "float32_collapsed": True,
        "counts": counts,
        "expected_counts": expected,
        "matched": counts == expected,
        "optix_library": os.environ.get("RTDL_OPTIX_LIB", ""),
        "claim_boundary": {
            "generic_operation_contract_probe": True,
            "paper_input_used": False,
            "app_specific_core_behavior_authorized": False,
            "performance_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
