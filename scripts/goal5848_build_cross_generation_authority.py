#!/usr/bin/env python3
"""Recount Goal5848 success across two distinct RTX generations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path

from experiments.goal5848_strong_baseline.contracts import (
    TASKS,
    digest,
    strict_json_loads,
)

ROOT = Path(__file__).resolve().parents[1]

_RTX_ARCHITECTURES = {
    "7.5": "TURING",
    "8.6": "AMPERE",
    "8.9": "ADA",
    "12.0": "BLACKWELL",
}


def _new_output_path(path: Path) -> Path:
    """Create-free canonical output validation without controller imports."""

    absolute = path.expanduser().absolute()
    if absolute.exists() or absolute.is_symlink():
        raise FileExistsError(absolute)
    parent = absolute.parent.resolve(strict=True)
    candidate = parent / absolute.name
    if os.path.commonpath((str(ROOT), str(candidate))) == str(ROOT):
        raise RuntimeError("Goal5848 authority output must be outside source Git")
    return candidate


def _read(path: Path) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError("Goal5848 cross-generation authority rejects symlink")
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 generation authority",
    )
    if not isinstance(value, dict):
        raise TypeError("Goal5848 generation authority must be an object")
    unsigned = dict(value)
    seal = unsigned.pop("authority_sha256", None)
    instrumentation = value.get("instrumentation_overhead")
    device_artifacts = value.get("device_artifact_build_receipt")
    aot_cache = value.get("aot_cache_authority")
    if (
        seal != digest(unsigned)
        or value.get("schema")
        != "rtdl.goal5848.single_generation_authority.v2"
        or value.get("status") != "PASS__INDEPENDENT_BYTE_AND_GATE_RECOUNT"
        or value.get("worker_count") != 80
        or value.get("process_count") != 80
        or value.get("direct_support_count") != 16
        or value.get("retry_count") != 0
        or value.get("discard_count") != 0
        or value.get("external_review_complete") is not False
        or value.get("public_or_manuscript_claim_authorized") is not False
        or not isinstance(instrumentation, Mapping)
        or set(instrumentation) != {"path", "bytes", "sha256"}
        or not isinstance(device_artifacts, Mapping)
        or set(device_artifacts) != {"path", "bytes", "sha256"}
        or not isinstance(aot_cache, Mapping)
        or set(aot_cache) != {"path", "bytes", "sha256"}
        or not isinstance(value.get("aot_cache_authority_sha256"), str)
    ):
        raise RuntimeError("Goal5848 generation authority differs")
    return value


def build(first_path: Path, second_path: Path) -> dict[str, object]:
    paths = (first_path.resolve(strict=True), second_path.resolve(strict=True))
    if paths[0] == paths[1]:
        raise RuntimeError("Goal5848 requires two independent authorities")
    recount_paths = tuple(
        path.with_name(f"{path.stem}.recount{path.suffix}")
        for path in paths
    )
    for authority_path, recount_path in zip(paths, recount_paths, strict=True):
        if (
            not recount_path.is_file()
            or recount_path.is_symlink()
            or authority_path.read_bytes() != recount_path.read_bytes()
        ):
            raise RuntimeError(
                "Goal5848 generation authority lacks byte-identical recount"
            )
    rows = [_read(path) for path in paths]
    if (
        len({row["source_commit"] for row in rows}) != 1
        or len({row["predecessor_commit"] for row in rows}) != 1
    ):
        raise RuntimeError("Goal5848 generation source identities differ")
    generation_rows = []
    for path, recount_path, row in zip(paths, recount_paths, rows, strict=True):
        recount = row.get("recount")
        hardware = recount.get("hardware") if isinstance(recount, Mapping) else None
        tasks = recount.get("tasks") if isinstance(recount, Mapping) else None
        capability = (
            hardware.get("compute_capability")
            if isinstance(hardware, Mapping)
            else None
        )
        architecture = _RTX_ARCHITECTURES.get(str(capability))
        if (
            architecture is None
            or not isinstance(tasks, Mapping)
            or set(tasks) != set(TASKS)
            or not all(
                isinstance(tasks[task], Mapping)
                and tasks[task].get("all_performance_gates_pass") is True
                for task in TASKS
            )
        ):
            raise RuntimeError("Goal5848 generation gate evidence differs")
        generation_rows.append({
            "authority_path": str(path),
            "authority_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "authority_recount_path": str(recount_path),
            "authority_recount_file_sha256": hashlib.sha256(
                recount_path.read_bytes()
            ).hexdigest(),
            "authority_sha256": row["authority_sha256"],
            "architecture": architecture,
            "hardware": hardware,
            "task_gate_direction": {
                task: "PASS" for task in TASKS
            },
            "instrumentation_overhead_file_sha256": row[
                "instrumentation_overhead"
            ]["sha256"],
            "device_artifact_build_receipt_file_sha256": row[
                "device_artifact_build_receipt"
            ]["sha256"],
            "aot_cache_authority_file_sha256": row[
                "aot_cache_authority"
            ]["sha256"],
            "aot_cache_authority_sha256": row[
                "aot_cache_authority_sha256"
            ],
        })
    if len({row["architecture"] for row in generation_rows}) != 2:
        raise RuntimeError("Goal5848 RTX architecture generations are not distinct")
    if len({row["hardware"]["gpu_uuid"] for row in generation_rows}) != 2:
        raise RuntimeError("Goal5848 generation authorities reuse one GPU")
    result = {
        "schema": "rtdl.goal5848.cross_generation_authority.v2",
        "status": (
            "PASS__GOAL5848_INTERNAL_TECHNICAL_COMPLETE__"
            "EXTERNAL_REVIEW_PENDING"
        ),
        "source_commit": rows[0]["source_commit"],
        "predecessor_commit": rows[0]["predecessor_commit"],
        "generation_count": 2,
        "architectures": sorted(
            row["architecture"] for row in generation_rows
        ),
        "generations": generation_rows,
        "cross_machine_raw_time_ratio_computed": False,
        "only_within_machine_registered_gates_compared": True,
        "retry_count": 0,
        "discard_count": 0,
        "external_review_complete": False,
        "public_or_manuscript_claim_authorized": False,
    }
    result["authority_sha256"] = digest(result)
    return result


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first", type=Path, required=True)
    parser.add_argument("--second", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.first, args.second)
    _write_create(_new_output_path(args.output), result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
