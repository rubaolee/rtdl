from __future__ import annotations

import json

import numpy as np

import rtdsl as rt


def main() -> int:
    columns = rt.Aabb2DColumns.from_mapping(
        {
            "id": np.asarray([10, 20], dtype=np.uint32),
            "min_x": np.asarray([0.0, 5.0]),
            "min_y": np.asarray([0.0, 5.0]),
            "max_x": np.asarray([2.0, 7.0]),
            "max_y": np.asarray([2.0, 7.0]),
        }
    )
    points = ((1.0, 1.0), (6.0, 6.0), (3.0, 3.0))
    columnar = rt.prepare_aabb_index_2d_columns(columns, backend="optix")
    try:
        columnar_result = columnar.count(point_queries=points, operation="point_contains")
    finally:
        columnar.close()
    row = rt.prepare_aabb_index_2d(
        ((0.0, 0.0, 2.0, 2.0), (5.0, 5.0, 7.0, 7.0)),
        backend="optix",
    )
    try:
        row_result = row.count(point_queries=points, operation="point_contains")
    finally:
        row.close()
    payload = {
        "schema": "rtdl.goal5487.generic_aabb_columnar_pod_gate.v1",
        "columnar_counts": columnar_result["counts"],
        "row_counts": row_result["counts"],
        "counts_match": columnar_result["counts"] == row_result["counts"],
        "columnar_rt_core_accelerated": bool(columnar_result["rt_core_accelerated"]),
        "row_rt_core_accelerated": bool(row_result["rt_core_accelerated"]),
        "claim_boundary": {
            "device_zero_copy_claimed": False,
            "librts_specific_claimed": False,
            "performance_ratio_claimed": False,
            "embree_in_scope": False,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["counts_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
