#!/usr/bin/env python3
"""Build and seal the two frozen Goal5848 baseline device products."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from experiments.goal5848_strong_baseline.contracts import digest, strict_json_loads
from experiments.goal5848_strong_baseline.controller import _new_output_root
from experiments.goal5848_strong_baseline.device_artifacts import (
    COMPACTION_SOURCE_RELATIVE,
    COMPILER_CHILD_RELATIVE,
    DEVICE_ARTIFACT_RECEIPT_SCHEMA,
    DEVICE_ARTIFACT_RECEIPT_STATUS,
    DEVICE_SOURCE_RELATIVE,
    _file_identity,
    _git_identity,
    _source_identity,
    load_device_artifact_receipt,
)
from scripts.goal5802_prepare_matched_ptx_untimed import architecture_contract

ROOT = Path(__file__).resolve().parents[1]


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


def _python_identity(path: Path) -> dict[str, object]:
    invocation = path.expanduser().absolute()
    if not invocation.is_file():
        raise RuntimeError("Goal5848 device builder Python is unavailable")
    return {"invocation_path": str(invocation), **_file_identity(invocation.resolve())}


def _run_child(
    *,
    python: Path,
    mode: str,
    source: Path,
    optix_include: Path,
    cuda_include: Path,
    compute_capability: str,
    nvrtc_library: Path | None,
    output: Path,
    receipt: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    child = (ROOT / COMPILER_CHILD_RELATIVE).resolve(strict=True)
    command = [
        str(python),
        str(child),
        "--mode",
        mode,
        "--source",
        str(source),
        "--compute-capability",
        compute_capability,
        "--output",
        str(output),
        "--receipt",
        str(receipt),
    ]
    if mode == "ptx":
        command.extend(
            [
                "--optix-include",
                str(optix_include),
                "--cuda-include",
                str(cuda_include),
            ]
        )
    if nvrtc_library is not None:
        command.extend(["--nvrtc-library", str(nvrtc_library)])
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0 or completed.stderr or not receipt.is_file():
        raise RuntimeError(
            {
                "mode": mode,
                "exit_code": completed.returncode,
                "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
            }
        )
    try:
        stdout = completed.stdout.decode("utf-8")
    except UnicodeError as error:
        raise RuntimeError("Goal5848 device compiler stdout is not UTF-8") from error
    child_value = strict_json_loads(
        receipt.read_text(encoding="utf-8"),
        label=f"Goal5848 device compiler child {mode}",
    )
    if not isinstance(child_value, dict):
        raise TypeError("Goal5848 device compiler receipt is not an object")
    process = {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_utf8": stdout,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_utf8": "",
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        "child_receipt_file": _file_identity(receipt),
    }
    return child_value, process


def build(args: argparse.Namespace) -> tuple[Path, dict[str, object]]:
    source_identity = _git_identity(ROOT)
    if (
        source_identity["commit"] != args.expected_source_commit
        or source_identity["clean"] is not True
    ):
        raise RuntimeError("Goal5848 device build source identity differs")
    optix_source = args.optix_source.resolve(strict=True)
    optix_identity = _git_identity(optix_source)
    if (
        optix_identity["commit"] != args.expected_optix_commit
        or optix_identity["tree"] != args.expected_optix_tree
        or optix_identity["clean"] is not True
    ):
        raise RuntimeError("Goal5848 OptiX header source identity differs")
    optix_include = args.optix_include.resolve(strict=True)
    cuda_include = args.cuda_include.resolve(strict=True)
    if (
        not optix_include.is_relative_to(optix_source)
        or not cuda_include.is_dir()
    ):
        raise RuntimeError("Goal5848 device build include roots differ")
    if args.expected_optix_sdk.count(".") != 2:
        raise RuntimeError("Goal5848 expected OptiX SDK text differs")
    version_parts = [int(item) for item in args.expected_optix_sdk.split(".")]
    expected_optix_version = (
        version_parts[0] * 10000 + version_parts[1] * 100 + version_parts[2]
    )
    optix_h = (optix_include / "optix.h").read_text(encoding="utf-8")
    marker = re.search(
        r"(?m)^\s*#\s*define\s+OPTIX_VERSION\s+([0-9]+)\s*$",
        optix_h,
    )
    if marker is None or int(marker.group(1)) != expected_optix_version:
        raise RuntimeError("Goal5848 OptiX header/API version differs")
    canonical, compute_architecture, sm_architecture = architecture_contract(
        args.compute_capability
    )
    if canonical != args.compute_capability:
        raise RuntimeError("Goal5848 compute capability is not canonical")
    nvrtc_library = (
        args.nvrtc_library.resolve(strict=True)
        if args.nvrtc_library is not None
        else None
    )
    if nvrtc_library is not None and nvrtc_library.is_symlink():
        raise RuntimeError("Goal5848 pinned NVRTC library must be resolved")

    output_root = _new_output_root(args.output_root)
    output_root.mkdir(parents=True)
    ptx = output_root / "matched_device.ptx"
    cubin = output_root / "relation_semantic_compaction.cubin"
    ptx_receipt_path = output_root / "ptx_child_receipt.json"
    cubin_receipt_path = output_root / "cubin_child_receipt.json"
    receipt_path = output_root / "device_artifact_build_receipt.json"
    stage = "PTX"
    try:
        ptx_child, ptx_process = _run_child(
            python=args.python.expanduser().absolute(),
            mode="ptx",
            source=(ROOT / DEVICE_SOURCE_RELATIVE).resolve(strict=True),
            optix_include=optix_include,
            cuda_include=cuda_include,
            compute_capability=canonical,
            nvrtc_library=nvrtc_library,
            output=ptx,
            receipt=ptx_receipt_path,
        )
        stage = "COMPACTION_CUBIN"
        cubin_child, cubin_process = _run_child(
            python=args.python.expanduser().absolute(),
            mode="cubin",
            source=(ROOT / COMPACTION_SOURCE_RELATIVE).resolve(strict=True),
            optix_include=optix_include,
            cuda_include=cuda_include,
            compute_capability=canonical,
            nvrtc_library=nvrtc_library,
            output=cubin,
            receipt=cubin_receipt_path,
        )
        value: dict[str, object] = {
            "schema": DEVICE_ARTIFACT_RECEIPT_SCHEMA,
            "status": DEVICE_ARTIFACT_RECEIPT_STATUS,
            "source_identity": source_identity,
            "sources": {
                "device_source": _source_identity(ROOT, DEVICE_SOURCE_RELATIVE),
                "compaction_source": _source_identity(
                    ROOT, COMPACTION_SOURCE_RELATIVE
                ),
                "compiler_child": _source_identity(ROOT, COMPILER_CHILD_RELATIVE),
            },
            "python": _python_identity(args.python),
            "optix_headers_identity": optix_identity,
            "optix_include_path": str(optix_include),
            "cuda_include_path": str(cuda_include),
            "expected_optix_sdk": args.expected_optix_sdk,
            "compute_capability": canonical,
            "compute_architecture": compute_architecture,
            "sm_architecture": sm_architecture,
            "builder_pid": os.getpid(),
            "compiler_processes": {
                "ptx": ptx_process,
                "compaction_cubin": cubin_process,
            },
            "compiler_receipts": {
                "ptx": ptx_child,
                "compaction_cubin": cubin_child,
            },
            "outputs": {
                "precompiled_ptx": _file_identity(ptx),
                "compaction_cubin": _file_identity(cubin),
            },
            "derivation_scope": (
                "SOURCE_AND_PRODUCT_BOUND__NOT_A_HERMETIC_CUDA_HEADER_CLOSURE"
            ),
            "clock_read_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "formal_worker_count": 0,
            "retry_count": 0,
            "discard_count": 0,
            "public_or_manuscript_claim_authorized": False,
        }
        value["receipt_sha256"] = digest(value)
        _write_create(receipt_path, value)
        load_device_artifact_receipt(
            receipt_path,
            precompiled_ptx=ptx,
            compaction_cubin=cubin,
            expected_source_commit=args.expected_source_commit,
            expected_optix_sdk=args.expected_optix_sdk,
            expected_compute_capability=canonical,
        )
        return receipt_path, value
    except BaseException as error:
        failure = {
            "schema": "rtdl.goal5848.device_artifact_build_failure.v1",
            "status": "FAIL__NO_RETRY_NO_DISCARD",
            "failed_stage": stage,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "retry_count": 0,
            "discard_count": 0,
        }
        failure["failure_sha256"] = digest(failure)
        _write_create(output_root / "failure.json", failure)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--optix-source", type=Path, required=True)
    parser.add_argument("--expected-optix-commit", required=True)
    parser.add_argument("--expected-optix-tree", required=True)
    parser.add_argument("--expected-optix-sdk", required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--nvrtc-library", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    _receipt_path, value = build(args)
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
