#!/usr/bin/env python3
"""Independently verify a downloaded Goal5840 GPU evidence directory.

This verifier intentionally imports only the Python standard library. It
replays the standalone target checker, validates every seal and cross-file
reference, checks the exact frozen 3 x 5 mutation denominator, and binds the
preserved native DSO and its build manifest to the source commit.
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
import sys
import tempfile
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/goal5840_independent_target_checker.py"
MUTATION_RUNNER = ROOT / "scripts/goal5840_mutation_suite.py"
SUMMARY_DOMAIN = b"rtdl.goal5840.true_optix_target_evidence.v5\0"
TRUST_ROOT_DOMAIN = b"rtdl.goal5840.runtime_trust_roots.v1\0"
MUTATION_DOMAIN = b"rtdl.goal5840.exact_bundle_mutation_suite.v1\0"
CHECKER_REPORT_DOMAIN = b"rtdl.goal5840.independent_target_check.v1\0"
PREREGISTRATION_DOMAIN = (
    b"rtdl.goal5840.independent_lowering_refinement_preregistration.v1\0"
)
PRE_POD_DOMAIN = b"rtdl.goal5840.pre_pod_input_authority.v1\0"
REPAIR_AUTHORITY_DOMAIN = b"rtdl.goal5840.post_attempt_01_repair_authority.v1\0"
ATTEMPT_02_REPAIR_AUTHORITY_DOMAIN = (
    b"rtdl.goal5840.post_attempt_02_repair_authority.v1\0"
)
ATTEMPT_03_REPAIR_AUTHORITY_DOMAIN = (
    b"rtdl.goal5840.post_attempt_03_repair_authority.v1\0"
)
ATTEMPT_04_REPAIR_AUTHORITY_DOMAIN = (
    b"rtdl.goal5840.post_attempt_04_repair_authority.v1\0"
)
VERIFICATION_DOMAIN = b"rtdl.goal5840.downloaded_gpu_evidence_verification.v5\0"
NATIVE_BUILD_DOMAIN = b"rtdl.goal5838.selected_sphere_optix_provider_build.v2\0"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
COMMIT_RE = re.compile(r"[0-9a-f]{40}")
PROPERTIES = (
    "CP001_ROLE_EFFECT_CLOSURE",
    "CP002_SEMANTIC_ABI_OWNERSHIP",
    "CP003_PHYSICAL_BINDING",
    "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS",
    "CP005_EXECUTABLE_IDENTITY_CHAIN",
)
EXPECTED_MODES = {
    "stable::bounded_relation::canonical_bounded_pair_collection": (
        "capacity_fail_closed_collection",
    ),
    "stable::triangle_reduction::checked_u64_reduction": (
        "all_hit_count",
        "weighted_hit_count",
    ),
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": (
        "accept_every_hit_and_continue",
    ),
}
ATTEMPT_02_REPAIR_RUNTIME_SOURCE_PATHS = frozenset({
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_attempt02_repair_inputs.py",
    "scripts/goal5840_freeze_gpu_inputs.py",
    "scripts/goal5840_freeze_repair_inputs.py",
    "scripts/goal5840_gpu_cases.py",
    "scripts/goal5840_independent_target_checker.py",
    "scripts/goal5840_mutation_suite.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_control_flow_evidence.py",
    "src/rtdsl/v4_target_evidence_bundle.py",
    "src/rtdsl/v4_target_evidence_capture.py",
})
ATTEMPT_01_REPAIR_RUNTIME_SOURCE_PATHS = (
    ATTEMPT_02_REPAIR_RUNTIME_SOURCE_PATHS
    - {
    "scripts/goal5840_freeze_attempt02_repair_inputs.py",
    }
)
ORIGINAL_RUNTIME_SOURCE_PATHS = ATTEMPT_02_REPAIR_RUNTIME_SOURCE_PATHS - {
    "scripts/goal5840_freeze_attempt02_repair_inputs.py",
    "scripts/goal5840_freeze_repair_inputs.py",
}
RUNTIME_SOURCE_PATHS = ATTEMPT_02_REPAIR_RUNTIME_SOURCE_PATHS | {
    "scripts/goal5840_freeze_attempt03_repair_inputs.py",
    "scripts/goal5840_freeze_attempt04_repair_inputs.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
    "src/rtdsl/v4_callback_ptx_composer.py",
    "src/rtdsl/v4_inline_cuda_codegen.py",
}
ATTEMPT_03_REPAIR_RUNTIME_SOURCE_PATHS = RUNTIME_SOURCE_PATHS - {
    "scripts/goal5840_freeze_attempt04_repair_inputs.py",
}
ATTEMPT_01_SOURCE_COMMIT = "91a8309d9ee234f0315b6640a8dde1db29abe7e9"
ATTEMPT_01_INCIDENT_SHA256 = (
    "862d36657120a190d76527536d09ac8ecd8da77e01b9df4465dd25aee45fe786"
)
REPAIR_ALLOWED_CHANGED_PATHS = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_01_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_01_REPAIR_AUTHORITY.json",
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_repair_inputs.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_evidence_capture.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
    "tests/goal5840_real_target_evidence_capture_test.py",
)
ATTEMPT_01_REPAIR_COMMIT = "3dcd92e3c2ebc71faffbcae0783b747b9820d71e"
ATTEMPT_02_INCIDENT_SHA256 = (
    "865eeb8d5ccacb4f87fe2a3bd73e99e9c835974e27dcae8ebd294ae12c5c7ade"
)
ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_02_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_02_REPAIR_AUTHORITY.json",
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_attempt02_repair_inputs.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_evidence_bundle.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
    "tests/goal5840_target_evidence_bundle_test.py",
)
ATTEMPT_03_SOURCE_COMMIT = "78610253c9650c3661f3f0107da373bf9f2ff549"
ATTEMPT_03_INCIDENT_SHA256 = (
    "d9985b8389882fc07895a1464051f3c5e5c9d85d2cbb83ec32328b63b264f6ee"
)
ATTEMPT_03_REPAIR_ALLOWED_CHANGED_PATHS = tuple(sorted((
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_03_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_03_REPAIR_AUTHORITY.json",
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_attempt03_repair_inputs.py",
    "scripts/goal5840_independent_target_checker.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
    "tests/goal5760_v4_bounded_relation_test.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
    "tests/goal5840_independent_target_checker_test.py",
)))
ATTEMPT_04_SOURCE_COMMIT = "4f2a5d7f4d0f2c4a74756d7456180c8520742a47"
ATTEMPT_04_INCIDENT_SHA256 = (
    "4a06eb1cc98b78719d7bddb99162f4a24619bdd0151eb2790631c2b058ff2918"
)
ATTEMPT_04_REPAIR_ALLOWED_CHANGED_PATHS = tuple(sorted((
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_04_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_04_REPAIR_AUTHORITY.json",
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_attempt04_repair_inputs.py",
    "scripts/goal5840_independent_target_checker.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
    "tests/goal5840_independent_target_checker_test.py",
)))
PREREGISTRATION_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "GOAL5840_PREREGISTRATION.json"
)
PRE_POD_AUTHORITY_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "PRE_POD_INPUT_AUTHORITY.json"
)
ATTEMPT_01_INCIDENT_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_01_ENGINEERING_FAILURE.md"
)
REPAIR_AUTHORITY_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_01_REPAIR_AUTHORITY.json"
)
ATTEMPT_02_INCIDENT_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_02_ENGINEERING_FAILURE.md"
)
ATTEMPT_02_REPAIR_AUTHORITY_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_02_REPAIR_AUTHORITY.json"
)
ATTEMPT_03_INCIDENT_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_03_ENGINEERING_FAILURE.md"
)
ATTEMPT_03_REPAIR_AUTHORITY_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_03_REPAIR_AUTHORITY.json"
)
ATTEMPT_04_INCIDENT_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_04_ENGINEERING_FAILURE.md"
)
ATTEMPT_04_REPAIR_AUTHORITY_PATH = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_04_REPAIR_AUTHORITY.json"
)
RESULT_SOURCE_PATHS = RUNTIME_SOURCE_PATHS | {
    PREREGISTRATION_PATH,
    PRE_POD_AUTHORITY_PATH,
    ATTEMPT_01_INCIDENT_PATH,
    REPAIR_AUTHORITY_PATH,
    ATTEMPT_02_INCIDENT_PATH,
    ATTEMPT_02_REPAIR_AUTHORITY_PATH,
    ATTEMPT_03_INCIDENT_PATH,
    ATTEMPT_03_REPAIR_AUTHORITY_PATH,
    ATTEMPT_04_INCIDENT_PATH,
    ATTEMPT_04_REPAIR_AUTHORITY_PATH,
}
GOAL5840_REQUIRED_NATIVE_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_traversal_audit_abort",
    "rtdl_optix_traversal_audit_begin",
    "rtdl_optix_traversal_audit_finish",
    "rtdl_optix_v4_checked_u64_product_sum_host_v1",
    "rtdl_optix_v4_describe_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v1",
    "rtdl_optix_v4_destroy_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_destroy_prepared_triangle_reduction_callback_v1",
    "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v3",
    "rtdl_optix_v4_execute_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v2",
    "rtdl_optix_v4_prepare_bounded_relation_callback_v1",
    "rtdl_optix_v4_prepare_builtin_sphere_callback_v1",
    "rtdl_optix_v4_prepare_triangle_reduction_callback_v1",
    "rtdl_optix_v4_rtdlexe_producer_descriptor_v1",
    "rtdl_optix_v4_runtime_compiler_attempt_count_v1",
)
NATIVE_BUILD_SOURCE_PATHS = frozenset({
    "scripts/goal5838_build_selected_sphere_optix_provider.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_particle_template.h",
    "src/native/optix/rtdl_optix_v4_product_status.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
})


class Goal5840EvidenceVerificationError(ValueError):
    """The downloaded evidence does not satisfy the frozen bounded contract."""


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise Goal5840EvidenceVerificationError(
            f"value is not canonical ASCII JSON: {error}"
        ) from error


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _defined_elf64_dynamic_symbols(path: Path) -> set[str]:
    """Read defined global/weak names directly from a little-endian ELF64 DSO."""

    raw = path.read_bytes()
    header_format = "<16sHHIQQQIHHHHHH"
    section_format = "<IIQQQQIIQQ"
    symbol_format = "<IBBHQQ"
    _require(len(raw) >= struct.calcsize(header_format), "native DSO is truncated")
    try:
        header = struct.unpack_from(header_format, raw, 0)
    except struct.error as error:
        raise Goal5840EvidenceVerificationError(
            f"native ELF header cannot be decoded: {error}"
        ) from error
    ident = header[0]
    _require(
        ident[:7] == b"\x7fELF\x02\x01\x01",
        "native DSO must be little-endian ELF64",
    )
    section_offset = int(header[6])
    section_entry_size = int(header[11])
    section_count = int(header[12])
    expected_section_size = struct.calcsize(section_format)
    _require(
        section_count > 0 and section_entry_size >= expected_section_size,
        "native DSO has unsupported section headers",
    )
    _require(
        section_offset + section_entry_size * section_count <= len(raw),
        "native DSO section table is out of bounds",
    )
    sections = []
    try:
        for index in range(section_count):
            sections.append(struct.unpack_from(
                section_format,
                raw,
                section_offset + index * section_entry_size,
            ))
    except struct.error as error:
        raise Goal5840EvidenceVerificationError(
            f"native ELF section cannot be decoded: {error}"
        ) from error
    result = set()
    for section in sections:
        section_type = int(section[1])
        if section_type != 11:  # SHT_DYNSYM
            continue
        offset, size, link, entry_size = (
            int(section[4]),
            int(section[5]),
            int(section[6]),
            int(section[9]),
        )
        _require(
            0 <= link < len(sections)
            and entry_size >= struct.calcsize(symbol_format)
            and size % entry_size == 0
            and offset + size <= len(raw),
            "native DSO dynamic-symbol section is invalid",
        )
        strings = sections[link]
        string_offset, string_size = int(strings[4]), int(strings[5])
        _require(
            string_offset + string_size <= len(raw),
            "native DSO dynamic string table is out of bounds",
        )
        string_table = raw[string_offset:string_offset + string_size]
        for symbol_offset in range(offset, offset + size, entry_size):
            try:
                name_offset, info, _other, section_index, _value, _size = (
                    struct.unpack_from(symbol_format, raw, symbol_offset)
                )
            except struct.error as error:
                raise Goal5840EvidenceVerificationError(
                    f"native ELF symbol cannot be decoded: {error}"
                ) from error
            binding = info >> 4
            if section_index == 0 or binding not in {1, 2, 10} or name_offset == 0:
                continue
            _require(name_offset < len(string_table), "ELF symbol name is out of bounds")
            end = string_table.find(b"\0", name_offset)
            _require(end >= 0, "ELF symbol name is not terminated")
            try:
                result.add(string_table[name_offset:end].decode("ascii"))
            except UnicodeDecodeError as error:
                raise Goal5840EvidenceVerificationError(
                    f"ELF dynamic symbol is not ASCII: {error}"
                ) from error
    _require(bool(result), "native DSO has no defined dynamic symbols")
    return result


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Goal5840EvidenceVerificationError(message)


def _mapping(value: object, label: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{label}: object required")
    return value


def _sequence(value: object, label: str) -> list[Any]:
    _require(isinstance(value, list), f"{label}: array required")
    return value


def _sha(value: object, label: str) -> str:
    _require(
        isinstance(value, str) and SHA256_RE.fullmatch(value) is not None,
        f"{label}: lowercase SHA-256 required",
    )
    return value


def _commit(value: object, label: str) -> str:
    _require(
        isinstance(value, str) and COMMIT_RE.fullmatch(value) is not None,
        f"{label}: full lowercase 40-hex Git commit required",
    )
    return value


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return _mapping(json.loads(path.read_text(encoding="ascii")), label)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise Goal5840EvidenceVerificationError(
            f"{label}: cannot read canonical evidence: {error}"
        ) from error


def _verify_seal(
    document: Mapping[str, object], field: str, domain: bytes, label: str
) -> str:
    observed = _sha(document.get(field), f"{label}.{field}")
    body = dict(document)
    body[field] = ""
    expected = hashlib.sha256(domain + _canonical(body)).hexdigest()
    _require(observed == expected, f"{label}: seal mismatch")
    return observed


def _safe_member(directory: Path, name: object, label: str) -> Path:
    _require(isinstance(name, str) and bool(name), f"{label}: filename required")
    candidate = Path(name)
    _require(
        not candidate.is_absolute()
        and candidate.name == name
        and name not in {".", ".."},
        f"{label}: simple relative filename required",
    )
    resolved = (directory / candidate).resolve(strict=True)
    _require(resolved.parent == directory, f"{label}: path escapes evidence directory")
    _require(resolved.is_file(), f"{label}: regular file required")
    return resolved


def _git_blob(root: Path, commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    _require(
        completed.returncode == 0,
        f"Git cannot resolve {commit}:{path}: {completed.stderr.decode(errors='replace')}",
    )
    return completed.stdout


def _git_changed_paths(root: Path, base: str, commit: str) -> tuple[str, ...]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..{commit}", "--"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    _require(
        completed.returncode == 0,
        f"Git cannot diff {base}..{commit}: {completed.stderr}",
    )
    return tuple(sorted(line for line in completed.stdout.splitlines() if line))


def _verify_source_rows(
    rows_value: object, *, root: Path, commit: str, label: str
) -> dict[str, dict[str, object]]:
    rows = _sequence(rows_value, label)
    result: dict[str, dict[str, object]] = {}
    for index, value in enumerate(rows):
        row = _mapping(value, f"{label}[{index}]")
        path = row.get("path")
        _require(
            isinstance(path, str) and path and path not in result,
            f"{label}: duplicate/invalid path",
        )
        blob = _git_blob(root, commit, path)
        _require(row.get("bytes") == len(blob), f"{label}: byte count differs for {path}")
        _require(
            row.get("sha256") == hashlib.sha256(blob).hexdigest(),
            f"{label}: Git blob digest differs for {path}",
        )
        result[path] = row
    _require(bool(result), f"{label}: empty source inventory")
    return result


def _load_committed_json(
    root: Path, commit: str, path: object, file_sha256: object, label: str
) -> dict[str, Any]:
    _require(isinstance(path, str) and path, f"{label}.path required")
    blob = _git_blob(root, commit, path)
    _require(
        hashlib.sha256(blob).hexdigest() == _sha(file_sha256, f"{label}.file_sha256"),
        f"{label}: committed file digest differs",
    )
    try:
        return _mapping(json.loads(blob.decode("ascii")), label)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise Goal5840EvidenceVerificationError(
            f"{label}: committed JSON cannot be decoded: {error}"
        ) from error


def _expected_mode_keys() -> set[str]:
    return {
        f"{route_id}::{mode}"
        for route_id, modes in EXPECTED_MODES.items()
        for mode in modes
    }


def _verify_preregistration(document: Mapping[str, object]) -> dict[str, dict[str, object]]:
    _require(
        document.get("schema")
        == "rtdl.goal5840.independent_lowering_refinement_preregistration.v1",
        "preregistration schema differs",
    )
    _verify_seal(document, "authority_sha256", PREREGISTRATION_DOMAIN, "preregistration")
    rows = _sequence(document.get("mutation_matrix"), "preregistration.mutation_matrix")
    expected_units = {
        (route_id, property_id)
        for route_id in EXPECTED_MODES
        for property_id in PROPERTIES
    }
    result: dict[str, dict[str, object]] = {}
    observed_units = set()
    for index, value in enumerate(rows):
        row = _mapping(value, f"mutation_matrix[{index}]")
        route_id = str(row.get("route_id"))
        property_id = str(row.get("property_id"))
        mutation_id = row.get("mutation_id")
        _require(
            mutation_id == f"{route_id}::{property_id}",
            "preregistration mutation identity differs",
        )
        _require(
            isinstance(row.get("target_selector"), str)
            and isinstance(row.get("replacement"), str)
            and isinstance(row.get("required_rejection"), str),
            "preregistration mutation is not fully frozen",
        )
        observed_units.add((route_id, property_id))
        result[str(mutation_id)] = row
    _require(
        len(rows) == 15 and observed_units == expected_units and len(result) == 15,
        "preregistration mutation denominator differs",
    )
    return result


def _verify_pre_pod_authority(
    document: Mapping[str, object], *, root: Path, commit: str
) -> dict[str, dict[str, object]]:
    _require(
        document.get("schema") == "rtdl.goal5840.pre_pod_input_authority.v1"
        and document.get("stage") == "BEFORE_ANY_GOAL5840_GPU_EXECUTION"
        and document.get("status") == "FROZEN_INPUTS_AND_TRUST_ROOTS__NO_GPU_RESULT",
        "pre-pod authority status differs",
    )
    _verify_seal(document, "authority_sha256", PRE_POD_DOMAIN, "pre_pod_authority")
    _require(
        document.get("execution_counts_at_freeze")
        == {
            "goal5840_gpu_launches": 0,
            "goal5840_positive_target_bundles": 0,
            "goal5840_exact_bundle_mutations": 0,
        },
        "pre-pod execution count is not zero",
    )
    _verify_source_rows(
        document.get("source_files"), root=root, commit=commit, label="pre_pod.source_files"
    )
    frozen_core = _mapping(
        document.get("goal5838_frozen_core"), "pre_pod.goal5838_frozen_core"
    )
    frozen_rows = _verify_source_rows(
        frozen_core.get("files"),
        root=root,
        commit=commit,
        label="pre_pod.goal5838_frozen_core.files",
    )
    _require(
        frozen_core.get("changed_file_count") == 0 and len(frozen_rows) == 3,
        "pre-pod Goal5838 frozen-core record differs",
    )
    rows = _sequence(document.get("mode_cases"), "pre_pod.mode_cases")
    result: dict[str, dict[str, object]] = {}
    for value in rows:
        row = _mapping(value, "pre_pod.mode_cases[]")
        key = row.get("key")
        _require(isinstance(key, str) and key not in result, "pre-pod mode key differs")
        result[key] = row
    _require(set(result) == _expected_mode_keys(), "pre-pod mode denominator differs")
    return result


def _verify_repair_authority(
    document: Mapping[str, object], *, root: Path, commit: str,
    original: Mapping[str, object], preregistration: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    _require(
        document.get("schema")
        == "rtdl.goal5840.post_attempt_01_repair_authority.v1"
        and document.get("stage")
        == "AFTER_ATTEMPT_01_BEFORE_ATTEMPT_02_GPU_EXECUTION"
        and document.get("status")
        == "FROZEN_BOUNDED_EVIDENCE_TRANSPORT_REPAIR__NO_ACCEPTED_RESULT",
        "repair authority status differs",
    )
    _verify_seal(
        document,
        "authority_sha256",
        REPAIR_AUTHORITY_DOMAIN,
        "repair_authority",
    )
    _require(
        document.get("route_bundle_group_count") == 3
        and document.get("required_mode_count") == 4
        and document.get("mode_cases") == original.get("mode_cases")
        and document.get("goal5838_frozen_core")
        == original.get("goal5838_frozen_core")
        and document.get("preregistration") == original.get("preregistration"),
        "repair authority changed a scientific input",
    )

    base = _mapping(document.get("base_attempt"), "repair_authority.base_attempt")
    pre_ref = _mapping(
        base.get("pre_pod_input_authority"),
        "repair_authority.base_attempt.pre_pod_input_authority",
    )
    incident_ref = _mapping(
        base.get("attempt_01_incident"),
        "repair_authority.base_attempt.attempt_01_incident",
    )
    pre_path = (
        "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
        "PRE_POD_INPUT_AUTHORITY.json"
    )
    incident_path = (
        "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
        "ATTEMPT_01_ENGINEERING_FAILURE.md"
    )
    original_bytes = _git_blob(root, ATTEMPT_01_SOURCE_COMMIT, pre_path)
    incident_bytes = _git_blob(root, commit, incident_path)
    _require(
        base.get("source_commit") == ATTEMPT_01_SOURCE_COMMIT
        and pre_ref.get("path") == pre_path
        and pre_ref.get("bytes") == len(original_bytes)
        and pre_ref.get("file_sha256")
        == hashlib.sha256(original_bytes).hexdigest()
        and pre_ref.get("authority_sha256") == original.get("authority_sha256")
        and incident_ref.get("path") == incident_path
        and incident_ref.get("bytes") == len(incident_bytes)
        and incident_ref.get("file_sha256") == ATTEMPT_01_INCIDENT_SHA256
        and hashlib.sha256(incident_bytes).hexdigest()
        == ATTEMPT_01_INCIDENT_SHA256
        and incident_ref.get("classification")
        == "EVIDENCE_TRANSPORT_ENGINEERING_FAILURE",
        "repair authority base-attempt chain differs",
    )
    expected_attempt_counts = {
        "runner_processes_started": 1,
        "frozen_modes_entered": 1,
        "public_route_expected_outputs_returned": 1,
        "published_evidence_bundles": 0,
        "published_independent_property_reports": 0,
        "published_mutation_applications": 0,
        "accepted_positive_evidence_rows": 0,
    }
    expected_repair_counts = {
        "attempted_runner_processes": 1,
        "entered_frozen_modes": 1,
        "returned_expected_outputs": 1,
        "published_evidence_bundles": 0,
        "published_independent_property_reports": 0,
        "published_mutation_applications": 0,
        "accepted_goal5840_positive_evidence_rows": 0,
    }
    _require(
        base.get("observed_counts") == expected_attempt_counts
        and document.get("execution_counts_at_repair_freeze")
        == expected_repair_counts,
        "repair authority execution history differs",
    )

    scope = _mapping(document.get("repair_scope"), "repair_authority.repair_scope")
    _require(
        scope.get("defect")
        == "nested_read_only_mapping_not_recursively_json_canonicalized"
        and scope.get("repair")
        == "recursive_mapping_sequence_to_canonical_json_tree"
        and scope.get("nonsemantic_harness_hardening")
        == "generate_pod_mutation_report_under_python_isolated_mode"
        and scope.get("allowed_changed_paths")
        == list(REPAIR_ALLOWED_CHANGED_PATHS)
        and scope.get("exact_changed_paths_since_base")
        == list(REPAIR_ALLOWED_CHANGED_PATHS)
        and all(
            scope.get(field) is False
            for field in (
                "route_change_allowed",
                "fixture_or_oracle_change_allowed",
                "declaration_or_control_root_change_allowed",
                "property_or_mutation_change_allowed",
                "native_engine_change_allowed",
                "frozen_core_change_allowed",
            )
        ),
        "repair authority scope differs",
    )
    _require(
        _git_changed_paths(root, ATTEMPT_01_SOURCE_COMMIT, commit)
        == REPAIR_ALLOWED_CHANGED_PATHS,
        "repair commit changed an unapproved path or omitted an approved repair path",
    )

    source_rows = _verify_source_rows(
        document.get("source_files"),
        root=root,
        commit=commit,
        label="repair_authority.source_files",
    )
    original_source_paths = {
        str(row.get("path"))
        for row in _sequence(original.get("source_files"), "pre_pod.source_files")
        if isinstance(row, dict)
    }
    _require(
        set(source_rows)
        == original_source_paths | {"scripts/goal5840_freeze_repair_inputs.py"}
        and ATTEMPT_01_REPAIR_RUNTIME_SOURCE_PATHS <= set(source_rows),
        "repair authority source denominator differs",
    )
    original_prereg = _mapping(
        original.get("preregistration"), "pre_pod.preregistration"
    )
    repair_prereg = _mapping(
        document.get("preregistration"), "repair_authority.preregistration"
    )
    _require(
        repair_prereg == original_prereg
        and repair_prereg.get("authority_sha256")
        == preregistration.get("authority_sha256"),
        "repair authority preregistration chain differs",
    )

    claims = _mapping(document.get("claim_boundary"), "repair_authority.claim_boundary")
    _require(
        claims.get("append_only_engineering_repair_authority") is True
        and claims.get("scientific_inputs_unchanged") is True
        and claims.get("accepted_goal5840_result") is False
        and claims.get("lowering_preservation_established") is False
        and claims.get("performance_or_speedup") is False
        and claims.get("application_correctness") is False
        and claims.get("external_review_or_consensus") is False,
        "repair authority claim boundary differs",
    )
    return {
        str(row["key"]): row
        for row in _sequence(document.get("mode_cases"), "repair_authority.mode_cases")
        if isinstance(row, dict)
    }


def _verify_attempt02_repair_authority(
    document: Mapping[str, object], *, root: Path, commit: str,
    original: Mapping[str, object], prior: Mapping[str, object],
    preregistration: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    _require(
        document.get("schema")
        == "rtdl.goal5840.post_attempt_02_repair_authority.v1"
        and document.get("stage")
        == "AFTER_ATTEMPT_02_BEFORE_ATTEMPT_03_GPU_EXECUTION"
        and document.get("status")
        == "FROZEN_BOUNDED_EXECUTABLE_IDENTITY_REPAIR__NO_ACCEPTED_RESULT",
        "Attempt-02 repair authority status differs",
    )
    _verify_seal(
        document,
        "authority_sha256",
        ATTEMPT_02_REPAIR_AUTHORITY_DOMAIN,
        "attempt_02_repair_authority",
    )
    _require(
        document.get("route_bundle_group_count") == 3
        and document.get("required_mode_count") == 4
        and document.get("mode_cases") == prior.get("mode_cases")
        and document.get("mode_cases") == original.get("mode_cases")
        and document.get("goal5838_frozen_core")
        == prior.get("goal5838_frozen_core")
        and document.get("preregistration") == prior.get("preregistration"),
        "Attempt-02 repair authority changed a scientific input",
    )

    chain = _mapping(
        document.get("base_chain"), "attempt_02_repair_authority.base_chain"
    )
    prior_ref = _mapping(
        chain.get("post_attempt_01_repair_authority"),
        "attempt_02_repair_authority.base_chain.post_attempt_01_repair_authority",
    )
    incident_ref = _mapping(
        chain.get("attempt_02_incident"),
        "attempt_02_repair_authority.base_chain.attempt_02_incident",
    )
    prior_blob = _git_blob(root, ATTEMPT_01_REPAIR_COMMIT, REPAIR_AUTHORITY_PATH)
    incident_blob = _git_blob(root, commit, ATTEMPT_02_INCIDENT_PATH)
    _require(
        chain.get("attempt_01_source_commit") == ATTEMPT_01_SOURCE_COMMIT
        and chain.get("attempt_01_repair_commit") == ATTEMPT_01_REPAIR_COMMIT
        and prior_ref.get("path") == REPAIR_AUTHORITY_PATH
        and prior_ref.get("bytes") == len(prior_blob)
        and prior_ref.get("file_sha256") == hashlib.sha256(prior_blob).hexdigest()
        and prior_ref.get("authority_sha256") == prior.get("authority_sha256")
        and incident_ref.get("path") == ATTEMPT_02_INCIDENT_PATH
        and incident_ref.get("bytes") == len(incident_blob)
        and incident_ref.get("file_sha256") == ATTEMPT_02_INCIDENT_SHA256
        and hashlib.sha256(incident_blob).hexdigest()
        == ATTEMPT_02_INCIDENT_SHA256
        and incident_ref.get("classification")
        == (
            "EVIDENCE_EXECUTABLE_IDENTITY_CANONICALIZATION_"
            "ENGINEERING_FAILURE"
        ),
        "Attempt-02 repair authority base chain differs",
    )
    _require(
        chain.get("formal_observed_counts_through_attempt_02")
        == {
            "runner_processes_started": 2,
            "frozen_modes_entered": 2,
            "public_route_expected_outputs_returned": 2,
            "published_evidence_bundles": 0,
            "published_independent_property_reports": 0,
            "published_mutation_applications": 0,
            "accepted_positive_evidence_rows": 0,
        }
        and chain.get("post_failure_diagnostics")
        == {
            "diagnostic_processes": 2,
            "diagnostic_mode_executions": 2,
            "diagnostic_expected_outputs_returned": 2,
            "diagnostic_evidence_files_published": 0,
            "accepted_positive_evidence_rows": 0,
        }
        and document.get("execution_counts_at_repair_freeze")
        == {
            "formal_runner_processes": 2,
            "formal_entered_modes": 2,
            "formal_returned_expected_outputs": 2,
            "diagnostic_processes": 2,
            "diagnostic_mode_executions": 2,
            "published_evidence_bundles": 0,
            "published_independent_property_reports": 0,
            "published_mutation_applications": 0,
            "accepted_goal5840_positive_evidence_rows": 0,
        },
        "Attempt-02 repair authority execution history differs",
    )

    scope = _mapping(
        document.get("repair_scope"), "attempt_02_repair_authority.repair_scope"
    )
    _require(
        scope.get("defect")
        == "str_derived_enum_role_stringified_to_enum_qualname"
        and scope.get("repair")
        == "preserve_and_validate_underlying_string_enum_value"
        and scope.get("allowed_changed_paths")
        == list(ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS)
        and scope.get("exact_changed_paths_since_base")
        == list(ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS)
        and all(
            scope.get(field) is False
            for field in (
                "route_change_allowed",
                "fixture_or_oracle_change_allowed",
                "declaration_or_control_root_change_allowed",
                "property_or_mutation_change_allowed",
                "native_engine_change_allowed",
                "frozen_core_change_allowed",
            )
        ),
        "Attempt-02 repair authority scope differs",
    )
    _require(
        _git_changed_paths(root, ATTEMPT_01_REPAIR_COMMIT, commit)
        == ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS,
        "Attempt-02 repair changed an unapproved path",
    )

    source_rows = _verify_source_rows(
        document.get("source_files"),
        root=root,
        commit=commit,
        label="attempt_02_repair_authority.source_files",
    )
    prior_source_paths = {
        str(row.get("path"))
        for row in _sequence(
            prior.get("source_files"), "repair_authority.source_files"
        )
        if isinstance(row, dict)
    }
    _require(
        set(source_rows)
        == prior_source_paths | {"scripts/goal5840_freeze_attempt02_repair_inputs.py"}
        and ATTEMPT_02_REPAIR_RUNTIME_SOURCE_PATHS <= set(source_rows),
        "Attempt-02 repair authority source denominator differs",
    )
    prior_prereg = _mapping(
        prior.get("preregistration"), "repair_authority.preregistration"
    )
    current_prereg = _mapping(
        document.get("preregistration"),
        "attempt_02_repair_authority.preregistration",
    )
    _require(
        current_prereg == prior_prereg
        and current_prereg.get("authority_sha256")
        == preregistration.get("authority_sha256"),
        "Attempt-02 repair authority preregistration chain differs",
    )
    claims = _mapping(
        document.get("claim_boundary"),
        "attempt_02_repair_authority.claim_boundary",
    )
    _require(
        claims.get("append_only_engineering_repair_authority") is True
        and claims.get("two_prior_formal_failures_preserved") is True
        and claims.get("diagnostic_launches_not_accepted_as_evidence") is True
        and claims.get("scientific_inputs_unchanged") is True
        and claims.get("accepted_goal5840_result") is False
        and claims.get("lowering_preservation_established") is False
        and claims.get("performance_or_speedup") is False
        and claims.get("application_correctness") is False
        and claims.get("external_review_or_consensus") is False,
        "Attempt-02 repair authority claim boundary differs",
    )
    return {
        str(row["key"]): row
        for row in _sequence(
            document.get("mode_cases"), "attempt_02_repair_authority.mode_cases"
        )
        if isinstance(row, dict)
    }


def _verify_attempt03_repair_authority(
    document: Mapping[str, object], *, root: Path, commit: str,
    original: Mapping[str, object], prior: Mapping[str, object],
    preregistration: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    _require(
        document.get("schema")
        == "rtdl.goal5840.post_attempt_03_repair_authority.v1"
        and document.get("stage")
        == "AFTER_ATTEMPT_03_BEFORE_ATTEMPT_04_GPU_EXECUTION"
        and document.get("status")
        == "FROZEN_INLINE_SPECIALIZATION_CHECKER_REPAIR__NO_ACCEPTED_RESULT",
        "Attempt-03 repair authority status differs",
    )
    _verify_seal(
        document,
        "authority_sha256",
        ATTEMPT_03_REPAIR_AUTHORITY_DOMAIN,
        "attempt_03_repair_authority",
    )
    _require(
        document.get("route_bundle_group_count") == 3
        and document.get("required_mode_count") == 4
        and document.get("mode_cases") == prior.get("mode_cases")
        and document.get("mode_cases") == original.get("mode_cases")
        and document.get("goal5838_frozen_core")
        == prior.get("goal5838_frozen_core")
        and document.get("preregistration") == prior.get("preregistration"),
        "Attempt-03 repair authority changed a scientific input",
    )

    chain = _mapping(
        document.get("base_chain"), "attempt_03_repair_authority.base_chain"
    )
    prior_ref = _mapping(
        chain.get("post_attempt_02_repair_authority"),
        "attempt_03_repair_authority.base_chain.post_attempt_02_repair_authority",
    )
    incident_ref = _mapping(
        chain.get("attempt_03_incident"),
        "attempt_03_repair_authority.base_chain.attempt_03_incident",
    )
    prior_blob = _git_blob(
        root, ATTEMPT_03_SOURCE_COMMIT, ATTEMPT_02_REPAIR_AUTHORITY_PATH
    )
    incident_blob = _git_blob(root, commit, ATTEMPT_03_INCIDENT_PATH)
    expected_failure_artifacts = [
        {
            "name": "mode_01_capacity_fail_closed_collection_bundle.json",
            "bytes": 1364074,
            "file_sha256": (
                "398e366efe3c7c156ef5c334ded4a258e360f55eded254eb5"
                "c7f491726296635"
            ),
        },
        {
            "name": (
                "mode_01_capacity_fail_closed_collection_"
                "independent_check.json"
            ),
            "bytes": 3396,
            "file_sha256": (
                "7aa16896c14e63664b486514b35713657b950a7e8e8a74709"
                "aa9816a0760c51a"
            ),
        },
    ]
    _require(
        chain.get("attempt_03_source_commit") == ATTEMPT_03_SOURCE_COMMIT
        and prior_ref.get("path") == ATTEMPT_02_REPAIR_AUTHORITY_PATH
        and prior_ref.get("bytes") == len(prior_blob)
        and prior_ref.get("file_sha256") == hashlib.sha256(prior_blob).hexdigest()
        and prior_ref.get("authority_sha256") == prior.get("authority_sha256")
        and incident_ref.get("path") == ATTEMPT_03_INCIDENT_PATH
        and incident_ref.get("bytes") == len(incident_blob)
        and incident_ref.get("file_sha256") == ATTEMPT_03_INCIDENT_SHA256
        and hashlib.sha256(incident_blob).hexdigest()
        == ATTEMPT_03_INCIDENT_SHA256
        and incident_ref.get("classification")
        == (
            "INDEPENDENT_CHECKER_INLINE_SPECIALIZATION_RULE_"
            "ENGINEERING_FAILURE"
        )
        and incident_ref.get("published_failure_artifacts")
        == expected_failure_artifacts,
        "Attempt-03 repair authority base chain differs",
    )
    _require(
        chain.get("formal_observed_counts_through_attempt_03")
        == {
            "runner_processes_started": 3,
            "frozen_modes_entered": 3,
            "public_route_expected_outputs_returned": 3,
            "published_evidence_bundles": 1,
            "published_independent_property_reports": 1,
            "independently_accepted_reports": 0,
            "published_mutation_applications": 0,
            "accepted_positive_evidence_rows": 0,
        }
        and chain.get("prior_post_failure_diagnostics")
        == {
            "diagnostic_processes": 2,
            "diagnostic_mode_executions": 2,
            "accepted_positive_evidence_rows": 0,
        }
        and chain.get("attempt_03_post_failure_gpu_diagnostics")
        == {
            "diagnostic_processes": 0,
            "diagnostic_mode_executions": 0,
            "accepted_positive_evidence_rows": 0,
        }
        and document.get("execution_counts_at_repair_freeze")
        == {
            "formal_runner_processes": 3,
            "formal_entered_modes": 3,
            "formal_returned_expected_outputs": 3,
            "prior_diagnostic_processes": 2,
            "prior_diagnostic_mode_executions": 2,
            "published_evidence_bundles": 1,
            "published_independent_property_reports": 1,
            "independently_accepted_reports": 0,
            "published_mutation_applications": 0,
            "accepted_goal5840_positive_evidence_rows": 0,
        },
        "Attempt-03 repair authority execution history differs",
    )

    scope = _mapping(
        document.get("repair_scope"), "attempt_03_repair_authority.repair_scope"
    )
    _require(
        scope.get("defect")
        == "linked_ptx_symbol_rule_applied_to_closed_inline_partial_evaluation"
        and scope.get("repair")
        == (
            "independently_hash_inline_definitions_and_extract_"
            "partial_evaluation_role_effects"
        )
        and scope.get("allowed_changed_paths")
        == list(ATTEMPT_03_REPAIR_ALLOWED_CHANGED_PATHS)
        and scope.get("exact_changed_paths_since_base")
        == list(ATTEMPT_03_REPAIR_ALLOWED_CHANGED_PATHS)
        and scope.get("linked_routes_keep_final_ptx_symbol_rule") is True
        and scope.get("bounded_wrapper_declares_partial_evaluation") is True
        and all(
            scope.get(field) is False
            for field in (
                "route_change_allowed",
                "fixture_or_oracle_change_allowed",
                "declaration_or_control_root_change_allowed",
                "property_or_mutation_change_allowed",
                "native_engine_change_allowed",
                "frozen_core_change_allowed",
            )
        ),
        "Attempt-03 repair authority scope differs",
    )
    _require(
        _git_changed_paths(root, ATTEMPT_03_SOURCE_COMMIT, commit)
        == ATTEMPT_03_REPAIR_ALLOWED_CHANGED_PATHS,
        "Attempt-03 repair changed an unapproved path",
    )

    source_rows = _verify_source_rows(
        document.get("source_files"),
        root=root,
        commit=commit,
        label="attempt_03_repair_authority.source_files",
    )
    prior_source_paths = {
        str(row.get("path"))
        for row in _sequence(
            prior.get("source_files"), "attempt_02_repair_authority.source_files"
        )
        if isinstance(row, dict)
    }
    expected_additions = {
        "scripts/goal5840_freeze_attempt03_repair_inputs.py",
        "src/rtdsl/v4_bounded_relation_optix_compiler.py",
        "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
        "src/rtdsl/v4_callback_ptx_composer.py",
        "src/rtdsl/v4_inline_cuda_codegen.py",
        "tests/goal5760_v4_bounded_relation_test.py",
    }
    _require(
        set(source_rows) == prior_source_paths | expected_additions
        and ATTEMPT_03_REPAIR_RUNTIME_SOURCE_PATHS <= set(source_rows),
        "Attempt-03 repair authority source denominator differs",
    )
    current_prereg = _mapping(
        document.get("preregistration"),
        "attempt_03_repair_authority.preregistration",
    )
    _require(
        current_prereg == prior.get("preregistration")
        and current_prereg.get("authority_sha256")
        == preregistration.get("authority_sha256"),
        "Attempt-03 repair authority preregistration chain differs",
    )
    claims = _mapping(
        document.get("claim_boundary"),
        "attempt_03_repair_authority.claim_boundary",
    )
    _require(
        claims.get("append_only_engineering_repair_authority") is True
        and claims.get("three_prior_formal_failures_preserved") is True
        and claims.get("failure_bundle_and_reject_report_not_accepted") is True
        and claims.get("diagnostic_launches_not_accepted_as_evidence") is True
        and claims.get("scientific_inputs_unchanged") is True
        and claims.get("accepted_goal5840_result") is False
        and claims.get("lowering_preservation_established") is False
        and claims.get("performance_or_speedup") is False
        and claims.get("application_correctness") is False
        and claims.get("external_review_or_consensus") is False,
        "Attempt-03 repair authority claim boundary differs",
    )
    return {
        str(row["key"]): row
        for row in _sequence(
            document.get("mode_cases"), "attempt_03_repair_authority.mode_cases"
        )
        if isinstance(row, dict)
    }


def _verify_attempt04_repair_authority(
    document: Mapping[str, object], *, root: Path, commit: str,
    original: Mapping[str, object], prior: Mapping[str, object],
    preregistration: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    _require(
        document.get("schema")
        == "rtdl.goal5840.post_attempt_04_repair_authority.v1"
        and document.get("stage")
        == "AFTER_ATTEMPT_04_BEFORE_ATTEMPT_05_GPU_EXECUTION"
        and document.get("status")
        == (
            "FROZEN_TRIANGLE_STATUS_FLOW_CHECKER_REPAIR__"
            "NO_COMPLETE_ACCEPTED_RESULT"
        ),
        "Attempt-04 repair authority status differs",
    )
    _verify_seal(
        document,
        "authority_sha256",
        ATTEMPT_04_REPAIR_AUTHORITY_DOMAIN,
        "attempt_04_repair_authority",
    )
    _require(
        document.get("route_bundle_group_count") == 3
        and document.get("required_mode_count") == 4
        and document.get("mode_cases") == prior.get("mode_cases")
        and document.get("mode_cases") == original.get("mode_cases")
        and document.get("goal5838_frozen_core")
        == prior.get("goal5838_frozen_core")
        and document.get("preregistration") == prior.get("preregistration"),
        "Attempt-04 repair authority changed a scientific input",
    )

    chain = _mapping(
        document.get("base_chain"), "attempt_04_repair_authority.base_chain"
    )
    prior_ref = _mapping(
        chain.get("post_attempt_03_repair_authority"),
        "attempt_04_repair_authority.base_chain.post_attempt_03_repair_authority",
    )
    incident_ref = _mapping(
        chain.get("attempt_04_incident"),
        "attempt_04_repair_authority.base_chain.attempt_04_incident",
    )
    prior_blob = _git_blob(
        root, ATTEMPT_04_SOURCE_COMMIT, ATTEMPT_03_REPAIR_AUTHORITY_PATH
    )
    incident_blob = _git_blob(root, commit, ATTEMPT_04_INCIDENT_PATH)
    expected_failure_artifacts = [
        {
            "name": "mode_01_capacity_fail_closed_collection_bundle.json",
            "bytes": 1364069,
            "file_sha256": (
                "785b0b9906368eabfecb190b0f6afc0d0768c2bcad00144c"
                "d018e5636c0f1d76"
            ),
        },
        {
            "name": (
                "mode_01_capacity_fail_closed_collection_"
                "independent_check.json"
            ),
            "bytes": 3967,
            "file_sha256": (
                "0c007fea0a8ab28e1ba3fe2f04752126aef28cd6bd181a921"
                "3d31de5c3f69876"
            ),
            "verdict": "ACCEPT",
            "property_pass_count": 5,
        },
        {
            "name": "mode_02_all_hit_count_bundle.json",
            "bytes": 806032,
            "file_sha256": (
                "03e869e83164e3c8dac830111d7dbf17ae97ad0f69e00d3c"
                "5cb2f6bca7084739"
            ),
        },
        {
            "name": "mode_02_all_hit_count_independent_check.json",
            "bytes": 3616,
            "file_sha256": (
                "02fbbf9a788b2d8589a6911ce20f07fec0e8e71fec5871e4"
                "56c898d9888a6b90"
            ),
            "verdict": "REJECT",
            "property_pass_count": 4,
            "property_reject_count": 1,
            "reason_id": "TC004_STATUS_SOURCE_ANCHOR_MISSING",
        },
    ]
    _require(
        chain.get("attempt_04_source_commit") == ATTEMPT_04_SOURCE_COMMIT
        and prior_ref.get("path") == ATTEMPT_03_REPAIR_AUTHORITY_PATH
        and prior_ref.get("bytes") == len(prior_blob)
        and prior_ref.get("file_sha256") == hashlib.sha256(prior_blob).hexdigest()
        and prior_ref.get("authority_sha256") == prior.get("authority_sha256")
        and incident_ref.get("path") == ATTEMPT_04_INCIDENT_PATH
        and incident_ref.get("bytes") == len(incident_blob)
        and incident_ref.get("file_sha256") == ATTEMPT_04_INCIDENT_SHA256
        and hashlib.sha256(incident_blob).hexdigest()
        == ATTEMPT_04_INCIDENT_SHA256
        and incident_ref.get("classification")
        == (
            "INDEPENDENT_CHECKER_TRIANGLE_STATUS_FLOW_RULE_"
            "ENGINEERING_FAILURE"
        )
        and incident_ref.get("published_failure_artifacts")
        == expected_failure_artifacts,
        "Attempt-04 repair authority base chain differs",
    )
    _require(
        chain.get("formal_observed_counts_through_attempt_04")
        == {
            "runner_processes_started": 4,
            "frozen_modes_entered": 5,
            "public_route_expected_outputs_returned": 5,
            "published_evidence_bundles": 3,
            "published_independent_property_reports": 3,
            "independently_accepted_per_mode_reports": 1,
            "published_mutation_applications": 0,
            "accepted_complete_goal5840_results": 0,
        }
        and chain.get("prior_post_failure_gpu_diagnostics")
        == {
            "diagnostic_processes": 2,
            "diagnostic_mode_executions": 2,
            "accepted_as_evidence": 0,
        }
        and chain.get("attempt_04_post_failure_gpu_diagnostics")
        == {
            "diagnostic_processes": 0,
            "diagnostic_mode_executions": 0,
            "accepted_as_evidence": 0,
        }
        and chain.get("attempt_04_post_failure_offline_checker_diagnostics")
        == {
            "processes": 2,
            "bundle_checks": 3,
            "accepted_bundle_checks": 2,
            "accepted_as_formal_evidence": 0,
        }
        and document.get("execution_counts_at_repair_freeze")
        == {
            "formal_runner_processes": 4,
            "formal_entered_modes": 5,
            "formal_returned_expected_outputs": 5,
            "prior_gpu_diagnostic_processes": 2,
            "prior_gpu_diagnostic_mode_executions": 2,
            "published_evidence_bundles": 3,
            "published_independent_property_reports": 3,
            "independently_accepted_per_mode_reports": 1,
            "published_mutation_applications": 0,
            "accepted_goal5840_complete_results": 0,
        },
        "Attempt-04 repair authority execution history differs",
    )

    scope = _mapping(
        document.get("repair_scope"), "attempt_04_repair_authority.repair_scope"
    )
    _require(
        scope.get("defect")
        == "stale_synthetic_triangle_status_flow_text_anchors"
        and scope.get("repair")
        == (
            "route_specific_lexically_masked_entry_function_status_"
            "flow_and_cardinality_checks"
        )
        and scope.get("allowed_changed_paths")
        == list(ATTEMPT_04_REPAIR_ALLOWED_CHANGED_PATHS)
        and scope.get("exact_changed_paths_since_base")
        == list(ATTEMPT_04_REPAIR_ALLOWED_CHANGED_PATHS)
        and scope.get("triangle_fast_and_diagnostic_paths_checked") is True
        and scope.get("comment_and_string_spoofing_rejected") is True
        and all(
            scope.get(field) is False
            for field in (
                "route_change_allowed",
                "fixture_or_oracle_change_allowed",
                "declaration_or_control_root_change_allowed",
                "property_or_mutation_change_allowed",
                "native_engine_or_runtime_change_allowed",
                "frozen_core_change_allowed",
            )
        ),
        "Attempt-04 repair authority scope differs",
    )
    _require(
        _git_changed_paths(root, ATTEMPT_04_SOURCE_COMMIT, commit)
        == ATTEMPT_04_REPAIR_ALLOWED_CHANGED_PATHS,
        "Attempt-04 repair changed an unapproved path",
    )
    source_rows = _verify_source_rows(
        document.get("source_files"),
        root=root,
        commit=commit,
        label="attempt_04_repair_authority.source_files",
    )
    prior_source_paths = {
        str(row.get("path"))
        for row in _sequence(
            prior.get("source_files"), "attempt_03_repair_authority.source_files"
        )
        if isinstance(row, dict)
    }
    _require(
        set(source_rows)
        == prior_source_paths | {"scripts/goal5840_freeze_attempt04_repair_inputs.py"}
        and RUNTIME_SOURCE_PATHS <= set(source_rows),
        "Attempt-04 repair authority source denominator differs",
    )
    current_prereg = _mapping(
        document.get("preregistration"),
        "attempt_04_repair_authority.preregistration",
    )
    _require(
        current_prereg == prior.get("preregistration")
        and current_prereg.get("authority_sha256")
        == preregistration.get("authority_sha256"),
        "Attempt-04 repair authority preregistration chain differs",
    )
    claims = _mapping(
        document.get("claim_boundary"),
        "attempt_04_repair_authority.claim_boundary",
    )
    _require(
        claims.get("append_only_engineering_repair_authority") is True
        and claims.get("four_prior_formal_failures_preserved") is True
        and claims.get("attempt_04_mode_01_acceptance_preserved") is True
        and claims.get("attempt_04_incomplete_run_not_accepted_as_goal_result")
        is True
        and claims.get("diagnostic_processes_not_accepted_as_evidence") is True
        and claims.get("scientific_inputs_unchanged") is True
        and claims.get("accepted_goal5840_result") is False
        and claims.get("lowering_preservation_established") is False
        and claims.get("performance_or_speedup") is False
        and claims.get("application_correctness") is False
        and claims.get("external_review_or_consensus") is False,
        "Attempt-04 repair authority claim boundary differs",
    )
    return {
        str(row["key"]): row
        for row in _sequence(
            document.get("mode_cases"), "attempt_04_repair_authority.mode_cases"
        )
        if isinstance(row, dict)
    }


def _verify_mutation_report(
    report: Mapping[str, object], frozen: Mapping[str, Mapping[str, object]]
) -> None:
    _require(
        report.get("schema") == "rtdl.goal5840.exact_bundle_mutation_suite.v1"
        and report.get("status")
        == "PASS__ALL_FROZEN_MUTATIONS_REJECTED_BEFORE_GPU_LAUNCH",
        "mutation report status differs",
    )
    _verify_seal(report, "report_sha256", MUTATION_DOMAIN, "mutation_report")
    _require(
        report.get("preregistered_claim_unit_count") == 15
        and report.get("mode_replication_application_count") == 20
        and report.get("rejected_application_count") == 20
        and report.get("all_rejected_before_gpu_launch") is True,
        "mutation report denominator differs",
    )
    expected = {
        (route_id, mode, property_id)
        for route_id, modes in EXPECTED_MODES.items()
        for mode in modes
        for property_id in PROPERTIES
    }
    observed = set()
    rows = _sequence(report.get("applications"), "mutation_report.applications")
    for value in rows:
        row = _mapping(value, "mutation_report.applications[]")
        key = (str(row.get("route_id")), str(row.get("mode")), str(row.get("property_id")))
        unit_id = f"{key[0]}::{key[2]}"
        frozen_row = frozen.get(unit_id)
        _require(
            frozen_row is not None and key not in observed,
            "mutation application identity differs",
        )
        _require(
            row.get("mutation_id") == unit_id
            and row.get("target_selector") == frozen_row.get("target_selector")
            and row.get("replacement") == frozen_row.get("replacement")
            and row.get("preregistered_required_rejection")
            == frozen_row.get("required_rejection")
            and row.get("checker_verdict") == "REJECT"
            and row.get("target_property_verdict") == "REJECT"
            and str(row.get("target_property_reason_id", "")).startswith(
                "TC" + key[2][2:5]
            )
            and row.get("gpu_launch_required_for_rejection") is False,
            f"mutation application did not reject its target property: {key}",
        )
        observed.add(key)
    _require(len(rows) == 20 and observed == expected, "mutation applications differ")


def _run_checker(bundle_path: Path, roots: Mapping[str, object]) -> dict[str, Any]:
    command = [
        sys.executable,
        "-I",
        str(CHECKER),
        str(bundle_path),
        "--trusted-declaration-sha256",
        _sha(roots.get("declaration_sha256"), "trust.declaration_sha256"),
        "--trusted-executable-identity-sha256",
        _sha(roots.get("executable_identity_sha256"), "trust.executable_identity_sha256"),
        "--trusted-control-flow-manifest-sha256",
        _sha(roots.get("control_flow_manifest_sha256"), "trust.control_flow_manifest_sha256"),
    ]
    completed = subprocess.run(
        command,
        cwd=bundle_path.parent,
        env={"PATH": os.environ.get("PATH", "")},
        text=True,
        capture_output=True,
        check=False,
    )
    _require(
        completed.returncode == 0,
        f"standalone checker rejected {bundle_path.name}: {completed.stdout} {completed.stderr}",
    )
    try:
        return _mapping(json.loads(completed.stdout), "replayed_checker_report")
    except json.JSONDecodeError as error:
        raise Goal5840EvidenceVerificationError(
            f"standalone checker output is not JSON: {error}"
        ) from error


def _run_mutation_suite(
    bundle_paths: Sequence[Path], trust_roots_path: Path
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as name:
        output = Path(name) / "replayed_mutations.json"
        command = [
            sys.executable,
            "-I",
            str(MUTATION_RUNNER),
            "--trust-roots",
            str(trust_roots_path),
            "--output",
            str(output),
        ]
        for path in bundle_paths:
            command.extend(("--bundle", str(path)))
        completed = subprocess.run(
            command,
            cwd=trust_roots_path.parent,
            env={"PATH": os.environ.get("PATH", "")},
            text=True,
            capture_output=True,
            check=False,
        )
        _require(
            completed.returncode == 0,
            "isolated mutation replay failed: "
            f"{completed.stdout} {completed.stderr}",
        )
        return _load_json(output, "replayed_mutation_report")


def _verify_mode(
    row: Mapping[str, object], *, directory: Path,
    trust_roots: Mapping[str, Mapping[str, object]],
    frozen_modes: Mapping[str, Mapping[str, object]], native_sha256: str,
) -> dict[str, object]:
    route_id = str(row.get("route_id"))
    mode = str(row.get("mode"))
    key = row.get("key")
    _require(key == f"{route_id}::{mode}" and key in frozen_modes, "mode key differs")
    roots = trust_roots.get(str(key))
    _require(isinstance(roots, Mapping), f"missing trust roots for {key}")
    frozen = frozen_modes[str(key)]
    _require(
        row.get("fixture_sha256") == frozen.get("fixture_sha256")
        and row.get("expected_output") == frozen.get("expected_output")
        and row.get("expected_output_sha256") == frozen.get("expected_output_sha256")
        and row.get("observed_output") == row.get("expected_output")
        and _digest(row.get("observed_output")) == row.get("observed_output_sha256")
        and row.get("true_optix") is True,
        f"mode oracle/output contract differs: {key}",
    )
    bundle_path = _safe_member(directory, row.get("bundle_file"), f"{key}.bundle_file")
    bundle = _load_json(bundle_path, f"{key}.bundle")
    _require(
        bundle.get("bundle_sha256") == row.get("bundle_sha256"),
        f"bundle seal reference differs: {key}",
    )
    receipt = _mapping(bundle.get("execution_receipt"), f"{key}.execution_receipt")
    physical = _mapping(bundle.get("physical_evidence"), f"{key}.physical_evidence")
    identity = _mapping(physical.get("executable_identity"), f"{key}.identity")
    control = _mapping(physical.get("target_control_flow_evidence"), f"{key}.control")
    traversal = _mapping(receipt.get("traversal_receipt"), f"{key}.traversal_receipt")
    declaration = _mapping(bundle.get("declaration"), f"{key}.declaration")
    _require(
        bundle.get("route_id") == route_id
        and receipt.get("route_id") == route_id
        and receipt.get("mode") == mode
        and receipt.get("status") == "OK"
        and receipt.get("status_code") == 0
        and receipt.get("status_before_output") is True
        and receipt.get("complete") is True
        and receipt.get("partial_result_exposed") is False
        and receipt.get("native_library_sha256") == native_sha256
        and traversal.get("physical_executor_classification") == "optix_traversal_observed"
        and traversal.get("provider_library_sha256") == native_sha256
        and traversal.get("output_digest") == row.get("observed_output_sha256"),
        f"true-OptiX execution receipt differs: {key}",
    )
    _require(
        declaration.get("declaration_sha256") == roots.get("declaration_sha256")
        == frozen.get("declaration_sha256")
        and identity.get("identity_sha256") == roots.get("executable_identity_sha256")
        and control.get("manifest_sha256") == roots.get("control_flow_manifest_sha256")
        == frozen.get("control_flow_manifest_sha256"),
        f"mode trust-root binding differs: {key}",
    )
    stored_path = _safe_member(
        directory, row.get("independent_check_file"), f"{key}.independent_check_file"
    )
    stored = _load_json(stored_path, f"{key}.stored_checker_report")
    _verify_seal(stored, "report_sha256", CHECKER_REPORT_DOMAIN, f"{key}.checker")
    replayed = _run_checker(bundle_path, roots)
    _require(stored == replayed, f"stored/replayed checker report differs: {key}")
    _require(
        stored.get("verdict") == "ACCEPT"
        and stored.get("pass_count") == 5
        and stored.get("reject_count") == 0
        and {
            item.get("property_id")
            for item in _sequence(
                stored.get("property_checks"), "property_checks"
            )
        }
        == set(PROPERTIES)
        and row.get("independent_check_sha256") == stored.get("report_sha256")
        and row.get("independent_property_pass_count") == 5,
        f"positive checker denominator differs: {key}",
    )
    return {
        "key": key,
        "bundle_file_sha256": _sha_file(bundle_path),
        "checker_file_sha256": _sha_file(stored_path),
        "bundle_sha256": bundle.get("bundle_sha256"),
        "checker_report_sha256": stored.get("report_sha256"),
    }


def verify(
    result_path: Path, *, native_path: Path, native_build_manifest_path: Path,
    expected_commit: str, repository_root: Path = ROOT,
) -> dict[str, object]:
    root = repository_root.resolve(strict=True)
    result_path = result_path.expanduser().resolve(strict=True)
    directory = result_path.parent
    summary = _load_json(result_path, "RESULT")
    _require(
        summary.get("schema") == "rtdl.goal5840.true_optix_target_evidence.v5"
        and summary.get("status")
        == "PASS__FOUR_MODES_TRUE_OPTIX_AND_15_UNIQUE_MUTATIONS_REJECTED",
        "RESULT status differs",
    )
    _require(summary.get("formal_attempt_number") == 5, "formal attempt differs")
    summary_sha = _verify_seal(summary, "summary_sha256", SUMMARY_DOMAIN, "RESULT")
    repository = _mapping(summary.get("repository"), "RESULT.repository")
    commit = _commit(
        repository.get("expected_commit"), "repository.expected_commit"
    )
    _require(
        commit == _commit(expected_commit, "expected_commit")
        and repository.get("head_before") == commit
        and repository.get("head_after") == commit
        and repository.get("clean_before") is True
        and repository.get("clean_after") is True,
        "repository custody differs",
    )
    repository_sources = _verify_source_rows(
        repository.get("source_files"), root=root, commit=commit,
        label="RESULT.repository.source_files",
    )
    _require(
        set(repository_sources) == RESULT_SOURCE_PATHS,
        "RESULT repository custody source denominator differs",
    )
    for path in RUNTIME_SOURCE_PATHS:
        current = (root / path).resolve(strict=True)
        try:
            current.relative_to(root)
        except ValueError as error:
            raise Goal5840EvidenceVerificationError(
                f"runtime source escapes repository: {path}"
            ) from error
        _require(
            current.is_file()
            and current.read_bytes() == _git_blob(root, commit, path),
            f"local verifier/runtime source differs from evidence commit: {path}",
        )

    prereg_ref = _mapping(summary.get("preregistration"), "RESULT.preregistration")
    prereg = _load_committed_json(
        root, commit, prereg_ref.get("path"), prereg_ref.get("file_sha256"),
        "preregistration",
    )
    current_prereg = (root / str(prereg_ref.get("path"))).resolve(strict=True)
    try:
        current_prereg.relative_to(root)
    except ValueError as error:
        raise Goal5840EvidenceVerificationError(
            "preregistration path escapes repository"
        ) from error
    _require(
        current_prereg.read_bytes()
        == _git_blob(root, commit, str(prereg_ref.get("path"))),
        "local preregistration differs from evidence commit",
    )
    _require(
        prereg_ref.get("authority_sha256") == prereg.get("authority_sha256"),
        "preregistration authority reference differs",
    )
    frozen_mutations = _verify_preregistration(prereg)

    pre_pod_ref = _mapping(
        summary.get("pre_pod_input_authority"), "RESULT.pre_pod_input_authority"
    )
    pre_pod_commit = _commit(
        pre_pod_ref.get("source_commit"), "pre_pod_input_authority.source_commit"
    )
    _require(
        pre_pod_commit == ATTEMPT_01_SOURCE_COMMIT,
        "pre-pod authority source commit differs",
    )
    pre_pod = _load_committed_json(
        root,
        pre_pod_commit,
        pre_pod_ref.get("path"),
        pre_pod_ref.get("file_sha256"),
        "pre_pod_authority",
    )
    _require(
        pre_pod_ref.get("authority_sha256") == pre_pod.get("authority_sha256"),
        "pre-pod authority reference differs",
    )
    original_frozen_modes = _verify_pre_pod_authority(
        pre_pod, root=root, commit=pre_pod_commit
    )
    pre_pod_sources = {
        str(row.get("path"))
        for row in _sequence(pre_pod.get("source_files"), "pre_pod.source_files")
        if isinstance(row, dict)
    }
    _require(
        ORIGINAL_RUNTIME_SOURCE_PATHS <= pre_pod_sources,
        "pre-pod authority omits an original Goal5840 runtime source",
    )
    pre_pod_prereg = _mapping(
        pre_pod.get("preregistration"), "pre_pod.preregistration"
    )
    _require(
        pre_pod_prereg.get("path") == prereg_ref.get("path")
        and pre_pod_prereg.get("file_sha256")
        == prereg_ref.get("file_sha256")
        and pre_pod_prereg.get("authority_sha256")
        == prereg_ref.get("authority_sha256"),
        "pre-pod/preregistration cross-reference differs",
    )

    incident_ref = _mapping(
        summary.get("attempt_01_engineering_failure"),
        "RESULT.attempt_01_engineering_failure",
    )
    incident_path = incident_ref.get("path")
    _require(
        incident_path == ATTEMPT_01_INCIDENT_PATH
        and incident_ref.get("accepted_positive_evidence_rows") == 0,
        "Attempt-01 incident reference differs",
    )
    incident_blob = _git_blob(root, commit, ATTEMPT_01_INCIDENT_PATH)
    _require(
        incident_ref.get("bytes") == len(incident_blob)
        and incident_ref.get("file_sha256") == ATTEMPT_01_INCIDENT_SHA256
        and hashlib.sha256(incident_blob).hexdigest()
        == ATTEMPT_01_INCIDENT_SHA256,
        "Attempt-01 incident bytes differ",
    )

    repair_ref = _mapping(
        summary.get("post_attempt_01_repair_authority"),
        "RESULT.post_attempt_01_repair_authority",
    )
    repair = _load_committed_json(
        root,
        ATTEMPT_01_REPAIR_COMMIT,
        repair_ref.get("path"),
        repair_ref.get("file_sha256"),
        "repair_authority",
    )
    _require(
        repair_ref.get("path") == REPAIR_AUTHORITY_PATH
        and repair_ref.get("authority_sha256")
        == repair.get("authority_sha256"),
        "repair authority reference differs",
    )
    frozen_modes = _verify_repair_authority(
        repair,
        root=root,
        commit=ATTEMPT_01_REPAIR_COMMIT,
        original=pre_pod,
        preregistration=prereg,
    )
    _require(
        frozen_modes == original_frozen_modes,
        "repair authority mode rows differ from original freeze",
    )

    attempt02_incident_ref = _mapping(
        summary.get("attempt_02_engineering_failure"),
        "RESULT.attempt_02_engineering_failure",
    )
    _require(
        attempt02_incident_ref.get("path") == ATTEMPT_02_INCIDENT_PATH
        and attempt02_incident_ref.get("accepted_positive_evidence_rows") == 0
        and attempt02_incident_ref.get("diagnostic_launches_accepted_as_evidence")
        == 0,
        "Attempt-02 incident reference differs",
    )
    attempt02_incident_blob = _git_blob(
        root, ATTEMPT_03_SOURCE_COMMIT, ATTEMPT_02_INCIDENT_PATH
    )
    _require(
        attempt02_incident_ref.get("bytes") == len(attempt02_incident_blob)
        and attempt02_incident_ref.get("file_sha256")
        == ATTEMPT_02_INCIDENT_SHA256
        and hashlib.sha256(attempt02_incident_blob).hexdigest()
        == ATTEMPT_02_INCIDENT_SHA256,
        "Attempt-02 incident bytes differ",
    )

    attempt02_repair_ref = _mapping(
        summary.get("post_attempt_02_repair_authority"),
        "RESULT.post_attempt_02_repair_authority",
    )
    attempt02_repair = _load_committed_json(
        root,
        ATTEMPT_03_SOURCE_COMMIT,
        attempt02_repair_ref.get("path"),
        attempt02_repair_ref.get("file_sha256"),
        "attempt_02_repair_authority",
    )
    _require(
        attempt02_repair_ref.get("path") == ATTEMPT_02_REPAIR_AUTHORITY_PATH
        and attempt02_repair_ref.get("authority_sha256")
        == attempt02_repair.get("authority_sha256"),
        "Attempt-02 repair authority reference differs",
    )
    attempt02_frozen_modes = _verify_attempt02_repair_authority(
        attempt02_repair,
        root=root,
        commit=ATTEMPT_03_SOURCE_COMMIT,
        original=pre_pod,
        prior=repair,
        preregistration=prereg,
    )
    _require(
        attempt02_frozen_modes == frozen_modes,
        "Attempt-02 repair authority mode rows differ from original freeze",
    )
    frozen_modes = attempt02_frozen_modes

    attempt03_incident_ref = _mapping(
        summary.get("attempt_03_engineering_failure"),
        "RESULT.attempt_03_engineering_failure",
    )
    _require(
        attempt03_incident_ref.get("path") == ATTEMPT_03_INCIDENT_PATH
        and attempt03_incident_ref.get("published_failure_bundle_count") == 1
        and attempt03_incident_ref.get("published_reject_report_count") == 1
        and attempt03_incident_ref.get("accepted_positive_evidence_rows") == 0
        and attempt03_incident_ref.get("post_failure_gpu_diagnostic_launches")
        == 0,
        "Attempt-03 incident reference differs",
    )
    attempt03_incident_blob = _git_blob(
        root, ATTEMPT_04_SOURCE_COMMIT, ATTEMPT_03_INCIDENT_PATH
    )
    _require(
        attempt03_incident_ref.get("bytes") == len(attempt03_incident_blob)
        and attempt03_incident_ref.get("file_sha256")
        == ATTEMPT_03_INCIDENT_SHA256
        and hashlib.sha256(attempt03_incident_blob).hexdigest()
        == ATTEMPT_03_INCIDENT_SHA256,
        "Attempt-03 incident bytes differ",
    )

    attempt03_repair_ref = _mapping(
        summary.get("post_attempt_03_repair_authority"),
        "RESULT.post_attempt_03_repair_authority",
    )
    attempt03_repair = _load_committed_json(
        root,
        ATTEMPT_04_SOURCE_COMMIT,
        attempt03_repair_ref.get("path"),
        attempt03_repair_ref.get("file_sha256"),
        "attempt_03_repair_authority",
    )
    _require(
        attempt03_repair_ref.get("path") == ATTEMPT_03_REPAIR_AUTHORITY_PATH
        and attempt03_repair_ref.get("authority_sha256")
        == attempt03_repair.get("authority_sha256"),
        "Attempt-03 repair authority reference differs",
    )
    attempt03_frozen_modes = _verify_attempt03_repair_authority(
        attempt03_repair,
        root=root,
        commit=ATTEMPT_04_SOURCE_COMMIT,
        original=pre_pod,
        prior=attempt02_repair,
        preregistration=prereg,
    )
    _require(
        attempt03_frozen_modes == frozen_modes,
        "Attempt-03 repair authority mode rows differ from original freeze",
    )
    frozen_modes = attempt03_frozen_modes

    attempt04_incident_ref = _mapping(
        summary.get("attempt_04_engineering_failure"),
        "RESULT.attempt_04_engineering_failure",
    )
    _require(
        attempt04_incident_ref.get("path") == ATTEMPT_04_INCIDENT_PATH
        and attempt04_incident_ref.get("published_failure_bundle_count") == 2
        and attempt04_incident_ref.get("published_independent_report_count")
        == 2
        and attempt04_incident_ref.get(
            "independently_accepted_per_mode_report_count"
        ) == 1
        and attempt04_incident_ref.get(
            "accepted_complete_goal5840_result_count"
        ) == 0
        and attempt04_incident_ref.get("post_failure_gpu_diagnostic_launches")
        == 0,
        "Attempt-04 incident reference differs",
    )
    attempt04_incident_blob = _git_blob(root, commit, ATTEMPT_04_INCIDENT_PATH)
    _require(
        attempt04_incident_ref.get("bytes") == len(attempt04_incident_blob)
        and attempt04_incident_ref.get("file_sha256")
        == ATTEMPT_04_INCIDENT_SHA256
        and hashlib.sha256(attempt04_incident_blob).hexdigest()
        == ATTEMPT_04_INCIDENT_SHA256,
        "Attempt-04 incident bytes differ",
    )

    attempt04_repair_ref = _mapping(
        summary.get("post_attempt_04_repair_authority"),
        "RESULT.post_attempt_04_repair_authority",
    )
    attempt04_repair = _load_committed_json(
        root,
        commit,
        attempt04_repair_ref.get("path"),
        attempt04_repair_ref.get("file_sha256"),
        "attempt_04_repair_authority",
    )
    _require(
        attempt04_repair_ref.get("path") == ATTEMPT_04_REPAIR_AUTHORITY_PATH
        and attempt04_repair_ref.get("authority_sha256")
        == attempt04_repair.get("authority_sha256"),
        "Attempt-04 repair authority reference differs",
    )
    attempt04_frozen_modes = _verify_attempt04_repair_authority(
        attempt04_repair,
        root=root,
        commit=commit,
        original=pre_pod,
        prior=attempt03_repair,
        preregistration=prereg,
    )
    _require(
        attempt04_frozen_modes == frozen_modes,
        "Attempt-04 repair authority mode rows differ from original freeze",
    )
    frozen_modes = attempt04_frozen_modes

    native = _mapping(summary.get("native"), "RESULT.native")
    native_path = native_path.expanduser().resolve(strict=True)
    native_sha = _sha(native.get("sha256"), "RESULT.native.sha256")
    _require(
        native_path.is_file()
        and native_path.stat().st_size == native.get("bytes")
        and _sha_file(native_path) == native_sha,
        "preserved native DSO differs",
    )
    dynamic_symbols = _defined_elf64_dynamic_symbols(native_path)
    missing_symbols = [
        symbol
        for symbol in GOAL5840_REQUIRED_NATIVE_SYMBOLS
        if symbol not in dynamic_symbols
    ]
    _require(not missing_symbols, f"native DSO misses Goal5840 ABI: {missing_symbols}")
    symbol_check = _mapping(
        native.get("goal5840_required_symbol_check"),
        "RESULT.native.goal5840_required_symbol_check",
    )
    _require(
        symbol_check.get("schema")
        == "rtdl.goal5840.required_native_symbols.v1"
        and symbol_check.get("method")
        == "gnu_nm_dynamic_external_defined_exact_name"
        and symbol_check.get("required_symbols")
        == list(GOAL5840_REQUIRED_NATIVE_SYMBOLS)
        and symbol_check.get("all_required_symbols_exported") is True
        and symbol_check.get("exported_symbol_count") == len(dynamic_symbols)
        and symbol_check.get("exported_symbol_names_sha256")
        == _digest(sorted(dynamic_symbols)),
        "runner/local native dynamic-symbol evidence differs",
    )
    build_ref = _mapping(native.get("build_manifest"), "RESULT.native.build_manifest")
    build_path = native_build_manifest_path.expanduser().resolve(strict=True)
    _require(
        build_path.is_file() and _sha_file(build_path) == build_ref.get("sha256"),
        "preserved native build manifest differs",
    )
    build = _load_json(build_path, "native_build_manifest")
    _verify_seal(
        build, "result_sha256", NATIVE_BUILD_DOMAIN, "native_build_manifest"
    )
    build_repo = _mapping(build.get("repository"), "native_build.repository")
    build_output = _mapping(build.get("native_output"), "native_build.native_output")
    build_input = _mapping(build.get("build_input"), "native_build.build_input")
    build_sources = _verify_source_rows(
        build_repo.get("source_files"),
        root=root,
        commit=commit,
        label="native_build.repository.source_files",
    )
    _require(
        build.get("status") == "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
        and build.get("all_required_symbols_exported") is True
        and build_repo.get("expected_commit") == commit
        and build_repo.get("head_before") == commit
        and build_repo.get("head_after") == commit
        and build_output.get("sha256") == native_sha,
        "native build does not bind the exact commit and DSO",
    )
    _require(
        NATIVE_BUILD_SOURCE_PATHS == set(build_sources)
        and build.get("build_input_sha256") == _digest(build_input)
        and build_input.get("builder_path")
        == "scripts/goal5838_build_selected_sphere_optix_provider.py"
        and build_input.get("builder_sha256")
        == build_sources[
            "scripts/goal5838_build_selected_sphere_optix_provider.py"
        ]["sha256"]
        and build_ref.get("schema") == build.get("schema")
        and build_ref.get("status") == build.get("status")
        and build_ref.get("result_sha256") == build.get("result_sha256"),
        "native build source/input identity differs",
    )

    trust_path = _safe_member(
        directory, summary.get("runtime_trust_roots_file"), "runtime_trust_roots_file"
    )
    trust = _load_json(trust_path, "runtime_trust_roots")
    _require(
        trust.get("schema") == "rtdl.goal5840.runtime_trust_roots.v1",
        "runtime trust-root schema differs",
    )
    trust_sha = _verify_seal(
        trust, "trust_roots_sha256", TRUST_ROOT_DOMAIN, "runtime_trust_roots"
    )
    _require(
        summary.get("runtime_trust_roots_sha256") == trust_sha,
        "RESULT trust-root reference differs",
    )
    trust_roots = _mapping(trust.get("trust_roots"), "runtime_trust_roots.trust_roots")
    _require(set(trust_roots) == _expected_mode_keys(), "runtime trust-root denominator differs")

    mode_rows = _sequence(summary.get("mode_cases"), "RESULT.mode_cases")
    observed_keys = [row.get("key") for row in mode_rows if isinstance(row, dict)]
    _require(
        len(mode_rows) == 4
        and len(observed_keys) == 4
        and set(observed_keys) == _expected_mode_keys(),
        "RESULT mode denominator differs",
    )
    verified_modes = [
        _verify_mode(
            _mapping(row, "RESULT.mode_cases[]"),
            directory=directory,
            trust_roots=trust_roots,
            frozen_modes=frozen_modes,
            native_sha256=native_sha,
        )
        for row in mode_rows
    ]

    mutation_path = _safe_member(
        directory, summary.get("mutation_result_file"), "mutation_result_file"
    )
    mutation = _load_json(mutation_path, "mutation_report")
    _verify_mutation_report(mutation, frozen_mutations)
    replayed_mutation = _run_mutation_suite(
        [
            _safe_member(directory, row.get("bundle_file"), "mode.bundle_file")
            for row in mode_rows
            if isinstance(row, Mapping)
        ],
        trust_path,
    )
    _require(
        replayed_mutation == mutation,
        "stored/replayed exact-bundle mutation report differs",
    )
    _require(
        summary.get("mutation_result_sha256") == mutation.get("report_sha256")
        and summary.get("route_bundle_group_count") == 3
        and summary.get("required_mode_bundle_count") == 4
        and summary.get("true_optix_mode_count") == 4
        and summary.get("independent_property_pass_count") == 20
        and summary.get("preregistered_unique_mutation_count") == 15
        and summary.get("mode_replication_mutation_count") == 20,
        "RESULT positive/mutation denominator differs",
    )
    summary_claims = _mapping(
        summary.get("claim_boundary"), "RESULT.claim_boundary"
    )
    _require(
        summary_claims.get("three_bounded_routes_only") is True
        and summary_claims.get("four_required_modes") is True
        and summary_claims.get("target_side_structural_refinement_evidence")
        is True
        and summary_claims.get(
            "attempt_01_preserved_as_unaccepted_engineering_failure"
        ) is True
        and summary_claims.get(
            "attempt_02_preserved_as_unaccepted_engineering_failure"
        ) is True
        and summary_claims.get(
            "attempt_03_preserved_as_unaccepted_engineering_failure"
        ) is True
        and summary_claims.get(
            "attempt_04_preserved_as_incomplete_engineering_failure"
        ) is True
        and summary_claims.get(
            "attempt_04_mode_01_acceptance_preserved_without_goal_promotion"
        ) is True
        and summary_claims.get(
            "diagnostic_launches_preserved_as_unaccepted_engineering_work"
        ) is True
        and summary_claims.get("append_only_repair_authority_chain_verified")
        is True
        and summary_claims.get("general_compiler_soundness") is False
        and summary_claims.get("application_correctness") is False
        and summary_claims.get("performance_or_speedup") is False
        and summary_claims.get("external_review_or_consensus") is False,
        "RESULT claim boundary differs",
    )
    frozen_core = _mapping(summary.get("frozen_core"), "RESULT.frozen_core")
    _require(
        frozen_core == pre_pod.get("goal5838_frozen_core")
        and frozen_core == repair.get("goal5838_frozen_core")
        and frozen_core == attempt02_repair.get("goal5838_frozen_core")
        and frozen_core == attempt03_repair.get("goal5838_frozen_core")
        and frozen_core == attempt04_repair.get("goal5838_frozen_core")
        and frozen_core.get("changed_file_count") == 0
        and len(_sequence(frozen_core.get("files"), "frozen_core.files")) == 3,
        "Goal5838 frozen-core preservation differs",
    )

    report: dict[str, object] = {
        "schema": "rtdl.goal5840.downloaded_gpu_evidence_verification.v5",
        "status": "PASS__DOWNLOADED_GOAL5840_EVIDENCE_REPLAYED_AND_BOUND",
        "formal_attempt_number": 5,
        "source_commit": commit,
        "attempt_01_source_commit": ATTEMPT_01_SOURCE_COMMIT,
        "pre_pod_authority_sha256": pre_pod.get("authority_sha256"),
        "attempt_01_incident_file_sha256": ATTEMPT_01_INCIDENT_SHA256,
        "repair_authority_sha256": repair.get("authority_sha256"),
        "attempt_01_repair_commit": ATTEMPT_01_REPAIR_COMMIT,
        "attempt_02_incident_file_sha256": ATTEMPT_02_INCIDENT_SHA256,
        "attempt_02_repair_authority_sha256": attempt02_repair.get(
            "authority_sha256"
        ),
        "attempt_03_source_commit": ATTEMPT_03_SOURCE_COMMIT,
        "attempt_03_incident_file_sha256": ATTEMPT_03_INCIDENT_SHA256,
        "attempt_03_repair_authority_sha256": attempt03_repair.get(
            "authority_sha256"
        ),
        "attempt_04_source_commit": ATTEMPT_04_SOURCE_COMMIT,
        "attempt_04_incident_file_sha256": ATTEMPT_04_INCIDENT_SHA256,
        "attempt_04_repair_authority_sha256": attempt04_repair.get(
            "authority_sha256"
        ),
        "result_file_sha256": _sha_file(result_path),
        "summary_sha256": summary_sha,
        "native_file_sha256": native_sha,
        "native_required_symbol_count": len(GOAL5840_REQUIRED_NATIVE_SYMBOLS),
        "native_exported_symbol_count": len(dynamic_symbols),
        "native_build_manifest_file_sha256": _sha_file(build_path),
        "runtime_trust_roots_file_sha256": _sha_file(trust_path),
        "mutation_result_file_sha256": _sha_file(mutation_path),
        "verified_route_group_count": 3,
        "verified_mode_count": 4,
        "replayed_property_pass_count": 20,
        "verified_unique_mutation_count": 15,
        "verified_mutation_application_count": 20,
        "mode_evidence": verified_modes,
        "claim_boundary": {
            "downloaded_exact_artifact_verification_only": True,
            "three_bounded_routes_only": True,
            "general_compiler_soundness": False,
            "application_correctness": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        },
        "verification_sha256": "",
    }
    report["verification_sha256"] = hashlib.sha256(
        VERIFICATION_DOMAIN + _canonical(report)
    ).hexdigest()
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(
        args.result,
        native_path=args.native,
        native_build_manifest_path=args.native_build_manifest,
        expected_commit=args.expected_commit,
        repository_root=args.repository_root,
    )
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        with args.output.expanduser().open("x", encoding="ascii") as stream:
            stream.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
