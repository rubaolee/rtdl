from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
import tempfile
from pathlib import Path, PurePosixPath


SCHEMA = "rtdl.paper_reproduction.librts.verified_operation_batch_extension.v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_member(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or not path.parts:
        raise ValueError(f"unsafe selected archive member: {name!r}")
    return path.as_posix()


def extend_batch(
    *,
    archive_path: Path,
    archive_result: dict[str, object],
    operation_inventory: dict[str, object],
    operation: str,
    pairs: list[dict[str, str]],
    destination: Path,
    base_extraction: dict[str, object],
) -> dict[str, object]:
    if not archive_result.get("claim_boundary", {}).get("archive_verified", False):
        raise ValueError("batch extension requires verified archive evidence")
    if operation_inventory.get("status") != "verified_archive_operation_inventory_complete":
        raise ValueError("operation inventory is incomplete")
    if not pairs:
        raise ValueError("batch extension requires at least one pair")

    allowed = {
        (_safe_member(item["geometry"]), _safe_member(item["query"]))
        for item in operation_inventory.get("inventory", {}).get("exact_pairs", {}).get(operation, [])
    }
    normalized_pairs = [
        {"geometry": _safe_member(item["geometry"]), "query": _safe_member(item["query"])}
        for item in pairs
    ]
    if len({(item["geometry"], item["query"]) for item in normalized_pairs}) != len(normalized_pairs):
        raise ValueError("batch extension contains duplicate operation pairs")
    if any((item["geometry"], item["query"]) not in allowed for item in normalized_pairs):
        raise ValueError("batch extension contains a pair absent from verified operation inventory")

    destination = destination.resolve()
    if not destination.is_dir():
        raise FileNotFoundError(f"existing verified destination is absent: {destination}")
    base_root = Path(base_extraction["extraction"]["final_path"]).resolve()
    if base_root != destination:
        raise ValueError("base extraction and extension destination differ")
    base_members = {
        _safe_member(item["relative_path"]): item
        for item in base_extraction["extraction"]["selected_members"]
    }

    selected = {item["geometry"] for item in normalized_pairs} | {item["query"] for item in normalized_pairs}
    existing_records: list[dict[str, object]] = []
    missing = set()
    for name in selected:
        target = destination / name
        if target.exists():
            if name not in base_members:
                raise FileExistsError(f"unverified existing selected member: {name}")
            base_record = base_members[name]
            if target.stat().st_size != int(base_record["size_bytes"]) or _sha256(target) != base_record["sha256"]:
                raise ValueError(f"existing selected member differs from base extraction: {name}")
            existing_records.append(dict(base_record))
        else:
            missing.add(name)

    extracted_records: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(dir=destination, prefix=".verified-extension.") as temp:
        staging = Path(temp)
        with tarfile.open(archive_path, mode="r:gz") as archive:
            for member in archive:
                name = _safe_member(member.name)
                if name not in missing:
                    continue
                if not member.isfile():
                    raise ValueError(f"selected member is not a regular file: {name}")
                staged = staging / name
                staged.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise RuntimeError(f"selected member has no payload: {name}")
                with source, staged.open("xb") as output:
                    while chunk := source.read(8 * 1024 * 1024):
                        output.write(chunk)
                if staged.stat().st_size != member.size:
                    raise RuntimeError(f"selected member size mismatch: {name}")
                extracted_records.append(
                    {"relative_path": name, "size_bytes": member.size, "sha256": _sha256(staged)}
                )
        if {item["relative_path"] for item in extracted_records} != missing:
            absent = sorted(missing - {item["relative_path"] for item in extracted_records})
            raise RuntimeError(f"batch extension was incomplete: {absent}")
        for record in extracted_records:
            name = str(record["relative_path"])
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging / name, target)

    members = sorted(existing_records + extracted_records, key=lambda item: str(item["relative_path"]))
    return {
        "schema": SCHEMA,
        "status": "exact_archive_operation_batch_safely_extended",
        "operation": operation,
        "archive": {
            "path": str(archive_path.resolve()),
            "verified_size_bytes": archive_result["verification"]["size_bytes"],
            "verified_md5": archive_result["verification"]["md5"],
        },
        "extraction": {
            "final_path": str(destination),
            "selected_pairs": normalized_pairs,
            "selected_members": members,
            "selected_pair_count": len(normalized_pairs),
            "selected_member_count": len(members),
            "reused_verified_member_count": len(existing_records),
            "newly_extracted_member_count": len(extracted_records),
            "atomic_member_promotion": True,
        },
        "claim_boundary": {
            "archive_verified": True,
            "archive_subset_extended": True,
            "exact_input_files_identified": True,
            "paper_figure_reproduced": False,
            "performance_ratio_authorized": False,
            "complete_paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--archive-result", type=Path, required=True)
    parser.add_argument("--operation-inventory", type=Path, required=True)
    parser.add_argument("--operation", required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--base-extraction", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = extend_batch(
        archive_path=args.archive.resolve(),
        archive_result=json.loads(args.archive_result.read_text(encoding="utf-8")),
        operation_inventory=json.loads(args.operation_inventory.read_text(encoding="utf-8")),
        operation=args.operation,
        pairs=json.loads(args.pairs.read_text(encoding="utf-8")),
        destination=args.destination,
        base_extraction=json.loads(args.base_extraction.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
