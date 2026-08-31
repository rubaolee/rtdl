from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
    }


def _fixture() -> tuple[tuple[rt.Polygon, ...], tuple[rt.Polygon, ...]]:
    left = (
        rt.Polygon(id=3, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
        rt.Polygon(id=20, vertices=((5.0, 5.0), (6.0, 5.0), (6.0, 6.0), (5.0, 6.0))),
        rt.Polygon(id=31, vertices=((10.0, 10.0), (11.0, 10.0), (11.0, 11.0), (10.0, 11.0))),
    )
    right = (
        rt.Polygon(id=10, vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))),
        rt.Polygon(id=11, vertices=((0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75))),
        rt.Polygon(id=12, vertices=((20.0, 20.0), (21.0, 20.0), (21.0, 21.0), (20.0, 21.0))),
        rt.Polygon(id=13, vertices=((4.0, 4.0), (7.0, 4.0), (7.0, 7.0), (4.0, 7.0))),
    )
    return left, right


def _host_active_rows(prepared, packed_left) -> list[dict[str, int]]:
    view = prepared._prepared.run_raw(packed_left.packed_polygons)
    try:
        rows = []
        for row in view.to_dict_rows():
            requires_segment = int(row["requires_lsi"])
            requires_containment = int(row["requires_pip"])
            if requires_segment or requires_containment:
                rows.append(
                    {
                        "left_id": int(row["left_polygon_id"]),
                        "right_id": int(row["right_polygon_id"]),
                        "requires_segment_intersection": requires_segment,
                        "requires_point_containment": requires_containment,
                    }
                )
        return sorted(rows, key=lambda item: (item["left_id"], item["right_id"]))
    finally:
        view.close()


def _device_active_rows(columns) -> list[dict[str, int]]:
    cupy_columns = columns.as_cupy_columns()
    import cupy as cp  # type: ignore

    cp.cuda.Stream.null.synchronize()
    left_ids = cp.asnumpy(cupy_columns["left_id"]).tolist()
    right_ids = cp.asnumpy(cupy_columns["right_id"]).tolist()
    requires_segment = cp.asnumpy(cupy_columns["requires_segment_intersection"]).tolist()
    requires_containment = cp.asnumpy(cupy_columns["requires_point_containment"]).tolist()
    rows = [
        {
            "left_id": int(left_id),
            "right_id": int(right_id),
            "requires_segment_intersection": int(segment),
            "requires_point_containment": int(containment),
        }
        for left_id, right_id, segment, containment in zip(
            left_ids,
            right_ids,
            requires_segment,
            requires_containment,
        )
    ]
    return sorted(rows, key=lambda item: (item["left_id"], item["right_id"]))


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    left, right = _fixture()
    with prepare_rayjoin_optix_shape_pair_active_count(
        right,
        dataset="goal3450_sparse_id_synthetic_fixture",
        dataset_note="Goal3450 sparse-id content-correctness fixture.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left)
        host_rows = _host_active_rows(prepared, packed_left)
        with prepared.active_relation_device_columns(
            packed_left,
            max_rows=int(args.max_rows),
        ) as columns:
            device_rows = _device_active_rows(columns)
            metadata = columns.to_metadata()
        with prepared.active_relation_device_columns(packed_left, max_rows=1) as overflow_columns:
            overflow_metadata = overflow_columns.to_metadata()
            overflow_result = {
                "overflow": bool(overflow_columns.overflow),
                "row_count": int(overflow_columns.row_count),
                "active_relation_count": int(overflow_columns.active_relation_count),
                "retry_capacity_hint": overflow_columns.retry_capacity_hint,
                "metadata_capacity_status": overflow_metadata["capacity_status"],
            }

    rows_match = host_rows == device_rows
    return {
        "schema": "rtdl.goal3450.shape_pair_relation_device_column_content.v1",
        "goal": 3450,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "fixture": "sparse_id_three_left_four_right_rectangles",
        "left_ids": [int(poly.id) for poly in left],
        "right_ids": [int(poly.id) for poly in right],
        "host_active_rows": host_rows,
        "device_active_rows": device_rows,
        "rows_match": rows_match,
        "host_row_count": len(host_rows),
        "device_row_count": len(device_rows),
        "metadata_schema_id": metadata["v2_8_typed_producer_metadata"]["schema_id"],
        "metadata_device_resident_output_stream_proven": metadata["v2_8_typed_producer_metadata"][
            "device_resident_output_stream_proven"
        ],
        "overflow_capacity_probe": overflow_result,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3450 relation device-column content correctness probe.")
    parser.add_argument("--max-rows", type=int, default=32)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not payload["rows_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
