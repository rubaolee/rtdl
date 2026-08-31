#!/usr/bin/env python3
"""Prove Goal5767 changed release surface, not frozen V4 execution semantics."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "history/internal_docs/goal5766_v4_portable_rc_v3_20260812.tar.gz"
CURRENT = ROOT / "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz"
ALLOWED_CHANGED = {"README.md", "pyproject.toml", "src/rtdsl/__init__.py"}
ALLOWED_ADDED = {
    "README.md",
    "pyproject.toml",
    "src/rtdsl/v4.py",
    "examples/current/v4_restricted_callback_quickstart.py",
    "tests/goal5767_v4_release_surface_test.py",
    "scripts/goal5767_release_audit.py",
    "scripts/goal5767_clean_validate.py",
    "scripts/goal5767_build_usable_rc.py",
}
ALLOWED_ADDED_PREFIXES = ("docs/v3/", "docs/v4/")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source(bundle: Path) -> tuple[dict[str, bytes], str]:
    with tarfile.open(bundle, "r:gz") as outer:
        handle = outer.extractfile("SOURCE.tar.gz")
        if handle is None:
            raise RuntimeError(f"missing SOURCE.tar.gz: {bundle}")
        raw = handle.read()
    rows = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as source:
        for member in source.getmembers():
            if member.isfile():
                handle = source.extractfile(member)
                if handle is None or member.name in rows:
                    raise RuntimeError(f"invalid source member: {member.name}")
                rows[member.name] = handle.read()
    return rows, _sha(raw)


def main() -> None:
    base, base_sha = _source(BASE)
    current, current_sha = _source(CURRENT)
    changed = sorted(name for name in base.keys() & current.keys() if base[name] != current[name])
    added = sorted(current.keys() - base.keys())
    removed = sorted(base.keys() - current.keys())
    unexpected_changed = sorted(set(changed) - ALLOWED_CHANGED)
    unexpected_added = sorted(
        name for name in added
        if name not in ALLOWED_ADDED and not name.startswith(ALLOWED_ADDED_PREFIXES)
    )
    if removed or unexpected_changed or unexpected_added:
        raise RuntimeError(json.dumps({
            "removed": removed,
            "unexpected_changed": unexpected_changed,
            "unexpected_added": unexpected_added,
        }, sort_keys=True))
    scientific_changes = [
        name for name in changed + added
        if name.startswith("src/rtdsl/v4_") and name != "src/rtdsl/v4.py"
    ]
    if scientific_changes:
        raise RuntimeError(f"scientific V4 module changed: {scientific_changes}")
    result = {
        "schema": "rtdl.goal5767.source_delta_audit.v1",
        "goal": 5767,
        "base_bundle_sha256": _sha(BASE.read_bytes()),
        "base_source_archive_sha256": base_sha,
        "current_bundle_sha256": _sha(CURRENT.read_bytes()),
        "current_source_archive_sha256": current_sha,
        "changed_existing": changed,
        "added": added,
        "removed": removed,
        "unexpected_changed": unexpected_changed,
        "unexpected_added": unexpected_added,
        "scientific_v4_execution_module_changes": scientific_changes,
        "execution_semantics_or_native_changed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
