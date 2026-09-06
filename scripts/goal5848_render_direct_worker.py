#!/usr/bin/env python3
"""Derive a portable Goal5848 Direct source bundle from Goal5802.

Only the preregistered warmup and retained-sample counts change in the worker.
The frozen relative include is copied as exact regular bytes so the generated
translation unit remains buildable outside the repository.  The renderer fails
closed if either source or either exact replacement drifts.
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
INCLUDE_DEPENDENCY = ROOT / "experiments/goal5796_matched/direct_optix.cpp"
INCLUDE_DEPENDENCY_SHA256 = (
    "2533a14152e441f97690e8e427e97f1be5f1747ee8faa0f181cd05b438a01383"
)
INCLUDE_DIRECTIVE = b'#include "../goal5796_matched/direct_optix.cpp"'
DERIVED_SOURCE_RELATIVE_PATH = (
    "source/goal5802_premeasurement/direct_worker.cpp"
)
INCLUDE_DEPENDENCY_RELATIVE_PATH = (
    "source/goal5796_matched/direct_optix.cpp"
)
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


def render(
    parent: Path = PARENT,
    include_dependency: Path = INCLUDE_DEPENDENCY,
) -> tuple[bytes, bytes, dict[str, object]]:
    source = parent.resolve(strict=True).read_bytes()
    if sha256_bytes(source) != PARENT_SHA256:
        raise RuntimeError("Goal5848 Direct parent source identity differs")
    dependency = include_dependency.resolve(strict=True).read_bytes()
    if sha256_bytes(dependency) != INCLUDE_DEPENDENCY_SHA256:
        raise RuntimeError("Goal5848 Direct include dependency identity differs")
    if source.count(INCLUDE_DIRECTIVE) != 1:
        raise RuntimeError("Goal5848 Direct relative include directive differs")
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
        "schema": "rtdl.goal5848.direct_source_derivation.v2",
        "status": (
            "PASS__PINNED_INCLUDE_BUNDLE_AND_EXACT_TWO_CONSTANT_DERIVATION"
        ),
        "parent_relative_path": PARENT.relative_to(ROOT).as_posix(),
        "parent_sha256": PARENT_SHA256,
        "derived_sha256": sha256_bytes(rendered),
        "derived_source_bundle_relative_path": DERIVED_SOURCE_RELATIVE_PATH,
        "include_dependency": {
            "directive_utf8": INCLUDE_DIRECTIVE.decode("ascii"),
            "source_relative_path": INCLUDE_DEPENDENCY.relative_to(ROOT).as_posix(),
            "bundle_relative_path": INCLUDE_DEPENDENCY_RELATIVE_PATH,
            "bytes": len(dependency),
            "sha256": INCLUDE_DEPENDENCY_SHA256,
            "regular_file_required": True,
            "semantic_change": False,
        },
        "replacements": rows,
        "semantic_change": (
            "source_bundle_copies_one_pinned_relative_include_without_semantic_"
            "change; worker_changes_only_warmups_8_to_16_and_retained_"
            "repetitions_64_to_128"
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
    return rendered, dependency, receipt


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
    parser.add_argument("--include-dependency-output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    source, dependency, receipt = render()
    output = _new_output_root(args.output)
    dependency_output = _new_output_root(args.include_dependency_output)
    receipt_path = _new_output_root(args.receipt)
    bundle_root = receipt_path.parent
    expected_output = bundle_root / DERIVED_SOURCE_RELATIVE_PATH
    expected_dependency_output = bundle_root / INCLUDE_DEPENDENCY_RELATIVE_PATH
    if output != expected_output or dependency_output != expected_dependency_output:
        raise ValueError("Goal5848 Direct source bundle layout differs")
    if len({output, dependency_output, receipt_path}) != 3:
        raise ValueError("Goal5848 Direct bundle output paths must differ")
    write_create(output, source)
    write_create(dependency_output, dependency)
    write_create(
        receipt_path,
        json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n",
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
