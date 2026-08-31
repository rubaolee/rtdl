"""Deterministic Goal5798 matched workloads and route-independent oracle.

This module is standard-library only and imports none of the Direct OptiX,
PyOptiX, OWL, or RTDL implementation routes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


RELATION_SIZE = 4096
TRIANGLE_SIZE = 16384


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def relation_workload(size: int = RELATION_SIZE) -> dict[str, object]:
    if size != RELATION_SIZE:
        raise ValueError("Goal5798 relation size is frozen at 4096")
    indexed: list[list[object]] = []
    queries: list[list[object]] = []
    expected: list[list[int]] = []
    for item_id in range(size):
        lower_x = f32(2 * item_id)
        upper_x = f32(2 * item_id + 1)
        box: list[object] = [lower_x, f32(0), upper_x, f32(1), item_id]
        indexed.append(box)
        queries.append(list(box))
        expected.append([item_id, item_id])
    return {
        "id": "GOAL5798_RELATION_4096_ONE_TO_ONE",
        "indexed": indexed,
        "sources": queries,
        "minimum_overlap": f32(1),
        "capacity": size,
        "expected_rows": expected,
    }


def triangle_workload(size: int = TRIANGLE_SIZE) -> dict[str, object]:
    if size != TRIANGLE_SIZE:
        raise ValueError("Goal5798 triangle size is frozen at 16384")
    vertices: list[list[float]] = []
    rays: list[list[list[float]]] = []
    weights: list[int] = []
    for ray_id in range(size):
        center_x = 3 * ray_id
        vertices.extend([
            [f32(center_x - 1), f32(-1), f32(1)],
            [f32(center_x + 1), f32(-1), f32(1)],
            [f32(center_x), f32(1), f32(1)],
        ])
        rays.append([
            [f32(center_x), f32(0), f32(0)],
            [f32(0), f32(0), f32(1)],
        ])
        weights.append(1 + ray_id % 7)
    expected_per_ray = [1] * size
    return {
        "id": "GOAL5798_TRIANGLE_16384_ONE_HIT",
        "vertices": vertices,
        "rays": rays,
        "weights": weights,
        "tmin": f32(0),
        "tmax": f32(2),
        "expected_per_ray": expected_per_ray,
        "expected_weighted_sum": sum(weights),
    }


def workload_authority() -> dict[str, object]:
    relation = relation_workload()
    triangle = triangle_workload()
    result: dict[str, object] = {
        "schema": "rtdl.goal5798.matched_workload_authority.v1",
        "status": "PASS",
        "generator_imports_gpu_or_rtdl_routes": False,
        "relation": {
            "id": relation["id"],
            "indexed_box_count": len(relation["indexed"]),
            "query_box_count": len(relation["sources"]),
            "minimum_overlap_f32": relation["minimum_overlap"],
            "semantic_capacity": relation["capacity"],
            "expected_canonical_row_count": len(relation["expected_rows"]),
            "indexed_sha256": digest(relation["indexed"]),
            "queries_sha256": digest(relation["sources"]),
            "expected_rows_sha256": digest(relation["expected_rows"]),
            "kat": {
                "first": relation["expected_rows"][0],
                "middle": relation["expected_rows"][RELATION_SIZE // 2],
                "last": relation["expected_rows"][-1],
            },
        },
        "triangle": {
            "id": triangle["id"],
            "triangle_count": len(triangle["vertices"]) // 3,
            "ray_count": len(triangle["rays"]),
            "vertices_sha256": digest(triangle["vertices"]),
            "rays_sha256": digest(triangle["rays"]),
            "weights_sha256": digest(triangle["weights"]),
            "expected_per_ray_sha256": digest(triangle["expected_per_ray"]),
            "expected_weighted_sum": triangle["expected_weighted_sum"],
            "kat": {
                "first_weight": triangle["weights"][0],
                "eighth_weight": triangle["weights"][7],
                "last_weight": triangle["weights"][-1],
                "last_ray": triangle["rays"][-1],
            },
        },
    }
    result["authority_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-output", type=Path, required=True)
    args = parser.parse_args()
    if args.authority_output.exists():
        raise FileExistsError(args.authority_output)
    authority = workload_authority()
    args.authority_output.parent.mkdir(parents=True, exist_ok=True)
    args.authority_output.write_bytes(json.dumps(
        authority, indent=2, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps(authority, sort_keys=True))


if __name__ == "__main__":
    main()
