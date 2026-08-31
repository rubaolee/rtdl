#!/usr/bin/env python3
"""Create-only dual validation of a prepared Goal5802 runtime.

This gate is deliberately earlier and weaker than the live worker-zero
preflight in the formal controller.  It launches no worker, reads no clock,
accepts no execution authority, and performs no compilation or GPU action.  It
does, however, require two separately implemented byte-validation paths to bind
the complete frozen product and frozen source projection to the prepared target
runtime before a preexecution review can be requested.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.goal5802_premeasurement import contract
from experiments.goal5802_premeasurement import independent_recount
from experiments.goal5802_premeasurement import runtime_manifest


PASS_SCHEMA = "rtdl.goal5802.preformal_runtime_dual_validation.v1"
FAILURE_SCHEMA = (
    "rtdl.goal5802.preformal_runtime_dual_validation_failure.v1")
PASS_STATUS = "PASS__DUAL_UNTIMED_PREFORMAL_RUNTIME_VALIDATION"
FAILURE_STATUS = (
    "FAIL__DUAL_UNTIMED_PREFORMAL_RUNTIME_VALIDATION__PRESERVE__"
    "NO_FORMAL_EXECUTION")

PYOPTIX_SCALAR_SOURCE = (
    "experiments/goal5802_premeasurement/pyoptix_scalar_arm.py")
GOAL5800_SOURCE = (
    "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py")
THIS_VALIDATOR_SOURCE = (
    "scripts/goal5802_verify_preformal_runtime_dual_untimed.py")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            hasher.update(block)
    return hasher.hexdigest()


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 \
        and all(character in "0123456789abcdef" for character in value)


def _regular_file_identity(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"input is not an exact regular file: {path}")
    resolved = path.resolve(strict=True)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": _sha(resolved),
    }


def _best_effort_file_identity(path: Path) -> dict[str, object]:
    try:
        return _regular_file_identity(path)
    except Exception as error:  # failure receipt must preserve the failed input
        return {
            "path": str(path.resolve(strict=False)),
            "identity_available": False,
            "failure_class": type(error).__name__,
            "failure_message": str(error),
        }


def _load_json_object(path: Path) -> dict[str, Any]:
    _regular_file_identity(path)
    try:
        value = json.loads(path.read_bytes())
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"input is not one exact JSON object: {path}") \
            from error
    if not isinstance(value, dict):
        raise RuntimeError(f"input JSON is not an object: {path}")
    return value


def _write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def _validate_zero_locks(
        freeze: Mapping[str, Any], runtime: Mapping[str, Any]) -> None:
    authorization = freeze.get("authorization")
    if not isinstance(authorization, Mapping) \
            or authorization.get("formal_worker_zero") is not False \
            or authorization.get("registered_gpu_timing") is not False \
            or authorization.get("pod_execution") is not False \
            or type(freeze.get("registered_performance_timing_count")) is not int \
            or freeze["registered_performance_timing_count"] != 0:
        raise RuntimeError("preformal freeze execution lock differs")
    if runtime.get("formal_worker_zero") is not False \
            or type(runtime.get("registered_performance_timing_count")) is not int \
            or runtime["registered_performance_timing_count"] != 0:
        raise RuntimeError("preformal runtime execution lock differs")


def _read_runtime_receipt(
        files: Mapping[str, Any], role: str) -> dict[str, Any]:
    record = files.get(role)
    if not isinstance(record, Mapping) or not isinstance(record.get("path"), str):
        raise RuntimeError(f"runtime receipt role is absent: {role}")
    return _load_json_object(Path(record["path"]))


def _primary_link_projection(
        freeze: Mapping[str, Any], runtime: Mapping[str, Any]) \
        -> dict[str, object]:
    """Reproduce the controller's freeze-to-runtime bindings explicitly."""

    files = runtime.get("files")
    directories = runtime.get("directories")
    product = freeze.get("product_binding")
    source_rows = freeze.get("source_manifest")
    if not isinstance(files, Mapping) \
            or not isinstance(directories, Mapping) \
            or not isinstance(product, Mapping) \
            or not isinstance(source_rows, list):
        raise RuntimeError("primary preformal link inputs are absent")

    expected_product_files = {
        "rtdl_wheel": product.get("wheel_sha256"),
        "native_library": product.get("native_sha256"),
        "trust_root": product.get("trust_root_sha256"),
        "trust_head": product.get("trust_head_sha256"),
        "trust_package": product.get("trust_package_sha256"),
        "relation_artifact": product.get("relation_artifact_sha256"),
        "relation_authority": product.get("relation_authority_sha256"),
        "triangle_artifact": product.get("triangle_artifact_sha256"),
        "triangle_authority": product.get("triangle_authority_sha256"),
        "rtdsl_init": product.get("rtdsl_init_sha256"),
        "rtdlexe_module": product.get("rtdlexe_module_sha256"),
    }
    if any(not _valid_sha256(value)
           for value in expected_product_files.values()):
        raise RuntimeError("primary frozen product identity is malformed")
    observed_product_files: dict[str, str] = {}
    for role, expected in expected_product_files.items():
        record = files.get(role)
        if not isinstance(record, Mapping) or record.get("sha256") != expected:
            raise RuntimeError(
                f"primary runtime/frozen-product link differs: {role}")
        observed_product_files[role] = str(record["sha256"])

    package = directories.get("rtdsl_package")
    deployments = runtime.get("deployment_ids")
    if not isinstance(package, Mapping) \
            or package.get("file_count") \
            != product.get("rtdsl_package_file_count") \
            or package.get("tree_sha256") \
            != product.get("rtdsl_package_tree_sha256"):
        raise RuntimeError("primary installed RTDL package link differs")
    if not isinstance(deployments, Mapping) \
            or deployments.get("relation") \
            != product.get("relation_deployment_id") \
            or deployments.get("triangle") \
            != product.get("triangle_deployment_id"):
        raise RuntimeError("primary RTDL deployment link differs")

    frozen_by_path: dict[str, str] = {}
    for row in source_rows:
        if not isinstance(row, Mapping) \
                or not isinstance(row.get("path"), str) \
                or not _valid_sha256(row.get("sha256")) \
                or row["path"] in frozen_by_path:
            raise RuntimeError("primary frozen source projection differs")
        frozen_by_path[str(row["path"])] = str(row["sha256"])
    source_links = {
        "direct_scalar_source": (
            "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"),
        "device_source": (
            "experiments/goal5802_premeasurement/"
            "matched_device_semantic_capacity.cu"),
        "compaction_source": (
            "experiments/goal5802_premeasurement/"
            "relation_semantic_compaction.cu"),
    }
    observed_source_files: dict[str, dict[str, str]] = {}
    for role, source_path in source_links.items():
        record = files.get(role)
        expected = frozen_by_path.get(source_path)
        if not isinstance(record, Mapping) or expected is None \
                or record.get("sha256") != expected:
            raise RuntimeError(
                f"primary runtime/frozen-source link differs: {role}")
        observed_source_files[role] = {
            "frozen_path": source_path, "sha256": expected}
    pyoptix = runtime.get("pyoptix")
    goal5800_sha = frozen_by_path.get(GOAL5800_SOURCE)
    if not isinstance(pyoptix, Mapping) or goal5800_sha is None \
            or pyoptix.get("goal5800_v7_source_sha256") != goal5800_sha:
        raise RuntimeError("primary Goal5800 source link differs")
    observed_source_files["goal5800_v7_source"] = {
        "frozen_path": GOAL5800_SOURCE, "sha256": goal5800_sha}

    scalar_sha = frozen_by_path.get(PYOPTIX_SCALAR_SOURCE)
    if scalar_sha is None:
        raise RuntimeError("primary frozen PyOptiX scalar source is absent")
    pyoptix_kat = _read_runtime_receipt(files, "pyoptix_operation_kat")
    runtime_manifest.validate_pyoptix_operation_kat(
        pyoptix_kat, files, expected_source_sha256=scalar_sha)
    direct_kat = _read_runtime_receipt(files, "direct_operation_kat")
    runtime_manifest.validate_direct_operation_kat(direct_kat, files)
    expected_executable_identities = {
        "relation": product.get("relation_executable_identity_sha256"),
        "triangle": product.get("triangle_executable_identity_sha256"),
    }
    if any(not _valid_sha256(value)
           for value in expected_executable_identities.values()):
        raise RuntimeError("primary frozen executable identity is malformed")
    rtdl_kat = _read_runtime_receipt(files, "rtdl_operation_kat")
    runtime_manifest.validate_rtdl_operation_kat(
        rtdl_kat, files, deployments,
        expected_executable_identities=expected_executable_identities)

    return {
        "product_files": observed_product_files,
        "rtdsl_package": {
            "file_count": package["file_count"],
            "tree_sha256": package["tree_sha256"],
        },
        "deployment_ids": dict(deployments),
        "frozen_source_files": observed_source_files,
        "pyoptix_scalar_source_sha256": scalar_sha,
        "rtdl_executable_identities": expected_executable_identities,
    }


