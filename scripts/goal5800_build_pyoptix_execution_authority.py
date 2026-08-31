#!/usr/bin/env python3
"""Create the exact preexecution source authority for Goal5800's PyOptiX arm."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess


REQUIRED_PATHS = (
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5798_premeasurement/workload.py",
    "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py",
)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _require_git_identity(value: str, label: str) -> str:
    if len(value) != 40 or any(
            character not in "0123456789abcdef" for character in value):
        raise RuntimeError(f"{label} must be a full lowercase Git SHA-1")
    return value


def _run_git(repository: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return completed.stdout


def _git_object_id(kind: str, value: bytes) -> str:
    framed = f"{kind} {len(value)}\0".encode("ascii") + value
    return hashlib.sha1(framed).hexdigest()


def _parse_tree(value: bytes) -> list[dict[str, str]]:
    rows = []
    cursor = 0
    while cursor < len(value):
        space = value.find(b" ", cursor)
        nul = value.find(b"\0", space + 1)
        if space <= cursor or nul < 0 or nul + 21 > len(value):
            raise RuntimeError("malformed raw Git tree object")
        mode = value[cursor:space].decode("ascii", errors="strict")
        name = value[space + 1:nul].decode("utf-8", errors="strict")
        object_id = value[nul + 1:nul + 21].hex()
        if not name or "/" in name or name in {".", ".."}:
            raise RuntimeError("unsafe Git tree entry name")
        rows.append({"mode": mode, "name": name, "object_id": object_id})
        cursor = nul + 21
    if len({row["name"] for row in rows}) != len(rows):
        raise RuntimeError("duplicate Git tree entry name")
    return rows


def _required_directory_paths() -> list[str]:
    directories = {""}
    for relative in REQUIRED_PATHS:
        parts = PurePosixPath(relative).parts
        for count in range(1, len(parts)):
            directories.add("/".join(parts[:count]))
    return sorted(directories, key=lambda value: (value.count("/") + bool(value), value))


def build(
        source_root: Path, *, origin_repository: Path,
        origin_commit: str, origin_tree: str) -> dict[str, object]:
    root = source_root.resolve(strict=True)
    repository = origin_repository.resolve(strict=True)
    commit = _require_git_identity(origin_commit, "origin commit")
    tree = _require_git_identity(origin_tree, "origin tree")
    resolved_commit = _run_git(
        repository, "rev-parse", f"{commit}^{{commit}}").decode("ascii").strip()
    resolved_tree = _run_git(
        repository, "rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()
    if resolved_commit != commit or resolved_tree != tree:
        raise RuntimeError("declared origin commit/tree differs from Git object database")
    commit_body = _run_git(repository, "cat-file", "commit", commit)
    if (_git_object_id("commit", commit_body) != commit
            or not commit_body.startswith(f"tree {tree}\n".encode("ascii"))):
        raise RuntimeError("origin commit object does not bind the declared root tree")

    node_ids: dict[str, str] = {"": tree}
    node_bodies: dict[str, bytes] = {}
    node_entries: dict[str, list[dict[str, str]]] = {}
    for directory in _required_directory_paths():
        if directory:
            parent, _, leaf = directory.rpartition("/")
            matches = [
                row for row in node_entries[parent]
                if row["name"] == leaf and row["mode"] == "40000"
            ]
            if len(matches) != 1:
                raise RuntimeError(f"required directory is absent from origin tree: {directory}")
            node_ids[directory] = matches[0]["object_id"]
        object_id = node_ids[directory]
        body = _run_git(repository, "cat-file", "tree", object_id)
        if _git_object_id("tree", body) != object_id:
            raise RuntimeError(f"Git tree object hash mismatch: {directory or '<root>'}")
        node_bodies[directory] = body
        node_entries[directory] = _parse_tree(body)

    rows = []
    for relative in REQUIRED_PATHS:
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError(f"invalid authority path: {relative}")
        value = (root / Path(*path.parts)).resolve(strict=True).read_bytes()
        origin_value = _run_git(repository, "show", f"{commit}:{relative}")
        if value != origin_value:
            raise RuntimeError(f"execution source is not exact origin Git bytes: {relative}")
        parent = str(path.parent).replace("\\", "/")
        if parent == ".":
            parent = ""
        matches = [row for row in node_entries[parent] if row["name"] == path.name]
        if len(matches) != 1 or matches[0]["mode"] not in {"100644", "100755"}:
            raise RuntimeError(f"origin path is not one regular Git blob: {relative}")
        blob_sha1 = _git_object_id("blob", value)
        if matches[0]["object_id"] != blob_sha1:
            raise RuntimeError(f"origin tree/blob linkage mismatch: {relative}")
        rows.append({
            "path": relative, "git_mode": matches[0]["mode"],
            "git_blob_sha1": blob_sha1,
            "bytes": len(value), "sha256": sha256(value),
        })
    tree_nodes = [{
        "path": directory,
        "object_id": node_ids[directory],
        "bytes": len(node_bodies[directory]),
        "base64": base64.b64encode(node_bodies[directory]).decode("ascii"),
    } for directory in _required_directory_paths()]
    return {
        "schema": "rtdl.goal5800.pyoptix_execution_authority.v2",
        "status": "FROZEN__PREEXECUTION_SOURCE_AUTHORITY",
        "capture_phase": "BEFORE_PYOPTIX_CUPY_IMPORT_OR_CUDA_OPTIX_INITIALIZATION",
        "origin_repository_commit": commit,
        "origin_repository_tree": tree,
        "git_membership_proof": {
            "object_format": "sha1",
            "commit_object": {
                "object_id": commit, "bytes": len(commit_body),
                "base64": base64.b64encode(commit_body).decode("ascii"),
            },
            "tree_nodes": tree_nodes,
            "all_required_files_exact_origin_blobs": True,
        },
        "file_count": len(rows),
        "files": rows,
        "files_sha256": sha256(canonical(rows)),
        "registered_performance_timing_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--origin-repository", type=Path, required=True)
    parser.add_argument("--origin-commit", required=True)
    parser.add_argument("--origin-tree", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    document = build(
        args.source_root, origin_repository=args.origin_repository,
        origin_commit=args.origin_commit,
        origin_tree=args.origin_tree)
    value = json.dumps(document, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(value)
    print(json.dumps({
        "status": document["status"], "output": str(args.output),
        "bytes": len(value), "sha256": sha256(value),
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
