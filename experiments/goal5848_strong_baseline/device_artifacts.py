"""Validate the frozen PTX/CUBIN build provenance for Goal5848.

This module is standard-library only.  Formal controllers and the independent
authority use it before trusting the device products shared by the PyOptix and
Direct OptiX arms.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
import subprocess
from collections.abc import Mapping
from pathlib import Path

from scripts.goal5802_prepare_matched_ptx_untimed import architecture_contract

from .contracts import digest, strict_json_loads

ROOT = Path(__file__).resolve().parents[2]
DEVICE_SOURCE_RELATIVE = Path(
    "experiments/goal5802_premeasurement/matched_device_semantic_capacity.cu"
)
COMPACTION_SOURCE_RELATIVE = Path(
    "experiments/goal5802_premeasurement/relation_semantic_compaction.cu"
)
COMPILER_CHILD_RELATIVE = Path("scripts/goal5802_nvrtc_compile_child.py")
DEVICE_ARTIFACT_RECEIPT_SCHEMA = "rtdl.goal5848.device_artifact_build.v1"
DEVICE_ARTIFACT_RECEIPT_STATUS = (
    "PASS__TWO_FRESH_PROCESS_UNTIMED_NVRTC_PRODUCTS"
)
CHILD_SCHEMA = "rtdl.goal5802.fresh_nvrtc_compile_child.v2"
CHILD_STATUS = "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE"


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _file_identity(path: Path) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError("Goal5848 device provenance rejects symlink")
    resolved = path.resolve(strict=True)
    metadata = resolved.stat()
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError("Goal5848 device provenance requires regular file")
    return {
        "path": str(resolved),
        "bytes": metadata.st_size,
        "sha256": _sha256_file(resolved),
    }


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_identity(root: Path) -> dict[str, object]:
    resolved = root.resolve(strict=True)
    status = _git(resolved, "status", "--porcelain=v1", "--untracked-files=all")
    return {
        "path": str(resolved),
        "commit": _git(resolved, "rev-parse", "HEAD"),
        "tree": _git(resolved, "rev-parse", "HEAD^{tree}"),
        "status": status,
        "clean": status == "",
    }


def _source_identity(repository_root: Path, relative: Path) -> dict[str, object]:
    path = repository_root / relative
    identity = _file_identity(path)
    tracked = _git(repository_root, "ls-files", "--error-unmatch", relative.as_posix())
    if tracked != relative.as_posix():
        raise RuntimeError("Goal5848 device source is not exact tracked path")
    committed = subprocess.run(
        ["git", "-C", str(repository_root), "show", f"HEAD:{relative.as_posix()}"],
        check=True,
        capture_output=True,
    ).stdout
    if hashlib.sha256(committed).hexdigest() != identity["sha256"]:
        raise RuntimeError("Goal5848 device source differs from HEAD")
    return {"relative_path": relative.as_posix(), **identity}


def _valid_optix_sdk(text: object) -> bool:
    return (
        isinstance(text, str)
        and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", text) is not None
    )


def _optix_sdk_number(text: str) -> int:
    if not _valid_optix_sdk(text):
        raise RuntimeError("Goal5848 expected OptiX SDK text differs")
    major, minor, patch = (int(item) for item in text.split("."))
    return major * 10_000 + minor * 100 + patch


def _validate_loaded_nvrtc(value: object) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "library",
        "builtins",
        "version",
    }:
        raise RuntimeError("Goal5848 loaded NVRTC identity differs")
    version = value.get("version")
    if (
        not isinstance(version, list)
        or len(version) != 2
        or any(type(item) is not int or item < 0 for item in version)
    ):
        raise RuntimeError("Goal5848 loaded NVRTC version differs")
    for label in ("library", "builtins"):
        row = value.get(label)
        if not isinstance(row, Mapping) or set(row) != {
            "path",
            "bytes",
            "sha256",
            "canonical_regular_file",
            "symlink",
        }:
            raise RuntimeError("Goal5848 loaded NVRTC file row differs")
        if (
            row.get("canonical_regular_file") is not True
            or row.get("symlink") is not False
        ):
            raise RuntimeError("Goal5848 loaded NVRTC file kind differs")
        observed = _file_identity(Path(str(row["path"])))
        if observed != {
            "path": row["path"],
            "bytes": row["bytes"],
            "sha256": row["sha256"],
        }:
            raise RuntimeError("Goal5848 loaded NVRTC bytes differ")


def _expected_child_options(
    *,
    mode: str,
    compute_capability: str,
    optix_include: Path,
    cuda_include: Path,
) -> tuple[list[str], str]:
    _canonical, compute_architecture, sm_architecture = architecture_contract(
        compute_capability
    )
    if mode == "ptx":
        return (
            [
                "--std=c++17",
                "--device-as-default-execution-space",
                "--relocatable-device-code=true",
                f"--gpu-architecture={compute_architecture}",
                f"-I{optix_include}",
                f"-I{cuda_include}",
                f"-I{cuda_include / 'nv'}",
            ],
            sm_architecture,
        )
    return (
        [
            "--std=c++17",
            "--device-as-default-execution-space",
            f"--gpu-architecture={sm_architecture}",
        ],
        sm_architecture,
    )


def _validate_child(
    value: object,
    *,
    mode: str,
    source: Mapping[str, object],
    product: Mapping[str, object],
    compute_capability: str,
    optix_include: Path,
    cuda_include: Path,
    builder_pid: int,
    expected_cwd: Path,
) -> None:
    if not isinstance(value, Mapping):
        raise TypeError("Goal5848 compiler child receipt is absent")
    unsigned = dict(value)
    seal = unsigned.pop("receipt_sha256", None)
    expected_keys = {
        "schema",
        "status",
        "pid",
        "parent_pid",
        "argv",
        "cwd",
        "mode",
        "source",
        "include_roots",
        "compute_capability",
        "compile_options",
        "target",
        "product",
        "loaded_nvrtc",
        "clock_read_count",
        "gpu_kernel_launch_count",
        "formal_worker_count",
        "registered_performance_timing_count",
        "receipt_sha256",
    }
    expected_options, expected_target = _expected_child_options(
        mode=mode,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
    )
    expected_source = {
        "path": source["path"],
        "bytes": source["bytes"],
        "sha256": source["sha256"],
    }
    expected_includes = {
        "optix": str(optix_include) if mode == "ptx" else None,
        "cuda": str(cuda_include) if mode == "ptx" else None,
    }
    if (
        set(value) != expected_keys
        or seal != digest(unsigned)
        or value.get("schema") != CHILD_SCHEMA
        or value.get("status") != CHILD_STATUS
        or type(value.get("pid")) is not int
        or value["pid"] <= 0
        or value.get("parent_pid") != builder_pid
        or not isinstance(value.get("argv"), list)
        or value.get("cwd") != str(expected_cwd)
        or value.get("mode") != mode
        or value.get("source") != expected_source
        or value.get("include_roots") != expected_includes
        or value.get("compute_capability") != compute_capability
        or value.get("compile_options") != expected_options
        or value.get("target") != expected_target
        or value.get("product") != product
        or any(
            type(value.get(field)) is not int or value[field] != 0
            for field in (
                "clock_read_count",
                "gpu_kernel_launch_count",
                "formal_worker_count",
                "registered_performance_timing_count",
            )
        )
    ):
        raise RuntimeError("Goal5848 compiler child contract differs")
    _validate_loaded_nvrtc(value.get("loaded_nvrtc"))


def _validate_process(
    value: object,
    *,
    child: Mapping[str, object],
    receipt_file: Mapping[str, object],
    python_invocation_path: str,
) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "command",
        "exit_code",
        "stdout_utf8",
        "stdout_sha256",
        "stderr_utf8",
        "stderr_sha256",
        "child_receipt_file",
    }:
        raise RuntimeError("Goal5848 compiler process receipt differs")
    stdout = json.dumps(
        {
            "pid": child["pid"],
            "product_sha256": child["product"]["sha256"],
            "receipt_sha256": child["receipt_sha256"],
            "status": CHILD_STATUS,
        },
        sort_keys=True,
    ) + "\n"
    command = value.get("command")
    if (
        not isinstance(command, list)
        or not command
        or command[0] != python_invocation_path
        or command[1:] != child.get("argv")
        or value.get("exit_code") != 0
        or value.get("stdout_utf8") != stdout
        or value.get("stdout_sha256")
        != hashlib.sha256(stdout.encode("utf-8")).hexdigest()
        or value.get("stderr_utf8") != ""
        or value.get("stderr_sha256") != hashlib.sha256(b"").hexdigest()
        or value.get("child_receipt_file") != receipt_file
        or _file_identity(Path(str(receipt_file["path"]))) != receipt_file
    ):
        raise RuntimeError("Goal5848 compiler process execution differs")


def validate_device_artifact_receipt(
    value: object,
    *,
    precompiled_ptx: Path,
    compaction_cubin: Path,
    expected_source_commit: str,
    expected_optix_sdk: str,
    expected_compute_capability: str | None = None,
    repository_root: Path = ROOT,
) -> dict[str, object]:
    """Validate a receipt and every live byte on which it depends."""

    if not isinstance(value, Mapping):
        raise TypeError("Goal5848 device artifact receipt is absent")
    unsigned = dict(value)
    seal = unsigned.pop("receipt_sha256", None)
    expected_keys = {
        "schema",
        "status",
        "source_identity",
        "sources",
        "python",
        "optix_headers_identity",
        "optix_include_path",
        "cuda_include_path",
        "expected_optix_sdk",
        "compute_capability",
        "compute_architecture",
        "sm_architecture",
        "builder_pid",
        "compiler_processes",
        "compiler_receipts",
        "outputs",
        "derivation_scope",
        "clock_read_count",
        "registered_performance_timing_count",
        "gpu_kernel_launch_count",
        "formal_worker_count",
        "retry_count",
        "discard_count",
        "public_or_manuscript_claim_authorized",
        "receipt_sha256",
    }
    if (
        set(value) != expected_keys
        or seal != digest(unsigned)
        or value.get("schema") != DEVICE_ARTIFACT_RECEIPT_SCHEMA
        or value.get("status") != DEVICE_ARTIFACT_RECEIPT_STATUS
        or value.get("expected_optix_sdk") != expected_optix_sdk
        or not _valid_optix_sdk(value.get("expected_optix_sdk"))
        or type(value.get("builder_pid")) is not int
        or value["builder_pid"] <= 0
        or value.get("derivation_scope")
        != "SOURCE_AND_PRODUCT_BOUND__NOT_A_HERMETIC_CUDA_HEADER_CLOSURE"
        or value.get("public_or_manuscript_claim_authorized") is not False
        or any(
            type(value.get(field)) is not int or value[field] != 0
            for field in (
                "clock_read_count",
                "registered_performance_timing_count",
                "gpu_kernel_launch_count",
                "formal_worker_count",
                "retry_count",
                "discard_count",
            )
        )
    ):
        raise RuntimeError("Goal5848 device artifact receipt contract differs")

    repository = repository_root.resolve(strict=True)
    source_identity = value.get("source_identity")
    observed_source_identity = _git_identity(repository)
    if (
        not isinstance(source_identity, Mapping)
        or source_identity.get("path") != str(repository)
        or source_identity.get("commit") != expected_source_commit
        or source_identity.get("clean") is not True
        or observed_source_identity != source_identity
    ):
        raise RuntimeError("Goal5848 device artifact source identity differs")

    sources = value.get("sources")
    expected_sources = {
        "device_source": _source_identity(repository, DEVICE_SOURCE_RELATIVE),
        "compaction_source": _source_identity(
            repository, COMPACTION_SOURCE_RELATIVE
        ),
        "compiler_child": _source_identity(repository, COMPILER_CHILD_RELATIVE),
    }
    if not isinstance(sources, Mapping) or dict(sources) != expected_sources:
        raise RuntimeError("Goal5848 device artifact source bytes differ")

    outputs = value.get("outputs")
    expected_outputs = {
        "precompiled_ptx": _file_identity(precompiled_ptx),
        "compaction_cubin": _file_identity(compaction_cubin),
    }
    if not isinstance(outputs, Mapping) or dict(outputs) != expected_outputs:
        raise RuntimeError("Goal5848 device artifact output bytes differ")
    if b".version" not in precompiled_ptx.read_bytes()[:4096]:
        raise RuntimeError("Goal5848 precompiled PTX header differs")
    if compaction_cubin.read_bytes()[:4] != b"\x7fELF":
        raise RuntimeError("Goal5848 compaction product is not ELF")

    compute_capability = value.get("compute_capability")
    if not isinstance(compute_capability, str):
        raise TypeError("Goal5848 compute capability differs")
    canonical, compute_architecture, sm_architecture = architecture_contract(
        compute_capability
    )
    if (
        canonical != compute_capability
        or value.get("compute_architecture") != compute_architecture
        or value.get("sm_architecture") != sm_architecture
        or (
            expected_compute_capability is not None
            and compute_capability != expected_compute_capability
        )
    ):
        raise RuntimeError("Goal5848 device artifact target differs")

    optix_include = Path(str(value.get("optix_include_path"))).resolve(strict=True)
    cuda_include = Path(str(value.get("cuda_include_path"))).resolve(strict=True)
    if not optix_include.is_dir() or not cuda_include.is_dir():
        raise RuntimeError("Goal5848 device artifact include root differs")
    optix_identity = value.get("optix_headers_identity")
    if (
        not isinstance(optix_identity, Mapping)
        or optix_identity.get("clean") is not True
        or _git_identity(Path(str(optix_identity["path"]))) != optix_identity
        or not optix_include.is_relative_to(
            Path(str(optix_identity["path"])).resolve(strict=True)
        )
    ):
        raise RuntimeError("Goal5848 OptiX header source identity differs")
    optix_text = (optix_include / "optix.h").read_text(encoding="utf-8")
    optix_match = re.search(
        r"(?m)^\s*#\s*define\s+OPTIX_VERSION\s+([0-9]+)\s*$",
        optix_text,
    )
    if (
        optix_match is None
        or int(optix_match.group(1)) != _optix_sdk_number(expected_optix_sdk)
    ):
        raise RuntimeError("Goal5848 OptiX header/API binding differs")

    python = value.get("python")
    if not isinstance(python, Mapping) or set(python) != {
        "invocation_path",
        "path",
        "bytes",
        "sha256",
    }:
        raise RuntimeError("Goal5848 device artifact Python identity differs")
    observed_python = _file_identity(Path(str(python["invocation_path"])).resolve())
    if observed_python != {
        "path": python["path"],
        "bytes": python["bytes"],
        "sha256": python["sha256"],
    }:
        raise RuntimeError("Goal5848 device artifact Python bytes differ")

    compiler_receipts = value.get("compiler_receipts")
    processes = value.get("compiler_processes")
    if (
        not isinstance(compiler_receipts, Mapping)
        or set(compiler_receipts) != {"ptx", "compaction_cubin"}
        or not isinstance(processes, Mapping)
        or set(processes) != {"ptx", "compaction_cubin"}
    ):
        raise RuntimeError("Goal5848 device compiler evidence set differs")
    for label, mode, source_label, output_label in (
        ("ptx", "ptx", "device_source", "precompiled_ptx"),
        (
            "compaction_cubin",
            "cubin",
            "compaction_source",
            "compaction_cubin",
        ),
    ):
        child = compiler_receipts[label]
        _validate_child(
            child,
            mode=mode,
            source=sources[source_label],
            product=outputs[output_label],
            compute_capability=compute_capability,
            optix_include=optix_include,
            cuda_include=cuda_include,
            builder_pid=int(value["builder_pid"]),
            expected_cwd=repository,
        )
        process = processes[label]
        if not isinstance(process, Mapping):
            raise TypeError("Goal5848 compiler process row differs")
        receipt_file = process.get("child_receipt_file")
        if not isinstance(receipt_file, Mapping):
            raise TypeError("Goal5848 child receipt file identity differs")
        child_path = Path(str(receipt_file["path"]))
        child_file_value = strict_json_loads(
            child_path.read_text(encoding="utf-8"),
            label=f"Goal5848 device child {label}",
        )
        if child_file_value != child:
            raise RuntimeError("Goal5848 embedded/file child receipt differs")
        _validate_process(
            process,
            child=child,
            receipt_file=receipt_file,
            python_invocation_path=str(python["invocation_path"]),
        )
    if compiler_receipts["ptx"]["loaded_nvrtc"] != compiler_receipts[
        "compaction_cubin"
    ]["loaded_nvrtc"]:
        raise RuntimeError("Goal5848 device products used different NVRTC")

    return dict(value)


def load_device_artifact_receipt(
    path: Path,
    **arguments: object,
) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError("Goal5848 device build receipt rejects symlink")
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 device artifact receipt",
    )
    return validate_device_artifact_receipt(value, **arguments)


__all__ = [
    "COMPACTION_SOURCE_RELATIVE",
    "COMPILER_CHILD_RELATIVE",
    "DEVICE_ARTIFACT_RECEIPT_SCHEMA",
    "DEVICE_ARTIFACT_RECEIPT_STATUS",
    "DEVICE_SOURCE_RELATIVE",
    "load_device_artifact_receipt",
    "validate_device_artifact_receipt",
]