def _rebuild_frozen_sources_independently(
        freeze: Mapping[str, Any], root: Path) \
        -> dict[str, dict[str, object]]:
    rows = freeze.get("source_manifest")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("independent frozen source manifest is absent")
    rebuilt: dict[str, dict[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping) or set(raw) != {
                "path", "bytes", "sha256"} \
                or not isinstance(raw.get("path"), str) \
                or type(raw.get("bytes")) is not int or raw["bytes"] < 0 \
                or not _valid_sha256(raw.get("sha256")):
            raise RuntimeError("independent frozen source row differs")
        relative = str(raw["path"])
        pure = PurePosixPath(relative)
        if not relative or pure.is_absolute() or ".." in pure.parts \
                or pure.as_posix() != relative or relative in rebuilt:
            raise RuntimeError("independent frozen source path differs")
        source = root.joinpath(*pure.parts)
        if source.is_symlink() or not source.is_file():
            raise RuntimeError(
                f"independent frozen source is not regular: {relative}")
        resolved = source.resolve(strict=True)
        if not resolved.is_relative_to(root) \
                or resolved.stat().st_size != raw["bytes"] \
                or _sha(resolved) != raw["sha256"]:
            raise RuntimeError(
                f"independent frozen source bytes differ: {relative}")
        rebuilt[relative] = {
            "absolute_path": str(resolved),
            "bytes": raw["bytes"],
            "sha256": raw["sha256"],
        }
    required = {
        PYOPTIX_SCALAR_SOURCE,
        GOAL5800_SOURCE,
        "experiments/goal5802_premeasurement/direct_scalar_worker.cpp",
        ("experiments/goal5802_premeasurement/"
         "matched_device_semantic_capacity.cu"),
        ("experiments/goal5802_premeasurement/"
         "relation_semantic_compaction.cu"),
        "experiments/goal5802_premeasurement/independent_recount.py",
        "scripts/goal5802_build_header_projection_untimed.py",
        "scripts/goal5802_nvrtc_compile_child.py",
        "scripts/goal5802_prepare_matched_ptx_untimed.py",
        THIS_VALIDATOR_SOURCE,
    }
    if not required.issubset(rebuilt):
        raise RuntimeError("independent required frozen source set differs")
    return rebuilt


def _independent_link_projection(
        freeze: Mapping[str, Any], runtime: Mapping[str, Any],
        frozen_sources: Mapping[str, Mapping[str, object]]) \
        -> dict[str, object]:
    """Independently restate every load-bearing freeze/runtime equality."""

    product = freeze.get("product_binding")
    files = runtime.get("files")
    directories = runtime.get("directories")
    deployments = runtime.get("deployment_ids")
    if not isinstance(product, Mapping) \
            or not isinstance(files, Mapping) \
            or not isinstance(directories, Mapping) \
            or not isinstance(deployments, Mapping):
        raise RuntimeError("independent preformal link inputs are absent")

    bindings = (
        ("rtdl_wheel", "wheel_sha256"),
        ("native_library", "native_sha256"),
        ("trust_root", "trust_root_sha256"),
        ("trust_head", "trust_head_sha256"),
        ("trust_package", "trust_package_sha256"),
        ("relation_artifact", "relation_artifact_sha256"),
        ("relation_authority", "relation_authority_sha256"),
        ("triangle_artifact", "triangle_artifact_sha256"),
        ("triangle_authority", "triangle_authority_sha256"),
        ("rtdsl_init", "rtdsl_init_sha256"),
        ("rtdlexe_module", "rtdlexe_module_sha256"),
    )
    product_projection: dict[str, str] = {}
    for runtime_role, product_key in bindings:
        record = files.get(runtime_role)
        expected = product.get(product_key)
        if not _valid_sha256(expected) \
                or not isinstance(record, Mapping) \
                or record.get("sha256") != expected:
            raise RuntimeError(
                "independent runtime/frozen-product link differs: "
                + runtime_role)
        product_projection[runtime_role] = str(expected)

    package = directories.get("rtdsl_package")
    if not isinstance(package, Mapping) \
            or package.get("file_count") \
            != product.get("rtdsl_package_file_count") \
            or package.get("tree_sha256") \
            != product.get("rtdsl_package_tree_sha256"):
        raise RuntimeError("independent installed RTDL package link differs")
    deployment_projection = {
        "relation": product.get("relation_deployment_id"),
        "triangle": product.get("triangle_deployment_id"),
    }
    if dict(deployments) != deployment_projection:
        raise RuntimeError("independent RTDL deployment link differs")

    source_bindings = (
        ("direct_scalar_source",
         "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"),
        ("device_source",
         "experiments/goal5802_premeasurement/"
         "matched_device_semantic_capacity.cu"),
        ("compaction_source",
         "experiments/goal5802_premeasurement/"
         "relation_semantic_compaction.cu"),
    )
    source_projection: dict[str, dict[str, str]] = {}
    for runtime_role, source_role in source_bindings:
        runtime_record = files.get(runtime_role)
        frozen_record = frozen_sources.get(source_role)
        if not isinstance(runtime_record, Mapping) \
                or not isinstance(frozen_record, Mapping) \
                or runtime_record.get("sha256") \
                != frozen_record.get("sha256"):
            raise RuntimeError(
                "independent runtime/frozen-source link differs: "
                + runtime_role)
        source_projection[runtime_role] = {
            "frozen_path": source_role,
            "sha256": str(frozen_record["sha256"]),
        }
    goal5800_record = frozen_sources.get(GOAL5800_SOURCE)
    pyoptix = runtime.get("pyoptix")
    if not isinstance(goal5800_record, Mapping) \
            or not isinstance(pyoptix, Mapping) \
            or pyoptix.get("goal5800_v7_source_sha256") \
            != goal5800_record.get("sha256"):
        raise RuntimeError("independent Goal5800 source link differs")
    source_projection["goal5800_v7_source"] = {
        "frozen_path": GOAL5800_SOURCE,
        "sha256": str(goal5800_record["sha256"]),
    }

    scalar = frozen_sources.get(PYOPTIX_SCALAR_SOURCE)
    executable_identities = {
        "relation": product.get("relation_executable_identity_sha256"),
        "triangle": product.get("triangle_executable_identity_sha256"),
    }
    if not isinstance(scalar, Mapping) \
            or not _valid_sha256(scalar.get("sha256")) \
            or any(not _valid_sha256(value)
                   for value in executable_identities.values()):
        raise RuntimeError("independent operation identity link differs")
    return {
        "product_files": product_projection,
        "rtdsl_package": {
            "file_count": package["file_count"],
            "tree_sha256": package["tree_sha256"],
        },
        "deployment_ids": deployment_projection,
        "frozen_source_files": source_projection,
        "pyoptix_scalar_source_sha256": scalar["sha256"],
        "rtdl_executable_identities": executable_identities,
    }


def _runtime_identity_projection(
        runtime: Mapping[str, Any]) -> dict[str, object]:
    files = runtime.get("files")
    directories = runtime.get("directories")
    if not isinstance(files, Mapping) or not isinstance(directories, Mapping):
        raise RuntimeError("runtime identity projection is absent")
    file_projection: dict[str, dict[str, object]] = {}
    for role, raw in files.items():
        if not isinstance(raw, Mapping):
            raise RuntimeError(f"runtime identity row differs: {role}")
        keys = (
            "path", "path_kind", "symlink_target", "resolved_path",
            "bytes", "sha256")
        file_projection[str(role)] = {
            key: raw[key] for key in keys if key in raw}
    directory_projection: dict[str, dict[str, object]] = {}
    for role, raw in directories.items():
        if not isinstance(raw, Mapping):
            raise RuntimeError(f"runtime tree identity row differs: {role}")
        keys = ("path", "file_count", "payload_bytes", "tree_sha256")
        directory_projection[str(role)] = {
            key: raw[key] for key in keys if key in raw}
    return {
        "schema": runtime.get("schema"),
        "status": runtime.get("status"),
        "manifest_sha256": runtime.get("manifest_sha256"),
        "files": file_projection,
        "directories": directory_projection,
        "deployment_ids": runtime.get("deployment_ids"),
        "pyoptix": runtime.get("pyoptix"),
        "target_observation": runtime.get("target_observation"),
        "target_policy": runtime.get("target_policy"),
        "architecture_contract": runtime.get("architecture_contract"),
        "build_provenance": runtime.get("build_provenance"),
        "formal_preflight_contract": runtime.get("formal_preflight_contract"),
    }


def build_pass_receipt(
        *, root: Path, freeze_path: Path, runtime_path: Path) \
        -> dict[str, object]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise RuntimeError("repository root is not a directory")
    if freeze_path.is_symlink() or runtime_path.is_symlink():
        raise RuntimeError("preformal input document must not be a symlink")
    freeze_path = freeze_path.resolve(strict=True)
    runtime_path = runtime_path.resolve(strict=True)
    freeze = _load_json_object(freeze_path)
    runtime = _load_json_object(runtime_path)
    freeze_file = _regular_file_identity(freeze_path)
    runtime_file = _regular_file_identity(runtime_path)

    contract.validate_freeze(freeze, root)
    runtime_manifest.validate_runtime_manifest(runtime)
    _validate_zero_locks(freeze, runtime)
    primary_links = _primary_link_projection(freeze, runtime)

    independent_recount._validate_freeze_bytes(
        freeze, freeze_file_sha256=str(freeze_file["sha256"]), root=root)
    frozen_sources = _rebuild_frozen_sources_independently(freeze, root)
    product = freeze.get("product_binding")
    if not isinstance(product, Mapping):
        raise RuntimeError("independent frozen product binding is absent")
    independent_recount._validate_runtime_bytes(
        runtime,
        expected_pyoptix_scalar_source_sha256=str(
            frozen_sources[PYOPTIX_SCALAR_SOURCE]["sha256"]),
        expected_rtdl_executable_identities={
            "relation": product.get(
                "relation_executable_identity_sha256"),
            "triangle": product.get(
                "triangle_executable_identity_sha256"),
        },
        expected_rtdsl_package_file_count=int(
            product["rtdsl_package_file_count"]),
        expected_rtdsl_package_tree_sha256=str(
            product["rtdsl_package_tree_sha256"]),
        frozen_sources=frozen_sources)
    independent_links = _independent_link_projection(
        freeze, runtime, frozen_sources)
    if primary_links != independent_links:
        raise RuntimeError(
            "primary and independent freeze/runtime link projections differ")

    receipt: dict[str, object] = {
        "schema": PASS_SCHEMA,
        "status": PASS_STATUS,
        "repository_root": str(root),
        "freeze_file": freeze_file,
        "runtime_manifest_file": runtime_file,
        "product_binding": dict(product),
        "product_binding_sha256": _digest(dict(product)),
        "runtime_identity_projection": _runtime_identity_projection(runtime),
        "runtime_identity_projection_sha256": _digest(
            _runtime_identity_projection(runtime)),
        "freeze_to_runtime_projection": primary_links,
        "freeze_to_runtime_projection_sha256": _digest(primary_links),
        "primary_validation": {
            "contract_validate_freeze": "PASS",
            "runtime_manifest_validate_runtime_manifest": "PASS",
            "strict_operation_kats_and_executable_identities": "PASS",
            "freeze_to_runtime_binding": "PASS",
        },
        "independent_validation": {
            "independent_freeze_byte_validation": "PASS",
            "independent_runtime_byte_validation": "PASS",
            "independent_frozen_source_rebuild": "PASS",
            "independently_reimplemented_freeze_to_runtime_binding": "PASS",
        },
        "validation_paths_exact_projection_equal": True,
        "execution_authority_accepted_as_input": False,
        "execution_authority_consumed": False,
        "formal_execution_authorized": False,
        "live_worker_zero_preflight_still_required": True,
        "formal_worker_zero_reached": False,
        "validation_attempt_count": 1,
        "retry_count": 0,
        "replacement_count": 0,
        "same_transaction_retry_allowed": False,
        "result_conditioned_replacement_allowed": False,
        "activity_count_scope": (
            "THIS_STATIC_VALIDATOR_INVOCATION_ONLY__PRESERVED_OPERATION_KATS_"
            "ARE_REVALIDATED_NOT_REEXECUTED"),
        "preserved_runtime_operation_kats_reexecuted": False,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
    }
    receipt["receipt_sha256"] = _digest(receipt)
    return receipt


def _failure_receipt(
        *, root: Path, freeze_path: Path, runtime_path: Path,
        error: Exception) -> dict[str, object]:
    receipt: dict[str, object] = {
        "schema": FAILURE_SCHEMA,
        "status": FAILURE_STATUS,
        "repository_root": str(root.resolve(strict=False)),
        "freeze_file": _best_effort_file_identity(freeze_path),
        "runtime_manifest_file": _best_effort_file_identity(runtime_path),
        "failure": {
            "class": type(error).__name__,
            "message": str(error),
        },
        "validation_completed": False,
        "failure_disposition": (
            "PRESERVE_RECEIPT__DO_NOT_AUTHORIZE_FORMAL_EXECUTION__"
            "DO_NOT_REUSE_THIS_CREATE_ONLY_OUTPUT"),
        "execution_authority_accepted_as_input": False,
        "execution_authority_consumed": False,
        "formal_execution_authorized": False,
        "live_worker_zero_preflight_still_required": True,
        "formal_worker_zero_reached": False,
        "validation_attempt_count": 1,
        "retry_count": 0,
        "replacement_count": 0,
        "same_transaction_retry_allowed": False,
        "result_conditioned_replacement_allowed": False,
        "activity_count_scope": (
            "THIS_STATIC_VALIDATOR_INVOCATION_ONLY__PRESERVED_OPERATION_KATS_"
            "ARE_NOT_REEXECUTED"),
        "preserved_runtime_operation_kats_reexecuted": False,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
    }
    receipt["receipt_sha256"] = _digest(receipt)
    return receipt


def run(
        *, root: Path, freeze_path: Path, runtime_path: Path,
        output: Path) -> int:
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    try:
        receipt = build_pass_receipt(
            root=root, freeze_path=freeze_path, runtime_path=runtime_path)
    except Exception as error:
        receipt = _failure_receipt(
            root=root, freeze_path=freeze_path, runtime_path=runtime_path,
            error=error)
        _write_new(output, receipt)
        print(json.dumps({
            "status": receipt["status"],
            "receipt_sha256": receipt["receipt_sha256"],
        }, sort_keys=True))
        return 1
    _write_new(output, receipt)
    print(json.dumps({
        "status": receipt["status"],
        "receipt_sha256": receipt["receipt_sha256"],
    }, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    return run(
        root=args.root, freeze_path=args.freeze,
        runtime_path=args.runtime_manifest, output=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
