from __future__ import annotations

import argparse
import json
import os
import shutil
import tarfile
from pathlib import Path, PurePosixPath

from acquire_exact_ae_archive import (
    ARCHIVE_MD5,
    ARCHIVE_NAME,
    ARCHIVE_SIZE_BYTES,
    verify_archive,
)


EXTRACTED_DIR_NAME = "PPoPPAE-v2"
MAX_MEMBER_COUNT = 5_000_000
MAX_UNPACKED_BYTES = 1024**4
EXTRA_FREE_DISK_BYTES = 5 * 1024**3


def _validated_relative_name(name: str) -> Path:
    if not name or "\\" in name:
        raise ValueError(f"unsafe tar member name: {name!r}")
    posix = PurePosixPath(name)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError(f"unsafe tar member path: {name!r}")
    if posix.parts and ":" in posix.parts[0]:
        raise ValueError(f"unsafe tar member drive prefix: {name!r}")
    normalized = Path(*[part for part in posix.parts if part not in ("", ".")])
    if not normalized.parts:
        raise ValueError(f"empty normalized tar member path: {name!r}")
    return normalized


def _validated_symlink_target(member_path: Path, linkname: str) -> str:
    if not linkname or "\\" in linkname:
        raise ValueError(f"unsafe tar symlink target: {linkname!r}")
    target = PurePosixPath(linkname)
    if target.is_absolute() or (target.parts and ":" in target.parts[0]):
        raise ValueError(f"unsafe tar symlink target: {linkname!r}")
    resolved_parts = list(member_path.parent.parts)
    for part in target.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not resolved_parts:
                raise ValueError(f"tar symlink escapes extraction root: {linkname!r}")
            resolved_parts.pop()
        else:
            resolved_parts.append(part)
    if not resolved_parts:
        raise ValueError(f"tar symlink resolves to extraction root: {linkname!r}")
    return linkname


def inspect_archive_members(
    archive_path: Path,
    *,
    max_member_count: int = MAX_MEMBER_COUNT,
    max_unpacked_bytes: int = MAX_UNPACKED_BYTES,
) -> dict[str, object]:
    seen: set[str] = set()
    file_count = 0
    directory_count = 0
    symlink_count = 0
    unpacked_bytes = 0
    top_level_entries: set[str] = set()
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member_count, member in enumerate(archive, start=1):
            if member_count > max_member_count:
                raise ValueError("archive member-count safety limit exceeded")
            relative = _validated_relative_name(member.name)
            normalized = relative.as_posix()
            if normalized in seen:
                raise ValueError(f"duplicate tar member path: {member.name!r}")
            seen.add(normalized)
            top_level_entries.add(relative.parts[0])
            if member.isdir():
                directory_count += 1
                continue
            if member.issym():
                _validated_symlink_target(relative, member.linkname)
                symlink_count += 1
                continue
            if not member.isfile():
                raise ValueError(
                    f"unsupported tar member type (hardlinks/devices forbidden): {member.name!r}"
                )
            if member.size < 0:
                raise ValueError(f"negative tar member size: {member.name!r}")
            file_count += 1
            unpacked_bytes += member.size
            if unpacked_bytes > max_unpacked_bytes:
                raise ValueError("archive expanded-size safety limit exceeded")
    return {
        "member_count": len(seen),
        "file_count": file_count,
        "directory_count": directory_count,
        "symlink_count": symlink_count,
        "unpacked_file_bytes": unpacked_bytes,
        "top_level_entries": sorted(top_level_entries),
        "member_types_allowed": ["directory", "regular_file", "safe_relative_symlink"],
        "hardlinks_and_special_files_rejected": True,
        "escaping_symlinks_rejected": True,
        "safe": True,
    }


