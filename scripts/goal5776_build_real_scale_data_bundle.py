#!/usr/bin/env python3
"""Build the exact, deterministic real-scale data bundle for Goal5776."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _add_bytes(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def _add_file(archive: tarfile.TarFile, name: str, source: Path) -> None:
    info = tarfile.TarInfo(name)
    info.size = source.stat().st_size
    info.mtime = 0
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    with source.open("rb") as stream:
        archive.addfile(info, stream)


def _files(root: Path, archive_prefix: str) -> list[tuple[str, Path]]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"data root must be a real directory: {root}")
    rows = []
    for source in sorted(root.rglob("*")):
        if source.is_dir():
            continue
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"unsupported data member: {source}")
        relative = source.relative_to(root).as_posix()
        destination = str(PurePosixPath(archive_prefix) / relative)
        rows.append((destination, source))
    if not rows:
        raise ValueError(f"empty data root: {root}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--common-root", type=Path, required=True)
    parser.add_argument("--particle-root", type=Path, required=True)
    parser.add_argument("--rtnn-root", type=Path, required=True)
    parser.add_argument("--xhd-root", type=Path, required=True)
    parser.add_argument("--rtdbscan-root", type=Path, required=True)
    parser.add_argument("--triangle-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    selected: list[tuple[str, Path]] = []
    common = args.common_root.resolve()
    common_files = (
        "librts/parks/cache/parks_bz2.json",
        "librts/parks/cache/parks_bz2.npz",
        "librts/parks/queries/point_contains_100000.wkt",
        "librts/parks/queries/range_contains_100000.wkt",
        "raydb/q11/data.bin",
        "raydb/q11/expected_rows.json",
        "raydb/q11/packet.json",
        "raydb/q11/predicate.txt",
        "rayjoin/top4_county.cdb",
        "rayjoin/top4_zipcode.cdb",
        "rt_barneshut/expected_forces.txt",
        "rt_barneshut/prepared_arrays.json",
    )
    for relative in common_files:
        source = common / relative
        if source.is_symlink() or not source.is_file():
            raise FileNotFoundError(source)
        selected.append((f"DATA/common/{relative}", source))
    for root, prefix in (
        (args.particle_root.resolve(), "DATA/particle"),
        (args.rtnn_root.resolve(), "DATA/rtnn"),
        (args.xhd_root.resolve(), "DATA/xhd"),
        (args.rtdbscan_root.resolve(), "DATA/rtdbscan"),
        (args.triangle_root.resolve(), "DATA/triangle"),
    ):
        selected.extend(_files(root, prefix))
    names = [name for name, _ in selected]
    if len(names) != len(set(names)):
        raise RuntimeError("duplicate Goal5776 data member")
    rows = [{
        "path": name,
        "size_bytes": source.stat().st_size,
        "sha256": _sha_file(source),
    } for name, source in selected]
    manifest = {
        "schema": "rtdl.goal5776.real_scale_data_manifest.v1",
        "paper_app_count": 9,
        "functional_execution_unit_count": 32,
        "formal_execution_unit_count": 15,
        "file_count": len(rows),
        "payload_bytes": sum(int(row["size_bytes"]) for row in rows),
        "files": rows,
    }
    manifest_bytes = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = output.with_name(output.name + ".partial")
    if temporary.exists():
        raise FileExistsError(temporary)
    try:
        with temporary.open("xb") as raw:
            with gzip.GzipFile(
                fileobj=raw, mode="wb", filename="", mtime=0,
            ) as compressed:
                with tarfile.open(
                    fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT,
                ) as archive:
                    for name, source in sorted(selected):
                        _add_file(archive, name, source)
                    _add_bytes(archive, "DATA_MANIFEST.json", manifest_bytes)
        temporary.replace(output)
    except Exception:
        # Preserve a partial build for diagnosis; never relabel it as complete.
        raise
    print(json.dumps({
        "archive": str(output),
        "archive_sha256": _sha_file(output),
        "file_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
