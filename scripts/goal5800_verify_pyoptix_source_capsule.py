#!/usr/bin/env python3
"""Verify the complete pinned otk-pyoptix tree without a checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import PurePosixPath
import tarfile


def git_object(kind: str, value: bytes) -> str:
    return hashlib.sha1(
        f"{kind} {len(value)}\0".encode("ascii") + value).hexdigest()


def tree_sha(node: dict[str, object]) -> str:
    entries = []
    for name, value in node.items():
        if isinstance(value, dict) and "blob" not in value:
            object_sha = tree_sha(value)
            mode = "40000"
            key = name.encode("utf-8") + b"/"
        else:
            assert isinstance(value, dict)
            object_sha = str(value["blob"])
            mode = str(value["mode"])
            key = name.encode("utf-8")
        record = (mode + " ").encode("ascii") + name.encode("utf-8") \
            + b"\0" + bytes.fromhex(object_sha)
        entries.append((key, record))
    body = b"".join(record for _, record in sorted(entries))
    return git_object("tree", body)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()
    files: dict[str, bytes] = {}
    with tarfile.open(args.archive, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() \
                    or member.islnk():
                raise RuntimeError(f"unsafe member: {member.name}")
            if member.isfile():
                stream = archive.extractfile(member)
                if stream is None or member.name in files:
                    raise RuntimeError(f"invalid member: {member.name}")
                files[member.name] = stream.read()
    root = "goal5800_pyoptix_source/"
    manifest = json.loads(files[root + "MANIFEST.json"])
    trie: dict[str, object] = {}
    for row in manifest["files"]:
        path = str(row["path"])
        git_value = files[root + "git_objects/" + path]
        checkout_value = files[root + "clean_checkout/" + path]
        if len(git_value) != row["git_object_bytes"] \
                or hashlib.sha256(git_value).hexdigest() != row[
                    "git_object_sha256"] \
                or git_object("blob", git_value) != row["git_blob_sha1"] \
                or len(checkout_value) != row["clean_checkout_bytes"] \
                or hashlib.sha256(checkout_value).hexdigest() != row[
                    "clean_checkout_sha256"]:
            raise RuntimeError(f"source member identity mismatch: {path}")
        parts = PurePosixPath(path).parts
        node = trie
        for part in parts[:-1]:
            child = node.setdefault(part, {})
            if not isinstance(child, dict):
                raise RuntimeError(f"file/tree collision: {path}")
            node = child
        node[parts[-1]] = {
            "mode": row["git_mode"], "blob": row["git_blob_sha1"]}
    rebuilt_tree = tree_sha(trie)
    if rebuilt_tree != manifest["tree"]:
        raise RuntimeError(
            f"Git tree mismatch: {rebuilt_tree} != {manifest['tree']}")
    print(json.dumps({
        "status": "PASS",
        "commit": manifest["commit"],
        "tree": rebuilt_tree,
        "tracked_file_count": len(manifest["files"]),
        "archive_sha256": hashlib.sha256(open(args.archive, "rb").read()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
