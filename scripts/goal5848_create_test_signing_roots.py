#!/usr/bin/env python3
"""Create two test-only signing roots for exact Goal5848 AOT requests."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path

from experiments.goal5848_strong_baseline.contracts import digest, strict_json_loads
from experiments.goal5848_strong_baseline.controller import _new_output_root
from scripts.goal5801_rtdlexe_trust import create_root


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_create(path: Path, value: dict[str, object]) -> None:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    try:
        payload = json.dumps(value, indent=2, sort_keys=True).encode("ascii") + b"\n"
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    root = _new_output_root(args.output_root)
    root.mkdir(parents=True)
    rows = {}
    for label in ("relation", "triangle"):
        private = root / f"{label}.private.json"
        public = root / f"{label}.public.json"
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            create_root(
                private_path=private,
                public_path=public,
                key_id=f"TEST_ONLY_goal5848_{label}",
                bits=2048,
            )
        creation_row = strict_json_loads(
            captured.getvalue(),
            label=f"Goal5848 signing-root creation {label}",
        )
        if (
            creation_row.get("key_id") != f"TEST_ONLY_goal5848_{label}"
            or creation_row.get("production_key_custody_attested") is not False
        ):
            raise RuntimeError("Goal5848 signing-root creation receipt differs")
        rows[label] = {
            "private_path": str(private.resolve(strict=True)),
            "private_sha256": _sha256(private),
            "public_path": str(public.resolve(strict=True)),
            "public_sha256": _sha256(public),
            "trust_root_sha256": creation_row["trust_root_sha256"],
        }
    value = {
        "schema": "rtdl.goal5848.test_signing_roots.v1",
        "status": "PASS__TWO_DISTINCT_TEST_ONLY_ROOTS_CREATED",
        "rows": rows,
        "private_key_paths_must_be_unlinked_by_aot_builder": True,
        "production_key_custody_attested": False,
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    value["receipt_sha256"] = digest(value)
    _write_create(root / "receipt.json", value)
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
