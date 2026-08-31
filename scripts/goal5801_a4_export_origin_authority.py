#!/usr/bin/env python3
"""Export a self-contained Git origin authority for Goal5801 A4.

The authority contains the raw commit object and a NUL-safe recursive tree
inventory.  The native-custody capture and its independent verifier use these
bytes to recompute the commit and root-tree identities without access to the
origin repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from scripts import goal5801_a3_capture_native_custody as custody


def _run(repository: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments], check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace')}")
    return completed.stdout


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()

    repository = args.repository.resolve(strict=True)
    commit = _run(repository, "rev-parse", f"{args.commit}^{{commit}}") \
        .decode("ascii").strip()
    tree = _run(repository, "rev-parse", f"{commit}^{{tree}}") \
        .decode("ascii").strip()
    commit_object = _run(repository, "cat-file", "commit", commit)
    inventory = _run(
        repository, "ls-tree", "-rz", "--full-tree", commit)
    if custody._git_object_sha1("commit", commit_object) != commit:
        raise RuntimeError("raw Git commit object identity mismatch")
    if not commit_object.startswith(f"tree {tree}\n".encode("ascii")):
        raise RuntimeError("raw Git commit does not bind resolved root tree")
    rows = custody._parse_full_inventory(inventory)
    if custody._inventory_tree_sha1(rows) != tree:
        raise RuntimeError("recursive Git inventory does not reconstruct root tree")

    output = args.output_directory.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    commit_path = output / "origin_commit_object.bin"
    inventory_path = output / "origin_full_git_ls_tree_z.bin"
    receipt_path = output / "receipt.json"
    _write_create_only(commit_path, commit_object)
    _write_create_only(inventory_path, inventory)
    receipt = {
        "schema": "rtdl.goal5801.a4.origin_authority_export.v1",
        "status": "PASS__SELF_CONTAINED_GIT_COMMIT_AND_TREE_AUTHORITY",
        "origin_commit": commit,
        "origin_tree": tree,
        "origin_commit_object_bytes": len(commit_object),
        "origin_commit_object_sha256": hashlib.sha256(commit_object).hexdigest(),
        "origin_inventory_bytes": len(inventory),
        "origin_inventory_sha256": hashlib.sha256(inventory).hexdigest(),
        "origin_inventory_leaf_count": len(rows),
        "registered_performance_timing_count": 0,
    }
    receipt_bytes = json.dumps(
        receipt, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8") + b"\n"
    _write_create_only(receipt_path, receipt_bytes)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
