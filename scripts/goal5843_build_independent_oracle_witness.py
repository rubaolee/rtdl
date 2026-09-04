#!/usr/bin/env python3
"""Build a route-independent structural oracle witness for Goal5843."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5798_premeasurement.workload import (
    relation_workload,
    triangle_workload,
)
from experiments.goal5843_post_r1_baseline.contracts import (
    ORACLE_WITNESS_SCHEMA,
    RELATION_TASK,
    TRIANGLE_TASK,
    digest,
    load_preregistration,
    task_contract,
)
from experiments.goal5843_post_r1_baseline.runtime import create_json, git_head


ROOT = Path(__file__).resolve().parents[1]
U64_MAX = (1 << 64) - 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg = load_preregistration(
        args.preregistration.resolve(), ROOT, verify_files=True
    )
    relation = relation_workload()
    relation_rows = []
    for index, (item, source) in enumerate(
        zip(relation["indexed"], relation["sources"], strict=True)
    ):
        if item != source or int(item[4]) != index:
            raise RuntimeError("relation deterministic identity invariant failed")
        if item[:4] != [float(2 * index), 0.0, float(2 * index + 1), 1.0]:
            raise RuntimeError("relation unit-box invariant failed")
        if index and float(item[0]) <= float(relation["indexed"][index - 1][2]):
            raise RuntimeError("relation boxes are not strictly separated")
        relation_rows.append((index, index))
    relation_input_sha = digest(
        {
            "indexed": relation["indexed"],
            "sources": relation["sources"],
            "capacity": relation["capacity"],
            "minimum_overlap": relation["minimum_overlap"],
        }
    )
    relation_contract = task_contract(prereg, RELATION_TASK)
    if (
        relation_input_sha != relation_contract["input_sha256"]
        or digest(tuple(relation_rows)) != relation_contract["full_oracle_sha256"]
    ):
        raise RuntimeError("independent relation oracle differs from preregistration")

    triangle = triangle_workload()
    size = len(triangle["rays"])
    if len(triangle["vertices"]) != size * 3 or len(triangle["weights"]) != size:
        raise RuntimeError("triangle fixture cardinality mismatch")
    per_ray = []
    weighted = 0
    for index, ((origin, direction), weight) in enumerate(
        zip(triangle["rays"], triangle["weights"], strict=True)
    ):
        center = float(3 * index)
        vertices = triangle["vertices"][index * 3 : index * 3 + 3]
        expected_vertices = [
            [center - 1.0, -1.0, 1.0],
            [center + 1.0, -1.0, 1.0],
            [center, 1.0, 1.0],
        ]
        if vertices != expected_vertices:
            raise RuntimeError("triangle geometry invariant failed")
        if origin != [center, 0.0, 0.0] or direction != [0.0, 0.0, 1.0]:
            raise RuntimeError("triangle ray invariant failed")
        if index and center - float(triangle["vertices"][(index - 1) * 3 + 1][0]) <= 1.0:
            raise RuntimeError("triangle x-support separation invariant failed")
        # At t=1 the ray reaches (center, 0, 1), strictly inside its own
        # triangle. Disjoint x-support proves no other triangle can be hit.
        count = 1
        product = count * int(weight)
        if product > U64_MAX or weighted > U64_MAX - product:
            raise OverflowError("independent checked-u64 reduction overflow")
        weighted += product
        per_ray.append(count)
    triangle_input_sha = digest(
        {
            "vertices": triangle["vertices"],
            "rays": triangle["rays"],
            "weights": triangle["weights"],
            "tmin": triangle["tmin"],
            "tmax": triangle["tmax"],
        }
    )
    full_triangle = {"weighted_sum": weighted, "per_ray": tuple(per_ray)}
    triangle_contract = task_contract(prereg, TRIANGLE_TASK)
    if (
        triangle_input_sha != triangle_contract["input_sha256"]
        or digest(full_triangle) != triangle_contract["full_oracle_sha256"]
        or digest(weighted) != triangle_contract["public_output_sha256"]
    ):
        raise RuntimeError("independent triangle oracle differs from preregistration")
    result: dict[str, object] = {
        "schema": ORACLE_WITNESS_SCHEMA,
        "status": "PASS__ROUTE_INDEPENDENT_STRUCTURAL_ORACLE_REDERIVED",
        "source_commit": git_head(ROOT),
        "preregistration_sha256": prereg["preregistration_sha256"],
        "implementation_route_import_count": 0,
        "registered_timing_observation_count": 0,
        "tasks": [
            {
                "task": RELATION_TASK,
                "input_sha256": relation_input_sha,
                "full_oracle_sha256": digest(tuple(relation_rows)),
                "public_output_sha256": digest(tuple(relation_rows)),
                "row_count": len(relation_rows),
                "structural_proof": "strictly_separated_unit_boxes_self_overlap_only",
            },
            {
                "task": TRIANGLE_TASK,
                "input_sha256": triangle_input_sha,
                "full_oracle_sha256": digest(full_triangle),
                "public_output_sha256": digest(weighted),
                "per_ray_count": len(per_ray),
                "weighted_sum": weighted,
                "structural_proof": "disjoint_x_support_and_strict_own_triangle_interior",
            },
        ],
    }
    result["witness_sha256"] = digest(result)
    create_json(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
