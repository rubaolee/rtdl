#!/usr/bin/env python3
"""Untimed, idiomatic current-source PyOptiX functional arm for Goal5800.

This successor exists to close the asymmetric result-materialization defect in
Goal5798 v11 before any future timing design is frozen.  It deliberately has
no clock, timer, repetition schedule, or performance field.  Device results
cross into Python through bulk ``ndarray.tolist()`` conversion; there is no
per-element Python ``int`` loop in the launch/output path.

The device source and low-level public PyOptiX construction remain the frozen
Goal5796 implementation.  This file changes the prepared host lifecycle,
transport, and result materialization; it does not change a device program.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Any
import zipfile


ARM = "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API__IDIOMATIC_BULK"
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
OPTIX_HEADERS_COMMIT = "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd"
OPTIX_HEADERS_TREE = "c30f1b41cb64f6cba6290d7ad82686cc84922267"
RAW_RELATION_CAPACITY = 8194
EXECUTED_SOURCE_PATHS = (
    "experiments/goal5796_matched/matched_device.cu",
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5798_premeasurement/workload.py",
    "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py",
)
OPERATION_LEDGER_SCOPE = (
    "TASK_OWNER_CONSTRUCTION_AND_EXECUTE__SOURCE_OBSERVABLE_WRAPPERS__"
    "EXCLUDES_CONTEXT_PIPELINE_SBT_AND_DRIVER_INTERNALS"
)


def _attribute_path(node: ast.AST) -> str | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def validate_execute_source_boundary(source: Path) -> dict[str, Any]:
    """Reject direct GPU/transfer/sync calls outside the reviewed wrappers.

    This is a source-level boundary over the two task-owner execute bodies. It
    complements the live allocator/asnumpy/direct-stream-sync observer in
    ``PreparedLaunch``; neither mechanism is represented as a driver-wide
    trace of CUDA library internals.
    """
    raw = source.read_bytes()
    tree = ast.parse(raw, filename=str(source))
    classes = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }
    required = {
        "RelationPrepared": {
            "zero_on_stream": 1, "enqueue": 1,
            "enqueue_d2h": 2, "synchronize": 2,
        },
        "TrianglePrepared": {
            "zero_on_stream": 1, "enqueue": 1,
            "enqueue_d2h": 3, "synchronize": 2,
        },
    }
    complete_call_shapes = {
        "RelationPrepared": {
            "<dynamic>.reshape": 1, "<dynamic>.tolist": 1,
            "DeviceStatusFailure": 1, "RuntimeError": 3,
            "b.operation_count_delta": 2, "dict": 2, "enumerate": 1,
            "exact_counts": 1, "int": 8, "len": 1, "list": 3,
            "map": 1, "require_execution_contract": 1,
            "self.launcher.enqueue": 1, "self.launcher.enqueue_d2h": 2,
            "self.launcher.synchronize": 2,
            "self.launcher.zero_on_stream": 1, "set": 1, "sorted": 1,
        },
        "TrianglePrepared": {
            "RuntimeError": 3, "b.operation_count_delta": 1, "dict": 2,
            "exact_counts": 1, "int": 8, "len": 1, "list": 1,
            "require_execution_contract": 1,
            "self.h_per_ray.tolist": 1, "self.launcher.enqueue": 1,
            "self.launcher.enqueue_d2h": 3,
            "self.launcher.synchronize": 2,
            "self.launcher.zero_on_stream": 1,
        },
    }
    receipts = []
    for class_name, expected_launcher_calls in required.items():
        class_node = classes.get(class_name)
        if class_node is None:
            raise RuntimeError(f"source boundary class absent: {class_name}")
        matches = [
            node for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "_execute_observed"
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"source boundary execute body absent/ambiguous: {class_name}")
        function = matches[0]
        launcher_calls: dict[str, int] = {}
        all_calls: dict[str, int] = {}
        forbidden: list[str] = []
        for node in ast.walk(function):
            if isinstance(node, ast.Attribute):
                path = _attribute_path(node)
                if path == "self.launcher.stream" \
                        or (path is not None and path.startswith(
                            "self.launcher.stream.")):
                    forbidden.append(path)
            if not isinstance(node, ast.Call):
                continue
            path = _attribute_path(node.func)
            call_key = path if path is not None else (
                f"<dynamic>.{node.func.attr}"
                if isinstance(node.func, ast.Attribute) else "<dynamic>"
            )
            all_calls[call_key] = all_calls.get(call_key, 0) + 1
            if isinstance(node.func, ast.Name) and node.func.id in {
                    "eval", "exec", "getattr", "setattr", "__import__"}:
                forbidden.append(node.func.id)
            if path is None:
                continue
            if path.startswith(("b.cp.", "b.optix.", "cp.", "cuda.",
                                "optix.", "self.d_")):
                forbidden.append(path)
            if path.startswith("self.launcher."):
                method = path.removeprefix("self.launcher.")
                launcher_calls[method] = launcher_calls.get(method, 0) + 1
        if forbidden:
            raise RuntimeError({
                "direct_execute_operation_forbidden": sorted(forbidden),
                "class": class_name,
            })
        if launcher_calls != expected_launcher_calls:
            raise RuntimeError({
                "execute_wrapper_call_shape_mismatch": launcher_calls,
                "expected": expected_launcher_calls,
                "class": class_name,
            })
        if all_calls != complete_call_shapes[class_name]:
            raise RuntimeError({
                "execute_complete_call_shape_mismatch": all_calls,
                "expected": complete_call_shapes[class_name],
                "class": class_name,
            })
        ast_bytes = ast.dump(function, include_attributes=False).encode("utf-8")
        receipts.append({
            "class": class_name,
            "method": "_execute_observed",
            "ast_sha256": sha256_bytes(ast_bytes),
            "wrapper_call_shape": launcher_calls,
            "complete_call_shape": all_calls,
        })
    return {
        "schema": "rtdl.goal5800.pyoptix_execute_source_boundary.v1",
        "source_sha256": sha256_bytes(raw),
        "checked_methods": receipts,
        "direct_gpu_calls_allowed": False,
        "dynamic_call_escape_allowed": False,
        "complete_driver_operation_observation_claimed": False,
    }


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return sha256_bytes(canonical(value))


def _no_duplicate_json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RuntimeError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json_object(value: bytes, label: str) -> dict[str, Any]:
    try:
        document = json.loads(
            value.decode("utf-8"), object_pairs_hook=_no_duplicate_json_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON value: {token}")),
        )
    except (UnicodeDecodeError, ValueError) as error:
        raise RuntimeError(f"invalid {label} JSON") from error
    if type(document) is not dict:
        raise RuntimeError(f"{label} must be a JSON object")
    return document


def _git_object_id(kind: str, value: bytes) -> str:
    return hashlib.sha1(f"{kind} {len(value)}\0".encode("ascii") + value).hexdigest()


def _decode_git_object(row: Any, *, kind: str, label: str) -> bytes:
    if type(row) is not dict or set(row) != {"object_id", "bytes", "base64"}:
        raise RuntimeError(f"{label} Git object row malformed")
    object_id = row["object_id"]
    if type(object_id) is not str or len(object_id) != 40 or any(
            character not in "0123456789abcdef" for character in object_id):
        raise RuntimeError(f"{label} Git object id malformed")
    encoded = row["base64"]
    if type(encoded) is not str or len(encoded) > 8_000_000:
        raise RuntimeError(f"{label} Git object base64 malformed")
    try:
        value = base64.b64decode(encoded, validate=True)
    except Exception as error:
        raise RuntimeError(f"{label} Git object base64 invalid") from error
    if base64.b64encode(value).decode("ascii") != encoded:
        raise RuntimeError(f"{label} Git object base64 is noncanonical")
    if type(row["bytes"]) is not int or type(row["bytes"]) is bool \
            or row["bytes"] != len(value):
        raise RuntimeError(f"{label} Git object byte count mismatch")
    if _git_object_id(kind, value) != object_id:
        raise RuntimeError(f"{label} Git object hash mismatch")
    return value


def _parse_raw_git_tree(value: bytes) -> list[dict[str, str]]:
    rows = []
    cursor = 0
    while cursor < len(value):
        space = value.find(b" ", cursor)
        nul = value.find(b"\0", space + 1)
        if space <= cursor or nul < 0 or nul + 21 > len(value):
            raise RuntimeError("malformed raw Git tree object")
        mode = value[cursor:space].decode("ascii", errors="strict")
        name = value[space + 1:nul].decode("utf-8", errors="strict")
        object_id = value[nul + 1:nul + 21].hex()
        if (not name or name in {".", ".."} or "/" in name or "\\" in name
                or mode not in {"40000", "100644"}):
            raise RuntimeError("unsafe or unsupported Git tree entry")
        rows.append({"mode": mode, "name": name, "object_id": object_id})
        cursor = nul + 21
    if len({row["name"] for row in rows}) != len(rows):
        raise RuntimeError("duplicate raw Git tree entry")
    return rows


def _required_git_directories() -> list[str]:
    directories = {""}
    for relative in EXECUTED_SOURCE_PATHS:
        parts = relative.split("/")
        for count in range(1, len(parts)):
            directories.add("/".join(parts[:count]))
    return sorted(
        directories, key=lambda value: (value.count("/") + bool(value), value))


def _read_regular_source(root: Path, relative: str) -> bytes:
    parts = relative.split("/")
    if (not relative or relative.startswith(("/", "./")) or ".." in parts
            or "" in parts or any("\\" in part for part in parts)):
        raise RuntimeError(f"unsafe executed source path: {relative}")
    candidate = root
    for part in parts:
        candidate = candidate / part
        metadata = candidate.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise RuntimeError(f"executed source path traverses a symlink: {relative}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(candidate, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"executed source is not a regular file: {relative}")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def verify_git_membership_proof(
        document: dict[str, Any], root: Path,
        rows: list[dict[str, Any]]) -> None:
    proof = document["git_membership_proof"]
    if type(proof) is not dict or set(proof) != {
            "object_format", "commit_object", "tree_nodes",
            "all_required_files_exact_origin_blobs"} \
            or proof["object_format"] != "sha1" \
            or proof["all_required_files_exact_origin_blobs"] is not True:
        raise RuntimeError("invalid Git membership proof envelope")
    commit_body = _decode_git_object(
        proof["commit_object"], kind="commit", label="origin commit")
    if proof["commit_object"]["object_id"] != document["origin_repository_commit"]:
        raise RuntimeError("Git commit proof differs from declared origin commit")
    header = commit_body.split(b"\n\n", 1)[0].splitlines()
    trees = [line[5:].decode("ascii", errors="strict")
             for line in header if line.startswith(b"tree ")]
    if trees != [document["origin_repository_tree"]]:
        raise RuntimeError("Git commit does not uniquely bind the declared root tree")
    nodes = proof["tree_nodes"]
    expected_directories = _required_git_directories()
    if type(nodes) is not list or [node.get("path") for node in nodes
                                   if type(node) is dict] != expected_directories:
        raise RuntimeError("Git tree proof is incomplete, noncanonical, or has unused nodes")
    entries_by_path: dict[str, list[dict[str, str]]] = {}
    object_by_path: dict[str, str] = {}
    for node in nodes:
        if type(node) is not dict or set(node) != {"path", "object_id", "bytes", "base64"}:
            raise RuntimeError("Git tree proof node malformed")
        value = _decode_git_object(
            {key: node[key] for key in ("object_id", "bytes", "base64")},
            kind="tree", label=f"tree {node['path']!r}")
        entries_by_path[node["path"]] = _parse_raw_git_tree(value)
        object_by_path[node["path"]] = node["object_id"]
    if object_by_path[""] != document["origin_repository_tree"]:
        raise RuntimeError("Git root proof differs from origin tree")
    for directory in expected_directories[1:]:
        parent, _, leaf = directory.rpartition("/")
        matches = [row for row in entries_by_path[parent]
                   if row["name"] == leaf and row["mode"] == "40000"]
        if len(matches) != 1 or matches[0]["object_id"] != object_by_path[directory]:
            raise RuntimeError(f"Git directory membership mismatch: {directory}")
    for row in rows:
        relative = row["path"]
        value = _read_regular_source(root, relative)
        if (len(value) != row["bytes"] or sha256_bytes(value) != row["sha256"]
                or _git_object_id("blob", value) != row["git_blob_sha1"]):
            raise RuntimeError(f"executed source/blob identity mismatch: {relative}")
        parent, _, leaf = relative.rpartition("/")
        matches = [entry for entry in entries_by_path[parent]
                   if entry["name"] == leaf and entry["mode"] == "100644"]
        if (row["git_mode"] != "100644" or len(matches) != 1
                or matches[0]["object_id"] != row["git_blob_sha1"]):
            raise RuntimeError(f"executed source lacks origin-tree membership: {relative}")


def distribution_manifest(name: str) -> dict[str, Any]:
    """Bind the bytes actually loaded from the installed distribution."""
    distribution = importlib.metadata.distribution(name)
    rows = []
    for relative in sorted(
            distribution.files or (), key=lambda value: str(value)):
        path = Path(distribution.locate_file(relative))
        if not path.is_file():
            continue
        value = path.read_bytes()
        rows.append({
            "path": str(relative).replace("\\", "/"),
            "bytes": len(value),
            "sha256": sha256_bytes(value),
        })
    if not rows:
        raise RuntimeError(f"installed distribution has no files: {name}")
    return {
        "distribution": name,
        "version": distribution.version,
        "file_count": len(rows),
        "files_sha256": digest(rows),
        "files": rows,
    }


def distribution_relative_path(name: str, loaded_path: Path) -> str:
    distribution = importlib.metadata.distribution(name)
    target = loaded_path.resolve(strict=True)
    matches = [
        str(relative).replace("\\", "/")
        for relative in distribution.files or ()
        if Path(distribution.locate_file(relative)).resolve(strict=True) == target
    ]
    if len(matches) != 1:
        raise RuntimeError({
            "loaded_distribution_path_match_count": len(matches),
            "loaded_path": str(target),
        })
    return matches[0]


def pinned_source_identity(path: Path) -> dict[str, Any]:
    """Bind the installed distribution's direct source checkout."""
    resolved = path.resolve()
    def git(*arguments: str) -> str:
        return subprocess.run(
            ["git", "-C", str(resolved), *arguments], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ).stdout.strip()
    commit = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    if commit != PYOPTIX_COMMIT or tree != PYOPTIX_TREE or status:
        raise RuntimeError({
            "pyoptix_source_commit": commit,
            "pyoptix_source_tree": tree,
            "pyoptix_source_status": status,
        })
    return {
        "path": str(resolved),
        "commit": commit,
        "tree": tree,
        "status_porcelain": status,
        "clean": True,
    }


