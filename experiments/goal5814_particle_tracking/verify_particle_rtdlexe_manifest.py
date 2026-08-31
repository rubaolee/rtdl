#!/usr/bin/env python3
"""Verify and public-load Goal5814 from an externally supplied manifest hash."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


def _require_sha(value: object, path: str) -> str:
    if (not isinstance(value, str) or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)):
        raise RuntimeError(f"invalid SHA-256 at {path}")
    return value


def _create_or_exact(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        if path.read_bytes() != payload:
            raise RuntimeError(f"create-only collision: {path}")
        return
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _load_manifest(path: Path, expected_sha256: str) -> dict[str, object]:
    expected_sha256 = _require_sha(expected_sha256, "expected_manifest_sha256")
    raw = path.expanduser().resolve(strict=True).read_bytes()
    if _sha_bytes(raw) != expected_sha256:
        raise RuntimeError("EXTERNAL_EXECUTABLE_MANIFEST_IDENTITY_MISMATCH")
    value = json.loads(raw)
    if (value.get("schema")
            != "rtdl.goal5814.particle_strict_interior_executable_manifest.v1"):
        raise RuntimeError("EXECUTABLE_MANIFEST_SCHEMA_MISMATCH")
    body = dict(value)
    seal = body.pop("manifest_body_sha256", None)
    if _require_sha(seal, "manifest_body_sha256") != _sha_bytes(_canonical(body)):
        raise RuntimeError("EXECUTABLE_MANIFEST_BODY_SEAL_MISMATCH")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.manifest.expanduser().resolve(strict=True)
    manifest = _load_manifest(
        manifest_path, args.expected_manifest_sha256)
    identities = manifest.get("identities")
    if not isinstance(identities, dict):
        raise RuntimeError("EXECUTABLE_MANIFEST_IDENTITIES_MISSING")
    artifact_path = (
        args.artifact.expanduser().resolve(strict=True) if args.artifact
        else Path(str(identities["artifact_absolute_path"])).resolve(strict=True))
    native_path = (
        args.native.expanduser().resolve(strict=True) if args.native
        else Path(str(identities["native_absolute_path"])).resolve(strict=True))

    before_modules = set(sys.modules)
    from rtdsl import (  # pylint: disable=import-outside-toplevel
        install_particle_rtdlexe_deployment,
        load_particle_rtdlexe,
    )
    deployment = install_particle_rtdlexe_deployment(
        deployment_id="goal5814/external-manifest-authority-kat/v1",
        expected_artifact_sha256=_require_sha(
            identities["artifact_sha256"], "artifact_sha256"),
        expected_native_sha256=_require_sha(
            identities["native_sha256"], "native_sha256"),
        expected_protocol_decision_sha256=_require_sha(
            manifest["standard_protocol"]["decision_sha256"],
            "protocol_decision_sha256"),
        expected_template_semantic_sha256=_require_sha(
            identities["template_semantic_sha256"],
            "template_semantic_sha256"),
    )
    loaded = load_particle_rtdlexe(
        artifact_path, deployment=deployment,
        native_library_path=native_path)
    try:
        observed = {
            "artifact_sha256": loaded.artifact_sha256,
            "ptx_sha256": loaded.ptx_sha256,
            "ptx_bytes": len(loaded.ptx_bytes),
        }
    finally:
        loaded.close()
    new_modules = set(sys.modules) - before_modules
    forbidden = sorted(
        name for name in new_modules
        if name.startswith("numba")
        or (name.startswith("rtdsl.") and any(
            marker in name.lower()
            for marker in ("compiler", "numba", "nvrtc")))
    )
    if forbidden:
        raise RuntimeError(f"CACHE_HIT_IMPORTED_COMPILER_PATH: {forbidden}")
    body = {
        "schema": "rtdl.goal5814.particle_rtdlexe_external_manifest_load_kat.v1",
        "status": "PASS__EXTERNAL_MANIFEST_AUTHORITY__PUBLIC_LOAD_CLOSE",
        "external_expected_manifest_sha256": args.expected_manifest_sha256,
        "external_expected_supplied_via_cli": True,
        "artifact_path": str(artifact_path),
        "native_path": str(native_path),
        **observed,
        "forbidden_cache_hit_imports": forbidden,
        "prepare_execute_attempted": False,
        "registered_timing_count": 0,
        "capability_serialized": False,
    }
    result = {**body, "result_body_sha256": _sha_bytes(_canonical(body))}
    payload = json.dumps(
        result, indent=2, sort_keys=True, ensure_ascii=False,
        allow_nan=False).encode("utf-8") + b"\n"
    result_path = args.result.expanduser().resolve()
    _create_or_exact(result_path, payload)
    print(json.dumps({
        "status": result["status"],
        "result_path": str(result_path),
        "result_file_sha256": _sha_bytes(payload),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
