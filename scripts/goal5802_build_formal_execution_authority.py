#!/usr/bin/env python3
"""Create the exact Goal5802 formal authority after review and owner approval.

This helper is intentionally outside the frozen measurement source.  It does
not authorize anything by itself: all four affirmative gates and the external
P0/P1 verdict must be supplied explicitly, and the controller's validator
checks the resulting bytes before worker zero.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.goal5802_premeasurement import contract
from experiments.goal5802_premeasurement.controller import (
    AUTHORITY_SCHEMA,
    OWNER_WAIVER_AUTHORITY_SCHEMA,
    OWNER_WAIVER_REASON,
    validate_execution_authority,
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_authority(
        *, freeze: Path, runtime_manifest: Path, external_cfr: Path,
        expected_external_cfr_sha256: str, external_review_p0: int,
        external_review_p1: int, external_exact_byte_approval: bool,
        owner_execution_authorized: bool,
        formal_worker_zero_authorized: bool,
        pod_gpu_timing_authorized: bool) -> dict[str, Any]:
    freeze = freeze.resolve(strict=True)
    runtime_manifest = runtime_manifest.resolve(strict=True)
    external_cfr = external_cfr.resolve(strict=True)
    for path in (freeze, runtime_manifest, external_cfr):
        if not path.is_file():
            raise RuntimeError(f"Goal5802 authority input is not a file: {path}")
    cfr_sha = _sha(external_cfr)
    if cfr_sha != expected_external_cfr_sha256:
        raise RuntimeError(
            "Goal5802 external CFR differs from the exact reviewed bytes")
    authority: dict[str, Any] = {
        "schema": AUTHORITY_SCHEMA,
        "freeze_file_sha256": _sha(freeze),
        "runtime_manifest_file_sha256": _sha(runtime_manifest),
        "external_cfr_sha256": cfr_sha,
        "external_review_p0": external_review_p0,
        "external_review_p1": external_review_p1,
        "external_exact_byte_approval": external_exact_byte_approval,
        "owner_execution_authorized": owner_execution_authorized,
        "formal_worker_zero_authorized": formal_worker_zero_authorized,
        "pod_gpu_timing_authorized": pod_gpu_timing_authorized,
    }
    authority["execution_authority_sha256"] = hashlib.sha256(
        contract.canonical(authority)).hexdigest()
    validate_execution_authority(
        authority,
        freeze_sha256=authority["freeze_file_sha256"],
        runtime_manifest_sha256=authority["runtime_manifest_file_sha256"],
    )
    return authority


def build_owner_waiver_authority(
        *, freeze: Path, runtime_manifest: Path, preexecution_cfr: Path,
        expected_preexecution_cfr_sha256: str,
        owner_explicit_external_review_waiver: bool,
        owner_waiver_reason: str, owner_execution_authorized: bool,
        formal_worker_zero_authorized: bool,
        pod_gpu_timing_authorized: bool) -> dict[str, Any]:
    """Build an honest owner-waiver authority without an external-review claim."""

    freeze = freeze.resolve(strict=True)
    runtime_manifest = runtime_manifest.resolve(strict=True)
    preexecution_cfr = preexecution_cfr.resolve(strict=True)
    for path in (freeze, runtime_manifest, preexecution_cfr):
        if not path.is_file():
            raise RuntimeError(
                f"Goal5802 owner-waiver authority input is not a file: {path}")
    cfr_sha = _sha(preexecution_cfr)
    if cfr_sha != expected_preexecution_cfr_sha256:
        raise RuntimeError(
            "Goal5802 preexecution CFR differs from the owner-approved bytes")
    authority: dict[str, Any] = {
        "schema": OWNER_WAIVER_AUTHORITY_SCHEMA,
        "freeze_file_sha256": _sha(freeze),
        "runtime_manifest_file_sha256": _sha(runtime_manifest),
        "preexecution_cfr_sha256": cfr_sha,
        "external_preexecution_review_claimed": False,
        "external_exact_byte_approval": False,
        "owner_explicit_external_review_waiver":
            owner_explicit_external_review_waiver,
        "owner_waiver_reason": owner_waiver_reason,
        "owner_execution_authorized": owner_execution_authorized,
        "formal_worker_zero_authorized": formal_worker_zero_authorized,
        "pod_gpu_timing_authorized": pod_gpu_timing_authorized,
    }
    authority["execution_authority_sha256"] = hashlib.sha256(
        contract.canonical(authority)).hexdigest()
    validate_execution_authority(
        authority,
        freeze_sha256=authority["freeze_file_sha256"],
        runtime_manifest_sha256=authority["runtime_manifest_file_sha256"],
    )
    return authority


def _write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.resolve(strict=True)
    payload = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with path.open("xb") as handle:
        handle.write(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--external-cfr", type=Path, required=True)
    parser.add_argument("--expected-external-cfr-sha256", required=True)
    parser.add_argument("--external-review-p0", type=int)
    parser.add_argument("--external-review-p1", type=int)
    parser.add_argument("--external-exact-byte-approval", action="store_true")
    parser.add_argument(
        "--owner-explicit-external-review-waiver", action="store_true")
    parser.add_argument("--owner-waiver-reason")
    parser.add_argument("--owner-execution-authorized", action="store_true")
    parser.add_argument("--formal-worker-zero-authorized", action="store_true")
    parser.add_argument("--pod-gpu-timing-authorized", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.owner_explicit_external_review_waiver:
        if args.external_review_p0 is not None \
                or args.external_review_p1 is not None \
                or args.external_exact_byte_approval:
            parser.error(
                "owner-waiver mode forbids every external-review claim")
        authority = build_owner_waiver_authority(
            freeze=args.freeze,
            runtime_manifest=args.runtime_manifest,
            preexecution_cfr=args.external_cfr,
            expected_preexecution_cfr_sha256=
                args.expected_external_cfr_sha256,
            owner_explicit_external_review_waiver=True,
            owner_waiver_reason=args.owner_waiver_reason or "",
            owner_execution_authorized=args.owner_execution_authorized,
            formal_worker_zero_authorized=args.formal_worker_zero_authorized,
            pod_gpu_timing_authorized=args.pod_gpu_timing_authorized,
        )
    else:
        if args.external_review_p0 is None \
                or args.external_review_p1 is None:
            parser.error(
                "external-review mode requires P0 and P1 verdicts")
        if args.owner_waiver_reason is not None:
            parser.error(
                "external-review mode forbids an owner-waiver reason")
        authority = build_authority(
            freeze=args.freeze,
            runtime_manifest=args.runtime_manifest,
            external_cfr=args.external_cfr,
            expected_external_cfr_sha256=args.expected_external_cfr_sha256,
            external_review_p0=args.external_review_p0,
            external_review_p1=args.external_review_p1,
            external_exact_byte_approval=args.external_exact_byte_approval,
            owner_execution_authorized=args.owner_execution_authorized,
            formal_worker_zero_authorized=args.formal_worker_zero_authorized,
            pod_gpu_timing_authorized=args.pod_gpu_timing_authorized,
        )
    _write_new(args.output, authority)
    print(json.dumps({
        "status": "PASS__GOAL5802_FORMAL_EXECUTION_AUTHORITY_CREATED",
        "output": str(args.output.resolve(strict=True)),
        "output_file_sha256": _sha(args.output),
        "execution_authority_sha256": authority[
            "execution_authority_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