def extract_archive_atomically(
    archive_path: Path,
    destination_root: Path,
    inventory: dict[str, object],
    *,
    resume_staging: bool = False,
) -> dict[str, object]:
    staging = destination_root / f".{EXTRACTED_DIR_NAME}.extracting"
    final = destination_root / EXTRACTED_DIR_NAME
    if staging.exists() and not resume_staging:
        raise FileExistsError(f"staging path already exists: {staging}")
    if staging.exists() and (staging.is_symlink() or not staging.is_dir()):
        raise ValueError(f"staging path is not a real directory: {staging}")
    if final.exists():
        raise FileExistsError(f"final extraction path already exists: {final}")
    free_bytes = shutil.disk_usage(destination_root).free
    required_bytes = int(inventory["unpacked_file_bytes"]) + EXTRA_FREE_DISK_BYTES
    if free_bytes < required_bytes:
        raise RuntimeError(
            f"insufficient extraction disk: require {required_bytes}, have {free_bytes}"
        )

    staging.mkdir(parents=True, exist_ok=resume_staging)
    extracted_files = 0
    extracted_bytes = 0
    resumed_files = 0
    rewritten_partial_files = 0
    pending_symlinks: list[tuple[Path, str]] = []
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive:
            relative = _validated_relative_name(member.name)
            target = staging / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=resume_staging)
                continue
            if member.issym():
                pending_symlinks.append(
                    (target, _validated_symlink_target(relative, member.linkname))
                )
                continue
            if not member.isfile():
                raise ValueError(f"unsupported tar member type: {member.name!r}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                if not resume_staging:
                    raise FileExistsError(f"archive target already exists: {target}")
                if target.is_symlink() or not target.is_file():
                    raise ValueError(f"existing archive target has the wrong type: {target}")
                if target.stat().st_size == member.size:
                    extracted_files += 1
                    extracted_bytes += member.size
                    resumed_files += 1
                    continue
                target.unlink()
                rewritten_partial_files += 1
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"tar member has no file payload: {member.name!r}")
            with source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=8 * 1024 * 1024)
            if target.stat().st_size != member.size:
                raise RuntimeError(f"extracted member size mismatch: {member.name!r}")
            extracted_files += 1
            extracted_bytes += member.size
    for target, linkname in pending_symlinks:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            if not resume_staging or os.readlink(target) != linkname:
                raise ValueError(f"existing archive symlink does not match: {target}")
            continue
        if target.exists():
            raise ValueError(f"archive symlink target path already exists: {target}")
        target.symlink_to(linkname)
    if extracted_files != int(inventory["file_count"]):
        raise RuntimeError("extracted file count does not match inspected inventory")
    if extracted_bytes != int(inventory["unpacked_file_bytes"]):
        raise RuntimeError("extracted byte count does not match inspected inventory")
    os.replace(staging, final)
    return {
        "final_path": str(final),
        "staging_path_promoted": str(staging),
        "file_count": extracted_files,
        "file_bytes": extracted_bytes,
        "symlink_count": len(pending_symlinks),
        "resume_staging_used": resume_staging,
        "resumed_complete_file_count": resumed_files,
        "rewritten_partial_file_count": rewritten_partial_files,
        "atomic_directory_promotion": True,
    }


