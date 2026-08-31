#!/usr/bin/env python3
"""Run the frozen BED transfer through the public sealed RTDL lifecycle.

This program reads no clock.  The CPU oracle is computed independently and is
compared only after public ``execute`` returns.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

from .bed_transfer import (
    BedInterval,
    DEFAULT_A,
    DEFAULT_B,
    DEFAULT_EXPECTED_PAIRS,
    MINIMUM_OVERLAP_F32,
    bedtools_default_pair_oracle,
    build_public_inputs,
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _fail(message: str) -> None:
    raise RuntimeError(message)


def _execute_expected_capacity_overflow(
    prepared: object, batch: object, *, executable_error_type: type[Exception],
) -> tuple[str, str]:
    """Accept only the public API's exact bounded-output overflow failure."""
    try:
        prepared.execute(batch, include_diagnostics=False)
    except executable_error_type as error:
        code = getattr(error, "code", None)
        if code != "RX041_OUTPUT_OVERFLOW":
            _fail(f"K+1 BED case failed for a non-overflow reason: {error}")
        return code, str(error)
    _fail("K+1 BED capacity case published an application result")


def _verify_frozen_core(root: Path, preaction: dict) -> list[dict[str, object]]:
    observed = []
    for row in preaction["frozen_execution_core_files"]:
        path = root / row["path"]
        actual = {"path": row["path"], "bytes": path.stat().st_size,
                  "sha256": _sha(path)}
        if actual["bytes"] != row["bytes"] or actual["sha256"] != row["sha256"]:
            _fail(f"frozen core identity mismatch: {actual!r}")
        observed.append(actual)
    return observed


def _verify_execution_freeze(
    root: Path, freeze_path: Path,
) -> tuple[dict, list[dict[str, object]]]:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze.get("status") != (
        "FROZEN_BEFORE_NEXT_GPU_CALL__NO_SCIENTIFIC_RESULT_YET"
    ):
        _fail("execution freeze is not the exact pre-GPU authority")
    observed = []
    for row in freeze.get("files", ()):
        path = root / row["path"]
        actual = {
            "path": row["path"],
            "bytes": path.stat().st_size,
            "sha256": _sha(path),
        }
        if actual["bytes"] != row["bytes"] \
                or actual["sha256"] != row["sha256"]:
            _fail(f"frozen exam-file identity mismatch: {actual!r}")
        observed.append(actual)
    if len(observed) != 4:
        _fail("execution freeze must bind exactly four exam files")
    return freeze, observed


def _verify_driver_compat(
    compat_root: Path, freeze: dict,
) -> list[dict[str, object]]:
    compat_root = compat_root.resolve()
    search_path = tuple(
        Path(part).resolve()
        for part in os.environ.get("LD_LIBRARY_PATH", "").split(":")
        if part
    )
    if compat_root not in search_path:
        _fail("exact driver-compat root is absent from LD_LIBRARY_PATH")
    observed = []
    for row in freeze["driver_compatibility_bridge"]["libraries"]:
        path = compat_root / row["name"]
        actual = {
            "name": row["name"],
            "bytes": path.stat().st_size,
            "sha256": _sha(path),
        }
        if actual["bytes"] != row["bytes"] \
                or actual["sha256"] != row["sha256"]:
            _fail(f"driver-compat library identity mismatch: {actual!r}")
        observed.append(actual)
    return observed


