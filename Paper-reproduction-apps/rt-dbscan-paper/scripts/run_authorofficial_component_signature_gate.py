from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import run_authorofficial_core_count_gate as core_gate
import rtdsl as rt


ROOT = core_gate.ROOT
DEFAULT_INPUT = core_gate.DEFAULT_INPUT


def _canonical_signature_from_labels(
    labels: list[int],
    *,
    core_count: int,
) -> dict[str, object]:
    return rt.component_signature_from_partition(labels, core_count=core_count)


def _canonical_partition_labels(labels: list[int]) -> list[int]:
    return list(rt.canonical_partition_labels(labels))


def _cpu_reference_component_result(
    points: tuple[tuple[float, float, float], ...],
    *,
    epsilon: float,
    min_points: int,
) -> dict[str, object]:
    radius_sq = float(epsilon) * float(epsilon)
    point_count = len(points)
    neighborhoods: list[list[int]] = [[] for _ in range(point_count)]
    for query_id, (qx, qy, qz) in enumerate(points):
        for neighbor_id, (sx, sy, sz) in enumerate(points):
            dx = sx - qx
            dy = sy - qy
            dz = sz - qz
            if dx * dx + dy * dy + dz * dz <= radius_sq + 1e-12:
                neighborhoods[query_id].append(neighbor_id)

    core_flags = [len(neighbors) >= int(min_points) for neighbors in neighborhoods]
    parent = list(range(point_count))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            parent[right_root] = left_root
        else:
            parent[left_root] = right_root

    for point_id, neighbors in enumerate(neighborhoods):
        if not core_flags[point_id]:
            continue
        for neighbor_id in neighbors:
            if core_flags[neighbor_id]:
                union(point_id, neighbor_id)

    root_to_label: dict[int, int] = {}
    labels: list[int] = [-1] * point_count
    for point_id, neighbors in enumerate(neighborhoods):
        candidate_roots: list[int] = []
        if core_flags[point_id]:
            candidate_roots.append(find(point_id))
        else:
            for neighbor_id in neighbors:
                if core_flags[neighbor_id]:
                    candidate_roots.append(find(neighbor_id))
        if not candidate_roots:
            labels[point_id] = -1
            continue
        root = min(candidate_roots)
        if root not in root_to_label:
            root_to_label[root] = len(root_to_label)
        labels[point_id] = root_to_label[root]

    signature = _canonical_signature_from_labels(
        labels,
        core_count=sum(1 for is_core in core_flags if is_core),
    )
    return {
        "backend": "cpu_reference",
        "component_labels": labels,
        "canonical_component_labels": _canonical_partition_labels(labels),
        "core_flags": [1 if is_core else 0 for is_core in core_flags],
        "signature": signature,
        "metadata": {
            "native_engine_row_contract": "not_called_cpu_reference_only",
            "component_partition_contract": "cpu_reference_fixed_radius_dbscan_partition_3d",
            "component_signature_contract": "cpu_reference_fixed_radius_dbscan_signature_from_partition_3d",
            "rt_core_accelerated": False,
        },
    }


def _neighborhoods(
    points: tuple[tuple[float, float, float], ...],
    *,
    epsilon: float,
) -> list[list[int]]:
    radius_sq = float(epsilon) * float(epsilon)
    neighborhoods: list[list[int]] = [[] for _ in range(len(points))]
    for query_id, (qx, qy, qz) in enumerate(points):
        for neighbor_id, (sx, sy, sz) in enumerate(points):
            dx = sx - qx
            dy = sy - qy
            dz = sz - qz
            if dx * dx + dy * dy + dz * dz <= radius_sq + 1e-12:
                neighborhoods[query_id].append(neighbor_id)
    return neighborhoods


