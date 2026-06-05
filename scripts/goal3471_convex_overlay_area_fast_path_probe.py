from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402


class _FakeRelationColumns:
    def __init__(self, cp, *, left_ordinals, right_ordinals, geometry: dict[str, object]):
        self._cp = cp
        self._left_ordinals = cp.asarray(left_ordinals, dtype=cp.uint32)
        self._right_ordinals = cp.asarray(right_ordinals, dtype=cp.uint32)
        self._geometry = geometry
        self.row_count = int(self._left_ordinals.size)
        self.overflow = False

    def as_cupy_ordinal_columns(self) -> dict[str, object]:
        return {"left_ordinal": self._left_ordinals, "right_ordinal": self._right_ordinals}

    def as_cupy_geometry_payload_columns(self) -> dict[str, object]:
        return self._geometry


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _stats(values: list[float]) -> dict[str, float]:
    return {"min": min(values), "median": statistics.median(values), "max": max(values)}


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


def _polygon_refs(cp, specs: list[tuple[int, int, int]]):
    return cp.asarray(specs, dtype=cp.uint32)


def run_synthetic_probe() -> dict[str, object]:
    import cupy as cp  # type: ignore

    left_vertices = [
        (0.0, 0.0),
        (2.0, 0.0),
        (2.0, 2.0),
        (0.0, 2.0),
        (0.0, 0.0),
        (2.0, 0.0),
        (2.0, 1.0),
        (1.0, 0.5),
        (0.0, 1.0),
    ]
    right_vertices = [
        (1.0, 1.0),
        (3.0, 1.0),
        (3.0, 3.0),
        (1.0, 3.0),
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]
    geometry = {
        "left_polygon_refs": _polygon_refs(cp, [(10, 0, 4), (11, 4, 5)]),
        "right_polygon_refs": _polygon_refs(cp, [(20, 0, 4), (21, 4, 4)]),
        "left_vertices_x": cp.asarray([x for x, _ in left_vertices], dtype=cp.float32),
        "left_vertices_y": cp.asarray([y for _, y in left_vertices], dtype=cp.float32),
        "right_vertices_x": cp.asarray([x for x, _ in right_vertices], dtype=cp.float32),
        "right_vertices_y": cp.asarray([y for _, y in right_vertices], dtype=cp.float32),
        "left_bounds": cp.zeros((2, 4), dtype=cp.float32),
        "right_bounds": cp.zeros((2, 4), dtype=cp.float32),
    }
    relation_columns = _FakeRelationColumns(
        cp,
        left_ordinals=[0, 1],
        right_ordinals=[0, 1],
        geometry=geometry,
    )
    result = rt.shape_pair_relation_convex_overlay_area_cupy(relation_columns)
    row_areas = cp.asnumpy(result.row_areas).tolist()
    status = cp.asnumpy(result.status).tolist()
    expected_first_area = 1.0
    first_area_error = abs(float(row_areas[0]) - expected_first_area)
    return {
        "row_areas": [float(value) for value in row_areas],
        "status": [int(value) for value in status],
        "expected_first_area": expected_first_area,
        "first_area_error": first_area_error,
        "metadata": result.to_metadata(),
        "passed": first_area_error <= 1.0e-6 and int(status[0]) == 0 and int(status[1]) == 1,
    }


def run_public_cdb_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    relation_times: list[float] = []
    overlay_times: list[float] = []
    supported_counts: list[int] = []
    positive_counts: list[int] = []
    total_supported_areas: list[float] = []
    status_counts: list[dict[str, int]] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3471 convex overlay-area routed fast-path probe.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            relation_start = time.perf_counter()
            with prepared.active_relation_device_columns(packed_left, max_rows=int(args.max_rows)) as columns:
                cp.cuda.Stream.null.synchronize()
                relation_sec = time.perf_counter() - relation_start
                overlay_start = time.perf_counter()
                overlay = rt.shape_pair_relation_convex_overlay_area_cupy(
                    columns,
                    simple_vertex_threshold=int(args.simple_vertex_threshold),
                    max_vertices_per_shape=int(args.max_vertices_per_shape),
                )
                cp.cuda.Stream.null.synchronize()
                overlay_sec = time.perf_counter() - overlay_start
                metadata = overlay.to_metadata()
                relation_times.append(relation_sec)
                overlay_times.append(overlay_sec)
                supported_counts.append(int(metadata["supported_row_count"]))
                positive_counts.append(int(metadata["positive_area_row_count"]))
                total_supported_areas.append(float(metadata["total_supported_area"]))
                status_counts.append({str(k): int(v) for k, v in metadata["status_counts"].items()})
                run = {
                    "iteration": index,
                    "row_count": int(columns.row_count),
                    "relation_columns_sec": relation_sec,
                    "convex_overlay_area_sec": overlay_sec,
                    "metadata": metadata,
                    "claim_boundary": _claim_boundary(),
                }
                runs.append(run)
                print(
                    "[goal3471] "
                    f"iteration={index} rows={columns.row_count} supported={metadata['supported_row_count']} "
                    f"positive={metadata['positive_area_row_count']} "
                    f"area={metadata['total_supported_area']:.9f} "
                    f"status={metadata['status_counts']} relation={relation_sec:.6f}s overlay={overlay_sec:.6f}s",
                    flush=True,
                )

    return {
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "relation_columns_sec": _stats(relation_times),
        "convex_overlay_area_sec": _stats(overlay_times),
        "supported_row_counts": supported_counts,
        "positive_area_row_counts": positive_counts,
        "total_supported_areas": total_supported_areas,
        "status_counts": status_counts,
        "all_supported_counts_stable": len(set(supported_counts)) == 1,
        "all_status_counts_stable": all(item == status_counts[0] for item in status_counts),
        "runs": runs,
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    synthetic = run_synthetic_probe()
    public_cdb = run_public_cdb_probe(args)
    return {
        "schema": "rtdl.goal3471.convex_overlay_area_fast_path_probe.v1",
        "goal": 3471,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "iterations": int(args.iterations),
        "max_rows": int(args.max_rows),
        "simple_vertex_threshold": int(args.simple_vertex_threshold),
        "max_vertices_per_shape": int(args.max_vertices_per_shape),
        "synthetic_convex_fixture": synthetic,
        "public_cdb": public_cdb,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3471 convex overlay-area fast-path probe.")
    parser.add_argument(
        "--left-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--iterations", type=int, default=4)
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--simple-vertex-threshold", type=int, default=64)
    parser.add_argument("--max-vertices-per-shape", type=int, default=128)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if not payload["synthetic_convex_fixture"]["passed"]:
        raise SystemExit(1)
    if not payload["public_cdb"]["all_supported_counts_stable"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
