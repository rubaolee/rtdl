#!/usr/bin/env python3
"""Analyze UCI 3DRoad AuthorOfficial/CPU-reference component differences.

This is an app-side diagnostic. It does not change RTDL core and does not claim
paper reproduction. The main question is whether the AuthorOfficial call-2
contract differs from a conventional DBSCAN border assignment reference.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import run_authorofficial_component_signature_gate as component_gate  # noqa: E402


def _read_points(path: Path) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    with path.open("r", newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if len(row) != 3:
                raise ValueError(f"expected 3 columns, got {len(row)}")
            points.append((float(row[0]), float(row[1]), float(row[2])))
    return points


def _neighborhoods(points: list[tuple[float, float, float]], epsilon: float) -> list[list[int]]:
    eps2 = float(epsilon) * float(epsilon)
    neighborhoods: list[list[int]] = [[] for _ in points]
    for i, (ix, iy, iz) in enumerate(points):
        for j, (jx, jy, jz) in enumerate(points):
            dx = jx - ix
            dy = jy - iy
            dz = jz - iz
            if dx * dx + dy * dy + dz * dz <= eps2 + 1e-12:
                neighborhoods[i].append(j)
    return neighborhoods


def _find(parent: list[int], item: int) -> int:
    while parent[item] != item:
        parent[item] = parent[parent[item]]
        item = parent[item]
    return item


def _union_min_root(parent: list[int], left: int, right: int) -> None:
    left_root = _find(parent, left)
    right_root = _find(parent, right)
    if left_root == right_root:
        return
    if left_root < right_root:
        parent[right_root] = left_root
    else:
        parent[left_root] = right_root


def _labels_from_roots(parent: list[int], core_flags: list[int]) -> list[int]:
    roots = [_find(parent, i) for i in range(len(parent))]
    root_has_core = [False] * len(parent)
    for i, is_core in enumerate(core_flags):
        if is_core:
            root_has_core[roots[i]] = True

    root_to_label: dict[int, int] = {}
    labels = [-1] * len(parent)
    for i, root in enumerate(roots):
        if not root_has_core[root]:
            continue
        if root not in root_to_label:
            root_to_label[root] = len(root_to_label)
        labels[i] = root_to_label[root]
    return labels


def conventional_labels(neighborhoods: list[list[int]], core_flags: list[int]) -> list[int]:
    parent = list(range(len(neighborhoods)))
    for point_id, neighbors in enumerate(neighborhoods):
        if not core_flags[point_id]:
            continue
        for neighbor_id in neighbors:
            if core_flags[neighbor_id]:
                _union_min_root(parent, point_id, neighbor_id)
    for point_id, neighbors in enumerate(neighborhoods):
        if core_flags[point_id]:
            continue
        core_roots = [_find(parent, n) for n in neighbors if core_flags[n]]
        if core_roots:
            parent[point_id] = min(core_roots)
    return _labels_from_roots(parent, core_flags)


def author_directional_labels(neighborhoods: list[list[int]], core_flags: list[int]) -> list[int]:
    """Deterministic approximation of the author call-2 contract.

    deviceCode.cu only acts for intersections where xID > primID and xID is
    core. If primID is core, the roots are unioned toward the smaller root. If
    primID is non-core, primID.parent is set to xID's current root. Thus a
    border point can only be absorbed by a higher-index core neighbor.
    """

    parent = list(range(len(neighborhoods)))
    for x_id, neighbors in enumerate(neighborhoods):
        if not core_flags[x_id]:
            continue
        for prim_id in neighbors:
            if x_id <= prim_id:
                continue
            if core_flags[prim_id]:
                _union_min_root(parent, x_id, prim_id)
            else:
                parent[prim_id] = _find(parent, x_id)
    return _labels_from_roots(parent, core_flags)


def _signature(labels: list[int], core_flags: list[int]) -> dict[str, object]:
    return component_gate._canonical_signature_from_labels(
        component_gate._canonical_partition_labels(labels),
        core_count=sum(core_flags),
    )


def analyze(
    *,
    input_path: Path,
    author_output: Path,
    epsilon: float,
    min_points: int,
) -> dict[str, object]:
    points = _read_points(input_path)
    neighborhoods = _neighborhoods(points, epsilon)
    core_flags = [1 if len(n) >= int(min_points) else 0 for n in neighborhoods]
    author_payload = json.loads(author_output.read_text(encoding="utf-8").splitlines()[-1])
    author_partition = component_gate._author_component_partition(author_payload)
    author_labels = list(author_partition["canonical_component_labels"])

    conventional = component_gate._canonical_partition_labels(conventional_labels(neighborhoods, core_flags))
    directional = component_gate._canonical_partition_labels(author_directional_labels(neighborhoods, core_flags))

    def mismatch_indexes(labels: list[int]) -> list[int]:
        return [i for i, (a, b) in enumerate(zip(author_labels, labels)) if a != b]

    conventional_mismatches = mismatch_indexes(conventional)
    directional_mismatches = mismatch_indexes(directional)
    author_noise_conventional_cluster = [
        i for i in conventional_mismatches if author_labels[i] == -1 and conventional[i] != -1
    ]
    directional_border_candidates = [
        {
            "point_id": i,
            "core_neighbor_count": sum(core_flags[n] for n in neighborhoods[i]),
            "higher_index_core_neighbor_count": sum(1 for n in neighborhoods[i] if core_flags[n] and n > i),
            "lower_index_core_neighbor_count": sum(1 for n in neighborhoods[i] if core_flags[n] and n < i),
        }
        for i in author_noise_conventional_cluster[:32]
    ]
    return {
        "schema": "rtdl.paper_reproduction.rt_dbscan.uci_3droad_contract_mismatch_analysis.v1",
        "status": "diagnostic_only_not_paper_reproduction",
        "input": str(input_path),
        "author_output": str(author_output),
        "epsilon": float(epsilon),
        "min_points": int(min_points),
        "point_count": len(points),
        "core_count": sum(core_flags),
        "author_signature": author_partition["signature"],
        "conventional_signature": _signature(conventional, core_flags),
        "author_directional_signature": _signature(directional, core_flags),
        "conventional_mismatch_count": len(conventional_mismatches),
        "author_directional_mismatch_count": len(directional_mismatches),
        "author_noise_conventional_cluster_count": len(author_noise_conventional_cluster),
        "first_author_noise_conventional_cluster_points": directional_border_candidates,
        "contract_hypothesis": (
            "Author call-2 can attach a non-core point only when the current ray "
            "xID is a higher-index core neighbor (xID > primID). A conventional "
            "DBSCAN reference attaches a border point to any core neighbor. "
            "This index-order-sensitive border rule is a plausible cause of the "
            "same-source 3DRoad component mismatch."
        ),
        "claim_boundary": (
            "Diagnostic app-side contract analysis only; not a clean AuthorOfficial "
            "gate, not exact paper data, not an RTDL core semantic."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--author-output", type=Path, required=True)
    parser.add_argument("--epsilon", type=float, required=True)
    parser.add_argument("--min-points", type=int, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(
        input_path=args.input,
        author_output=args.author_output,
        epsilon=args.epsilon,
        min_points=args.min_points,
    )
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
