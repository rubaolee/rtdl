from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable


PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_VERSION = "rtdl.predicate_aware_boundary_union.reference.v1"
PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_STATUS = "reference_contract_candidate_not_promoted"
PREDICATE_AWARE_BOUNDARY_UNION_POLICIES = ("lowest_component_root",)


def predicate_aware_boundary_union_reference(
    *,
    point_count: int,
    candidate_pairs: Iterable[tuple[int, int]],
    predicate_flags: Iterable[bool],
    boundary_assignment_policy: str = "lowest_component_root",
) -> dict[str, object]:
    """Reference contract for generic predicate-aware fixed-radius components.

    Predicate meaning is caller-owned. RTDL sees only boolean flags, candidate
    pairs, component roots, and deterministic boundary assignment metadata.
    """

    resolved_point_count = int(point_count)
    if resolved_point_count < 0:
        raise ValueError("point_count must be non-negative")
    if boundary_assignment_policy not in PREDICATE_AWARE_BOUNDARY_UNION_POLICIES:
        raise ValueError(
            "boundary_assignment_policy must be one of "
            f"{PREDICATE_AWARE_BOUNDARY_UNION_POLICIES!r}"
        )

    flags = tuple(bool(flag) for flag in predicate_flags)
    if len(flags) != resolved_point_count:
        raise ValueError("predicate_flags length must match point_count")
    pairs = tuple((int(left), int(right)) for left, right in candidate_pairs)
    for left, right in pairs:
        if left < 0 or right < 0 or left >= resolved_point_count or right >= resolved_point_count:
            raise ValueError("candidate pair index out of range")

    parent = list(range(resolved_point_count))
    def find(item: int) -> int:
        root = item
        while parent[root] != root:
            root = parent[root]
        while parent[item] != item:
            next_item = parent[item]
            parent[item] = root
            item = next_item
        return root

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        lower_root = min(left_root, right_root)
        higher_root = max(left_root, right_root)
        parent[higher_root] = lower_root

    true_true_pair_count = 0
    boundary_pair_count = 0
    ignored_false_false_pair_count = 0
    for left, right in pairs:
        left_true = flags[left]
        right_true = flags[right]
        if left_true and right_true:
            union(left, right)
            true_true_pair_count += 1
        elif left_true or right_true:
            boundary_pair_count += 1
        else:
            ignored_false_false_pair_count += 1

    boundary_candidate_roots: dict[int, set[int]] = defaultdict(set)
    for left, right in pairs:
        left_true = flags[left]
        right_true = flags[right]
        if left_true and not right_true:
            boundary_candidate_roots[right].add(find(left))
        elif right_true and not left_true:
            boundary_candidate_roots[left].add(find(right))

    labels: list[int] = [-1] * resolved_point_count
    for item, flag in enumerate(flags):
        if flag:
            labels[item] = find(item)
    for item, roots in boundary_candidate_roots.items():
        if not flags[item] and roots:
            labels[item] = min(roots)

    component_counts = Counter(label for label in labels if label >= 0)
    predicate_true_count = sum(1 for flag in flags if flag)
    assigned_count = sum(1 for label in labels if label >= 0)
    boundary_assigned_count = sum(1 for index, label in enumerate(labels) if label >= 0 and not flags[index])
    unassigned_count = resolved_point_count - assigned_count

    return {
        "contract": PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_VERSION,
        "status": PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_STATUS,
        "point_count": resolved_point_count,
        "candidate_pair_count": len(pairs),
        "true_true_pair_count": true_true_pair_count,
        "boundary_pair_count": boundary_pair_count,
        "ignored_false_false_pair_count": ignored_false_false_pair_count,
        "predicate_true_count": predicate_true_count,
        "assigned_count": assigned_count,
        "boundary_assigned_count": boundary_assigned_count,
        "unassigned_count": unassigned_count,
        "component_count": len(component_counts),
        "component_sizes": tuple(sorted(component_counts.values())),
        "component_labels": tuple(labels),
        "boundary_candidate_component_counts": tuple(
            sorted((item, len(roots)) for item, roots in boundary_candidate_roots.items())
        ),
        "boundary_assignment_policy": boundary_assignment_policy,
        "policy_metadata": {
            "predicate_meaning": "caller_owned",
            "boundary_assignment_policy": boundary_assignment_policy,
            "component_size_contract_requires_policy": True,
            "counts_only_contract_available": True,
            "native_engine_app_specific_logic": False,
            "route_promotion_authorized": False,
        },
    }


__all__ = [
    "PREDICATE_AWARE_BOUNDARY_UNION_POLICIES",
    "PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_STATUS",
    "PREDICATE_AWARE_BOUNDARY_UNION_REFERENCE_VERSION",
    "predicate_aware_boundary_union_reference",
]
