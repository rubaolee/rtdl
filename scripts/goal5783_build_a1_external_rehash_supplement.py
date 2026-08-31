"""Package the frozen Goal5782 source and Goal5783 A1 proof for reviewers."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


PAYLOADS = (
    "history/internal_docs/goal5782_portable_source_v5_20260814.tar.gz",
    "history/internal_docs/goal5783_frozen_core_audit_20260814.json",
    "history/internal_docs/review_goal5783_postfreeze_held_out_rtxrmq_20260814.md",
    "history/internal_docs/goal5783_owner_returned_external_review_absorption_20260814.json",
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
    "tests/goal5783_postfreeze_rtxrmq_exam_test.py",
    "history/internal_docs/goal5783_amendment_a1_external_audit_convenience_20260814/FUNCTIONAL_RECEIPT.json",
    "history/internal_docs/goal5783_amendment_a1_external_audit_convenience_20260814/INDEPENDENT_RECOUNT.json",
    "history/internal_docs/goal5783_amendment_a1_external_audit_convenience_20260814/stdout.json",
    "history/internal_docs/goal5783_amendment_a1_external_audit_convenience_20260814/stderr.log",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add(handle: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data); info.mtime = 0; info.uid = info.gid = 0
    info.uname = info.gname = ""; info.mode = 0o644
    handle.addfile(info, io.BytesIO(data))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    blobs = [(name, (root / name).read_bytes()) for name in PAYLOADS]
    manifest = {
        "schema": "rtdl.goal5783.amendment_a1_external_rehash_manifest.v1",
        "payload_count": len(blobs),
        "payload_bytes": sum(len(data) for _, data in blobs),
        "payloads": [
            {"path": name, "size": len(data), "sha256": sha(data)}
            for name, data in blobs
        ],
    }
    manifest_bytes = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w") as handle:
                for name, data in blobs:
                    add(handle, name, data)
                add(handle, "GOAL5783_AMENDMENT_A1_MANIFEST.json", manifest_bytes)
    print(json.dumps({
        "archive_sha256": sha(args.output.read_bytes()),
        "payload_count": len(blobs),
        "payload_bytes": manifest["payload_bytes"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
