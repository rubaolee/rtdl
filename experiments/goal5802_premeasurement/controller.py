#!/usr/bin/env python3
"""Goal5802 controller admission and command-plan verifier.

The controlling local freeze has all execution booleans false.  This module
therefore emits only a deterministic command plan unless a future exact-byte
external review and a separate owner authority are both supplied.  No such
authority is created by Goal5802 premeasurement work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import time
from typing import Any, Mapping

from .contract import (
    ARMS,
    LEGACY_WORKERS,
    SCHEMA,
    canonical,
    validate_freeze,
)
from .runtime_manifest import (
    direct_nvrtc_identity_stdout_bytes,
    digest as runtime_digest,
    numba_llvmlite_runtime_authority,
    validate_direct_nvrtc_identity_document,
    validate_direct_operation_kat,
    validate_pyoptix_operation_kat,
    validate_rtdl_operation_kat,
    validate_runtime_manifest,
    validate_target_observation_receipt,
)
from scripts.goal5802_build_combined_runtime_untimed import (
    verify_run as verify_combined_runtime,
)


AUTHORITY_SCHEMA = "rtdl.goal5802.formal_execution_authority.v1"
OWNER_WAIVER_AUTHORITY_SCHEMA = (
    "rtdl.goal5802.owner_waiver_formal_execution_authority.v1")
OWNER_WAIVER_REASON = (
    "OWNER_DIRECTED_EXECUTION_WITHOUT_EXTERNAL_PREEXECUTION_REVIEW__"
    "MUST_DISCLOSE_AND_MUST_NOT_RELABEL")
QUALIFICATION_ONLY_TRUST_KEY_PREFIX = (
    "TEST_ONLY_goal5802_final_home_qualification_")
PREFLIGHT_PATH_ENV = "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_PATH"
PREFLIGHT_FILE_SHA_ENV = "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_FILE_SHA256"
PREFLIGHT_SELF_SHA_ENV = "GOAL5802_RUNTIME_PREFLIGHT_SHA256"
LIVE_CAPABILITY_SCHEMA = "rtdl.goal5802.live_controller_worker_capability.v1"
RTDSL_PACKAGE_PREFLIGHT_MODULES = (
    "rtdsl", "rtdsl.v4", "rtdsl.v4_callback_lifecycle",
    "rtdsl.v4_bounded_relation_optix_compiler",
    "rtdsl.v4_triangle_standard_library",
    "rtdsl.v4_triangle_reduction_optix_compiler",
    "rtdsl.v4_rtdlexe",
)


def _read_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid JSON: {path}: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _condition_common_deployment_file_union(
        files: Mapping[str, Any]) -> dict[str, object]:
    """Do no selective page-cache warming; six-order balance is the control."""

    del files
    rows: list[dict[str, object]] = []
    return {
        "policy": (
            "NO_MANUAL_FILE_PAGE_CONDITIONING__OS_PAGE_CACHE_UNCONTROLLED__"
            "BALANCED_SIX_ORDER"),
        "roles": [],
        "payload_bytes": 0,
        "rows_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
        "duration_ns": 0,
        "os_shared_library_and_driver_cache_state": "UNCONTROLLED__DISCLOSED",
    }


def _cache_root_end_state(roots: Mapping[str, Path]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for role, root in sorted(roots.items()):
        for path in sorted(root.rglob("*")):
            if path.is_symlink() or (not path.is_file() and not path.is_dir()):
                raise RuntimeError(f"isolated cache contains special path: {path}")
            if path.is_file():
                payload = path.read_bytes()
                rows.append({
                    "root": role, "path": path.relative_to(root).as_posix(),
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                })
    return {
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "rows_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
        "all_cache_roots_file_empty_after_worker": len(rows) == 0,
    }


def _valid_python_runtime_preload_receipt(
        arm: object, value: object) -> bool:
    if not isinstance(value, Mapping) \
            or value.get("schema") \
            != "rtdl.goal5802.python_runtime_preload.v1" \
            or value.get("status") != "PASS__BEFORE_PRIMARY_CLOCK" \
            or value.get("arm") != arm \
            or value.get("runtime_import_inside_primary_timer") is not False:
        return False
    if arm == "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY":
        return set(value) == {
            "schema", "status", "arm", "runtime_module",
            "required_preloaded_modules", "forbidden_absent_modules",
            "compiler_only_nvrtc_loaded", "prebuilt_ptx_deployment",
            "runtime_import_inside_primary_timer",
        } and value.get("runtime_module") \
            == "experiments.goal5796_matched.pyoptix_baseline" \
            and value.get("required_preloaded_modules") == [
                "experiments.goal5796_matched.pyoptix_baseline",
                "cupy", "numpy", "optix", "optix._optix",
            ] \
            and value.get("forbidden_absent_modules") \
            == ["cuda.bindings.nvrtc"] \
            and value.get("compiler_only_nvrtc_loaded") is False \
            and value.get("prebuilt_ptx_deployment") is True
    if arm == "D_RTDL_CLEAN_INSTALLED_RTLEXE":
        required = [
            "rtdsl", "rtdsl.v4_rtdlexe",
            "rtdsl.physical_execution_provenance",
            "atexit",
        ]
        if os.name == "posix":
            required.append("fcntl")
        return set(value) == {
            "schema", "status", "arm", "runtime_module",
            "implementation_module", "required_preloaded_modules",
            "forbidden_absent_modules", "public_symbol_identity_match_count",
            "legacy_rtdsl_v4_loaded", "runtime_import_inside_primary_timer",
        } and value.get("runtime_module") == "rtdsl" \
            and value.get("implementation_module") == "rtdsl.v4_rtdlexe" \
            and value.get("required_preloaded_modules") == required \
            and value.get("forbidden_absent_modules") == [
                "cuda.bindings.nvrtc",
                "experiments.goal5796_matched.pyoptix_baseline",
            ] \
            and value.get("public_symbol_identity_match_count") == 6 \
            and value.get("legacy_rtdsl_v4_loaded") is False
    return False


def validate_execution_authority(
        authority: Mapping[str, Any], *, freeze_sha256: str,
        runtime_manifest_sha256: str) -> None:
    schema = authority.get("schema")
    common = {
        "schema", "freeze_file_sha256", "runtime_manifest_file_sha256",
        "owner_execution_authorized", "formal_worker_zero_authorized",
        "pod_gpu_timing_authorized", "execution_authority_sha256",
    }
    if schema == AUTHORITY_SCHEMA:
        required = common | {
            "external_cfr_sha256", "external_review_p0",
            "external_review_p1", "external_exact_byte_approval",
        }
    elif schema == OWNER_WAIVER_AUTHORITY_SCHEMA:
        required = common | {
            "preexecution_cfr_sha256",
            "external_preexecution_review_claimed",
            "external_exact_byte_approval",
            "owner_explicit_external_review_waiver",
            "owner_waiver_reason",
        }
    else:
        raise RuntimeError("Goal5802 execution authority schema differs")
    if set(authority) != required:
        raise RuntimeError("Goal5802 execution authority keys differ")
    copy = dict(authority)
    observed = copy.pop("execution_authority_sha256")
    expected = hashlib.sha256(canonical(copy)).hexdigest()
    if observed != expected:
        raise RuntimeError("Goal5802 execution authority self-digest mismatch")
    if authority["freeze_file_sha256"] != freeze_sha256 \
            or authority["runtime_manifest_file_sha256"] \
            != runtime_manifest_sha256 \
            or authority["owner_execution_authorized"] is not True \
            or authority["formal_worker_zero_authorized"] is not True \
            or authority["pod_gpu_timing_authorized"] is not True:
        raise RuntimeError("Goal5802 two-key execution authority is not complete")
    if schema == AUTHORITY_SCHEMA:
        if authority["external_review_p0"] != 0 \
                or authority["external_review_p1"] != 0 \
                or authority["external_exact_byte_approval"] is not True:
            raise RuntimeError(
                "Goal5802 external-review execution authority is incomplete")
        document_key = "external_cfr_sha256"
    else:
        if authority["external_preexecution_review_claimed"] is not False \
                or authority["external_exact_byte_approval"] is not False \
                or authority["owner_explicit_external_review_waiver"] is not True \
                or authority["owner_waiver_reason"] != OWNER_WAIVER_REASON:
            raise RuntimeError(
                "Goal5802 owner-waiver authority is incomplete or misleading")
        document_key = "preexecution_cfr_sha256"
    for key in (
            "freeze_file_sha256", "runtime_manifest_file_sha256",
            document_key):
        item = authority[key]
        if not isinstance(item, str) or len(item) != 64 \
                or any(ch not in "0123456789abcdef" for ch in item):
            raise RuntimeError(f"Goal5802 execution authority digest invalid: {key}")


def reject_qualification_only_trust_root_for_formal(path: Path) -> None:
    """Make a Home-qualification key structurally unusable for formal work."""
    value = _read_json(path)
    key_id = value.get("key_id")
    if isinstance(key_id, str) \
            and key_id.startswith(QUALIFICATION_ONLY_TRUST_KEY_PREFIX):
        raise RuntimeError(
            "qualification-only trust root cannot authorize formal Goal5802 work")


def command_templates() -> dict[str, list[str]]:
    result = {
        "A_DIRECT_CUDA_OPTIX": [
            "<direct_scalar_worker>", "--task", "<task>",
            "--regime", "<regime>", "--ptx", "<matched_ptx>",
            "--ptx-sha256", "<matched_ptx_sha256>",
        ],
        "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY": [
            "<clean_python>", "-I", "-S", "-B", "-P", "-c",
            "<controlled_runpy_module_bootstrap>",
            "--arm", "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY",
            "--task", "<task>", "--regime", "<regime>",
            "--ptx", "<matched_ptx>",
        ],
        "D_RTDL_CLEAN_INSTALLED_RTLEXE": [
            "<clean_python>", "-I", "-S", "-B", "-P", "-c",
            "<controlled_runpy_module_bootstrap>",
            "--arm", "D_RTDL_CLEAN_INSTALLED_RTLEXE",
            "--task", "<task>", "--regime", "<regime>",
            "--artifact", "<artifact>", "--authority", "<authority>",
            "--trust-root", "<trust_root>", "--trust-head", "<trust_head>",
            "--trust-package", "<trust_package>",
            "--native-library", "<native_library>",
            "--deployment-id", "<deployment_id>",
        ],
    }
    if set(result) != set(ARMS):
        raise RuntimeError("Goal5802 command arm set drift")
    flattened = "\n".join(" ".join(tokens) for tokens in result.values())
    for path in LEGACY_WORKERS:
        if path in flattened:
            raise RuntimeError(f"legacy Goal5798 worker entered command plan: {path}")
    return result


def local_plan(freeze_path: Path, root: Path) -> dict[str, object]:
    freeze = _read_json(freeze_path)
    validate_freeze(freeze, root)
    if freeze.get("schema") != SCHEMA:
        raise RuntimeError("Goal5802 freeze schema mismatch")
    return {
        "schema": "rtdl.goal5802.local_command_plan.v1",
        "status": "PASS__LOCAL_PLAN_ONLY__FORMAL_WORKER_ZERO_LOCKED",
        "freeze_file_sha256": _sha(freeze_path),
        "freeze_self_sha256": freeze["freeze_sha256"],
        "worker_row_count": freeze["worker_row_count"],
        "build_cold_absolute_worker_row_count": freeze[
            "build_cold_absolute_worker_row_count"],
        "measurement_boundary_contract": {
            "DEPLOYMENT_COLD_primary_estimator":
                "WARM_PROCESS_DEPLOYMENT_COLD",
            "process_cold_claimed": False,
            "process_startup_and_admission_required_for_all_three_arms": True,
            "direct_pre_main_dso_loading":
                "SEPARATE_PROCESS_STARTUP_AND_ADMISSION_PHASE__NOT_PRIMARY",
            "python_interpreter_imports_and_selected_runtime_preload":
                "SEPARATE_PROCESS_STARTUP_AND_ADMISSION_PHASE__NOT_PRIMARY",
            "python_primary_timer_new_module_load_policy":
                "REJECT_ALL_NOT_PRELOADED",
            "python_startup_flags_exact": ["-I", "-S", "-B", "-P", "-c"],
            "pth_execution_in_build_kat_preflight_or_formal": False,
        },
        "command_templates": command_templates(),
        "build_cold_command_template": [
            "<clean_python>", "-I", "-S", "-B", "-P", "-c",
            "<controlled_runpy_module_bootstrap>",
            "--arm", "<arm>", "--task", "<task>",
            "--output-directory", "<new_build_output>",
        ],
        "legacy_goal5798_worker_allowed": False,
        "registered_performance_timing_count": 0,
        "formal_worker_zero": False,
    }


def _controlled_python_command(
        runtime: Mapping[str, Any], *, import_root: Path,
        module: str | None = None, script: Path | None = None) -> list[str]:
    """Use one site-disabled startup for S0, KAT, and formal workers."""

    if (module is None) == (script is None):
        raise RuntimeError("choose exactly one controlled Python target")
    files = runtime["files"]
    directories = runtime["directories"]
    clean_python = Path(str(files["clean_python"]["path"])).absolute()
    clean_python.resolve(strict=True)
    source_root = import_root.resolve(strict=True)
    package_root = Path(str(directories["rtdsl_package"]["path"])).resolve(
        strict=True)
    site_packages = package_root.parent
    pyoptix_initializer = Path(
        str(files["pyoptix_initializer"]["path"])).resolve(strict=True)
    if package_root.name != "rtdsl" \
            or pyoptix_initializer.parent.parent != site_packages:
        raise RuntimeError(
            "controlled Python packages do not share one exact site root")
    if module is not None:
        if not module or any(character.isspace() for character in module):
            raise RuntimeError("controlled Python module name differs")
        target = module
        invoke = f"runpy.run_module({module!r},run_name='__main__')"
    else:
        assert script is not None
        target_path = script.resolve(strict=True)
        target = str(target_path)
        invoke = f"runpy.run_path({str(target_path)!r},run_name='__main__')"
    bootstrap = (
        "import runpy,sys;"
        "sys.dont_write_bytecode=True;"
        f"sys.path[:0]=[{str(source_root)!r},{str(site_packages)!r}];"
        f"sys.argv=[{target!r},*sys.argv[1:]];"
        f"{invoke}"
    )
    return [
        str(clean_python), "-I", "-S", "-B", "-P", "-c", bootstrap,
    ]


def _write_new(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _materialize_host_code_snapshot(
        root: Path, output: Path, freeze: Mapping[str, Any]) -> dict[str, object]:
    """Create a manifest-exact, pycache-free import root for formal Python."""

    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    rows = []
    for record in freeze["source_manifest"]:
        relative = str(record["path"])
        if not relative.endswith(".py") or not (
                relative.startswith("experiments/")
                or relative.startswith("scripts/")):
            continue
        source = (root / relative).resolve(strict=True)
        payload = source.read_bytes()
        if len(payload) != record["bytes"] \
                or hashlib.sha256(payload).hexdigest() != record["sha256"]:
            raise RuntimeError(f"host-code snapshot source differs: {relative}")
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        destination.chmod(0o444)
        rows.append({"path": relative, "bytes": len(payload),
                     "sha256": record["sha256"]})
    if not rows or any(path.name == "__pycache__" for path in output.rglob("*")):
        raise RuntimeError("host-code snapshot is empty or contains pycache")
    for directory in sorted(
            (path for path in output.rglob("*") if path.is_dir()), reverse=True):
        directory.chmod(0o555)
    output.chmod(0o555)
    return {"schema": "rtdl.goal5802.host_code_snapshot.v1",
            "file_count": len(rows),
            "payload_bytes": sum(int(row["bytes"]) for row in rows),
            "rows_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
            "pycache_file_count": 0, "readonly": True}


def _preflight_file(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    if not resolved.is_file() or resolved.is_symlink():
        raise RuntimeError(f"Goal5802 preflight payload is not regular: {path}")
    return {
        "path": str(resolved), "bytes": resolved.stat().st_size,
        "sha256": _sha(resolved),
    }


def _preflight_process(
        command: list[str], *, root: Path, environment: Mapping[str, str],
        timeout_seconds: int,
        raw_evidence_path: Path) -> tuple[dict[str, object], dict[str, Any]]:
    completed = subprocess.run(
        command, cwd=root, env=dict(environment), capture_output=True,
        check=False, timeout=timeout_seconds)
    try:
        stdout = completed.stdout.decode("utf-8")
        stderr = completed.stderr.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError("Goal5802 preflight output is not UTF-8") from error
    process = {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_utf8": stdout,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_utf8": stderr,
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
    }
    _write_new(
        raw_evidence_path,
        json.dumps(process, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    if completed.returncode != 0 or stderr:
        raise RuntimeError({"Goal5802 runtime preflight process failed": process})
    try:
        document = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Goal5802 preflight stdout is not JSON") from error
    if not isinstance(document, dict):
        raise RuntimeError("Goal5802 preflight stdout root is not an object")
    return process, document


def _validate_live_python_nvrtc_receipt(
        value: Mapping[str, Any], *, runtime: Mapping[str, Any],
        output: Path, receipt_path: Path, child_path: Path,
        root: Path) -> None:
    files = runtime["files"]
    directories = runtime["directories"]
    cc = str(runtime["target_observation"]["compute_capability"])
    compute = "compute_" + cc.replace(".", "")
    sm = "sm_" + cc.replace(".", "")
    expected_argv = [
        str(child_path), "--mode", "ptx", "--source",
        str(files["device_source"]["path"]), "--compute-capability", cc,
        "--nvrtc-library", str(files["nvrtc_library"]["path"]),
        "--output", str(output), "--receipt", str(receipt_path),
        "--optix-include", str(directories["optix_include"]["path"]),
        "--cuda-include", str(directories["cuda_include"]["path"]),
    ]
    unsigned = dict(value)
    observed_seal = unsigned.pop("receipt_sha256", None)
    expected_product = _preflight_file(output)
    expected_source = {
        "path": str(Path(str(files["device_source"]["path"])).resolve(
            strict=True)),
        "bytes": files["device_source"]["bytes"],
        "sha256": files["device_source"]["sha256"],
    }
    expected_library = {
        "path": files["nvrtc_library"]["path"],
        "bytes": files["nvrtc_library"]["bytes"],
        "sha256": files["nvrtc_library"]["sha256"],
        "canonical_regular_file": True, "symlink": False,
    }
    expected_builtins = {
        "path": files["nvrtc_builtins"]["path"],
        "bytes": files["nvrtc_builtins"]["bytes"],
        "sha256": files["nvrtc_builtins"]["sha256"],
        "canonical_regular_file": True, "symlink": False,
    }
    expected_version = runtime["architecture_contract"]["libnvrtc_version"]
    if set(value) != {
            "schema", "status", "pid", "parent_pid", "argv", "cwd",
            "mode", "source", "include_roots", "compute_capability",
            "compile_options", "target", "product", "loaded_nvrtc",
            "clock_read_count", "gpu_kernel_launch_count",
            "formal_worker_count", "registered_performance_timing_count",
            "receipt_sha256"} \
            or value.get("schema") \
            != "rtdl.goal5802.fresh_nvrtc_compile_child.v2" \
            or value.get("status") \
            != "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE" \
            or value.get("pid") == os.getpid() \
            or value.get("parent_pid") != os.getpid() \
            or value.get("argv") != expected_argv \
            or value.get("cwd") != str(root) \
            or value.get("mode") != "ptx" \
            or value.get("source") != expected_source \
            or value.get("include_roots") != {
                "optix": directories["optix_include"]["path"],
                "cuda": directories["cuda_include"]["path"]} \
            or value.get("compute_capability") != cc \
            or value.get("compile_options") != [
                "--std=c++17", "--device-as-default-execution-space",
                "--relocatable-device-code=true",
                f"--gpu-architecture={compute}",
                f"-I{directories['optix_include']['path']}",
                f"-I{directories['cuda_include']['path']}",
                f"-I{Path(str(directories['cuda_include']['path'])) / 'nv'}"] \
            or value.get("target") != sm \
            or value.get("product") != expected_product \
            or value.get("loaded_nvrtc") != {
                "library": expected_library, "builtins": expected_builtins,
                "version": expected_version} \
            or any(type(value.get(key)) is not int or value[key] != 0 for key in (
                "clock_read_count", "gpu_kernel_launch_count",
                "formal_worker_count", "registered_performance_timing_count")) \
            or observed_seal != runtime_digest(unsigned) \
            or expected_product["sha256"] != files["matched_ptx"]["sha256"] \
            or expected_product["bytes"] != files["matched_ptx"]["bytes"]:
        raise RuntimeError("Goal5802 live Python NVRTC replay differs")


def _formal_runtime_preflight_impl(
        *, root: Path, output_directory: Path,
        host_code_snapshot_root: Path, runtime_path: Path,
        runtime: Mapping[str, Any], environment: Mapping[str, str],
        timeout_seconds: int, preflight_root: Path,
        stage_state: dict[str, str]) -> dict[str, object]:
    """Re-observe target and both compiler DSOs before formal worker zero."""

    files = runtime["files"]
    stage_state["stage"] = "TARGET_REOBSERVATION_PROCESS"
    target_path = preflight_root / "target_observation.json"
    capture = host_code_snapshot_root / "scripts/goal5802_capture_target_untimed.py"
    target_command = [
        *_controlled_python_command(
            runtime, import_root=host_code_snapshot_root, script=capture),
        "--nvidia-smi", str(files["nvidia_smi"]["path"]),
        "--nvcc", str(files["nvcc"]["path"]),
        "--output", str(target_path),
    ]
    target_process, target_stdout = _preflight_process(
        target_command, root=root, environment=environment,
        timeout_seconds=timeout_seconds,
        raw_evidence_path=preflight_root / "target_process.json")
    stage_state["stage"] = "TARGET_REOBSERVATION_VALIDATE"
    target_document = _read_json(target_path)
    if target_stdout != target_document:
        raise RuntimeError("Goal5802 live target stdout/receipt differs")
    live_target = validate_target_observation_receipt(
        target_document, files, require_current_loader_environment=False)
    frozen_target = runtime["target_observation"]
    if any(live_target[key] != frozen_target[key] for key in live_target):
        raise RuntimeError("Goal5802 live target differs before worker zero")
    frozen_target_document = _read_json(
        Path(str(files["target_observation_receipt"]["path"])))
    if target_document != frozen_target_document:
        raise RuntimeError(
            "Goal5802 live target receipt differs byte-semantically from prepare")

    stage_state["stage"] = "RTDSL_PACKAGE_IMPORT_PROCESS"
    package = runtime["directories"]["rtdsl_package"]
    import_child = host_code_snapshot_root / (
        "scripts/goal5802_capture_rtdsl_package_import_untimed.py")
    package_command = [
        *_controlled_python_command(
            runtime, import_root=host_code_snapshot_root, script=import_child),
        "--package-root", str(package["path"]),
        "--package-file-count", str(package["file_count"]),
        "--package-tree-sha256", str(package["tree_sha256"]),
    ]
    package_process, package_document = _preflight_process(
        package_command, root=root, environment=environment,
        timeout_seconds=timeout_seconds,
        raw_evidence_path=preflight_root / "rtdsl_package_process.json")
    stage_state["stage"] = "RTDSL_PACKAGE_IMPORT_VALIDATE"
    package_unsigned = dict(package_document)
    package_seal = package_unsigned.pop("receipt_sha256", None)
    package_rows = package.get("files")
    by_relative = {
        row.get("path"): row for row in package_rows
        if isinstance(row, Mapping)} if isinstance(package_rows, list) else {}
    imported = package_document.get("imported_modules")
    if not isinstance(imported, list) \
            or len(imported) != len(RTDSL_PACKAGE_PREFLIGHT_MODULES) \
            or package_document.get("schema") \
            != "rtdl.goal5802.rtdsl_package_import_preflight.v1" \
            or package_document.get("status") \
            != "PASS__CLEAN_PYTHON_IMPORTED_SEALED_RTDSL_PACKAGE" \
            or package_document.get("python_executable") \
            != str(Path(str(files["clean_python"].get(
                "resolved_path", files["clean_python"]["path"]))).resolve(
                    strict=True)) \
            or package_document.get("package_root") != package["path"] \
            or package_document.get("rtdsl_package_file_count") \
            != package["file_count"] \
            or package_document.get("rtdsl_package_tree_sha256") \
            != package["tree_sha256"] \
            or package_document.get("required_module_names") \
            != list(RTDSL_PACKAGE_PREFLIGHT_MODULES) \
            or any(type(package_document.get(key)) is not int
                   or package_document[key] != 0 for key in (
                       "clock_read_count", "registered_performance_timing_count",
                       "gpu_kernel_launch_count", "formal_worker_count")) \
            or package_seal != runtime_digest(package_unsigned):
        raise RuntimeError("Goal5802 clean Python package import differs")
    for expected_name, row in zip(
            RTDSL_PACKAGE_PREFLIGHT_MODULES, imported, strict=True):
        expected = (by_relative.get(row.get("relative_path"))
                    if isinstance(row, Mapping) else None)
        if not isinstance(row, Mapping) or set(row) != {
                "module", "path", "relative_path", "bytes", "sha256"} \
                or row.get("module") != expected_name \
                or not isinstance(expected, Mapping) \
                or row.get("bytes") != expected.get("bytes") \
                or row.get("sha256") != expected.get("sha256") \
                or Path(str(row.get("path"))) \
                != Path(str(package["path"])) / str(
                    row.get("relative_path")).removeprefix("rtdsl/"):
            raise RuntimeError(
                "Goal5802 clean Python imported module identity differs")

    stage_state["stage"] = "DIRECT_NVRTC_IDENTITY_PROCESS"
    direct_command = [
        str(files["direct_scalar_worker"]["path"]),
        "--local-nvrtc-identity",
    ]
    direct_process, direct_document = _preflight_process(
        direct_command, root=root, environment=environment,
        timeout_seconds=timeout_seconds,
        raw_evidence_path=preflight_root / "direct_process.json")
    stage_state["stage"] = "DIRECT_NVRTC_IDENTITY_VALIDATE"
    validate_direct_nvrtc_identity_document(direct_document, files)
    if direct_process["stdout_utf8"].encode("utf-8") \
            != direct_nvrtc_identity_stdout_bytes(direct_document):
        raise RuntimeError("Goal5802 live Direct identity stdout differs")
    direct_build = _read_json(
        Path(str(files["direct_worker_build_receipt"]["path"])))
    if direct_build.get("loaded_nvrtc_identity_document") != direct_document:
        raise RuntimeError(
            "Goal5802 live Direct NVRTC compile identity differs from prepare")

    stage_state["stage"] = "PYTHON_NVRTC_IDENTITY_PROCESS"
    python_product = preflight_root / "fresh_python_matched.ptx"
    python_receipt_path = preflight_root / "fresh_python_nvrtc.json"
    child = host_code_snapshot_root / "scripts/goal5802_nvrtc_compile_child.py"
    cc = str(runtime["target_observation"]["compute_capability"])
    python_command = [
        *_controlled_python_command(
            runtime, import_root=host_code_snapshot_root, script=child),
        "--mode", "ptx", "--source", str(files["device_source"]["path"]),
        "--compute-capability", cc,
        "--nvrtc-library", str(files["nvrtc_library"]["path"]),
        "--output", str(python_product),
        "--receipt", str(python_receipt_path),
        "--optix-include", str(runtime["directories"]["optix_include"]["path"]),
        "--cuda-include", str(runtime["directories"]["cuda_include"]["path"]),
    ]
    python_process, python_stdout = _preflight_process(
        python_command, root=root, environment=environment,
        timeout_seconds=timeout_seconds,
        raw_evidence_path=preflight_root / "python_process.json")
    stage_state["stage"] = "PYTHON_NVRTC_IDENTITY_VALIDATE"
    python_document = _read_json(python_receipt_path)
    _validate_live_python_nvrtc_receipt(
        python_document, runtime=runtime, output=python_product,
        receipt_path=python_receipt_path, child_path=child, root=root)
    if python_stdout != {
            "status": python_document["status"],
            "pid": python_document["pid"],
            "product_sha256": python_document["product"]["sha256"],
            "receipt_sha256": python_document["receipt_sha256"],
    }:
        raise RuntimeError("Goal5802 live Python NVRTC stdout/receipt differs")
    stage_state["stage"] = "CROSS_ARM_NVRTC_IDENTITY_COMPARE"
    loaded = python_document["loaded_nvrtc"]
    if direct_document["loaded_library_sha256"] \
            != loaded["library"]["sha256"] \
            or direct_document["loaded_builtins_sha256"] \
            != loaded["builtins"]["sha256"] \
            or direct_document["nvrtc_version"] != {
                "major": loaded["version"][0],
                "minor": loaded["version"][1]}:
        raise RuntimeError("Goal5802 live cross-arm NVRTC identity differs")

    stage_state["stage"] = "LOADER_AND_TOOL_ENVIRONMENT_COMPARE"
    loader_environment = {
        key: environment.get(key)
        for key in ("PATH", "LD_LIBRARY_PATH", "LD_PRELOAD")}
    if {key: loader_environment[key]
        for key in ("LD_LIBRARY_PATH", "LD_PRELOAD")} \
            != target_document["loader_environment"] \
            or loader_environment.get("LD_PRELOAD") is not None \
            or not loader_environment.get("PATH") \
            or any(not item or not Path(item).is_absolute()
                   for item in str(loader_environment["PATH"]).split(
                       os.pathsep)):
        raise RuntimeError("Goal5802 formal loader environment differs")
    stage_state["stage"] = "SUCCESS_RECEIPT_SEAL"
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.formal_runtime_preflight.v1",
        "status": "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO",
        "runtime_manifest_file_sha256": _sha(runtime_path),
        "loader_environment": loader_environment,
        "target_reobservation": {
            "process": target_process,
            "process_evidence": _preflight_file(
                preflight_root / "target_process.json"),
            "receipt": _preflight_file(target_path),
            "document": target_document,
            "all_frozen_fields_equal": True,
        },
        "direct_nvrtc_compile_identity": {
            "process": direct_process,
            "process_evidence": _preflight_file(
                preflight_root / "direct_process.json"),
            "document": direct_document,
            "prepare_document_byte_projection_equal": True,
        },
        "rtdsl_package_import_identity": {
            "process": package_process,
            "process_evidence": _preflight_file(
                preflight_root / "rtdsl_package_process.json"),
            "document": package_document,
            "all_modules_match_sealed_package": True,
        },
        "python_nvrtc_compile_identity": {
            "process": python_process,
            "process_evidence": _preflight_file(
                preflight_root / "python_process.json"),
            "receipt": _preflight_file(python_receipt_path),
            "document": python_document,
            "product": _preflight_file(python_product),
            "matched_ptx_byte_identical": True,
        },
        "cross_arm_libnvrtc_builtins_version_equal": True,
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
    }
    value["preflight_sha256"] = runtime_digest(value)
    validate_formal_runtime_preflight_receipt(
        value, runtime_manifest_sha256=_sha(runtime_path), rehash_files=True)
    _write_new(
        preflight_root / "receipt.json",
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return value


def _validate_preflight_process(value: object) -> None:
    if not isinstance(value, Mapping) or set(value) != {
            "command", "exit_code", "stdout_utf8", "stdout_sha256",
            "stderr_utf8", "stderr_sha256"} \
            or not isinstance(value.get("command"), list) \
            or not value["command"] \
            or not all(isinstance(item, str) and item for item in value["command"]) \
            or value.get("exit_code") != 0 \
            or not isinstance(value.get("stdout_utf8"), str) \
            or value.get("stdout_sha256") != hashlib.sha256(
                value["stdout_utf8"].encode("utf-8")).hexdigest() \
            or value.get("stderr_utf8") != "" \
            or value.get("stderr_sha256") != hashlib.sha256(b"").hexdigest():
        raise RuntimeError("Goal5802 formal preflight process evidence differs")


def _validate_preflight_file_record(
        value: object, *, rehash_files: bool) -> None:
    if not isinstance(value, Mapping) or set(value) != {
            "path", "bytes", "sha256"} \
            or not isinstance(value.get("path"), str) \
            or not Path(value["path"]).is_absolute() \
            or type(value.get("bytes")) is not int or value["bytes"] < 0 \
            or not isinstance(value.get("sha256"), str) \
            or len(value["sha256"]) != 64:
        raise RuntimeError("Goal5802 formal preflight file record differs")
    if rehash_files and _preflight_file(Path(value["path"])) != dict(value):
        raise RuntimeError("Goal5802 formal preflight file bytes differ")


def validate_formal_runtime_preflight_receipt(
        value: Mapping[str, Any], *, runtime_manifest_sha256: str,
        rehash_files: bool) -> None:
    """Validate the mandatory zero-worker live-runtime receipt."""

    unsigned = dict(value)
    observed_seal = unsigned.pop("preflight_sha256", None)
    required = {
        "schema", "status", "runtime_manifest_file_sha256",
        "loader_environment", "target_reobservation",
        "direct_nvrtc_compile_identity", "python_nvrtc_compile_identity",
        "rtdsl_package_import_identity",
        "cross_arm_libnvrtc_builtins_version_equal", "clock_read_count",
        "registered_performance_timing_count", "gpu_kernel_launch_count",
        "formal_worker_count", "preflight_sha256",
    }
    if set(value) != required \
            or value.get("schema") \
            != "rtdl.goal5802.formal_runtime_preflight.v1" \
            or value.get("status") \
            != "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO" \
            or value.get("runtime_manifest_file_sha256") \
            != runtime_manifest_sha256 \
            or observed_seal != runtime_digest(unsigned) \
            or value.get("cross_arm_libnvrtc_builtins_version_equal") is not True \
            or any(type(value.get(key)) is not int or value[key] != 0 for key in (
                "clock_read_count", "registered_performance_timing_count",
                "gpu_kernel_launch_count", "formal_worker_count")):
        raise RuntimeError("Goal5802 formal runtime preflight envelope differs")
    loader = value.get("loader_environment")
    if not isinstance(loader, Mapping) \
            or set(loader) != {"PATH", "LD_LIBRARY_PATH", "LD_PRELOAD"} \
            or loader.get("LD_PRELOAD") is not None \
            or not isinstance(loader.get("PATH"), str) or not loader["PATH"] \
            or any(not item or not Path(item).is_absolute()
                   for item in loader["PATH"].split(os.pathsep)) \
            or loader.get("LD_LIBRARY_PATH") is not None and (
                not isinstance(loader["LD_LIBRARY_PATH"], str)
                or not loader["LD_LIBRARY_PATH"]
                or any(not item or not Path(item).is_absolute()
                       for item in loader["LD_LIBRARY_PATH"].split(os.pathsep))):
        raise RuntimeError("Goal5802 formal preflight loader environment differs")
    target = value.get("target_reobservation")
    direct = value.get("direct_nvrtc_compile_identity")
    python = value.get("python_nvrtc_compile_identity")
    package = value.get("rtdsl_package_import_identity")
    if not isinstance(target, Mapping) or set(target) != {
            "process", "process_evidence", "receipt", "document",
            "all_frozen_fields_equal"} \
            or target.get("all_frozen_fields_equal") is not True \
            or not isinstance(direct, Mapping) or set(direct) != {
                "process", "process_evidence", "document",
                "prepare_document_byte_projection_equal"} \
            or direct.get("prepare_document_byte_projection_equal") is not True \
            or not isinstance(package, Mapping) or set(package) != {
                "process", "process_evidence", "document",
                "all_modules_match_sealed_package"} \
            or package.get("all_modules_match_sealed_package") is not True \
            or not isinstance(python, Mapping) or set(python) != {
                "process", "process_evidence", "receipt", "document",
                "product", "matched_ptx_byte_identical"} \
            or python.get("matched_ptx_byte_identical") is not True:
        raise RuntimeError("Goal5802 formal preflight component envelope differs")
    for row in (target, direct, package, python):
        _validate_preflight_process(row.get("process"))
        _validate_preflight_file_record(
            row.get("process_evidence"), rehash_files=rehash_files)
    for record in (target.get("receipt"), python.get("receipt"),
                   python.get("product")):
        _validate_preflight_file_record(record, rehash_files=rehash_files)
    try:
        target_stdout = json.loads(target["process"]["stdout_utf8"])
        direct_stdout = json.loads(direct["process"]["stdout_utf8"])
        package_stdout = json.loads(package["process"]["stdout_utf8"])
        python_stdout = json.loads(python["process"]["stdout_utf8"])
    except (TypeError, json.JSONDecodeError) as error:
        raise RuntimeError("Goal5802 formal preflight stdout is not JSON") from error
    if target_stdout != target.get("document") \
            or direct_stdout != direct.get("document") \
            or package_stdout != package.get("document"):
        raise RuntimeError("Goal5802 formal preflight stdout document differs")
    target_document = target.get("document")
    python_document = python.get("document")
    package_document = package.get("document")
    if not isinstance(target_document, Mapping) \
            or not isinstance(python_document, Mapping) \
            or not isinstance(package_document, Mapping):
        raise RuntimeError("Goal5802 formal preflight document absent")
    target_unsigned = dict(target_document)
    target_seal = target_unsigned.pop("observation_sha256", None)
    python_unsigned = dict(python_document)
    python_seal = python_unsigned.pop("receipt_sha256", None)
    package_unsigned = dict(package_document)
    package_seal = package_unsigned.pop("receipt_sha256", None)
    if target_seal != runtime_digest(target_unsigned) \
            or python_seal != runtime_digest(python_unsigned) \
            or package_seal != runtime_digest(package_unsigned) \
            or package_document.get("schema") \
            != "rtdl.goal5802.rtdsl_package_import_preflight.v1" \
            or package_document.get("status") \
            != "PASS__CLEAN_PYTHON_IMPORTED_SEALED_RTDSL_PACKAGE" \
            or python_stdout != {
                "status": python_document.get("status"),
                "pid": python_document.get("pid"),
                "product_sha256": (
                    python_document.get("product", {}).get("sha256")
                    if isinstance(python_document.get("product"), Mapping)
                    else None),
                "receipt_sha256": python_document.get("receipt_sha256"),
            }:
        raise RuntimeError("Goal5802 formal preflight nested seal differs")


def validate_formal_worker_preflight_gate(
        *, runtime_manifest_sha256: str,
        environment: Mapping[str, str] | None = None) -> dict[str, str]:
    """Require the exact successful live preflight before worker admission.

    This is an accidental/direct-entry guard and durable lineage binding.  The
    environment variables and unkeyed hashes are deliberately not described as
    authentication against a malicious owner; external exact-byte review and
    the independent raw recount remain the scientific trust boundary.
    """

    source = os.environ if environment is None else environment
    raw_path = source.get(PREFLIGHT_PATH_ENV)
    expected_file_sha = source.get(PREFLIGHT_FILE_SHA_ENV)
    expected_self_sha = source.get(PREFLIGHT_SELF_SHA_ENV)
    if not isinstance(raw_path, str) or not raw_path \
            or not isinstance(expected_file_sha, str) \
            or len(expected_file_sha) != 64 \
            or not isinstance(expected_self_sha, str) \
            or len(expected_self_sha) != 64:
        raise RuntimeError("Goal5802 formal worker preflight gate is absent")
    path = Path(raw_path)
    if not path.is_absolute() or path.is_symlink() or not path.is_file() \
            or str(path.resolve(strict=True)) != raw_path \
            or _sha(path) != expected_file_sha:
        raise RuntimeError("Goal5802 formal worker preflight file differs")
    value = _read_json(path)
    validate_formal_runtime_preflight_receipt(
        value, runtime_manifest_sha256=runtime_manifest_sha256,
        rehash_files=True)
    if value.get("preflight_sha256") != expected_self_sha:
        raise RuntimeError("Goal5802 formal worker preflight seal differs")
    return {
        "path": raw_path,
        "file_sha256": expected_file_sha,
        "preflight_sha256": expected_self_sha,
    }


def _live_worker_capability_bytes(
        row: Mapping[str, Any], *, environment: Mapping[str, str],
        nonce: str) -> bytes:
    value = {
        "schema": LIVE_CAPABILITY_SCHEMA,
        "controller_pid": os.getpid(),
        "worker_id": row["worker_id"],
        "runtime_manifest_sha256": environment[
            "GOAL5802_RUNTIME_MANIFEST_SHA256"],
        "preflight_receipt_file_sha256": environment[PREFLIGHT_FILE_SHA_ENV],
        "preflight_sha256": environment[PREFLIGHT_SELF_SHA_ENV],
        "nonce": nonce,
    }
    return canonical(value) + b"\n"


def consume_formal_worker_live_capability(
        *, worker_id: str, runtime_manifest_sha256: str,
        environment: Mapping[str, str] | None = None,
        stream: Any | None = None) -> str:
    """Consume one non-persistent controller capability from anonymous stdin.

    The fresh pipe closes after one frame.  A stale receipt plus copied env
    therefore cannot enter a formal worker.  This prevents ordinary direct
    spawn/operator mistakes; a malicious owner can implement a fake controller
    and is outside this unkeyed local-process threat boundary.
    """

    source = os.environ if environment is None else environment
    parent = source.get("GOAL5802_FORMAL_CONTROLLER_PID")
    if parent != str(os.getppid()):
        raise RuntimeError("Goal5802 live controller parent differs")
    handle = sys.stdin.buffer if stream is None else stream
    payload = handle.read(4097)
    if not isinstance(payload, bytes) or not payload or len(payload) > 4096 \
            or not payload.endswith(b"\n") or payload.count(b"\n") != 1:
        raise RuntimeError("Goal5802 live controller capability frame differs")
    try:
        value = json.loads(payload)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "Goal5802 live controller capability is not JSON") from error
    required = {
        "schema", "controller_pid", "worker_id", "runtime_manifest_sha256",
        "preflight_receipt_file_sha256", "preflight_sha256", "nonce",
    }
    nonce = value.get("nonce") if isinstance(value, Mapping) else None
    if not isinstance(value, Mapping) or set(value) != required \
            or value.get("schema") != LIVE_CAPABILITY_SCHEMA \
            or value.get("controller_pid") != os.getppid() \
            or value.get("worker_id") != worker_id \
            or value.get("runtime_manifest_sha256") \
            != runtime_manifest_sha256 \
            or value.get("preflight_receipt_file_sha256") \
            != source.get(PREFLIGHT_FILE_SHA_ENV) \
            or value.get("preflight_sha256") \
            != source.get(PREFLIGHT_SELF_SHA_ENV) \
            or not isinstance(nonce, str) or len(nonce) != 64 \
            or any(character not in "0123456789abcdef" for character in nonce) \
            or payload != canonical(dict(value)) + b"\n":
        raise RuntimeError("Goal5802 live controller capability differs")
    # Return only a public one-way trace; never persist or return the nonce.
    return hashlib.sha256(payload).hexdigest()


def _formal_runtime_preflight(
        *, root: Path, output_directory: Path,
        host_code_snapshot_root: Path, runtime_path: Path,
        runtime: Mapping[str, Any], environment: Mapping[str, str],
        timeout_seconds: int) -> dict[str, object]:
    preflight_root = output_directory / "runtime_preflight"
    preflight_root.mkdir()
    stage_state = {"stage": "PREFLIGHT_ROOT_CREATED"}
    try:
        return _formal_runtime_preflight_impl(
            root=root, output_directory=output_directory,
            host_code_snapshot_root=host_code_snapshot_root,
            runtime_path=runtime_path, runtime=runtime,
            environment=environment, timeout_seconds=timeout_seconds,
            preflight_root=preflight_root, stage_state=stage_state)
    except Exception as error:
        preserved = []
        for path in sorted(preflight_root.iterdir(), key=lambda item: item.name):
            if path.name == "failure_receipt.json" or not path.is_file() \
                    or path.is_symlink():
                continue
            record = _preflight_file(path)
            preserved.append({"name": path.name, **record})
        loader_environment = {
            key: environment.get(key)
            for key in ("PATH", "LD_LIBRARY_PATH", "LD_PRELOAD")}
        failure: dict[str, object] = {
            "schema": "rtdl.goal5802.formal_runtime_preflight_failure.v1",
            "status": "FAIL__TERMINATED_BEFORE_FORMAL_WORKER_ZERO",
            "failed_stage": stage_state["stage"],
            "error": {"type": type(error).__name__, "message": str(error)},
            "runtime_manifest_file_sha256": _sha(runtime_path),
            "loader_environment": loader_environment,
            "preserved_preflight_payloads": preserved,
            "retry_count": 0,
            "replacement_count": 0,
            "clock_read_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "formal_worker_count": 0,
        }
        failure["failure_sha256"] = runtime_digest(failure)
        failure_path = preflight_root / "failure_receipt.json"
        _write_new(
            failure_path,
            json.dumps(failure, indent=2, sort_keys=True).encode("utf-8") + b"\n")
        raise RuntimeError(
            f"Goal5802 runtime preflight failed before worker zero; "
            f"receipt={failure_path}") from error


def _formal_command(
        row: Mapping[str, Any], *, root: Path, freeze_path: Path,
        authority_path: Path, runtime_path: Path,
        runtime: Mapping[str, Any], import_root: Path) -> list[str]:
    files = runtime["files"]
    directories = runtime["directories"]
    task = str(row["task"])
    regime = str(row["regime"])
    arm = str(row["arm"])
    common = [
        "--task", task,
        "--regime", regime,
        "--ptx", str(files["matched_ptx"]["path"]),
        "--ptx-sha256", str(files["matched_ptx"]["sha256"]),
    ]
    if task.startswith("CUSTOM_AABB"):
        common.extend([
            "--compaction-cubin", str(files["compaction_cubin"]["path"]),
            "--compaction-cubin-sha256", str(
                files["compaction_cubin"]["sha256"]),
        ])
    if arm == "A_DIRECT_CUDA_OPTIX":
        return [
            str(files["direct_scalar_worker"]["path"]),
            "--worker-id", str(row["worker_id"]),
            "--freeze-sha256", _sha(freeze_path),
            "--authority-sha256", _sha(authority_path),
            "--runtime-manifest-sha256", _sha(runtime_path),
            *common,
        ]
    python_common = [
        *_controlled_python_command(
            runtime, import_root=import_root,
            module="experiments.goal5802_premeasurement.python_worker"),
        "--arm", arm, "--task", task, "--regime", regime,
        "--root", str(root), "--freeze", str(freeze_path),
        "--execution-authority", str(authority_path),
        "--runtime-manifest", str(runtime_path),
        "--worker-id", str(row["worker_id"]),
    ]
    if arm.startswith("B_NVIDIA_PYOPTIX"):
        command = [
            *python_common,
            "--ptx", str(files["matched_ptx"]["path"]),
        ]
        if task.startswith("CUSTOM_AABB"):
            command.extend([
                "--compaction-cubin", str(
                    files["compaction_cubin"]["path"]),
            ])
        return command
    family = "relation" if task.startswith("CUSTOM_AABB") else "triangle"
    return [
        *python_common,
        "--artifact", str(files[f"{family}_artifact"]["path"]),
        "--authority", str(files[f"{family}_authority"]["path"]),
        "--trust-root", str(files["trust_root"]["path"]),
        "--trust-head", str(files["trust_head"]["path"]),
        "--trust-package", str(files["trust_package"]["path"]),
        "--native-library", str(files["native_library"]["path"]),
        "--deployment-id", str(runtime["deployment_ids"][family]),
    ]


def _build_cold_command(
        row: Mapping[str, Any], *, root: Path, freeze_path: Path,
        authority_path: Path, runtime_path: Path,
        runtime: Mapping[str, Any], product_directory: Path,
        import_root: Path) -> list[str]:
    return [
        *_controlled_python_command(
            runtime, import_root=import_root,
            module="experiments.goal5802_premeasurement.build_cold_worker"),
        "--arm", str(row["arm"]),
        "--task", str(row["task"]),
        "--worker-id", str(row["worker_id"]),
        "--root", str(root),
        "--freeze", str(freeze_path),
        "--execution-authority", str(authority_path),
        "--runtime-manifest", str(runtime_path),
        "--output-directory", str(product_directory),
    ]


def _execute_one(
        *, row: Mapping[str, Any], command: list[str], root: Path,
        environment: Mapping[str, str], worker_dir: Path,
        timeout_seconds: int, receipt_schema: str,
        cache_conditioning_files: Mapping[str, Any] | None = None
        ) -> dict[str, object]:
    flattened = " ".join(command)
    if any(path in flattened for path in LEGACY_WORKERS):
        raise RuntimeError("legacy Goal5798 worker entered formal command")
    worker_dir.mkdir()
    cache_root = worker_dir / "isolated_process_caches"
    cuda_cache = cache_root / "cuda"
    cupy_cache = cache_root / "cupy"
    optix_cache = cache_root / "optix"
    xdg_cache = cache_root / "xdg"
    isolated_home = worker_dir / "isolated_home"
    isolated_tmp = worker_dir / "isolated_tmp"
    cache_roots = {
        "cuda": cuda_cache, "cupy": cupy_cache, "optix": optix_cache,
        "xdg": xdg_cache, "home": isolated_home, "tmp": isolated_tmp,
    }
    for path in cache_roots.values():
        path.mkdir(parents=True)
    isolated_cache_policy = {
        "policy": "FRESH_EMPTY_PER_WORKER_PROCESS_CACHE_ROOTS",
        "cuda_cache_disabled": True,
        "optix_cache_disabled": True,
        "cuda_cache_path": str(cuda_cache.resolve()),
        "cupy_cache_dir": str(cupy_cache.resolve()),
        "optix_cache_path": str(optix_cache.resolve()),
        "xdg_cache_home": str(xdg_cache.resolve()),
        "home": str(isolated_home.resolve()),
        "tmp": str(isolated_tmp.resolve()),
        "all_directories_empty_before_worker": True,
    }
    _write_new(
        worker_dir / "command.json",
        json.dumps(command, sort_keys=True).encode("utf-8") + b"\n")
    envelope_start = time.perf_counter_ns()
    cache_conditioning = (
        _condition_common_deployment_file_union(cache_conditioning_files)
        if cache_conditioning_files is not None else None)
    worker_environment = dict(environment)
    worker_environment.update({
        "HOME": isolated_cache_policy["home"],
        "XDG_CACHE_HOME": isolated_cache_policy["xdg_cache_home"],
        "CUDA_CACHE_PATH": isolated_cache_policy["cuda_cache_path"],
        "CUDA_CACHE_DISABLE": "1",
        "CUPY_CACHE_DIR": isolated_cache_policy["cupy_cache_dir"],
        "OPTIX_CACHE_PATH": isolated_cache_policy["optix_cache_path"],
        "OPTIX_CACHE_ENABLED": "0",
        "OPTIX_CACHE_MAXSIZE": "0",
        "RTDL_DISABLE_CUBIN_CACHE": "1",
        "TMP": isolated_cache_policy["tmp"],
        "TEMP": isolated_cache_policy["tmp"],
        "TMPDIR": isolated_cache_policy["tmp"],
    })
    for key in (
            "GOAL5802_RUNTIME_MANIFEST_SHA256", PREFLIGHT_FILE_SHA_ENV,
            PREFLIGHT_SELF_SHA_ENV):
        item = worker_environment.get(key)
        if not isinstance(item, str) or len(item) != 64 \
                or any(character not in "0123456789abcdef" for character in item):
            raise RuntimeError(
                f"Goal5802 live worker capability input differs: {key}")
    process: subprocess.Popen[bytes] | None = None
    spawn_error: str | None = None
    orphan_process_group_detected = False
    timed_out = False
    stdout = b""
    stderr = b""
    exit_code: int | None = None
    try:
        spawn_start = time.perf_counter_ns()
        worker_environment["GOAL5802_CONTROLLER_ENVELOPE_START_NS"] = str(
            spawn_start)
        process = subprocess.Popen(
            command, cwd=root, env=worker_environment,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=(os.name == "posix"),
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0))
        try:
            # Generate and send one nonce only after the child exists.  stdin is
            # a fresh anonymous pipe per worker and closes after this frame.
            capability = _live_worker_capability_bytes(
                row, environment=worker_environment,
                nonce=secrets.token_hex(32))
            stdout, stderr = process.communicate(
                input=capability, timeout=timeout_seconds)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            stdout, stderr = process.communicate()
            exit_code = None
        if os.name == "posix" and not timed_out:
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                pass
            else:
                orphan_process_group_detected = True
                os.killpg(process.pid, signal.SIGKILL)
    except OSError as error:
        spawn_error = f"{type(error).__name__}: {error}"
        stderr = spawn_error.encode("utf-8", errors="replace")
    envelope_ns = time.perf_counter_ns() - envelope_start
    isolated_cache_end_state = _cache_root_end_state(cache_roots)
    _write_new(worker_dir / "stdout.bin", stdout)
    _write_new(worker_dir / "stderr.bin", stderr)
    parsed = None
    if exit_code == 0:
        try:
            parsed = json.loads(stdout)
        except (UnicodeError, json.JSONDecodeError):
            parsed = None
    comparative = (
        receipt_schema
        == "rtdl.goal5802.comparative_controller_worker_receipt.v1")
    measurement_boundary = None
    measurement_boundary_valid = not comparative
    if comparative and isinstance(parsed, dict):
        phases = parsed.get("phase_durations_ns")
        admission = (
            phases.get("process_startup_and_admission")
            if isinstance(phases, Mapping) else None)
        expected_estimator = (
            "WARM_PROCESS_DEPLOYMENT_COLD"
            if row["regime"] == "DEPLOYMENT_COLD" else row["regime"])
        python_arm = row["arm"] != "A_DIRECT_CUDA_OPTIX"
        preload = parsed.get("constructor_runtime_preload_receipt")
        python_boundary_valid = (
            not python_arm or (
                _valid_python_runtime_preload_receipt(row["arm"], preload)
                and parsed.get("primary_estimator_name") == expected_estimator
                and parsed.get("new_forbidden_module_load_inside_primary_timer")
                is False
                and parsed.get("primary_timer_new_module_load_policy")
                == "REJECT_ALL_NOT_PRELOADED"
                and parsed.get("constructor_evidence_inside_primary_timer")
                is False))
        measurement_boundary_valid = (
            type(admission) is int and admission > 0
            and python_boundary_valid)
        measurement_boundary = {
            "schema": "rtdl.goal5802.comparative_measurement_boundary.v1",
            "primary_estimator_name": expected_estimator,
            "primary_estimator_excludes_process_startup_and_admission": True,
            "process_startup_and_admission_separately_published": True,
            "process_startup_and_admission_ns": admission,
            "controller_process_envelope_separately_published": True,
            "direct_pre_main_dso_boundary": (
                "INCLUDED_IN_PROCESS_STARTUP_AND_ADMISSION__OUTSIDE_PRIMARY"
                if not python_arm else "NOT_APPLICABLE"),
            "python_interpreter_import_and_arm_runtime_preload_boundary": (
                "INCLUDED_IN_PROCESS_STARTUP_AND_ADMISSION__OUTSIDE_PRIMARY"
                if python_arm else "NOT_APPLICABLE"),
            "deployment_cold_is_process_cold_claimed": False,
            "boundary_valid": measurement_boundary_valid,
        }
    success = (
        exit_code == 0 and isinstance(parsed, dict)
        and parsed.get("status") == "PASS"
        and parsed.get("arm") == row["arm"]
        and parsed.get("worker_id") == row["worker_id"]
        and parsed.get("task") == row["task"]
        and parsed.get("regime") == row["regime"]
        and parsed.get("freeze_file_sha256")
        == environment.get("GOAL5802_FREEZE_FILE_SHA256")
        and parsed.get("execution_authority_sha256")
        == environment.get("GOAL5802_EXECUTION_AUTHORITY_SHA256")
        and parsed.get("runtime_manifest_sha256")
        == environment.get("GOAL5802_RUNTIME_MANIFEST_SHA256")
        and spawn_error is None and orphan_process_group_detected is False
        and measurement_boundary_valid
        and isolated_cache_end_state[
            "all_cache_roots_file_empty_after_worker"] is True
    )
    receipt = {
        "schema": receipt_schema,
        "worker_directory_name": worker_dir.name,
        "schedule_row": row,
        "status": "PASS" if success else "FAIL__NO_RETRY_OR_REPLACEMENT",
        "exit_code": exit_code,
        "timed_out": timed_out,
        "spawn_error": spawn_error,
        "new_process_group_or_session": True,
        "orphan_process_group_detected": orphan_process_group_detected,
        "controller_process_envelope_ns": envelope_ns,
        "preworker_common_cache_conditioning": cache_conditioning,
        "isolated_process_cache_policy": isolated_cache_policy,
        "isolated_process_cache_end_state": isolated_cache_end_state,
        "stdout_bytes": len(stdout),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_bytes": len(stderr),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "worker_result": parsed,
        "comparative_measurement_boundary": measurement_boundary,
    }
    _write_new(
        worker_dir / "receipt.json",
        json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return receipt


def execute_formal(
        *, root: Path, freeze_path: Path, authority_path: Path,
        runtime_path: Path, output_directory: Path,
        timeout_seconds: int) -> dict[str, object]:
    """Execute the exact schedule once; never retry or replace a worker."""

    root = root.resolve(strict=True)
    freeze_path = freeze_path.resolve(strict=True)
    authority_path = authority_path.resolve(strict=True)
    runtime_path = runtime_path.resolve(strict=True)
    output_directory = output_directory.resolve(strict=False)
    freeze = _read_json(freeze_path)
    validate_freeze(freeze, root)
    authority = _read_json(authority_path)
    freeze_file_sha = _sha(freeze_path)
    runtime = _read_json(runtime_path)
    validate_runtime_manifest(runtime)
    combined_runtime_receipt = Path(str(
        runtime["files"]["combined_runtime_receipt"]["path"]))
    combined_runtime = verify_combined_runtime(combined_runtime_receipt.parent)
    runtime_file_sha = _sha(runtime_path)
    validate_execution_authority(
        authority, freeze_sha256=freeze_file_sha,
        runtime_manifest_sha256=runtime_file_sha)
    files = runtime["files"]
    reject_qualification_only_trust_root_for_formal(
        Path(str(files["trust_root"]["path"])))
    product = freeze["product_binding"]
    expected_product_files = {
        "rtdl_wheel": product["wheel_sha256"],
        "native_library": product["native_sha256"],
        "trust_root": product["trust_root_sha256"],
        "trust_head": product["trust_head_sha256"],
        "trust_package": product["trust_package_sha256"],
        "relation_artifact": product["relation_artifact_sha256"],
        "relation_authority": product["relation_authority_sha256"],
        "triangle_artifact": product["triangle_artifact_sha256"],
        "triangle_authority": product["triangle_authority_sha256"],
        "rtdsl_init": product["rtdsl_init_sha256"],
        "rtdlexe_module": product["rtdlexe_module_sha256"],
    }
    if any(files[role]["sha256"] != expected
           for role, expected in expected_product_files.items()) \
            or runtime["directories"]["rtdsl_package"]["file_count"] \
            != product["rtdsl_package_file_count"] \
            or runtime["directories"]["rtdsl_package"]["tree_sha256"] \
            != product["rtdsl_package_tree_sha256"] \
            or runtime["deployment_ids"]["relation"] \
            != product["relation_deployment_id"] \
            or runtime["deployment_ids"]["triangle"] \
            != product["triangle_deployment_id"]:
        raise RuntimeError("Goal5802 runtime differs from final clean RTDL binding")
    frozen_sources = {row["path"]: row["sha256"]
                      for row in freeze["source_manifest"]}
    exact_runtime_source_links = {
        "direct_scalar_source": (
            "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"),
        "device_source": (
            "experiments/goal5802_premeasurement/"
            "matched_device_semantic_capacity.cu"),
        "compaction_source": (
            "experiments/goal5802_premeasurement/"
            "relation_semantic_compaction.cu"),
    }
    if any(files[role]["sha256"] != frozen_sources[path]
           for role, path in exact_runtime_source_links.items()) \
            or runtime["pyoptix"]["goal5800_v7_source_sha256"] \
            != frozen_sources[
                "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py"]:
        raise RuntimeError("Goal5802 target runtime source differs from freeze")
    operation_kat = _read_json(Path(str(files["pyoptix_operation_kat"]["path"])))
    validate_pyoptix_operation_kat(
        operation_kat, files,
        expected_source_sha256=frozen_sources[
            "experiments/goal5802_premeasurement/pyoptix_scalar_arm.py"])
    direct_operation_kat = _read_json(
        Path(str(files["direct_operation_kat"]["path"])))
    validate_direct_operation_kat(direct_operation_kat, files)
    rtdl_operation_kat = _read_json(
        Path(str(files["rtdl_operation_kat"]["path"])))
    validate_rtdl_operation_kat(
        rtdl_operation_kat, files, runtime["deployment_ids"],
        expected_executable_identities={
            "relation": product[
                "relation_executable_identity_sha256"],
            "triangle": product[
                "triangle_executable_identity_sha256"],
        })
    if output_directory.exists() or output_directory.is_symlink():
        raise FileExistsError(output_directory)
    output_directory.mkdir(parents=True)
    host_code_snapshot = _materialize_host_code_snapshot(
        root, output_directory / "host_code_snapshot", freeze)
    authority_file_sha = _sha(authority_path)
    environment = {
        key: value for key, value in os.environ.items()
        if key in {
            "PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "WINDIR",
            "TMP", "TEMP", "LD_LIBRARY_PATH",
        }
    }
    environment.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "GOAL5802_FORMAL_CONTROLLER_PID": str(os.getpid()),
        "GOAL5802_FREEZE_FILE_SHA256": freeze_file_sha,
        "GOAL5802_EXECUTION_AUTHORITY_SHA256": authority_file_sha,
        "GOAL5802_RUNTIME_MANIFEST_SHA256": runtime_file_sha,
    })
    host_runtime = _read_json(
        Path(str(files["host_runtime_provenance"]["path"])))
    compiler_runtime_authority = numba_llvmlite_runtime_authority(
        host_runtime, files)
    formal_thread_environment = host_runtime.get(
        "thread_and_visibility_environment")
    expected_thread_keys = {
        "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
        "PYTHONHASHSEED", "CUDA_VISIBLE_DEVICES",
        "PATH", "LD_LIBRARY_PATH", "LD_PRELOAD",
    }
    if not isinstance(formal_thread_environment, Mapping) \
            or set(formal_thread_environment) != expected_thread_keys:
        raise RuntimeError("formal thread/visibility environment is absent")
    for key, value in formal_thread_environment.items():
        if value is None:
            environment.pop(key, None)
        elif isinstance(value, str):
            environment[key] = value
        else:
            raise RuntimeError(
                f"formal environment value is not text/null: {key}")
    environment["PYTHONPATH"] = str(
        (output_directory / "host_code_snapshot").resolve(strict=True))
    runtime_preflight = _formal_runtime_preflight(
        root=root, output_directory=output_directory,
        host_code_snapshot_root=(
            output_directory / "host_code_snapshot").resolve(strict=True),
        runtime_path=runtime_path, runtime=runtime, environment=environment,
        timeout_seconds=timeout_seconds)
    preflight_receipt_path = (
        output_directory / "runtime_preflight" / "receipt.json").resolve(
            strict=True)
    environment[PREFLIGHT_PATH_ENV] = str(preflight_receipt_path)
    environment[PREFLIGHT_FILE_SHA_ENV] = _sha(preflight_receipt_path)
    environment[PREFLIGHT_SELF_SHA_ENV] = str(
        runtime_preflight["preflight_sha256"])
    validate_formal_worker_preflight_gate(
        runtime_manifest_sha256=runtime_file_sha, environment=environment)
    controlled_import_root = (
        output_directory / "host_code_snapshot").resolve(strict=True)
    comparative_rows = []
    for row in freeze["schedule"]:
        command = _formal_command(
            row, root=root, freeze_path=freeze_path,
            authority_path=authority_path, runtime_path=runtime_path,
            runtime=runtime, import_root=controlled_import_root)
        worker_dir = output_directory / (
            f"comparative_{int(row['ordinal']):04d}_{row['worker_id']}")
        comparative_rows.append(_execute_one(
            row=row, command=command, root=root, environment=environment,
            worker_dir=worker_dir, timeout_seconds=timeout_seconds,
            receipt_schema="rtdl.goal5802.comparative_controller_worker_receipt.v1",
            cache_conditioning_files=files))
    build_cold_rows = []
    for row in freeze["build_cold_absolute_schedule"]:
        worker_dir = output_directory / (
            f"build_cold_{int(row['ordinal']):04d}_{row['worker_id']}")
        command = _build_cold_command(
            row, root=root, freeze_path=freeze_path,
            authority_path=authority_path, runtime_path=runtime_path,
            runtime=runtime, product_directory=worker_dir / "built_product",
            import_root=controlled_import_root)
        build_cold_rows.append(_execute_one(
            row=row, command=command, root=root, environment=environment,
            worker_dir=worker_dir, timeout_seconds=timeout_seconds,
            receipt_schema="rtdl.goal5802.build_cold_controller_worker_receipt.v1"))
    all_rows = [*comparative_rows, *build_cold_rows]
    # Detect any mutation of the exact installed package, compiler inputs, or
    # deployment payloads that occurred after preflight or during the matrix.
    validate_runtime_manifest(runtime)
    post_execution_runtime_revalidation = {
        "status": "PASS__ALL_RUNTIME_PAYLOADS_REHASHED_AFTER_FINAL_WORKER",
        "runtime_manifest_file_sha256": _sha(runtime_path),
        "combined_runtime_receipt_sha256": _sha(combined_runtime_receipt),
        "combined_runtime_full_venv_member_tree_sha256": (
            verify_combined_runtime(combined_runtime_receipt.parent)[
                "venv_member_tree_sha256"]),
        "rtdsl_package_file_count": runtime["directories"][
            "rtdsl_package"]["file_count"],
        "rtdsl_package_tree_sha256": runtime["directories"][
            "rtdsl_package"]["tree_sha256"],
    }
    result = {
        "schema": "rtdl.goal5802.formal_controller_result.v2",
        "status": (
            "COMPLETE" if all(row["status"] == "PASS" for row in all_rows)
            else "COMPLETE_WITH_FAILED_ROWS__NO_RETRY_OR_REPLACEMENT"),
        "freeze_file_sha256": freeze_file_sha,
        "execution_authority_sha256": authority_file_sha,
        "runtime_manifest_sha256": _sha(runtime_path),
        "worker_count": len(all_rows),
        "comparative_worker_count": len(comparative_rows),
        "build_cold_absolute_worker_count": len(build_cold_rows),
        "passed_worker_count": sum(
            row["status"] == "PASS" for row in all_rows),
        "failed_worker_count": sum(
            row["status"] != "PASS" for row in all_rows),
        "retry_count": 0,
        "replacement_count": 0,
        "comparative_rows": comparative_rows,
        "build_cold_absolute_rows": build_cold_rows,
        "build_cold_enters_comparative_gate": False,
        "host_code_snapshot": host_code_snapshot,
        "runtime_preflight": runtime_preflight,
        "preworker_combined_runtime_revalidation": {
            "receipt_sha256": _sha(combined_runtime_receipt),
            "venv_member_tree_sha256": combined_runtime[
                "venv_member_tree_sha256"],
        },
        "numba_llvmlite_runtime_authority": compiler_runtime_authority,
        "post_execution_runtime_revalidation": (
            post_execution_runtime_revalidation),
        "measurement_boundary_contract": {
            "DEPLOYMENT_COLD_primary_estimator":
                "WARM_PROCESS_DEPLOYMENT_COLD",
            "process_cold_claimed": False,
            "process_startup_and_admission_required_for_all_three_arms": True,
            "process_startup_and_admission_separately_published": True,
            "direct_pre_main_dso_loading":
                "SEPARATE_PROCESS_STARTUP_AND_ADMISSION_PHASE__NOT_PRIMARY",
            "python_interpreter_imports_and_selected_runtime_preload":
                "SEPARATE_PROCESS_STARTUP_AND_ADMISSION_PHASE__NOT_PRIMARY",
            "python_adapter_load_scope":
                "DEPLOYED_BYTES_AND_PUBLIC_RUNTIME_DEPLOYMENT_LOAD_ONLY",
            "python_primary_timer_new_module_load_policy":
                "REJECT_ALL_NOT_PRELOADED",
            "python_startup_flags_exact": ["-I", "-S", "-B", "-P", "-c"],
            "pth_execution_in_build_kat_preflight_or_formal": False,
        },
    }
    _write_new(
        output_directory / "controller_result.json",
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--plan-output", type=Path)
    parser.add_argument("--execution-authority", type=Path)
    parser.add_argument("--runtime-manifest", type=Path)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    args = parser.parse_args()
    result = local_plan(args.freeze, args.root)
    if args.execution_authority is not None:
        if args.runtime_manifest is None or args.output_directory is None:
            raise RuntimeError(
                "formal Goal5802 controller requires runtime manifest and output")
        formal = execute_formal(
            root=args.root, freeze_path=args.freeze,
            authority_path=args.execution_authority,
            runtime_path=args.runtime_manifest,
            output_directory=args.output_directory,
            timeout_seconds=args.timeout_seconds)
        print(json.dumps(formal, sort_keys=True))
        return 0
    if args.plan_output is not None:
        if args.plan_output.exists():
            raise FileExistsError(args.plan_output)
        args.plan_output.parent.mkdir(parents=True, exist_ok=True)
        args.plan_output.write_bytes(
            json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
