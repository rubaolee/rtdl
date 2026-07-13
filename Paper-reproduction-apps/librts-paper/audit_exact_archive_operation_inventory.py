from __future__ import annotations

import argparse
import json
import re
import tarfile
from pathlib import Path


SCHEMA = "rtdl.paper_reproduction.librts.exact_archive_operation_inventory.v1"
OPERATION_PATTERNS = {
    "point_contains": ("point-contains_queries_", "point_contains"),
    "range_contains": ("range-contains_queries_", "range_contains"),
    "range_intersects": ("range-intersects_select_", "range_intersects"),
    "pip": ("pip", "point-in-polygon", "point_in_polygon"),
    "mutation": ("insertion_batch", "deletion_batch", "point-contains_update", "update_batch"),
}
QUERY_MARKERS = ("/datasets/queries/", "\\datasets\\queries\\")
GEOMETRY_MARKERS = ("/datasets/polygons/", "\\datasets\\polygons\\")


def _relative_member(name: str) -> str:
    return name.replace("\\", "/").lstrip("./")


def _operation_hits(path: str) -> list[str]:
    lowered = path.lower()
    return [
        operation
        for operation, patterns in OPERATION_PATTERNS.items()
        if any(pattern in lowered for pattern in patterns)
    ]


def audit_archive(*, archive_path: Path, archive_result: dict[str, object]) -> dict[str, object]:
    if not archive_result.get("claim_boundary", {}).get("archive_verified", False):
        raise ValueError("operation inventory requires a verified archive result")
    if not archive_path.is_file():
        raise FileNotFoundError(archive_path)
    geometry_members: list[str] = []
    query_members: list[str] = []
    operation_members: dict[str, list[str]] = {name: [] for name in OPERATION_PATTERNS}
    member_count = 0
    total_bytes = 0
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            name = _relative_member(member.name)
            member_count += 1
            total_bytes += int(member.size)
            lowered = name.lower()
            if any(marker in lowered for marker in GEOMETRY_MARKERS):
                geometry_members.append(name)
            if any(marker in lowered for marker in QUERY_MARKERS):
                query_members.append(name)
            for operation in _operation_hits(name):
                operation_members[operation].append(name)

    geometry_by_basename = {Path(name).name: name for name in geometry_members}
    exact_pairs: dict[str, list[dict[str, str]]] = {name: [] for name in OPERATION_PATTERNS}
    for operation, members in operation_members.items():
        for query in members:
            basename = Path(query).name
            geometry = geometry_by_basename.get(basename)
            if geometry is not None:
                exact_pairs[operation].append({"geometry": geometry, "query": query})

    return {
        "schema": SCHEMA,
        "status": "verified_archive_operation_inventory_complete",
        "archive": {
            "path": str(archive_path.resolve()),
            "verified_result_path": archive_result.get("verification", {}).get("path"),
            "size_bytes": archive_path.stat().st_size,
        },
        "inventory": {
            "regular_file_member_count": member_count,
            "regular_file_total_bytes": total_bytes,
            "geometry_member_count": len(geometry_members),
            "query_member_count": len(query_members),
            "operation_member_counts": {name: len(values) for name, values in operation_members.items()},
            "operation_exact_pair_counts": {name: len(values) for name, values in exact_pairs.items()},
            "operation_members": operation_members,
            "exact_pairs": exact_pairs,
        },
        "decision": {
            "point_contains_exact_pairs_available": bool(exact_pairs["point_contains"]),
            "range_contains_exact_pairs_available": bool(exact_pairs["range_contains"]),
            "range_intersects_exact_pairs_available": bool(exact_pairs["range_intersects"]),
            "pip_exact_pairs_available": bool(exact_pairs["pip"]),
            "mutation_exact_pairs_available": bool(exact_pairs["mutation"]),
            "do_not_invent_missing_paper_inputs": True,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--archive-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit_archive(
        archive_path=args.archive.resolve(),
        archive_result=json.loads(args.archive_result.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