def loaded_file_identity(path: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    value = resolved.read_bytes()
    return {
        "path": str(resolved),
        "bytes": len(value),
        "sha256": sha256_bytes(value),
    }


def verified_execution_authority(
        authority_path: Path, launch_pin_path: Path, source_root: Path,
        device_source_path: Path) -> dict[str, Any]:
    """Rehash the pre-frozen executed sources before any GPU-stack import."""
    resolved = authority_path.resolve(strict=True)
    raw = resolved.read_bytes()
    document = strict_json_object(raw, "execution authority")
    if type(document) is not dict or set(document) != {
            "schema", "status", "capture_phase", "file_count", "files",
            "files_sha256", "origin_repository_commit",
            "origin_repository_tree", "git_membership_proof",
            "registered_performance_timing_count"} \
            or document["schema"] \
            != "rtdl.goal5800.pyoptix_execution_authority.v2" \
            or document["status"] != "FROZEN__PREEXECUTION_SOURCE_AUTHORITY" \
            or document["capture_phase"] \
            != "BEFORE_PYOPTIX_CUPY_IMPORT_OR_CUDA_OPTIX_INITIALIZATION" \
            or document["registered_performance_timing_count"] != 0:
        raise RuntimeError("invalid preexecution source authority")
    for key in ("origin_repository_commit", "origin_repository_tree"):
        identity = document[key]
        if type(identity) is not str or len(identity) != 40 or any(
                character not in "0123456789abcdef" for character in identity):
            raise RuntimeError(f"invalid preexecution source {key}")
    rows = document["files"]
    if type(rows) is not list or document["file_count"] != len(rows) \
            or [row.get("path") for row in rows] != list(EXECUTED_SOURCE_PATHS) \
            or document["files_sha256"] != digest(rows):
        raise RuntimeError("preexecution source authority rows invalid")
    root = source_root.resolve(strict=True)
    for row in rows:
        if type(row) is not dict or set(row) != {
                "path", "git_mode", "git_blob_sha1", "bytes", "sha256"}:
            raise RuntimeError("preexecution source authority row malformed")
        value = _read_regular_source(root, row["path"])
        if len(value) != row["bytes"] or sha256_bytes(value) != row["sha256"]:
            raise RuntimeError(
                f"executed source differs from preexecution authority: {row['path']}")
    verify_git_membership_proof(document, root, rows)
    expected_device = (root / EXECUTED_SOURCE_PATHS[0]).resolve(strict=True)
    if device_source_path.resolve(strict=True) != expected_device:
        raise RuntimeError("device source argument is outside executed authority")
    pin_resolved = launch_pin_path.resolve(strict=True)
    pin_raw = pin_resolved.read_bytes()
    pin = strict_json_object(pin_raw, "execution launch pin")
    if type(pin) is not dict or set(pin) != {
            "schema", "status", "capture_phase", "authority", "authority_schema",
            "origin_repository_commit", "origin_repository_tree",
            "executed_source_file_count", "all_required_files_exact_origin_blobs",
            "changed_expected_allowed", "registered_performance_timing_count"} \
            or pin["schema"] != "rtdl.goal5800.pyoptix_execution_launch_pin.v1" \
            or pin["status"] != "FROZEN__SEPARATE_PREEXECUTION_TRUST_ANCHOR" \
            or pin["capture_phase"] \
            != "AFTER_AUTHORITY_FREEZE__BEFORE_PYOPTIX_CUPY_IMPORT_OR_GPU_EXECUTION" \
            or pin["authority_schema"] != document["schema"] \
            or pin["origin_repository_commit"] != document["origin_repository_commit"] \
            or pin["origin_repository_tree"] != document["origin_repository_tree"] \
            or pin["executed_source_file_count"] != len(rows) \
            or pin["all_required_files_exact_origin_blobs"] is not True \
            or pin["changed_expected_allowed"] is not False \
            or pin["registered_performance_timing_count"] != 0:
        raise RuntimeError("invalid or mismatched separate execution launch pin")
    authority_identity = pin["authority"]
    if type(authority_identity) is not dict or set(authority_identity) != {
            "path", "bytes", "sha256"} \
            or authority_identity["bytes"] != len(raw) \
            or authority_identity["sha256"] != sha256_bytes(raw):
        raise RuntimeError("execution launch pin does not bind the authority bytes")
    return {
        "file": {
            "path": str(resolved), "bytes": len(raw),
            "sha256": sha256_bytes(raw),
        },
        "document": document,
        "launch_pin": {
            "file": {
                "path": str(pin_resolved), "bytes": len(pin_raw),
                "sha256": sha256_bytes(pin_raw),
            },
            "document": pin,
        },
    }


def verified_pyoptix_receipt(
        path: Path, *, expected_schema: str) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    value = resolved.read_bytes()
    identity = {
        "path": str(resolved), "bytes": len(value),
        "sha256": sha256_bytes(value),
    }
    document = json.loads(value)
    if type(document) is not dict or document.get("schema") != expected_schema:
        raise RuntimeError(f"invalid PyOptiX receipt: {expected_schema}")
    if type(document.get("registered_performance_timing_count")) is not int \
            or document["registered_performance_timing_count"] != 0:
        raise RuntimeError("PyOptiX provenance receipt contains timing")
    if expected_schema.endswith("clean_wheel_build_receipt.v1"):
        if document.get("status") \
                != "PASS__CLEAN_SOURCE_TO_WHEEL_BUILD__UNTIMED" \
                or document.get("transaction_kind") \
                != "build_provenance_not_performance":
            raise RuntimeError("invalid PyOptiX wheel-build receipt status")
        source = document.get("pyoptix_source")
        headers = document.get("optix_headers")
        build = document.get("build")
        wheel = document.get("wheel")
        if type(source) is not dict or type(headers) is not dict \
                or type(build) is not dict or type(wheel) is not dict \
                or source.get("commit") != PYOPTIX_COMMIT \
                or source.get("tree") != PYOPTIX_TREE \
                or headers.get("commit") != OPTIX_HEADERS_COMMIT \
                or headers.get("tree") != OPTIX_HEADERS_TREE \
                or type(headers.get("api_macro")) is not int \
                or headers["api_macro"] != 90000 \
                or type(build.get("exit_code")) is not int \
                or build["exit_code"] != 0:
            raise RuntimeError("PyOptiX wheel-build source identity mismatch")
        wheel_path = (resolved.parent / str(wheel.get("path"))).resolve(
            strict=True)
        wheel_identity = loaded_file_identity(wheel_path)
        if type(wheel.get("bytes")) is not int \
                or wheel["bytes"] != wheel_identity["bytes"] \
                or wheel.get("sha256") != wheel_identity["sha256"]:
            raise RuntimeError("PyOptiX wheel-build wheel identity mismatch")
        member = wheel.get("extension_member")
        if type(member) is not str:
            raise RuntimeError("PyOptiX wheel extension member absent")
        with zipfile.ZipFile(wheel_path) as archive:
            extension = archive.read(member)
        extension_sha = sha256_bytes(extension)
        if type(wheel.get("extension_bytes")) is not int \
                or wheel["extension_bytes"] != len(extension) \
                or wheel.get("extension_sha256") != extension_sha:
            raise RuntimeError("PyOptiX wheel extension identity mismatch")
        return {
            "file": identity, "document": document,
            "wheel_identity": wheel_identity,
            "wheel_sha256": wheel_identity["sha256"],
            "extension_sha256": extension_sha,
            "optix_headers_root": str(
                Path(str(headers.get("root"))).resolve(strict=True)),
        }
    if expected_schema.endswith("clean_install_receipt.v1"):
        if document.get("status") \
                != "PASS__FRESH_VENV__CLEAN_BUILT_EXTENSION_LOADED__UNTIMED" \
                or document.get("transaction_kind") \
                != "installation_and_import_not_performance" \
                or document.get("optix_api_version") != "9.0.0":
            raise RuntimeError("invalid PyOptiX clean-install receipt status")
        wheel = document.get("wheel")
        extension = document.get("loaded_optix_extension")
        if type(wheel) is not dict or type(extension) is not dict \
                or extension.get("module") != "optix._optix":
            raise RuntimeError("invalid PyOptiX clean-install identities")
        wheel_identity = loaded_file_identity(Path(str(wheel.get("path"))))
        extension_identity = loaded_file_identity(
            Path(str(extension.get("path"))))
        if type(wheel.get("bytes")) is not int \
                or wheel["bytes"] != wheel_identity["bytes"] \
                or wheel.get("sha256") != wheel_identity["sha256"] \
                or type(extension.get("bytes")) is not int \
                or extension["bytes"] != extension_identity["bytes"] \
                or extension.get("sha256") != extension_identity["sha256"]:
            raise RuntimeError("PyOptiX clean-install file identity mismatch")
        return {
            "file": identity, "document": document,
            "wheel_identity": wheel_identity,
            "wheel_sha256": wheel_identity["sha256"],
            "extension_identity": extension_identity,
            "extension_sha256": extension_identity["sha256"],
        }
    raise RuntimeError(f"unsupported PyOptiX receipt schema: {expected_schema}")


def loaded_shared_library_manifest() -> dict[str, Any]:
    """Hash address-free identities for every mapped Linux shared object."""
    maps = Path("/proc/self/maps")
    if not maps.is_file():
        raise RuntimeError("executed PyOptiX arm requires Linux /proc/self/maps")
    paths = set()
    for line in maps.read_text(encoding="utf-8", errors="strict").splitlines():
        fields = line.split(None, 5)
        if len(fields) != 6:
            continue
        raw = fields[5]
        if not raw.startswith("/") or ".so" not in Path(raw).name:
            continue
        path = Path(raw).resolve(strict=True)
        if path.is_file():
            paths.add(path)
    rows = [loaded_file_identity(path) for path in sorted(paths, key=str)]
    if not rows:
        raise RuntimeError("no loaded shared objects found in /proc/self/maps")
    return {
        "source": "/proc/self/maps",
        "address_fields_recorded": False,
        "shared_object_count": len(rows),
        "rows_sha256": digest(rows),
        "rows": rows,
    }


def exact_counts(baseline: Any, **nonzero: int) -> dict[str, int]:
    result = baseline.new_operation_counts()
    unknown = set(nonzero).difference(result)
    if unknown:
        raise RuntimeError(f"unknown operation counters: {sorted(unknown)}")
    result.update({key: int(value) for key, value in nonzero.items()})
    return result


def require_execution_contract(
        result: dict[str, Any], *, expected_counts: dict[str, int],
        expected_order: list[str]) -> None:
    if result["execute_operation_counts"] != expected_counts:
        raise RuntimeError({
            "operation_count_mismatch": result["execute_operation_counts"],
            "expected": expected_counts,
        })
    if result["operation_order"] != expected_order:
        raise RuntimeError({
            "operation_order_mismatch": result["operation_order"],
            "expected": expected_order,
        })


def operation_ledger_execution(
        execution: dict[str, Any], *, byte_fields: tuple[str, ...]) -> dict[str, Any]:
    return {
        "execute_operation_counts": execution["execute_operation_counts"],
        "operation_order": execution["operation_order"],
        "independent_execute_guard": execution["independent_execute_guard"],
        "total_host_blocking_count": execution["total_host_blocking_count"],
        "bytes": {key: execution[key] for key in byte_fields},
    }


class DeviceStatusFailure(RuntimeError):
    def __init__(self, message: str, evidence: dict[str, Any]):
        super().__init__(message)
        self.evidence = evidence


class RelationPrepared:
    """Two-orientation matched relation execution with bulk output handling."""

    def __init__(self, baseline: Any, context: Any, pipeline: Any, sbt: Any,
                 fixture: dict[str, Any], *, pipeline_keepalive: Any,
                 sbt_keepalive: Any,
                 raw_capacity: int = RAW_RELATION_CAPACITY):
        self.b = baseline
        self.context = context
        self.pipeline = pipeline
        self.sbt = sbt
        self.pipeline_keepalive = pipeline_keepalive
        self.sbt_keepalive = sbt_keepalive
        self.fixture = fixture
        self.raw_capacity = int(raw_capacity)
        if self.raw_capacity <= 0:
            raise ValueError("relation raw capacity must be positive")
        self.operation_counts = baseline.new_operation_counts()
        self.closed = False
        self.indexed = baseline.boxes_array(fixture["indexed"])
        self.sources = baseline.boxes_array(fixture["sources"])
        self.d_indexed = baseline.to_device(
            self.indexed, operation_counts=self.operation_counts)
        self.d_sources = baseline.to_device(
            self.sources, operation_counts=self.operation_counts)
        cp = baseline.cp
        self.d_rows = cp.zeros(self.raw_capacity * 2, dtype=cp.uint32)
        self.d_control = cp.zeros(3, dtype=cp.uint32)
        self.d_count = self.d_control[0:1]
        self.d_overflow = self.d_control[1:2]
        self.d_status = self.d_control[2:3]
        self.operation_counts["prepare_device_allocation_call_count"] += 2
        self.launcher = baseline.PreparedLaunch(
            pipeline, sbt, operation_counts=self.operation_counts)
        self.indexed_handle, self.indexed_gas = baseline.build_custom_gas(
            context, self.indexed, operation_counts=self.operation_counts,
            stream=self.launcher.stream)
        self.source_handle, self.source_gas = baseline.build_custom_gas(
            context, self.sources, operation_counts=self.operation_counts,
            stream=self.launcher.stream)
        self.h_control = self.launcher.pinned_array(
            (3,), baseline.np.uint32)
        self.h_rows = self.launcher.pinned_array(
            (self.raw_capacity * 2,), baseline.np.uint32)
        self.prepared_launches: list[tuple[Any, int]] = []
        for reverse, primitive_host, query_host, d_primitive, d_query, handle in (
            (0, self.indexed, self.sources, self.d_indexed, self.d_sources,
             self.indexed_handle),
            (1, self.sources, self.indexed, self.d_sources, self.d_indexed,
             self.source_handle),
        ):
            params = self.launcher.pinned_array((1,), baseline.PARAM_DTYPE)
            params[0] = (
                handle, d_primitive.ptr, d_query.ptr, self.d_rows.data.ptr,
                self.d_count.data.ptr, self.d_overflow.data.ptr,
                len(primitive_host), len(query_host), self.raw_capacity,
                reverse, baseline.np.float32(fixture["minimum_overlap"]),
                baseline.np.float32(0.0), baseline.np.float32(1.0),
                0, 0, 0, 0, 0, self.d_status.data.ptr,
            )
            self.prepared_launches.append((params, len(query_host)))
        self.prepare_operation_counts = dict(self.operation_counts)
        expected_prepare = exact_counts(
            baseline,
            prepare_device_allocation_call_count=11,
            prepare_h2d_call_count=4,
            prepare_pinned_host_allocation_call_count=4,
            prepare_stream_creation_count=1,
        )
        if self.prepare_operation_counts != expected_prepare:
            raise RuntimeError("relation prepare operation count drift")

    def execute(self) -> dict[str, Any]:
        try:
            with self.launcher.observe_execution() as observer:
                result = self._execute_observed()
        except DeviceStatusFailure as failure:
            failure.evidence["independent_execute_guard"] = observer.receipt
            raise
        result["independent_execute_guard"] = observer.receipt
        return result

    def _execute_observed(self) -> dict[str, Any]:
        if self.closed:
            raise RuntimeError("relation prepared owner is closed")
        b = self.b
        before = dict(self.operation_counts)
        self.launcher.zero_on_stream(
            self.d_rows, self.d_control,
            events=("rows_reset", "control_reset"),
        )
        rows_reset_bytes = int(self.d_rows.nbytes)
        control_reset_bytes = int(self.d_control.nbytes)
        for index, (params, width) in enumerate(self.prepared_launches):
            self.launcher.enqueue(
                params, width,
                h2d_event=f"params{index}_h2d",
                launch_event=f"launch{index}",
            )
        control_d2h_bytes = int(self.d_control.nbytes)
        self.launcher.enqueue_d2h(
            self.d_control, self.h_control, control_d2h_bytes,
            event="control_d2h",
        )
        self.launcher.synchronize(event="status_ready_sync")

        # All control scalars are consumed before application rows are copied.
        raw_count = int(self.h_control[0])
        overflow = int(self.h_control[1])
        status = int(self.h_control[2])
        if overflow or status or raw_count > self.raw_capacity:
            raise DeviceStatusFailure(
                f"relation device failure: {raw_count}/{overflow}/{status}",
                {
                    "raw_event_count": raw_count,
                    "device_overflow": overflow,
                    "device_status": status,
                    "raw_capacity": self.raw_capacity,
                    "application_output_exposed": False,
                    "application_output_d2h_call_count": 0,
                    "operation_order": list(self.launcher.execution_events),
                    "execute_operation_counts": b.operation_count_delta(
                        self.operation_counts, before),
                },
            )
        output_d2h_bytes = raw_count * int(b.ROW_DTYPE.itemsize)
        self.launcher.enqueue_d2h(
            self.d_rows, self.h_rows, output_d2h_bytes,
            event="rows_d2h",
        )
        self.launcher.synchronize(event="output_ready_sync")
        raw = self.h_rows[:raw_count * 2].reshape((-1, 2)).tolist()
        rows = sorted(set(map(tuple, raw)))
        output = [list(row) for row in rows]
        if len(output) > int(self.fixture["capacity"]):
            raise RuntimeError("relation capacity exceeded; partial output withheld")
        if output != self.fixture["expected_rows"]:
            raise RuntimeError("relation independent-oracle mismatch")
        result = {
            "output": output,
            "raw_event_count": raw_count,
            "device_status": status,
            "device_overflow": overflow,
            "launch_count": 2,
            "required_sync_count": 2,
            "control_d2h_bytes": control_d2h_bytes,
            "output_d2h_bytes": output_d2h_bytes,
            "rows_reset_bytes": rows_reset_bytes,
            "control_reset_bytes": control_reset_bytes,
            "total_host_blocking_count": 2,
            "operation_order": list(self.launcher.execution_events),
            "prepare_operation_counts": dict(self.prepare_operation_counts),
            "operation_ledger_scope": OPERATION_LEDGER_SCOPE,
            "execute_operation_counts": b.operation_count_delta(
                self.operation_counts, before),
        }
        require_execution_contract(
            result,
            expected_counts=exact_counts(
                b,
                execute_async_h2d_call_count=2,
                execute_async_d2h_call_count=2,
                execute_device_zero_fill_call_count=2,
                execute_explicit_stream_sync_call_count=2,
                execute_launch_call_count=2,
            ),
            expected_order=[
                "rows_reset", "control_reset",
                "params0_h2d", "launch0", "params1_h2d", "launch1",
                "control_d2h", "status_ready_sync",
                "rows_d2h", "output_ready_sync",
            ],
        )
        return result

    def close(self) -> None:
        if self.closed:
            return
        self.launcher.close()
        self.closed = True


class TrianglePrepared:
    """One-launch matched triangle execution with bulk output handling."""

    def __init__(self, baseline: Any, context: Any, pipeline: Any, sbt: Any,
                 task: dict[str, Any], *, pipeline_keepalive: Any,
                 sbt_keepalive: Any):
        self.b = baseline
        self.context = context
        self.pipeline = pipeline
        self.sbt = sbt
        self.pipeline_keepalive = pipeline_keepalive
        self.sbt_keepalive = sbt_keepalive
        self.task = task
        self.operation_counts = baseline.new_operation_counts()
        self.closed = False
        b = baseline
        self.launcher = b.PreparedLaunch(
            pipeline, sbt, operation_counts=self.operation_counts)
        self.vertices = b.np.asarray(task["vertices"], dtype=b.np.float32)
        self.handle, self.gas = b.build_triangle_gas(
            context, self.vertices, operation_counts=self.operation_counts,
            stream=self.launcher.stream)
        rays = b.np.zeros(len(task["rays"]), dtype=b.RAY_DTYPE)
        for index, (origin, direction) in enumerate(task["rays"]):
            rays[index] = tuple(
                b.np.float32(value) for value in (*origin, *direction))
        self.rays = rays
        self.weights = b.np.asarray(task["weights"], dtype=b.np.uint64)
        self.d_rays = b.to_device(
            rays, operation_counts=self.operation_counts)
        self.d_weights = b.to_device(
            self.weights, operation_counts=self.operation_counts)
        self.d_per_ray = b.cp.zeros(len(rays), dtype=b.cp.uint64)
        self.d_weighted = b.cp.zeros(1, dtype=b.cp.uint64)
        self.d_status = b.cp.zeros(1, dtype=b.cp.uint32)
        self.operation_counts["prepare_device_allocation_call_count"] += 3
        self.params = self.launcher.pinned_array((1,), b.PARAM_DTYPE)
        self.h_status = self.launcher.pinned_array((1,), b.np.uint32)
        self.h_per_ray = self.launcher.pinned_array(
            (len(rays),), b.np.uint64)
        self.h_weighted = self.launcher.pinned_array((1,), b.np.uint64)
        self.params[0] = (
            self.handle, 0, 0, 0, 0, 0, 0, len(self.rays), 0, 0,
            b.np.float32(0.0), b.np.float32(task["tmin"]),
            b.np.float32(task["tmax"]), 0, self.d_rays.ptr,
            self.d_weights.ptr, self.d_per_ray.data.ptr,
            self.d_weighted.data.ptr, self.d_status.data.ptr,
        )
        self.prepare_operation_counts = dict(self.operation_counts)
        expected_prepare = exact_counts(
            b,
            prepare_device_allocation_call_count=9,
            prepare_h2d_call_count=3,
            prepare_pinned_host_allocation_call_count=4,
            prepare_stream_creation_count=1,
        )
        if self.prepare_operation_counts != expected_prepare:
            raise RuntimeError("triangle prepare operation count drift")

    def execute(self) -> dict[str, Any]:
        try:
            with self.launcher.observe_execution() as observer:
                result = self._execute_observed()
        except DeviceStatusFailure as failure:
            failure.evidence["independent_execute_guard"] = observer.receipt
            raise
        result["independent_execute_guard"] = observer.receipt
        return result

    def _execute_observed(self) -> dict[str, Any]:
        if self.closed:
            raise RuntimeError("triangle prepared owner is closed")
        b = self.b
        before = dict(self.operation_counts)
        self.launcher.zero_on_stream(
            self.d_per_ray, self.d_weighted, self.d_status,
            events=("per_ray_reset", "weighted_reset", "status_reset"),
        )
        per_ray_reset_bytes = int(self.d_per_ray.nbytes)
        weighted_reset_bytes = int(self.d_weighted.nbytes)
        status_reset_bytes = int(self.d_status.nbytes)
        self.launcher.enqueue(
            self.params, len(self.rays),
            h2d_event="params_h2d", launch_event="launch",
        )
        status_d2h_bytes = int(self.d_status.nbytes)
        self.launcher.enqueue_d2h(
            self.d_status, self.h_status, status_d2h_bytes,
            event="control_d2h",
        )
        self.launcher.synchronize(event="status_ready_sync")
        # Status is consumed before any application output is exposed.
        status = int(self.h_status[0])
        if status:
            raise RuntimeError(f"triangle device status failure: {status}")
        per_ray_d2h_bytes = int(self.d_per_ray.nbytes)
        weighted_d2h_bytes = int(self.d_weighted.nbytes)
        self.launcher.enqueue_d2h(
            self.d_per_ray, self.h_per_ray, per_ray_d2h_bytes,
            event="per_ray_d2h",
        )
        self.launcher.enqueue_d2h(
            self.d_weighted, self.h_weighted, weighted_d2h_bytes,
            event="weighted_d2h",
        )
        self.launcher.synchronize(event="output_ready_sync")
        per_ray = self.h_per_ray.tolist()
        weighted = int(self.h_weighted[0])
        if per_ray != self.task["expected_per_ray"] \
                or weighted != self.task["expected_weighted_sum"]:
            raise RuntimeError("triangle independent-oracle mismatch")
        result = {
            "per_ray": per_ray,
            "weighted_sum": weighted,
            "device_status": status,
            "launch_count": 1,
            "required_sync_count": 2,
            "status_d2h_bytes": status_d2h_bytes,
            "per_ray_d2h_bytes": per_ray_d2h_bytes,
            "weighted_d2h_bytes": weighted_d2h_bytes,
            "per_ray_reset_bytes": per_ray_reset_bytes,
            "weighted_reset_bytes": weighted_reset_bytes,
            "status_reset_bytes": status_reset_bytes,
            "total_host_blocking_count": 2,
            "operation_order": list(self.launcher.execution_events),
            "prepare_operation_counts": dict(self.prepare_operation_counts),
            "operation_ledger_scope": OPERATION_LEDGER_SCOPE,
            "execute_operation_counts": b.operation_count_delta(
                self.operation_counts, before),
        }
        require_execution_contract(
            result,
            expected_counts=exact_counts(
                b,
                execute_async_h2d_call_count=1,
                execute_async_d2h_call_count=3,
                execute_device_zero_fill_call_count=3,
                execute_explicit_stream_sync_call_count=2,
                execute_launch_call_count=1,
            ),
            expected_order=[
                "per_ray_reset", "weighted_reset", "status_reset",
                "params_h2d", "launch", "control_d2h",
                "status_ready_sync", "per_ray_d2h", "weighted_d2h",
                "output_ready_sync",
            ],
        )
        return result

    def close(self) -> None:
        if self.closed:
            return
        self.launcher.close()
        self.closed = True


def plan(source: Path) -> dict[str, Any]:
    text = source.read_text(encoding="utf-8")
    forbidden = [
        "[int(value)" + " for value in cp.asnumpy",
        "for row" + " in raw",
        "time." + "perf_counter",
        "time." + "monotonic",
    ]
    hits = [literal for literal in forbidden if literal in text]
    if hits:
        raise RuntimeError(f"non-idiomatic/timing literals present: {hits}")
    source_boundary = validate_execute_source_boundary(source)
    return {
        "schema": "rtdl.goal5800.pyoptix_idiomatic_arm.plan.v2",
        "status": "PASS__SOURCE_PLAN_ONLY__GPU_NOT_IMPORTED",
        "arm": ARM,
        "pyoptix_commit": PYOPTIX_COMMIT,
        "pyoptix_tree": PYOPTIX_TREE,
        "bulk_relation_materialization": "reshape.tolist_then_set_map",
        "bulk_triangle_materialization": "ndarray.tolist",
        "status_before_output": True,
        "relation_launch_count": 2,
        "triangle_launch_count": 1,
        "persistent_stream_per_prepared_owner": True,
        "persistent_launch_param_device_buffer_per_prepared_owner": True,
        "same_stream_async_param_h2d_and_launch": True,
        "current_stream_preexecute_sync": False,
        "sync_after_every_launch": False,
        "relation_explicit_sync_count_per_execute": 2,
        "triangle_explicit_sync_count_per_execute": 2,
        "relation_async_h2d_count_per_execute": 2,
        "triangle_async_h2d_count_per_execute": 1,
        "relation_async_d2h_count_per_execute": 2,
        "triangle_async_d2h_count_per_execute": 3,
        "relation_blocking_d2h_count_per_execute": 0,
        "triangle_blocking_d2h_count_per_execute": 0,
        "relation_total_host_blocking_count_per_execute": 2,
        "triangle_total_host_blocking_count_per_execute": 2,
        "relation_device_reset_count_per_execute": 2,
        "triangle_device_reset_count_per_execute": 3,
        "same_prepared_owner_initial_repeat_required": True,
        "operation_ledger_scope": OPERATION_LEDGER_SCOPE,
        "execute_source_boundary": source_boundary,
        "complete_driver_operation_observation_claimed": False,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "source_sha256": sha256_bytes(source.read_bytes()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--device-source", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--pyoptix-source-root", type=Path)
    parser.add_argument("--pyoptix-wheel-build-receipt", type=Path)
    parser.add_argument("--pyoptix-clean-install-receipt", type=Path)
    parser.add_argument("--execution-authority", type=Path)
    parser.add_argument("--execution-pin", type=Path)
    parser.add_argument("--expected-optix-api-version", default="9.0.0")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve()
    if args.plan_only:
        print(json.dumps(plan(source), sort_keys=True))
        return
    source_boundary = validate_execute_source_boundary(source)
    for name in (
            "device_source", "optix_include", "cuda_include",
            "pyoptix_source_root", "pyoptix_wheel_build_receipt",
            "pyoptix_clean_install_receipt", "execution_authority",
            "execution_pin", "output"):
        if getattr(args, name) is None:
            raise ValueError(f"execution requires --{name.replace('_', '-')}")
    if args.output.exists():
        raise FileExistsError(args.output)

    root = source.parents[2]
    executed_source_authority = verified_execution_authority(
        args.execution_authority, args.execution_pin, root, args.device_source)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from experiments.goal5796_matched import pyoptix_baseline as b
    from experiments.goal5798_premeasurement.workload import (
        relation_workload, triangle_workload,
    )

    expected_api = tuple(
        int(value) for value in args.expected_optix_api_version.split("."))
    actual_api = tuple(int(value) for value in b.optix.version())
    if actual_api != expected_api or b.PYOPTIX_COMMIT != PYOPTIX_COMMIT:
        raise RuntimeError("PyOptiX source/API identity mismatch")
    source_identity = pinned_source_identity(args.pyoptix_source_root)
    optix_extension = sys.modules.get("optix._optix")
    if optix_extension is None or not getattr(optix_extension, "__file__", None):
        raise RuntimeError("loaded optix._optix extension identity unavailable")
    optix_initializer_identity = loaded_file_identity(Path(b.optix.__file__))
    optix_extension_identity = loaded_file_identity(
        Path(optix_extension.__file__))
    loaded_optix_extension = {
        "module": "optix._optix",
        "source_path": distribution_relative_path(
            "pyoptix", Path(optix_extension.__file__)),
        "distribution_path": optix_extension_identity["path"],
        "bytes": optix_extension_identity["bytes"],
        "sha256": optix_extension_identity["sha256"],
    }
    wheel_build_receipt = verified_pyoptix_receipt(
        args.pyoptix_wheel_build_receipt,
        expected_schema=(
            "rtdl.goal5800.pyoptix_clean_wheel_build_receipt.v1"),
    )
    clean_install_receipt = verified_pyoptix_receipt(
        args.pyoptix_clean_install_receipt,
        expected_schema="rtdl.goal5800.pyoptix_clean_install_receipt.v1",
    )
    if wheel_build_receipt["wheel_sha256"] \
            != clean_install_receipt["wheel_sha256"]:
        raise RuntimeError("PyOptiX built/installed wheel identity mismatch")
    for receipt in (wheel_build_receipt, clean_install_receipt):
        if receipt["extension_sha256"] != optix_extension_identity["sha256"]:
            raise RuntimeError("PyOptiX receipt/loaded extension identity mismatch")
    if clean_install_receipt["extension_identity"]["path"] \
            != optix_extension_identity["path"]:
        raise RuntimeError("PyOptiX clean-install/current extension path mismatch")
    expected_optix_include = (
        Path(wheel_build_receipt["optix_headers_root"]) / "include"
    ).resolve(strict=True)
    if args.optix_include.resolve(strict=True) != expected_optix_include:
        raise RuntimeError("device compile/build OptiX header identity mismatch")
    device_source = args.device_source.read_bytes()
    ptx = b.compile_ptx(
        args.device_source, args.optix_include, args.cuda_include)
    context, logger = b.make_context()
    relation_pipeline, relation_groups, _ = b.build_pipeline(
        context, ptx, task="relation")
    relation_sbt, relation_sbt_keepalive = b.make_sbt(relation_groups)
    triangle_pipeline, triangle_groups, _ = b.build_pipeline(
        context, ptx, task="triangle")
    triangle_sbt, triangle_sbt_keepalive = b.make_sbt(triangle_groups)
    relation_task = relation_workload()
    triangle_task = triangle_workload()
    relation_owner = RelationPrepared(
        b, context, relation_pipeline, relation_sbt, relation_task,
        pipeline_keepalive=relation_groups,
        sbt_keepalive=relation_sbt_keepalive,
    )
    triangle_owner = TrianglePrepared(
        b, context, triangle_pipeline, triangle_sbt, triangle_task,
        pipeline_keepalive=triangle_groups,
        sbt_keepalive=triangle_sbt_keepalive,
    )
    try:
        relation_initial = relation_owner.execute()
        relation_repeat = relation_owner.execute()
        triangle_initial = triangle_owner.execute()
        triangle_repeat = triangle_owner.execute()
        if relation_initial != relation_repeat:
            raise RuntimeError("relation same-owner initial/repeat mismatch")
        if triangle_initial != triangle_repeat:
            raise RuntimeError("triangle same-owner initial/repeat mismatch")
    finally:
        relation_owner.close()
        triangle_owner.close()
    status_witness_owner = RelationPrepared(
        b, context, relation_pipeline, relation_sbt, relation_task,
        pipeline_keepalive=relation_groups,
        sbt_keepalive=relation_sbt_keepalive,
        raw_capacity=1,
    )
    try:
        try:
            status_witness_owner.execute()
        except DeviceStatusFailure as failure:
            device_failure_witness = failure.evidence
        else:
            raise RuntimeError("tiny-capacity relation device failure was accepted")
    finally:
        status_witness_owner.close()
    expected_failure_counts = exact_counts(
        b,
        execute_async_h2d_call_count=2,
        execute_async_d2h_call_count=1,
        execute_device_zero_fill_call_count=2,
        execute_explicit_stream_sync_call_count=1,
        execute_launch_call_count=2,
    )
    expected_failure_order = [
        "rows_reset", "control_reset",
        "params0_h2d", "launch0", "params1_h2d", "launch1",
        "control_d2h", "status_ready_sync",
    ]
    if device_failure_witness["execute_operation_counts"] \
            != expected_failure_counts \
            or device_failure_witness["operation_order"] \
            != expected_failure_order \
            or device_failure_witness["application_output_exposed"] is not False \
            or device_failure_witness["application_output_d2h_call_count"] != 0 \
            or not (
                device_failure_witness["device_overflow"]
                or device_failure_witness["device_status"]
                or device_failure_witness["raw_event_count"]
                > device_failure_witness["raw_capacity"]
            ):
        raise RuntimeError({
            "device_failure_witness_contract_mismatch": device_failure_witness,
        })
    validation_errors = [
        row for row in logger.messages if int(row["level"]) <= 2]
    if validation_errors:
        raise RuntimeError(f"OptiX validation errors: {validation_errors}")
    shared_library_manifest = loaded_shared_library_manifest()
    pyoptix_distribution = distribution_manifest("pyoptix")
    operation_ledger = {
        "schema": "rtdl.goal5800.pyoptix_operation_ledger.v3",
        "scope": OPERATION_LEDGER_SCOPE,
        "source_observable_wrapper_counter_keys": list(b.OPERATION_COUNT_KEYS),
        "execute_source_boundary": source_boundary,
        "complete_driver_operation_observation_claimed": False,
        "relation": {
            "prepare_operation_counts":
                relation_initial["prepare_operation_counts"],
            "initial": operation_ledger_execution(
                relation_initial,
                byte_fields=(
                    "rows_reset_bytes", "control_reset_bytes",
                    "control_d2h_bytes", "output_d2h_bytes",
                ),
            ),
            "repeat": operation_ledger_execution(
                relation_repeat,
                byte_fields=(
                    "rows_reset_bytes", "control_reset_bytes",
                    "control_d2h_bytes", "output_d2h_bytes",
                ),
            ),
            "initial_repeat_exact": relation_initial == relation_repeat,
        },
        "triangle": {
            "prepare_operation_counts":
                triangle_initial["prepare_operation_counts"],
            "initial": operation_ledger_execution(
                triangle_initial,
                byte_fields=(
                    "per_ray_reset_bytes", "weighted_reset_bytes",
                    "status_reset_bytes", "status_d2h_bytes",
                    "per_ray_d2h_bytes", "weighted_d2h_bytes",
                ),
            ),
            "repeat": operation_ledger_execution(
                triangle_repeat,
                byte_fields=(
                    "per_ray_reset_bytes", "weighted_reset_bytes",
                    "status_reset_bytes", "status_d2h_bytes",
                    "per_ray_d2h_bytes", "weighted_d2h_bytes",
                ),
            ),
            "initial_repeat_exact": triangle_initial == triangle_repeat,
        },
        "context_module_pipeline_sbt_prepare_counted": False,
        "owner_close_operation_counts_claimed": False,
        "device_failure_status_before_output_witness": device_failure_witness,
    }
    result = {
        "schema": "rtdl.goal5800.pyoptix_idiomatic_arm.result.v2",
        "status": "PASS__UNTIMED_FUNCTIONAL",
        "arm": ARM,
        "pyoptix_commit": PYOPTIX_COMMIT,
        "pyoptix_tree": PYOPTIX_TREE,
        "executed_source_authority": executed_source_authority,
        "pyoptix_source_authority_identity": source_identity,
        "pyoptix_install_provenance": {
            "wheel_build_receipt": wheel_build_receipt,
            "clean_install_receipt": clean_install_receipt,
            "built_wheel_equals_installed_wheel": True,
            "receipt_extensions_equal_loaded_extension": True,
        },
        "pyoptix_distribution_version": importlib.metadata.version("pyoptix"),
        "pyoptix_loaded_distribution_manifest": pyoptix_distribution,
        "loaded_optix_module_file": optix_initializer_identity["path"],
        "loaded_optix_module_sha256": optix_initializer_identity["sha256"],
        "loaded_optix_initializer_identity": optix_initializer_identity,
        "loaded_optix_extension": loaded_optix_extension,
        "loaded_shared_library_manifest": shared_library_manifest,
        "operation_ledger": operation_ledger,
        "execute_source_boundary": source_boundary,
        "device_failure_status_before_output_witness": device_failure_witness,
        "optix_api_version": ".".join(map(str, actual_api)),
        "device_source_sha256": sha256_bytes(device_source),
        "ptx_sha256": sha256_bytes(ptx),
        "relation": {
            **relation_initial,
            "output_sha256": digest(relation_initial["output"]),
            "same_prepared_owner_reused": True,
            "initial_repeat_exact": True,
            "initial_execution": relation_initial,
            "repeat_execution": relation_repeat,
        },
        "triangle": {
            **triangle_initial,
            "per_ray_sha256": digest(triangle_initial["per_ray"]),
            "same_prepared_owner_reused": True,
            "initial_repeat_exact": True,
            "initial_execution": triangle_initial,
            "repeat_execution": triangle_repeat,
        },
        "prepared_owners_closed_after_repeat": (
            relation_owner.closed and triangle_owner.closed),
        "operation_ledger_scope": OPERATION_LEDGER_SCOPE,
        "optix_validation": "PASS",
        "optix_validation_error_message_count": 0,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
