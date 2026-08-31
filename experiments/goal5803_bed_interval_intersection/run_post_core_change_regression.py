#!/usr/bin/env python3
"""Untimed Home-GPU regression after the generic compact-status core fix.

This is not a second transfer exam.  It preserves and re-verifies the failed
frozen Goal5803 transaction, then replays its exact BED fixtures, artifact,
native image and trust chain with one declared Python-only successor core.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from . import run_untimed as frozen_runner
from .bed_transfer import (
    BedInterval,
    DEFAULT_A,
    DEFAULT_B,
    DEFAULT_EXPECTED_PAIRS,
    MINIMUM_OVERLAP_F32,
    bedtools_default_pair_oracle,
    build_public_inputs,
)


_OLD_CORE_SHA256 = (
    "7429dddc578c927a9bd837a402300ed0e7256e5188accc17e5ebc6e732efa840")
_OLD_CORE_BYTES = 212166
_NEW_CORE_SHA256 = (
    "36fdecbc86e60807a49326377e0d74415f7777867cbaa638f52b82342a4bf526")
_NEW_CORE_BYTES = 217818
_PATCH_SHA256 = (
    "d5253940c39607dfdb53c2678eb7252afca9c8df241abf7b1f9c1390609ca235")
_PATCH_BYTES = 11871
_ORIGINAL_FAILURE_SHA256 = {
    "goal5803_bed_interval_intersection_run_v2.stdout":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "goal5803_bed_interval_intersection_run_v2.stderr":
        "e7b9c0f7a63f7029734b781484ae7babed124360d8cd80970737b23bed0cf6f7",
    "goal5803_bed_interval_intersection_run_v2.exit_code":
        "741d14df730e53a5a019a710116f696db4ec23a132b74cf6fbb3cf7617e68313",
}


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _exact(path: Path, *, size: int, sha256: str, label: str) -> dict:
    path = path.resolve()
    observed = {"path": str(path), "bytes": path.stat().st_size,
                "sha256": _sha(path)}
    if observed["bytes"] != size or observed["sha256"] != sha256:
        raise RuntimeError(f"{label} identity mismatch: {observed!r}")
    return observed


def _verify_successor_custody(
    *, successor_root: Path, original_root: Path, patch_path: Path,
) -> tuple[dict, dict, list[dict], list[dict], dict]:
    original_preaction_path = (
        original_root / "experiments/goal5803_bed_interval_intersection/preaction.json")
    original_freeze_path = (
        original_root /
        "experiments/goal5803_bed_interval_intersection/execution_freeze_v2.json")
    preaction = json.loads(original_preaction_path.read_text(encoding="utf-8"))
    freeze, original_exam_files = frozen_runner._verify_execution_freeze(
        original_root, original_freeze_path)
    original_core_files = frozen_runner._verify_frozen_core(
        original_root, preaction)

    old_copy = _exact(
        successor_root / "v4_rtdlexe.py.pre_core_change_exact",
        size=_OLD_CORE_BYTES, sha256=_OLD_CORE_SHA256,
        label="successor preserved old core")
    new_core = _exact(
        successor_root / "src/rtdsl/v4_rtdlexe.py",
        size=_NEW_CORE_BYTES, sha256=_NEW_CORE_SHA256,
        label="successor core")
    patch = _exact(
        patch_path, size=_PATCH_BYTES, sha256=_PATCH_SHA256,
        label="old-to-new patch")

    # The old copy must be byte-identical to the original frozen core.  Every
    # other core file in the successor remains the frozen byte sequence.
    if old_copy["sha256"] != original_core_files[0]["sha256"]:
        raise RuntimeError("preserved old core is not the original frozen core")
    unchanged_successor_core = []
    for row in preaction["frozen_execution_core_files"][1:]:
        unchanged_successor_core.append(_exact(
            successor_root / row["path"], size=row["bytes"],
            sha256=row["sha256"], label=f"unchanged successor {row['path']}"))

    failures = {}
    for name, expected_sha in _ORIGINAL_FAILURE_SHA256.items():
        path = original_root / name
        failures[name] = {
            "path": str(path.resolve()), "bytes": path.stat().st_size,
            "sha256": _sha(path),
        }
        if failures[name]["sha256"] != expected_sha:
            raise RuntimeError(f"original failure evidence changed: {name}")
    return (
        preaction, freeze, original_exam_files, unchanged_successor_core,
        {"old_core": old_copy, "new_core": new_core, "patch": patch,
         "original_failure_evidence": failures},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--trust-root", type=Path, required=True)
    parser.add_argument("--trust-head", type=Path, required=True)
    parser.add_argument("--trust-package", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--driver-compat-root", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)

    successor_root = Path(__file__).resolve().parents[2]
    original_root = args.original_root.resolve()
    preaction, freeze, frozen_exam_files, unchanged_core, custody = (
        _verify_successor_custody(
            successor_root=successor_root, original_root=original_root,
            patch_path=args.patch.resolve()))
    driver_compat = frozen_runner._verify_driver_compat(
        args.driver_compat_root, freeze)

    from rtdsl import (
        RTDLExecutableError,
        install_rtdlexe_deployment,
        load_rtdlexe,
    )

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    candidate = manifest["candidates"]["relation"]
    frozen_artifact = preaction["frozen_execution_artifact"]
    if str(args.manifest.resolve()) != frozen_artifact["candidate_manifest_path"]:
        raise RuntimeError("manifest is not the original frozen v14 path")
    for key in (
        "deployment_id", "artifact_sha256", "authority_sha256",
        "executable_identity_sha256",
    ):
        if candidate.get(key) != frozen_artifact[key]:
            raise RuntimeError(f"frozen candidate drift: {key}")
    if manifest.get("native_sha256") != frozen_artifact["native_sha256"]:
        raise RuntimeError("frozen native identity drift")
    artifact = frozen_runner._require_candidate_file(
        candidate, "artifact_path", "artifact_sha256")
    authority = frozen_runner._require_candidate_file(
        candidate, "authority_path", "authority_sha256")
    native = args.native.resolve()
    if _sha(native) != manifest["native_sha256"]:
        raise RuntimeError("executed native differs from frozen manifest")

    deployment = install_rtdlexe_deployment(
        trust_root_path=args.trust_root,
        trust_head_path=args.trust_head,
        trust_package_path=args.trust_package,
        deployment_id=candidate["deployment_id"],
    )
    loaded = load_rtdlexe(
        artifact_path=artifact, authority_path=authority,
        deployment=deployment)
    runtime = loaded.product_projection["runtime"]
    minimum = runtime.get("minimum_overlap_f32")
    capacity = runtime.get("capacity")
    if type(minimum) is not float or not math.isfinite(minimum) \
            or minimum != MINIMUM_OVERLAP_F32:
        raise RuntimeError(f"sealed threshold drift: {minimum!r}")
    if type(capacity) is not int or capacity != frozen_artifact["capacity"]:
        raise RuntimeError(f"sealed capacity drift: {capacity!r}")

    oracle = bedtools_default_pair_oracle(DEFAULT_A, DEFAULT_B)
    if oracle != DEFAULT_EXPECTED_PAIRS:
        raise RuntimeError("frozen normal-case CPU oracle changed")
    static, batch = build_public_inputs(
        __import__("rtdsl"), DEFAULT_A, DEFAULT_B)
    if batch.expected_rows is not None:
        raise RuntimeError("oracle entered public normal-case input")
    prepared = loaded.prepare(static, native_library_path=native)
    try:
        result = prepared.execute(batch, include_diagnostics=True)
        if result.output != oracle:
            raise RuntimeError("normal BED output differs from frozen oracle")
        if result.device_status.get("ok") is not True:
            raise RuntimeError("normal BED status-before-output is not success")
        receipt = dict(result.traversal_receipt or {})
        if receipt.get("physical_executor_classification") \
                != "optix_traversal_observed":
            raise RuntimeError("normal BED execution lacks behavioral OptiX")
    finally:
        prepared.close()

    overflow_a = tuple(
        BedInterval("chrOverflow", 10, 11, index)
        for index in range(capacity + 1))
    overflow_b = (BedInterval("chrOverflow", 0, 100, 0),)
    overflow_count = len(bedtools_default_pair_oracle(overflow_a, overflow_b))
    if overflow_count != capacity + 1:
        raise RuntimeError("frozen K+1 oracle changed")
    overflow_static, overflow_batch = build_public_inputs(
        __import__("rtdsl"), overflow_a, overflow_b)
    if overflow_batch.expected_rows is not None:
        raise RuntimeError("oracle entered public overflow input")
    overflow_prepared = loaded.prepare(
        overflow_static, native_library_path=native)
    overflow_error = None
    try:
        try:
            overflow_prepared.execute(
                overflow_batch, include_diagnostics=False)
        except RTDLExecutableError as error:
            if error.code != "RX041_OUTPUT_OVERFLOW":
                raise RuntimeError(
                    f"K+1 regression retained a non-overflow failure: {error}")
            overflow_error = str(error)
        else:
            raise RuntimeError("K+1 regression published an application result")
        owner = overflow_prepared._owner
        operation = dict(owner._last_fast_operation_receipt)
        compact_control = dict(owner._last_fast_compact_control)
        if operation["status_before_output"] is not True \
                or operation["output_d2h_bytes"] != 0 \
                or operation["output_d2h_copy_call_count"] != 0 \
                or operation["output_d2h_after_status_failure"] != 0:
            raise RuntimeError("overflow path transferred partial output")
        expected_fixed_control = {
            "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
            "status": 0xffff5102,
            "semantic_capacity": capacity,
            "raw_event_capacity": 2 * capacity,
            "control_d2h_bytes": 28,
        }
        if any(compact_control.get(key) != expected
               for key, expected in expected_fixed_control.items()) \
                or type(compact_control.get("raw_event_count")) is not int \
                or type(compact_control.get("unique_event_count")) is not int \
                or compact_control["overflowed"] not in {0, 1} \
                or compact_control["unique_event_count"] > min(
                    compact_control["raw_event_count"],
                    compact_control["raw_event_capacity"]) \
                or not (
                    compact_control["overflowed"] == 1
                    or compact_control["raw_event_count"]
                        > compact_control["raw_event_capacity"]
                    or compact_control["unique_event_count"]
                        > compact_control["semantic_capacity"]):
            raise RuntimeError(f"unexpected K+1 compact control: {compact_control!r}")
    finally:
        overflow_prepared.close()

    payload = {
        "schema": "rtdl.goal5803.bed.post_core_change_regression.v1",
        "status": "PASS__POST_CORE_CHANGE_REGRESSION",
        "post_core_change_regression": True,
        "prior_frozen_outcome_preserved":
            "CORE_CHANGE_REQUIRED__RX035_FOR_NATIVE_0xffff5102",
        "fresh_transfer_count": 0,
        "generality_exam_count_increment": 0,
        "registered_performance_timing_count": 0,
        "formal_performance_worker_count": 0,
        "clock_read_or_timing_performed": False,
        "task_replacement_or_fixture_change": False,
        "original_runner_reexecuted_with_changed_core": False,
        "original_freeze_guard_rejects_changed_core": True,
        "core_delta": custody,
        "unchanged_successor_core_files": unchanged_core,
        "original_frozen_exam_files": frozen_exam_files,
        "manifest": {"path": str(args.manifest.resolve()),
                     "sha256": _sha(args.manifest)},
        "artifact": {"path": str(artifact), "sha256": _sha(artifact)},
        "authority": {"path": str(authority), "sha256": _sha(authority)},
        "native": {"path": str(native), "sha256": _sha(native)},
        "trust": {
            "root_sha256": _sha(args.trust_root),
            "head_sha256": _sha(args.trust_head),
            "package_sha256": _sha(args.trust_package),
        },
        "driver_compatibility_bridge": {
            "root": str(args.driver_compat_root.resolve()),
            "libraries": driver_compat,
            "system_packages_installed_or_changed": False,
            "host_rebooted": False,
        },
        "normal_case": {
            "oracle_pairs": [list(row) for row in oracle],
            "output_pairs": [list(row) for row in result.output],
            "exact": True,
            "behavioral_optix": True,
            "output_sha256": result.output_sha256,
            "device_status": dict(result.device_status),
        },
        "capacity_overflow": {
            "expected_unique_pair_count": overflow_count,
            "failure_code": "RX041_OUTPUT_OVERFLOW",
            "failure_text": overflow_error,
            "partial_application_result_published": False,
            "operation_receipt": operation,
            "compact_control": compact_control,
        },
        "native_ptx_artifact_authority_or_trust_changed": False,
        "private_execution_api_used": False,
        "private_fields_read_after_public_failure_for_regression_evidence": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n")
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
