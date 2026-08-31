#!/usr/bin/env python3
"""Create-only exact target runtime manifest for Goal5802."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.goal5802_premeasurement.runtime_manifest import (
    HOST_RUNTIME_DISTRIBUTIONS,
    HOST_RUNTIME_MODULES,
    PYOPTIX_SOURCE_COMMIT,
    PYOPTIX_SOURCE_TREE,
    SCHEMA,
    digest,
    rtdsl_package_identity,
    sha256_file,
    tree_identity,
    validate_direct_operation_kat,
    direct_nvrtc_identity_stdout_bytes,
    validate_direct_nvrtc_identity_document,
    validate_pyoptix_operation_kat,
    validate_rtdl_operation_kat,
    validate_host_runtime_provenance,
    validate_runtime_manifest,
    validate_target_observation_receipt,
)
from experiments.goal5802_premeasurement.build_cold_worker import _recipe_argv
from scripts.goal5802_build_header_projection_untimed import (
    validate_header_projection,
)
from scripts.goal5802_prepare_matched_ptx_untimed import (
    FINAL_PROJECTION_CLAIM,
    validate_matched_ptx_prepare_receipt,
)
from scripts.goal5802_materialize_pyoptix_build_provenance import (
    EXTENSION_BYTES as PYOPTIX_EXTENSION_BYTES,
    EXTENSION_MEMBER as PYOPTIX_EXTENSION_MEMBER,
    EXTENSION_SHA256 as PYOPTIX_EXTENSION_SHA256,
    validate_materialization_receipt,
)
from scripts.goal5802_clean_install_pyoptix_offline import (
    verify as verify_offline_pyoptix_install,
)
from scripts.goal5802_build_combined_runtime_untimed import (
    verify_run as verify_combined_runtime,
)


FILE_ROLES = (
    "clean_python", "direct_scalar_worker", "direct_scalar_source",
    "direct_build_recipe", "direct_worker_build_receipt",
    "direct_operation_kat", "rtdl_operation_kat",
    "device_source", "compaction_source", "matched_ptx",
    "compaction_cubin", "matched_ptx_prepare_receipt",
    "callback_proof", "nvrtc_library", "nvrtc_builtins",
    "cxx_compiler", "nvcc", "nvidia_smi", "target_observation_receipt",
    "rtdl_wheel", "pyoptix_wheel", "pyoptix_wheel_build_receipt",
    "pyoptix_clean_install_receipt", "goal5800_v7_source",
    "pyoptix_operation_kat", "host_runtime_provenance",
    "header_projection_receipt", "combined_runtime_receipt",
    "pyoptix_initializer",
    "pyoptix_extension", "rtdsl_init", "rtdlexe_module", "native_library",
    "trust_root", "trust_head", "trust_package", "relation_artifact",
    "relation_authority", "triangle_artifact", "triangle_authority",
)
DIRECTORY_ROLES = (
    "optix_include", "cuda_include", "optix_sdk", "header_projection")
EXECUTABLE_ROLES_ALLOWING_EXACT_SYMLINK = (
    "clean_python", "cxx_compiler", "nvcc", "nvidia_smi",
)
OFFLINE_PYOPTIX_VALIDATION_BOUNDARY = {
    "installed_measured_runtime_distribution_import_count": 0,
    "pyoptix_import_count": 0,
    "cupy_import_count": 0,
    "device_query_count": 0,
    "gpu_kernel_launch_count": 0,
    "registered_measurement_clock_read_count": 0,
    "formal_worker_count": 0,
    "registered_performance_timing_count": 0,
    "execution_authority_consumed": False,
    "self_hash_is_execution_authority": False,
    "caller_must_bind_exact_plan_before_run": True,
}
OFFLINE_PYOPTIX_PIP_POLICY = {
    "python_interpreter_executes_pip_module_without_script_or_shebang": True,
    "pip_loaded_via_runpy_with_site_disabled": True,
    "safe_path_enabled_for_every_build_command": True,
    "isolated": True,
    "no_index": True,
    "no_deps": True,
    "no_cache_dir": True,
    "no_compile": True,
    "exact_venv_site_packages_target": True,
    "prefix_mode_allowed": False,
    "implicit_download_allowed": False,
    "pip_script_or_shebang_invocation_allowed": False,
}


def _validate_offline_pyoptix_manifest_projection(
        value: object) -> dict[str, object]:
    """Consume the current Goal5802 receipt at its versioned field layer.

    The producer verifier has already rehashed the complete install.  This
    consumer-side projection deliberately repeats the load-bearing policy and
    zero-execution boundary so a future schema move cannot silently become a
    permissive ``dict.get`` or an always-failing legacy lookup.
    """
    if not isinstance(value, dict) \
            or value.get("schema") \
            != "rtdl.goal5802.offline_pyoptix_clean_install_receipt.v1" \
            or value.get("status") \
            != "PASS__OFFLINE_CREATE_ONLY_PYOPTIX_RUNTIME_INSTALLED" \
            or value.get("create_only") is not True:
        raise RuntimeError(
            "offline PyOptiX manifest-consumer projection differs")
    boundary = value.get("validation_boundary")
    zero_keys = (
        "installed_measured_runtime_distribution_import_count",
        "pyoptix_import_count", "cupy_import_count", "device_query_count",
        "gpu_kernel_launch_count", "registered_measurement_clock_read_count",
        "formal_worker_count", "registered_performance_timing_count",
    )
    if not isinstance(boundary, dict) \
            or set(boundary) != set(OFFLINE_PYOPTIX_VALIDATION_BOUNDARY) \
            or any(type(boundary.get(key)) is not int or boundary[key] != 0
                   for key in zero_keys) \
            or boundary.get("execution_authority_consumed") is not False \
            or boundary.get("self_hash_is_execution_authority") is not False \
            or boundary.get("caller_must_bind_exact_plan_before_run") is not True:
        raise RuntimeError(
            "offline PyOptiX manifest-consumer execution boundary differs")
    policy = value.get("pip_policy")
    if not isinstance(policy, dict) or set(policy) != set(
            OFFLINE_PYOPTIX_PIP_POLICY) \
            or any(type(policy.get(key)) is not type(expected)
                   or policy[key] != expected
                   for key, expected in OFFLINE_PYOPTIX_PIP_POLICY.items()):
        raise RuntimeError(
            "offline PyOptiX manifest-consumer pip policy differs")
    command = value.get("install_command")
    required_flags = (
        "--no-index", "--no-deps", "--no-cache-dir", "--no-compile",
        "--disable-pip-version-check", "--target",
    )
    if not isinstance(command, list) \
            or any(command.count(flag) != 1 for flag in required_flags) \
            or "--prefix" in command:
        raise RuntimeError(
            "offline PyOptiX manifest-consumer install policy differs")
    return value


def _file_record(path: Path, *, allow_symlink: bool) -> dict[str, object]:
    original = path.absolute()
    if original.is_symlink():
        if not allow_symlink:
            raise RuntimeError(f"runtime input is a symlink: {original}")
        resolved = original.resolve(strict=True)
        if not resolved.is_file():
            raise RuntimeError(f"runtime executable symlink target invalid: {original}")
        return {
            "path": str(original),
            "path_kind": "EXACT_SYMLINK_TO_REGULAR_FILE",
            "symlink_target": str(original.readlink()),
            "resolved_path": str(resolved),
            "bytes": resolved.stat().st_size,
            "sha256": sha256_file(resolved),
        }
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise RuntimeError(f"runtime input is not a regular file: {resolved}")
    return {
        "path": str(resolved), "path_kind": "REGULAR_FILE",
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def _directory_record(path: Path) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError(f"runtime directory is a symlink: {path}")
    resolved = path.resolve(strict=True)
    return {"path": str(resolved), **tree_identity(resolved)}


def build_manifest(args: argparse.Namespace) -> dict[str, object]:
    files = {
        role: _file_record(
            getattr(args, role),
            allow_symlink=role in EXECUTABLE_ROLES_ALLOWING_EXACT_SYMLINK)
        for role in FILE_ROLES}
    directories = {
        role: _directory_record(getattr(args, role)) for role in DIRECTORY_ROLES}
    rtdsl_package_root = Path(str(files["rtdsl_init"]["path"])).parent
    package_identity = rtdsl_package_identity(rtdsl_package_root)
    directories["rtdsl_package"] = {
        "path": str(rtdsl_package_root), **package_identity}
    combined_receipt_path = Path(files["combined_runtime_receipt"]["path"])
    if combined_receipt_path.name != "combined_runtime_receipt.json":
        raise RuntimeError("combined-runtime receipt filename differs")
    combined_root = combined_receipt_path.parent
    combined_runtime = verify_combined_runtime(combined_root)
    combined_python = combined_root / "venv/bin/python"
    combined_site = combined_root / "venv/lib/python3.12/site-packages"
    combined_path_projection = {
        "root_path": str(combined_root),
        "clean_python_relative": "venv/bin/python",
        "site_packages_relative": "venv/lib/python3.12/site-packages",
        "rtdsl_package_relative": "venv/lib/python3.12/site-packages/rtdsl",
        "pyoptix_initializer_relative": (
            "venv/lib/python3.12/site-packages/optix/__init__.py"),
        "pyoptix_extension_relative": (
            "venv/lib/python3.12/site-packages/" + PYOPTIX_EXTENSION_MEMBER),
        "all_runtime_paths_inside_receipted_combined_root": True,
    }
    if Path(files["clean_python"]["path"]) != combined_python \
            or rtdsl_package_root != combined_site / "rtdsl" \
            or Path(files["pyoptix_initializer"]["path"]) \
            != combined_site / "optix/__init__.py" \
            or Path(files["pyoptix_extension"]["path"]) \
            != combined_site / PYOPTIX_EXTENSION_MEMBER:
        raise RuntimeError(
            "executed Python/module paths are outside receipted combined runtime")

    header_projection = json.loads(Path(
        files["header_projection_receipt"]["path"]).read_text(
            encoding="utf-8"))
    if not isinstance(header_projection, dict):
        raise RuntimeError("header projection receipt is not an object")
    validate_header_projection(
        header_projection, Path(directories["header_projection"]["path"]))
    if header_projection.get("projection_file_count") \
            != directories["header_projection"]["file_count"] \
            or header_projection.get("projection_payload_bytes") \
            != directories["header_projection"]["payload_bytes"] \
            or header_projection.get("projection_tree_sha256") \
            != directories["header_projection"]["tree_sha256"]:
        raise RuntimeError("header projection receipt/tree binding differs")
    projection_root = Path(directories["header_projection"]["path"])
    if any(not Path(directories[role]["path"]).is_relative_to(projection_root)
           for role in ("optix_include", "cuda_include")):
        raise RuntimeError("compiler include root escapes header projection")
    command_authority = header_projection.get("command_authority")
    if not isinstance(command_authority, dict):
        raise RuntimeError("header projection command authority is absent")
    authority_tools = command_authority.get("tools")
    authority_sources = command_authority.get("sources")
    if not isinstance(authority_tools, dict) \
            or not isinstance(authority_sources, dict):
        raise RuntimeError("header projection command inputs are absent")

    def same_manifest_file(authority: object, manifest_role: str) -> bool:
        if not isinstance(authority, dict):
            return False
        target = files[manifest_role]
        target_resolved = target.get("resolved_path", target["path"])
        return authority.get("resolved_path") == target_resolved \
            and authority.get("bytes") == target["bytes"] \
            and authority.get("sha256") == target["sha256"]

    if not same_manifest_file(authority_tools.get("nvcc"), "nvcc") \
            or not same_manifest_file(
                authority_tools.get("cxx"), "cxx_compiler") \
            or not same_manifest_file(authority_sources.get(
                "matched_device_source"), "device_source") \
            or not same_manifest_file(authority_sources.get(
                "relation_compaction_source"), "compaction_source") \
            or not same_manifest_file(authority_sources.get(
                "direct_source"), "direct_scalar_source"):
        raise RuntimeError(
            "header projection tool/source authority differs from manifest")

    def sealed_receipt(role: str, schema: str) -> dict[str, object]:
        receipt = json.loads(Path(files[role]["path"]).read_text(encoding="utf-8"))
        if not isinstance(receipt, dict) or receipt.get("schema") != schema:
            raise RuntimeError(f"runtime build receipt schema differs: {role}")
        unsigned = dict(receipt)
        observed = unsigned.pop("receipt_sha256", None)
        if observed != digest(unsigned):
            raise RuntimeError(f"runtime build receipt self-digest differs: {role}")
        return receipt

    direct_receipt = sealed_receipt(
        "direct_worker_build_receipt",
        "rtdl.goal5802.direct_worker_untimed_build_receipt.v2")
    direct_recipe = json.loads(
        Path(files["direct_build_recipe"]["path"]).read_text(encoding="utf-8"))
    expected_sha256_kat_stdout = (
        b'{"schema":"rtdl.goal5802.direct_sha256_kat.v1",'
        b'"status":"PASS__UNTIMED_NO_GPU","input_utf8":"abc",'
        b'"sha256":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",'
        b'"registered_performance_timing_count":0,"gpu_kernel_launch_count":0}\n')
    expected_direct_command = _recipe_argv(
        direct_recipe,
        runtime={
            "files": {
                "cxx_compiler": {"path": files["cxx_compiler"]["path"]},
                "direct_scalar_source": {
                    "path": files["direct_scalar_source"]["path"]},
            },
            "directories": {
                "optix_include": {"path": directories["optix_include"]["path"]},
                "cuda_include": {"path": directories["cuda_include"]["path"]},
            },
        },
        output_binary=Path(files["direct_scalar_worker"]["path"]),
    )
    if set(direct_receipt) != {
            "schema", "status", "recipe_sha256", "cxx_path", "cxx_sha256",
            "direct_source_sha256", "optix_include_tree", "cuda_include_tree",
            "direct_source_operation_audit", "command", "loader_linkage",
            "exit_code", "stdout_sha256", "stderr_sha256",
            "output_bytes", "output_sha256",
            "sha256_kat_command", "sha256_kat_exit_code",
            "sha256_kat_stdout_sha256", "sha256_kat_stderr_sha256",
            "sha256_kat_document",
            "loaded_nvrtc_identity_command",
            "loaded_nvrtc_identity_exit_code",
            "loaded_nvrtc_identity_stdout_sha256",
            "loaded_nvrtc_identity_stderr_sha256",
            "loaded_nvrtc_identity_document",
            "registered_performance_timing_count", "gpu_kernel_launch_count",
            "receipt_sha256"} \
            or direct_receipt.get("status") \
            != "PASS__SOURCE_TO_DIRECT_WORKER__UNTIMED" \
            or type(direct_receipt.get(
                "registered_performance_timing_count")) is not int \
            or direct_receipt["registered_performance_timing_count"] != 0 \
            or type(direct_receipt.get("gpu_kernel_launch_count")) is not int \
            or direct_receipt["gpu_kernel_launch_count"] != 0 \
            or direct_receipt.get("recipe_sha256") \
            != files["direct_build_recipe"]["sha256"] \
            or direct_receipt.get("direct_source_sha256") \
            != files["direct_scalar_source"]["sha256"] \
            or direct_receipt.get("cxx_sha256") != files["cxx_compiler"]["sha256"] \
            or direct_receipt.get("cxx_path") != files["cxx_compiler"]["path"] \
            or direct_receipt.get("command") != expected_direct_command \
            or direct_receipt.get("loader_linkage") != {
                "schema": "rtdl.goal5802.direct_nvrtc_loader_linkage.v1",
                "nvrtc_link_flag": "-lnvrtc", "dl_link_flag": "-ldl",
                "nvrtc_link_flag_count": 1, "dl_link_flag_count": 1,
                "both_before_output_flag": True,
            } \
            or not isinstance(
                direct_receipt.get("direct_source_operation_audit"), dict) \
            or direct_receipt["direct_source_operation_audit"].get(
                "source_sha256") != files["direct_scalar_source"]["sha256"] \
            or direct_receipt.get("exit_code") != 0 \
            or any(not isinstance(direct_receipt.get(key), str)
                   or len(direct_receipt[key]) != 64
                   or any(ch not in "0123456789abcdef"
                          for ch in direct_receipt[key])
                   for key in ("stdout_sha256", "stderr_sha256")) \
            or direct_receipt.get("optix_include_tree") \
            != {key: directories["optix_include"][key]
                for key in ("file_count", "payload_bytes", "tree_sha256")} \
            or direct_receipt.get("cuda_include_tree") \
            != {key: directories["cuda_include"][key]
                for key in ("file_count", "payload_bytes", "tree_sha256")} \
            or direct_receipt.get("output_bytes") \
            != files["direct_scalar_worker"]["bytes"] \
            or direct_receipt.get("output_sha256") \
            != files["direct_scalar_worker"]["sha256"] \
            or direct_receipt.get("sha256_kat_command") != [
                files["direct_scalar_worker"]["path"], "--local-sha256-kat"] \
            or direct_receipt.get("sha256_kat_exit_code") != 0 \
            or direct_receipt.get("sha256_kat_stdout_sha256") \
            != hashlib.sha256(expected_sha256_kat_stdout).hexdigest() \
            or direct_receipt.get("sha256_kat_stderr_sha256") \
            != hashlib.sha256(b"").hexdigest() \
            or direct_receipt.get("sha256_kat_document") != {
                "schema": "rtdl.goal5802.direct_sha256_kat.v1",
                "status": "PASS__UNTIMED_NO_GPU",
                "input_utf8": "abc",
                "sha256": (
                    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
                "registered_performance_timing_count": 0,
                "gpu_kernel_launch_count": 0,
            } \
            or direct_receipt.get("loaded_nvrtc_identity_command") != [
                files["direct_scalar_worker"]["path"],
                "--local-nvrtc-identity"] \
            or direct_receipt.get("loaded_nvrtc_identity_exit_code") != 0 \
            or direct_receipt.get(
                "loaded_nvrtc_identity_stderr_sha256") \
            != hashlib.sha256(b"").hexdigest() \
            or not isinstance(direct_receipt.get(
                "loaded_nvrtc_identity_document"), dict):
        raise RuntimeError("Direct worker build provenance differs")
    direct_operation_kat = sealed_receipt(
        "direct_operation_kat",
        "rtdl.goal5802.direct_operation_guard_untimed_kat.v1")
    validate_direct_operation_kat(direct_operation_kat, files)
    rtdl_operation_kat = sealed_receipt(
        "rtdl_operation_kat",
        "rtdl.goal5802.rtdl_operation_guard_untimed_kat.v1")
    validate_rtdl_operation_kat(
        rtdl_operation_kat, files, {
            "relation": args.relation_deployment_id,
            "triangle": args.triangle_deployment_id,
        })

    ptx_receipt = sealed_receipt(
        "matched_ptx_prepare_receipt",
        "rtdl.goal5802.matched_ptx_untimed_prepare.v3")
    validate_matched_ptx_prepare_receipt(
        ptx_receipt, projection_receipt=header_projection,
        projection_root=projection_root)
    authority_roots = command_authority["original_sdk_roots"]
    mapping_by_role = {
        row["role"]: row for row in header_projection["root_mappings"]}
    if authority_roots["optix_include"]["resolved_path"] \
            != ptx_receipt.get("original_optix_include_path") \
            or authority_roots["cuda_include"]["resolved_path"] \
            != ptx_receipt.get("original_cuda_include_path") \
            or mapping_by_role["optix_include"]["projected_root"] \
            != directories["optix_include"]["path"] \
            or mapping_by_role["cuda_include"]["projected_root"] \
            != directories["cuda_include"]["path"]:
        raise RuntimeError(
            "header projection original/projected roots differ from replay")
    nvrtc_library = ptx_receipt.get("nvrtc_library")
    nvrtc_builtins = ptx_receipt.get("nvrtc_builtins")
    if ptx_receipt.get("status") \
            != "PASS__FRESH_PROCESS_TRACED_UNTIMED_PREPARE" \
            or ptx_receipt.get("projection_claim") != FINAL_PROJECTION_CLAIM \
            or ptx_receipt.get("device_source_sha256") \
            != files["device_source"]["sha256"] \
            or ptx_receipt.get("compaction_source_sha256") \
            != files["compaction_source"]["sha256"] \
            or ptx_receipt.get("optix_include_tree") \
            != {key: directories["optix_include"][key]
                for key in ("file_count", "payload_bytes", "tree_sha256")} \
            or ptx_receipt.get("cuda_include_tree") \
            != {key: directories["cuda_include"][key]
                for key in ("file_count", "payload_bytes", "tree_sha256")} \
            or ptx_receipt.get("header_projection_receipt_sha256") \
            != files["header_projection_receipt"]["sha256"] \
            or ptx_receipt.get("header_projection_tree_sha256") \
            != directories["header_projection"]["tree_sha256"] \
            or ptx_receipt.get("original_ptx_sha256") \
            != files["matched_ptx"]["sha256"] \
            or ptx_receipt.get(
                "projected_ptx_byte_identical_to_original") is not True \
            or ptx_receipt.get(
                "nvcc_only_ptx_byte_identical_to_original") is not True \
            or ptx_receipt.get(
                "union_ptx_byte_identical_to_original") is not True \
            or not isinstance(nvrtc_library, dict) \
            or nvrtc_library != {
                "path": files["nvrtc_library"]["path"],
                "bytes": files["nvrtc_library"]["bytes"],
                "sha256": files["nvrtc_library"]["sha256"],
                "canonical_regular_file": True,
                "symlink": False,
                "version": nvrtc_library.get("version"),
            } \
            or not isinstance(nvrtc_builtins, dict) \
            or nvrtc_builtins != {
                "path": files["nvrtc_builtins"]["path"],
                "bytes": files["nvrtc_builtins"]["bytes"],
                "sha256": files["nvrtc_builtins"]["sha256"],
                "canonical_regular_file": True,
                "symlink": False,
            } \
            or not isinstance(nvrtc_library.get("version"), list) \
            or len(nvrtc_library["version"]) != 2 \
            or not all(type(item) is int and item >= 0
                       for item in nvrtc_library["version"]) \
            or ptx_receipt.get("ptx_bytes") != files["matched_ptx"]["bytes"] \
            or ptx_receipt.get("ptx_sha256") != files["matched_ptx"]["sha256"] \
            or ptx_receipt.get("compaction_cubin_bytes") \
            != files["compaction_cubin"]["bytes"] \
            or ptx_receipt.get("compaction_cubin_sha256") \
            != files["compaction_cubin"]["sha256"] \
            or not isinstance(
                ptx_receipt.get("compaction_cubin_architecture"), str) \
            or not ptx_receipt["compaction_cubin_architecture"].startswith("sm_") \
            or not isinstance(ptx_receipt.get("ptx_target"), str) \
            or not isinstance(ptx_receipt.get("ptx_compile_options"), list) \
            or not isinstance(
                ptx_receipt.get("compaction_compile_options"), list):
        raise RuntimeError("matched PTX build provenance differs")
    direct_nvrtc = direct_receipt["loaded_nvrtc_identity_document"]
    validate_direct_nvrtc_identity_document(direct_nvrtc, files)
    if direct_receipt.get("loaded_nvrtc_identity_stdout_sha256") \
            != hashlib.sha256(
                direct_nvrtc_identity_stdout_bytes(direct_nvrtc)).hexdigest():
        raise RuntimeError("Direct NVRTC identity stdout digest differs")
    if direct_nvrtc.get("nvrtc_version") != {
            "major": nvrtc_library["version"][0],
            "minor": nvrtc_library["version"][1],
    }:
        raise RuntimeError(
            "Direct and Python arms loaded different NVRTC versions")

    wheel_build = validate_materialization_receipt(
        Path(files["pyoptix_wheel_build_receipt"]["path"]))
    clean_receipt_path = Path(
        files["pyoptix_clean_install_receipt"]["path"])
    if clean_receipt_path.name != "offline_pyoptix_clean_install_receipt.json":
        raise RuntimeError("offline PyOptiX clean receipt filename differs")
    clean_install = verify_offline_pyoptix_install(clean_receipt_path.parent)
    _validate_offline_pyoptix_manifest_projection(clean_install)
    wheel_headers_root = Path(wheel_build["materialized_headers"]["path"])
    original_optix_include = Path(command_authority[
        "original_sdk_roots"]["optix_include"]["resolved_path"])
    projected_optix_include = Path(
        mapping_by_role["optix_include"]["projected_root"])
    wheel_path = Path(files["pyoptix_wheel"]["path"])
    try:
        with zipfile.ZipFile(wheel_path) as archive:
            wheel_initializer = archive.read("optix/__init__.py")
            wheel_extension = archive.read(PYOPTIX_EXTENSION_MEMBER)
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        raise RuntimeError("exact PyOptiX wheel members are unreadable") from error
    if wheel_build["pyoptix_wheel"]["sha256"] \
            != files["pyoptix_wheel"]["sha256"] \
            or wheel_build["pyoptix_wheel"]["bytes"] \
            != files["pyoptix_wheel"]["bytes"] \
            or len(wheel_extension) != PYOPTIX_EXTENSION_BYTES \
            or hashlib.sha256(wheel_extension).hexdigest() \
            != PYOPTIX_EXTENSION_SHA256 \
            or len(wheel_extension) != files["pyoptix_extension"]["bytes"] \
            or hashlib.sha256(wheel_extension).hexdigest() \
            != files["pyoptix_extension"]["sha256"] \
            or len(wheel_initializer) != files["pyoptix_initializer"]["bytes"] \
            or hashlib.sha256(wheel_initializer).hexdigest() \
            != files["pyoptix_initializer"]["sha256"] \
            or wheel_headers_root.resolve(strict=True) \
            != Path(directories["optix_sdk"]["path"]).resolve(strict=True) \
            or (wheel_headers_root / "include").resolve(strict=True) \
            != original_optix_include.resolve(strict=True) \
            or projected_optix_include.resolve(strict=True) \
            != Path(directories["optix_include"]["path"]).resolve(strict=True) \
            or original_optix_include.resolve(strict=True) \
            == projected_optix_include.resolve(strict=True):
        raise RuntimeError("PyOptiX build/install provenance differs")
    operation_kat = sealed_receipt(
        "pyoptix_operation_kat",
        "rtdl.goal5802.pyoptix_operation_guard_untimed_kat.v1")
    # Use the same exact-schema validator as the controller and independent
    # recount.  It requires the post-K+1 8 OptiX + 3 auxiliary = 11 launch
    # envelope, all first/reuse rows, the hostile device-capacity row, and
    # task-specific runtime identities.  The controller subsequently binds
    # its source boundary to the exact frozen source-manifest hash.
    validate_pyoptix_operation_kat(operation_kat, files)
    host_runtime = sealed_receipt(
        "host_runtime_provenance",
        "rtdl.goal5802.host_runtime_provenance.v3")
    if set(host_runtime) != {
            "schema", "status", "python", "distributions",
            "loaded_module_files", "host", "thread_and_visibility_environment",
            "registered_performance_timing_count", "formal_worker_count",
            "receipt_sha256"} \
            or host_runtime.get("status") \
            != "PASS__UNTIMED_EXACT_HOST_RUNTIME_CAPTURE" \
            or host_runtime.get("registered_performance_timing_count") != 0 \
            or host_runtime.get("formal_worker_count") != 0 \
            or not isinstance(host_runtime.get("python"), dict) \
            or not isinstance(host_runtime.get("distributions"), list) \
            or [row.get("name") for row in host_runtime["distributions"]
                if isinstance(row, dict)] \
            != list(HOST_RUNTIME_DISTRIBUTIONS) \
            or set(host_runtime.get("loaded_module_files", {})) \
            != set(HOST_RUNTIME_MODULES) \
            or not isinstance(host_runtime.get("host"), dict) \
            or not isinstance(
                host_runtime.get("thread_and_visibility_environment"), dict):
        raise RuntimeError("host/runtime provenance receipt differs")
    validate_host_runtime_provenance(host_runtime, files)
    observation = json.loads(Path(
        files["target_observation_receipt"]["path"]).read_text(
            encoding="utf-8"))
    if not isinstance(observation, dict):
        raise RuntimeError("target observation receipt schema differs")
    validate_target_observation_receipt(
        observation, files, require_current_loader_environment=True)
    expected_cubin_architecture = (
        "sm_" + str(observation["compute_capability"]).replace(".", ""))
    expected_compute_architecture = (
        "compute_" + str(observation["compute_capability"]).replace(".", ""))
    original_optix = ptx_receipt.get("original_optix_include_path")
    original_cuda = ptx_receipt.get("original_cuda_include_path")
    projection_command_tokens = [
        token for run in header_projection["runs"]
        for token in run["command"]]
    if ptx_receipt["compaction_cubin_architecture"] \
            != expected_cubin_architecture \
            or command_authority.get("compute_capability") \
            != expected_cubin_architecture \
            or ptx_receipt["compute_capability"] \
            != observation["compute_capability"] \
            or ptx_receipt["ptx_target"] != expected_cubin_architecture \
            or ptx_receipt["ptx_compile_options"] != [
                "--std=c++17", "--device-as-default-execution-space",
                "--relocatable-device-code=true",
                f"--gpu-architecture={expected_compute_architecture}",
                f"-I{directories['optix_include']['path']}",
                f"-I{directories['cuda_include']['path']}",
                f"-I{Path(str(directories['cuda_include']['path'])) / 'nv'}",
            ] \
            or not isinstance(original_optix, str) or not original_optix \
            or not isinstance(original_cuda, str) or not original_cuda \
            or f"-I{original_optix}" not in projection_command_tokens \
            or f"-I{original_cuda}" not in projection_command_tokens \
            or f"-I{Path(original_cuda) / 'nv'}" not in projection_command_tokens \
            or ptx_receipt["original_ptx_compile_options"] != [
                "--std=c++17", "--device-as-default-execution-space",
                "--relocatable-device-code=true",
                f"--gpu-architecture={expected_compute_architecture}",
                f"-I{original_optix}", f"-I{original_cuda}",
                f"-I{Path(original_cuda) / 'nv'}",
            ] \
            or ptx_receipt["compaction_compile_options"] != [
                "--std=c++17", "--device-as-default-execution-space",
                f"--gpu-architecture={expected_cubin_architecture}",
            ]:
        raise RuntimeError(
            "matched compiler architecture differs from observed target")

    expected_cc_parts = [
        int(part) for part in str(observation["compute_capability"]).split(".")]
    if len(expected_cc_parts) != 2:
        raise RuntimeError("observed target compute capability is not major.minor")
    artifact_architecture: dict[str, object] = {}
    for prefix in ("relation", "triangle"):
        artifact = json.loads(Path(files[f"{prefix}_artifact"]["path"])
                              .read_text(encoding="utf-8"))
        product = artifact.get("product_projection") \
            if isinstance(artifact, dict) else None
        toolchain = product.get("target_toolchain") \
            if isinstance(product, dict) else None
        ptx_metadata = product.get("ptx_metadata") \
            if isinstance(product, dict) else None
        provider = product.get("provider_key") \
            if isinstance(product, dict) else None
        if not all(isinstance(item, dict)
                   for item in (toolchain, ptx_metadata, provider)) \
                or toolchain.get("compute_capability") != expected_cc_parts \
                or ptx_metadata.get("target") != expected_cubin_architecture \
                or provider.get("target_compute_capability") \
                != expected_cc_parts \
                or provider.get("ptx_target") != expected_cubin_architecture:
            raise RuntimeError(
                f"RTDL {prefix} artifact target differs from measured target")
        artifact_architecture[prefix] = {
            "artifact_sha256": files[f"{prefix}_artifact"]["sha256"],
            "target_toolchain_compute_capability": expected_cc_parts,
            "ptx_metadata_target": expected_cubin_architecture,
            "provider_target_compute_capability": expected_cc_parts,
            "provider_ptx_target": expected_cubin_architecture,
        }
    goal5800_source_sha = files["goal5800_v7_source"]["sha256"]
    value: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PREPARED_UNTIMED__FORMAL_EXECUTION_LOCKED",
        "files": files,
        "directories": directories,
        "deployment_ids": {
            "relation": args.relation_deployment_id,
            "triangle": args.triangle_deployment_id,
        },
        "pyoptix": {
            "distribution_version": "9.1.0",
            "optix_api_version": "9.0.0",
            "source_commit": PYOPTIX_SOURCE_COMMIT,
            "source_tree": PYOPTIX_SOURCE_TREE,
            "goal5800_v7_source_sha256": goal5800_source_sha,
        },
        "target_observation": {
            key: observation[key] for key in (
                "gpu_name", "compute_capability", "driver_version",
                "cuda_driver_version", "cuda_toolkit_version", "optix_version")
        } | {"observation_receipt_sha256": files[
            "target_observation_receipt"]["sha256"]},
        "target_policy": {
            "gpu_model_or_driver_preselection_allowed": False,
            "eligibility": "FIRST_OWNER_PROVIDED_TARGET_PASSING_UNTIMED_GATE",
            "result_conditioned_replacement_allowed": False,
            "driver_or_gpu_failure_disposition": (
                "PRESERVE_FAILED_ROW__NO_REPLACEMENT"),
        },
        "architecture_contract": {
            "compute_capability": observation["compute_capability"],
            "nvrtc_compute_architecture": expected_compute_architecture,
            "ptx_target": expected_cubin_architecture,
            "ptx_target_directive_count": 1,
            "rtdl_artifacts": artifact_architecture,
            "libnvrtc_sha256": files["nvrtc_library"]["sha256"],
            "libnvrtc_builtins_sha256": files[
                "nvrtc_builtins"]["sha256"],
            "libnvrtc_version": ptx_receipt["nvrtc_library"]["version"],
            "fresh_process_projection_claim": FINAL_PROJECTION_CLAIM,
        },
        "build_provenance": {
            "direct_worker_receipt_sha256": files[
                "direct_worker_build_receipt"]["sha256"],
            "direct_operation_kat_sha256": files[
                "direct_operation_kat"]["sha256"],
            "rtdl_operation_kat_sha256": files[
                "rtdl_operation_kat"]["sha256"],
            "matched_ptx_receipt_sha256": files[
                "matched_ptx_prepare_receipt"]["sha256"],
            "pyoptix_wheel_build_receipt_sha256": files[
                "pyoptix_wheel_build_receipt"]["sha256"],
            "pyoptix_clean_install_receipt_sha256": files[
                "pyoptix_clean_install_receipt"]["sha256"],
            "pyoptix_operation_kat_sha256": files[
                "pyoptix_operation_kat"]["sha256"],
            "host_runtime_provenance_sha256": files[
                "host_runtime_provenance"]["sha256"],
            "header_projection_receipt_sha256": files[
                "header_projection_receipt"]["sha256"],
            "combined_runtime_receipt_sha256": files[
                "combined_runtime_receipt"]["sha256"],
            "combined_runtime_full_venv_member_tree_sha256": combined_runtime[
                "venv_member_tree_sha256"],
            "combined_runtime_path_projection": combined_path_projection,
            "header_projection_tree_sha256": directories[
                "header_projection"]["tree_sha256"],
            "fresh_process_projection_replay_verified": True,
            "all_source_to_runtime_links_verified_untimed": True,
        },
        "formal_preflight_contract": {
            "required_before_worker_zero": True,
            "python_startup_flags_exact": ["-I", "-S", "-B", "-P", "-c"],
            "controlled_site_packages_injection_required": True,
            "controlled_host_code_snapshot_import_required": True,
            "pth_execution_in_build_kat_preflight_or_formal": False,
            "live_target_all_fields_equal": True,
            "exact_loader_environment_replayed": True,
            "direct_nvrtc_v2_compile_identity_required": True,
            "fresh_python_matched_ptx_identity_required": True,
            "clean_python_rtdsl_package_import_identity_required": True,
            "cross_arm_libnvrtc_builtins_version_equal_required": True,
            "any_mismatch": "TERMINATE_BEFORE_WORKER_ZERO",
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
        },
        "registered_performance_timing_count": 0,
        "formal_worker_zero": False,
    }
    value["manifest_sha256"] = digest(value)
    validate_runtime_manifest(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    for role in FILE_ROLES:
        parser.add_argument(f"--{role.replace('_', '-')}",
                            dest=role, type=Path, required=True)
    for role in DIRECTORY_ROLES:
        parser.add_argument(f"--{role.replace('_', '-')}",
                            dest=role, type=Path, required=True)
    parser.add_argument("--relation-deployment-id", required=True)
    parser.add_argument("--triangle-deployment-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    value = build_manifest(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": value["status"], "manifest_sha256": value["manifest_sha256"],
        "formal_worker_zero": False, "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
