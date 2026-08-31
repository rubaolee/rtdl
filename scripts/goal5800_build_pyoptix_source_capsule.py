#!/usr/bin/env python3
"""Freeze the complete pinned NVIDIA otk-pyoptix tree deterministically."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".tmp_goal5796_upstream_20260823" / "otk-pyoptix"
OUTPUT = ROOT / "history" / "internal_docs" / (
    "goal5800_nvidia_otk_pyoptix_source_capsule_v2_20260824.tar.gz")
TWIN = OUTPUT.with_name(
    "goal5800_nvidia_otk_pyoptix_source_capsule_v2_twin_20260824.tar.gz")
EXPECTED_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
EXPECTED_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
ARCHIVE_ROOT = "goal5800_pyoptix_source"


def run_git(*arguments: str, binary: bool = False):
    result = subprocess.run(
        ["git", "-C", str(SOURCE), *arguments], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha1(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value).hexdigest()


def add_bytes(archive: tarfile.TarFile, name: str, value: bytes, mode: int) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(value)
    info.mode = mode
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(value))


def build_bytes() -> bytes:
    commit = run_git("rev-parse", "HEAD")
    tree = run_git("rev-parse", "HEAD^{tree}")
    status = run_git("status", "--porcelain=v1", "--untracked-files=all")
    if commit != EXPECTED_COMMIT or tree != EXPECTED_TREE or status:
        raise RuntimeError({"commit": commit, "tree": tree, "status": status})

    ls_tree = run_git("ls-tree", "-rz", "HEAD", binary=True)
    rows = []
    payloads: list[tuple[str, bytes, int]] = []
    for raw in ls_tree.rstrip(b"\0").split(b"\0"):
        metadata, raw_path = raw.split(b"\t", 1)
        mode_text, kind, object_sha = metadata.decode("ascii").split(" ")
        if kind != "blob":
            raise RuntimeError(f"non-blob tracked entry is unsupported: {raw!r}")
        relative = raw_path.decode("utf-8")
        # Preserve both the canonical Git object and the exact clean-checkout
        # projection used by the already-frozen source/line references.  On
        # Windows the latter can contain CRLF without making the checkout
        # dirty; conflating the two was the original custody defect.
        git_value = run_git("show", f"HEAD:{relative}", binary=True)
        checkout_value = (SOURCE / relative).read_bytes()
        if git_blob_sha1(git_value) != object_sha:
            raise RuntimeError(f"Git blob identity mismatch: {relative}")
        mode = 0o755 if mode_text == "100755" else 0o644
        rows.append({
            "path": relative,
            "git_mode": mode_text,
            "git_blob_sha1": object_sha,
            "git_object_bytes": len(git_value),
            "git_object_sha256": sha256(git_value),
            "clean_checkout_bytes": len(checkout_value),
            "clean_checkout_sha256": sha256(checkout_value),
        })
        payloads.append((
            f"{ARCHIVE_ROOT}/git_objects/{relative}", git_value, mode))
        payloads.append((
            f"{ARCHIVE_ROOT}/clean_checkout/{relative}", checkout_value, mode))

    manifest = {
        "schema": "rtdl.goal5800.nvidia_otk_pyoptix_source_capsule.v1",
        "repository": run_git("remote", "get-url", "origin"),
        "commit": commit,
        "tree": tree,
        "tracked_file_count": len(rows),
        "git_object_payload_bytes": sum(
            row["git_object_bytes"] for row in rows),
        "clean_checkout_payload_bytes": sum(
            row["clean_checkout_bytes"] for row in rows),
        "git_ls_tree_sha256": sha256(ls_tree),
        "files": rows,
    }
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n")

    raw_tar = io.BytesIO()
    with tarfile.open(fileobj=raw_tar, mode="w", format=tarfile.PAX_FORMAT) as archive:
        add_bytes(archive, f"{ARCHIVE_ROOT}/MANIFEST.json", manifest_bytes, 0o644)
        add_bytes(archive, f"{ARCHIVE_ROOT}/GIT_LS_TREE.z", ls_tree, 0o644)
        for name, value, mode in payloads:
            add_bytes(archive, name, value, mode)
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as stream:
        stream.write(raw_tar.getvalue())
    return compressed.getvalue()


def main() -> None:
    if OUTPUT.exists() or TWIN.exists():
        raise FileExistsError("source capsule output already exists")
    first = build_bytes()
    second = build_bytes()
    if first != second:
        raise RuntimeError("deterministic source-capsule twin mismatch")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(first)
    TWIN.write_bytes(second)
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "bytes": len(first),
        "sha256": sha256(first),
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
