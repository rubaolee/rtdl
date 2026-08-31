#!/usr/bin/env python3
"""Build and verify the deterministic anonymous CGO evidence package."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).absolute().parents[1]
ARTIFACT = ROOT / "paper" / "cgo2027" / "artifact"
DEFAULT_OUTPUT = ROOT / "paper" / "cgo2027" / "rtdl_cgo2027_anonymous_artifact.tar.gz"
PREFIX = "rtdl-cgo2027-artifact"
FORBIDDEN_BYTES = (
    b"Lestat",
    b"C:\\Users\\",
    b"C:/Users/",
    b"history/internal_docs",
    b"root@",
    b"192.168.",
    b"213.173.",
    b"157.157.",
    b"codex/v4",
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_manifest() -> tuple[dict, list[tuple[str, bytes]]]:
    manifest_path = ARTIFACT / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest["schema"] == "rtdl.artifact.manifest.v1"
    rows = manifest["files"]
    assert len(rows) == manifest["file_count"]
    assert sum(row["bytes"] for row in rows) == manifest["payload_bytes"]
    members: list[tuple[str, bytes]] = [("manifest.json", manifest_bytes)]
    for row in rows:
        relative = PurePosixPath(row["path"])
        assert not relative.is_absolute()
        assert ".." not in relative.parts
        path = ARTIFACT.joinpath(*relative.parts)
        payload = path.read_bytes()
        assert len(payload) == row["bytes"]
        assert digest(payload) == row["sha256"]
        members.append((relative.as_posix(), payload))
    assert len({name for name, _ in members}) == len(members)
    for name, payload in members:
        for forbidden in FORBIDDEN_BYTES:
            assert forbidden not in payload, (name, forbidden)
    return manifest, sorted(members, key=lambda row: row[0].encode("utf-8"))


def build_bytes(members: list[tuple[str, bytes]]) -> bytes:
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed,
                       compresslevel=9, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for relative, payload in members:
                info = tarfile.TarInfo(f"{PREFIX}/{relative}")
                info.size = len(payload)
                info.mode = 0o444
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.type = tarfile.REGTYPE
                archive.addfile(info, io.BytesIO(payload))
    return compressed.getvalue()


def verify_archive(raw: bytes, expected: list[tuple[str, bytes]]) -> None:
    expected_by_name = {f"{PREFIX}/{name}": payload for name, payload in expected}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        members = archive.getmembers()
        assert len(members) == len(expected_by_name)
        assert all(member.isfile() for member in members)
        assert all(member.mode == 0o444 for member in members)
        assert all(member.mtime == 0 for member in members)
        assert all(member.uid == member.gid == 0 for member in members)
        assert all(member.uname == member.gname == "" for member in members)
        assert {member.name for member in members} == set(expected_by_name)
        for member in members:
            stream = archive.extractfile(member)
            assert stream is not None
            assert stream.read() == expected_by_name[member.name]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest, members = load_manifest()
    first = build_bytes(members)
    second = build_bytes(members)
    assert first == second
    verify_archive(first, members)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(first)
    print(json.dumps({
        "schema": "rtdl.goal5822.anonymous_artifact_package_receipt.v1",
        "status": "PASS",
        "archive": str(args.output),
        "archive_bytes": len(first),
        "archive_sha256": digest(first),
        "member_count": len(members),
        "manifest_file_count": manifest["file_count"],
        "manifest_payload_bytes": manifest["payload_bytes"],
        "all_regular": True,
        "mode": "0444",
        "uid_gid": 0,
        "mtime": 0,
        "single_root_prefix": PREFIX,
        "byte_identical_second_build": True,
        "forbidden_identity_scan_passed": True,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
