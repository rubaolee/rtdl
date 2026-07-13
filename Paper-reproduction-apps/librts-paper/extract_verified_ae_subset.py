from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tarfile
from pathlib import Path

from acquire_exact_ae_archive import ARCHIVE_NAME
from extract_verified_ae_archive import (
    _validated_relative_name,
    load_verified_inventory_evidence,
)


MINIMUM_FREE_BYTES = 5 * 1024**3


def extract_selected_members_atomically(
    archive_path: Path,
    destination: Path,
    selected_members: tuple[str, ...],
) -> dict[str, object]:
    normalized = tuple(
        _validated_relative_name(name).as_posix() for name in selected_members
    )
    if not normalized or len(set(normalized)) != len(normalized):
        raise ValueError("selected archive members must be nonempty and unique")
    staging = destination.parent / f".{destination.name}.extracting"
    if staging.exists() or destination.exists():
        raise FileExistsError("subset staging/final destination already exists")
    if shutil.disk_usage(destination.parent).free < MINIMUM_FREE_BYTES:
        raise RuntimeError("insufficient free space for bounded subset extraction")
    staging.mkdir(parents=True)
    selected = set(normalized)
    extracted: dict[str, dict[str, object]] = {}
    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            for member in archive:
                relative = _validated_relative_name(member.name)
                name = relative.as_posix()
                if name not in selected:
                    continue
                if not member.isfile():
                    raise ValueError(f"selected archive member is not a regular file: {name}")
                target = staging / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise RuntimeError(f"selected member has no payload: {name}")
                digest = hashlib.sha256()
                written = 0
                with source, target.open("xb") as output:
                    while True:
                        chunk = source.read(8 * 1024 * 1024)
                        if not chunk:
                            break
                        output.write(chunk)
                        digest.update(chunk)
                        written += len(chunk)
                if written != member.size:
                    raise RuntimeError(f"selected member size mismatch: {name}")
                extracted[name] = {
                    "relative_path": name,
                    "size_bytes": written,
                    "sha256": digest.hexdigest(),
                }
                if extracted.keys() == selected:
                    break
        missing = sorted(selected - extracted.keys())
        if missing:
            raise FileNotFoundError(f"selected archive members are missing: {missing}")
        os.replace(staging, destination)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return {
        "final_path": str(destination),
        "selected_members": [extracted[name] for name in normalized],
        "selected_member_count": len(extracted),
        "atomic_directory_promotion": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--verified-inventory", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--member", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    archive_path = args.archive_dir.resolve() / ARCHIVE_NAME
    verification, inventory = load_verified_inventory_evidence(
        args.verified_inventory.resolve(), archive_path
    )
    destination = args.destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    extraction = extract_selected_members_atomically(
        archive_path, destination, tuple(args.member)
    )
    payload = {
        "schema": "rtdl.paper_reproduction.librts.safe_subset_extraction.v1",
        "status": "exact_ae_archive_selected_members_safely_extracted",
        "verification": verification,
        "inventory_reference": {
            "safe": inventory["safe"],
            "member_count": inventory["member_count"],
            "unpacked_file_bytes": inventory["unpacked_file_bytes"],
        },
        "extraction": extraction,
        "claim_boundary": {
            "archive_verified": True,
            "inventory_completed": True,
            "archive_extracted": False,
            "archive_subset_extracted": True,
            "exact_input_files_identified": True,
            "paper_figure_reproduced": False,
            "performance_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
