#!/usr/bin/env python3
"""Stdlib-only oracle and result checker for Goal5796.

This file imports none of the A/B/C/D implementation routes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


U64_MAX = (1 << 64) - 1


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def relation_rows(fixture: dict[str, object]) -> list[list[int]]:
    threshold = f32(fixture["minimum_overlap"])
    rows: set[tuple[int, int]] = set()
    for source_raw in fixture["sources"]:
        source = [f32(v) for v in source_raw[:4]]
        source_id = int(source_raw[4])
        for item_raw in fixture["indexed"]:
            item = [f32(v) for v in item_raw[:4]]
            item_id = int(item_raw[4])
            closed = (
                item[0] <= source[2]
                and item[2] >= source[0]
                and item[1] <= source[3]
                and item[3] >= source[1]
            )
            dx = f32(max(f32(0.0), f32(min(source[2], item[2]) - max(source[0], item[0]))))
            dy = f32(max(f32(0.0), f32(min(source[3], item[3]) - max(source[1], item[1]))))
            area = f32(dx * dy)
            if closed and area >= threshold:
                rows.add((source_id, item_id))
    ordered = [list(row) for row in sorted(rows)]
    if len(ordered) > int(fixture["capacity"]):
        raise OverflowError("relation capacity exceeded; no partial result")
    return ordered


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [f32(a[i] - b[i]) for i in range(3)]


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [
        f32(a[1] * b[2] - a[2] * b[1]),
        f32(a[2] * b[0] - a[0] * b[2]),
        f32(a[0] * b[1] - a[1] * b[0]),
    ]


def _dot(a: list[float], b: list[float]) -> float:
    return f32(f32(a[0] * b[0]) + f32(a[1] * b[1]) + f32(a[2] * b[2]))


def intersects_triangle(
    origin_raw: list[float], direction_raw: list[float],
    a_raw: list[float], b_raw: list[float], c_raw: list[float],
    tmin: float, tmax: float,
) -> bool:
    origin = [f32(v) for v in origin_raw]
    direction = [f32(v) for v in direction_raw]
    a = [f32(v) for v in a_raw]
    b = [f32(v) for v in b_raw]
    c = [f32(v) for v in c_raw]
    e1 = _sub(b, a)
    e2 = _sub(c, a)
    p = _cross(direction, e2)
    det = _dot(e1, p)
    if abs(det) <= f32(1.0e-7):
        return False
    inv_det = f32(1.0 / det)
    tv = _sub(origin, a)
    u = f32(_dot(tv, p) * inv_det)
    if u < 0.0 or u > 1.0:
        return False
    q = _cross(tv, e1)
    v = f32(_dot(direction, q) * inv_det)
    if v < 0.0 or f32(u + v) > 1.0:
        return False
    t = f32(_dot(e2, q) * inv_det)
    return f32(tmin) <= t <= f32(tmax)


def triangle_result(task: dict[str, object]) -> tuple[list[int], int]:
    vertices = task["vertices"]
    if len(vertices) % 3:
        raise ValueError("triangle vertex count is not divisible by three")
    counts: list[int] = []
    for origin, direction in task["rays"]:
        count = sum(
            intersects_triangle(
                origin, direction, vertices[i], vertices[i + 1], vertices[i + 2],
                task["tmin"], task["tmax"],
            )
            for i in range(0, len(vertices), 3)
        )
        counts.append(count)
    total = 0
    for count, weight in zip(counts, task["weights"], strict=True):
        product = count * int(weight)
        if product > U64_MAX or total > U64_MAX - product:
            raise OverflowError("checked u64 reduction overflow")
        total += product
    return counts, total


def build_expected(spec: dict[str, object]) -> dict[str, object]:
    relation = spec["tasks"]["CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"]
    relation_results = {
        row["id"]: relation_rows(row) for row in relation["fixtures"]
    }
    triangle = spec["tasks"]["BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"]
    per_ray, weighted = triangle_result(triangle)
    expected = {
        "bounded_relation": relation_results,
        "triangle": {"per_ray": per_ray, "weighted_sum": weighted},
    }
    for row in relation["fixtures"]:
        if relation_results[row["id"]] != row["expected_rows"]:
            raise RuntimeError(f"frozen relation expectation drift: {row['id']}")
    witness = relation["overflow_witness"]
    witness_rows = relation_results[witness["base_fixture_id"]]
    if len(witness_rows) != int(witness["expected_unique_row_count"]) \
            or len(witness_rows) <= int(witness["capacity"]):
        raise RuntimeError("frozen relation overflow witness drift")
    if per_ray != triangle["expected_per_ray"] or weighted != triangle["expected_weighted_sum"]:
        raise RuntimeError("frozen triangle expectation drift")
    return expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=Path(__file__).with_name("semantic_spec.json"))
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    spec_bytes = args.spec.read_bytes()
    spec = json.loads(spec_bytes)
    expected = build_expected(spec)
    output: dict[str, object] = {
        "schema": "rtdl.goal5796.independent_oracle.v1",
        "status": "PASS",
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "expected": expected,
        "expected_sha256": digest(expected),
        "overflow_witness": spec["tasks"]
            ["CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"]["overflow_witness"],
    }
    if args.result:
        result = json.loads(args.result.read_bytes())
        if result["outputs"] != expected:
            raise RuntimeError("implementation output differs from independent oracle")
        output["checked_result_sha256"] = hashlib.sha256(args.result.read_bytes()).hexdigest()
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
