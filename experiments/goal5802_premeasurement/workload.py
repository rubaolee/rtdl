"""Route-independent Goal5802 workloads and scalar-only triangle oracle.
This module is deliberately standard-library only.  It does not import RTDL,
PyOptiX, CUDA, OptiX, NumPy, or any measured arm.  In particular, the
triangle task has no per-ray host output: its complete user-visible product is
one checked unsigned-64 reduction after a successful device-status decision.
"""

from __future__ import annotations

import hashlib
import json
import struct


RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED"
RELATION_SIZE = 4096
TRIANGLE_SIZE = 16384


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def f32(value: object) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def f32_bits(value: object) -> int:
    return struct.unpack("<I", struct.pack("<f", float(value)))[0]


def relation_workload() -> dict[str, object]:
    indexed: list[list[object]] = []
    sources: list[list[object]] = []
    expected_rows: list[list[int]] = []
    for item_id in range(RELATION_SIZE):
        lower = f32(2 * item_id)
        row: list[object] = [
            lower, f32(0), f32(2 * item_id + 1), f32(1), item_id,
        ]
        indexed.append(row)
        sources.append(list(row))
        expected_rows.append([item_id, item_id])
    return {
        "task": RELATION_TASK,
        "indexed": indexed,
        "sources": sources,
        "minimum_overlap_f32": f32(1),
        "semantic_capacity": RELATION_SIZE,
        "expected_rows": expected_rows,
    }


def _segment_intersects_closed_box(
        query: list[object], item: list[object], *, reverse: bool) -> bool:
    if reverse:
        origin = (float(query[0]), float(query[1]))
        direction = (
            float(query[2]) - float(query[0]),
            float(query[3]) - float(query[1]))
    else:
        origin = (float(query[2]), float(query[1]))
        direction = (
            float(query[0]) - float(query[2]),
            float(query[3]) - float(query[1]))
    lower = (float(item[0]), float(item[1]))
    upper = (float(item[2]), float(item[3]))
    t_min, t_max = 0.0, 1.0
    for axis in range(2):
        if direction[axis] == 0.0:
            if origin[axis] < lower[axis] or origin[axis] > upper[axis]:
                return False
            continue
        first = (lower[axis] - origin[axis]) / direction[axis]
        second = (upper[axis] - origin[axis]) / direction[axis]
        axis_min, axis_max = min(first, second), max(first, second)
        t_min, t_max = max(t_min, axis_min), min(t_max, axis_max)
        if t_min > t_max:
            return False
    return True


def derive_relation_rows_cpu(
        indexed: list[list[object]], sources: list[list[object]],
        minimum_overlap: float) -> dict[str, object]:
    """Derive both traversal orientations without importing an RT route."""

    rows: list[tuple[int, int]] = []
    counts = []
    for reverse in (False, True):
        boxes, queries = (sources, indexed) if reverse else (indexed, sources)
        before = len(rows)
        for query in queries:
            for item in boxes:
                if not _segment_intersects_closed_box(
                        query, item, reverse=reverse):
                    continue
                dx = max(0.0, min(float(query[2]), float(item[2]))
                         - max(float(query[0]), float(item[0])))
                dy = max(0.0, min(float(query[3]), float(item[3]))
                         - max(float(query[1]), float(item[1])))
                if dx * dy < minimum_overlap:
                    continue
                rows.append((
                    int(item[4]) if reverse else int(query[4]),
                    int(query[4]) if reverse else int(item[4])))
        counts.append(len(rows) - before)
    return {
        "kind": (
            "ROUTE_INDEPENDENT_CPU_SEGMENT_AABB_CANDIDATE_AND_"
            "CLOSED_OVERLAP_ENUMERATION"),
        "forward_raw_event_count": counts[0],
        "reverse_raw_event_count": counts[1],
        "raw_event_count": len(rows),
        "unique_event_count": len(set(rows)),
    }