def _author_directional_component_result(
    points: tuple[tuple[float, float, float], ...],
    *,
    epsilon: float,
    min_points: int,
) -> dict[str, object]:
    """App-side reference for the pinned AuthorOfficial call-2 contract.

    This is intentionally not a generic RTDL primitive. The pinned author kernel
    only processes call-2 intersections when ``xID > primID``. A non-core point
    can therefore be absorbed as a border point only through a higher-index core
    neighbor. Goal5107 showed this contract explains the UCI 3DRoad 1K mismatch
    against a conventional DBSCAN reference.
    """

    neighborhoods = _neighborhoods(points, epsilon=epsilon)
    core_flags = [len(neighbors) >= int(min_points) for neighbors in neighborhoods]
    parent = list(range(len(points)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            parent[right_root] = left_root
        else:
            parent[left_root] = right_root

    for x_id, neighbors in enumerate(neighborhoods):
        if not core_flags[x_id]:
            continue
        for prim_id in neighbors:
            if x_id <= prim_id:
                continue
            if core_flags[prim_id]:
                union(x_id, prim_id)
            else:
                parent[prim_id] = find(x_id)

    roots = [find(i) for i in range(len(points))]
    root_has_core = [False] * len(points)
    for point_id, is_core in enumerate(core_flags):
        if is_core:
            root_has_core[roots[point_id]] = True

    root_to_label: dict[int, int] = {}
    labels: list[int] = [-1] * len(points)
    for point_id, root in enumerate(roots):
        if not root_has_core[root]:
            continue
        if root not in root_to_label:
            root_to_label[root] = len(root_to_label)
        labels[point_id] = root_to_label[root]

    canonical_labels = _canonical_partition_labels(labels)
    core_values = [1 if is_core else 0 for is_core in core_flags]
    signature = _canonical_signature_from_labels(canonical_labels, core_count=sum(core_values))
    return {
        "backend": "author_directional_cpu_reference",
        "component_labels": labels,
        "canonical_component_labels": canonical_labels,
        "core_flags": core_values,
        "signature": signature,
        "metadata": {
            "native_engine_row_contract": "not_called_app_side_author_contract_reference_only",
            "component_partition_contract": "app_side_author_directional_border_assignment_reference_3d",
            "component_signature_contract": "author_directional_fixed_radius_dbscan_signature_from_partition_3d",
            "border_assignment_policy": "author_call2_xid_greater_than_primid_only",
            "rt_core_accelerated": False,
            "claim_boundary": (
                "App-owned comparator for pinned AuthorOfficial behavior; not a generic RTDL core semantic "
                "and not conventional DBSCAN."
            ),
        },
    }


def _rtdl_optix_numba_component_signature(
    points: tuple[tuple[float, float, float], ...],
    *,
    epsilon: float,
    min_points: int,
) -> dict[str, object]:
    import numpy as np
    rtdl_points = core_gate._to_rtdl_points(points)
    prepared = rt.prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
        rtdl_points,
        radius=epsilon,
        partner="numba",
    )
    try:
        result = rt.radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
            prepared,
            min_neighbors=int(min_points),
            return_metadata=True,
        )
    finally:
        prepared.close()

    columns = result["columns"]
    point_ids = np.asarray(columns["point_ids"].copy_to_host(), dtype=np.int64)
    raw_labels_by_row = np.asarray(columns["component_labels"].copy_to_host(), dtype=np.int64)
    core_flags_by_row = np.asarray(columns["is_core"].copy_to_host(), dtype=np.int64)
    labels = [-1] * len(points)
    core_flags = [0] * len(points)
    for row_index, point_id in enumerate(point_ids.tolist()):
        point_id = int(point_id)
        labels[point_id] = int(raw_labels_by_row[row_index])
        core_flags[point_id] = 1 if int(core_flags_by_row[row_index]) else 0
    canonical_labels = _canonical_partition_labels(labels)
    signature = _canonical_signature_from_labels(
        canonical_labels,
        core_count=sum(core_flags),
    )
    return {
        "backend": "optix_numba_component_signature",
        "component_labels": labels,
        "canonical_component_labels": canonical_labels,
        "core_flags": core_flags,
        "signature": signature,
        "metadata": dict(result["metadata"]),
    }


