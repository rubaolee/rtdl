#!/usr/bin/env python3
"""Build the deterministic self-contained Goal5749 RTX functional bundle."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import pathlib
import re
import tarfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXECUTOR = ROOT / "scripts/goal5749_modern_rtx_executor.sh"
CUDA_DEBS = (
    "cuda-cccl-12-8_12.8.90-1_amd64.deb",
    "cuda-crt-12-8_12.8.93-1_amd64.deb",
    "cuda-cudart-dev-12-8_12.8.90-1_amd64.deb",
    "cuda-driver-dev-12-8_12.8.90-1_amd64.deb",
    "cuda-nvcc-12-8_12.8.93-1_amd64.deb",
    "cuda-nvrtc-12-8_12.8.93-1_amd64.deb",
    "cuda-nvrtc-dev-12-8_12.8.93-1_amd64.deb",
    "cuda-nvvm-12-8_12.8.93-1_amd64.deb",
)
WHEEL_PREFIXES = (
    "llvmlite-0.47.0-",
    "numba-0.65.1-",
    "numpy-2.2.6-",
    "nvidia_cuda_nvcc_cu12-12.8.93-",
    "nvidia_cuda_nvrtc_cu12-12.8.93-",
    "nvidia_cuda_runtime_cu12-12.8.90-",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read(path: pathlib.Path) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_bytes()


def member(name: str, data: bytes, *, executable: bool = False) -> tuple[str, bytes, int]:
    return name, data, 0o755 if executable else 0o644


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-archive", required=True, type=pathlib.Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--optix-include", required=True, type=pathlib.Path)
    parser.add_argument("--cuda-debs", required=True, type=pathlib.Path)
    parser.add_argument("--wheelhouse", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{9,40}", args.source_commit):
        raise ValueError("source commit must be an exact lowercase Git identity")

    source = read(args.source_archive)
    source_sha = sha(source)
    executor = read(EXECUTOR).decode("utf-8").replace("\r\n", "\n")
    if "\r" in executor:
        raise ValueError("executor contains a noncanonical carriage return")
    if executor.count("@SOURCE_ARCHIVE_SHA256@") != 2 or executor.count("@SOURCE_COMMIT@") != 2:
        raise ValueError("executor placeholder cardinality changed")
    executor = executor.replace("@SOURCE_ARCHIVE_SHA256@", source_sha).replace(
        "@SOURCE_COMMIT@", args.source_commit)

    members: list[tuple[str, bytes, int]] = [
        member("goal5749_modern_rtx_executor.sh", executor.encode(), executable=True),
        member("payload/source.tar.gz", source),
        member("payload/optix9_include.tar.gz", read(args.optix_include)),
    ]
    for name in CUDA_DEBS:
        members.append(member(f"payload/cuda_debs/{name}", read(args.cuda_debs / name)))
    wheels = sorted(path for path in args.wheelhouse.iterdir() if path.is_file())
    for prefix in WHEEL_PREFIXES:
        matches = [path for path in wheels if path.name.startswith(prefix)]
        if len(matches) != 1:
            raise ValueError(f"expected exactly one wheel with prefix {prefix!r}, got {matches}")
        path = matches[0]
        members.append(member(f"payload/wheelhouse/{path.name}", read(path)))

    payload_lines = [
        f"{sha(data)}  {name}"
        for name, data, _ in members if name.startswith("payload/")
    ]
    members.append(member("BUNDLE_PAYLOADS.sha256", ("\n".join(payload_lines) + "\n").encode()))
    manifest = [{"path": name, "size": len(data), "sha256": sha(data)}
                for name, data, _ in members]
    manifest.append({
        "schema": "rtdl.goal5749.modern_rtx_bundle.v1",
        "source_commit": args.source_commit,
        "source_archive_sha256": source_sha,
        "functional_only": True,
        "registered_performance_timing_allowed": False,
    })
    members.append(member("BUNDLE_MANIFEST.json",
                          (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    with args.output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=6) as zipped:
            with tarfile.open(mode="w", fileobj=zipped, format=tarfile.GNU_FORMAT) as archive:
                for name, data, mode in members:
                    info = tarfile.TarInfo(name)
                    info.size = len(data); info.mode = mode
                    info.mtime = 0; info.uid = 0; info.gid = 0
                    info.uname = ""; info.gname = ""
                    archive.addfile(info, io.BytesIO(data))
    print(json.dumps({"output": str(args.output), "size": args.output.stat().st_size,
                      "sha256": sha(args.output.read_bytes()), "members": len(members)},
                     sort_keys=True))


if __name__ == "__main__":
    main()
