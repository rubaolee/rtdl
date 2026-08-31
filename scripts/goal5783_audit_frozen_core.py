"""Prove Goal5783 did not change the frozen Goal5782 product source."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-source", type=Path, required=True)
    parser.add_argument("--current-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    archive = args.frozen_source.resolve()
    root = args.current_root.resolve()
    frozen: dict[str, str] = {}
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            path = PurePosixPath(member.name)
            if not member.isfile() or not path.parts or path.parts[0] != "src":
                continue
            stream = handle.extractfile(member)
            if stream is None:
                raise RuntimeError(member.name)
            frozen[path.as_posix()] = digest(stream.read())
    current = {
        path.relative_to(root).as_posix(): digest(path.read_bytes())
        for path in (root / "src").rglob("*") if path.is_file()
        and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    missing = sorted(set(frozen) - set(current))
    unexpected = sorted(set(current) - set(frozen))
    mismatch = sorted(
        name for name in set(frozen) & set(current)
        if frozen[name] != current[name])
    result = {
        "schema": "rtdl.goal5783.frozen_core_audit.v1",
        "frozen_source_archive_sha256": digest(archive.read_bytes()),
        "frozen_src_file_count": len(frozen),
        "current_src_file_count": len(current),
        "missing_paths": missing,
        "unexpected_paths": unexpected,
        "byte_mismatch_paths": mismatch,
        "core_unchanged": not missing and not unexpected and not mismatch,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if not result["core_unchanged"]:
        raise SystemExit("Goal5783 core seal failed")


if __name__ == "__main__":
    main()
