"""Non-paper consumer of the generic fixed-radius component compiler route."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
for path in (ROOT, ROOT / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rtdsl.action_api import compile_action_source, detect_action_target_profile
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_ir import (
    F32,
    U32,
    ActionEmitSpec,
    ActionField,
    ActionRecordType,
    CapacityExtent,
    CapacityMul,
    DeliveryEnforcement,
    DuplicatePolicy,
    ExtentKind,
    LogicalEventContract,
    OrderKey,
    OrderKeyRole,
    OutputOrderKind,
    PhysicalDelivery,
)
from rtdsl.fixed_radius_graph_compiler import (
    execute_registered_fixed_radius_graph_components_3d,
    plan_registered_fixed_radius_graph_components_3d,
    prepare_registered_fixed_radius_graph_context,
)


ACTION_SOURCE = """
def action(event, params):
    source = event.source_id
    target = event.target_id
    distance_sq = event.distance_sq
    radius_sq = params.radius_sq
    eligible = distance_sq <= radius_sq
    require(eligible)
    emit("edges", source, target)
"""


def action_contract() -> RestrictedActionFrontendContract:
    event_type = ActionRecordType(
        "distance_candidate",
        (
            ActionField("source_id", U32),
            ActionField("target_id", U32),
            ActionField("distance_sq", F32),
        ),
    )
    parameter_type = ActionRecordType(
        "parameters", (ActionField("radius_sq", F32),)
    )
    edge_type = ActionRecordType(
        "edge_row",
        (ActionField("source_id", U32), ActionField("target_id", U32)),
    )
    return RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=parameter_type,
        logical_event=LogicalEventContract(
            key_fields=("source_id", "target_id"),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="prepared-index-single-delivery-contract-v1",
        ),
        emits=(
            ActionEmitSpec(
                "edges",
                edge_type,
                CapacityMul(
                    CapacityExtent(ExtentKind.QUERY_COUNT),
                    CapacityExtent(ExtentKind.PRIMITIVE_COUNT),
                ),
                OutputOrderKind.CANONICAL_ORDER,
                (
                    OrderKey("source_id"),
                    OrderKey("target_id", role=OrderKeyRole.ITEM_ID),
                ),
                DuplicatePolicy.STABLE_ITEM_ID,
            ),
        ),
    )


def _independent_partition(
    points: np.ndarray,
    *,
    radius: float,
    min_neighbors: int,
) -> dict[str, list[object]]:
    points = np.ascontiguousarray(points, dtype=np.float32)
    radius_f32 = np.float32(radius)
    radius_sq = np.multiply(radius_f32, radius_f32, dtype=np.float32)
    neighbors: list[list[int]] = []
    for source in points:
        row = []
        for target_id, target in enumerate(points):
            delta = np.subtract(source, target, dtype=np.float32)
            squared = np.multiply(delta, delta, dtype=np.float32)
            distance_sq = np.add(
                squared[0], squared[1], dtype=np.float32
            )
            if points.shape[1] == 3:
                distance_sq = np.add(
                    distance_sq, squared[2], dtype=np.float32
                )
            if distance_sq <= radius_sq:
                row.append(target_id)
        neighbors.append(row)
    core = [len(row) >= min_neighbors for row in neighbors]
    parent = list(range(len(points)))

    def find(item: int) -> int:
        root = item
        while parent[root] != root:
            root = parent[root]
        while parent[item] != item:
            following = parent[item]
            parent[item] = root
            item = following
        return root

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    for source_id, targets in enumerate(neighbors):
        if not core[source_id]:
            continue
        for target_id in targets:
            if core[target_id]:
                union(source_id, target_id)
    labels = [-1] * len(points)
    for point_id, is_core in enumerate(core):
        if is_core:
            labels[point_id] = find(point_id)
        else:
            roots = {
                find(target_id)
                for target_id in neighbors[point_id]
                if core[target_id]
            }
            if roots:
                labels[point_id] = min(roots)
    canonical: dict[int, int] = {}
    canonical_labels = []
    for label in labels:
        if label < 0:
            canonical_labels.append(-1)
        else:
            canonical.setdefault(label, len(canonical))
            canonical_labels.append(canonical[label])
    return {
        "canonical_component_labels": canonical_labels,
        "core_flags": core,
    }


def run() -> dict[str, object]:
    batches = (
        {
            "id": "nx2_exact_endpoint_duplicates_all_core",
            "points": np.asarray(
                (
                    (0.0, 0.0),
                    (0.0, 0.0),
                    (1.0, 0.0),
                    (5.0, 0.0),
                    (6.0, 0.0),
                    (20.0, 0.0),
                ),
                dtype=np.float32,
            ),
            "radius": 1.0,
            "min_neighbors": 2,
        },
        {
            "id": "nx3_core_border_noise",
            "points": np.asarray(
                (
                    (0.0, 0.0, 0.0),
                    (0.2, 0.0, 0.0),
                    (0.4, 0.0, 0.0),
                    (0.8, 0.0, 0.0),
                    (4.0, 0.0, 0.0),
                    (4.2, 0.0, 0.0),
                    (10.0, 0.0, 0.0),
                ),
                dtype=np.float32,
            ),
            "radius": 0.45,
            "min_neighbors": 3,
        },
    )
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    target = detect_action_target_profile(cpu_reference_available=False)
    context = prepare_registered_fixed_radius_graph_context(compiled, target)
    context_metadata = context.to_metadata()
    results = []
    try:
        for batch in batches:
            points = np.ascontiguousarray(batch["points"], dtype=np.float32)
            expected = _independent_partition(
                points,
                radius=float(batch["radius"]),
                min_neighbors=int(batch["min_neighbors"]),
            )
            plan = plan_registered_fixed_radius_graph_components_3d(
                compiled,
                target,
                points=points,
                radius=float(batch["radius"]),
                min_neighbors=int(batch["min_neighbors"]),
                prepared_context=context,
            )
            execution = execute_registered_fixed_radius_graph_components_3d(
                plan,
                points=points,
                radius=float(batch["radius"]),
                min_neighbors=int(batch["min_neighbors"]),
            )
            actual = {
                "canonical_component_labels": [
                    int(item)
                    for item in execution["actual"][
                        "canonical_component_labels"
                    ]
                ],
                "core_flags": [
                    bool(item) for item in execution["actual"]["core_flags"]
                ],
            }
            route = execution["route_metadata"]["route"]
            count_symbol = route["count_metadata"]["native_metadata"][
                "native_symbol"
            ]
            union_symbol = route["native_grouped_stream_metadata"][
                "native_symbol"
            ]
            results.append(
                {
                    "id": batch["id"],
                    "point_count": len(points),
                    "dimension": int(points.shape[1]),
                    "radius": float(batch["radius"]),
                    "min_neighbors": int(batch["min_neighbors"]),
                    "matched_independent_oracle": actual == expected,
                    "actual": actual,
                    "expected": expected,
                    "selected_producer_kind": execution[
                        "selected_producer_kind"
                    ],
                    "selected_backend": execution["selected_backend"],
                    "count_native_symbol": count_symbol,
                    "grouped_union_native_symbol": union_symbol,
                    "compiler_plan": execution["compiler_plan"],
                    "invocation_receipt": execution["invocation_receipt"],
                }
            )
    finally:
        context.close()
    context_digests = {
        row["compiler_plan"]["prepared_context_identity_digest"]
        for row in results
    }
    input_digests = {
        row["compiler_plan"]["input_digest"] for row in results
    }
    parameter_digests = {
        row["compiler_plan"]["parameter_digest"] for row in results
    }
    return {
        "schema": (
            "rtdl.research.goal5652."
            "thresholded_proximity_components_second_consumer.v1"
        ),
        "status": "pass" if all(
            row["matched_independent_oracle"] for row in results
        ) else "fail",
        "consumer": "non_paper_thresholded_proximity_components",
        "batch_count": len(results),
        "same_static_context_reused": len(context_digests) == 1,
        "distinct_dynamic_inputs_bound": len(input_digests) == len(results),
        "distinct_dynamic_parameters_bound": (
            len(parameter_digests) == len(results)
        ),
        "static_context": {
            "identity_digest": context_metadata["identity_digest"],
            "evidence_digest": context_metadata["refinement_evidence"][
                "artifact_sha256"
            ],
            "full_static_metadata_serialization_per_batch": context_metadata[
                "full_static_metadata_serialization_per_batch"
            ],
        },
        "batches": results,
        "paper_performance_claimed": False,
        "public_release_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run()
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(args.output),
                "batch_count": payload["batch_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
