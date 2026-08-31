#!/usr/bin/env python3
"""Build a create-only, exact header closure for Goal5802 target preparation.

The target CUDA include directory is a distribution-owned tree containing
unrelated symlinks, so treating the whole directory as one regular-file tree
is neither executable nor auditable.  This tool asks the CUDA and C++
compilers for the dependency closure of the two measured CUDA sources and the
Direct worker source, copies every named dependency as regular bytes into one
projection, and seals both sides of the copy.  It takes no clocks and launches
no GPU work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import subprocess
from typing import Mapping, NoReturn, Sequence


SCHEMA = "rtdl.goal5802.load_bearing_header_projection.v2"
STATUS = (
    "PASS__UNTIMED_OBSERVED_NVCC_SDK_HEADER_PROJECTION__"
    "FRESH_PROCESS_REPLAY_REQUIRED")
CLOSURE_CLAIM = (
    "OBSERVED_NVCC_DEPENDENCY_SET_UNDER_MATCHED_ARCH_AND_EXACT_HOST_CXX__"
    "PROJECTED_SDK_HEADER_CANDIDATE__FRESH_PROCESS_EXACT_NVRTC_REPLAY_"
    "NOT_YET_ESTABLISHED__"
    "NOT_A_GENERAL_NVRTC_SUPERSET")
RUN_ROLES = (
    "matched_device_cuda_dependencies",
    "relation_compaction_cuda_dependencies",
    "direct_cpp_dependencies",
)
CUDA_ROLE_SOURCE_KEYS = {
    "matched_device_cuda_dependencies": "matched_device_source",
    "relation_compaction_cuda_dependencies": "relation_compaction_source",
}
DIRECT_ROLE = "direct_cpp_dependencies"
NVCC_HOST_COMPILER_POLICY = (
    "EXACT_CONFIGURED_CXX__NVCC_DEPENDENCY_ONLY__"
    "ALLOW_UNSUPPORTED_COMPILER_EXPLICIT")
SDK_CLASS = "LOAD_BEARING_PROJECTED_SDK_HEADER"
PROVENANCE_CLASS = "PROVENANCE_ONLY_SOURCE_SYSTEM_OR_TOOLCHAIN"


class DependencyCommandFailure(RuntimeError):
    """A dependency command failed before a projection could be created."""

    def __init__(self, captured: Mapping[str, object]):
        super().__init__(f"dependency command failed: {captured.get('role')}")
        self.captured = dict(captured)


def _fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def _plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _normalized_absolute(path: Path) -> Path:
    """Collapse dot components without resolving an intervening symlink."""

    absolute = path.absolute()
    if not absolute.is_absolute() or not absolute.anchor:
        _fail(f"dependency path is not absolute: {path}")
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        if part in {"", "."}:
            continue
        if part == "..":
            if current.is_symlink():
                _fail(
                    "dependency parent traversal crosses a symlink: "
                    f"{path}")
            parent = current.parent
            if parent == current:
                _fail(f"dependency path traverses above its anchor: {path}")
            current = parent
        else:
            current = current / part
    return current


def _reject_receipt_inside_projection(
        projection_root: Path, receipt_path: Path) -> None:
    """Reject lexical and existing-parent symlink aliases into the tree."""

    projection_lexical = _normalized_absolute(projection_root)
    receipt_lexical = _normalized_absolute(receipt_path)
    projection_resolved = projection_lexical.resolve(strict=False)
    receipt_resolved = receipt_lexical.resolve(strict=False)
    if any(receipt == projection or receipt.is_relative_to(projection)
           for receipt, projection in (
               (receipt_lexical, projection_lexical),
               (receipt_resolved, projection_resolved))):
        _fail("header projection receipt must be outside projection root")


def _file(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        _fail(f"dependency payload is not a regular file: {resolved}")
    payload = resolved.read_bytes()
    return {
        "path": str(path.absolute()),
        "resolved_path": str(resolved),
        "bytes": len(payload),
        "sha256": _sha(payload),
    }


def _symlink_chain(path: Path) -> list[dict[str, str]]:
    """Record every symlink component followed while resolving ``path``."""

    absolute = _normalized_absolute(path)
    if not absolute.is_absolute():
        _fail(f"dependency path is not absolute: {path}")
    pending = list(absolute.parts[1:])
    current = Path(absolute.anchor)
    rows: list[dict[str, str]] = []
    step_count = 0
    while pending:
        step_count += 1
        if step_count > 1024:
            _fail(f"dependency symlink resolution exceeds bound: {path}")
        part = pending.pop(0)
        candidate = current / part
        if candidate.is_symlink():
            target = candidate.readlink()
            target_path = target if target.is_absolute() \
                else candidate.parent / target
            target_path = _normalized_absolute(target_path)
            resolved = candidate.resolve(strict=True)
            rows.append({
                "link_path": str(candidate),
                "link_target": str(target),
                "resolved_target": str(resolved),
            })
            pending = [*target_path.parts[1:], *pending]
            current = Path(target_path.anchor)
        else:
            current = candidate
    if current.resolve(strict=True) != absolute.resolve(strict=True):
        _fail(f"dependency symlink-chain resolution differs: {path}")
    return rows


def _projection_relative(path: Path) -> PurePosixPath:
    absolute = _normalized_absolute(path)
    if not absolute.is_absolute():
        _fail(f"dependency path is not absolute: {path}")
    parts = list(absolute.parts)
    anchor = absolute.anchor
    if not parts or not anchor:
        _fail(f"dependency path has no absolute anchor: {path}")
    parts = parts[1:]
    prefix: list[str] = ["rootfs"]
    drive = absolute.drive.rstrip(":/\\")
    if drive:
        prefix.append(f"drive_{drive}")
    for part in parts:
        if part in {"", ".", ".."} or "/" in part or "\\" in part:
            _fail(f"dependency path component is not projectable: {path}")
        prefix.append(part)
    return PurePosixPath(*prefix)


def _parse_make_dependencies(stdout_utf8: str) -> list[Path]:
    logical = stdout_utf8.replace("\\\r\n", " ").replace("\\\n", " ")
    if ":" not in logical:
        _fail("dependency stdout lacks a Makefile target separator")
    _, dependency_text = logical.split(":", 1)
    try:
        tokens = shlex.split(dependency_text, posix=True)
    except ValueError as error:
        raise RuntimeError("dependency stdout has invalid escaping") from error
    if not tokens:
        _fail("dependency stdout has no dependencies")
    paths = [Path(token) for token in tokens]
    if any(not path.is_absolute() for path in paths):
        _fail("dependency stdout contains a non-absolute path")
    return paths


def _ordered_unique_dependencies(paths: Sequence[Path]) -> list[Path]:
    """Return the load-bearing set without hiding repeated Make tokens."""

    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        lexical = str(_normalized_absolute(path))
        if lexical not in seen:
            seen.add(lexical)
            unique.append(path)
    return unique


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _dependency_record(
        path: Path, projection_root: Path, *, classification: str,
        sdk_root_role: str | None) -> dict[str, object]:
    original = _normalized_absolute(path)
    try:
        resolved = original.resolve(strict=True)
    except OSError as error:
        raise RuntimeError(
            f"dependency does not resolve to a regular file: {original}") \
            from error
    if not resolved.is_file():
        _fail(f"dependency does not resolve to a regular file: {original}")
    payload = resolved.read_bytes()
    common: dict[str, object] = {
        "original_path": str(original),
        "resolved_path": str(resolved),
        "symlink_chain": _symlink_chain(original),
        "bytes": len(payload),
        "sha256": _sha(payload),
        "classification": classification,
        "sdk_root_role": sdk_root_role,
    }
    if classification == PROVENANCE_CLASS:
        return common
    if classification != SDK_CLASS or sdk_root_role not in {
            "optix_include", "cuda_include"}:
        _fail(f"dependency classification is invalid: {original}")
    relative = _projection_relative(original)
    projected = projection_root / Path(relative.as_posix())
    if projected.exists() or projected.is_symlink():
        if not projected.is_file() or projected.is_symlink() \
                or projected.read_bytes() != payload:
            _fail(f"duplicate projected dependency differs: {relative}")
    else:
        _write_create_only(projected, payload)
    return {
        **common,
        "projection_path": relative.as_posix(),
        "projected_bytes": projected.stat().st_size,
        "projected_sha256": _sha(projected.read_bytes()),
    }


def _projection_rows(root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            _fail(f"header projection contains a symlink: {path}")
        if path.is_file():
            payload = path.read_bytes()
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": len(payload),
                "sha256": _sha(payload),
            })
        elif not path.is_dir():
            _fail(f"header projection contains a special file: {path}")
    return rows


def _tool_record(command: Sequence[str]) -> dict[str, object]:
    if not command:
        _fail("dependency command is empty")
    return _file(Path(command[0]))


def _directory_record(path: Path) -> dict[str, str]:
    original = _normalized_absolute(path)
    resolved = original.resolve(strict=True)
    if not resolved.is_dir():
        _fail(f"SDK include root is not a directory: {original}")
    return {"path": str(original), "resolved_path": str(resolved)}


def _command_sha256(command: Sequence[str]) -> str:
    return _sha(_canonical(list(command)))


def build_command_authority(
        *, nvcc: Path, cxx: Path, matched_device_source: Path,
        relation_compaction_source: Path, direct_source: Path,
        optix_include: Path, cuda_include: Path,
        compute_capability: str) -> dict[str, object]:
    """Build the independently reconstructable exact dependency commands."""

    if not compute_capability.startswith("sm_") \
            or not compute_capability[3:].isdigit():
        _fail("compute capability must be sm_<digits>")
    tools = {"nvcc": _file(nvcc), "cxx": _file(cxx)}
    sources = {
        "matched_device_source": _file(matched_device_source),
        "relation_compaction_source": _file(relation_compaction_source),
        "direct_source": _file(direct_source),
    }
    roots = {
        "optix_include": _directory_record(optix_include),
        "cuda_include": _directory_record(cuda_include),
    }
    cuda_common = [
        str(_normalized_absolute(nvcc)), "-ccbin",
        tools["cxx"]["resolved_path"], "-allow-unsupported-compiler",
        "-M", "-std=c++17",
        f"-arch={compute_capability}",
        f"-I{roots['optix_include']['resolved_path']}",
        f"-I{roots['cuda_include']['resolved_path']}",
        f"-I{Path(str(roots['cuda_include']['resolved_path'])) / 'nv'}",
    ]
    commands = {
        "matched_device_cuda_dependencies": [
            *cuda_common, sources["matched_device_source"]["resolved_path"]],
        "relation_compaction_cuda_dependencies": [
            *cuda_common,
            sources["relation_compaction_source"]["resolved_path"]],
        DIRECT_ROLE: [
            str(_normalized_absolute(cxx)), "-M", "-std=c++17", "-O3",
            "-DNDEBUG", f"-I{roots['optix_include']['resolved_path']}",
            f"-I{roots['cuda_include']['resolved_path']}",
            f"-I{Path(str(roots['cuda_include']['resolved_path'])) / 'nv'}",
            sources["direct_source"]["resolved_path"],
        ],
    }
    return {
        "schema": "rtdl.goal5802.dependency_command_authority.v4",
        "compute_capability": compute_capability,
        "nvcc_host_compiler_policy": NVCC_HOST_COMPILER_POLICY,
        "tools": tools,
        "sources": sources,
        "original_sdk_roots": roots,
        "expected_commands": [{
            "role": role,
            "command": commands[role],
            "command_sha256": _command_sha256(commands[role]),
        } for role in RUN_ROLES],
    }


def _validate_command_authority(
        authority: Mapping[str, object]) -> dict[str, list[str]]:
    expected_without_io = _validate_command_authority_shape_no_io(authority)
    if set(authority) != {
            "schema", "compute_capability", "nvcc_host_compiler_policy",
            "tools", "sources",
            "original_sdk_roots", "expected_commands"} \
            or authority.get("schema") \
            != "rtdl.goal5802.dependency_command_authority.v4":
        _fail("dependency command authority schema differs")
    compute = authority.get("compute_capability")
    policy = authority.get("nvcc_host_compiler_policy")
    tools = authority.get("tools")
    sources = authority.get("sources")
    roots = authority.get("original_sdk_roots")
    expected = authority.get("expected_commands")
    if not isinstance(compute, str) or not compute.startswith("sm_") \
            or not compute[3:].isdigit() \
            or policy != NVCC_HOST_COMPILER_POLICY \
            or not isinstance(tools, Mapping) \
            or set(tools) != {"nvcc", "cxx"} \
            or not isinstance(sources, Mapping) \
            or set(sources) != {
                "matched_device_source", "relation_compaction_source",
                "direct_source"} \
            or not isinstance(roots, Mapping) \
            or set(roots) != {"optix_include", "cuda_include"} \
            or not isinstance(expected, list):
        _fail("dependency command authority envelope differs")
    for name, record in tools.items():
        if not isinstance(record, Mapping):
            _fail(f"dependency tool record is malformed: {name}")
        observed = _file(Path(str(record.get("path", ""))))
        if record != observed:
            _fail(f"dependency tool identity differs: {name}")
    for name, record in sources.items():
        if not isinstance(record, Mapping):
            _fail(f"dependency source record is malformed: {name}")
        observed = _file(Path(str(record.get("path", ""))))
        if record != observed:
            _fail(f"dependency source identity differs: {name}")
    for name, record in roots.items():
        if not isinstance(record, Mapping) or record != _directory_record(
                Path(str(record.get("path", "")))):
            _fail(f"dependency SDK root identity differs: {name}")
    rebuilt = build_command_authority(
        nvcc=Path(str(tools["nvcc"]["path"])),
        cxx=Path(str(tools["cxx"]["path"])),
        matched_device_source=Path(str(
            sources["matched_device_source"]["path"])),
        relation_compaction_source=Path(str(
            sources["relation_compaction_source"]["path"])),
        direct_source=Path(str(sources["direct_source"]["path"])),
        optix_include=Path(str(roots["optix_include"]["path"])),
        cuda_include=Path(str(roots["cuda_include"]["path"])),
        compute_capability=compute,
    )
    if dict(authority) != rebuilt:
        _fail("dependency exact commands differ from authority inputs")
    if expected_without_io != {
            str(row["role"]): list(row["command"])
            for row in rebuilt["expected_commands"]}:
        _fail("dependency command authority static reconstruction differs")
    return expected_without_io


def _validate_command_authority_shape_no_io(
        authority: Mapping[str, object]) -> dict[str, list[str]]:
    """Reconstruct exact commands from sealed records without host reads."""

    if set(authority) != {
            "schema", "compute_capability", "nvcc_host_compiler_policy",
            "tools", "sources",
            "original_sdk_roots", "expected_commands"} \
            or authority.get("schema") \
            != "rtdl.goal5802.dependency_command_authority.v4":
        _fail("dependency command authority schema differs")
    compute = authority.get("compute_capability")
    policy = authority.get("nvcc_host_compiler_policy")
    tools = authority.get("tools")
    sources = authority.get("sources")
    roots = authority.get("original_sdk_roots")
    expected = authority.get("expected_commands")
    if not isinstance(compute, str) or not compute.startswith("sm_") \
            or not compute[3:].isdigit() \
            or policy != NVCC_HOST_COMPILER_POLICY \
            or not isinstance(tools, Mapping) \
            or set(tools) != {"nvcc", "cxx"} \
            or not isinstance(sources, Mapping) \
            or set(sources) != {
                "matched_device_source", "relation_compaction_source",
                "direct_source"} \
            or not isinstance(roots, Mapping) \
            or set(roots) != {"optix_include", "cuda_include"} \
            or not isinstance(expected, list):
        _fail("dependency command authority envelope differs")
    file_keys = {"path", "resolved_path", "bytes", "sha256"}
    for collection in (tools, sources):
        for record in collection.values():
            if not isinstance(record, Mapping) or set(record) != file_keys \
                    or not isinstance(record.get("path"), str) \
                    or not Path(record["path"]).is_absolute() \
                    or not isinstance(record.get("resolved_path"), str) \
                    or not Path(record["resolved_path"]).is_absolute() \
                    or not isinstance(record.get("bytes"), int) \
                    or record["bytes"] < 0 \
                    or not isinstance(record.get("sha256"), str) \
                    or len(record["sha256"]) != 64:
                _fail("dependency sealed file record is malformed")
    for record in roots.values():
        if not isinstance(record, Mapping) or set(record) != {
                "path", "resolved_path"} \
                or not all(isinstance(record.get(key), str)
                           and Path(record[key]).is_absolute()
                           for key in ("path", "resolved_path")):
            _fail("dependency sealed SDK root record is malformed")
    cuda_common = [
        str(tools["nvcc"]["path"]), "-ccbin",
        str(tools["cxx"]["resolved_path"]),
        "-allow-unsupported-compiler", "-M", "-std=c++17",
        f"-arch={compute}",
        f"-I{roots['optix_include']['resolved_path']}",
        f"-I{roots['cuda_include']['resolved_path']}",
        f"-I{Path(str(roots['cuda_include']['resolved_path'])) / 'nv'}",
    ]
    rebuilt = {
        "matched_device_cuda_dependencies": [
            *cuda_common, str(sources["matched_device_source"][
                "resolved_path"])],
        "relation_compaction_cuda_dependencies": [
            *cuda_common, str(sources["relation_compaction_source"][
                "resolved_path"])],
        DIRECT_ROLE: [
            str(tools["cxx"]["path"]), "-M", "-std=c++17", "-O3",
            "-DNDEBUG", f"-I{roots['optix_include']['resolved_path']}",
            f"-I{roots['cuda_include']['resolved_path']}",
            f"-I{Path(str(roots['cuda_include']['resolved_path'])) / 'nv'}",
            str(sources["direct_source"]["resolved_path"])],
    }
    rebuilt_rows = [{
        "role": role, "command": rebuilt[role],
        "command_sha256": _command_sha256(rebuilt[role]),
    } for role in RUN_ROLES]
    if expected != rebuilt_rows:
        _fail("dependency exact command shape differs")
    return rebuilt


def _root_mappings(
        authority: Mapping[str, object], projection_root: Path,
        ) -> list[dict[str, object]]:
    roots = authority["original_sdk_roots"]
    assert isinstance(roots, Mapping)
    projection_absolute = _normalized_absolute(projection_root)
    rows = []
    for role in ("optix_include", "cuda_include"):
        record = roots[role]
        assert isinstance(record, Mapping)
        original = Path(str(record["resolved_path"]))
        relative = _projection_relative(original).as_posix()
        projected = projection_absolute / Path(relative)
        if original == projected \
                or original.is_relative_to(projected) \
                or projected.is_relative_to(original):
            _fail(f"original and projected SDK roots overlap: {role}")
        rows.append({
            "role": role,
            "original_root": str(original),
            "projection_relative_root": relative,
            "projected_root": str(projected),
            "roots_distinct_and_nonoverlapping": True,
        })
    originals = [Path(str(row["original_root"])) for row in rows]
    projected = [Path(str(row["projected_root"])) for row in rows]
    for first, second, label in (
            (originals[0], originals[1], "original"),
            (projected[0], projected[1], "projected")):
        if first == second or first.is_relative_to(second) \
                or second.is_relative_to(first):
            _fail(f"{label} OptiX/CUDA include roots overlap")
    return rows


def _classify_dependency(
        path: Path, root_mappings: Sequence[Mapping[str, object]]) \
        -> tuple[str, str | None]:
    original = _normalized_absolute(path)
    matches = [
        str(row["role"]) for row in root_mappings
        if original.is_relative_to(Path(str(row["original_root"])))
    ]
    if len(matches) > 1:
        _fail(f"dependency belongs to multiple SDK roots: {original}")
    if matches:
        return SDK_CLASS, matches[0]
    return PROVENANCE_CLASS, None


def _process_record(captured: Mapping[str, object]) -> dict[str, object]:
    command = captured.get("command")
    stdout_utf8 = captured.get("stdout_utf8")
    stderr_utf8 = captured.get("stderr_utf8")
    if not isinstance(command, list) \
            or not all(isinstance(item, str) and item for item in command) \
            or not isinstance(captured.get("exit_code"), int) \
            or not isinstance(stdout_utf8, str) \
            or not isinstance(stderr_utf8, str):
        _fail("captured dependency process is malformed")
    return {
        "role": captured["role"],
        "command": command,
        "tool": _tool_record(command),
        "exit_code": captured["exit_code"],
        "stdout_utf8": stdout_utf8,
        "stdout_sha256": _sha(stdout_utf8.encode("utf-8")),
        "stderr_utf8": stderr_utf8,
        "stderr_sha256": _sha(stderr_utf8.encode("utf-8")),
    }


def materialize_captured_runs(
        captured_runs: Sequence[Mapping[str, object]], *,
        projection_root: Path, receipt_path: Path,
        command_authority: Mapping[str, object]) -> dict[str, object]:
    """Materialize already captured dependency stdout into sealed bytes.

    Kept public for the hostile tests.  Production callers must obtain every
    captured run from ``subprocess.run`` in this module's ``main``.
    """

    _reject_receipt_inside_projection(projection_root, receipt_path)
    if projection_root.exists() or projection_root.is_symlink():
        raise FileExistsError(projection_root)
    if receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError(receipt_path)
    if [run.get("role") for run in captured_runs] != list(RUN_ROLES):
        _fail("dependency run roles/order differ")
    expected_commands = _validate_command_authority(command_authority)
    mappings = _root_mappings(command_authority, projection_root)
    projection_root.mkdir(parents=True)
    runs = []
    for captured in captured_runs:
        command = captured.get("command")
        stdout_utf8 = captured.get("stdout_utf8")
        stderr_utf8 = captured.get("stderr_utf8")
        if not isinstance(command, list) \
                or not all(isinstance(item, str) and item for item in command) \
                or command != expected_commands.get(str(captured.get("role"))) \
                or captured.get("exit_code") != 0 \
                or not isinstance(stdout_utf8, str) \
                or not isinstance(stderr_utf8, str):
            _fail("captured dependency run is malformed or failed")
        occurrences = _parse_make_dependencies(stdout_utf8)
        unique_paths = _ordered_unique_dependencies(occurrences)
        dependency_rows = []
        for path in unique_paths:
            classification, root_role = _classify_dependency(path, mappings)
            dependency_rows.append(_dependency_record(
                path, projection_root, classification=classification,
                sdk_root_role=root_role))
        sdk_dependencies = [
            row for row in dependency_rows
            if row["classification"] == SDK_CLASS]
        provenance_dependencies = [
            row for row in dependency_rows
            if row["classification"] == PROVENANCE_CLASS]
        process = _process_record(captured)
        runs.append({
            **process,
            "dependency_occurrence_count": len(occurrences),
            "unique_dependency_path_count": len(unique_paths),
            "duplicate_dependency_occurrence_count": (
                len(occurrences) - len(unique_paths)),
            "load_bearing_sdk_dependency_count": len(sdk_dependencies),
            "provenance_only_dependency_count": len(provenance_dependencies),
            "load_bearing_sdk_dependencies": sdk_dependencies,
            "provenance_only_dependencies": provenance_dependencies,
        })
    projection_rows = _projection_rows(projection_root)
    value: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "closure_claim": CLOSURE_CLAIM,
        "command_authority": dict(command_authority),
        "root_mappings": mappings,
        "runs": runs,
        "projection_root": str(projection_root.resolve(strict=True)),
        "projection_file_count": len(projection_rows),
        "projection_payload_bytes": sum(
            int(row["bytes"]) for row in projection_rows),
        "projection_tree_sha256": _sha(_canonical(projection_rows)),
        "dependency_run_count": len(runs),
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    value["receipt_sha256"] = _sha(_canonical(value))
    validate_header_projection(value, projection_root)
    _write_create_only(
        receipt_path,
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return value


def _validate_projection_envelope(
        value: Mapping[str, object], projection_root: Path) \
        -> tuple[Path, list[Mapping[str, object]], list[Mapping[str, object]]]:
    required_top = {
        "schema", "status", "runs", "projection_root",
        "projection_file_count", "projection_payload_bytes",
        "projection_tree_sha256", "dependency_run_count",
        "closure_claim", "command_authority", "root_mappings",
        "clock_read_count", "gpu_kernel_launch_count", "formal_worker_count",
        "registered_performance_timing_count", "receipt_sha256",
    }
    unsigned = dict(value)
    seal = unsigned.pop("receipt_sha256", None)
    root = projection_root.resolve(strict=True)
    if set(value) != required_top or value.get("schema") != SCHEMA \
            or value.get("status") != STATUS \
            or value.get("closure_claim") != CLOSURE_CLAIM \
            or value.get("projection_root") != str(root) \
            or value.get("dependency_run_count") != len(RUN_ROLES) \
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                "clock_read_count", "gpu_kernel_launch_count",
                "formal_worker_count", "registered_performance_timing_count")) \
            or seal != _sha(_canonical(unsigned)):
        _fail("header projection envelope differs")
    authority = value.get("command_authority")
    mappings = value.get("root_mappings")
    runs = value.get("runs")
    if not isinstance(authority, Mapping) \
            or not isinstance(mappings, list) or len(mappings) != 2 \
            or not all(isinstance(row, Mapping) for row in mappings) \
            or not isinstance(runs, list) \
            or [run.get("role") if isinstance(run, Mapping) else None
                for run in runs] != list(RUN_ROLES):
        _fail("header projection run roles differ")
    reconstructed_commands = _validate_command_authority_shape_no_io(
        authority)
    roots = authority.get("original_sdk_roots")
    expected = authority.get("expected_commands")
    if not isinstance(roots, Mapping) \
            or set(roots) != {"optix_include", "cuda_include"} \
            or not isinstance(expected, list) \
            or [row.get("role") if isinstance(row, Mapping) else None
                for row in expected] != list(RUN_ROLES):
        _fail("header projection command authority differs")
    for row in expected:
        if not isinstance(row, Mapping) or set(row) != {
                "role", "command", "command_sha256"} \
                or not isinstance(row.get("command"), list) \
                or not all(isinstance(item, str) and item
                           for item in row["command"]) \
                or row.get("command_sha256") \
                != _command_sha256(row["command"]):
            _fail("header projection expected command differs")
    mapping_by_role: dict[str, Mapping[str, object]] = {}
    for row in mappings:
        if set(row) != {
                "role", "original_root", "projection_relative_root",
                "projected_root", "roots_distinct_and_nonoverlapping"} \
                or row.get("role") not in {"optix_include", "cuda_include"} \
                or row.get("roots_distinct_and_nonoverlapping") is not True:
            _fail("header projection root mapping schema differs")
        role = str(row["role"])
        if role in mapping_by_role:
            _fail("header projection root mapping is duplicated")
        original = Path(str(row["original_root"]))
        relative = _independent_projection_relative_from_record(original)
        projected = root / Path(relative)
        if row.get("projection_relative_root") != relative \
                or row.get("projected_root") != str(projected) \
                or original == projected \
                or original.is_relative_to(projected) \
                or projected.is_relative_to(original):
            _fail("header projection roots are not distinct/mapped")
        root_record = roots.get(role)
        if not isinstance(root_record, Mapping) \
                or root_record.get("resolved_path") != str(original):
            _fail("header projection root authority differs")
        mapping_by_role[role] = row
    if set(mapping_by_role) != {"optix_include", "cuda_include"}:
        _fail("header projection root mapping roles differ")
    original_roots = [
        Path(str(mapping_by_role[role]["original_root"]))
        for role in ("optix_include", "cuda_include")]
    projected_roots = [
        Path(str(mapping_by_role[role]["projected_root"]))
        for role in ("optix_include", "cuda_include")]
    for first, second, label in (
            (original_roots[0], original_roots[1], "original"),
            (projected_roots[0], projected_roots[1], "projected")):
        if first == second or first.is_relative_to(second) \
                or second.is_relative_to(first):
            _fail(f"header projection {label} SDK roots overlap")
    if reconstructed_commands != {
            str(row["role"]): list(row["command"])
            for row in expected if isinstance(row, Mapping)}:
        _fail("header projection command reconstruction differs")
    return root, runs, mappings


def _independent_projection_relative_from_record(path: Path) -> str:
    """Pure lexical projection mapping usable without original bytes."""

    return _projection_relative(path).as_posix()


def validate_projection_only(
        value: Mapping[str, object], projection_root: Path) -> None:
    """Verify the sealed projection after the original SDK is unavailable."""

    root, runs, mappings = _validate_projection_envelope(
        value, projection_root)
    authority = value["command_authority"]
    assert isinstance(authority, Mapping)
    expected_rows = authority["expected_commands"]
    assert isinstance(expected_rows, list)
    expected_commands = {
        str(row["role"]): list(row["command"])
        for row in expected_rows if isinstance(row, Mapping)
    }
    tools = authority["tools"]
    assert isinstance(tools, Mapping)
    referenced_projection_paths: set[str] = set()
    for run in runs:
        if not isinstance(run, Mapping) or set(run) != {
                "role", "command", "tool", "exit_code", "stdout_utf8",
                "stdout_sha256", "stderr_utf8", "stderr_sha256",
                "dependency_occurrence_count", "unique_dependency_path_count",
                "duplicate_dependency_occurrence_count",
                "load_bearing_sdk_dependency_count",
                "provenance_only_dependency_count",
                "load_bearing_sdk_dependencies",
                "provenance_only_dependencies"}:
            _fail("header projection run schema differs")
        command = run.get("command")
        stdout_utf8 = run.get("stdout_utf8")
        stderr_utf8 = run.get("stderr_utf8")
        if not isinstance(command, list) \
                or not all(isinstance(item, str) and item for item in command) \
                or command != expected_commands.get(str(run.get("role"))) \
                or run.get("tool") != tools[
                    "cxx" if run.get("role") == DIRECT_ROLE else "nvcc"] \
                or run.get("exit_code") != 0 \
                or not isinstance(stdout_utf8, str) \
                or run.get("stdout_sha256") \
                != _sha(stdout_utf8.encode("utf-8")) \
                or not isinstance(stderr_utf8, str) \
                or run.get("stderr_sha256") \
                != _sha(stderr_utf8.encode("utf-8")):
            _fail("header projection process identity differs")
        occurrences = _parse_make_dependencies(stdout_utf8)
        parsed = _ordered_unique_dependencies(occurrences)
        sdk_dependencies = run.get("load_bearing_sdk_dependencies")
        provenance_dependencies = run.get("provenance_only_dependencies")
        if not isinstance(sdk_dependencies, list) \
                or not isinstance(provenance_dependencies, list) \
                or len(sdk_dependencies) + len(provenance_dependencies) \
                != len(parsed) \
                or run.get("dependency_occurrence_count") \
                != len(occurrences) \
                or run.get("unique_dependency_path_count") != len(parsed) \
                or run.get("duplicate_dependency_occurrence_count") \
                != len(occurrences) - len(parsed) \
                or run.get("load_bearing_sdk_dependency_count") \
                != len(sdk_dependencies) \
                or run.get("provenance_only_dependency_count") \
                != len(provenance_dependencies):
            _fail("header projection dependency count differs from stdout")
        all_rows = [*sdk_dependencies, *provenance_dependencies]
        by_original: dict[str, Mapping[str, object]] = {}
        for observed in all_rows:
            if not isinstance(observed, Mapping):
                _fail("header projection dependency schema differs")
            original_text = observed.get("original_path")
            if not isinstance(original_text, str) \
                    or original_text in by_original:
                _fail("header projection dependency identity duplicated")
            by_original[original_text] = observed
        if set(by_original) != {
                str(_normalized_absolute(path)) for path in parsed}:
            _fail("header projection dependencies differ from stdout")
        for observed in sdk_dependencies:
            if not isinstance(observed, Mapping) or set(observed) != {
                    "original_path", "resolved_path", "symlink_chain",
                    "bytes", "sha256", "classification", "sdk_root_role",
                    "projection_path", "projected_bytes",
                    "projected_sha256"} \
                    or observed.get("classification") != SDK_CLASS \
                    or observed.get("sdk_root_role") not in {
                        "optix_include", "cuda_include"}:
                _fail("projected SDK dependency schema differs")
            original = Path(str(observed["original_path"]))
            role_mapping = next(
                row for row in mappings
                if row["role"] == observed["sdk_root_role"])
            if not original.is_relative_to(Path(str(
                    role_mapping["original_root"]))):
                _fail("projected SDK dependency escapes its original root")
            relative = _independent_projection_relative_from_record(original)
            projected = root / Path(relative)
            payload = projected.read_bytes() if projected.is_file() else b""
            if observed.get("projection_path") != relative \
                    or not projected.is_file() or projected.is_symlink() \
                    or observed.get("bytes") != len(payload) \
                    or observed.get("sha256") != _sha(payload) \
                    or observed.get("projected_bytes") != len(payload) \
                    or observed.get("projected_sha256") \
                    != _sha(payload):
                _fail("projected SDK dependency bytes differ")
            referenced_projection_paths.add(relative)
        for observed in provenance_dependencies:
            if not isinstance(observed, Mapping) or set(observed) != {
                    "original_path", "resolved_path", "symlink_chain",
                    "bytes", "sha256", "classification", "sdk_root_role"} \
                    or observed.get("classification") != PROVENANCE_CLASS \
                    or observed.get("sdk_root_role") is not None:
                _fail("provenance-only dependency schema differs")
            original = Path(str(observed["original_path"]))
            if any(original.is_relative_to(Path(str(row["original_root"])))
                   for row in mappings):
                _fail("SDK dependency was relabelled as provenance-only")
    projection_rows = _projection_rows(root)
    if {str(row["path"]) for row in projection_rows} \
            != referenced_projection_paths \
            or value.get("projection_file_count") != len(projection_rows) \
            or value.get("projection_payload_bytes") \
            != sum(int(row["bytes"]) for row in projection_rows) \
            or value.get("projection_tree_sha256") \
            != _sha(_canonical(projection_rows)):
        _fail("header projection exact file set/tree differs")


def validate_provenance(
        value: Mapping[str, object], projection_root: Path) -> None:
    """Verify original tools/sources/SDK roots and every dependency byte."""

    validate_projection_only(value, projection_root)
    authority = value.get("command_authority")
    assert isinstance(authority, Mapping)
    expected_commands = _validate_command_authority(authority)
    mappings = _root_mappings(authority, projection_root)
    if value.get("root_mappings") != mappings:
        _fail("header projection original-to-projected root mapping differs")
    runs = value.get("runs")
    assert isinstance(runs, list)
    for run in runs:
        assert isinstance(run, Mapping)
        command = run["command"]
        assert isinstance(command, list)
        if command != expected_commands[str(run["role"])] \
                or run.get("tool") != _tool_record(command):
            _fail("header projection exact role command differs")
        occurrences = _parse_make_dependencies(str(run["stdout_utf8"]))
        unique = _ordered_unique_dependencies(occurrences)
        sdk_dependencies = run["load_bearing_sdk_dependencies"]
        provenance_dependencies = run["provenance_only_dependencies"]
        assert isinstance(sdk_dependencies, list)
        assert isinstance(provenance_dependencies, list)
        by_original = {
            str(row["original_path"]): row
            for row in [*sdk_dependencies, *provenance_dependencies]
            if isinstance(row, Mapping)
        }
        for path in unique:
            original = _normalized_absolute(path)
            observed = by_original.get(str(original))
            classification, root_role = _classify_dependency(path, mappings)
            if not isinstance(observed, Mapping) \
                    or observed.get("classification") != classification \
                    or observed.get("sdk_root_role") != root_role:
                _fail("header projection dependency classification differs")
            resolved = original.resolve(strict=True)
            payload = resolved.read_bytes()
            if observed.get("resolved_path") != str(resolved) \
                    or observed.get("symlink_chain") != _symlink_chain(original) \
                    or observed.get("bytes") != len(payload) \
                    or observed.get("sha256") != _sha(payload):
                _fail("header projection original dependency bytes differ")
            if classification == SDK_CLASS:
                projected = Path(str(value["projection_root"])) / Path(str(
                    observed["projection_path"]))
                if projected.read_bytes() != payload:
                    _fail("header projection copied SDK bytes differ")


def validate_header_projection(
        value: Mapping[str, object], projection_root: Path) -> None:
    """Full verifier: projection-only integrity plus original provenance."""

    validate_provenance(value, projection_root)


def _run(role: str, command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, capture_output=True, check=False)
    try:
        stdout_utf8 = completed.stdout.decode("utf-8")
        stderr_utf8 = completed.stderr.decode("utf-8")
    except UnicodeError as error:
        raise RuntimeError(f"dependency output is not UTF-8: {role}") from error
    captured: dict[str, object] = {
        "role": role, "command": command, "exit_code": 0,
        "stdout_utf8": stdout_utf8, "stderr_utf8": stderr_utf8,
    }
    captured["exit_code"] = completed.returncode
    if completed.returncode != 0:
        raise DependencyCommandFailure(captured)
    return captured


def _write_dependency_failure(
        *, receipt_path: Path, completed: Sequence[Mapping[str, object]],
        failure: DependencyCommandFailure) -> dict[str, object]:
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.load_bearing_header_projection_failure.v1",
        "status": "FAIL__DEPENDENCY_COMMAND__NO_PROJECTION_CREATED",
        "completed_runs": [_process_record(run) for run in completed],
        "failed_run": _process_record(failure.captured),
        "projection_created": False,
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    value["receipt_sha256"] = _sha(_canonical(value))
    _write_create_only(
        receipt_path,
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return value


def _write_materialization_failure(
        *, receipt_path: Path, captured: Sequence[Mapping[str, object]],
        projection_root: Path, error: Exception) -> dict[str, object]:
    projection_exists = projection_root.exists()
    rows = _projection_rows(projection_root) if projection_exists else []
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.load_bearing_header_projection_failure.v2",
        "status": "FAIL__MATERIALIZATION__PARTIAL_PROJECTION_QUARANTINED",
        "completed_runs": [_process_record(run) for run in captured],
        "materialization_error": {
            "type": type(error).__name__,
            "message": str(error),
        },
        "projection_root": str(projection_root.absolute()),
        "projection_created": projection_exists,
        "partial_projection_file_count": len(rows),
        "partial_projection_payload_bytes": sum(
            int(row["bytes"]) for row in rows),
        "partial_projection_tree_sha256": _sha(_canonical(rows)),
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    value["receipt_sha256"] = _sha(_canonical(value))
    _write_create_only(
        receipt_path,
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nvcc", type=Path, required=True)
    parser.add_argument("--cxx", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--compaction-source", type=Path, required=True)
    parser.add_argument("--direct-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--projection-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    _reject_receipt_inside_projection(args.projection_root, args.receipt)
    if not args.compute_capability.startswith("sm_") \
            or not args.compute_capability[3:].isdigit():
        _fail("compute capability must be sm_<digits>")
    nvcc = args.nvcc.resolve(strict=True)
    cxx = args.cxx.resolve(strict=True)
    sources = [
        args.device_source.resolve(strict=True),
        args.compaction_source.resolve(strict=True),
        args.direct_source.resolve(strict=True),
    ]
    optix = args.optix_include.resolve(strict=True)
    cuda = args.cuda_include.resolve(strict=True)
    if not all(path.is_file() for path in (nvcc, cxx, *sources)) \
            or not optix.is_dir() or not cuda.is_dir():
        _fail("header projection inputs are not regular files/directories")
    authority = build_command_authority(
        nvcc=nvcc, cxx=cxx,
        matched_device_source=sources[0],
        relation_compaction_source=sources[1], direct_source=sources[2],
        optix_include=optix, cuda_include=cuda,
        compute_capability=args.compute_capability)
    expected_rows = authority["expected_commands"]
    assert isinstance(expected_rows, list)
    commands = [
        list(row["command"]) for row in expected_rows
        if isinstance(row, Mapping)]
    captured: list[dict[str, object]] = []
    try:
        for role, command in zip(RUN_ROLES, commands, strict=True):
            captured.append(_run(role, command))
    except DependencyCommandFailure as failure:
        value = _write_dependency_failure(
            receipt_path=args.receipt, completed=captured, failure=failure)
        print(json.dumps({
            "status": value["status"],
            "failed_role": value["failed_run"]["role"],
            "exit_code": value["failed_run"]["exit_code"],
            "receipt_sha256": value["receipt_sha256"],
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
        }, sort_keys=True))
        return 1
    try:
        value = materialize_captured_runs(
            captured, projection_root=args.projection_root,
            receipt_path=args.receipt, command_authority=authority)
    except Exception as error:
        value = _write_materialization_failure(
            receipt_path=args.receipt, captured=captured,
            projection_root=args.projection_root, error=error)
        print(json.dumps({
            "status": value["status"],
            "materialization_error_type": value["materialization_error"][
                "type"],
            "partial_projection_file_count": value[
                "partial_projection_file_count"],
            "receipt_sha256": value["receipt_sha256"],
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
        }, sort_keys=True))
        return 1
    print(json.dumps({
        "status": value["status"],
        "projection_file_count": value["projection_file_count"],
        "projection_payload_bytes": value["projection_payload_bytes"],
        "projection_tree_sha256": value["projection_tree_sha256"],
        "receipt_sha256": value["receipt_sha256"],
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
