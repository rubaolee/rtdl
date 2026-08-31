#!/usr/bin/env python3
"""Run one Goal5814 untimed KAT and bind its otherwise omitted entry mode.

The underlying KAT result intentionally describes GPU operations and outcomes,
but its v1 schema does not say whether the complete-public or exact-core entry
point produced those bytes.  This wrapper leaves that result untouched and
creates a separate, create-only receipt that binds the reviewed branch, wrapper
source, manifest, and exact underlying result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import experiments.goal5814_particle.untimed_dual_arm_kat as kat


RECEIPT_SCHEMA = "rtdl.goal5814.entry_bound_untimed_kat_receipt.v1"


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_record(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "bytes": len(payload),
        "path": str(path),
        "sha256": _sha(payload),
    }


def _argument_value(arguments: list[str], name: str) -> str:
    try:
        return arguments[arguments.index(name) + 1]
    except (ValueError, IndexError) as exc:
        raise SystemExit(f"missing underlying KAT argument: {name}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run and mode-bind one create-only Goal5814 untimed KAT")
    parser.add_argument("mode", choices=("complete", "exact-core"))
    parser.add_argument("--binding-receipt", required=True, type=Path)
    known, kat_arguments = parser.parse_known_args(argv)

    manifest_path = Path(_argument_value(
        kat_arguments, "--executable-manifest")).resolve(strict=True)
    result_path = Path(_argument_value(
        kat_arguments, "--output")).resolve(strict=False)
    binding_path = known.binding_receipt.resolve(strict=False)
    if binding_path.exists() or binding_path.is_symlink():
        raise FileExistsError(binding_path)

    manifest_payload = manifest_path.read_bytes()
    kat.FORMAL_EXECUTABLE_MANIFEST_BYTES = len(manifest_payload)
    kat.FORMAL_EXECUTABLE_MANIFEST_SHA256 = _sha(manifest_payload)

    if known.mode == "complete":
        entrypoint = "untimed_dual_arm_kat.main"
        return_code = kat.main(kat_arguments)
    else:
        entrypoint = "untimed_dual_arm_kat.main_exact_core_boundary"
        return_code = kat.main_exact_core_boundary(kat_arguments)
    if return_code != 0:
        return return_code

    result_record = _file_record(result_path.resolve(strict=True))
    result_value = json.loads(result_path.read_text(encoding="utf-8"))
    if result_value.get("status") != "PASS__UNTIMED_DUAL_ARM_KAT" \
            or result_value.get("timed") is not False \
            or result_value.get("retry_count") != 0 \
            or result_value.get("replacement_count") != 0:
        raise RuntimeError("underlying Goal5814 KAT result boundary differs")

    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "status": "PASS__ENTRY_MODE_BOUND_TO_UNTIMED_KAT_RESULT",
        "entry_mode": known.mode,
        "entrypoint": entrypoint,
        "wrapper_source": _file_record(Path(__file__).resolve(strict=True)),
        "executable_manifest": _file_record(manifest_path),
        "underlying_kat_result": result_record,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "retry_count": 0,
        "replacement_count": 0,
    }
    receipt["receipt_sha256"] = _sha(_canonical(receipt))
    encoded = json.dumps(
        receipt, allow_nan=False, indent=2, sort_keys=True,
    ).encode("utf-8") + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(binding_path, flags, 0o644)
    try:
        offset = 0
        while offset < len(encoded):
            written = os.write(descriptor, encoded[offset:])
            if written <= 0:
                raise RuntimeError("short write of Goal5814 binding receipt")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    print(json.dumps({
        "entry_mode": known.mode,
        "entrypoint": entrypoint,
        "receipt_sha256": receipt["receipt_sha256"],
        "result_sha256": result_record["sha256"],
        "status": receipt["status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
