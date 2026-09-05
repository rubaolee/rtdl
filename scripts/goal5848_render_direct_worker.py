#!/usr/bin/env python3
"""Derive the Goal5848 Direct worker from the audited Goal5802 source.

Only the preregistered warmup and retained-sample counts change.  The renderer
fails closed if the frozen parent source or either exact replacement drifts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from experiments.goal5848_strong_baseline.controller import _new_output_root

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"
PARENT_SHA256 = "078570a19000221890bd5421676c8d4857fd2196c5b7daae60eec7d511ffd165"
REPLACEMENTS = (
    (
        b"constexpr int kSteadyWarmups = 8;",
        b"constexpr int kSteadyWarmups = 16;",
    ),
    (
        b"constexpr int kSteadyRepetitions = 64;",
        b"constexpr int kSteadyRepetitions = 128;",
    ),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def render(parent: Path = PARENT) -> tuple[bytes, dict[str, object]]:
    source = parent.resolve(strict=True).read_bytes()
    if sha256_bytes(source) != PARENT_SHA256:
        raise RuntimeError("Goal5848 Direct parent source identity differs")
    rendered = source
    rows = []
    for before, after in REPLACEMENTS:
        if rendered.count(before) != 1 or rendered.count(after) != 0:
            raise RuntimeError("Goal5848 Direct exact replacement differs")
        rendered = rendered.replace(before, after)
        rows.append({
            "before_utf8": before.decode("ascii"),
            "after_utf8": after.decode("ascii"),
        })
    receipt = {
        "schema": "rtdl.goal5848.direct_source_derivation.v1",
        "status": "PASS__EXACT_TWO_CONSTANT_DERIVATION",
        "parent_relative_path": PARENT.relative_to(ROOT).as_posix(),
        "parent_sha256": PARENT_SHA256,
        "derived_sha256": sha256_bytes(rendered),
        "replacements": rows,
        "semantic_change": (
            "warmups_8_to_16_and_retained_repetitions_64_to_128_only"
        ),
        "optix_cuda_or_output_logic_changed": False,
        "public_or_manuscript_claim_authorized": False,
    }
    receipt["receipt_sha256"] = sha256_bytes(
        json.dumps(
            receipt,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    )
    return rendered, receipt


def write_create(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
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
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    source, receipt = render()
    output = _new_output_root(args.output)
    receipt_path = _new_output_root(args.receipt)
    if output == receipt_path:
        raise ValueError("Goal5848 Direct source and receipt paths must differ")
    write_create(output, source)
    write_create(
        receipt_path,
        json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n",
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
