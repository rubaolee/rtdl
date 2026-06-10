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
        "full_overlay_area_claim_authorized": False,
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


def _expected_refs(polygons: tuple[rt.Polygon, ...]) -> list[list[int]]:
    refs: list[list[int]] = []
    offset = 0
    for polygon in polygons:
        count = len(polygon.vertices)
        refs.append([int(polygon.id), offset, count])
        offset += count
    return refs


def _expected_xy(polygons: tuple[rt.Polygon, ...]) -> tuple[list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    for polygon in polygons:
        for x, y in polygon.vertices:
            xs.append(float(x))
            ys.append(float(y))
    return xs, ys


def _expected_bounds(polygons: tuple[rt.Polygon, ...]) -> list[list[float]]:
    bounds: list[list[float]] = []
    for polygon in polygons:
        xs = [float(x) for x, _ in polygon.vertices]
        ys = [float(y) for _, y in polygon.vertices]
        bounds.append([min(xs), min(ys), max(xs), max(ys)])
    return bounds


def _as_list(array) -> list:
    import cupy as cp  # type: ignore

    cp.cuda.Stream.null.synchronize()
    return cp.asnumpy(array).tolist()


def run_probe() -> dict[str, object]:
    left, right = _fixture()
    with prepare_rayjoin_optix_shape_pair_active_count(
        right,
        dataset="goal3453_sparse_id_geometry_payload_fixture",
        dataset_note="Goal3453 generic geometry-payload device-column fixture.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left)
        with prepared.active_relation_device_columns(packed_left, max_rows=32) as columns:
            geometry = columns.as_cupy_geometry_payload_columns()
            metadata = columns.to_metadata()
            observed = {
                "left_polygon_refs": _as_list(geometry["left_polygon_refs"]),
                "right_polygon_refs": _as_list(geometry["right_polygon_refs"]),
                "left_vertices_x": _as_list(geometry["left_vertices_x"]),
                "left_vertices_y": _as_list(geometry["left_vertices_y"]),
                "right_vertices_x": _as_list(geometry["right_vertices_x"]),
                "right_vertices_y": _as_list(geometry["right_vertices_y"]),
                "left_bounds": _as_list(geometry["left_bounds"]),
                "right_bounds": _as_list(geometry["right_bounds"]),
            }

    expected = {
        "left_polygon_refs": _expected_refs(left),
        "right_polygon_refs": _expected_refs(right),
        "left_vertices_x": _expected_xy(left)[0],
        "left_vertices_y": _expected_xy(left)[1],
        "right_vertices_x": _expected_xy(right)[0],
        "right_vertices_y": _expected_xy(right)[1],
        "left_bounds": _expected_bounds(left),
        "right_bounds": _expected_bounds(right),
    }
    matches = observed == expected
    return {
        "schema": "rtdl.goal3453.shape_pair_relation_geometry_payload.v1",
        "goal": 3453,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "fixture": "sparse_id_three_left_four_right_rectangles",
        "observed": observed,
        "expected": expected,
        "geometry_payload_matches": matches,
        "metadata_geometry_payload": metadata["runtime"]["geometry_payload"],
        "metadata_schema_id": metadata["v2_8_typed_producer_metadata"]["schema_id"],
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3453 relation geometry payload device-column probe.")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not payload["geometry_payload_matches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
