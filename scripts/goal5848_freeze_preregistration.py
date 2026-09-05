#!/usr/bin/env python3
"""Freeze one Goal5848 GPU-generation transaction before worker zero."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from experiments.goal5848_strong_baseline.aot_cache_authority import (
    load_aot_cache_authority,
)
from experiments.goal5848_strong_baseline.contracts import (
    ARMS,
    BLOCKS,
    INSTRUMENTATION_OVERHEAD_LIMIT_PPM,
    PARTITION_ABSOLUTE_TOLERANCE_NS,
    PARTITION_RELATIVE_TOLERANCE_PPM,
    POST_IMPORT_BLOCK_RATIO_LIMIT_PPM,
    POST_IMPORT_RATIO_LIMIT_PPM,
    PREREGISTRATION_ARTIFACT_ARGUMENTS,
    PREREGISTRATION_SCHEMA,
    PRIMARY_ARMS,
    PUBLIC_DIRECT_RATIO_LIMIT_PPM,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    STRONG_COMPETENCE_RATIO_LIMIT_PPM,
    SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM,
    TASK_CONTRACTS,
    TASKS,
    aot_cache_protocol,
    build_schedule,
    digest,
    instrumentation_protocol,
    require_formal_cache_policy,
)
from experiments.goal5848_strong_baseline.controller import _new_output_root
from experiments.goal5848_strong_baseline.device_artifacts import (
    load_device_artifact_receipt,
)

ROOT = Path(__file__).resolve().parents[1]


def _git(path: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_identity(path: Path) -> dict[str, object]:
    root = path.resolve(strict=True)
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    return {
        "path": str(root),
        "commit": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "status": status,
        "clean": status == "",
    }


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _file_identity(path: Path) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError(f"Goal5848 preregistration rejects symlink: {path}")
    resolved = path.resolve(strict=True)
    metadata = resolved.stat()
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(f"Goal5848 preregistration requires file: {path}")
    return {
        "path": str(resolved),
        "bytes": metadata.st_size,
        "sha256": _sha256_file(resolved),
    }


def _write_create(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def build_preregistration(args: argparse.Namespace) -> dict[str, object]:
    source = _git_identity(ROOT)
    predecessor = _git_identity(args.predecessor_root)
    pyoptix = _git_identity(args.pyoptix_source)
    if (
        source["commit"] != args.expected_source_commit
        or source["clean"] is not True
        or predecessor["commit"] != args.expected_predecessor_commit
        or predecessor["clean"] is not True
        or pyoptix["commit"] != args.expected_pyoptix_commit
        or pyoptix["tree"] != args.expected_pyoptix_tree
        or pyoptix["clean"] is not True
    ):
        raise RuntimeError("Goal5848 preregistration source identity differs")
    load_device_artifact_receipt(
        args.device_artifact_build_receipt,
        precompiled_ptx=args.precompiled_ptx,
        compaction_cubin=args.compaction_cubin,
        expected_source_commit=args.expected_source_commit,
        expected_optix_sdk=args.expected_optix_sdk,
        repository_root=ROOT,
    )
    load_aot_cache_authority(
        args.aot_cache_authority,
        candidate_manifest=args.candidate_manifest,
        expected_source_commit=args.expected_source_commit,
    )
    artifacts = {
        label: _file_identity(Path(getattr(args, argument)))
        for label, argument in PREREGISTRATION_ARTIFACT_ARGUMENTS.items()
    }
    python = _file_identity(args.python.resolve(strict=True))
    schedule = list(build_schedule())
    value: dict[str, object] = {
        "schema": PREREGISTRATION_SCHEMA,
        "status": "FROZEN__BEFORE_FORMAL_WORKER_ZERO",
        "source_commit": source["commit"],
        "source_tree": source["tree"],
        "predecessor_commit": predecessor["commit"],
        "predecessor_tree": predecessor["tree"],
        "pyoptix_commit": pyoptix["commit"],
        "pyoptix_tree": pyoptix["tree"],
        "source_identity": source,
        "predecessor_identity": predecessor,
        "pyoptix_identity": pyoptix,
        "python": python,
        "python_version": sys.version.split()[0],
        "expected_optix_sdk": args.expected_optix_sdk,
        "optix_disk_cache_policy": "disabled_for_all_primary_arms",
        "artifacts": artifacts,
        "tasks": list(TASKS),
        "task_contracts": TASK_CONTRACTS,
        "primary_arms": list(PRIMARY_ARMS),
        "all_arms": list(ARMS),
        "blocks": BLOCKS,
        "steady_warmups": STEADY_WARMUPS,
        "steady_repetitions": STEADY_REPETITIONS,
        "schedule": schedule,
        "schedule_sha256": digest(schedule),
        "thresholds_ppm": {
            "post_import_median": POST_IMPORT_RATIO_LIMIT_PPM,
            "post_import_worst_block": POST_IMPORT_BLOCK_RATIO_LIMIT_PPM,
            "public_direct_median": PUBLIC_DIRECT_RATIO_LIMIT_PPM,
            "successor_predecessor_median": (
                SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM
            ),
            "strong_competence_median": STRONG_COMPETENCE_RATIO_LIMIT_PPM,
            "instrumentation_overhead": INSTRUMENTATION_OVERHEAD_LIMIT_PPM,
        },
        "partition_reconciliation": {
            "absolute_tolerance_ns": PARTITION_ABSOLUTE_TOLERANCE_NS,
            "relative_tolerance_ppm": PARTITION_RELATIVE_TOLERANCE_PPM,
        },
        "instrumentation_protocol": instrumentation_protocol(),
        "aot_cache_protocol": aot_cache_protocol(),
        "endpoint": (
            "implementation_import_end_to_first_exact_public_result"
        ),
        "estimator": "median_of_eight_within_block_integer_ratios",
        "failure_policy": {
            "formal_worker_retry": False,
            "formal_worker_discard": False,
            "prior_rows_authorized_for_pooling": False,
            "repair_requires_new_preregistration": True,
        },
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "claim_boundary": {
            "single_generation_only": True,
            "external_review_complete": False,
            "public_or_manuscript_claim_authorized": False,
        },
        "retry_count": 0,
        "discard_count": 0,
    }
    value["preregistration_sha256"] = digest(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--predecessor-root", type=Path, required=True)
    parser.add_argument("--expected-predecessor-commit", required=True)
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--expected-pyoptix-commit", required=True)
    parser.add_argument("--expected-pyoptix-tree", required=True)
    parser.add_argument("--expected-optix-sdk", required=True)
    for argument in PREREGISTRATION_ARTIFACT_ARGUMENTS.values():
        parser.add_argument(f"--{argument.replace('_', '-')}", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require_formal_cache_policy()
    result = build_preregistration(args)
    _write_create(_new_output_root(args.output), result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