def relation_k_plus_one_workload() -> dict[str, object]:
    """One static box, K+1 accepted rows, and one threshold sentinel.

    Each source lies inside the static box but away from its rising diagonal.
    The source-as-query traversal therefore emits one row per source, while the
    reverse traversal emits none.  One additional source has overlap 0.5 and
    must be rejected at threshold 1.0. Raw rows are exactly K+1 (< 2*K), so a raw
    storage cap cannot catch this case: the device unique-count gate must set
    status ``0xffff5102`` before any application-row D2H transfer.
    """

    max_u32 = (1 << 32) - 1
    sources = [[
        f32(0.125), f32(2.0), f32(1.125), f32(3.0), item_id]
        for item_id in range(RELATION_SIZE + 1)]
    # This sentinel intersects the forward traversal but has overlap 0.5.
    # It is rejected at the registered threshold 1.0 and accepted at 0.0,
    # making a threshold override change the raw/unique control counts.
    sentinel_source_id = RELATION_SIZE + 1
    sources.append([
        f32(0.125), f32(2.0), f32(0.625), f32(3.0),
        sentinel_source_id])
    indexed = [[
        f32(0.0), f32(0.0), f32(4.0), f32(4.0), max_u32]]
    minimum_overlap = f32(1.0)
    oracle = derive_relation_rows_cpu(indexed, sources, minimum_overlap)
    zero_threshold_oracle = derive_relation_rows_cpu(
        indexed, sources, f32(0.0))
    if oracle["forward_raw_event_count"] != RELATION_SIZE + 1 \
            or oracle["reverse_raw_event_count"] != 0 \
            or oracle["raw_event_count"] != RELATION_SIZE + 1 \
            or oracle["unique_event_count"] != RELATION_SIZE + 1 \
            or zero_threshold_oracle["raw_event_count"] != RELATION_SIZE + 2 \
            or zero_threshold_oracle["unique_event_count"] \
            != RELATION_SIZE + 2:
        raise RuntimeError("Goal5802 K+1 CPU oracle drift")
    oracle.update({
        "minimum_overlap_f32_bits": f32_bits(minimum_overlap),
        "sentinel_source_id": sentinel_source_id,
        "sentinel_overlap_f32_bits": f32_bits(0.5),
        "zero_threshold_raw_event_count": zero_threshold_oracle[
            "raw_event_count"],
        "zero_threshold_unique_event_count": zero_threshold_oracle[
            "unique_event_count"],
    })
    packed = bytearray(b"goal5802-relation-k-plus-one-v1\0")
    packed.extend(struct.pack("<II", len(indexed), len(sources)))
    packed.extend(struct.pack(
        "<fII", minimum_overlap, RELATION_SIZE, 2 * RELATION_SIZE))
    for row in (*indexed, *sources):
        lower_x, lower_y, upper_x, upper_y, item_id = row
        packed.extend(struct.pack(
            "<ffffffI", lower_x, lower_y, f32(0.0),
            upper_x, upper_y, f32(0.0), item_id))
    value: dict[str, object] = {
        "task": RELATION_TASK,
        "indexed": indexed,
        "sources": sources,
        "minimum_overlap_f32": minimum_overlap,
        "semantic_capacity": RELATION_SIZE,
        # The output must never be exposed.  This empty value exists only so
        # all three adapters can share the normal workload schema.
        "expected_rows": [],
        "expected_failure": {
            "raw_event_count": oracle["raw_event_count"],
            "unique_event_count": oracle["unique_event_count"],
            "overflowed": 1,
            "status": 0xFFFF5102,
            "semantic_capacity": RELATION_SIZE,
            "raw_capacity": 2 * RELATION_SIZE,
            "control_d2h_bytes": 16,
            "status_output_commit_blocking_boundary_count": 1,
            "application_output_exposed": False,
            "application_output_d2h_call_count": 0,
            "application_output_d2h_bytes": 0,
        },
        "oracle_derivation": oracle,
        "packed_input_sha256": hashlib.sha256(packed).hexdigest(),
    }
    value["workload_sha256"] = digest({
        key: item for key, item in value.items() if key != "workload_sha256"})
    return value