def _require_candidate_file(row: dict, key: str, hash_key: str) -> Path:
    path = Path(row[key]).resolve()
    actual = _sha(path)
    if actual != row[hash_key]:
        _fail(f"candidate {key} hash mismatch: {actual}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--trust-root", type=Path, required=True)
    parser.add_argument("--trust-head", type=Path, required=True)
    parser.add_argument("--trust-package", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--driver-compat-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)

    root = Path(__file__).resolve().parents[2]
    preaction_path = Path(__file__).with_name("preaction.json")
    freeze_path = Path(__file__).with_name("execution_freeze_v2.json")
    preaction = json.loads(preaction_path.read_text(encoding="utf-8"))
    freeze, frozen_exam_files = _verify_execution_freeze(root, freeze_path)
    frozen_core = _verify_frozen_core(root, preaction)
    if preaction["status"] != (
        "TASK_SEMANTICS_DECLARED_BEFORE_IMPLEMENTATION__"
        "EXACT_EXECUTION_BYTES_FROZEN_BEFORE_NEXT_GPU_CALL"
    ):
        _fail("preaction chronology boundary changed")
    driver_compat = _verify_driver_compat(args.driver_compat_root, freeze)

    from rtdsl import (
        RTDLExecutableError,
        install_rtdlexe_deployment,
        load_rtdlexe,
    )

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    candidate = manifest["candidates"]["relation"]
    frozen_artifact = preaction["frozen_execution_artifact"]
    if str(args.manifest.resolve()) != frozen_artifact["candidate_manifest_path"]:
        _fail("candidate manifest path differs from frozen execution artifact")
    for key in (
        "deployment_id", "artifact_sha256", "authority_sha256",
        "executable_identity_sha256",
    ):
        if candidate.get(key) != frozen_artifact[key]:
            _fail(f"candidate {key} differs from frozen execution artifact")
    if manifest.get("native_sha256") != frozen_artifact["native_sha256"]:
        _fail("candidate native differs from frozen execution artifact")
    artifact = _require_candidate_file(
        candidate, "artifact_path", "artifact_sha256")
    authority = _require_candidate_file(
        candidate, "authority_path", "authority_sha256")
    native = args.native.resolve()
    if _sha(native) != manifest["native_sha256"]:
        _fail("native identity differs from candidate manifest")
    deployment = install_rtdlexe_deployment(
        trust_root_path=args.trust_root,
        trust_head_path=args.trust_head,
        trust_package_path=args.trust_package,
        deployment_id=candidate["deployment_id"],
    )
    loaded = load_rtdlexe(
        artifact_path=artifact,
        authority_path=authority,
        deployment=deployment,
    )
    runtime = loaded.product_projection["runtime"]
    minimum = runtime.get("minimum_overlap_f32")
    capacity = runtime.get("capacity")
    if type(minimum) is not float or not math.isfinite(minimum) \
            or minimum != MINIMUM_OVERLAP_F32:
        _fail(f"sealed relation threshold is not {MINIMUM_OVERLAP_F32}: {minimum!r}")
    if type(capacity) is not int or capacity < len(DEFAULT_EXPECTED_PAIRS):
        _fail(f"sealed relation capacity is invalid: {capacity!r}")
    if capacity != frozen_artifact["capacity"] \
            or minimum != frozen_artifact["minimum_overlap_f32"]:
        _fail("loaded protocol differs from frozen execution artifact")

    oracle = bedtools_default_pair_oracle(DEFAULT_A, DEFAULT_B)
    if oracle != DEFAULT_EXPECTED_PAIRS:
        _fail(f"frozen CPU oracle changed: {oracle!r}")
    static, batch = build_public_inputs(
        __import__("rtdsl"), DEFAULT_A, DEFAULT_B)
    if batch.expected_rows is not None:
        _fail("oracle entered the public execute input")

    prepared = loaded.prepare(static, native_library_path=native)
    try:
        result = prepared.execute(batch, include_diagnostics=True)
        if result.output != oracle:
            _fail(f"RTDL output differs from BED oracle: {result.output!r}")
        if result.output_sha256 is None:
            _fail("diagnostic execution omitted output identity")
        receipt = dict(result.traversal_receipt or {})
        if receipt.get("physical_executor_classification") \
                != "optix_traversal_observed":
            _fail("execution lacks behavioral OptiX receipt")
        if result.device_status.get("ok") is not True:
            _fail("successful BED query lacks status-before-output success")
    finally:
        prepared.close()
    if not prepared.closed:
        _fail("prepared BED query did not close")

    # K+1 unique application rows must fail without publishing a partial
    # result.  This uses a fresh public prepared owner and passes no oracle.
    overflow_a = tuple(
        BedInterval("chrOverflow", 10, 11, index)
        for index in range(capacity + 1)
    )
    overflow_b = (BedInterval("chrOverflow", 0, 100, 0),)
    overflow_oracle_count = len(
        bedtools_default_pair_oracle(overflow_a, overflow_b))
    if overflow_oracle_count != capacity + 1:
        _fail("overflow oracle does not contain K+1 unique pairs")
    overflow_static, overflow_batch = build_public_inputs(
        __import__("rtdsl"), overflow_a, overflow_b)
    overflow_prepared = loaded.prepare(
        overflow_static, native_library_path=native)
    try:
        overflow_failure_code, overflow_failure_text = (
            _execute_expected_capacity_overflow(
                overflow_prepared, overflow_batch,
                executable_error_type=RTDLExecutableError,
            )
        )
    finally:
        overflow_prepared.close()

    result_payload = {
        "schema": "rtdl.goal5803.bed_interval_intersection.untimed_result.v1",
        "status": "PASS__ONE_FROZEN_CORE_EXTERNAL_SPEC_TRANSFER",
        "task": preaction["task"]["name"],
        "external_specification": preaction["task"]["external_specification"],
        "selection_and_exposure": preaction["selection_and_exposure"],
        "claim_ceiling": preaction["claim_ceiling"],
        "frozen_core_files": frozen_core,
        "frozen_exam_files": frozen_exam_files,
        "preaction_path": str(preaction_path),
        "preaction_sha256": _sha(preaction_path),
        "execution_freeze_path": str(freeze_path),
        "execution_freeze_sha256": _sha(freeze_path),
        "driver_compatibility_bridge": {
            "root": str(args.driver_compat_root.resolve()),
            "libraries": driver_compat,
            "system_packages_installed_or_changed": False,
            "host_rebooted": False
        },
        "candidate_manifest_path": str(args.manifest.resolve()),
        "candidate_manifest_sha256": _sha(args.manifest),
        "artifact_path": str(artifact),
        "artifact_sha256": _sha(artifact),
        "authority_path": str(authority),
        "authority_sha256": _sha(authority),
        "native_path": str(native),
        "native_sha256": _sha(native),
        "trust_root_sha256": _sha(args.trust_root),
        "trust_head_sha256": _sha(args.trust_head),
        "trust_package_sha256": _sha(args.trust_package),
        "deployment_id": candidate["deployment_id"],
        "executable_identity_sha256": result.executable_identity_sha256,
        "minimum_overlap_f32": minimum,
        "capacity": capacity,
        "normal_case": {
            "a_count": len(DEFAULT_A),
            "b_count": len(DEFAULT_B),
            "oracle_pairs": [list(row) for row in oracle],
            "output_pairs": [list(row) for row in result.output],
            "output_sha256": result.output_sha256,
            "device_status": dict(result.device_status),
            "role_counters": list(result.role_counters),
            "traversal_receipt": receipt,
            "oracle_passed_into_execute": False,
        },
        "coverage": {
            "positive_overlap": True,
            "miss": True,
            "adjacent_half_open_boundary_rejected": True,
            "cross_chromosome_rejected": True,
            "one_base_overlap_at_max_exact_f32_integer": True,
        },
        "capacity_overflow": {
            "expected_unique_pair_count": overflow_oracle_count,
            "failure_code": overflow_failure_code,
            "failure_text": overflow_failure_text,
            "partial_application_result_published": False,
            "prepared_closed": overflow_prepared.closed,
        },
        "public_lifecycle": ["install", "load", "prepare", "execute", "close"],
        "private_execution_api_used": False,
        "handwritten_ptx_sbt_or_pipeline_used": False,
        "core_or_native_changed_for_task": False,
        "registered_performance_timing_count": 0,
        "formal_performance_worker_count": 0
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result_payload, sort_keys=True, indent=2).encode() + b"\n")
    print(json.dumps(result_payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
