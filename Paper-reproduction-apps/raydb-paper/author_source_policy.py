"""Pinned, app-owned author-source admission policy for the RayDB evidence."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


PINNED_AUTHOR_REMOTE = "https://github.com/LonelySlim/myOptixDB"
PINNED_AUTHOR_COMMIT = "a610c00d7334d8907435cc0a124f9ca8392ee456"
APPROVED_STATUS_PORCELAIN = [" M Makefile"]
APPROVED_COMPATIBILITY_PATCH_SHA256 = (
    "2cd73c8afb1d1c98e726f30457c48c730dafee8a7dfe18221e44b6df0b7e4388"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_author_source_identity(
    identity: object,
    *,
    compatibility_patch_path: Path,
) -> dict[str, Any]:
    if not isinstance(identity, dict):
        raise ValueError("author source identity must be an object")
    patch_sha256 = sha256_file(compatibility_patch_path)
    if patch_sha256 != APPROVED_COMPATIBILITY_PATCH_SHA256:
        raise ValueError("compatibility patch does not match the approved digest")
    repository_path = identity.get("repository_path")
    if not isinstance(repository_path, str) or not repository_path:
        raise ValueError("author repository path must be present but is host-specific")
    expected = {
        "repository_remote": PINNED_AUTHOR_REMOTE,
        "commit": PINNED_AUTHOR_COMMIT,
        "status_porcelain": APPROVED_STATUS_PORCELAIN,
        "tracked_diff_sha256": patch_sha256,
        "identity_complete": True,
    }
    mismatches = {
        key: {"expected": value, "observed": identity.get(key)}
        for key, value in expected.items()
        if identity.get(key) != value
    }
    if mismatches:
        raise ValueError(f"author source identity violates pinned policy: {mismatches}")
    return {
        "repository_remote": PINNED_AUTHOR_REMOTE,
        "commit": PINNED_AUTHOR_COMMIT,
        "status_porcelain": list(APPROVED_STATUS_PORCELAIN),
        "tracked_diff_sha256": patch_sha256,
        "identity_complete": True,
        "compatibility_patch_sha256": patch_sha256,
    }
