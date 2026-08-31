"""Build the local-only Goal5793 X1 environment/shared-native authority.

The builder rehashes preserved Goal5791 target materialization evidence.  It
does not probe a GPU, search ambient libraries, build native code, contact a
network, or execute candidate work.  Missing exact identities remain explicit
blocking facts; they are never filled from the current Windows host.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import tarfile
from typing import Any

from scripts.goal5793_x1_canonical import (
    CANONICALIZATION_NAME,
    canonical_json_bytes,
    seal_document,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT / "history/internal_docs/goal5791_stage_a_v15_rtx4000ada_20260821"
)
OUTPUT_PATH = (
    ROOT
    / "history/internal_docs/goal5793_x1_environment_shared_native_authority_v4_20260822.json"
)
OPTIX_ARCHIVE = ROOT / "history/internal_docs/goal5749_optix9_include_20260811.tar.gz"
OPTIX_ARCHIVE_SHA256 = "7fae86ce3dca2fbc2a47be075f02465cf6ee9d9eafd204234f2882fbdeebee54"
ENVIRONMENT_ADMISSION = (
    ROOT
    / "history/internal_docs/goal5791_stage_a_v15_environment_repair_20260821/ENVIRONMENT_ADMISSION.json"
)
ENVIRONMENT_ADMISSION_SHA256 = (
    "1c920552e7a18f6a598505704e42883949b30959da5f08f0c5a89eebbf326f4d"
)
SUPERSEDED_V2_PATH = (
    ROOT
    / "history/internal_docs/goal5793_x1_environment_shared_native_authority_v2_20260822.json"
)
SUPERSEDED_V2_FILE_SHA256 = (
    "c8ec8e4b7fa612d15cabe71cee388f6aa7b9e6473bac4df42a32c944ccedc5d2"
)
SUPERSEDED_V1_PATH = (
    ROOT
    / "history/internal_docs/goal5793_x1_environment_shared_native_authority_20260822.json"
)
SUPERSEDED_V1_FILE_SHA256 = (
    "214e2c2639177f8cdf43525b53c5f3d08be0dfdbb3d5c5863cc1c829b84a4259"
)
EXPECTED_FILES = {
    "EXECUTION_SOURCE.tar.gz": (
        "5f75d2f2793e1ec3151994031bb7ca6121fc058fc8d634ba40ae9e14f6118373"
    ),
    "librtdl_optix.so": (
        "713d33734cdd6b1ad9be7852fc4af18e4ed138ae1080f1fd15638ef1b874dfe1"
    ),
    "TARGET_MATERIALIZATION_EVIDENCE.tar.gz": (
        "e2ce4fa7bcc87b8205fdbbb08dd330ac841b0f64faed9283e822728e3367bb03"
    ),
    "RUNTIME.json": "18afdf2b9908fac5b88aabcb71a5ddc2fa52c418e37288d549675f6824ad8f91",
    "DEPENDENCY_LOCK.json": (
        "e8fdc9b1f259e47b51a7883abca04ced8fe96b3540ebdeabd2773f7ccb5613e9"
    ),
    "TARGET_PROGRAM_INSPECTION.json": (
        "c2ba693c9dab69806b5f8f8182833ea92148eeaebc66e570bc960d56748690a0"
    ),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _tar_member_bytes(archive: Path, member: str) -> bytes:
    with tarfile.open(archive, "r:gz") as handle:
        info = handle.getmember(member)
        extracted = handle.extractfile(info)
        if extracted is None:
            raise ValueError(f"missing regular member: {member}")
        return extracted.read()


def _tar_json(archive: Path, member: str) -> dict[str, Any]:
    value = json.loads(_tar_member_bytes(archive, member).decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object member: {member}")
    return value


def _root_file_record(path: Path, expected_sha256: str) -> dict[str, object]:
    observed = _sha256(path)
    if observed != expected_sha256:
        raise ValueError(f"frozen file hash mismatch: {path.relative_to(ROOT)}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": observed,
    }


def _safe_regular_tar_rows(archive: Path) -> tuple[list[dict[str, object]], dict[str, bytes]]:
    rows: list[dict[str, object]] = []
    payloads: dict[str, bytes] = {}
    with tarfile.open(archive, "r:gz") as handle:
        if handle.pax_headers:
            raise ValueError("global PAX headers are not allowed")
        seen: set[str] = set()
        for info in handle.getmembers():
            name = info.name.replace("\\", "/")
            parts = name.split("/")
            if (
                not name
                or name.startswith("/")
                or "\\" in info.name
                or any(part in ("", ".", "..") for part in parts)
                or name in seen
            ):
                raise ValueError(f"unsafe or duplicate archive member: {info.name!r}")
            seen.add(name)
            if info.isdir():
                continue
            if not info.isfile():
                raise ValueError(f"non-regular OptiX archive member: {name}")
            if info.pax_headers:
                raise ValueError(f"member PAX headers are not allowed: {name}")
            extracted = handle.extractfile(info)
            if extracted is None:
                raise ValueError(f"unreadable archive member: {name}")
            payload = extracted.read()
            payloads[name] = payload
            rows.append(
                {
                    "path": name,
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
    rows.sort(key=lambda row: str(row["path"]).encode("utf-8"))
    return rows, payloads


def _extract_define(payload: bytes, macro: str) -> int:
    text = payload.decode("utf-8")
    matches = re.findall(rf"^\s*#\s*define\s+{re.escape(macro)}\s+(\d+)\s*$", text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one numeric {macro} definition")
    return int(matches[0])


def _extract_successful_execve_argv(trace_bytes: bytes, executable: str) -> list[str]:
    trace = trace_bytes.decode("utf-8")
    matches = re.findall(
        rf'execve\("{re.escape(executable)}",\s*(\[.*?\]),'
        rf'\s*0x[0-9a-f]+\s*/\*\s*\d+ vars\s*\*/\)\s*=\s*0',
        trace,
        flags=re.DOTALL,
    )
    if len(matches) != 1:
        raise ValueError(
            f"expected one successful {executable} argv, got {len(matches)}"
        )
    argv = ast.literal_eval(matches[0])
    if not isinstance(argv, list) or not all(isinstance(item, str) for item in argv):
        raise ValueError(f"{executable} argv is not a string list")
    return argv


def _successful_open_paths(trace_bytes: bytes, substring: str) -> list[str]:
    rows: list[str] = []
    for line in trace_bytes.decode("utf-8", errors="strict").splitlines():
        if substring not in line or "openat(" not in line:
            continue
        match = re.search(r'openat\([^,]+,\s*"([^"]+)".*\)\s*=\s*(\d+)', line)
        if match is not None:
            rows.append(match.group(1))
    return sorted(set(rows), key=lambda value: value.encode("utf-8"))


def _elf_dynamic_identity(payload: bytes) -> dict[str, object]:
    if len(payload) < 64 or payload[:4] != b"\x7fELF":
        raise ValueError("native is not ELF")
    if payload[4] != 2 or payload[5] != 1:
        raise ValueError("only little-endian ELF64 is supported")
    e_shoff = struct.unpack_from("<Q", payload, 0x28)[0]
    e_shentsize = struct.unpack_from("<H", payload, 0x3A)[0]
    e_shnum = struct.unpack_from("<H", payload, 0x3C)[0]
    e_shstrndx = struct.unpack_from("<H", payload, 0x3E)[0]
    if e_shentsize != 64 or not (0 < e_shnum < 65536) or e_shstrndx >= e_shnum:
        raise ValueError("unsupported ELF section table")

    sections = [
        struct.unpack_from("<IIQQQQIIQQ", payload, e_shoff + index * e_shentsize)
        for index in range(e_shnum)
    ]
    shstr = sections[e_shstrndx]
    shstr_bytes = payload[shstr[4] : shstr[4] + shstr[5]]

    def cstring(table: bytes, offset: int) -> str:
        end = table.find(b"\0", offset)
        if end < 0:
            raise ValueError("unterminated ELF string")
        return table[offset:end].decode("utf-8")

    named = {cstring(shstr_bytes, section[0]): section for section in sections}
    dynamic = named.get(".dynamic")
    dynstr = named.get(".dynstr")
    note = named.get(".note.gnu.build-id")
    if dynamic is None or dynstr is None or note is None:
        raise ValueError("required ELF sections are absent")
    strings = payload[dynstr[4] : dynstr[4] + dynstr[5]]
    needed: list[str] = []
    rpath: list[str] = []
    runpath: list[str] = []
    entry_size = dynamic[9] or 16
    if entry_size != 16:
        raise ValueError("unexpected ELF dynamic entry size")
    for offset in range(dynamic[4], dynamic[4] + dynamic[5], entry_size):
        tag, value = struct.unpack_from("<qQ", payload, offset)
        if tag == 0:
            break
        if tag == 1:
            needed.append(cstring(strings, value))
        elif tag == 15:
            rpath.append(cstring(strings, value))
        elif tag == 29:
            runpath.append(cstring(strings, value))

    note_bytes = payload[note[4] : note[4] + note[5]]
    namesz, descsz, note_type = struct.unpack_from("<III", note_bytes, 0)
    name_end = 12 + namesz
    desc_start = (name_end + 3) & ~3
    desc = note_bytes[desc_start : desc_start + descsz]
    if note_type != 3 or note_bytes[12:name_end].rstrip(b"\0") != b"GNU":
        raise ValueError("unexpected GNU build-id note")
    return {
        "gnu_build_id": desc.hex(),
        "dt_needed": needed,
        "rpath": rpath,
        "runpath": runpath,
    }


def _extract_top_level_nvcc_argv(trace_bytes: bytes) -> tuple[list[str], str]:
    trace = trace_bytes.decode("utf-8")
    matches = re.findall(
        r'execve\("/usr/local/cuda-12\.8/bin/nvcc",\s*(\[.*?\]),'
        r'\s*0x[0-9a-f]+\s*/\*\s*\d+ vars\s*\*/\)\s*=\s*0',
        trace,
        flags=re.DOTALL,
    )
    if len(matches) != 1:
        raise ValueError(f"expected one successful top-level nvcc argv, got {len(matches)}")
    argv = ast.literal_eval(matches[0])
    if not isinstance(argv, list) or not all(isinstance(item, str) for item in argv):
        raise ValueError("top-level nvcc argv is not a string list")
    build_args = [
        item for item in argv if item.startswith('-DRTDL_OPTIX_BUILD_ID=')
    ]
    if len(build_args) != 1:
        raise ValueError("expected one embedded build-id argument")
    build_id_match = re.fullmatch(
        r'-DRTDL_OPTIX_BUILD_ID=\\?"(\d{8}T\d{15})\\?"', build_args[0]
    )
    if build_id_match is None:
        raise ValueError("embedded build id is absent or not the observed time form")
    return argv, build_id_match.group(1)


def _file_record(name: str) -> dict[str, object]:
    path = EVIDENCE_ROOT / name
    observed = _sha256(path)
    expected = EXPECTED_FILES.get(name)
    if expected is not None and observed != expected:
        raise ValueError(f"frozen file hash mismatch: {name}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": observed,
    }


def build_authority() -> dict[str, object]:
    runtime = _json(EVIDENCE_ROOT / "RUNTIME.json")
    dependency = _json(EVIDENCE_ROOT / "DEPENDENCY_LOCK.json")
    evidence_archive = EVIDENCE_ROOT / "TARGET_MATERIALIZATION_EVIDENCE.tar.gz"
    inspection_bytes = _tar_member_bytes(
        evidence_archive, "TARGET_PROGRAM_INSPECTION.json"
    )
    external_inspection_bytes = (
        EVIDENCE_ROOT / "TARGET_PROGRAM_INSPECTION.json"
    ).read_bytes()
    if inspection_bytes != external_inspection_bytes:
        raise ValueError("external/archive TARGET_PROGRAM_INSPECTION bytes mismatch")
    if hashlib.sha256(inspection_bytes).hexdigest() != EXPECTED_FILES[
        "TARGET_PROGRAM_INSPECTION.json"
    ]:
        raise ValueError("TARGET_PROGRAM_INSPECTION member hash mismatch")
    inspection = json.loads(inspection_bytes.decode("utf-8"))
    toolchain = _tar_json(evidence_archive, "TOOLCHAIN_IDENTITY.json")
    source_manifest_bytes = _tar_member_bytes(evidence_archive, "SOURCE_MANIFEST.json")
    source_manifest = json.loads(source_manifest_bytes.decode("utf-8"))
    source_manifest_file_sha256 = hashlib.sha256(source_manifest_bytes).hexdigest()
    if source_manifest_file_sha256 != runtime["execution_source_manifest_file_sha256"]:
        raise ValueError("execution SOURCE_MANIFEST file identity mismatch")
    native_audit = _tar_json(
        evidence_archive, "TARGET_NATIVE_BUILD_PRODUCER_AUDIT.json"
    )
    trace_bytes = _tar_member_bytes(
        evidence_archive, "TARGET_NATIVE_BUILD_EXECVE_OPENAT_TRACE.log"
    )
    trace_sha256 = hashlib.sha256(trace_bytes).hexdigest()
    if trace_sha256 != native_audit["trace_sha256"]:
        raise ValueError("native build trace identity mismatch")
    top_level_nvcc_argv, embedded_build_id = _extract_top_level_nvcc_argv(
        trace_bytes
    )
    linker_argv = _extract_successful_execve_argv(trace_bytes, "/usr/bin/ld")
    ptx_trace_bytes = _tar_member_bytes(
        evidence_archive, "TARGET_PTX_PRODUCER_OPENAT_TRACE.log"
    )
    ptx_trace_sha256 = hashlib.sha256(ptx_trace_bytes).hexdigest()
    ptx_audit = toolchain["ptx_producer_audit"]
    if ptx_trace_sha256 != ptx_audit["trace_sha256"]:
        raise ValueError("PTX producer trace identity mismatch")

    optix_archive_record = _root_file_record(OPTIX_ARCHIVE, OPTIX_ARCHIVE_SHA256)
    optix_rows, optix_payloads = _safe_regular_tar_rows(OPTIX_ARCHIVE)
    if len(optix_rows) != 14 or set(optix_payloads) != {
        str(row["path"]) for row in optix_rows
    }:
        raise ValueError("unexpected OptiX header archive member set")
    optix_version = _extract_define(optix_payloads["include/optix.h"], "OPTIX_VERSION")
    optix_abi_version = _extract_define(
        optix_payloads["include/optix_function_table.h"], "OPTIX_ABI_VERSION"
    )
    if (optix_version, optix_abi_version) != (90000, 105):
        raise ValueError("unexpected OptiX version or ABI")

    environment_admission_record = _root_file_record(
        ENVIRONMENT_ADMISSION, ENVIRONMENT_ADMISSION_SHA256
    )
    environment_admission = _json(ENVIRONMENT_ADMISSION)
    linker_digest = environment_admission["external_tools"].get("/usr/bin/ld")
    if linker_digest != "5b674ea1d7017c2929f3c52c43487478bb240ecdd7197a25cce3813a70329a5c":
        raise ValueError("unexpected preserved linker digest")

    native_payload = (EVIDENCE_ROOT / "librtdl_optix.so").read_bytes()
    elf_identity = _elf_dynamic_identity(native_payload)
    if elf_identity["gnu_build_id"] != "d3c7850f6d77f7021fdd47187da7aa906e073bcf":
        raise ValueError("unexpected native GNU build-id")
    expected_needed = [
        "libcuda.so.1",
        "libnvrtc.so.12",
        "libstdc++.so.6",
        "libm.so.6",
        "libgcc_s.so.1",
        "libc.so.6",
        "ld-linux-x86-64.so.2",
    ]
    if elf_identity["dt_needed"] != expected_needed:
        raise ValueError("unexpected native DT_NEEDED vector")
    if elf_identity["rpath"] or elf_identity["runpath"]:
        raise ValueError("preserved native unexpectedly has RPATH/RUNPATH")

    native_geos_attempts = [
        line
        for line in trace_bytes.decode("utf-8").splitlines()
        if "geos_c.h" in line and "openat(" in line
    ]
    native_geos_successes = _successful_open_paths(trace_bytes, "geos_c.h")
    ptx_geos_successes = _successful_open_paths(ptx_trace_bytes, "libgeos")
    if not native_geos_attempts or native_geos_successes or ptx_geos_successes:
        raise ValueError("GEOS not-used proof does not match the preserved traces")
    if "-lgeos_c" in linker_argv or "-lgeos_c" in top_level_nvcc_argv:
        raise ValueError("preserved successful build unexpectedly links GEOS")

    observed_runtime_paths: dict[str, list[str]] = {}
    for soname in ("libcuda.so.1", "libstdc++.so.6", "libc.so.6"):
        paths = _successful_open_paths(ptx_trace_bytes, soname)
        if len(paths) != 1:
            raise ValueError(f"expected one successful PTX trace path for {soname}")
        observed_runtime_paths[soname] = paths

    file_records = {name: _file_record(name) for name in EXPECTED_FILES}
    if runtime["native_library_sha256"] != file_records["librtdl_optix.so"]["sha256"]:
        raise ValueError("runtime/native bytes mismatch")
    if inspection["native_library_sha256"] != runtime["native_library_sha256"]:
        raise ValueError("inspection/runtime native mismatch")
    if dependency["dependency_lock_sha256"] != (
        "f0dfb57f3e2abe279d2c689b6f3212dde0bc21a9e19ba79c26a1c0c33e423ad9"
    ):
        raise ValueError("dependency lock self identity mismatch")
    if _sha256(SUPERSEDED_V1_PATH) != SUPERSEDED_V1_FILE_SHA256:
        raise ValueError("superseded v1 bytes mismatch")
    if _sha256(SUPERSEDED_V2_PATH) != SUPERSEDED_V2_FILE_SHA256:
        raise ValueError("superseded v2 bytes mismatch")

    missing = [
        "python.sys_path exact ordered vector",
        "CUDA header-tree manifest and digest",
        "executed host linker bytes and version (path, declared digest and exact argv are preserved)",
        "libcuda.so.1 exact bytes digest",
        "libstdc++.so exact bytes digest",
        "glibc/libc.so.6 exact bytes digest and version",
        "remaining transitive runtime-library byte closure including libnvoptix/loader dependencies",
        "future candidate/oracle dependency closure (GEOS is proven unused only by this native/PTX producer)",
        "Numba leaf-cache exact byte authority for this shared native environment",
        "non-time-derived embedded native build identity",
        "elimination of ambient soname/default-loader resolution",
    ]
    worker_environment = runtime["formal_worker_environment"]
    result: dict[str, object] = {
        "schema": "rtdl.goal5793.x1.environment_shared_native_authority.v4",
        "date": "2026-08-22",
        "status": "BLOCKS_EXAM_EXECUTION__EXACT_ENVIRONMENT_INCOMPLETE",
        "canonicalization": CANONICALIZATION_NAME,
        "authority_sha256": "",
        "scope": {
            "local_evidence_rehash_only": True,
            "gpu_probe_count": 0,
            "native_build_count": 0,
            "network_call_count": 0,
            "candidate_execution_count": 0,
            "registered_timing_count": 0,
            "authorizes_exam_execution": False,
        },
        "supersedes": {
            "path": SUPERSEDED_V2_PATH.relative_to(ROOT).as_posix(),
            "file_sha256": SUPERSEDED_V2_FILE_SHA256,
            "authority_sha256": (
                "7a8a4a4ad5ce41a35fe97c536c1c3298d3aad5a40f9522522e4608aba9e8a5d4"
            ),
            "reason": (
                "v2 mislabeled the compiled callback-program ABI as an OptiX SDK "
                "ABI, did not bind the inspection input through the pinned archive, "
                "and conflated base and execution source-manifest identities"
            ),
            "controlling": False,
        },
        "unwritten_dry_predecessor": {
            "version": 3,
            "authority_sha256": "aee8c29bba37900f7e44067c3632daaec7bf62f9b59819f463bd1557ccb938d4",
            "formal_history_file_created": False,
            "controlling": False,
            "reason": "v3 was byte-reviewed only as a dry candidate and was never emitted",
        },
        "frozen_files": file_records,
        "supplemental_frozen_files": {
            "optix_header_archive": optix_archive_record,
            "environment_admission": environment_admission_record,
        },
        "embedded_self_identities": {
            "runtime_sha256": runtime["runtime_sha256"],
            "dependency_lock_sha256": dependency["dependency_lock_sha256"],
        },
        "source": {
            "execution_source_archive": file_records["EXECUTION_SOURCE.tar.gz"],
            "execution": {
                "source_tree_sha256": source_manifest["source_tree_sha256"],
                "source_manifest_file_sha256": source_manifest_file_sha256,
                "source_file_count_excluding_manifest": source_manifest[
                    "file_count_excluding_this_manifest"
                ],
            },
            "base": {
                "source_archive_sha256": source_manifest[
                    "base_source_archive_sha256"
                ],
                "source_tree_sha256": source_manifest["base_source_tree_sha256"],
                "source_manifest_sha256": source_manifest[
                    "base_source_manifest_sha256"
                ],
                "source_file_count_excluding_manifest": source_manifest[
                    "base_source_file_count_excluding_manifest"
                ],
            },
            "execution_source_root": runtime["execution_source_root"],
            "PYTHONPATH": worker_environment["PYTHONPATH"],
            "sys_path": {
                "status": "MISSING_EXACT_ORDERED_VECTOR__BLOCKING",
                "value": None,
            },
        },
        "python": {
            "executable_path": runtime["python_executable"],
            "executable_sha256": runtime["python_executable_sha256"],
            "version": runtime["python_version"],
            "packages": {
                "numpy": runtime["numpy_version"],
                "numba": runtime["numba_version"],
                "llvmlite": runtime["llvmlite_version"],
                "cupy": runtime["cupy_version"],
            },
            "dependency_lock": file_records["DEPENDENCY_LOCK.json"],
            "wheelhouse_sha256": dependency["wheelhouse_archive_sha256"],
            "network_install_allowed": False,
        },
        "cuda": {
            "toolkit_version": toolchain["cuda_toolkit_version"],
            "prefix": worker_environment["RTDL_V4_CUDA_PREFIX"],
            "include_path": runtime["cuda_include"],
            "header_tree": "MISSING_EXACT_MANIFEST_AND_DIGEST__BLOCKING",
            "nvcc_path": native_audit["nvcc_executed_path"],
            "nvcc_sha256": native_audit["nvcc_executed_sha256"],
            "architecture": inspection["ptx_program_identity"]["composed"]["directives"]["target"],
            "top_level_build_argv_authority": {
                "trace_sha256": trace_sha256,
                "trace_member": "TARGET_NATIVE_BUILD_EXECVE_OPENAT_TRACE.log",
                "exact_argv": top_level_nvcc_argv,
            },
            "ptx_producer_trace_sha256": ptx_trace_sha256,
            "libnvrtc": {
                "paths": ptx_audit["loaded_nvrtc_family_paths"],
                "sha256": ptx_audit["loaded_nvrtc_family_sha256"],
            },
            "libdevice": {
                "path": ptx_audit["numba_selected_libdevice_path"],
                "sha256": ptx_audit["numba_selected_libdevice_sha256"],
            },
            "libnvvm": {
                "path": ptx_audit["numba_selected_nvvm_path"],
                "sha256": ptx_audit["numba_selected_nvvm_sha256"],
            },
        },
        "optix": {
            "sdk_version": toolchain["optix_sdk_version"],
            "include_path": runtime["optix_include"],
            "header_archive": optix_archive_record,
            "header_tree": {
                "regular_file_count": len(optix_rows),
                "rows": optix_rows,
            },
            "optix_version_macro": optix_version,
            "sdk_abi_exact_authority": {
                "macro": "OPTIX_ABI_VERSION",
                "value": optix_abi_version,
                "source_member": "include/optix_function_table.h",
            },
        },
        "compiled_program": {
            "callback_abi_sha256": inspection["abi_sha256"],
            "callback_ir_sha256": inspection["callback_ir_sha256"],
            "composed_program_sha256": inspection["composed_program_sha256"],
        },
        "host_toolchain": {
            "compiler_paths": native_audit["host_compiler_executed_paths"],
            "compiler_sha256": native_audit["host_compiler_executed_sha256"],
            "compiler_versions": native_audit["host_compiler_version_first_line"],
            "linker": {
                "path": "/usr/bin/ld",
                "declared_target_sha256": linker_digest,
                "exact_argv": linker_argv,
                "argv_trace_member": "TARGET_NATIVE_BUILD_EXECVE_OPENAT_TRACE.log",
                "argv_trace_sha256": trace_sha256,
                "bytes_preserved_for_independent_rehash": False,
                "version_preserved": False,
                "status": "PARTIAL__BLOCKING",
            },
        },
        "shared_native": {
            "policy": "ONE_EXACT_NATIVE_FOR_ALL_EXAMS__NO_CANDIDATE_SPECIFIC_BUILD",
            "preserved_path": file_records["librtdl_optix.so"]["path"],
            "target_path": runtime["native_library_path"],
            "sha256": runtime["native_library_sha256"],
            "target_identity_sha256": inspection["target_identity_sha256"],
            "embedded_build_id_observed_in_frozen_trace": embedded_build_id,
            "elf_dynamic_identity_recomputed_from_preserved_bytes": elf_identity,
            "build_id_policy": "TIME_DERIVED_EXISTING_ID__INELIGIBLE_FOR_X1_EXECUTION",
        },
        "target_machine": toolchain["gpu"],
        "runtime_libraries": {
            "libcuda": {
                "observed_successful_paths": observed_runtime_paths["libcuda.so.1"],
                "exact_bytes_digest": None,
                "status": "PATH_EXACT__BYTES_MISSING__BLOCKING",
            },
            "libstdcxx": {
                "observed_successful_paths": observed_runtime_paths["libstdc++.so.6"],
                "exact_bytes_digest": None,
                "status": "PATH_EXACT__BYTES_MISSING__BLOCKING",
            },
            "glibc": {
                "observed_successful_paths": observed_runtime_paths["libc.so.6"],
                "exact_bytes_digest": None,
                "version": None,
                "status": "PATH_EXACT__BYTES_AND_VERSION_MISSING__BLOCKING",
            },
            "geos": {
                "scope": "THIS_EXACT_PRESERVED_NATIVE_BUILD_AND_PTX_PRODUCER_ONLY",
                "native_header_probe_count": len(native_geos_attempts),
                "successful_header_open_count": 0,
                "successful_ptx_libgeos_open_count": 0,
                "successful_link_argv_contains_lgeos_c": False,
                "status": "NOT_USED_IN_THIS_NARROW_SCOPE",
                "future_candidate_or_oracle_use_ruled_out": False,
            },
        },
        "dynamic_library_resolution": {
            "rtdl_native_top_level_path_explicit": True,
            "nvrtc": (
                "EXACT_LOADED_PATHS_OBSERVED__SONAME_SEARCH_ABSENCE_NOT_PROVEN__BLOCKING"
            ),
            "native_transitive_dependencies": {
                "dt_needed": elf_identity["dt_needed"],
                "rpath": elf_identity["rpath"],
                "runpath": elf_identity["runpath"],
                "ld_library_path": worker_environment["LD_LIBRARY_PATH"],
                "ambient_or_default_loader_resolution_structurally_used": True,
                "exact_dependency_bytes_complete": False,
                "status": "AMBIENT_RESOLUTION_PRESENT__BLOCKING",
            },
            "ambient_search_absence_claimed": False,
        },
        "cache": {
            "PYTHONDONTWRITEBYTECODE": worker_environment["PYTHONDONTWRITEBYTECODE"],
            "PYTHONHASHSEED": worker_environment["PYTHONHASHSEED"],
            "PYTHONNOUSERSITE": worker_environment["PYTHONNOUSERSITE"],
            "numba_cache_variables": "NOT_EXACTLY_RECORDED__BLOCKING",
            "leaf_cache_authority": "NOT_PRESERVED_FOR_THIS_SHARED_ENVIRONMENT__BLOCKING",
        },
        "missing_required_exact_identities": missing,
        "claim_boundary": {
            "preserved_native_bytes_are_real": True,
            "preserved_environment_is_partially_exact": True,
            "exact_environment_ready": False,
            "shared_native_execution_ready": False,
            "candidate_specific_native_allowed": False,
            "goal5793_exam_execution_authorized": False,
            "optix_header_tree_and_sdk_abi_recovered": True,
            "geos_not_used_claim_is_shared_native_producer_only": True,
            "ambient_resolution_was_used": True,
        },
    }
    result["authority_sha256"] = seal_document(
        result,
        seal_field="authority_sha256",
        domain="rtdl.goal5793.x1.environment_shared_native_authority",
        version=4,
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    authority = build_authority()
    if args.check:
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if canonical_json_bytes(existing) != canonical_json_bytes(authority):
            raise SystemExit("environment authority is not byte-semantically current")
    elif args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as handle:
            handle.write(canonical_json_bytes(authority) + b"\n")
    print(
        authority["status"], authority["authority_sha256"],
        "WROTE" if args.write else "DRY_RUN_NO_HISTORY_WRITE",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
