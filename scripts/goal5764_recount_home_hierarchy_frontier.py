#!/usr/bin/env python3
"""Independent raw recount for Goal5764; imports no RTDL/product/app module."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def check_receipt(receipt: dict[str, object], output_sha: str) -> None:
    body = dict(receipt)
    claimed = body.pop("receipt_sha256")
    if claimed != digest(body):
        raise AssertionError("receipt digest mismatch")
    snap = receipt["native_snapshot"]
    successful = snap["successful_launch_count"]
    if not (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and receipt["output_digest"] == output_sha
        and successful > 0
        and snap["complete_context_launch_count"] == successful
        and snap["failed_launch_count"] == 0
        and snap["incomplete_context_launch_count"] == 0
        and snap["pending_context_at_finish"] == 0
        and snap["session_error"] == 0
        and snap["raygen_invocation_count"] > 0
        and snap["first_traversable"]
        and snap["last_traversable"]
        and receipt["expected_program_observed_at_receipt_edge"] is True
    ):
        raise AssertionError("behavioral traversal receipt invalid")


def recount(columns: dict[str, list], reducer: str, ratio: float, softening: float):
    point_count = len(columns["point_x"])
    node_count = len(columns["node_cx"])
    child_nodes = set(columns["child_indices"])
    roots = [index for index in range(node_count) if index not in child_nodes]
    if len(roots) != 1:
        raise AssertionError("one root required")
    rows = []
    softening_sq = softening * softening
    for source in range(point_count):
        value = 0.0
        visited = aggregate = exact = 0
        status = 0
        node = roots[0]
        ray_self = 0
        steps = 0
        while node >= 0:
            if node >= node_count:
                status = 2
                break
            steps += 1
            if steps > node_count * 2 + 1:
                status = 3
                break
            visited += 1
            is_leaf = columns["child_offsets"][node] == columns["child_offsets"][node + 1]
            dx = columns["point_x"][source] - columns["node_cx"][node]
            dy = columns["point_y"][source] - columns["node_cy"][node]
            dz = columns["point_z"][source] - columns["node_cz"][node]
            raw_distance_sq = dx * dx + dy * dy + dz * dz
            distance_sq = raw_distance_sq + softening_sq
            hit = columns["node_half_size"][node] < math.sqrt(raw_distance_sq) * ratio

            def add_leaf() -> None:
                nonlocal value, exact
                begin = columns["member_offsets"][node]
                end = columns["member_offsets"][node + 1]
                for offset in range(begin, end):
                    item = columns["member_indices"][offset]
                    if item == source:
                        continue
                    if reducer == "aggregate_count":
                        value += 1.0
                    else:
                        x = columns["point_x"][item] - columns["point_x"][source]
                        y = columns["point_y"][item] - columns["point_y"][source]
                        z = columns["point_z"][item] - columns["point_z"][source]
                        dsq = x * x + y * y + z * z + softening_sq
                        if dsq > 0.0:
                            value += columns["point_weight"][source] * columns["point_weight"][item] / dsq
                    exact += 1

            if hit:
                if is_leaf:
                    add_leaf()
                elif distance_sq > 0.0:
                    if reducer == "aggregate_count":
                        value += 1.0
                    else:
                        value += columns["point_weight"][source] * columns["node_weight"][node] / distance_sq
                    aggregate += 1
                node = columns["node_rope_index"][node]
            else:
                if is_leaf and ray_self == 0:
                    add_leaf()
                node = columns["node_next_index"][node]
            if node < 0:
                break
            ndx = columns["point_x"][source] - columns["node_cx"][node]
            ndy = columns["point_y"][source] - columns["node_cy"][node]
            ndz = columns["point_z"][source] - columns["node_cz"][node]
            ray_self = 1 if math.sqrt(ndx * ndx + ndy * ndy + ndz * ndz) * ratio == 0.0 else 0
        rows.append({
            "source_id": source,
            "reducer_value_0": value,
            "reducer_value_1": 0.0,
            "reducer_value_2": 0.0,
            "visited_node_count": visited,
            "aggregate_contribution_count": aggregate,
            "exact_contribution_count": exact,
            "status_code": status,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_path = args.raw / "RESULT.json" if args.raw.is_dir() else args.raw
    raw = json.loads(raw_path.read_text())
    summaries = []
    for lane in raw["lanes"]:
        inputs = lane["input"]
        rows = recount(
            inputs["hierarchy_columns"],
            inputs["reducer"],
            float(inputs["opening"]["max_ratio"]),
            float(inputs["softening"]),
        )
        actual = lane["native_rows"]
        if len(rows) != len(actual):
            raise AssertionError("row count mismatch")
        maximum_delta = 0.0
        for expected, observed in zip(rows, actual):
            for key in (
                "source_id", "visited_node_count", "aggregate_contribution_count",
                "exact_contribution_count", "status_code",
            ):
                if int(expected[key]) != int(observed[key]):
                    raise AssertionError(f"{lane['lane']} {key} mismatch")
            delta = abs(float(expected["reducer_value_0"]) - float(observed["reducer_value_0"]))
            maximum_delta = max(maximum_delta, delta)
            tolerance = 1.0e-12 * max(1.0, abs(float(expected["reducer_value_0"])))
            if delta > tolerance:
                raise AssertionError(f"{lane['lane']} reducer mismatch {delta}")
        output_sha = digest(actual)
        if output_sha != lane["output_sha256"]:
            raise AssertionError("output digest mismatch")
        check_receipt(lane["traversal_receipt"], output_sha)
        if "expected_rows" in lane:
            scale = float(lane["paper_reference"]["force_scale"])
            for native, expected in zip(actual, lane["expected_rows"]):
                if abs(float(native["reducer_value_0"]) * scale - float(expected["scalar_force"])) > 1.0e-9:
                    raise AssertionError("independent paper oracle mismatch")
        summaries.append({
            "lane": lane["lane"],
            "row_count": len(rows),
            "maximum_reducer_delta": maximum_delta,
            "output_sha256": output_sha,
            "receipt_sha256": lane["traversal_receipt"]["receipt_sha256"],
            "exact": True,
            "behavioral_true_optix": True,
        })
    result = {
        "schema": "rtdl.goal5764.independent_hierarchy_frontier_recount.v1",
        "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "lane_count": len(summaries),
        "exact_count": sum(row["exact"] for row in summaries),
        "behavioral_true_optix_count": sum(row["behavioral_true_optix"] for row in summaries),
        "imports_product_compiler_or_app": False,
        "lanes": summaries,
    }
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
