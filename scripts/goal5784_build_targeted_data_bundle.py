#!/usr/bin/env python3
"""Build the exact Goal5784 subset of the immutable Goal5776 data archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


SELECTED = (
    "DATA/common/rt_barneshut/expected_forces.txt",
    "DATA/common/rt_barneshut/prepared_arrays.json",
    "DATA/triangle/cit-Patents.edge",
    "DATA/triangle/com-dblp.edge",
    "DATA/triangle/soc-LiveJournal1.edge",
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _info(name: str, size: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = size
    info.mtime = 0
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def _read_manifest(source: Path) -> dict[str, object]:
    with tarfile.open(source, "r:gz") as archive:
        handle = archive.extractfile("DATA_MANIFEST.json")
        if handle is None:
            raise RuntimeError("Goal5776 data archive omitted manifest")
        return json.load(handle)


def _build(source: Path, output: Path, manifest: dict[str, object]) -> None:
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    source_rows = {str(row["path"]): row for row in manifest["files"]}
    if not set(SELECTED).issubset(source_rows):
        raise RuntimeError("Goal5784 selected data are absent from Goal5776")
    subset = {
        "schema": "rtdl.goal5776.real_scale_data_manifest.v1",
        "run_goal_id": 5784,
        "subset_of_goal5776_data_archive_sha256": _sha(source),
        "file_count": len(SELECTED),
        "files": [source_rows[name] for name in sorted(SELECTED)],
    }
    manifest_bytes = (json.dumps(subset, indent=2, sort_keys=True) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as source_stream, output.open("xb") as target_stream:
        with tarfile.open(fileobj=source_stream, mode="r:gz") as source_tar:
            with gzip.GzipFile(fileobj=target_stream, mode="wb", filename="", mtime=0) as gz:
                with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
                    for name in sorted(SELECTED):
                        member = source_tar.getmember(name)
                        if not member.isfile() or member.size != int(source_rows[name]["size_bytes"]):
                            raise RuntimeError(f"Goal5784 source member mismatch: {name}")
                        handle = source_tar.extractfile(member)
                        if handle is None:
                            raise RuntimeError(f"Goal5784 unreadable data member: {name}")
                        out.addfile(_info(name, member.size), handle)
                    out.addfile(_info("DATA_MANIFEST.json", len(manifest_bytes)),
                                io.BytesIO(manifest_bytes))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    manifest = _read_manifest(source)
    _build(source, args.output, manifest)
    _build(source, args.twin, manifest)
    if _sha(args.output) != _sha(args.twin):
        raise RuntimeError("Goal5784 targeted data twin differs")
    print(json.dumps({
        "source_archive_sha256": _sha(source),
        "targeted_data_archive_sha256": _sha(args.output),
        "selected_payload_count": len(SELECTED),
        "selected_payload_bytes": sum(
            int(row["size_bytes"]) for row in manifest["files"]
            if row["path"] in SELECTED),
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
