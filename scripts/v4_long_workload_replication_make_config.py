#!/usr/bin/env python3
"""Derive the two-arm cit-Patents replication config from verified inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any


BASE_SCHEMA = "rtdl.v4_paper_apps_pyoptix.config.v1"
FORMAL_SCHEMA = "rtdl.v4_long_workload.formal_config.v1"
RTDLEXE_SCHEMA = "rtdl.v4_long_workload.triangle_rtdlexe_build.v1"
UNIT_ID = "triangle_counting__cit_patents__rt_2a1__4m"
SOURCE_FIELDS = (
    "source_root",
    "source_commit",
    "source_tree",
    "native_library_path",
    "native_library_sha256",
    "native_build_manifest_path",
    "native_build_manifest_sha256",
)
REMOVED_COMMON_FIELDS = frozenset({
    "schema",
    *SOURCE_FIELDS,
    "prepared_repetitions",
    "performance_threshold_present",
})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def derive_config(
    base: Mapping[str, Any], rtdlexe: Mapping[str, Any], *,
    cpu_id: int, worker_timeout_seconds: int,
) -> dict[str, Any]:
    if base.get("schema") != BASE_SCHEMA:
        raise ValueError("base config schema differs")
    if rtdlexe.get("schema") != RTDLEXE_SCHEMA \
            or rtdlexe.get("status") \
            != "PASS__SIGNED_PUBLIC_LOAD_AND_DEVICE_PROGRAM_PREPARE_VERIFIED":
        raise ValueError("triangle RTDL executable manifest is not accepted")
    if type(cpu_id) is not int or cpu_id < 0:
        raise ValueError("CPU affinity must be one nonnegative logical CPU")
    if type(worker_timeout_seconds) is not int \
            or worker_timeout_seconds < 120:
        raise ValueError("worker timeout must be at least 120 seconds")
    if base.get("registered_before_performance_observation") is not True \
            or base.get("retry_allowed") is not False \
            or base.get("discard_allowed") is not False:
        raise ValueError("base config does not preserve preregistration policy")
    if any(not base.get(name) for name in SOURCE_FIELDS):
        raise ValueError("base config source/native identity is incomplete")

    source = rtdlexe.get("source")
    target = rtdlexe.get("target")
    fragment = rtdlexe.get("formal_config_fragment")
    if not all(isinstance(value, Mapping) for value in (
            source, target, fragment)):
        raise TypeError("triangle RTDL executable manifest mappings are incomplete")
    if source.get("commit") != base["source_commit"] \
            or source.get("tree") != base["source_tree"] \
            or target.get("native_sha256") != base["native_library_sha256"] \
            or fragment.get("expected_native_sha256") \
            != base["native_library_sha256"]:
        raise ValueError("triangle RTDL executable identity differs from base config")

    common = {
        key: value for key, value in base.items()
        if key not in REMOVED_COMMON_FIELDS
    }
    common.update({
        "prepared_warmups": 1,
        "worker_timeout_seconds": worker_timeout_seconds,
        "cpu_affinity": {"cpu_ids": [cpu_id]},
        "replication_config_builder": {
            "path": str(Path(__file__).resolve(strict=True)),
            "sha256": _sha256(Path(__file__).resolve(strict=True)),
        },
    })
    implementation = {name: base[name] for name in SOURCE_FIELDS}
    return {
        "schema": FORMAL_SCHEMA,
        "common": common,
        "implementations": {
            "new_v4": {
                **implementation,
                "triangle_rtdlexe": dict(fragment),
            },
            "pyoptix": dict(implementation),
        },
        "units": {
            UNIT_ID: {
                "unit_id": UNIT_ID,
                "app": "triangle_counting",
                "operation": None,
                "dataset": "cit-Patents",
                "expected_triangle_count": 7_515_023,
                "max_relation_rows": 4_000_000,
                "prepared_repetitions": 3,
            },
        },
    }


def _write_create(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=False) as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-config", type=Path, required=True)
    parser.add_argument("--triangle-rtdlexe-manifest", type=Path, required=True)
    parser.add_argument("--cpu-id", type=int, required=True)
    parser.add_argument("--worker-timeout-seconds", type=int, default=900)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base_path = args.base_config.resolve(strict=True)
    rtdlexe_path = args.triangle_rtdlexe_manifest.resolve(strict=True)
    output = args.output.resolve()
    value = derive_config(
        _read_object(base_path), _read_object(rtdlexe_path),
        cpu_id=args.cpu_id,
        worker_timeout_seconds=args.worker_timeout_seconds,
    )
    value["common"]["replication_config_inputs"] = {
        "base_config_path": str(base_path),
        "base_config_sha256": _sha256(base_path),
        "triangle_rtdlexe_manifest_path": str(rtdlexe_path),
        "triangle_rtdlexe_manifest_sha256": _sha256(rtdlexe_path),
    }
    _write_create(output, value)
    print(json.dumps({
        "status": "PASS__TWO_ARM_REPLICATION_CONFIG_CREATED",
        "output": str(output),
        "output_sha256": _sha256(output),
        "unit_id": UNIT_ID,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
