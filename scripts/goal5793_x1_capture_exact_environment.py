"""Capture the exact Goal5793 X1 Linux execution environment.

This collector performs no build, GPU call, network call, candidate work, or
timing. It binds the frozen 326-file source surface, a separately frozen
non-GPU direct-native build trace, an explicit Python home, the formal Numba
leaf cache, the final native and all named runtime libraries. Execution still
requires a later reviewed stage authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from typing import Any, Mapping

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


REQUEST_SCHEMA = "rtdl.goal5793.x1.exact_environment_capture_request.v2"
RESULT_SCHEMA = "rtdl.goal5793.x1.exact_environment_capture.v2"
EXPECTED_RUNPATH = "$ORIGIN/goal5793_x1_deps"
EXPECTED_RUNTIME_KEYS = {
    "libcuda.so.1", "libnvrtc.so.12", "libstdc++.so.6", "libm.so.6",
    "libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2",
}
EXPECTED_DLOPEN_KEYS = {"libnvoptix.so.1"}
EXPECTED_ROLE_COUNTS = {
    "any_hit": 7, "bounds": 4, "closest_hit": 5, "finalize": 8,
    "intersection": 4, "make_ray": 8, "miss": 8,
}
EXPECTED_POLICY_PATHS = {
    "formal_codegen": "src/rtdsl/v4_callback_numba_codegen.py",
    "isolated_compile_child": "src/rtdsl/_v4_numba_compile_child.py",
    "ptx_auditor": "src/rtdsl/v4_callback_poc.py",
}
REQUEST_KEYS = {
    "schema", "stage_id", "python_executable", "python_loader", "python_home", "source_root",
    "source_authority_file", "source_bundle", "source_sys_path_entries",
    "cuda_entry_header_root", "optix_header_root", "linker", "native_library",
    "numba_cache_root", "native_trace_authority", "native_trace_evidence",
    "native_trace_evidence_twin", "runtime_libraries", "dlopen_libraries",
    "expected_rtdl_build_id", "expected_gnu_build_id", "expected_cuda_arch",
    "environment",
}


class CaptureError(ValueError):
    pass


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _absolute_regular(path_value: object, context: str) -> Path:
    if not isinstance(path_value, str):
        raise CaptureError(f"{context}_not_string")
    path = Path(path_value)
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise CaptureError(f"{context}_not_explicit_regular_file")
    return path


def _absolute_directory(path_value: object, context: str) -> Path:
    if not isinstance(path_value, str):
        raise CaptureError(f"{context}_not_string")
    path = Path(path_value)
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise CaptureError(f"{context}_not_explicit_directory")
    return path


def _file_record(path: Path, spelling: str) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    return {
        "declared_path": spelling,
        "resolved_path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": _sha256(resolved),
    }


def _tree_rows(root: Path, context: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix().encode("utf-8")):
        if path.is_symlink():
            raise CaptureError(f"{context}_symlink_forbidden:{path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise CaptureError(f"{context}_nonregular_forbidden:{path}")
        rel = path.relative_to(root).as_posix()
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": _sha256(path)})
    if not rows:
        raise CaptureError(f"{context}_empty")
    return rows


def _tree_authority(root: Path, context: str) -> dict[str, object]:
    rows = _tree_rows(root, context)
    return {
        "root": str(root.resolve(strict=True)),
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
        "rows": rows,
        "rows_sha256": _sha256_bytes(canonical_json_bytes(rows)),
    }


def _elf_sections(payload: bytes) -> dict[str, tuple[int, ...]]:
    if len(payload) < 64 or payload[:4] != b"\x7fELF" or payload[4:6] != b"\x02\x01":
        raise CaptureError("not_little_endian_elf64")
    e_shoff = struct.unpack_from("<Q", payload, 0x28)[0]
    e_shentsize = struct.unpack_from("<H", payload, 0x3A)[0]
    e_shnum = struct.unpack_from("<H", payload, 0x3C)[0]
    e_shstrndx = struct.unpack_from("<H", payload, 0x3E)[0]
    if e_shentsize != 64 or not (0 < e_shnum < 65536) or e_shstrndx >= e_shnum:
        raise CaptureError("unsupported_section_table")
    if e_shoff + e_shnum * e_shentsize > len(payload):
        raise CaptureError("section_table_out_of_bounds")
    sections = [struct.unpack_from("<IIQQQQIIQQ", payload, e_shoff + i * e_shentsize) for i in range(e_shnum)]
    shstr = sections[e_shstrndx]
    if shstr[4] + shstr[5] > len(payload):
        raise CaptureError("section_name_table_out_of_bounds")
    names = payload[shstr[4]:shstr[4] + shstr[5]]

    def cstring(offset: int) -> str:
        if offset >= len(names):
            raise CaptureError("string_offset_out_of_bounds")
        end = names.find(b"\0", offset)
        if end < 0:
            raise CaptureError("unterminated_string")
        return names[offset:end].decode("utf-8")

    return {cstring(row[0]): row for row in sections}


def _section_payload(payload: bytes, row: tuple[int, ...], context: str) -> bytes:
    offset, size = row[4], row[5]
    if offset + size > len(payload):
        raise CaptureError(f"{context}_out_of_bounds")
    return payload[offset:offset + size]


def _parse_gnu_build_id_note(note: bytes) -> str:
    offset = 0
    matches: list[str] = []
    while offset + 12 <= len(note):
        namesz, descsz, note_type = struct.unpack_from("<III", note, offset)
        offset += 12
        name_end = offset + namesz
        desc_start = (name_end + 3) & ~3
        desc_end = desc_start + descsz
        next_offset = (desc_end + 3) & ~3
        if next_offset > len(note):
            raise CaptureError("gnu_build_id_note_truncated")
        if note_type == 3 and note[offset:name_end].rstrip(b"\0") == b"GNU":
            matches.append(note[desc_start:desc_end].hex())
        offset = next_offset
    if len(matches) != 1 or not re.fullmatch(r"[0-9a-f]{40}", matches[0]):
        raise CaptureError("gnu_build_id_not_unique_sha1_length")
    return matches[0]


def _elf_identity(payload: bytes) -> dict[str, object]:
    named = _elf_sections(payload)
    dynamic, dynstr, note = named.get(".dynamic"), named.get(".dynstr"), named.get(".note.gnu.build-id")
    if dynamic is None or dynstr is None or note is None:
        raise CaptureError("elf_required_sections_absent")
    strings = _section_payload(payload, dynstr, "dynstr")

    def cstring(offset: int) -> str:
        if offset >= len(strings):
            raise CaptureError("dynamic_string_offset_out_of_bounds")
        end = strings.find(b"\0", offset)
        if end < 0:
            raise CaptureError("dynamic_string_unterminated")
        return strings[offset:end].decode("utf-8")

    needed: list[str] = []
    rpath: list[str] = []
    runpath: list[str] = []
    if (dynamic[9] or 16) != 16:
        raise CaptureError("dynamic_entry_size_invalid")
    for offset in range(dynamic[4], dynamic[4] + dynamic[5], 16):
        tag, value = struct.unpack_from("<qQ", payload, offset)
        if tag == 0:
            break
        if tag == 1:
            needed.append(cstring(value))
        elif tag == 15:
            rpath.append(cstring(value))
        elif tag == 29:
            runpath.append(cstring(value))
    return {
        "dt_needed": needed, "rpath": rpath, "runpath": runpath,
        "gnu_build_id": _parse_gnu_build_id_note(_section_payload(payload, note, "gnu_build_id_note")),
    }


def _verify_plain_seal(document: Mapping[str, Any], field: str) -> None:
    stored = document.get(field)
    if not isinstance(stored, str) or not re.fullmatch(r"[0-9a-f]{64}", stored):
        raise CaptureError(f"{field}_malformed")
    body = dict(document)
    body.pop(field, None)
    if _sha256_bytes(canonical_json_bytes(body)) != stored:
        raise CaptureError(f"{field}_mismatch")


def _verify_source_authority(path: Path, source_root: Path) -> dict[str, object]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("schema") != "rtdl.goal5793.s0.source_and_admission_freeze.v1":
        raise CaptureError("source_authority_schema_mismatch")
    _verify_plain_seal(document, "source_authority_sha256")
    declared = document.get("declared_product_native_source_zero_drift_authority")
    if not isinstance(declared, dict) or not isinstance(declared.get("rows"), list):
        raise CaptureError("source_authority_rows_absent")
    rows = declared["rows"]
    live = [{"path": row["path"], "sha256": row["sha256"], "size_bytes": row["bytes"]}
            for row in _tree_rows(source_root, "source_tree")]
    if canonical_json_bytes(live) != canonical_json_bytes(rows):
        raise CaptureError("source_tree_not_exact_s0_326_surface")
    expected_summary = {
        "file_count": 326, "total_bytes": 14587884, "rows_canonical_bytes": 46672,
        "rows_sha256": "f26b55e6d9a120a34882e9c7ada44df5503f1f90f83db893d1d6957ab0202f97",
    }
    if declared.get("summary") != expected_summary:
        raise CaptureError("source_authority_summary_mismatch")
    return {"file": _file_record(path, str(path)), "source_authority_sha256": document["source_authority_sha256"], "summary": expected_summary}


def _verify_trace_authority(authority_path: Path, archive_path: Path, twin_path: Path) -> tuple[dict[str, object], dict[str, Any]]:
    document = json.loads(authority_path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("schema") != "rtdl.goal5793.x1.native_trace_authority.v1":
        raise CaptureError("native_trace_authority_schema_mismatch")
    expected = seal_document(document, seal_field="authority_sha256", domain="rtdl.goal5793.x1.native_trace_authority", version=1)
    if document.get("authority_sha256") != expected:
        raise CaptureError("native_trace_authority_seal_mismatch")
    archive_sha = _sha256(archive_path)
    if archive_sha != _sha256(twin_path) or archive_path.stat().st_size != twin_path.stat().st_size:
        raise CaptureError("native_trace_archive_twin_mismatch")
    evidence = document.get("evidence_archive")
    if not isinstance(evidence, dict) or evidence.get("sha256") != archive_sha or evidence.get("bytes") != archive_path.stat().st_size:
        raise CaptureError("native_trace_archive_identity_mismatch")
    if document.get("trace", {}).get("forbidden_gpu_marker_hit_count") != 0 or document.get("stripped_rebuilds_byte_identical") is not True:
        raise CaptureError("native_trace_scope_or_rebuild_mismatch")
    record = {
        "authority": _file_record(authority_path, str(authority_path)), "authority_sha256": document["authority_sha256"],
        "evidence": _file_record(archive_path, str(archive_path)), "twin": _file_record(twin_path, str(twin_path)),
    }
    return record, document


def _verify_numba_cache(root: Path, source_root: Path, python_sha256: str) -> dict[str, object]:
    tree = _tree_authority(root, "numba_cache")
    if tree["file_count"] != 44:
        raise CaptureError("numba_cache_artifact_count_mismatch")
    role_counts: dict[str, int] = {}
    rows: list[dict[str, object]] = []
    policy_hashes = {name: _sha256(source_root / relative) for name, relative in EXPECTED_POLICY_PATHS.items()}
    for file_row in tree["rows"]:
        relative = str(file_row["path"])
        if not re.fullmatch(r"[0-9a-f]{64}/artifact\.json", relative):
            raise CaptureError("numba_cache_noncanonical_member")
        path = root / relative
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or set(document) != {"schema", "key", "key_sha256", "artifact"}:
            raise CaptureError("numba_cache_artifact_schema_mismatch")
        key, artifact = document["key"], document["artifact"]
        if not isinstance(key, dict) or not isinstance(artifact, dict):
            raise CaptureError("numba_cache_key_or_artifact_not_object")
        key_sha = _sha256_bytes(canonical_json_bytes(key))
        if document["schema"] != "rtdl.v4.formal_numba_leaf_cache.v1" or key_sha != document["key_sha256"] or key_sha != path.parent.name:
            raise CaptureError("numba_cache_key_identity_mismatch")
        if key.get("python_executable_sha256") != python_sha256 or key.get("expected_python_version") != "3.12.3":
            raise CaptureError("numba_cache_python_identity_mismatch")
        if key.get("expected_numpy_version") != "2.4.4" or key.get("expected_numba_version") != "0.65.1":
            raise CaptureError("numba_cache_package_version_mismatch")
        if key.get("compute_capability") != [6, 1] or artifact.get("compute_capability") != [6, 1]:
            raise CaptureError("numba_cache_compute_capability_mismatch")
        if key.get("compiler_policy_source_sha256") != policy_hashes:
            raise CaptureError("numba_cache_policy_source_mismatch")
        ptx = artifact.get("ptx")
        if not isinstance(ptx, str) or _sha256_bytes(ptx.encode("utf-8")) != artifact.get("ptx_sha256"):
            raise CaptureError("numba_cache_ptx_identity_mismatch")
        if artifact.get("ptx_target") != "sm_61" or artifact.get("numba_version") != "0.65.1" or artifact.get("python_version") != "3.12.3":
            raise CaptureError("numba_cache_artifact_toolchain_mismatch")
        role = artifact.get("role")
        if role != key.get("role") or role not in EXPECTED_ROLE_COUNTS:
            raise CaptureError("numba_cache_role_mismatch")
        role_counts[str(role)] = role_counts.get(str(role), 0) + 1
        rows.append({"key_sha256": key_sha, "role": role, "ptx_sha256": artifact["ptx_sha256"]})
    if role_counts != EXPECTED_ROLE_COUNTS:
        raise CaptureError("numba_cache_role_distribution_mismatch")
    rows.sort(key=lambda row: str(row["key_sha256"]).encode("utf-8"))
    return {**tree, "validated_artifacts": rows, "role_counts": role_counts,
            "validated_artifact_set_sha256": _sha256_bytes(canonical_json_bytes(rows))}


def _capture_python_environment(
    python: Path,
    loader: Path,
    library_path: Path,
    environment: Mapping[str, str | None],
) -> dict[str, object]:
    actual_env = {key: value for key, value in environment.items() if value is not None}
    code = ("import json,sys,numpy,numba,llvmlite; print(json.dumps({'sys_path':sys.path,'prefix':sys.prefix,"
            "'executable':sys.executable,'numpy':[numpy.__version__,numpy.__file__],"
            "'numba':[numba.__version__,numba.__file__],'llvmlite':[llvmlite.__version__,llvmlite.__file__]},sort_keys=True))")
    completed = subprocess.run(
                               [str(loader), "--library-path", str(library_path), str(python), "-S", "-s", "-c", code],
                               stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=actual_env, check=False, timeout=120)
    if completed.returncode != 0:
        raise CaptureError("frozen_python_environment_probe_failed:" + completed.stderr.decode("utf-8", errors="replace")[:300])
    value = json.loads(completed.stdout.decode("utf-8"))
    if not isinstance(value, dict):
        raise CaptureError("frozen_python_environment_probe_invalid")
    return value


def capture(request: object) -> dict[str, Any]:
    if not isinstance(request, Mapping) or set(request) != REQUEST_KEYS:
        raise CaptureError("request_keyset_mismatch")
    if request["schema"] != REQUEST_SCHEMA or not isinstance(request["stage_id"], str) or not request["stage_id"]:
        raise CaptureError("request_schema_or_stage_mismatch")
    build_id, gnu_build_id = request["expected_rtdl_build_id"], request["expected_gnu_build_id"]
    if build_id != "goal5793-x1-sm61" or not isinstance(gnu_build_id, str) or not re.fullmatch(r"[0-9a-f]{40}", gnu_build_id):
        raise CaptureError("deterministic_build_identity_invalid")
    if request["expected_cuda_arch"] != "sm_61":
        raise CaptureError("cuda_arch_mismatch")

    python = _absolute_regular(request["python_executable"], "python")
    python_home = _absolute_directory(request["python_home"], "python_home")
    python_loader = _absolute_regular(request["python_loader"], "python_loader")
    source = _absolute_directory(request["source_root"], "source_root")
    source_authority_path = _absolute_regular(request["source_authority_file"], "source_authority")
    source_bundle = _absolute_regular(request["source_bundle"], "source_bundle")
    cuda_headers = _absolute_directory(request["cuda_entry_header_root"], "cuda_entry_header_root")
    optix_headers = _absolute_directory(request["optix_header_root"], "optix_header_root")
    linker = _absolute_regular(request["linker"], "linker")
    native = _absolute_regular(request["native_library"], "native")
    numba_cache = _absolute_directory(request["numba_cache_root"], "numba_cache_root")
    trace_authority_path = _absolute_regular(request["native_trace_authority"], "native_trace_authority")
    trace_evidence_path = _absolute_regular(request["native_trace_evidence"], "native_trace_evidence")
    trace_twin_path = _absolute_regular(request["native_trace_evidence_twin"], "native_trace_evidence_twin")
    entries_value = request["source_sys_path_entries"]
    if not isinstance(entries_value, list) or not entries_value or not all(isinstance(v, str) for v in entries_value):
        raise CaptureError("source_sys_path_entries_invalid")
    entries = [str(_absolute_directory(v, f"source_sys_path_{i}").resolve(strict=True)) for i, v in enumerate(entries_value)]
    if entries[0] != str((source / "src").resolve(strict=True)):
        raise CaptureError("source_sys_path_first_entry_not_source_src")

    environment = request["environment"]
    if not isinstance(environment, Mapping):
        raise CaptureError("environment_not_object")
    expected_environment = {
        "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
        "PYTHONHOME": str(python_home.resolve(strict=True)), "PYTHONPATH": os.pathsep.join(entries),
        "LD_LIBRARY_PATH": str((python_home / "runtime_deps").resolve(strict=True)), "LD_PRELOAD": None,
        "PYTHONHASHSEED": "0", "PYTHONNOUSERSITE": "1", "PYTHONSAFEPATH": "1", "PYTHONDONTWRITEBYTECODE": "1",
    }
    if canonical_json_bytes(environment) != canonical_json_bytes(expected_environment):
        raise CaptureError("environment_vector_mismatch")
    python_runtime_deps = (python_home / "runtime_deps").resolve(strict=True)
    if python.resolve(strict=True) != (python_home / "bin/python3.12").resolve(strict=True):
        raise CaptureError("python_executable_not_inside_frozen_home")
    if python_loader.resolve(strict=True) != (python_home / "runtime_deps/ld-linux-x86-64.so.2").resolve(strict=True):
        raise CaptureError("python_loader_not_inside_frozen_home")

    runtime, dlopen = request["runtime_libraries"], request["dlopen_libraries"]
    if not isinstance(runtime, Mapping) or set(runtime) != EXPECTED_RUNTIME_KEYS:
        raise CaptureError("runtime_library_keyset_mismatch")
    if not isinstance(dlopen, Mapping) or set(dlopen) != EXPECTED_DLOPEN_KEYS:
        raise CaptureError("dlopen_library_keyset_mismatch")
    dependency_root = native.parent / "goal5793_x1_deps"
    runtime_records: dict[str, dict[str, object]] = {}
    for name in sorted(runtime):
        path = _absolute_regular(runtime[name], f"runtime_{name}")
        if path.parent.resolve(strict=True) != dependency_root.resolve(strict=True) or path.name != name:
            raise CaptureError("runtime_library_not_exact_relative_dependency")
        runtime_records[name] = _file_record(path, str(runtime[name]))
    dlopen_records: dict[str, dict[str, object]] = {}
    for name in sorted(dlopen):
        path = _absolute_regular(dlopen[name], f"dlopen_{name}")
        if path.parent.resolve(strict=True) != dependency_root.resolve(strict=True) or path.name != name:
            raise CaptureError("dlopen_library_not_exact_relative_dependency")
        dlopen_records[name] = _file_record(path, str(dlopen[name]))

    native_payload = native.read_bytes()
    elf = _elf_identity(native_payload)
    if set(elf["dt_needed"]) != EXPECTED_RUNTIME_KEYS or elf["rpath"] or elf["runpath"] != [EXPECTED_RUNPATH]:
        raise CaptureError("native_dynamic_contract_mismatch")
    if elf["gnu_build_id"] != gnu_build_id or native_payload.count(build_id.encode("ascii")) != 1:
        raise CaptureError("native_build_identity_mismatch")

    source_authority = _verify_source_authority(source_authority_path, source)
    trace, trace_doc = _verify_trace_authority(trace_authority_path, trace_evidence_path, trace_twin_path)
    if trace_doc["source"]["bundle"]["sha256"] != _sha256(source_bundle):
        raise CaptureError("source_bundle_trace_crossbind_mismatch")
    stripped_hashes = {trace_doc["native_rebuilds"]["reference_stripped"]["sha256"],
                       trace_doc["native_rebuilds"]["traced_stripped"]["sha256"]}
    if stripped_hashes != {_sha256(native)} or trace_doc["top_level_nvcc"]["argv"].count("-arch=sm_61") != 1:
        raise CaptureError("final_native_or_trace_arch_mismatch")

    cuda_tree = _tree_authority(cuda_headers, "cuda_entry_headers")
    optix_tree = _tree_authority(optix_headers, "optix_headers")
    if not (cuda_headers / "cuda.h").is_file():
        raise CaptureError("cuda_h_absent")
    optix_h, function_table = optix_headers / "optix.h", optix_headers / "optix_function_table.h"
    if optix_tree["file_count"] != 14 or not optix_h.is_file() or not function_table.is_file():
        raise CaptureError("optix_header_tree_mismatch")
    if re.search(r"#\s*define\s+OPTIX_VERSION\s+90000\b", optix_h.read_text(encoding="utf-8")) is None:
        raise CaptureError("optix_version_mismatch")
    if re.search(r"#\s*define\s+OPTIX_ABI_VERSION\s+105\b", function_table.read_text(encoding="utf-8")) is None:
        raise CaptureError("optix_abi_mismatch")
    preserved_hashes = {row["sha256"] for row in trace_doc["surviving_external_inputs"]["content_rows"]}
    if cuda_tree["rows"][0]["sha256"] not in preserved_hashes:
        raise CaptureError("cuda_entry_header_not_preserved_by_native_trace")
    copied_optix = {row["path"]: row["sha256"] for row in optix_tree["rows"]}
    traced_optix = [
        row for row in trace_doc["surviving_external_inputs"]["declared_paths"]
        if str(row["declared_path"]).startswith("/home/lestat/vendor/optix-dev/include/")
    ]
    if not traced_optix:
        raise CaptureError("native_trace_has_no_optix_header_reads")
    for row in traced_optix:
        relative = str(row["declared_path"])[len("/home/lestat/vendor/optix-dev/include/"):]
        if copied_optix.get(relative) != row["sha256"]:
            raise CaptureError("traced_optix_header_not_equal_frozen_sdk_tree")
    if _sha256(linker) not in preserved_hashes:
        raise CaptureError("linker_not_preserved_by_native_trace")

    python_home_tree = _tree_authority(python_home, "python_home")
    numba_tree = _verify_numba_cache(numba_cache, source, _sha256(python))
    python_probe = _capture_python_environment(python, python_loader, python_runtime_deps, environment)
    if python_probe.get("prefix") != str(python_home.resolve(strict=True)):
        raise CaptureError("python_prefix_not_frozen_home")
    if python_probe.get("numpy", [None])[0] != "2.4.4" or python_probe.get("numba", [None])[0] != "0.65.1" or python_probe.get("llvmlite", [None])[0] != "0.47.0":
        raise CaptureError("python_package_probe_version_mismatch")
    allowed_roots = [source.resolve(strict=True), python_home.resolve(strict=True)]
    for path_text in python_probe.get("sys_path", []):
        path = Path(path_text)
        if path.exists() and not any(root in (path.resolve(strict=True), *path.resolve(strict=True).parents) for root in allowed_roots):
            raise CaptureError("python_sys_path_existing_entry_outside_frozen_roots")

    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA, "stage_id": request["stage_id"],
        "status": "EXACT_TARGET_EXECUTION_ENVIRONMENT_CAPTURED__REVIEW_REQUIRED__NO_EXECUTION_AUTHORIZATION",
        "request_sha256": _sha256_bytes(canonical_json_bytes(request)),
        "source": {**source_authority, "bundle": _file_record(source_bundle, str(source_bundle))},
        "native_build_trace": trace,
        "python": {"executable": _file_record(python, str(request["python_executable"])),
                   "loader": _file_record(python_loader, str(request["python_loader"])), "home": python_home_tree,
                   "flags": ["-S", "-s"], "probe": python_probe},
        "cuda_entry_headers": cuda_tree, "optix_headers": optix_tree,
        "linker": _file_record(linker, str(request["linker"])),
        "runtime_libraries": runtime_records, "dlopen_libraries": dlopen_records,
        "native": {**_file_record(native, str(request["native_library"])), "rtdl_build_id": build_id,
                   "gnu_build_id": gnu_build_id, "cuda_arch": request["expected_cuda_arch"], "elf_dynamic": elf,
                   "exactly_reproduced_after_strip_by_two_direct_builds": True},
        "numba_cache": numba_tree, "environment": dict(environment),
        "claim_boundary": {
            "native_build_environment_vector_fully_reconstructed": False, "native_rebuild_required_for_exam": False,
            "exact_final_native_bytes_frozen": True, "exact_target_execution_environment_frozen": True,
            "execution_result_count": 0, "generality_exam_count": 0, "usability_evidence_count": 0,
        },
        "scope": {
            "network_calls": 0, "gpu_calls": 0, "candidate_work": 0, "registered_timing": 0,
            "native_build_performed_by_collector": False, "execution_authorized": False,
            "search_entropy_selection_authorized": False, "publication_authorized": False,
        },
        "authority_sha256": "",
    }
    result["authority_sha256"] = seal_document(result, seal_field="authority_sha256",
                                                  domain="rtdl.goal5793.x1.exact_environment_capture", version=2)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise CaptureError("create_only_output_exists")
    result = capture(json.loads(args.request.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(canonical_json_bytes(result) + b"\n")
    print(result["status"], result["authority_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