def load_verified_inventory_evidence(
    evidence_path: Path,
    archive_path: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    """Reuse a completed verification/inventory gate without rereading the archive."""
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    verification = payload.get("verification")
    inventory = payload.get("inventory")
    boundary = payload.get("claim_boundary")
    if not isinstance(verification, dict) or not isinstance(inventory, dict):
        raise ValueError("verified inventory evidence is missing verification/inventory")
    if not isinstance(boundary, dict):
        raise ValueError("verified inventory evidence is missing claim boundary")
    if payload.get("status") != "exact_ae_archive_inventory_complete__not_extracted":
        raise ValueError("verified inventory evidence has the wrong status")
    if verification.get("verified") is not True:
        raise ValueError("archive verification evidence is not complete")
    if boundary.get("archive_verified") is not True or boundary.get("inventory_completed") is not True:
        raise ValueError("archive inventory evidence is not complete")
    if inventory.get("safe") is not True:
        raise ValueError("archive inventory evidence is not marked safe")
    if Path(str(verification.get("path", ""))).resolve() != archive_path.resolve():
        raise ValueError("verified archive path does not match extraction archive")
    if int(verification.get("size_bytes", -1)) != ARCHIVE_SIZE_BYTES:
        raise ValueError("verified archive size does not match the pinned archive")
    if str(verification.get("md5", "")).lower() != ARCHIVE_MD5:
        raise ValueError("verified archive md5 does not match the pinned archive")
    if not archive_path.is_file() or archive_path.stat().st_size != ARCHIVE_SIZE_BYTES:
        raise ValueError("current archive is absent or has changed size")
    required_inventory_fields = {
        "member_count",
        "file_count",
        "directory_count",
        "symlink_count",
        "unpacked_file_bytes",
        "top_level_entries",
    }
    if not required_inventory_fields.issubset(inventory):
        raise ValueError("verified inventory evidence is incomplete")
    return dict(verification), dict(inventory)


def build_plan(*, archive_path: Path, destination_root: Path) -> dict[str, object]:
    return {
        "schema": "rtdl.paper_reproduction.librts.safe_extraction_plan.v1",
        "status": (
            "verified_archive_ready_for_inventory"
            if archive_path.is_file()
            else "safe_extraction_contract_ready__verified_archive_absent"
        ),
        "paths": {
            "archive": str(archive_path),
            "staging": str(destination_root / f".{EXTRACTED_DIR_NAME}.extracting"),
            "final": str(destination_root / EXTRACTED_DIR_NAME),
        },
        "safety_contract": {
            "archive_size_and_md5_required_before_inventory": True,
            "completed_verification_inventory_evidence_may_be_reused_for_extraction": True,
            "absolute_or_parent_paths_rejected": True,
            "backslash_and_drive_prefixes_rejected": True,
            "duplicate_paths_rejected": True,
            "safe_relative_symlinks_allowed": True,
            "escaping_symlinks_hardlinks_devices_and_special_files_rejected": True,
            "expanded_size_checked_before_extraction": True,
            "staging_directory_required": True,
            "final_directory_promotion_is_atomic": True,
        },
        "claim_boundary": {
            "archive_present": archive_path.is_file(),
            "archive_verified": False,
            "inventory_completed": False,
            "archive_extracted": False,
            "exact_input_files_identified": False,
            "paper_figure_reproduced": False,
            "performance_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }


def _write(payload: dict[str, object], output: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("plan", "inventory", "extract"), required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verified-inventory", type=Path)
    parser.add_argument("--resume-staging", action="store_true")
    args = parser.parse_args()

    archive_path = args.archive_dir.resolve() / ARCHIVE_NAME
    destination_root = args.destination_root.resolve()
    destination_root.mkdir(parents=True, exist_ok=True)
    plan = build_plan(archive_path=archive_path, destination_root=destination_root)
    if args.mode == "plan":
        _write(plan, args.output)
        return 0

    if args.verified_inventory is not None:
        if args.mode != "extract":
            raise ValueError("--verified-inventory is only valid with --mode extract")
        verification, inventory = load_verified_inventory_evidence(
            args.verified_inventory.resolve(), archive_path
        )
        evidence_reused = True
    else:
        verification = verify_archive(archive_path)
        inventory = inspect_archive_members(archive_path)
        evidence_reused = False
    payload = {**plan, "verification": verification, "inventory": inventory}
    payload["verified_inventory_evidence_reused"] = evidence_reused
    payload["status"] = "exact_ae_archive_inventory_complete__not_extracted"
    payload["claim_boundary"]["archive_verified"] = True
    payload["claim_boundary"]["inventory_completed"] = True
    if args.mode == "extract":
        payload["extraction"] = extract_archive_atomically(
            archive_path,
            destination_root,
            inventory,
            resume_staging=args.resume_staging,
        )
        payload["status"] = "exact_ae_archive_safely_extracted__dataset_identity_pending"
        payload["claim_boundary"]["archive_extracted"] = True
    _write(payload, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
