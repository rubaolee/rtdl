#!/usr/bin/env python3
"""Build deterministic Goal5769 Home functional evidence and an exact twin."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith(".py") else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return output.getvalue()


def add_file(payloads: dict[str, bytes], name: str, path: Path) -> None:
    if not path.is_file() or name in payloads:
        raise RuntimeError(f"missing/duplicate evidence payload: {name}")
    payloads[name] = path.read_bytes()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--recount", type=Path, required=True)
    parser.add_argument("--self-review", type=Path, required=True)
    parser.add_argument("--hard-stop-review", type=Path, required=True)
    parser.add_argument("--core-manifest", type=Path, required=True)
    parser.add_argument("--failure-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output, args.twin):
        if path.exists():
            raise FileExistsError(path)

    root = args.result_root.resolve()
    payloads: dict[str, bytes] = {}
    for name in (
        "RESULT.json", "EXECUTION_SOURCE.tar.gz", "librtdl_optix.so",
        "FIXED_RADIUS_REFINEMENT_EVIDENCE.json",
        "FIXED_RADIUS_REMATERIALIZATION.json", "RUNTIME.json",
    ):
        add_file(payloads, f"HOME_RESULT/{name}", root / name)
    for directory in ("functional_raw", "logs"):
        for path in sorted((root / directory).glob("*")):
            if path.is_file():
                add_file(payloads, f"HOME_RESULT/{directory}/{path.name}", path)
    add_file(payloads, "INDEPENDENT_RECOUNT.json", args.recount.resolve())
    add_file(payloads, "TOOLS/goal5769_recount_home_functional.py",
             Path(__file__).resolve().parent / "goal5769_recount_home_functional.py")
    add_file(payloads, "SELF_REVIEW.md", args.self_review.resolve())
    add_file(payloads, "PREEXECUTION_HARD_STOP_REVIEW.md",
             args.hard_stop_review.resolve())
    add_file(payloads, "CORE_SUCCESSOR_MANIFEST.json", args.core_manifest.resolve())
    for path in sorted(args.failure_root.resolve().rglob("*")):
        if path.is_file():
            name = "PRESERVED_FAILURES/" + path.relative_to(
                args.failure_root.resolve()).as_posix()
            add_file(payloads, name, path)

    bundle = args.bundle.resolve()
    with tarfile.open(bundle, "r:gz") as outer:
        member = outer.getmember("PORTABLE_MANIFEST.json")
        handle = outer.extractfile(member)
        if handle is None:
            raise RuntimeError("bundle portable manifest unreadable")
        payloads["BUNDLE_PORTABLE_MANIFEST.json"] = handle.read()

    rows = [
        {"path": name, "sha256": sha(data), "size_bytes": len(data)}
        for name, data in sorted(payloads.items())
    ]
    result = json.loads(payloads["HOME_RESULT/RESULT.json"])
    recount = json.loads(payloads["INDEPENDENT_RECOUNT.json"])
    if result["bundle_sha256"] != sha(bundle.read_bytes()) \
            or recount["bundle_sha256"] != result["bundle_sha256"]:
        raise RuntimeError("bundle/result/recount identity mismatch")
    manifest = {
        "schema": "rtdl.goal5769.home_functional_evidence_manifest.v1",
        "goal": 5769,
        "scope": "Home Linux clean functional evidence; no formal performance",
        "companion_bundle_path": bundle.name,
        "companion_bundle_sha256": result["bundle_sha256"],
        "companion_bundle_size_bytes": bundle.stat().st_size,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    payloads["EVIDENCE_MANIFEST.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    evidence = archive(payloads)
    args.output.write_bytes(evidence)
    args.twin.write_bytes(evidence)
    if args.output.read_bytes() != args.twin.read_bytes():
        raise RuntimeError("Goal5769 evidence twin differs")
    print(json.dumps({
        "evidence_sha256": sha(evidence),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