def triangle_workload() -> dict[str, object]:
    vertices: list[list[float]] = []
    queries: list[list[object]] = []
    weights: list[int] = []
    for query_id in range(TRIANGLE_SIZE):
        center = 3 * query_id
        vertices.extend([
            [f32(center - 1), f32(-1), f32(1)],
            [f32(center + 1), f32(-1), f32(1)],
            [f32(center), f32(1), f32(1)],
        ])
        queries.append([
            [f32(center), f32(0), f32(0)],
            [f32(0), f32(0), f32(1)],
            f32(2),
        ])
        weights.append(1 + query_id % 7)

    # The triangles occupy disjoint x intervals [3*i-1, 3*i+1].  Query i is
    # at x=3*i and travels in +z through z=1, so it has exactly one hit.  This
    # analytic construction is independent of all three executable routes.
    expected = sum(weights)
    if expected != 65530:
        raise RuntimeError("Goal5802 scalar oracle drift")
    return {
        "task": TRIANGLE_TASK,
        "vertices": vertices,
        "queries": queries,
        "weights": weights,
        "expected_reduced_u64": expected,
        "oracle_derivation": {
            "kind": "DISJOINT_INTEGER_X_INTERVALS__ONE_HIT_PER_QUERY",
            "triangle_i_x_interval": "[3*i-1,3*i+1]",
            "query_i_x": "3*i",
            "adjacent_interval_gap": 1,
            "reduction": "sum(weights[i] for i in range(16384))",
        },
    }


def workload_authority() -> dict[str, object]:
    relation = relation_workload()
    relation_k_plus_one = relation_k_plus_one_workload()
    triangle = triangle_workload()
    authority: dict[str, object] = {
        "schema": "rtdl.goal5802.scalar_only_workload_authority.v1",
        "status": "FROZEN_LOCAL_PREMEASUREMENT__ZERO_TIMINGS",
        "route_import_count": 0,
        "user_visible_output_contract": {
            RELATION_TASK: {
                "success_control": "device_status_ok",
                "product": "canonical_sorted_unique_u32_pair_rows",
            },
            TRIANGLE_TASK: {
                "success_control": "device_status_ok",
                "product": "one_checked_u64_scalar",
                "per_ray_host_output": False,
                "per_ray_d2h_bytes": 0,
                "per_ray_oracle_materialization": False,
            },
        },
        "relation": {
            "indexed_count": len(relation["indexed"]),
            "source_count": len(relation["sources"]),
            "semantic_capacity": relation["semantic_capacity"],
            "indexed_sha256": digest(relation["indexed"]),
            "sources_sha256": digest(relation["sources"]),
            "expected_rows_sha256": digest(relation["expected_rows"]),
            "expected_row_count": len(relation["expected_rows"]),
        },
        "relation_k_plus_one_device_failure_kat": {
            "indexed_count": len(relation_k_plus_one["indexed"]),
            "source_count": len(relation_k_plus_one["sources"]),
            "indexed_sha256": digest(relation_k_plus_one["indexed"]),
            "sources_sha256": digest(relation_k_plus_one["sources"]),
            "workload_sha256": relation_k_plus_one["workload_sha256"],
            "packed_input_sha256": relation_k_plus_one[
                "packed_input_sha256"],
            "minimum_overlap_f32": relation_k_plus_one[
                "minimum_overlap_f32"],
            "oracle_derivation": relation_k_plus_one["oracle_derivation"],
            "expected_failure": relation_k_plus_one["expected_failure"],
            "raw_count_below_raw_capacity": True,
            "route_import_count": 0,
        },
        "triangle": {
            "triangle_count": len(triangle["vertices"]) // 3,
            "query_count": len(triangle["queries"]),
            "vertices_sha256": digest(triangle["vertices"]),
            "queries_sha256": digest(triangle["queries"]),
            "weights_sha256": digest(triangle["weights"]),
            "expected_reduced_u64": triangle["expected_reduced_u64"],
            "expected_output_sha256": digest(
                triangle["expected_reduced_u64"]),
            "oracle_derivation": triangle["oracle_derivation"],
            "expected_per_ray_field_present": False,
        },
    }
    authority["authority_sha256"] = digest(authority)
    return authority