def _rtdl_optix_cupy_component_signature(
    points: tuple[tuple[float, float, float], ...],
    *,
    epsilon: float,
    min_points: int,
) -> dict[str, object]:
    import cupy
    rtdl_points = core_gate._to_rtdl_points(points)
    prepared = rt.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
        rtdl_points,
        radius=epsilon,
        partner="cupy",
    )
    try:
        result = rt.radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns(
            prepared,
            min_neighbors=int(min_points),
            return_metadata=True,
        )
    finally:
        prepared.close()

    columns = result["columns"]
    point_ids = cupy.asnumpy(columns["point_ids"]).astype("int64", copy=False)
    raw_labels_by_row = cupy.asnumpy(columns["component_labels"]).astype("int64", copy=False)
    core_flags_by_row = cupy.asnumpy(columns["is_core"]).astype("int64", copy=False)
    labels = [-1] * len(points)
    core_flags = [0] * len(points)
    for row_index, point_id in enumerate(point_ids.tolist()):
        point_id = int(point_id)
        labels[point_id] = int(raw_labels_by_row[row_index])
        core_flags[point_id] = 1 if int(core_flags_by_row[row_index]) else 0
    canonical_labels = _canonical_partition_labels(labels)
    signature = _canonical_signature_from_labels(
        canonical_labels,
        core_count=sum(core_flags),
    )
    return {
        "backend": "optix_cupy_component_signature",
        "component_labels": labels,
        "canonical_component_labels": canonical_labels,
        "core_flags": core_flags,
        "signature": signature,
        "metadata": dict(result["metadata"]),
    }


def _rtdl_component_result(
    points: tuple[tuple[float, float, float], ...],
    *,
    epsilon: float,
    min_points: int,
    backend: str,
) -> dict[str, object]:
    if backend == "cpu_reference":
        return _cpu_reference_component_result(points, epsilon=epsilon, min_points=min_points)
    if backend == "author_directional_cpu_reference":
        return _author_directional_component_result(points, epsilon=epsilon, min_points=min_points)
    if backend == "optix_numba_component_signature":
        return _rtdl_optix_numba_component_signature(points, epsilon=epsilon, min_points=min_points)
    if backend == "optix_cupy_component_signature":
        return _rtdl_optix_cupy_component_signature(points, epsilon=epsilon, min_points=min_points)
    raise ValueError(
        "backend must be cpu_reference, author_directional_cpu_reference, "
        "optix_numba_component_signature, or optix_cupy_component_signature"
    )


def _author_component_partition(author_payload: dict[str, object]) -> dict[str, object]:
    required = ("component_labels", "component_sizes", "noise_count", "core_count")
    missing = [key for key in required if key not in author_payload]
    if missing:
        raise ValueError(f"AuthorOfficial payload is missing component partition fields: {missing}")
    raw_labels = [int(value) for value in author_payload["component_labels"]]
    canonical_labels = _canonical_partition_labels(raw_labels)
    core_flags = [int(value) for value in author_payload.get("core_flags", [])]
    if core_flags and len(core_flags) != len(raw_labels):
        raise ValueError("AuthorOfficial core_flags length does not match component_labels length")
    component_sizes = sorted(int(value) for value in author_payload["component_sizes"])
    signature = _canonical_signature_from_labels(
        canonical_labels,
        core_count=int(author_payload["core_count"]),
    )
    payload_signature = {
        "core_count": int(author_payload["core_count"]),
        "component_count": len(component_sizes),
        "component_sizes": component_sizes,
        "noise_count": int(author_payload["noise_count"]),
    }
    if payload_signature != signature:
        raise ValueError(
            "AuthorOfficial component_labels do not match its component signature fields: "
            f"{signature} != {payload_signature}"
        )
    return {
        "component_labels": raw_labels,
        "canonical_component_labels": canonical_labels,
        "core_flags": core_flags,
        "signature": signature,
    }


def _run_author(
    author_binary: Path,
    input_path: Path,
    *,
    size: int,
    epsilon: float,
    min_points: int,
    output_path: Path,
) -> dict[str, object]:
    return core_gate._run_author(
        author_binary,
        input_path,
        size=size,
        epsilon=epsilon,
        min_points=min_points,
        output_path=output_path,
    )


