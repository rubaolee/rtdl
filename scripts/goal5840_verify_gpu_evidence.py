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
SUMMARY_DOMAIN = b"rtdl.goal5840.true_optix_target_evidence.v1\0"
TRUST_ROOT_DOMAIN = b"rtdl.goal5840.runtime_trust_roots.v1\0"
MUTATION_DOMAIN = b"rtdl.goal5840.exact_bundle_mutation_suite.v1\0"
CHECKER_REPORT_DOMAIN = b"rtdl.goal5840.independent_target_check.v1\0"
PREREGISTRATION_DOMAIN = (
    b"rtdl.goal5840.independent_lowering_refinement_preregistration.v1\0"
)
PRE_POD_DOMAIN = b"rtdl.goal5840.pre_pod_input_authority.v1\0"
VERIFICATION_DOMAIN = b"rtdl.goal5840.downloaded_gpu_evidence_verification.v1\0"
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
RUNTIME_SOURCE_PATHS = frozenset({
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_gpu_inputs.py",
    "scripts/goal5840_gpu_cases.py",
    "scripts/goal5840_independent_target_checker.py",
    "scripts/goal5840_mutation_suite.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_control_flow_evidence.py",
    "src/rtdsl/v4_target_evidence_bundle.py",
    "src/rtdsl/v4_target_evidence_capture.py",
})
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
        summary.get("schema") == "rtdl.goal5840.true_optix_target_evidence.v1"
        and summary.get("status")
        == "PASS__FOUR_MODES_TRUE_OPTIX_AND_15_UNIQUE_MUTATIONS_REJECTED",
        "RESULT status differs",
    )
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
        RUNTIME_SOURCE_PATHS <= set(repository_sources),
        "RESULT repository custody omits a Goal5840 runtime source",
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
    pre_pod = _load_committed_json(
        root, commit, pre_pod_ref.get("path"), pre_pod_ref.get("file_sha256"),
        "pre_pod_authority",
    )
    _require(
        pre_pod_ref.get("authority_sha256") == pre_pod.get("authority_sha256"),
        "pre-pod authority reference differs",
    )
    frozen_modes = _verify_pre_pod_authority(pre_pod, root=root, commit=commit)
    pre_pod_sources = {
        str(row.get("path"))
        for row in _sequence(pre_pod.get("source_files"), "pre_pod.source_files")
        if isinstance(row, dict)
    }
    _require(
        RUNTIME_SOURCE_PATHS <= pre_pod_sources,
        "pre-pod authority omits a Goal5840 runtime source",
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
    frozen_core = _mapping(summary.get("frozen_core"), "RESULT.frozen_core")
    _require(
        frozen_core == pre_pod.get("goal5838_frozen_core")
        and frozen_core.get("changed_file_count") == 0
        and len(_sequence(frozen_core.get("files"), "frozen_core.files")) == 3,
        "Goal5838 frozen-core preservation differs",
    )

    report: dict[str, object] = {
        "schema": "rtdl.goal5840.downloaded_gpu_evidence_verification.v1",
        "status": "PASS__DOWNLOADED_GOAL5840_EVIDENCE_REPLAYED_AND_BOUND",
        "source_commit": commit,
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
