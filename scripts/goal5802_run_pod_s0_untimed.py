#!/usr/bin/env python3
"""Execute the create-only, two-stage Goal5802 target S0 transaction.

This is an orchestration boundary, not a measurement controller.  It runs a
fixed sequence of source-controlled untimed preparation tools, stops at one
predeclared offline TEST_ONLY signing checkpoint, and never accepts a formal
execution authority.  Every subprocess is invoked once with an argv vector;
shell evaluation, retry, resume, replacement, and output-root reuse are
forbidden.

The target configuration intentionally contains absolute paths.  A target is
observed rather than selected, and the exact resolved configuration becomes a
run input.  The scientific programs remain frozen in the source tree; this
file only removes the manual bridges between their existing create-only CLIs.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any, Mapping, NoReturn


CONFIG_SCHEMA = "rtdl.goal5802.pod_s0_config.v3"
STEP_SCHEMA = "rtdl.goal5802.pod_s0_step.v2"
PREPARED_SCHEMA = "rtdl.goal5802.pod_s0_prepared_state.v1"
FINISHED_SCHEMA = "rtdl.goal5802.pod_s0_finished_state.v1"
FAILURE_SCHEMA = "rtdl.goal5802.pod_s0_terminal_failure.v1"
TRUST_REQUEST_SCHEMA = "rtdl.goal5802.pod_s0_trust_request.v1"
TRUST_RESPONSE_SCHEMA = "rtdl.goal5802.pod_s0_signed_trust_response.v1"
TRUST_ROOT_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_root.v1"
TRUST_PACKAGE_SCHEMA = "rtdl.v4.rtdlexe.deployment_trust_package.v1"
TRUST_HEAD_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_head.v1"
TRUST_ROOT_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-ROOT-V1\x00"
TRUST_PACKAGE_DOMAIN = b"RTDL-V4-RTDLEXE-DEPLOYMENT-TRUST-PACKAGE-V1\x00"
TRUST_HEAD_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-HEAD-V1\x00"
AUTHORITY_DOMAIN = b"RTDL-V4-RTDLEXE-DETACHED-AUTHORITY-V1\x00"
RSA_DIGEST_INFO = bytes.fromhex("3031300d060960864801650304020105000420")
POSTUSE_CUSTODY_SCHEMA = (
    "rtdl.goal5802.test_trust_postuse_custody_receipt.v1")
RELATION_FAMILY = "custom_aabb_bounded_relation_v1"
TRIANGLE_FAMILY = "builtin_triangle_reduction_v1"
QUALIFICATION_ONLY_TRUST_KEY_PREFIX = (
    "TEST_ONLY_goal5802_final_home_qualification_")
FORMAL_MEASUREMENT_TRUST_KEY_ID = (
    "TEST_ONLY_goal5802_rtx_measurement_root_v5_20260826")
FORMAL_MEASUREMENT_TRUST_ROOT_FILE_SHA256 = (
    "3364f744a637e27710319001c2fa505bd6c54f75904b51429de253bcd4da8dc4")
FORMAL_MEASUREMENT_TRUST_SCOPE = "CONTROLLING_FORMAL_MEASUREMENT_ROOT"
QUALIFICATION_ONLY_TRUST_SCOPE = (
    "QUALIFICATION_ONLY__NOT_FORMAL_MEASUREMENT_ROOT")

DYNAMIC_TOKENS = {
    "${OBSERVED_CC}", "${OBSERVED_SM}",
    "${LDD_CUDA}", "${LDD_NVRTC}", "${LDD_GEOS_C}",
    "${RELATION_ARTIFACT}", "${RELATION_AUTHORITY}",
    "${RELATION_DEPLOYMENT_ID}", "${RELATION_EXECUTABLE_IDENTITY}",
    "${TRIANGLE_ARTIFACT}", "${TRIANGLE_AUTHORITY}",
    "${TRIANGLE_DEPLOYMENT_ID}", "${TRIANGLE_EXECUTABLE_IDENTITY}",
    "${TRUST_PACKAGE_SEQ1}", "${TRUST_HEAD_SEQ1}",
    "${TRUST_PACKAGE_SEQ2}", "${TRUST_HEAD_SEQ2}",
    "${TRUST_CUSTODY_RECEIPT}",
    "${COMBINED_PLAN_FILE_SHA256}",
}
NAMED_DYNAMIC_TOKENS = {
    "cuda": "${LDD_CUDA}",
    "nvrtc": "${LDD_NVRTC}",
    "geos_c": "${LDD_GEOS_C}",
}

PREPARE_STEPS = (
    "source_packet_verify",
    "pyoptix_build_provenance_materialize",
    "pyoptix_build_provenance_verify",
    "pyoptix_offline_plan",
    "pyoptix_offline_run",
    "pyoptix_offline_verify",
    "target_observation",
    "origin_authority",
    "native_build",
    "native_custody_capture",
    "native_custody_verify",
    "candidate_seed1",
    "candidate_seed777",
)

FINISH_STEPS = (
    "rtdl_wheel_double_seed",
    "rtdl_clean_install",
    "rtdl_clean_install_verify",
    "combined_runtime_plan",
    "combined_runtime_run",
    "combined_runtime_verify",
    "product_binding",
    "freeze_inputs",
    "successor_forecast",
    "local_freeze",
    "local_freeze_verify",
    "header_projection",
    "header_projection_verify",
    "direct_recipe",
    "direct_worker",
    "matched_ptx",
    "direct_kat",
    "pyoptix_kat",
    "rtdl_kat",
    "host_runtime",
    "target_runtime_manifest",
    "dual_validation",
    "plan_only",
)

# A stage may only execute this source-controlled entrypoint.  The two seed
# stages intentionally share one builder; their required PYTHONHASHSEED values
# are checked separately below.
SCRIPT_TARGETS = {
    "source_packet_verify": "scripts/goal5802_verify_exact_source_packet.py",
    "pyoptix_build_provenance_materialize": (
        "scripts/goal5802_materialize_pyoptix_build_provenance.py"),
    "pyoptix_build_provenance_verify": (
        "scripts/goal5802_materialize_pyoptix_build_provenance.py"),
    "pyoptix_offline_plan": (
        "scripts/goal5802_clean_install_pyoptix_offline.py"),
    "pyoptix_offline_run": (
        "scripts/goal5802_clean_install_pyoptix_offline.py"),
    "pyoptix_offline_verify": (
        "scripts/goal5802_clean_install_pyoptix_offline.py"),
    "target_observation": "scripts/goal5802_capture_target_untimed.py",
    "origin_authority": "scripts/goal5801_a4_export_origin_authority.py",
    "native_build": "scripts/goal5801_a4_run_native_build.py",
    "native_custody_capture": "scripts/goal5801_a3_capture_native_custody.py",
    "native_custody_verify": "scripts/goal5801_a3_verify_native_custody.py",
    "candidate_seed1": "scripts/goal5801_lx1_untimed_smoke.py",
    "candidate_seed777": "scripts/goal5801_lx1_untimed_smoke.py",
    "rtdl_wheel_double_seed": (
        "scripts/goal5802_build_rtdl_wheel_double_seed_untimed.py"),
    "rtdl_clean_install": "scripts/goal5801_a3_run_clean_install.py",
    "rtdl_clean_install_verify": "scripts/goal5801_a3_verify_clean_install.py",
    "combined_runtime_plan": "scripts/goal5802_build_combined_runtime_untimed.py",
    "combined_runtime_run": "scripts/goal5802_build_combined_runtime_untimed.py",
    "combined_runtime_verify": "scripts/goal5802_build_combined_runtime_untimed.py",
    "product_binding": "scripts/goal5802_bind_final_clean_install.py",
    "freeze_inputs": "scripts/goal5802_export_freeze_inputs_untimed.py",
    "successor_forecast": "scripts/goal5802_build_successor_forecast.py",
    "local_freeze": "scripts/goal5802_build_local_premeasurement_freeze.py",
    "local_freeze_verify": "scripts/goal5802_verify_local_premeasurement_freeze.py",
    "header_projection": "scripts/goal5802_build_header_projection_untimed.py",
    "header_projection_verify": "scripts/goal5802_verify_header_projection_untimed.py",
    "direct_recipe": "scripts/goal5802_build_direct_recipe.py",
    "direct_worker": "scripts/goal5802_build_direct_worker_untimed.py",
    "matched_ptx": "scripts/goal5802_prepare_matched_ptx_untimed.py",
    "direct_kat": "scripts/goal5802_run_direct_operation_kat_untimed.py",
    "pyoptix_kat": "scripts/goal5802_run_pyoptix_operation_kat_untimed.py",
    "rtdl_kat": "scripts/goal5802_run_rtdl_operation_kat_untimed.py",
    "host_runtime": "scripts/goal5802_capture_host_runtime_provenance.py",
    "target_runtime_manifest": "scripts/goal5802_build_target_runtime_manifest.py",
    "dual_validation": (
        "scripts/goal5802_verify_preformal_runtime_dual_untimed.py"),
}

PLAN_ONLY_MODULE = "experiments.goal5802_premeasurement.controller"
ALLOWED_ENV_OVERRIDES = {
    "CUDA_VISIBLE_DEVICES", "LANG", "LC_ALL", "LD_LIBRARY_PATH", "PATH",
    "PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ",
}
FORBIDDEN_TOKENS = {
    "--execution-authority", "execute_formal",
    "formal_worker", "registered_timing",
}


class S0Error(RuntimeError):
    """Fail-closed S0 configuration, state, or execution error."""


def _fail(message: str) -> NoReturn:
    raise S0Error(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _read_regular_file_once(path: Path, label: str) -> bytes:
    """Read one stable regular-file payload without check/reopen races."""
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    elif path.is_symlink():
        # Windows lacks O_NOFOLLOW.  Retain rejection of a stable reparse-link
        # input without claiming Linux-equivalent concurrent replacement
        # resistance on this non-target platform.
        _fail(f"{label} may not be a symlink: {path}")
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise S0Error(f"{label} cannot be opened as a regular file: {path}") \
            from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            _fail(f"{label} is not a regular file: {path}")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            raw = stream.read()
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_mode, before.st_size,
                before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_dev, after.st_ino, after.st_mode, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns) \
                or len(raw) != before.st_size:
            _fail(f"{label} changed during its single read: {path}")
        return raw
    finally:
        os.close(descriptor)


def _strict_json_bytes(raw: bytes, label: str, *,
                       canonical_required: bool) -> Any:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_no_duplicate_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise S0Error(f"{label} is not strict UTF-8 JSON") from error
    if canonical_required and raw != _canonical(value) + b"\n":
        _fail(f"{label} must be canonical JSON plus terminal LF")
    return value


def _strict_json(path: Path, label: str, *, canonical_required: bool) -> Any:
    return _strict_json_bytes(
        _read_regular_file_once(path, label), label,
        canonical_required=canonical_required)


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_constant(value: str) -> NoReturn:
    _fail(f"non-finite JSON value is forbidden: {value}")


def _write_new(path: Path, value: object) -> None:
    payload = _canonical(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _write_new_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _strict_sha(value: object, label: str, *, width: int = 64) -> str:
    if not isinstance(value, str) or len(value) != width \
            or any(character not in "0123456789abcdef" for character in value):
        _fail(f"{label} must be a lowercase {width * 4}-bit hex digest")
    return value


def _absolute_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be a nonempty absolute path string")
    path = Path(value)
    if not path.is_absolute():
        _fail(f"{label} must be absolute: {value}")
    return path


def _exact_keys(value: object, keys: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        _fail(f"{label} keys differ")
    return value


def _file_record(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        _fail(f"required regular file absent: {path}")
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": _sha_file(path),
    }


def _payload_file_record(path: Path, payload: bytes) -> dict[str, object]:
    return {
        "path": str(path.resolve(strict=True)),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _b64_integer(value: object, label: str) -> int:
    if not isinstance(value, str):
        _fail(f"{label} must be base64")
    try:
        payload = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as error:
        raise S0Error(f"{label} is not canonical base64") from error
    if not payload:
        _fail(f"{label} is empty")
    return int.from_bytes(payload, "big")


def _verify_rsa(signature_value: object, message: bytes, *, modulus: int,
                exponent: int, label: str) -> None:
    if not isinstance(signature_value, str):
        _fail(f"{label} signature is absent")
    try:
        signature = base64.b64decode(signature_value, validate=True)
    except (ValueError, TypeError) as error:
        raise S0Error(f"{label} signature is not base64") from error
    width = (modulus.bit_length() + 7) // 8
    if len(signature) != width:
        _fail(f"{label} signature width differs")
    digest_info = RSA_DIGEST_INFO + hashlib.sha256(message).digest()
    padding = width - len(digest_info) - 3
    if padding < 8:
        _fail("trust-root RSA modulus is too small")
    expected = b"\x00\x01" + b"\xff" * padding + b"\x00" + digest_info
    observed = pow(int.from_bytes(signature, "big"), exponent, modulus).to_bytes(
        width, "big")
    if observed != expected:
        _fail(f"{label} RSA signature rejected")


def _authority_entry(path: Path) -> dict[str, object]:
    authority = _strict_json(
        path, "detached candidate authority", canonical_required=True)
    expected = {
        "schema", "authority_version", "artifact_sha256", "artifact_bytes",
        "product_projection_sha256", "protocol_decision_sha256",
        "executable_identity_sha256", "native_library_sha256", "target_sha256",
        "deployment_id", "family", "task_semantics_sha256",
        "target_compute_capability", "authority_seal",
    }
    if not isinstance(authority, dict) or set(authority) != expected \
            or authority.get("schema") != "rtdl.v4.rtdlexe.detached_authority.v1" \
            or authority.get("authority_version") != 1:
        _fail("detached candidate authority envelope differs")
    body = dict(authority)
    seal = body.pop("authority_seal")
    # The authority domain is frozen in the runtime.  Retain an explicit
    # fallback check against the known schema framing only if the domain name
    # changes would otherwise make this orchestration silently accept it.
    expected_seal = hashlib.sha256(AUTHORITY_DOMAIN + _canonical(body)).hexdigest()
    if seal != expected_seal:
        _fail("detached candidate authority seal differs")
    return {
        "deployment_id": authority["deployment_id"],
        "family": authority["family"],
        "task_semantics_sha256": authority["task_semantics_sha256"],
        "authority_sha256": _sha_file(path),
        "artifact_sha256": authority["artifact_sha256"],
        "executable_identity_sha256": authority["executable_identity_sha256"],
        "target_sha256": authority["target_sha256"],
        "native_library_sha256": authority["native_library_sha256"],
        "compute_capability": authority["target_compute_capability"],
    }


def _tree_record(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_dir():
        _fail(f"required real directory absent: {path}")
    rows = []
    for item in sorted(path.rglob("*"), key=lambda row: row.as_posix()):
        if item.is_symlink():
            _fail(f"output tree contains symlink: {item}")
        if item.is_file():
            relative = item.relative_to(path).as_posix()
            rows.append({
                "path": relative,
                "bytes": item.stat().st_size,
                "sha256": _sha_file(item),
                "executable": bool(item.stat().st_mode & stat.S_IXUSR),
            })
        elif not item.is_dir():
            _fail(f"output tree contains special node: {item}")
    return {
        "path": str(path.resolve()),
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": _digest(rows),
    }


def _git(source: Path, executable: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        [str(executable), "-C", str(source), *arguments], check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        _fail(
            f"git {' '.join(arguments)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace')}")
    return completed.stdout


def _verify_source(config: Mapping[str, Any]) -> None:
    source = _absolute_path(config["source_root"], "source_root")
    git = _absolute_path(config["git"], "git")
    if source.is_symlink() or not source.is_dir():
        _fail("source root must be a real directory")
    if git.is_symlink() or not git.is_file():
        _fail("git must be a regular file")
    head = _git(source, git, "rev-parse", "HEAD").decode("ascii").strip()
    tree = _git(source, git, "rev-parse", "HEAD^{tree}").decode("ascii").strip()
    if head != config["source_commit"] or tree != config["source_tree"]:
        _fail("source HEAD/tree differs from frozen configuration")
    if _git(source, git, "status", "--porcelain=v1", "--untracked-files=all"):
        _fail("source checkout is not clean, including untracked files")
    autocrlf = _git(source, git, "config", "--get", "core.autocrlf").decode(
        "utf-8", errors="strict").strip().lower()
    if autocrlf not in {"false", "input"}:
        _fail("source checkout core.autocrlf must be false or input")


def _output_rows(raw: object, run_root: Path, label: str) \
        -> list[dict[str, str]]:
    if not isinstance(raw, list) or not raw:
        _fail(f"{label} outputs must be a nonempty list")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        row = _exact_keys(item, {"path", "kind"}, f"{label} output {index}")
        path = _absolute_path(row["path"], f"{label} output {index} path")
        try:
            path.relative_to(run_root)
        except ValueError:
            _fail(f"{label} output escapes run root: {path}")
        kind = row["kind"]
        if kind not in {"file", "directory"}:
            _fail(f"{label} output kind invalid")
        if str(path) in seen:
            _fail(f"{label} output path duplicates")
        seen.add(str(path))
        result.append({"path": str(path), "kind": str(kind)})
    return result


def _validate_step(raw: object, expected_name: str, config: Mapping[str, Any],
                   run_root: Path) -> dict[str, Any]:
    step = _exact_keys(raw, {
        "schema", "name", "runner", "target", "interpreter", "args",
        "environment", "outputs",
    }, f"step {expected_name}")
    if step["schema"] != STEP_SCHEMA or step["name"] != expected_name:
        _fail(f"step order/name differs at {expected_name}")
    runner = step["runner"]
    if runner not in {"python_script", "python_module"}:
        _fail(f"step {expected_name} runner invalid")
    target = step["target"]
    if not isinstance(target, str) or not target:
        _fail(f"step {expected_name} target invalid")
    source = _absolute_path(config["source_root"], "source_root")
    if expected_name == "plan_only":
        if runner != "python_module" or target != PLAN_ONLY_MODULE:
            _fail("plan_only must invoke the frozen controller module")
    else:
        expected_target = SCRIPT_TARGETS[expected_name]
        if runner != "python_script" or target != expected_target:
            _fail(f"step {expected_name} target differs")
        resolved_target = source / target
        if resolved_target.is_symlink() or not resolved_target.is_file():
            _fail(f"step {expected_name} target is absent: {resolved_target}")
    interpreter = step["interpreter"]
    if runner in {"python_script", "python_module"}:
        _absolute_path(interpreter, f"step {expected_name} interpreter")
    args = step["args"]
    if not isinstance(args, list) or any(
            not isinstance(item, str) or not item for item in args):
        _fail(f"step {expected_name} args invalid")
    for item in args:
        if "${" in item and item not in DYNAMIC_TOKENS:
            name, separator, token = item.partition("=")
            if not separator or NAMED_DYNAMIC_TOKENS.get(name) != token \
                    or item != f"{name}={token}":
                _fail(f"step {expected_name} contains unsupported dynamic token")
    if any(token in args for token in FORBIDDEN_TOKENS):
        _fail(f"step {expected_name} contains a formal/timing token")
    if expected_name == "plan_only":
        required = {"--freeze", "--root", "--plan-output"}
        if not required <= set(args) or {
                "--runtime-manifest", "--execution-authority",
                "--output-directory"} & set(args):
            _fail("plan_only argv is not the zero-locked controller form")
    if expected_name in {"candidate_seed1", "candidate_seed777"}:
        if not args or args[0] != "build":
            _fail(f"{expected_name} must use lx1 build, never run")
    environment = step["environment"]
    if not isinstance(environment, Mapping) \
            or any(key not in ALLOWED_ENV_OVERRIDES for key in environment) \
            or any(not isinstance(value, str) for value in environment.values()):
        _fail(f"step {expected_name} environment overrides invalid")
    expected_seed = {
        "candidate_seed1": "1", "candidate_seed777": "777",
    }.get(expected_name)
    if expected_seed is not None \
            and environment.get("PYTHONHASHSEED") != expected_seed:
        _fail(f"{expected_name} has wrong PYTHONHASHSEED")
    return {
        "schema": STEP_SCHEMA,
        "name": expected_name,
        "runner": runner,
        "target": target,
        "interpreter": interpreter,
        "args": list(args),
        "environment": dict(environment),
        "outputs": _output_rows(
            step["outputs"], run_root, f"step {expected_name}"),
    }


def _validate_config_value(raw: object, run_root: Path) -> dict[str, Any]:
    config = _exact_keys(raw, {
        "schema", "source_root", "source_commit", "source_tree", "git",
        "python", "run_root", "source_packet_manifest", "public_trust_root",
        "trust_root_scope", "trust_root_file_sha256",
        "private_key_sha256", "deployment_generation", "candidate_seeds",
        "wheel_seeds", "relation_minimum_overlap_f32", "prepare_steps",
        "finish_steps", "candidate_manifests", "final_outputs",
        "claim_boundary",
    }, "S0 configuration")
    if config["schema"] != CONFIG_SCHEMA:
        _fail("S0 configuration schema differs")
    _strict_sha(config["source_commit"], "source_commit", width=40)
    _strict_sha(config["source_tree"], "source_tree", width=40)
    _strict_sha(config["private_key_sha256"], "private_key_sha256")
    _strict_sha(config["trust_root_file_sha256"], "trust_root_file_sha256")
    if config["trust_root_scope"] not in {
            FORMAL_MEASUREMENT_TRUST_SCOPE,
            QUALIFICATION_ONLY_TRUST_SCOPE}:
        _fail("trust-root scope differs")
    if config["trust_root_scope"] == FORMAL_MEASUREMENT_TRUST_SCOPE \
            and config["trust_root_file_sha256"] \
            != FORMAL_MEASUREMENT_TRUST_ROOT_FILE_SHA256:
        _fail("formal trust-root file identity differs")
    if config["trust_root_scope"] == QUALIFICATION_ONLY_TRUST_SCOPE \
            and config["trust_root_file_sha256"] \
            == FORMAL_MEASUREMENT_TRUST_ROOT_FILE_SHA256:
        _fail("formal trust root cannot be relabelled qualification-only")
    configured_root = _absolute_path(config["run_root"], "run_root")
    if configured_root != run_root.absolute():
        _fail("CLI output root differs from frozen configuration")
    source = _absolute_path(config["source_root"], "source_root")
    try:
        run_root.relative_to(source)
    except ValueError:
        pass
    else:
        _fail("run root must be outside the source checkout")
    for label in ("git", "python"):
        path_value = _absolute_path(config[label], label)
        try:
            resolved = path_value.resolve(strict=True)
        except OSError as error:
            raise S0Error(f"configuration {label} cannot be resolved") from error
        if not resolved.is_file():
            _fail(f"configuration {label} is not a regular file")
    for label in ("source_packet_manifest", "public_trust_root"):
        path_value = _absolute_path(config[label], label)
        if path_value.is_symlink() or not path_value.is_file():
            _fail(f"configuration {label} is not a regular file")
    if _sha_file(_absolute_path(
            config["public_trust_root"], "public_trust_root")) \
            != config["trust_root_file_sha256"]:
        _fail("trust-root file identity differs")
    if config["candidate_seeds"] != [1, 777] \
            or config["wheel_seeds"] != [1, 777]:
        _fail("candidate and wheel seeds must be exactly [1,777]")
    if config["deployment_generation"] != "v3" \
            or config["relation_minimum_overlap_f32"] != 1.0:
        _fail("deployment generation or relation threshold differs")
    claim = _exact_keys(config["claim_boundary"], {
        "formal_worker_count", "registered_performance_timing_count",
        "execution_authority_consumed", "gpu_use",
        "retry_resume_replacement_allowed", "target_selection_allowed",
    }, "claim boundary")
    if claim != {
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "execution_authority_consumed": False,
        "gpu_use": "UNTIMED_TARGET_OBSERVATION_AND_OPERATION_KATS_ONLY",
        "retry_resume_replacement_allowed": False,
        "target_selection_allowed": False,
    }:
        _fail("claim boundary differs")
    raw_prepare = config["prepare_steps"]
    raw_finish = config["finish_steps"]
    if not isinstance(raw_prepare, list) or len(raw_prepare) != len(PREPARE_STEPS) \
            or not isinstance(raw_finish, list) or len(raw_finish) != len(FINISH_STEPS):
        _fail("S0 step counts differ")
    prepared = [
        _validate_step(item, name, config, run_root)
        for item, name in zip(raw_prepare, PREPARE_STEPS)
    ]
    finished = [
        _validate_step(item, name, config, run_root)
        for item, name in zip(raw_finish, FINISH_STEPS)
    ]
    manifests = _exact_keys(config["candidate_manifests"], {
        "seed1", "seed777"}, "candidate manifests")
    for name, value in manifests.items():
        path_value = _absolute_path(value, f"candidate manifest {name}")
        try:
            path_value.relative_to(run_root)
        except ValueError:
            _fail("candidate manifest path escapes run root")
    finals = _exact_keys(config["final_outputs"], {
        "freeze", "runtime_manifest", "dual_validation", "plan",
    }, "final outputs")
    for name, value in finals.items():
        path_value = _absolute_path(value, f"final output {name}")
        try:
            path_value.relative_to(run_root)
        except ValueError:
            _fail(f"final output {name} escapes run root")
    result = dict(config)
    result["prepare_steps"] = prepared
    result["finish_steps"] = finished
    result["candidate_manifests"] = dict(manifests)
    result["final_outputs"] = dict(finals)
    return result


def _load_config_with_bytes(path: Path, run_root: Path) \
        -> tuple[dict[str, Any], bytes]:
    payload = _read_regular_file_once(path, "S0 configuration")
    raw = _strict_json_bytes(
        payload, "S0 configuration", canonical_required=True)
    return _validate_config_value(raw, run_root), payload


def _load_config(path: Path, run_root: Path) -> dict[str, Any]:
    config, _ = _load_config_with_bytes(path, run_root)
    return config


def _named_step(config: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    for phase in ("prepare_steps", "finish_steps"):
        for step in config[phase]:
            if step["name"] == name:
                return step
    _fail(f"configured stage is absent: {name}")


def _single_output(config: Mapping[str, Any], name: str, kind: str) -> Path:
    rows = [
        row for row in _named_step(config, name)["outputs"]
        if row["kind"] == kind
    ]
    if len(rows) != 1:
        _fail(f"stage {name} must declare exactly one {kind} output")
    return Path(str(rows[0]["path"]))


def _ldd_context(native_build_root: Path) -> dict[str, str]:
    receipt = native_build_root / "tool_receipts" / "native_ldd.txt"
    if receipt.is_symlink() or not receipt.is_file():
        return {}
    matches: dict[str, list[Path]] = {"cuda": [], "nvrtc": [], "geos_c": []}
    patterns = {
        "cuda": re.compile(r"^libcuda\.so(?:\.|$)"),
        "nvrtc": re.compile(r"^libnvrtc\.so(?:\.|$)"),
        "geos_c": re.compile(r"^libgeos_c\.so(?:\.|$)"),
    }
    try:
        lines = receipt.read_text(encoding="utf-8").splitlines()
    except UnicodeError as error:
        raise S0Error("native ldd receipt is not UTF-8") from error
    for line in lines:
        match = re.match(r"^\s*(\S+)\s+=>\s+(\S+)\s+\(0x[0-9a-fA-F]+\)\s*$", line)
        if match is None:
            continue
        soname, raw_path = match.groups()
        for label, pattern in patterns.items():
            if pattern.match(soname):
                path = Path(raw_path)
                try:
                    resolved = path.resolve(strict=True)
                except OSError as error:
                    raise S0Error(
                        f"ldd {label} path cannot be resolved: {path}") from error
                if not resolved.is_file():
                    _fail(f"ldd {label} path is not a regular file")
                matches[label].append(resolved)
    if any(len(rows) != 1 for rows in matches.values()):
        _fail("native ldd must resolve exactly one cuda, nvrtc and geos_c input")
    return {
        "${LDD_CUDA}": str(matches["cuda"][0]),
        "${LDD_NVRTC}": str(matches["nvrtc"][0]),
        "${LDD_GEOS_C}": str(matches["geos_c"][0]),
    }


def _dynamic_context(config: Mapping[str, Any],
                     response_path: Path | None) -> dict[str, str]:
    context: dict[str, str] = {}
    observation_path = _single_output(config, "target_observation", "file")
    if observation_path.is_file() and not observation_path.is_symlink():
        observation = _strict_json(
            observation_path, "target observation", canonical_required=False)
        if not isinstance(observation, Mapping):
            _fail("target observation is not an object")
        capability = observation.get("compute_capability")
        if observation.get("schema") != "rtdl.goal5802.target_observation.v2" \
                or observation.get("status") \
                != "PASS__UNTIMED_EXACT_TARGET_OBSERVATION" \
                or observation.get("formal_worker_count") != 0 \
                or observation.get("registered_performance_timing_count") != 0 \
                or observation.get("gpu_kernel_launch_count") != 0 \
                or not isinstance(capability, str) \
                or re.fullmatch(r"[1-9][0-9]*\.[0-9]", capability) is None:
            _fail("target observation cannot supply a frozen compute capability")
        context["${OBSERVED_CC}"] = capability
        context["${OBSERVED_SM}"] = "sm_" + capability.replace(".", "")

    native_root = _single_output(config, "native_build", "directory")
    if native_root.is_dir() and not native_root.is_symlink():
        context.update(_ldd_context(native_root))

    combined_plan_path = _single_output(
        config, "combined_runtime_plan", "file")
    if combined_plan_path.is_file() and not combined_plan_path.is_symlink():
        context["${COMBINED_PLAN_FILE_SHA256}"] = _sha_file(
            combined_plan_path)

    manifest_path = Path(str(config["candidate_manifests"]["seed1"]))
    if manifest_path.is_file() and not manifest_path.is_symlink():
        manifest = _strict_json(
            manifest_path, "seed-1 candidate manifest", canonical_required=False)
        if not isinstance(manifest, Mapping):
            _fail("candidate manifest is not an object")
        candidates = manifest.get("candidates")
        if manifest.get("schema") \
                != "rtdl.goal5801.lx1_untimed_candidate_manifest.v2" \
                or manifest.get("status") \
                != "UNTRUSTED_CANDIDATES__NOT_AUTHORIZED" \
                or not isinstance(candidates, Mapping) \
                or set(candidates) != {"relation", "triangle"}:
            _fail("candidate manifest cannot supply dynamic artifact paths")
        for family in ("relation", "triangle"):
            row = candidates[family]
            if not isinstance(row, Mapping):
                _fail("candidate row is not an object")
            artifact = Path(str(row.get("artifact_path")))
            authority = Path(str(row.get("authority_path")))
            deployment = row.get("deployment_id")
            executable_identity = row.get("executable_identity_sha256")
            if artifact.is_symlink() or authority.is_symlink() \
                    or not artifact.is_file() or not authority.is_file() \
                    or not isinstance(deployment, str) or not deployment \
                    or not isinstance(executable_identity, str):
                _fail("candidate dynamic artifact/authority is absent")
            _strict_sha(
                executable_identity,
                f"candidate {family} executable identity")
            upper = family.upper()
            context[f"${{{upper}_ARTIFACT}}"] = str(artifact.resolve())
            context[f"${{{upper}_AUTHORITY}}"] = str(authority.resolve())
            context[f"${{{upper}_DEPLOYMENT_ID}}"] = deployment
            context[f"${{{upper}_EXECUTABLE_IDENTITY}}"] = executable_identity

    if response_path is not None:
        labels = {
            "package_seq1": "${TRUST_PACKAGE_SEQ1}",
            "head_seq1": "${TRUST_HEAD_SEQ1}",
            "package_seq2": "${TRUST_PACKAGE_SEQ2}",
            "head_seq2": "${TRUST_HEAD_SEQ2}",
            "custody_receipt": "${TRUST_CUSTODY_RECEIPT}",
        }
        response = _strict_json(
            response_path, "signed trust response", canonical_required=True)
        for label, token in labels.items():
            context[token] = str(
                _response_file(response_path, response[label], label).resolve())
    return context


def _expand_dynamic(value: str, context: Mapping[str, str], label: str) -> str:
    if "${" not in value:
        return value
    if value in DYNAMIC_TOKENS:
        if value not in context:
            _fail(f"{label} dynamic input is not yet materialized: {value}")
        return context[value]
    name, separator, token = value.partition("=")
    if not separator or NAMED_DYNAMIC_TOKENS.get(name) != token \
            or value != f"{name}={token}":
        _fail(f"{label} contains an unsupported or embedded dynamic token")
    if token not in context:
        _fail(f"{label} dynamic input is not yet materialized: {token}")
    return f"{name}={context[token]}"


def _controlled_site_packages(
        config: Mapping[str, Any], interpreter: Path) -> Path | None:
    """Locate only a run-root virtualenv site-packages, without processing .pth."""

    lexical = interpreter.expanduser().absolute()
    run_root = Path(str(config["run_root"])).absolute()
    try:
        lexical.relative_to(run_root)
    except ValueError:
        return None
    if os.name == "nt":
        expected_suffix = ("venv", "scripts", "python.exe")
        if tuple(part.lower() for part in lexical.parts[-3:]) \
                != tuple(part.lower() for part in expected_suffix):
            _fail("run-root interpreter is not a controlled virtualenv Python")
        site_packages = lexical.parents[1] / "Lib" / "site-packages"
    else:
        if tuple(lexical.parts[-3:]) != ("venv", "bin", "python"):
            _fail("run-root interpreter is not a controlled virtualenv Python")
        site_packages = (
            lexical.parents[1] / "lib" / "python3.12" / "site-packages")
    if site_packages.is_symlink() or not site_packages.is_dir():
        _fail("controlled virtualenv site-packages is absent or symbolic")
    return site_packages.resolve(strict=True)


def _command(step: Mapping[str, Any], config: Mapping[str, Any],
             context: Mapping[str, str]) -> list[str]:
    source = Path(str(config["source_root"]))
    arguments = [
        _expand_dynamic(str(value), context, f"step {step['name']} argv")
        for value in step["args"]
    ]
    if step["runner"] == "python_script":
        python = Path(str(step["interpreter"]))
        try:
            resolved = python.resolve(strict=True)
        except OSError as error:
            raise S0Error(
                f"step {step['name']} interpreter is absent: {python}") from error
        if not resolved.is_file() or not os.access(resolved, os.X_OK):
            _fail(f"step {step['name']} interpreter is not executable")
        target = source / str(step["target"])
        source_paths = [str(source)]
        if step["name"] in {"candidate_seed1", "candidate_seed777"}:
            source_paths.append(str(source / "src"))
        site_packages = _controlled_site_packages(config, python)
        if site_packages is not None:
            source_paths.append(str(site_packages))
        bootstrap = (
            "import runpy,sys;"
            "count=int(sys.argv[1]);"
            "roots=sys.argv[2:2+count];"
            "target=sys.argv[2+count];args=sys.argv[3+count:];"
            "sys.path[:0]=roots;"
            "sys.argv=[target,*args];"
            "runpy.run_path(target,run_name='__main__')"
        )
        return [str(python), "-I", "-S", "-B", "-P", "-c", bootstrap,
                str(len(source_paths)), *source_paths, str(target), *arguments]
    if step["runner"] == "python_module":
        python = Path(str(step["interpreter"]))
        try:
            resolved = python.resolve(strict=True)
        except OSError as error:
            raise S0Error(
                f"step {step['name']} interpreter is absent: {python}") from error
        if not resolved.is_file() or not os.access(resolved, os.X_OK):
            _fail(f"step {step['name']} interpreter is not executable")
        module_paths = [str(source)]
        site_packages = _controlled_site_packages(config, python)
        if site_packages is not None:
            module_paths.append(str(site_packages))
        bootstrap = (
            "import runpy,sys;"
            "count=int(sys.argv[1]);roots=sys.argv[2:2+count];"
            "module=sys.argv[2+count];args=sys.argv[3+count:];"
            "sys.path[:0]=roots;sys.argv=[module,*args];"
            "runpy.run_module(module,run_name='__main__',alter_sys=False)"
        )
        return [str(python), "-I", "-S", "-B", "-P", "-c", bootstrap,
                str(len(module_paths)), *module_paths,
                str(step["target"]), *arguments]
    _fail("unreachable S0 runner kind")


def _run_step(step: Mapping[str, Any], config: Mapping[str, Any],
              journal: Path, ordinal: int,
              response_path: Path | None = None) -> dict[str, Any]:
    _verify_source(config)
    outputs = step["outputs"]
    for row in outputs:
        path = Path(str(row["path"]))
        if path.exists() or path.is_symlink():
            _fail(f"step {step['name']} output already exists: {path}")
    context = _dynamic_context(config, response_path)
    command = _command(step, config, context)
    environment = dict(os.environ)
    for key in list(environment):
        if key.startswith("PYTHON"):
            environment.pop(key, None)
    environment.pop("LD_PRELOAD", None)
    environment.update({
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONSAFEPATH": "1",
    })
    environment.update(step["environment"])
    stdout_path = journal / f"{ordinal:02d}_{step['name']}.stdout.bin"
    stderr_path = journal / f"{ordinal:02d}_{step['name']}.stderr.bin"
    exit_path = journal / f"{ordinal:02d}_{step['name']}.exit_code"
    completed = subprocess.run(
        command, cwd=Path(str(config["source_root"])), env=environment,
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_path.write_bytes(completed.stdout)
    stderr_path.write_bytes(completed.stderr)
    exit_path.write_text(f"{completed.returncode}\n", encoding="ascii")
    receipt: dict[str, Any] = {
        "ordinal": ordinal,
        "name": step["name"],
        "argv": command,
        "environment_overrides": dict(step["environment"]),
        "exit_code": completed.returncode,
        "stdout": _file_record(stdout_path),
        "stderr": _file_record(stderr_path),
        "outputs": [],
        "invocation_count": 1,
        "retry_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    if completed.returncode != 0:
        receipt["status"] = "TERMINAL_FAILURE__PRESERVE_NO_REUSE"
        return receipt
    observed = []
    for row in outputs:
        path = Path(str(row["path"]))
        observed.append(
            _file_record(path) if row["kind"] == "file" else _tree_record(path))
    receipt["outputs"] = observed
    receipt["status"] = "PASS__CREATE_ONLY_UNTIMED_STEP"
    _verify_source(config)
    return receipt


def _candidate_projection(path: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    value = _strict_json(path, "candidate manifest", canonical_required=False)
    if not isinstance(value, dict) \
            or value.get("schema") != "rtdl.goal5801.lx1_untimed_candidate_manifest.v2" \
            or value.get("status") != "UNTRUSTED_CANDIDATES__NOT_AUTHORIZED" \
            or value.get("registered_timing_count") != 0:
        _fail("candidate manifest envelope differs")
    candidates = value.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != {"relation", "triangle"}:
        _fail("candidate manifest family set differs")
    projection = copy.deepcopy(value)
    projection.pop("native_path", None)
    projection.pop("proof_path", None)
    payloads: dict[str, bytes] = {}
    for family in ("relation", "triangle"):
        row = candidates[family]
        if not isinstance(row, dict):
            _fail("candidate row is not an object")
        artifact = Path(str(row.get("artifact_path")))
        authority = Path(str(row.get("authority_path")))
        if artifact.is_symlink() or authority.is_symlink() \
                or not artifact.is_file() or not authority.is_file():
            _fail("candidate artifact/authority is absent")
        artifact_bytes = artifact.read_bytes()
        authority_bytes = authority.read_bytes()
        if hashlib.sha256(artifact_bytes).hexdigest() != row.get("artifact_sha256") \
                or hashlib.sha256(authority_bytes).hexdigest() != row.get("authority_sha256"):
            _fail("candidate manifest file identity differs")
        payloads[f"{family}.artifact"] = artifact_bytes
        payloads[f"{family}.authority"] = authority_bytes
        projected = projection["candidates"][family]
        projected["artifact_path"] = f"<SEED_ROOT>/{artifact.name}"
        projected["authority_path"] = f"<SEED_ROOT>/{authority.name}"
    return projection, payloads


def _verify_double_seed(config: Mapping[str, Any]) -> dict[str, Any]:
    paths = config["candidate_manifests"]
    first_projection, first_payloads = _candidate_projection(Path(paths["seed1"]))
    second_projection, second_payloads = _candidate_projection(Path(paths["seed777"]))
    if first_projection != second_projection or first_payloads != second_payloads:
        _fail("candidate double-seed outputs are not byte/projection identical")
    return {
        "schema": "rtdl.goal5802.pod_s0_candidate_double_seed.v1",
        "status": "PASS__SEEDS_1_777_BYTE_IDENTICAL_AUTHORITIES_AND_ARTIFACTS",
        "seeds": [1, 777],
        "projection_sha256": _digest(first_projection),
        "files": {
            name: {"bytes": len(payload),
                   "sha256": hashlib.sha256(payload).hexdigest()}
            for name, payload in sorted(first_payloads.items())
        },
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }


def _trust_request(config: Mapping[str, Any], comparison: Mapping[str, Any],
                   state_path: Path) -> dict[str, Any]:
    manifest = _strict_json(
        Path(config["candidate_manifests"]["seed1"]),
        "seed-1 candidate manifest", canonical_required=False)
    candidates = manifest["candidates"]
    root = Path(str(config["public_trust_root"]))
    value: dict[str, Any] = {
        "schema": TRUST_REQUEST_SCHEMA,
        "status": "PREPARED__OFFLINE_TEST_ONLY_SIGNING_REQUIRED",
        "prepared_state": _file_record(state_path),
        "source_commit": config["source_commit"],
        "source_tree": config["source_tree"],
        "public_trust_root": _file_record(root),
        "private_key_sha256": config["private_key_sha256"],
        "sequence_1": {
            "family": "relation",
            "authority": _file_record(Path(candidates["relation"]["authority_path"])),
            "previous_package_sha256": None,
        },
        "sequence_2": {
            "family": "triangle",
            "authority": _file_record(Path(candidates["triangle"]["authority_path"])),
            "previous_sequence": 1,
        },
        "candidate_double_seed_sha256": _digest(comparison),
        "required_package_signatures": 2,
        "required_head_signatures": 2,
        "private_key_must_never_enter_pod": True,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "execution_authority_consumed": False,
    }
    value["request_sha256"] = _digest(value)
    return value


def _terminal(run_root: Path, phase: str, completed: list[dict[str, Any]],
              error: BaseException) -> None:
    failure = {
        "schema": FAILURE_SCHEMA,
        "status": "TERMINAL_FAILURE__NO_RETRY_RESUME_REPLACEMENT_OR_ROOT_REUSE",
        "phase": phase,
        "completed_steps": completed,
        "failed_reason_type": type(error).__name__,
        "failed_reason": str(error),
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "execution_authority_consumed": False,
    }
    failure["failure_sha256"] = _digest(failure)
    try:
        _write_new(run_root / f"{phase}_terminal_failure.json", failure)
    except FileExistsError:
        pass


def prepare(config_path: Path, run_root: Path) -> dict[str, Any]:
    absolute_root = run_root.absolute()
    if absolute_root.exists() or absolute_root.is_symlink():
        raise FileExistsError(absolute_root)
    config, config_payload = _load_config_with_bytes(config_path, absolute_root)
    absolute_root.mkdir(parents=True)
    journal = absolute_root / "prepare_journal"
    journal.mkdir()
    config_copy = absolute_root / "s0_config.json"
    _write_new_bytes(config_copy, config_payload)
    completed: list[dict[str, Any]] = []
    try:
        _verify_source(config)
        for ordinal, step in enumerate(config["prepare_steps"], 1):
            receipt = _run_step(step, config, journal, ordinal)
            completed.append(receipt)
            _write_new(
                journal / f"{ordinal:02d}_{step['name']}.receipt.json", receipt)
            if receipt["status"] != "PASS__CREATE_ONLY_UNTIMED_STEP":
                _fail(f"prepare step failed: {step['name']}")
        comparison = _verify_double_seed(config)
        _write_new(absolute_root / "candidate_double_seed.json", comparison)
        state: dict[str, Any] = {
            "schema": PREPARED_SCHEMA,
            "status": "PASS__TARGET_PREPARED__OFFLINE_SIGNING_CHECKPOINT",
            "config": _payload_file_record(config_copy, config_payload),
            "source_commit": config["source_commit"],
            "source_tree": config["source_tree"],
            "source_packet_manifest": _file_record(
                Path(str(config["source_packet_manifest"]))),
            "public_trust_root": _file_record(
                Path(str(config["public_trust_root"]))),
            "private_key_sha256": config["private_key_sha256"],
            "completed_steps": completed,
            "candidate_double_seed": comparison,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "execution_authority_consumed": False,
            "offline_checkpoint_is_predeclared_not_retry": True,
        }
        state["state_sha256"] = _digest(state)
        state_path = absolute_root / "prepared_state.json"
        _write_new(state_path, state)
        request = _trust_request(config, comparison, state_path)
        _write_new(absolute_root / "trust_signing_request.json", request)
        return state
    except BaseException as error:
        _terminal(absolute_root, "prepare", completed, error)
        raise


def _validate_prepared_state(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    state = _strict_json(path, "prepared state", canonical_required=True)
    if not isinstance(state, dict) or state.get("schema") != PREPARED_SCHEMA \
            or state.get("status") \
            != "PASS__TARGET_PREPARED__OFFLINE_SIGNING_CHECKPOINT":
        _fail("prepared state envelope differs")
    seal = state.get("state_sha256")
    body = dict(state)
    body.pop("state_sha256", None)
    if seal != _digest(body) or state.get("formal_worker_count") != 0 \
            or state.get("registered_performance_timing_count") != 0 \
            or state.get("execution_authority_consumed") is not False:
        _fail("prepared state seal/zero lock differs")
    config_record = state.get("config")
    if not isinstance(config_record, dict):
        _fail("prepared state config record absent")
    config_path = Path(str(config_record.get("path")))
    config_payload = _read_regular_file_once(
        config_path, "prepared-state S0 configuration")
    if _payload_file_record(config_path, config_payload) != config_record:
        _fail("prepared state config bytes changed")
    config_value = _strict_json_bytes(
        config_payload, "prepared-state S0 configuration",
        canonical_required=True)
    config = _validate_config_value(config_value, path.parent.absolute())
    _verify_source(config)
    return state, config


def _response_file(response_path: Path, record: object, label: str) -> Path:
    row = _exact_keys(record, {"path", "bytes", "sha256"}, label)
    relative = row["path"]
    if not isinstance(relative, str) or not relative or "\\" in relative:
        _fail(f"{label} response path invalid")
    pure = Path(relative)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        _fail(f"{label} response path escapes response root")
    path = response_path.parent.joinpath(*pure.parts)
    observed = _file_record(path)
    if observed["bytes"] != row["bytes"] or observed["sha256"] != row["sha256"]:
        _fail(f"{label} response bytes differ")
    return path


def _verify_signed_trust_chain(response: Mapping[str, Any],
                               response_path: Path,
                               config: Mapping[str, Any]) -> Mapping[str, Any]:
    root_path = Path(str(config["public_trust_root"]))
    root = _strict_json(root_path, "public trust root", canonical_required=True)
    root = dict(_exact_keys(root, {
        "schema", "key_id", "rsa_modulus_base64", "rsa_exponent",
        "trust_root_sha256",
    }, "public trust root"))
    if root["schema"] != TRUST_ROOT_SCHEMA or type(root["rsa_exponent"]) is not int:
        _fail("public trust root envelope differs")
    root_body = dict(root)
    root_seal = root_body.pop("trust_root_sha256")
    if root_seal != hashlib.sha256(
            TRUST_ROOT_DOMAIN + _canonical(root_body)).hexdigest():
        _fail("public trust root seal differs")
    modulus = _b64_integer(root["rsa_modulus_base64"], "trust root modulus")
    exponent = int(root["rsa_exponent"])
    # A conventional 2048-bit RSA key may have a 2047-bit product even when
    # both generated primes have their top bit set.  Reject anything below
    # that exact boundary; do not accidentally reject a valid generated root.
    if modulus.bit_length() < 2047 or exponent != 65537:
        _fail("public trust root RSA parameters differ")

    manifests = config["candidate_manifests"]
    manifest = _strict_json(
        Path(str(manifests["seed1"])), "candidate manifest",
        canonical_required=False)
    expected_entries = {}
    for family in ("relation", "triangle"):
        candidate = manifest["candidates"][family]
        entry = _authority_entry(Path(str(candidate["authority_path"])))
        expected_family = {
            "relation": RELATION_FAMILY,
            "triangle": TRIANGLE_FAMILY,
        }[family]
        if entry["family"] != expected_family:
            _fail("candidate family/authority differs")
        expected_entries[family] = entry

    packages: list[tuple[dict[str, Any], Path]] = []
    for sequence in (1, 2):
        label = f"package_seq{sequence}"
        path = _response_file(response_path, response[label], label)
        package = _strict_json(path, label, canonical_required=True)
        package = dict(_exact_keys(package, {
            "schema", "key_id", "sequence", "previous_package_sha256",
            "authorities", "signature_algorithm", "signature_base64",
        }, label))
        if package["schema"] != TRUST_PACKAGE_SCHEMA \
                or package["key_id"] != root["key_id"] \
                or package["sequence"] != sequence \
                or package["signature_algorithm"] != "rsa-pkcs1-v1_5-sha256":
            _fail(f"{label} envelope differs")
        signed = dict(package)
        signature = signed.pop("signature_base64")
        _verify_rsa(
            signature, TRUST_PACKAGE_DOMAIN + _canonical(signed),
            modulus=modulus, exponent=exponent, label=label)
        packages.append((package, path))
    package1, package1_path = packages[0]
    package2, package2_path = packages[1]
    if package1["previous_package_sha256"] is not None \
            or package2["previous_package_sha256"] != _sha_file(package1_path):
        _fail("trust package predecessor chain differs")
    expected_seq1 = [expected_entries["relation"]]
    expected_seq2 = sorted(
        expected_entries.values(), key=lambda row: str(row["deployment_id"]))
    if package1["authorities"] != expected_seq1 \
            or package2["authorities"] != expected_seq2:
        _fail("trust package authority set/order differs")

    for sequence, package_path in ((1, package1_path), (2, package2_path)):
        label = f"head_seq{sequence}"
        head = _strict_json(
            _response_file(response_path, response[label], label), label,
            canonical_required=True)
        head = dict(_exact_keys(head, {
            "schema", "key_id", "current_package_sha256", "current_sequence",
            "signature_algorithm", "signature_base64",
        }, label))
        if head["schema"] != TRUST_HEAD_SCHEMA \
                or head["key_id"] != root["key_id"] \
                or head["current_package_sha256"] != _sha_file(package_path) \
                or head["current_sequence"] != sequence \
                or head["signature_algorithm"] != "rsa-pkcs1-v1_5-sha256":
            _fail(f"{label} package binding differs")
        signed_head = dict(head)
        head_signature = signed_head.pop("signature_base64")
        _verify_rsa(
            head_signature, TRUST_HEAD_DOMAIN + _canonical(signed_head),
            modulus=modulus, exponent=exponent, label=label)
    return root


def _expected_postuse_custody_counters(
        verified_root: Mapping[str, Any]) -> dict[str, object]:
    key_id = str(verified_root.get("key_id", ""))
    qualification_only = key_id.startswith(QUALIFICATION_ONLY_TRUST_KEY_PREFIX)
    diagnostic_minimum = 0 \
        if key_id == FORMAL_MEASUREMENT_TRUST_KEY_ID else 2
    return {
        "diagnostic_keypair_signing_invocation_known_minimum":
            diagnostic_minimum,
        "diagnostic_keypair_signing_invocation_count_exactly_attested":
            qualification_only,
        "diagnostic_keypair_signing_invocation_exact_count":
            2 if qualification_only else None,
        "trust_package_signing_invocation_count": 2,
        "trust_head_signing_invocation_count": 2,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "untimed_gpu_kernel_launch_count": 0,
        "trust_package_signing_invocations_without_preserved_package": 0,
        "trust_head_signing_invocations_without_preserved_head": 0,
    }


def _validate_custody_receipt(response: Mapping[str, Any],
                              response_path: Path,
                              config: Mapping[str, Any],
                              verified_root: Mapping[str, Any]) -> None:
    custody_path = _response_file(
        response_path, response["custody_receipt"], "custody_receipt")
    custody = _strict_json(
        custody_path, "post-use trust custody receipt", canonical_required=True)
    expected_keys = {
        "schema", "status", "observed_at_utc_owner_supplied",
        "observation_host_label_owner_supplied", "preuse_custody_receipt",
        "public_root", "materialized_trust_chain",
        "explicit_actual_counters", "private_key_observation",
        "claim_boundaries", "clock_read_count_by_helper", "create_only",
        "receipt_sha256",
    }
    custody = dict(_exact_keys(
        custody, expected_keys, "post-use trust custody receipt"))
    custody_seal = custody.pop("receipt_sha256")
    if custody_seal != _digest(custody):
        _fail("post-use trust custody receipt seal differs")
    if custody["schema"] != POSTUSE_CUSTODY_SCHEMA \
            or custody["status"] \
            != "TEST_ONLY_POSTUSE_CUSTODY_SNAPSHOT__SIGNED_CHAIN_VERIFIED" \
            or custody["clock_read_count_by_helper"] != 0 \
            or custody["create_only"] is not True:
        _fail("post-use trust custody receipt envelope differs")

    public = custody["public_root"]
    if not isinstance(public, Mapping) \
            or public.get("sha256") != _sha_file(
                Path(str(config["public_trust_root"]))) \
            or public.get("role") != "public_root":
        _fail("post-use custody public-root binding differs")

    chain = custody["materialized_trust_chain"]
    if not isinstance(chain, Mapping):
        _fail("post-use custody materialized chain is absent")
    packages = chain.get("packages")
    heads = chain.get("heads")
    if not isinstance(packages, list) or not isinstance(heads, list) \
            or len(packages) != 2 or len(heads) != 2 \
            or chain.get("materialized_sequence_count") != 2 \
            or chain.get("all_signatures_verified_against_public_root") is not True:
        _fail("post-use custody must preserve exactly two signed sequences")
    expected_package_shas = [
        _sha_file(_response_file(
            response_path, response[f"package_seq{sequence}"],
            f"package_seq{sequence}"))
        for sequence in (1, 2)
    ]
    expected_head_shas = [
        _sha_file(_response_file(
            response_path, response[f"head_seq{sequence}"],
            f"head_seq{sequence}"))
        for sequence in (1, 2)
    ]
    if [row.get("sha256") for row in packages if isinstance(row, Mapping)] \
            != expected_package_shas \
            or [row.get("sha256") for row in heads if isinstance(row, Mapping)] \
            != expected_head_shas \
            or [row.get("sequence") for row in packages
                if isinstance(row, Mapping)] != [1, 2] \
            or [row.get("current_sequence") for row in heads
                if isinstance(row, Mapping)] != [1, 2] \
            or [row.get("authority_count") for row in packages
                if isinstance(row, Mapping)] != [1, 2]:
        _fail("post-use custody package/head identity chain differs")

    manifest = _strict_json(
        Path(str(config["candidate_manifests"]["seed1"])),
        "candidate manifest for custody", canonical_required=False)
    expected_deployments = sorted(
        str(manifest["candidates"][family]["deployment_id"])
        for family in ("relation", "triangle"))
    if chain.get("final_deployment_ids") != expected_deployments:
        _fail("post-use custody final deployment set differs")

    counters = custody["explicit_actual_counters"]
    if not isinstance(counters, Mapping) or dict(counters) \
            != _expected_postuse_custody_counters(verified_root):
        _fail("post-use custody exact counters differ")
    qualification_only = str(verified_root.get("key_id", "")).startswith(
        QUALIFICATION_ONLY_TRUST_KEY_PREFIX)
    integer_counter_keys = {
        "diagnostic_keypair_signing_invocation_known_minimum",
        "trust_package_signing_invocation_count",
        "trust_head_signing_invocation_count", "formal_worker_count",
        "registered_performance_timing_count",
        "untimed_gpu_kernel_launch_count",
        "trust_package_signing_invocations_without_preserved_package",
        "trust_head_signing_invocations_without_preserved_head",
    }
    if any(type(counters[key]) is not int for key in integer_counter_keys) \
            or type(counters[
                "diagnostic_keypair_signing_invocation_count_exactly_attested"]) \
            is not bool \
            or (qualification_only and type(counters[
                "diagnostic_keypair_signing_invocation_exact_count"]) is not int) \
            or (not qualification_only and counters[
                "diagnostic_keypair_signing_invocation_exact_count"] is not None):
        _fail("post-use custody counter scalar types differ")

    private = custody["private_key_observation"]
    if not isinstance(private, Mapping) \
            or private.get("observed_state") \
            != "PRESENT_RETAINED_OUTSIDE_REPOSITORY" \
            or private.get("regular_file_observed") is not True \
            or private.get("sha256") != config["private_key_sha256"] \
            or private.get("copied_or_embedded_in_receipt") is not False:
        _fail("post-use custody retained-private-key observation differs")
    claims = custody["claim_boundaries"]
    if not isinstance(claims, Mapping) or dict(claims) != {
        "test_only_not_production_key": True,
        "private_key_committed_or_embedded": False,
        "private_key_erasure_attested": False,
        "private_key_nonrecoverability_attested": False,
        "global_private_key_absence_attested": False,
        "absence_at_declared_path_is_not_erasure": True,
        "future_state_not_claimed": True,
        "receipt_is_snapshot_not_continuous_monitoring": True,
        "execution_authority_consumed": False,
        "performance_claim_authorized": False,
    }:
        _fail("post-use custody claim boundary differs")


def _validate_response(response_path: Path, request_path: Path,
                       config: Mapping[str, Any]) -> dict[str, Any]:
    response = _strict_json(
        response_path, "signed trust response", canonical_required=True)
    response = dict(_exact_keys(response, {
        "schema", "status", "request_sha256", "public_trust_root_sha256",
        "package_seq1", "head_seq1", "package_seq2", "head_seq2",
        "custody_receipt", "private_key_sha256", "response_sha256",
    }, "signed trust response"))
    seal = response.pop("response_sha256")
    if seal != _digest(response):
        _fail("signed trust response seal differs")
    if response["schema"] != TRUST_RESPONSE_SCHEMA \
            or response["status"] \
            != "PASS__EXACT_TWO_SEQUENCE_TEST_ONLY_TRUST_RESPONSE":
        _fail("signed trust response envelope differs")
    request = _strict_json(
        request_path, "trust signing request", canonical_required=True)
    if response["request_sha256"] != request.get("request_sha256") \
            or response["private_key_sha256"] != config["private_key_sha256"] \
            or response["public_trust_root_sha256"] != _sha_file(
                Path(str(config["public_trust_root"]))):
        _fail("signed trust response request/root/key binding differs")
    for label in ("package_seq1", "head_seq1", "package_seq2", "head_seq2",
                  "custody_receipt"):
        _response_file(response_path, response[label], label)
    response["response_sha256"] = seal
    verified_root = _verify_signed_trust_chain(
        response, response_path, config)
    _validate_custody_receipt(
        response, response_path, config, verified_root)
    return response


def _validate_final_outputs(config: Mapping[str, Any]) -> dict[str, object]:
    paths = {name: Path(value) for name, value in config["final_outputs"].items()}
    values = {
        name: _strict_json(path, f"final {name}", canonical_required=False)
        for name, path in paths.items()
    }
    plan = values["plan"]
    if not isinstance(plan, dict) \
            or plan.get("status") \
            != "PASS__LOCAL_PLAN_ONLY__FORMAL_WORKER_ZERO_LOCKED" \
            or plan.get("formal_worker_zero") is not False \
            or plan.get("legacy_goal5798_worker_allowed") is not False \
            or type(plan.get("registered_performance_timing_count")) is not int \
            or plan["registered_performance_timing_count"] != 0 \
            or type(plan.get("worker_row_count")) is not int \
            or plan["worker_row_count"] != 432 \
            or type(plan.get("build_cold_absolute_worker_row_count")) is not int \
            or plan["build_cold_absolute_worker_row_count"] != 72:
        _fail("final plan-only zero lock/counts differ")
    for name in ("freeze", "runtime_manifest", "dual_validation"):
        value = values[name]
        if not isinstance(value, dict) \
                or value.get("registered_performance_timing_count") != 0:
            _fail(f"final {name} registered timing zero lock differs")
    dual = values["dual_validation"]
    if dual.get("formal_worker_count") != 0 \
            or dual.get("execution_authority_consumed") is not False:
        _fail("dual validation worker/authority zero lock differs")
    return {name: _file_record(path) for name, path in paths.items()}


def finish(state_path: Path, response_path: Path) -> dict[str, Any]:
    state, config = _validate_prepared_state(state_path)
    run_root = state_path.parent.absolute()
    if (run_root / "finish_started.json").exists() \
            or (run_root / "finished_state.json").exists() \
            or (run_root / "finish_terminal_failure.json").exists():
        _fail("finish phase was already started; retry/root reuse forbidden")
    request_path = run_root / "trust_signing_request.json"
    response = _validate_response(response_path, request_path, config)
    start = {
        "schema": "rtdl.goal5802.pod_s0_finish_start.v1",
        "status": "STARTED_ONCE__NO_RETRY_RESUME_REPLACEMENT",
        "prepared_state": _file_record(state_path),
        "signed_trust_response": _file_record(response_path),
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "execution_authority_consumed": False,
    }
    start["start_sha256"] = _digest(start)
    _write_new(run_root / "finish_started.json", start)
    journal = run_root / "finish_journal"
    journal.mkdir()
    completed: list[dict[str, Any]] = []
    try:
        for ordinal, step in enumerate(config["finish_steps"], 1):
            receipt = _run_step(
                step, config, journal, ordinal, response_path=response_path)
            completed.append(receipt)
            _write_new(
                journal / f"{ordinal:02d}_{step['name']}.receipt.json", receipt)
            if receipt["status"] != "PASS__CREATE_ONLY_UNTIMED_STEP":
                _fail(f"finish step failed: {step['name']}")
        final_outputs = _validate_final_outputs(config)
        result: dict[str, Any] = {
            "schema": FINISHED_SCHEMA,
            "status": "PASS__POD_S0_UNTIMED_COMPLETE__EXTERNAL_REVIEW_REQUIRED",
            "prepared_state": _file_record(state_path),
            "signed_trust_response": _file_record(response_path),
            "trust_response_sha256": response["response_sha256"],
            "completed_steps": completed,
            "final_outputs": final_outputs,
            "comparative_planned_rows": 432,
            "build_cold_absolute_planned_rows": 72,
            "executed_row_count": 0,
            "result_row_count": 0,
            "raw_row_count": 0,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "execution_authority_consumed": False,
            "external_review_p0_p1_zero_required_before_worker_zero": True,
            "owner_execution_authority_required_after_external_review": True,
            "live_worker_zero_preflight_still_required": True,
        }
        result["state_sha256"] = _digest(result)
        _write_new(run_root / "finished_state.json", result)
        return result
    except BaseException as error:
        _terminal(run_root, "finish", completed, error)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run create-only untimed Goal5802 POD S0; never formal work")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare-target")
    prepare_parser.add_argument("--config", type=Path, required=True)
    prepare_parser.add_argument("--output-root", type=Path, required=True)
    finish_parser = commands.add_parser("finish-target")
    finish_parser.add_argument("--state", type=Path, required=True)
    finish_parser.add_argument(
        "--signed-trust-response", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "prepare-target":
        value = prepare(args.config, args.output_root)
    else:
        value = finish(args.state, args.signed_trust_response)
    print(json.dumps({
        "status": value["status"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "execution_authority_consumed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