def run_gate(
    *,
    input_path: Path,
    epsilon: float,
    min_points: int,
    backend: str,
    author_binary: Path | None = None,
    author_output: Path | None = None,
    author_payload_path: Path | None = None,
) -> dict[str, object]:
    points = core_gate._read_points(input_path)
    rtdl_result = _rtdl_component_result(points, epsilon=epsilon, min_points=min_points, backend=backend)
    author_payload = None
    author_partition = None
    if author_payload_path is not None:
        author_payload = json.loads(author_payload_path.read_text(encoding="utf-8").splitlines()[-1])
        author_partition = _author_component_partition(author_payload)
    elif author_binary is not None:
        output_path = author_output
        if output_path is None:
            tmp = tempfile.NamedTemporaryFile(prefix="rt_dbscan_author_component_signature_", suffix=".jsonl", delete=False)
            tmp.close()
            output_path = Path(tmp.name)
        author_payload = _run_author(
            author_binary,
            input_path,
            size=len(points),
            epsilon=epsilon,
            min_points=min_points,
            output_path=output_path,
        )
        author_partition = _author_component_partition(author_payload)

    matched = None
    signature_matched = None
    component_partition_matched = None
    core_flags_matched = None
    if author_partition is not None:
        signature_matched = author_partition["signature"] == rtdl_result["signature"]
        component_partition_matched = (
            author_partition["canonical_component_labels"] == rtdl_result.get("canonical_component_labels")
        )
        author_core_flags = author_partition.get("core_flags", [])
        core_flags_matched = None if not author_core_flags else author_core_flags == rtdl_result.get("core_flags")
        matched = bool(signature_matched and component_partition_matched and (core_flags_matched is not False))

    return {
        "schema": "rtdl.paper_reproduction.rt_dbscan.authorofficial_component_partition_gate.v2",
        "paper_app": "rt-dbscan-paper",
        "input_path": str(input_path),
        "point_count": len(points),
        "epsilon": float(epsilon),
        "min_points": int(min_points),
        "rtdl": rtdl_result,
        "author": author_payload,
        "author_partition": author_partition,
        "author_signature": None if author_partition is None else author_partition["signature"],
        "author_comparator_used": author_payload is not None,
        "signature_matched": signature_matched,
        "component_partition_matched": component_partition_matched,
        "core_flags_matched": core_flags_matched,
        "matched": matched,
        "bounded_component_signature_reproduction_claim_authorized": bool(author_payload is not None and signature_matched),
        "bounded_component_partition_reproduction_claim_authorized": bool(author_payload is not None and matched),
        "paper_reproduction_claim_authorized": False,
        "whole_program_speedup_claim_authorized": False,
        "performance_claim_authorized": False,
        "boundary": (
            "Bounded same-input RT-DBSCAN component-partition comparator gate. "
            "It compares canonical point partitions modulo component-label renaming, "
            "plus core_count, component_sizes, noise_count, and core_flags when the "
            "AuthorOfficial payload provides them. It does not claim exact author "
            "label IDs, exact paper datasets, full DBSCAN output format, or performance."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RT-DBSCAN AuthorOfficial component-signature comparator gate.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--epsilon", type=float, default=0.35)
    parser.add_argument("--min-points", type=int, default=3)
    parser.add_argument(
        "--backend",
        choices=(
            "cpu_reference",
            "author_directional_cpu_reference",
            "optix_numba_component_signature",
            "optix_cupy_component_signature",
        ),
        default="cpu_reference",
    )
    parser.add_argument("--author-binary", type=Path, default=None)
    parser.add_argument("--author-output", type=Path, default=None)
    parser.add_argument("--author-payload", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    args = parser.parse_args(argv)

    summary = run_gate(
        input_path=args.input,
        epsilon=args.epsilon,
        min_points=args.min_points,
        backend=args.backend,
        author_binary=args.author_binary,
        author_output=args.author_output,
        author_payload_path=args.author_payload,
    )
    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(text + "\n", encoding="utf-8")
    print(text)
    if summary["author_comparator_used"] and not summary["matched"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
