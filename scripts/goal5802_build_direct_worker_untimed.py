#!/usr/bin/env python3
"""Build and bind the exact Goal5802 Direct comparative worker, untimed."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

from experiments.goal5802_premeasurement.build_cold_worker import _recipe_argv
from experiments.goal5802_premeasurement.direct_source_audit import (
    audit_direct_source,
)
from experiments.goal5802_premeasurement.runtime_manifest import (
    digest, sha256_file, tree_identity,
)


_NVRTC_IDENTITY_KEYS = {
    "schema", "status", "discovery", "loaded_library_path",
    "loaded_library_bytes", "loaded_library_sha256",
    "loaded_builtins_path", "loaded_builtins_bytes",
    "loaded_builtins_sha256", "nvrtc_version", "nvrtc_compile_kat",
    "clock_read_count", "formal_worker_count",
    "registered_performance_timing_count", "gpu_kernel_launch_count",
}
_NVRTC_COMPILE_KAT_KEYS = {
    "source_utf8", "source_sha256", "compile_options", "product_bytes",
    "product_sha256", "compile_success", "program_destroyed",
}
_NVRTC_COMPILE_SOURCE = (
    'extern "C" __global__ void goal5802_nvrtc_identity_probe() {}\n')
_NVRTC_DISCOVERY = (
    "MINIMAL_NVRTC_COMPILE_THEN_DLADDR_NVRTCVERSION_AND_"
    "PROC_SELF_MAPS_UNIQUE_BUILTINS_REALPATH_OPEN_NOFOLLOW_FSTAT")
_DIRECT_BUILD_RECEIPT_SCHEMA = (
    "rtdl.goal5802.direct_worker_untimed_build_receipt.v2")


def _plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_direct_recipe_linkage(recipe: object) -> dict[str, object]:
    if not isinstance(recipe, dict):
        raise RuntimeError("Direct build recipe root is not an object")
    template = recipe.get("argv_template")
    if not isinstance(template, list) or not all(
            isinstance(item, str) for item in template):
        raise RuntimeError("Direct build recipe argv template is invalid")
    counts = {flag: template.count(flag) for flag in ("-lnvrtc", "-ldl")}
    if counts != {"-lnvrtc": 1, "-ldl": 1}:
        raise RuntimeError(
            f"Direct build recipe loader linkage differs: {counts}")
    if template.index("-lnvrtc") >= template.index("-ldl") \
            or template.index("-ldl") >= template.index("-o"):
        raise RuntimeError(
            "Direct NVRTC/libdl linkage ordering is not explicit")
    return {
        "schema": "rtdl.goal5802.direct_nvrtc_loader_linkage.v1",
        "nvrtc_link_flag": "-lnvrtc",
        "dl_link_flag": "-ldl",
        "nvrtc_link_flag_count": 1,
        "dl_link_flag_count": 1,
        "both_before_output_flag": True,
    }


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 \
        and all(character in "0123456789abcdef" for character in value)


def _rehash_loaded_regular_file(
        value: dict[str, object], *, prefix: str,
        basename_prefix: str) -> tuple[int, int]:
    """Rehash one canonical regular loaded DSO through a no-follow fd."""

    path_text = value.get(f"{prefix}_path")
    if not isinstance(path_text, str) or not path_text:
        raise RuntimeError(f"Direct {prefix} identity path is absent")
    path = Path(path_text)
    if not path.is_absolute():
        raise RuntimeError(f"Direct {prefix} identity path is not absolute")
    if path.name != basename_prefix \
            and not path.name.startswith(basename_prefix + "."):
        raise RuntimeError(f"Direct {prefix} identity basename differs")
    try:
        before = path.lstat()
    except OSError as error:
        raise RuntimeError(
            f"Direct {prefix} identity path is unreadable") from error
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise RuntimeError(
            f"Direct {prefix} identity is not a canonical regular file")
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise RuntimeError(
            f"Direct {prefix} identity cannot be resolved") from error
    if os.path.normcase(str(resolved)) != os.path.normcase(str(path)):
        raise RuntimeError(
            f"Direct {prefix} identity path is not canonical")

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) \
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise RuntimeError(
            f"Direct {prefix} identity file cannot be opened") from error
    try:
        opened_before = os.fstat(descriptor)
        if not stat.S_ISREG(opened_before.st_mode) \
                or (opened_before.st_dev, opened_before.st_ino,
                    opened_before.st_size) != (
                        before.st_dev, before.st_ino, before.st_size):
            raise RuntimeError(
                f"Direct {prefix} path/open file identities differ")
        observed_hash = hashlib.sha256()
        observed_bytes = 0
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            observed_hash.update(block)
            observed_bytes += len(block)
        opened_after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    try:
        after = path.lstat()
    except OSError as error:
        raise RuntimeError(
            f"Direct {prefix} identity path vanished") from error
    stable_identity = (opened_before.st_dev, opened_before.st_ino,
                       opened_before.st_size)
    if (opened_after.st_dev, opened_after.st_ino, opened_after.st_size) \
            != stable_identity \
            or (after.st_dev, after.st_ino, after.st_size) != stable_identity \
            or stat.S_ISLNK(after.st_mode) or not stat.S_ISREG(after.st_mode):
        raise RuntimeError(
            f"Direct {prefix} identity changed during independent rehash")
    declared_bytes = value.get(f"{prefix}_bytes")
    declared_sha256 = value.get(f"{prefix}_sha256")
    if not _plain_int(declared_bytes) or declared_bytes <= 0 \
            or declared_bytes != observed_bytes \
            or not _valid_sha256(declared_sha256) \
            or declared_sha256 != observed_hash.hexdigest():
        raise RuntimeError(
            f"Direct {prefix} exact-byte identity differs")
    return before.st_dev, before.st_ino


def _validate_nvrtc_identity_document(value: object) -> dict[str, object]:
    """Rehash both DSOs and validate the no-GPU compile-before-maps KAT."""

    if not isinstance(value, dict) or set(value) != _NVRTC_IDENTITY_KEYS:
        raise RuntimeError("Direct loaded-NVRTC identity schema keys differ")
    if value.get("schema") \
            != "rtdl.goal5802.direct_loaded_nvrtc_identity.v2" \
            or value.get("status") != "PASS__UNTIMED_NO_GPU" \
            or value.get("discovery") != _NVRTC_DISCOVERY \
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                       "clock_read_count",
                       "registered_performance_timing_count",
                       "gpu_kernel_launch_count", "formal_worker_count")):
        raise RuntimeError("Direct loaded-NVRTC identity constants differ")

    library_identity = _rehash_loaded_regular_file(
        value, prefix="loaded_library", basename_prefix="libnvrtc.so")
    builtins_identity = _rehash_loaded_regular_file(
        value, prefix="loaded_builtins",
        basename_prefix="libnvrtc-builtins.so")
    if library_identity == builtins_identity:
        raise RuntimeError("Direct NVRTC and builtins identities alias")

    version = value.get("nvrtc_version")
    if not isinstance(version, dict) or set(version) != {"major", "minor"} \
            or not _plain_int(version.get("major")) \
            or not _plain_int(version.get("minor")) \
            or version["major"] <= 0 or version["minor"] < 0:
        raise RuntimeError("Direct loaded-NVRTC version is absent or invalid")

    compile_kat = value.get("nvrtc_compile_kat")
    expected_source_sha256 = hashlib.sha256(
        _NVRTC_COMPILE_SOURCE.encode("utf-8")).hexdigest()
    if not isinstance(compile_kat, dict) \
            or set(compile_kat) != _NVRTC_COMPILE_KAT_KEYS \
            or compile_kat.get("source_utf8") != _NVRTC_COMPILE_SOURCE \
            or compile_kat.get("source_sha256") != expected_source_sha256 \
            or compile_kat.get("compile_options") != ["--std=c++11"] \
            or not _plain_int(compile_kat.get("product_bytes")) \
            or compile_kat["product_bytes"] <= 0 \
            or not _valid_sha256(compile_kat.get("product_sha256")) \
            or compile_kat.get("compile_success") is not True \
            or compile_kat.get("program_destroyed") is not True:
        raise RuntimeError("Direct minimal NVRTC compile KAT differs")
    return dict(value)


def _parse_nvrtc_identity_stdout(stdout: bytes) -> dict[str, object]:
    """Accept exactly one deterministic UTF-8 JSON line, then validate it."""

    try:
        decoded = stdout.decode("utf-8")
        value = json.loads(decoded)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "Direct loaded-NVRTC identity is not UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise RuntimeError("Direct loaded-NVRTC identity root is not an object")
    exact = json.dumps(
        value, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
    if stdout != exact:
        raise RuntimeError(
            "Direct loaded-NVRTC identity stdout is not one exact JSON line")
    return _validate_nvrtc_identity_document(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--cxx", type=Path, required=True)
    parser.add_argument("--direct-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output, args.receipt):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    cxx = args.cxx.absolute()
    direct_source = args.direct_source.resolve(strict=True)
    recipe_path = args.recipe.resolve(strict=True)
    optix_include = args.optix_include.resolve(strict=True)
    cuda_include = args.cuda_include.resolve(strict=True)
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    loader_linkage = _validate_direct_recipe_linkage(recipe)
    direct_source_audit = audit_direct_source(direct_source)
    runtime = {
        "files": {
            "cxx_compiler": {"path": str(cxx)},
            "direct_scalar_source": {"path": str(direct_source)},
        },
        "directories": {
            "optix_include": {"path": str(optix_include)},
            "cuda_include": {"path": str(cuda_include)},
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = _recipe_argv(recipe, runtime=runtime, output_binary=args.output)
    completed = subprocess.run(command, capture_output=True, check=False)
    if completed.returncode != 0 or not args.output.is_file() \
            or args.output.is_symlink():
        raise RuntimeError({
            "direct_compile_exit": completed.returncode,
            "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        })
    kat_command = [str(args.output.resolve(strict=True)), "--local-sha256-kat"]
    kat = subprocess.run(kat_command, capture_output=True, check=False)
    try:
        kat_document = json.loads(kat.stdout)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("Direct retained-byte SHA-256 KAT is not JSON") from error
    expected_kat = {
        "schema": "rtdl.goal5802.direct_sha256_kat.v1",
        "status": "PASS__UNTIMED_NO_GPU",
        "input_utf8": "abc",
        "sha256": (
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
    }
    if kat.returncode != 0 or kat.stderr or kat_document != expected_kat:
        raise RuntimeError({
            "direct_sha256_kat_exit": kat.returncode,
            "stdout_sha256": hashlib.sha256(kat.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(kat.stderr).hexdigest(),
        })
    identity_command = [
        str(args.output.resolve(strict=True)), "--local-nvrtc-identity"]
    identity = subprocess.run(
        identity_command, capture_output=True, check=False)
    if identity.returncode != 0 or identity.stderr:
        raise RuntimeError({
            "direct_loaded_nvrtc_identity_exit": identity.returncode,
            "stdout_sha256": hashlib.sha256(identity.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(identity.stderr).hexdigest(),
        })
    identity_document = _parse_nvrtc_identity_stdout(identity.stdout)
    value: dict[str, object] = {
        "schema": _DIRECT_BUILD_RECEIPT_SCHEMA,
        "status": "PASS__SOURCE_TO_DIRECT_WORKER__UNTIMED",
        "recipe_sha256": sha256_file(recipe_path),
        "cxx_path": str(cxx),
        "cxx_sha256": sha256_file(cxx.resolve(strict=True)),
        "direct_source_sha256": sha256_file(direct_source),
        "direct_source_operation_audit": direct_source_audit,
        "optix_include_tree": tree_identity(optix_include),
        "cuda_include_tree": tree_identity(cuda_include),
        "command": command,
        "loader_linkage": loader_linkage,
        "exit_code": completed.returncode,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        "output_bytes": args.output.stat().st_size,
        "output_sha256": sha256_file(args.output),
        "sha256_kat_command": kat_command,
        "sha256_kat_exit_code": kat.returncode,
        "sha256_kat_stdout_sha256": hashlib.sha256(kat.stdout).hexdigest(),
        "sha256_kat_stderr_sha256": hashlib.sha256(kat.stderr).hexdigest(),
        "sha256_kat_document": kat_document,
        "loaded_nvrtc_identity_command": identity_command,
        "loaded_nvrtc_identity_exit_code": identity.returncode,
        "loaded_nvrtc_identity_stdout_sha256": hashlib.sha256(
            identity.stdout).hexdigest(),
        "loaded_nvrtc_identity_stderr_sha256": hashlib.sha256(
            identity.stderr).hexdigest(),
        "loaded_nvrtc_identity_document": identity_document,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
    }
    value["receipt_sha256"] = digest(value)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
