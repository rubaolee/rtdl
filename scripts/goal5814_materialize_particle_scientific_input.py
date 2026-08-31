#!/usr/bin/env python3
"""Create the durable Goal5814 Particle Tracking scientific-input root.

This is a create-only custody operation.  It accepts only the already frozen
Goal5776 v2 input manifest, copies its seven NumPy payloads byte-for-byte, adds
the exact public RTxAdvect VTU source, and emits a path-independent manifest.
It never imports RTDL, PyOptiX, or an application execution route.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil


POLICY_RELATIVE_PATH = (
    "history/internal_docs/"
    "goal5814_particle_tracking_scientific_scope_and_measurement_policy_"
    "preaction_20260828.json"
)
POLICY_SHA256 = (
    "79f0d56f8765894666eaaec363f7e149c92de68e85d35ce43d3aa765132e625e"
)
UPSTREAM_MANIFEST_SHA256 = (
    "7f21844610c4c9ad8ccdf6ec6961de28d6f1099af8b1bf0e37e41bf53fb55743"
)
AUTHOR_VTU_SHA256 = (
    "b6be6c692256e73ea9f93d71dc81ad99478b49ec3866a9ab0109da35f72c57b8"
)
AUTHOR_VTU_BYTES = 79_719_401
AUTHOR_COMMIT = "5cfe63fed227c238905a8f24082b59b5d3160966"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _checked_file(path: Path, *, size: int, sha256: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    observed_size = path.stat().st_size
    observed_sha = _sha256(path)
    if observed_size != size or observed_sha != sha256:
        raise RuntimeError({
            "path": str(path),
            "expected_bytes": size,
            "observed_bytes": observed_size,
            "expected_sha256": sha256,
            "observed_sha256": observed_sha,
        })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--author-vtu", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    source_root = args.source_root.resolve()
    author_vtu = args.author_vtu.resolve()
    destination = args.destination.resolve()
    policy = (workspace / POLICY_RELATIVE_PATH).resolve()

    if source_root.name != ".tmp_goal5776_particle_prepared_v2":
        raise RuntimeError(
            "Goal5814 accepts only .tmp_goal5776_particle_prepared_v2; "
            "the superseded v1 root is rejected")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    _checked_file(policy, size=10_431, sha256=POLICY_SHA256)

    upstream_manifest_path = source_root / "MANIFEST.json"
    _checked_file(
        upstream_manifest_path, size=2_692,
        sha256=UPSTREAM_MANIFEST_SHA256)
    upstream = json.loads(upstream_manifest_path.read_text(encoding="utf-8"))
    if upstream.get("schema") != "rtdl.goal5776.particle_real_scale_input.v1":
        raise RuntimeError("unexpected Goal5776 v2 manifest schema")
    if upstream.get("source", {}).get("sha256") != AUTHOR_VTU_SHA256 \
            or upstream.get("source", {}).get("public_author_commit") != AUTHOR_COMMIT:
        raise RuntimeError("Goal5776 v2 author-source authority differs")

    members: list[dict[str, object]] = []
    for name, row in sorted(upstream["members"].items()):
        source = source_root / name
        _checked_file(
            source, size=int(row["size_bytes"]), sha256=str(row["sha256"]))
        members.append({
            "name": name,
            "role": "FROZEN_GOAL5776_V2_NUMPY_PAYLOAD",
            "bytes": int(row["size_bytes"]),
            "sha256": str(row["sha256"]),
            "shape": list(row["shape"]),
            "dtype": str(row["dtype"]),
        })
    _checked_file(author_vtu, size=AUTHOR_VTU_BYTES, sha256=AUTHOR_VTU_SHA256)

    destination.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(upstream_manifest_path, destination / "GOAL5776_MANIFEST.json")
    for row in members:
        name = str(row["name"])
        shutil.copyfile(source_root / name, destination / name)
    shutil.copyfile(author_vtu, destination / "solution_4.vtu")

    payloads = [
        {
            "name": "GOAL5776_MANIFEST.json",
            "role": "BYTE_IDENTICAL_CONTROLLING_GOAL5776_V2_MANIFEST",
            "bytes": 2_692,
            "sha256": UPSTREAM_MANIFEST_SHA256,
        },
        *members,
        {
            "name": "solution_4.vtu",
            "role": "PINNED_PUBLIC_RTXADVECT_SOURCE_MESH",
            "bytes": AUTHOR_VTU_BYTES,
            "sha256": AUTHOR_VTU_SHA256,
        },
    ]
    durable_manifest = {
        "schema": "rtdl.goal5814.particle_tracking_durable_scientific_input.v1",
        "status": "DURABLE_BYTE_IDENTICAL_SUCCESSOR__NO_TMP_RUNTIME_DEPENDENCY",
        "date": "2026-08-28",
        "controlling_policy": {
            "path": POLICY_RELATIVE_PATH,
            "bytes": 10_431,
            "sha256": POLICY_SHA256,
        },
        "source_authority": {
            "project": "RTxAdvect",
            "commit": AUTHOR_COMMIT,
            "repository_path": "dataset/microfludics/solution_4.vtu",
            "bytes": AUTHOR_VTU_BYTES,
            "sha256": AUTHOR_VTU_SHA256,
        },
        "upstream_goal5776_v2_manifest": {
            "copied_name": "GOAL5776_MANIFEST.json",
            "bytes": 2_692,
            "sha256": UPSTREAM_MANIFEST_SHA256,
        },
        "superseded_goal5776_v1_accepted": False,
        "temporary_source_root_required_after_materialization": False,
        "payload_count": len(payloads),
        "payload_bytes": sum(int(row["bytes"]) for row in payloads),
        "payloads": payloads,
        "claim_boundary": {
            "scientific_input_custody_only": True,
            "oracle_rederivation_completed": False,
            "executable_bytes_frozen": False,
            "performance_worker_authorized": False,
        },
    }
    manifest_path = destination / "SCIENTIFIC_INPUT_MANIFEST.json"
    manifest_path.write_bytes(_canonical_bytes(durable_manifest))

    for row in payloads:
        _checked_file(
            destination / str(row["name"]),
            size=int(row["bytes"]), sha256=str(row["sha256"]))

    result = {
        "status": "PASS",
        "destination": str(destination),
        "payload_count": len(payloads),
        "payload_bytes": durable_manifest["payload_bytes"],
        "manifest_bytes": manifest_path.stat().st_size,
        "manifest_sha256": _sha256(manifest_path),
        "superseded_v1_rejected": True,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
