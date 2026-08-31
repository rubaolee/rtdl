"""Create the zero-worker Goal5814 target/request/closure transaction.

This utility does not execute Particle, launch OptiX, or read a performance
clock.  It only records and validates the exact target products and the
bounded owner-scope control plane consumed by the formal controller.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib
import importlib.metadata
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

from .measurement_protocol import (
    BLOCK_ORDER_RULE,
    BOOTSTRAP_RULE,
    CACHE_RULE,
    CLOCK_RULE,
    CUPY_WHEEL_SHA256,
    EXECUTION_CONCURRENCY_RULE,
    EXECUTION_REQUEST_SCHEMA,
    INVALID_ROW_RULE,
    NUMPY_WHEEL_SHA256,
    OWNER_DIRECTIVE_RECEIPT_RELATIVE_PATH,
    PREACTION_RELATIVE_PATH,
    PROJECT_CLOSURE_SCHEMA,
    PYOPTIX_WHEEL_SHA256,
    SCHEDULE_SHA256,
    SOURCE_ROLE_PATHS,
    STEADY_MEDIAN_RULE,
    TARGET_MANIFEST_SCHEMA,
    TOTAL_WORKER_COUNT,
    WORKER_TIMEOUT_SECONDS,
    canonical_document,
    digest,
    file_record,
    validate_authority_window,
    validate_execution_request,
    validate_owner_directive_receipt,
    validate_preaction,
    validate_project_closure,
    validate_target_manifest,
)


class MaterializationError(RuntimeError):
    """The exact zero-worker transaction could not be materialized."""


def _parse_utc(value: str, label: str) -> datetime:
    if not value.endswith("Z"):
        raise MaterializationError(f"{label} is not canonical UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise MaterializationError(f"{label} is not canonical UTC") from error
    if parsed.tzinfo != timezone.utc:
        raise MaterializationError(f"{label} is not canonical UTC")
    return parsed


def _write_create_only(path: Path, value: object) -> None:
    with path.open("xb") as stream:
        stream.write(canonical_document(value))


def _wheel_by_sha(directory: Path, expected_sha: str) -> Path:
    matches = [
        path.resolve(strict=True)
        for path in directory.glob("*.whl")
        if file_record(path)["sha256"] == expected_sha
    ]
    if len(matches) != 1:
        raise MaterializationError(
            f"expected exactly one wheel for SHA-256 {expected_sha}")
    return matches[0]


def _gpu_identity(nvidia_smi: Path, selector: str) -> dict[str, Any]:
    completed = subprocess.run(
        [
            str(nvidia_smi), f"--id={selector}",
            "--query-gpu=uuid,name,compute_cap,driver_version,memory.total",
            "--format=csv,noheader,nounits",
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    rows = completed.stdout.decode("utf-8").strip().splitlines()
    fields = [part.strip() for part in rows[0].split(",")] \
        if len(rows) == 1 else []
    if completed.returncode != 0 or len(fields) != 5:
        raise MaterializationError("selected GPU identity query failed")
    try:
        memory_mib = int(fields[4])
    except ValueError as error:
        raise MaterializationError("selected GPU memory identity differs") \
            from error
    return {
        "gpu_uuid": fields[0],
        "gpu_name": fields[1],
        "compute_capability": fields[2],
        "driver_version": fields[3],
        "gpu_memory_total_mib": memory_mib,
    }


def _sealed(value: dict[str, Any], key: str) -> dict[str, Any]:
    result = dict(value)
    result[key] = digest(result)
    return result


def materialize(
        *, root: Path, native_directory: Path, scientific_directory: Path,
        wheelhouse: Path, output_directory: Path, gpu_selector: str,
        cuda_visible_devices: str, not_before_utc: str,
        not_after_utc: str) -> dict[str, Any]:
    resolved_root = root.resolve(strict=True)
    native = native_directory.resolve(strict=True)
    scientific = scientific_directory.resolve(strict=True)
    wheels = wheelhouse.resolve(strict=True)
    output = output_directory.absolute()
    if output.exists():
        raise MaterializationError("transaction output directory already exists")
    before = _parse_utc(not_before_utc, "not-before")
    after = _parse_utc(not_after_utc, "not-after")
    if after <= before or (after - before).total_seconds() > 8 * 60 * 60:
        raise MaterializationError("transaction window is empty or exceeds 8h")

    preaction_path = (resolved_root / PREACTION_RELATIVE_PATH).resolve(
        strict=True)
    owner_receipt_path = (
        resolved_root / OWNER_DIRECTIVE_RECEIPT_RELATIVE_PATH).resolve(
            strict=True)
    validate_preaction(preaction_path)
    validate_owner_directive_receipt(owner_receipt_path, root=resolved_root)

    numpy = importlib.import_module("numpy")
    cupy = importlib.import_module("cupy")
    optix = importlib.import_module("optix")
    extension = importlib.import_module("optix._optix")
    nvidia_smi = Path("/usr/bin/nvidia-smi").resolve(strict=True)
    python_executable = Path(sys.executable).resolve(strict=True)
    manifest = native / "executable_manifest.json"
    ptx = native / (
        "9484a5a4e600885d335cff16130e9cbbc0d1c5d8ed6d24297e2ecb202e0c6e67."
        "compute_86.pass1.ptx")
    artifact = native / (
        "14e3688ada1f9297a6dbb628e4debcbac4e6ad790ceeb3619717d7a12d76f099."
        "rtdlexe")
    files: dict[str, Any] = {
        role: file_record(resolved_root / relative)
        for role, relative in SOURCE_ROLE_PATHS.items()
    }
    files.update({
        "preaction": file_record(preaction_path),
        "scientific_manifest": file_record(
            scientific / "SCIENTIFIC_INPUT_MANIFEST.json"),
        "executable_manifest": file_record(manifest),
        "prebuilt_ptx": file_record(ptx),
        "native_dso": file_record(native / "librtdl_optix.so"),
        "rtdlexe": file_record(artifact),
        "nvidia_smi": file_record(nvidia_smi),
        "python_executable": file_record(python_executable),
        "numpy_module": file_record(Path(numpy.__file__)),
        "cupy_module": file_record(Path(cupy.__file__)),
        "optix_module": file_record(Path(optix.__file__)),
        "pyoptix_extension": file_record(Path(extension.__file__)),
        "pyoptix_wheel": file_record(
            _wheel_by_sha(wheels, PYOPTIX_WHEEL_SHA256)),
        "cupy_wheel": file_record(
            _wheel_by_sha(wheels, CUPY_WHEEL_SHA256)),
        "numpy_wheel": file_record(
            _wheel_by_sha(wheels, NUMPY_WHEEL_SHA256)),
        "target_kat_preaction": file_record(
            resolved_root / "history/internal_docs/"
            "goal5814_particle_rtxa5000_untimed_exact_core_kat_v4_"
            "readonly_view_repair_preaction_20260828.json"),
        "target_kat_result": file_record(
            resolved_root / "history/internal_docs/"
            "goal5814_particle_rtxa5000_untimed_exact_core_kat_v4_result_"
            "20260828.json"),
    })

    target_identity = {
        "hostname": platform.node(),
        "gpu_selector": gpu_selector,
        **_gpu_identity(nvidia_smi, gpu_selector),
        "cuda_visible_devices": cuda_visible_devices,
        "python_version": platform.python_version(),
        "numpy_version": str(numpy.__version__),
        "cupy_version": str(cupy.__version__),
        "pyoptix_distribution_version": importlib.metadata.version("pyoptix"),
        "optix_api_version": ".".join(str(item) for item in optix.version()),
        "ld_library_path": os.environ.get("LD_LIBRARY_PATH"),
        "ld_preload": os.environ.get("LD_PRELOAD"),
    }
    target = _sealed({
        "schema": TARGET_MANIFEST_SCHEMA,
        "status": "PREPARED_TARGET_PRODUCTS__WORKER_ZERO",
        "target": target_identity,
        "scientific_input_directory": str(scientific),
        "files": files,
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }, "target_manifest_sha256")

    output.mkdir(parents=True, exist_ok=False)
    target_path = output / "target_manifest.json"
    _write_create_only(target_path, target)
    validated_target = validate_target_manifest(
        target_path, root=resolved_root, rehash=True)

    common = {
        "owner_directive_receipt_file": file_record(owner_receipt_path),
        "preaction_file": file_record(preaction_path),
        "scientific_manifest": files["scientific_manifest"],
        "executable_manifest": files["executable_manifest"],
        "target_manifest_file": file_record(target_path),
        "schedule_sha256": SCHEDULE_SHA256,
        "clock_rule": CLOCK_RULE,
        "steady_median_rule": STEADY_MEDIAN_RULE,
        "bootstrap_rule": BOOTSTRAP_RULE,
        "block_order_rule": BLOCK_ORDER_RULE,
        "execution_concurrency_rule": EXECUTION_CONCURRENCY_RULE,
        "cache_rule": CACHE_RULE,
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "authorization_not_before_utc": not_before_utc,
        "authorization_not_after_utc": not_after_utc,
        "invalid_row_rule": INVALID_ROW_RULE,
        "owner_target_bound_exact_bytes_approval_claimed": False,
        "project_materialized_under_owner_scope": True,
        "descriptive_unconditional_acceptance": True,
        "confirmatory_noninferiority_claim": False,
        "threshold_count": 0,
        "retry_resume_replacement_or_row_drop_allowed": False,
        "total_worker_count": TOTAL_WORKER_COUNT,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    request = _sealed({
        "schema": EXECUTION_REQUEST_SCHEMA,
        "status": "PROJECT_PREPARED__TARGET_BOUND__NONAUTHORIZING_REQUEST",
        **common,
        "formal_worker_zero_authorized": False,
        "pod_gpu_timing_authorized": False,
    }, "execution_request_sha256")
    request_path = output / "execution_request.json"
    _write_create_only(request_path, request)
    validated_request = validate_execution_request(
        request_path, preaction_path=preaction_path,
        target_manifest_path=target_path, target_manifest=validated_target,
        owner_receipt_path=owner_receipt_path)

    closure_common = dict(common)
    closure_common["execution_request_file"] = file_record(request_path)
    closure = _sealed({
        "schema": PROJECT_CLOSURE_SCHEMA,
        "status": (
            "PROJECT_CLOSED_UNDER_EXACT_BROAD_OWNER_SCOPE__NOT_OWNER_"
            "EXACT_BYTE_APPROVAL"),
        **closure_common,
        "formal_worker_zero_authorized_under_owner_scope": True,
        "pod_gpu_timing_authorized_under_owner_scope": True,
    }, "project_closure_sha256")
    closure_path = output / "project_closure.json"
    _write_create_only(closure_path, closure)
    validated_closure = validate_project_closure(
        closure_path, preaction_path=preaction_path,
        target_manifest_path=target_path,
        execution_request_path=request_path,
        target_manifest=validated_target,
        execution_request=validated_request,
        owner_receipt_path=owner_receipt_path)
    validate_authority_window(validated_closure)
    return {
        "status": "PASS__ZERO_WORKER_TRANSACTION_MATERIALIZED",
        "target_manifest_file": file_record(target_path),
        "execution_request_file": file_record(request_path),
        "project_closure_file": file_record(closure_path),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--native-directory", type=Path, required=True)
    parser.add_argument("--scientific-directory", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--gpu-selector", default="0")
    parser.add_argument("--cuda-visible-devices", default="0")
    parser.add_argument("--not-before-utc", required=True)
    parser.add_argument("--not-after-utc", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = materialize(
        root=args.root,
        native_directory=args.native_directory,
        scientific_directory=args.scientific_directory,
        wheelhouse=args.wheelhouse,
        output_directory=args.output_directory,
        gpu_selector=args.gpu_selector,
        cuda_visible_devices=args.cuda_visible_devices,
        not_before_utc=args.not_before_utc,
        not_after_utc=args.not_after_utc,
    )
    print(canonical_document(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
