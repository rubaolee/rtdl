#!/usr/bin/env python3
"""Create-only modern-RTX preparation for Goal5791.

This transaction requires a separately supplied, self-sealed owner authority.
It verifies the exact pre-POD bundle and three external uploads, creates one
new target materialization root, installs the frozen wheelhouse offline,
builds a fresh native,
executes four untimed K4 token-path smokes, and emits a target binding,
postprepare Stage-A authority, and sealed formal runtime.  It executes zero
formal workers and creates zero registered timings.  It never creates the
owner Stage-B formal authority.
"""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import shutil
import stat
import struct
import subprocess
import sys
import tarfile
import types


BUNDLE_SCHEMA = "rtdl.goal5791.pre_pod_bundle.v3"
OWNER_SCHEMA = "rtdl.goal5791.owner_create_only_target_prepare_authority.v1"
OWNER_STATUS = "OWNER_AUTHORIZED_EXACTLY_ONCE_CREATE_ONLY_TARGET_PREPARE"
STAGE_A_THIRD_POD_JUSTIFICATION = {
    "paid_transaction_ordinal_if_stage_a_is_authorized": 3,
    "original_v4_cgo_plan_paid_transaction_budget": 2,
    "original_two_transactions_spent_by": ["Goal5784", "Goal5785"],
    "original_two_transaction_budget_superseded": True,
    "superseding_requirement": (
        "Goal5788-A1 mandatory same-source same-cohort ablation before any "
        "checked-U64 causal performance claim"
    ),
    "goal5788_a1_mandatory_next_evidence_path": (
        "history/internal_docs/"
        "goal5788_amendment_a1_triangle_causal_interpretation_20260816.json"
    ),
    "goal5788_a1_mandatory_next_evidence_file_sha256": (
        "b13846a2bd37de10bdc1eae7df7620b0f32ce8824aed4310dbc2c5b62bfda157"
    ),
    "mandatory_next_evidence_same_source_tree": True,
    "mandatory_next_evidence_same_gpu_and_cohort": True,
    "pascal_cannot_execute_final_modern_rtx_measurement": True,
    "third_transaction_is_cost_of_correction_not_scope_creep": True,
    "stage_a_still_emits_zero_formal_workers_and_zero_registered_timings": True,
}
SOURCE_CPU_TEST_TIMEOUT_SECONDS = 1_200
TRUSTED_INDEPENDENT_PORTABLE_AUDITOR_SHA256 = (
    "04e75cb2040e4ba33ebb9956538fda6d7e13a4c5771c38be4c47acb66cce6f60"
)
SOURCE_MANIFEST_MEMBER = (
    "history/internal_docs/goal5791_portable_source_manifest_v1_20260817.json"
)
PRETARGET_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_pretarget_preexecution_authority_v9_20260820.json"
)
HOME_FUNCTIONAL_CLOSURE_MEMBER = "HOME_FUNCTIONAL_CLOSURE.json"
SEMANTIC_SUCCESSOR_MEMBER = (
    "SEMANTIC_PHYSICAL_VARIANT_SUCCESSOR_AUTHORITY.json"
)
OUTER_HARNESS_TO_SOURCE = {
    "HARNESS/CLEAN_VALIDATE.py": "scripts/goal5791_home_clean_validate.py",
    "HARNESS/HOME_TOKEN_WORKER.py": (
        "scripts/goal5791_home_token_validation.py"),
    "HARNESS/HOME_INDEPENDENT_RECOUNT.py": (
        "scripts/goal5791_independent_home_recount.py"),
    "HARNESS/TARGET_PREPARE.py": "scripts/goal5791_target_prepare.py",
    "HARNESS/TARGET_PRODUCER_PROBE.py": (
        "scripts/goal5791_target_producer_probe.py"),
    "HARNESS/OPEN_UPLOAD_STAGING.py": (
        "scripts/goal5791_open_upload_staging.py"),
    "HARNESS/OWNER_AUTHORITY_BUILDER.py": (
        "scripts/goal5791_build_owner_authority.py"),
    "HARNESS/INDEPENDENT_PORTABLE_AUDIT.py": (
        "scripts/goal5791_independent_portable_audit.py"),
    "HARNESS/FORMAL_CONTROLLER.py": "scripts/goal5791_formal_controller.py",
    "HARNESS/FORMAL_WORKER.py": "scripts/goal5791_formal_worker.py",
    "HARNESS/EVALUATE.py": "scripts/goal5791_formal_evaluate.py",
    "HARNESS/INDEPENDENT_RECOUNT.py": (
        "scripts/goal5791_formal_independent_recount.py"),
}
OUTER_TO_SOURCE_AUTHORITY_MEMBERS = {
    "CLAIM_AND_RELATED_WORK_FREEZE.json": (
        "history/internal_docs/"
        "goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json"
    ),
    "EXPECTED_VALUE_AND_FALLBACK.json": (
        "history/internal_docs/"
        "goal5790_preregistered_expected_value_and_fallback_20260816.json"
    ),
    "PREREGISTRATION.json": (
        "history/internal_docs/goal5791_preregistration_v9_20260820.json"
    ),
    "PRETARGET_PREEXECUTION_AUTHORITY.json": PRETARGET_AUTHORITY_MEMBER,
    "RUNTIME_BUDGET.json": (
        "history/internal_docs/"
        "goal5791_pre_pod_conservative_runtime_budget_20260817.json"
    ),
    "OWNER_AUTHORITY_REQUEST_PROTOCOL.md": (
        "history/internal_docs/"
        "goal5791_owner_authority_request_protocol_20260817.md"
    ),
}
BUNDLE_FIXED_PAYLOAD_MEMBERS = frozenset({
    "SOURCE.tar.gz",
    "SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
    "SOURCE_INDEPENDENT_AUDIT.json",
    "CLAIM_AND_RELATED_WORK_FREEZE.json",
    "SEMANTIC_PHYSICAL_VARIANT_SUCCESSOR_AUTHORITY.json",
    "EXPECTED_VALUE_AND_FALLBACK.json",
    "PREREGISTRATION.json",
    "PRETARGET_PREEXECUTION_AUTHORITY.json",
    "RUNTIME_BUDGET.json",
    "OWNER_AUTHORITY_REQUEST_PROTOCOL.md",
    "HOME_FUNCTIONAL_CLOSURE.json",
    "HOME_EVIDENCE_MANIFEST.json",
    "HOME_EVIDENCE_INDEPENDENT_AUDIT.json",
    "HOME_FUNCTIONAL_RECOUNT.json",
    "README.md",
})
EXPECTED_BUNDLE_PAYLOAD_MEMBERS = (
    BUNDLE_FIXED_PAYLOAD_MEMBERS | frozenset(OUTER_HARNESS_TO_SOURCE)
)
EXPECTED_BUNDLE_OUTER_MEMBERS = (
    EXPECTED_BUNDLE_PAYLOAD_MEMBERS | {"BUNDLE_MANIFEST.json"}
)
_HOME_ZERO_COUNT_KEYS = frozenset((
    "elapsed_value_count",
    "clock_sample_count",
    "reported_elapsed_value_count",
    "test_or_scientific_clock_sample_count",
    "registered_performance_timing_count",
))
_HOME_TRUE_OPERATIONAL_CLOCK_KEYS = frozenset((
    "operational_timeout_watchdog_uses_host_clock",
    "operational_watchdog_clock_not_persisted_or_registered",
))
_SOURCE_OPERATIONAL_TIMEOUT_FIELDS = {
    "cpu_test_timeout_seconds": 1_200,
}
_HOME_FALSE_OBSERVATION_KEYS = frozenset((
    "elapsed_values_recorded",
    "home_performance_observation_created",
    "home_performance_diagnostic_used",
    "registered_performance_timing_created",
    "performance_or_compiler_fusion_claimed",
    "performance_or_timing_claimed",
    "variant_selected_from_app_dataset_result_or_timing",
    "timing_or_duration_recorded",
    "performance_claimed",
    "performance_observation_created",
    "compiler_fusion_performance_demonstrated",
    "registered_performance_result_created",
    "home_timing_used_for_claim",
    "performance_evidence_included",
    "target_performance_observation",
    "evidence_hashing_or_serialization_inside_registered_timer",
    "registered_timing",
))
_HOME_TIMER_CONTRACT = {
    "schema": "rtdl.goal5791.home_zero_elapsed_observation.v1",
    "elapsed_value_count": 0,
    "clock_sample_count": 0,
    "home_performance_observation_created": False,
    "home_performance_diagnostic_used": False,
    "token_admission_before_device_geometry": True,
    "device_iterator_closed_before_evidence_seal": True,
}
_HOME_FORBIDDEN_OBSERVATION_KEY_TOKENS = (
    "elapsed", "clock", "duration", "timing", "timer", "timestamp",
    "monotonic", "perf_counter", "process_time", "wall_time", "latency",
    "throughput", "benchmark", "performance",
)
_HOME_FORBIDDEN_OBSERVATION_KEY_SUFFIXES = (
    "_started_ns", "_ended_ns", "_start_ns", "_end_ns",
    "_seconds", "_milliseconds", "_microseconds", "_nanoseconds",
)
HOME_FUNCTIONAL_CLOSURE_KEYS = frozenset("""
schema status execution_source_archive_sha256 execution_source_tree_sha256
source_manifest_sha256 native_library_sha256
target_materialization_receipt_sha256 target_materialization_evidence_sha256
home_evidence_sha256 home_evidence_twin_sha256 home_evidence_twin_byte_identical
home_evidence_manifest_sha256 home_evidence_independent_audit_sha256
home_evidence_payload_count gpu home_machine_authority ptx_producer_toolchain_files
ptx_producer_observation home_qualification_dependency_identity
home_qualification_identity_is_not_cross_environment_reproducibility
ptx_producer_open_audit ptx_program_identity_sha256
home_functional_lane_count small_lane_count bounded_real_lane_count exact_lane_count
behavioral_true_optix_lane_count token_only_lane_count fresh_parent_pid_count
operation_receipt_count successful_operation_event_count_by_variant
event_count_per_receipt all_tokens_admitted_in_preparation
fresh_private_cupy_cache_per_lane cache_policy cache_policy_sha256 cold_definition
cold_claim_excludes operating_system_page_cache_controlled_or_dropped
operating_system_page_cache_scope cuda_driver_jit_cache_controlled_or_isolated
optix_disk_cache_controlled_or_isolated
round_major_abba_is_uncontrolled_cache_mitigation_not_control
independent_simple_undirected_oracle_recomputed_from_raw_edges
independently_recounted_inputs legacy_execution_path_used
exact_source_and_native_preserved_before_first_lane
source_manifest_payloads_read_only_before_first_lane
source_manifest_fully_rehashed_after_functional_lanes
source_exact_set_before_first_lane
source_exact_set_and_all_tree_paths_read_only_after_lanes formal_worker_count
registered_performance_timing_count elapsed_value_count clock_sample_count
home_performance_observation_created home_performance_diagnostic_used
performance_or_compiler_fusion_claimed pod_used prebuilt_target_native_used
private_codex_dependency_used
formal_worker_environment_contract_sha256 home_locale_matches_formal_environment_contract
source_admission_policy_sha256
""".split())
UPLOAD_STAGING_RECEIPT_NAME = "UPLOAD_STAGING_OPEN_RECEIPT.json"
UPLOAD_STAGING_RECEIPT_SCHEMA = (
    "rtdl.goal5791.upload_staging_open_receipt.v1")
UPLOAD_STAGING_RECEIPT_STATUS = (
    "UPLOAD_STAGING_CREATED__TARGET_MATERIALIZATION_ROOT_REMAINS_ABSENT")
STAGED_UPLOAD_RELATIVE_PATHS = {
    "bundle": "GOAL5791_PRE_POD_BUNDLE.tar.gz",
    "data_bundle": "GOAL5791_DATA_BUNDLE.tar.gz",
    "wheelhouse": "GOAL5791_DEPENDENCY_WHEELHOUSE.tar.gz",
    "optix_headers": "GOAL5791_OPTIX_HEADERS.tar.gz",
    "owner_authority": "OWNER_TARGET_PREPARE_AUTHORITY.json",
    "target_prepare": "TARGET_PREPARE.py",
}
UPLOAD_STAGING_CLEANUP_DISPOSITION = (
    "REMOVE_UPLOAD_STAGING_ONLY_AFTER_TARGET_EVIDENCE_LOCAL_PRESERVATION")
AMBIENT_DEVICE_OR_CACHE_SELECTORS = frozenset({
    "CUDA_VISIBLE_DEVICES",
    "NVIDIA_VISIBLE_DEVICES",
    "NUMBA_DISABLE_CUDA",
    "NUMBA_ENABLE_CUDASIM",
    "NUMBA_FORCE_CUDA_CC",
    "NUMBA_CUDA_DEFAULT_PTX_CC",
    "NUMBA_CUDA_NVVM",
    "NUMBA_CUDA_LIBDEVICE",
    "CUPY_CACHE_DIR",
    "CUPY_ACCELERATORS",
    "CUDA_CACHE_PATH",
    "CUDA_CACHE_DISABLE",
    "OPTIX_CACHE_PATH",
    "OPTIX_CACHE_MAXSIZE",
    "OPTIX_CACHE_ENABLED",
})
SHARED_FREEZE_MEMBER = (
    "history/internal_docs/goal5789_contract_evidence_20260816/"
    "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json"
)
DATA_AUTHORITY_MEMBER = (
    "history/internal_docs/"
    "goal5791_frozen_triangle_data_and_oracle_authority_20260817.json"
)
EXPECTED_DATA_SHA256 = (
    "f186cd28a5ae767f968eaa1372cd66285934be430bceb77ff14c6cf94e33e6eb"
)
EXPECTED_WHEELHOUSE_SHA256 = (
    "d0c0f75365a78792cf0c2f548e0bdd144f0ad7175e0d8f83efcf335eb3b311f3"
)
EXPECTED_OPTIX_HEADERS_SHA256 = (
    "7fae86ce3dca2fbc2a47be075f02465cf6ee9d9eafd204234f2882fbdeebee54"
)
EXPECTED_TARGET_DEPENDENCY_IDENTITY = {
    "python": "3.12.3",
    "numba": "0.65.1",
    "numpy": "2.4.4",
    "llvmlite": "0.47.0",
    "cupy": "14.0.1",
    "cuda_runtime_int": 12090,
}
EXPECTED_TARGET_PRODUCER_DEPENDENCY_VERSIONS = {
    name: EXPECTED_TARGET_DEPENDENCY_IDENTITY[name]
    for name in ("python", "numba", "numpy", "cupy", "llvmlite")
}
EXPECTED_DATA = {
    "com_dblp": {
        "member": "DATA/triangle/com-dblp.edge",
        "sha256": "e9647564c1ca96589cc52314cabf5569ec80b9f5d697578a55d47fbe7aafca67",
        "bytes": 8_398_928,
        "expected_triangle_count": 2_224_385,
        "oracle_authority_sha256": (
            "2aba6effb60def2f6581f3f44fc1ba8d2e7a9fdab6a3337ac1564eea79869a79"),
    },
    "cit_patents": {
        "member": "DATA/triangle/cit-Patents.edge",
        "sha256": "c5b2c9203eeabb46414965755c33befdb1810e71cb51155eb940a68a6179d855",
        "bytes": 132_151_584,
        "expected_triangle_count": 7_515_023,
        "oracle_authority_sha256": (
            "0e50e235cb677da5964baba20cbe1d9b71463bd4e87d157eede72a98e56891b0"),
    },
    "soc_livejournal1": {
        "member": "DATA/triangle/soc-LiveJournal1.edge",
        "sha256": "80199ecebb7ebdf3b4861748e009d16b1c5f93c35eba837a7ce37f94ada35f83",
        "bytes": 551_950_184,
        "expected_triangle_count": 285_730_264,
        "oracle_authority_sha256": (
            "99e0dfbca7c22c47af124bb10600050ce3e489e7d3d712a27e34b804c259809c"),
    },
}
FORMAL_SOURCE_NAMES = (
    "scripts/goal5791_formal_contract.py",
    "scripts/goal5791_segment_descriptors.py",
    "scripts/goal5791_formal_worker.py",
    "scripts/goal5791_formal_controller.py",
    "scripts/goal5791_formal_evaluate.py",
    "scripts/goal5791_formal_independent_recount.py",
)
SOURCE_MANIFEST_KEYS = {
    "schema", "goal", "status", "base_source_archive_sha256",
    "base_source_manifest_sha256", "base_source_tree_sha256",
    "base_source_file_count_excluding_manifest", "old_source_manifest_removed",
    "product_delta_paths", "product_delta",
    "nonproduct_overlay_count_including_builder", "deep_blob_audit",
    "manifest_is_non_self_referential", "file_count_excluding_this_manifest",
    "source_tree_sha256", "home_or_target_execution_count",
    "formal_worker_count", "registered_performance_timing_count", "files",
}


class PrepareError(RuntimeError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _reject_home_performance_observations(
    value: object, *, label: str,
) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            folded = key.casefold()
            if key in _HOME_ZERO_COUNT_KEYS:
                if type(item) is not int or item != 0:
                    raise PrepareError(
                        f"Home observation count is not exact zero: "
                        f"{label}.{key}")
            elif key in _HOME_FALSE_OBSERVATION_KEYS:
                if item is not False:
                    raise PrepareError(
                        f"Home observation marker is not false: "
                        f"{label}.{key}")
            elif key in _HOME_TRUE_OPERATIONAL_CLOCK_KEYS:
                if item is not True:
                    raise PrepareError(
                        f"operational watchdog disclosure is not true: "
                        f"{label}.{key}")
            elif key in _SOURCE_OPERATIONAL_TIMEOUT_FIELDS:
                if type(item) is not int \
                        or item != _SOURCE_OPERATIONAL_TIMEOUT_FIELDS[key]:
                    raise PrepareError(
                        f"source operational timeout binding drifted: "
                        f"{label}.{key}")
            elif key == "overlay_sha256" \
                    and label == "SOURCE_BASE_AND_OVERLAY_AUTHORITY.json":
                if not isinstance(item, dict) or not item \
                        or any(
                            not isinstance(path, str) or not path
                            or not isinstance(digest, str) or len(digest) != 64
                            or any(ch not in "0123456789abcdef" for ch in digest)
                            for path, digest in item.items()
                        ):
                    raise PrepareError(
                        "source overlay digest map shape drifted")
                continue
            elif key == "timer_contract_sha256":
                if item != _digest(_HOME_TIMER_CONTRACT):
                    raise PrepareError(
                        f"Home zero-observation contract digest drifted: "
                        f"{label}.{key}")
            elif any(token in folded
                     for token in _HOME_FORBIDDEN_OBSERVATION_KEY_TOKENS) \
                    or folded.endswith(
                        _HOME_FORBIDDEN_OBSERVATION_KEY_SUFFIXES):
                raise PrepareError(
                    f"Home performance/clock field is forbidden: "
                    f"{label}.{key}")
            _reject_home_performance_observations(
                item, label=f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_home_performance_observations(
                item, label=f"{label}[{index}]")


def _require_exact_bundle_member_set(payloads: dict[str, bytes]) -> None:
    actual = set(payloads)
    if actual != EXPECTED_BUNDLE_OUTER_MEMBERS:
        raise PrepareError(
            "Goal5791 bundle outer membership is not the frozen exact set: "
            f"missing={sorted(EXPECTED_BUNDLE_OUTER_MEMBERS - actual)!r}, "
            f"extra={sorted(actual - EXPECTED_BUNDLE_OUTER_MEMBERS)!r}"
        )


def _strict_json(path: Path) -> dict[str, object]:
    seen: list[str] = []

    def pairs(rows):
        value = {}
        for key, item in rows:
            if key in value:
                raise PrepareError(f"duplicate JSON key in {path}: {key}")
            value[key] = item
        seen.append(str(path))
        return value

    try:
        result = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                PrepareError(f"non-finite JSON constant: {token}")),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrepareError(f"cannot read strict JSON: {path}") from exc
    if not isinstance(result, dict):
        raise PrepareError(f"expected JSON object: {path}")
    return result


def _strict_json_bytes(data: bytes, label: str) -> dict[str, object]:
    def pairs(rows):
        value = {}
        for key, item in rows:
            if key in value:
                raise PrepareError(f"duplicate JSON key in {label}: {key}")
            value[key] = item
        return value

    try:
        result = json.loads(
            data.decode("utf-8"), object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                PrepareError(f"non-finite JSON constant in {label}: {token}")),
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PrepareError(f"cannot read strict JSON bytes: {label}") from exc
    if not isinstance(result, dict):
        raise PrepareError(f"expected JSON object: {label}")
    return result


def _write_json_create_only(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def _normalized(name: str) -> str:
    pure = PurePosixPath(name)
    parts = tuple(part for part in pure.parts if part not in ("", "."))
    normalized = "/".join(parts)
    if not parts or pure.is_absolute() or ".." in parts:
        raise PrepareError(f"unsafe archive member: {name!r}")
    return normalized


def _read_regular_archive_bytes(
    data: bytes, *, label: str,
) -> dict[str, bytes]:
    values: dict[str, bytes] = {}
    folded: set[str] = set()
    try:
        archive_context = tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")
    except (tarfile.TarError, OSError) as exc:
        raise PrepareError(f"cannot open archive: {label}") from exc
    with archive_context as archive:
        for member in archive.getmembers():
            if member.isdir():
                # GNU tar commonly records the archive root as `.`.  It is a
                # directory marker, not a payload path.  Admit only that exact
                # root spelling without weakening normalization for files or
                # non-root directories.
                if member.name in (".", "./"):
                    continue
                _normalized(member.name)
                continue
            name = _normalized(member.name)
            if name in values or name.casefold() in folded:
                raise PrepareError(f"duplicate/case-colliding archive member: {name}")
            if not member.isfile() or member.issym() or member.islnk():
                raise PrepareError(f"unsupported archive member: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise PrepareError(f"unreadable archive member: {name}")
            values[name] = stream.read()
            folded.add(name.casefold())
    return values


def _read_regular_archive(path: Path) -> dict[str, bytes]:
    return _read_regular_archive_bytes(path.read_bytes(), label=str(path))


def _extract_payloads(payloads: dict[str, bytes], destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    destination.mkdir(parents=True)
    for name, data in sorted(payloads.items()):
        target = destination.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def _extract_selected(
    archive_path: Path, selected: set[str], destination: Path,
) -> dict[str, Path]:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    destination.mkdir(parents=True)
    result: dict[str, Path] = {}
    seen: set[str] = set()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            name = _normalized(member.name)
            if name not in selected:
                continue
            if name in seen or not member.isfile() or member.issym() or member.islnk():
                raise PrepareError(f"selected archive member invalid: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise PrepareError(f"selected archive member unreadable: {name}")
            target = destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(stream.read())
            result[name] = target
            seen.add(name)
    if set(result) != selected:
        raise PrepareError(f"selected archive membership drifted: {selected-set(result)}")
    return result


def _deterministic_archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _run(
    command: list[str], *, cwd: Path, env: dict[str, str], log: Path,
    timeout: int,
) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, text=True, encoding="utf-8",
        errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False, timeout=timeout,
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode:
        raise PrepareError(f"command failed: {command!r}; see {log}")
    return completed.stdout


def _load_bundle_auditor(source: bytes) -> types.ModuleType:
    if _sha_bytes(source) != TRUSTED_INDEPENDENT_PORTABLE_AUDITOR_SHA256:
        raise PrepareError(
            "Goal5791 bundle independent auditor bytes are not trusted")
    module = types.ModuleType("goal5791_frozen_independent_portable_audit")
    module.__file__ = "/goal5791/HARNESS/INDEPENDENT_PORTABLE_AUDIT.py"
    module.__package__ = ""
    try:
        exec(compile(source, module.__file__, "exec"), module.__dict__)
    except Exception as exc:
        raise PrepareError(
            "Goal5791 frozen independent bundle auditor failed to load") from exc
    return module


def _validate_source_cpu_gate_binding(
    *, source_receipt: dict[str, object], source_payloads: dict[str, bytes],
    auditor: types.ModuleType,
) -> None:
    try:
        auditor._validate_source_receipt_governance(
            source_receipt,
            builder_bytes=source_payloads[
                "scripts/goal5791_build_portable_source.py"],
            helper_bytes=source_payloads["scripts/goal5791_cpu_test_gate.py"],
        )
    except Exception as exc:
        raise PrepareError(
            "Goal5791 source CPU gate contract is not independently valid") \
            from exc
    if source_receipt.get("schema") \
                != "rtdl.goal5791.portable_source_build_receipt.v26" \
            or type(source_receipt.get("cpu_test_timeout_seconds")) is not int \
            or source_receipt.get("cpu_test_timeout_seconds") \
                != SOURCE_CPU_TEST_TIMEOUT_SECONDS:
        raise PrepareError("Goal5791 source CPU gate binding drifted")
    empty_outcomes = {
        "failures": [], "errors": [], "skipped": [],
        "expectedFailures": [], "unexpectedSuccesses": [],
    }
    for field, scope in (
        ("workspace_cpu_test_gate_result", "workspace"),
        ("clean_cpu_test_gate_result", "clean"),
    ):
        gate = source_receipt.get(field)
        if not isinstance(gate, dict) \
                or gate.get("schema") \
                    != "rtdl.goal5791.cpu_test_gate_result.v2" \
                or gate.get("scope") != scope \
                or gate.get("outcome_test_ids") != empty_outcomes \
                or gate.get("outcome_test_ids_sha256") \
                    != _digest(empty_outcomes) \
                or gate.get("failure_test_ids") != [] \
                or gate.get("error_test_ids") != [] \
                or gate.get("failure_exception_summaries") != [] \
                or gate.get("error_exception_summaries") != [] \
                or gate.get("success") is not True:
            raise PrepareError(
                "Goal5791 successful source CPU outcome evidence drifted")


def _validate_bundle(path: Path) -> tuple[dict[str, bytes], dict[str, object]]:
    outer = _read_regular_archive(path)
    _require_exact_bundle_member_set(outer)
    manifest_bytes = outer.get("BUNDLE_MANIFEST.json")
    if manifest_bytes is None:
        raise PrepareError("Goal5791 bundle manifest is absent")
    manifest = _strict_json_bytes(manifest_bytes, "BUNDLE_MANIFEST.json")
    _reject_home_performance_observations(
        manifest, label="BUNDLE_MANIFEST.json")
    if not isinstance(manifest, dict) or (
        manifest.get("schema") != BUNDLE_SCHEMA
        or manifest.get("goal") != 5791
        or manifest.get("formal_worker_count_executed") != 0
        or manifest.get("registered_performance_timing_count") != 0
        or manifest.get("elapsed_value_count") != 0
        or manifest.get("clock_sample_count") != 0
        or manifest.get("home_performance_observation_created") is not False
        or manifest.get("home_performance_diagnostic_used") is not False
        or manifest.get("contains_owner_prepare_authority") is not False
        or manifest.get("contains_owner_formal_authority") is not False
        or manifest.get("contains_real_scale_data") is not False
        or manifest.get("contains_wheelhouse") is not False
        or manifest.get("contains_optix_headers") is not False
        or manifest.get("contains_prebuilt_target_native") is not False
        or manifest.get("source_is_only_nested_container") is not True
    ):
        raise PrepareError("Goal5791 bundle scope drifted")
    rows = manifest.get("payloads")
    if not isinstance(rows, list):
        raise PrepareError("Goal5791 bundle payload manifest is absent")
    expected = {
        str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
        for row in rows
    }
    if len(expected) != len(rows) or set(outer) != set(expected) | {
        "BUNDLE_MANIFEST.json"
    }:
        raise PrepareError("Goal5791 bundle membership drifted")
    for name, (size, sha) in expected.items():
        data = outer[name]
        if len(data) != size or _sha_bytes(data) != sha:
            raise PrepareError(f"Goal5791 bundle payload drifted: {name}")
    if _sha_bytes(outer["SOURCE.tar.gz"]) \
            != manifest.get("source_archive_sha256"):
        raise PrepareError("Goal5791 bundle/source cross-binding drifted")
    source_payloads = _read_regular_archive_bytes(
        outer["SOURCE.tar.gz"], label="SOURCE.tar.gz")
    for outer_name, source_name in OUTER_HARNESS_TO_SOURCE.items():
        if outer.get(outer_name) != source_payloads.get(source_name):
            raise PrepareError(
                f"Goal5791 outer/source harness bytes drifted: {outer_name}")
    for outer_name, source_name in OUTER_TO_SOURCE_AUTHORITY_MEMBERS.items():
        if outer.get(outer_name) != source_payloads.get(source_name):
            raise PrepareError(
                f"Goal5791 outer/source authority bytes drifted: {outer_name}")
    auditor = _load_bundle_auditor(
        outer["HARNESS/INDEPENDENT_PORTABLE_AUDIT.py"])
    try:
        source_summary = auditor.audit_source(
            outer["SOURCE.tar.gz"], perform_clean_extraction=False)
        auditor._validate_bundle_manifest(
            manifest=manifest, payloads=outer,
            source_payloads=source_payloads, source_summary=source_summary,
        )
        auditor._validate_bundle_source_chain(
            payloads=outer, bundle_manifest=manifest,
            source_data=outer["SOURCE.tar.gz"],
            source_payloads=source_payloads, source_summary=source_summary,
        )
    except Exception as exc:
        raise PrepareError(
            "Goal5791 trusted source/manifest admission failed") from exc
    executing = Path(__file__).resolve().read_bytes()
    if executing != outer.get("HARNESS/TARGET_PREPARE.py"):
        raise PrepareError(
            "executing Goal5791 target prepare differs from frozen bundle")
    home = _strict_json_bytes(
        outer.get(HOME_FUNCTIONAL_CLOSURE_MEMBER, b""),
        HOME_FUNCTIONAL_CLOSURE_MEMBER,
    )
    if set(home) != HOME_FUNCTIONAL_CLOSURE_KEYS or (
        home.get("schema")
            != "rtdl.goal5791.home_token_functional_closure.v1"
        or home.get("status")
            != "PASS__10_OF_10_TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX"
        or home.get("execution_source_archive_sha256")
            != manifest.get("source_archive_sha256")
        or home.get("execution_source_tree_sha256")
            != manifest.get("source_tree_sha256")
        or home.get("source_manifest_sha256")
            != manifest.get("source_manifest_sha256")
        or home.get("exact_lane_count") != 10
        or home.get("behavioral_true_optix_lane_count") != 10
        or home.get("token_only_lane_count") != 10
        or home.get("formal_worker_count") != 0
        or home.get("registered_performance_timing_count") != 0
        or home.get("elapsed_value_count") != 0
        or home.get("clock_sample_count") != 0
        or home.get("home_performance_observation_created") is not False
        or home.get("home_performance_diagnostic_used") is not False
        or home.get("pod_used") is not False
        or _sha_bytes(outer[HOME_FUNCTIONAL_CLOSURE_MEMBER])
            != manifest.get("home_functional_closure_file_sha256")
    ):
        raise PrepareError("Goal5791 frozen Home functional closure drifted")
    _reject_home_performance_observations(
        home, label=HOME_FUNCTIONAL_CLOSURE_MEMBER)
    try:
        auditor._validate_bundle_home_chain(
            payloads=outer, bundle_manifest=manifest,
            home=home, source_summary=source_summary,
        )
    except Exception as exc:
        raise PrepareError(
            "Goal5791 trusted internal Home small-chain admission failed") from exc

    semantic = _strict_json_bytes(
        outer.get(SEMANTIC_SUCCESSOR_MEMBER, b""), SEMANTIC_SUCCESSOR_MEMBER)
    semantic_unsigned = dict(semantic)
    semantic_claimed = semantic_unsigned.pop("authority_sha256", None)
    semantic_source = semantic.get("source")
    semantic_home = semantic.get("home_functional_closure")
    semantic_authorization = semantic.get("authorization")
    if (
        semantic.get("schema")
            != "rtdl.goal5791.semantic_physical_variant_successor_authority.v1"
        or semantic.get("status")
            != "FROZEN_PRE_POD_SUCCESSOR_IDENTITY__NOT_EXECUTION_AUTHORITY"
        or semantic_claimed != _digest(semantic_unsigned)
        or not isinstance(semantic_source, dict)
        or semantic_source.get("archive_sha256")
            != manifest.get("source_archive_sha256")
        or semantic_source.get("tree_sha256")
            != manifest.get("source_tree_sha256")
        or semantic_source.get("manifest_sha256")
            != manifest.get("source_manifest_sha256")
        or not isinstance(semantic_home, dict)
        or semantic_home.get("home_evidence_sha256")
            != home.get("home_evidence_sha256")
        or semantic_home.get("elapsed_value_count") != 0
        or semantic_home.get("clock_sample_count") != 0
        or semantic_home.get("home_performance_observation_created") is not False
        or semantic_home.get("home_performance_diagnostic_used") is not False
        or not isinstance(semantic_authorization, dict)
        or any(value is not False for value in semantic_authorization.values())
    ):
        raise PrepareError("Goal5791 semantic successor authority drifted")
    _reject_home_performance_observations(
        semantic_home,
        label=f"{SEMANTIC_SUCCESSOR_MEMBER}.home_functional_closure",
    )
    try:
        auditor._validate_semantic_authority(
            semantic=semantic, source_summary=source_summary,
            source_payloads=source_payloads, home=home,
        )
        if outer["README.md"] != auditor.canonical_readme(
            source_sha256=str(source_summary["archive_sha256"]),
            source_tree_sha256=str(source_summary["source_tree_sha256"]),
        ):
            raise PrepareError(
                "Goal5791 README trusted reconstruction drifted")
    except PrepareError:
        raise
    except Exception as exc:
        raise PrepareError(
            "Goal5791 trusted semantic/README admission failed") from exc
    source_receipt = _strict_json_bytes(
        outer["SOURCE_BASE_AND_OVERLAY_AUTHORITY.json"],
        "SOURCE_BASE_AND_OVERLAY_AUTHORITY.json",
    )
    _reject_home_performance_observations(
        source_receipt, label="SOURCE_BASE_AND_OVERLAY_AUTHORITY.json")
    _validate_source_cpu_gate_binding(
        source_receipt=source_receipt, source_payloads=source_payloads,
        auditor=auditor)
    uploads = manifest.get("external_uploads")
    if uploads != {
        "data_bundle_sha256": EXPECTED_DATA_SHA256,
        "wheelhouse_sha256": EXPECTED_WHEELHOUSE_SHA256,
        "optix_headers_sha256": EXPECTED_OPTIX_HEADERS_SHA256,
    }:
        raise PrepareError("Goal5791 external upload manifest drifted")
    return outer, manifest


def _validate_source_payloads(
    payloads: dict[str, bytes], source: Path,
) -> dict[str, object]:
    """Rehash the non-self manifest against every extracted source payload."""

    manifest_path = source / SOURCE_MANIFEST_MEMBER
    value = _strict_json(manifest_path)
    if set(value) != SOURCE_MANIFEST_KEYS:
        raise PrepareError("Goal5791 source manifest fields drifted")
    rows = value.get("files")
    if not isinstance(rows, list):
        raise PrepareError("Goal5791 source manifest rows are absent")
    expected: dict[str, tuple[int, str]] = {}
    observed_order: list[str] = []
    folded: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {
            "path", "size_bytes", "sha256",
        }:
            raise PrepareError(f"Goal5791 source manifest row drifted: {index}")
        name = _normalized(str(row["path"]))
        if name.casefold() in folded or name == SOURCE_MANIFEST_MEMBER:
            raise PrepareError("Goal5791 source manifest path collision/self-row")
        size = row["size_bytes"]
        sha = row["sha256"]
        if type(size) is not int or size < 0 \
                or not isinstance(sha, str) \
                or re.fullmatch(r"[0-9a-f]{64}", sha) is None:
            raise PrepareError("Goal5791 source manifest size/hash drifted")
        expected[name] = (size, sha)
        observed_order.append(name)
        folded.add(name.casefold())
    actual_names = set(payloads) - {SOURCE_MANIFEST_MEMBER}
    if len(expected) != len(rows) or set(expected) != actual_names \
            or observed_order != sorted(observed_order):
        raise PrepareError("Goal5791 source manifest membership/order drifted")
    for name, (size, sha) in expected.items():
        data = payloads[name]
        extracted = source.joinpath(*PurePosixPath(name).parts)
        if len(data) != size or _sha_bytes(data) != sha \
                or extracted.stat().st_size != size or _sha(extracted) != sha:
            raise PrepareError(f"Goal5791 source payload drifted: {name}")
    canonical_rows = [
        {"path": name, "size_bytes": len(payloads[name]),
         "sha256": _sha_bytes(payloads[name])}
        for name in sorted(actual_names)
    ]
    if (
        value.get("schema") != "rtdl.goal5791.portable_source_manifest.v1"
        or value.get("goal") != 5791
        or value.get("status")
            != "PORTABLE_SOURCE_FROZEN__HOME_REQUALIFICATION_REQUIRED"
        or value.get("manifest_is_non_self_referential") is not True
        or value.get("file_count_excluding_this_manifest") != len(rows)
        or value.get("source_tree_sha256") != _digest(canonical_rows)
        or value.get("home_or_target_execution_count") != 0
        or value.get("formal_worker_count") != 0
        or value.get("registered_performance_timing_count") != 0
    ):
        raise PrepareError("Goal5791 source manifest identity/scope drifted")
    return value


def _audit_exact_source_set(
    source: Path, manifest: dict[str, object], *,
    manifest_file_sha256: str, require_read_only: bool,
) -> dict[str, object]:
    """Require only manifest files/parents and reject links or special nodes."""

    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise PrepareError("Goal5791 source rows disappeared")
    expected_files = {
        str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
        for row in rows
    }
    expected_files[SOURCE_MANIFEST_MEMBER] = (
        (source / SOURCE_MANIFEST_MEMBER).stat().st_size,
        manifest_file_sha256,
    )
    expected_dirs: set[str] = set()
    for name in expected_files:
        parent = PurePosixPath(name).parent
        while str(parent) not in ("", "."):
            expected_dirs.add(parent.as_posix())
            parent = parent.parent
    observed_files: dict[str, tuple[int, str]] = {}
    observed_dirs: set[str] = set()
    all_paths = [source, *source.rglob("*")]
    for path in all_paths:
        relative = "." if path == source else path.relative_to(source).as_posix()
        lstat = path.lstat()
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        if path.is_symlink() or (
            reparse_flag
            and getattr(lstat, "st_file_attributes", 0) & reparse_flag
        ):
            raise PrepareError(
                f"Goal5791 source link/reparse remains: {relative}")
        mode = lstat.st_mode
        if require_read_only and mode & 0o222:
            raise PrepareError(f"Goal5791 source path is writable: {relative}")
        if path.is_dir():
            if path != source:
                observed_dirs.add(relative)
            continue
        if not path.is_file():
            raise PrepareError(f"Goal5791 source special node remains: {relative}")
        observed_files[relative] = (path.stat().st_size, _sha(path))
    if observed_dirs != expected_dirs:
        raise PrepareError(
            "Goal5791 source directory set drifted: "
            + repr(sorted(observed_dirs ^ expected_dirs)[:16]))
    if observed_files != expected_files:
        raise PrepareError(
            "Goal5791 source regular-file set/bytes drifted: "
            + repr(sorted(set(observed_files) ^ set(expected_files))[:16]))
    return {
        "regular_file_count": len(observed_files),
        "directory_count_excluding_root": len(observed_dirs),
        "regular_file_set_exact": True,
        "directory_set_exact": True,
        "extra_regular_file_count": 0,
        "extra_directory_count": 0,
        "link_count": 0,
        "reparse_point_count": 0,
        "special_file_count": 0,
        "all_tree_paths_without_write_bits": require_read_only,
    }


def _validate_owner_prebundle(
    path: Path, *, bundle_sha: str,
    materialization_root: Path, upload_staging_root: Path,
    pod_endpoint: dict[str, object],
) -> dict[str, object]:
    value = _strict_json(path)
    expected_keys = {
        "schema", "goal", "status", "bundle_sha256",
        "source_archive_sha256", "data_bundle_sha256",
        "wheelhouse_sha256", "optix_headers_sha256",
        "pretarget_preexecution_authority_file_sha256",
        "formal_contract_sha256", "schedule_sha256",
        "runtime_budget_authority_file_sha256", "token_amendment_sha256",
        "joint_delivery_audit",
        "required_target", "first_entry_stdin_bootstrap", "execution_target",
        "resource_confirmation", "paid_transaction_justification",
        "owner_authorization_nonce",
        "authorization", "authority_sha256",
    }
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256", None)
    bootstrap = value.get("first_entry_stdin_bootstrap")
    target_value = value.get("execution_target")
    _validate_joint_delivery_audit_authority(
        value.get("joint_delivery_audit"), bundle_sha=bundle_sha)
    if set(value) != expected_keys \
            or _digest(unsigned) != claimed \
            or value.get("schema") != OWNER_SCHEMA \
            or value.get("goal") != 5791 \
            or value.get("status") != OWNER_STATUS \
            or value.get("bundle_sha256") != bundle_sha \
            or value.get("data_bundle_sha256") != EXPECTED_DATA_SHA256 \
            or value.get("wheelhouse_sha256") != EXPECTED_WHEELHOUSE_SHA256 \
            or value.get("optix_headers_sha256") \
                != EXPECTED_OPTIX_HEADERS_SHA256 \
            or not isinstance(bootstrap, dict) \
            or set(bootstrap) != {
                "source", "source_sha256",
                "actual_source_rehashed_from_proc_cmdline_before_helper_exec",
                "honest_owner_exact_ssh_command_is_operational_tcb",
            } \
            or not isinstance(bootstrap.get("source"), str) \
            or _sha_bytes(bootstrap["source"].encode("utf-8")) \
                != bootstrap.get("source_sha256") \
            or bootstrap.get(
                "actual_source_rehashed_from_proc_cmdline_before_helper_exec") \
                is not True \
            or bootstrap.get(
                "honest_owner_exact_ssh_command_is_operational_tcb") is not True \
            or not isinstance(target_value, dict) \
            or target_value.get("target_materialization_root") \
                != str(materialization_root) \
            or target_value.get("upload_staging_root") \
                != str(upload_staging_root) \
            or target_value.get("pod_endpoint") != pod_endpoint \
            or target_value.get(
                "upload_staging_and_target_materialization_roots_required_absent_at_first_target_entry") \
                is not True \
            or target_value.get("preexisting_or_shared_roots_allowed") is not False \
            or target_value.get("staged_upload_relative_paths") \
                != STAGED_UPLOAD_RELATIVE_PATHS \
            or target_value.get("upload_staging_cleanup_disposition") \
                != UPLOAD_STAGING_CLEANUP_DISPOSITION \
            or value.get("authorization") != {
                "authorizes_pod_connection": True,
                "authorizes_create_only_upload_staging_root": True,
                "authorizes_exact_staged_uploads": True,
                "authorizes_create_only_target_materialization_root": True,
                "authorizes_exact_target_prepare": True,
                "authorizes_formal_worker_zero": False,
                "authorizes_registered_timing": False,
                "authorizes_owner_formal_authority_creation": False,
                "authorizes_any_other_goal_target_or_matrix": False,
            } \
            or value.get("paid_transaction_justification") \
                != STAGE_A_THIRD_POD_JUSTIFICATION:
        raise PermissionError(
            "Goal5791 owner pre-bundle authority admission drifted")
    return value


def _validate_joint_delivery_audit_authority(
    value: object, *, bundle_sha: str,
) -> dict[str, object]:
    expected_keys = {
        "joint_bundle_audit_receipt_file_sha256",
        "joint_bundle_audit_receipt_sha256",
        "independent_portable_auditor_sha256", "bundle_sha256",
        "bundle_twin_sha256", "bundle_twin_byte_identical",
        "home_evidence_sha256", "home_evidence_twin_sha256",
        "home_evidence_twin_byte_identical", "strict_joint_audit_passed",
        "home_independent_raw_recount_reexecuted_and_byte_identical",
    }
    if not isinstance(value, dict) or set(value) != expected_keys \
            or value.get("bundle_sha256") != bundle_sha \
            or value.get("bundle_twin_sha256") != bundle_sha \
            or value.get("independent_portable_auditor_sha256") \
                != TRUSTED_INDEPENDENT_PORTABLE_AUDITOR_SHA256 \
            or any(
                re.fullmatch(r"[0-9a-f]{64}", str(value.get(name))) is None
                for name in (
                    "joint_bundle_audit_receipt_file_sha256",
                    "joint_bundle_audit_receipt_sha256",
                    "home_evidence_sha256", "home_evidence_twin_sha256",
                )
            ) \
            or value.get("home_evidence_sha256") \
                != value.get("home_evidence_twin_sha256") \
            or any(value.get(name) is not True for name in (
                "bundle_twin_byte_identical",
                "home_evidence_twin_byte_identical",
                "strict_joint_audit_passed",
                "home_independent_raw_recount_reexecuted_and_byte_identical",
            )):
        raise PermissionError(
            "Goal5791 strict joint delivery audit authority drifted")
    return value


def _crossbind_owner_joint_home_chain(
    owner: dict[str, object], *, outer: dict[str, bytes],
    manifest: dict[str, object],
) -> None:
    """Bind the owner-reviewed external pair to the bundle's small chain."""

    joint = owner["joint_delivery_audit"]
    home = _strict_json_bytes(
        outer[HOME_FUNCTIONAL_CLOSURE_MEMBER],
        HOME_FUNCTIONAL_CLOSURE_MEMBER,
    )
    evidence_sha = joint["home_evidence_sha256"]
    twin_sha = joint["home_evidence_twin_sha256"]
    if manifest.get("home_evidence_sha256") != evidence_sha \
            or manifest.get("home_evidence_twin_sha256") != twin_sha \
            or home.get("home_evidence_sha256") != evidence_sha \
            or home.get("home_evidence_twin_sha256") != twin_sha \
            or home.get("home_evidence_twin_byte_identical") is not True:
        raise PermissionError(
            "Goal5791 owner joint Home pair/bundle small-chain binding drifted")


def _owner_pinned_bundle_admission(
    *, authority: Path, bundle: Path, materialization_root: Path,
    upload_staging_root: Path, pod_endpoint: dict[str, object],
) -> tuple[dict[str, bytes], dict[str, object]]:
    """Admit the owner-pinned raw bundle before parsing or executing it."""

    owner = _validate_owner_prebundle(
        authority, bundle_sha=_sha(bundle),
        materialization_root=materialization_root,
        upload_staging_root=upload_staging_root,
        pod_endpoint=pod_endpoint,
    )
    outer, manifest = _validate_bundle(bundle)
    _crossbind_owner_joint_home_chain(
        owner, outer=outer, manifest=manifest)
    return outer, manifest


def _validate_owner(
    path: Path, *, bundle_sha: str, source_sha: str,
    materialization_root: Path | str,
    upload_staging_root: Path | str,
    gpu: dict[str, str], base_python_sha256: str, base_python_version: str,
    base_python_path: str,
    pod_endpoint: dict[str, object],
) -> dict[str, object]:
    value = _strict_json(path)
    expected_keys = {
        "schema", "goal", "status", "bundle_sha256",
        "source_archive_sha256", "data_bundle_sha256",
        "wheelhouse_sha256", "optix_headers_sha256",
        "pretarget_preexecution_authority_file_sha256",
        "formal_contract_sha256", "schedule_sha256",
        "runtime_budget_authority_file_sha256", "token_amendment_sha256",
        "joint_delivery_audit",
        "required_target", "first_entry_stdin_bootstrap", "execution_target",
        "resource_confirmation", "paid_transaction_justification",
        "owner_authorization_nonce", "authorization", "authority_sha256",
    }
    if set(value) != expected_keys:
        raise PermissionError("Goal5791 owner prepare authority fields drifted")
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256")
    if _digest(unsigned) != claimed or value["schema"] != OWNER_SCHEMA \
            or value["goal"] != 5791 or value["status"] != OWNER_STATUS:
        raise PermissionError("Goal5791 owner prepare authority seal/header drifted")
    if value["paid_transaction_justification"] \
            != STAGE_A_THIRD_POD_JUSTIFICATION:
        raise PermissionError(
            "Goal5791 third paid-transaction justification drifted")
    if (
        value["bundle_sha256"] != bundle_sha
        or value["source_archive_sha256"] != source_sha
        or value["data_bundle_sha256"] != EXPECTED_DATA_SHA256
        or value["wheelhouse_sha256"] != EXPECTED_WHEELHOUSE_SHA256
        or value["optix_headers_sha256"] != EXPECTED_OPTIX_HEADERS_SHA256
    ):
        raise PermissionError("Goal5791 owner prepare payload identity drifted")
    _validate_joint_delivery_audit_authority(
        value["joint_delivery_audit"], bundle_sha=bundle_sha)
    required = value["required_target"]
    if not isinstance(required, dict) or set(required) != {
        "gpu_name", "gpu_uuid", "driver_version", "compute_capability",
        "cuda_toolkit_version", "optix_sdk_version",
        "base_python_executable_path", "base_python_executable_sha256",
        "base_python_version",
    } or required != {
        "gpu_name": gpu["gpu_name"],
        "gpu_uuid": gpu["gpu_uuid"],
        "driver_version": gpu["driver_version"],
        "compute_capability": "8.9",
        "cuda_toolkit_version": "12.8",
        "optix_sdk_version": "9.0.0",
        "base_python_executable_path": base_python_path,
        "base_python_executable_sha256": base_python_sha256,
        "base_python_version": base_python_version,
    }:
        raise PermissionError("Goal5791 owner target identity drifted")
    bootstrap = value["first_entry_stdin_bootstrap"]
    if not isinstance(bootstrap, dict) or set(bootstrap) != {
        "source", "source_sha256",
        "actual_source_rehashed_from_proc_cmdline_before_helper_exec",
        "honest_owner_exact_ssh_command_is_operational_tcb",
    } or not isinstance(bootstrap["source"], str) \
            or _sha_bytes(bootstrap["source"].encode("utf-8")) \
                != bootstrap["source_sha256"] \
            or bootstrap[
                "actual_source_rehashed_from_proc_cmdline_before_helper_exec"
            ] is not True \
            or bootstrap[
                "honest_owner_exact_ssh_command_is_operational_tcb"
            ] is not True:
        raise PermissionError("Goal5791 first-entry bootstrap pin drifted")
    target = value["execution_target"]
    # A local CPU-only authority generator passes the POSIX spelling as a
    # string.  Converting it to a host ``Path`` on Windows would silently
    # rewrite separators and, worse, tempt the generator to treat local
    # filesystem state as a remote observation.  Target execution passes its
    # already-resolved POSIX Path and performs the live absence check itself.
    expected_materialization_root = (
        materialization_root if isinstance(materialization_root, str)
        else str(materialization_root)
    )
    expected_staging_root = (
        upload_staging_root if isinstance(upload_staging_root, str)
        else str(upload_staging_root)
    )
    if not isinstance(target, dict) or set(target) != {
        "target_materialization_root",
        "upload_staging_root",
        "upload_staging_and_target_materialization_roots_required_absent_at_first_target_entry",
        "preexisting_or_shared_roots_allowed", "pod_endpoint",
        "staged_upload_relative_paths",
        "upload_staging_cleanup_disposition",
    } or target != {
        "target_materialization_root": expected_materialization_root,
        "upload_staging_root": expected_staging_root,
        "upload_staging_and_target_materialization_roots_required_absent_at_first_target_entry": True,
        "preexisting_or_shared_roots_allowed": False,
        "pod_endpoint": pod_endpoint,
        "staged_upload_relative_paths": STAGED_UPLOAD_RELATIVE_PATHS,
        "upload_staging_cleanup_disposition": (
            UPLOAD_STAGING_CLEANUP_DISPOSITION),
    }:
        raise PermissionError("Goal5791 create-only root authority drifted")
    resource = value["resource_confirmation"]
    if not isinstance(resource, dict) or set(resource) != {
        "owner_confirmed_prepare_window_hours", "confirmed_free_disk_bytes",
        "confirmed_before_target_materialization_root_creation",
    } or isinstance(resource["owner_confirmed_prepare_window_hours"], bool) \
            or not isinstance(resource["owner_confirmed_prepare_window_hours"],
                              (int, float)) \
            or not math.isfinite(float(resource[
                "owner_confirmed_prepare_window_hours"])) \
            or float(resource["owner_confirmed_prepare_window_hours"]) < 1.0 \
            or type(resource["confirmed_free_disk_bytes"]) is not int \
            or resource["confirmed_free_disk_bytes"] < 20_000_000_000 \
            or resource[
                "confirmed_before_target_materialization_root_creation"
            ] is not True:
        raise PermissionError("Goal5791 prepare resource authority is insufficient")
    if not re.fullmatch(r"[0-9a-f]{64}", str(value[
            "owner_authorization_nonce"])):
        raise PermissionError("Goal5791 owner prepare nonce is invalid")
    if value["authorization"] != {
        "authorizes_pod_connection": True,
        "authorizes_create_only_upload_staging_root": True,
        "authorizes_exact_staged_uploads": True,
        "authorizes_create_only_target_materialization_root": True,
        "authorizes_exact_target_prepare": True,
        "authorizes_formal_worker_zero": False,
        "authorizes_registered_timing": False,
        "authorizes_owner_formal_authority_creation": False,
        "authorizes_any_other_goal_target_or_matrix": False,
    }:
        raise PermissionError("Goal5791 owner prepare authorization drifted")
    return value


def _validate_upload_staging(
    *, staging_root: Path, materialization_root: Path,
    staged_paths: dict[str, Path], owner_authority_sha256: str,
    staging_helper_sha256: str, staging_helper_size_bytes: int,
    first_entry_stdin_bootstrap: dict[str, object],
    required_target: dict[str, object], pod_endpoint: dict[str, object],
) -> dict[str, object]:
    if staging_root == materialization_root \
            or staging_root in materialization_root.parents \
            or materialization_root in staging_root.parents:
        raise PrepareError("Goal5791 staging and materialization roots overlap")
    if not staging_root.is_dir() or staging_root.is_symlink():
        raise PrepareError("Goal5791 upload staging root is not a real directory")
    if set(staged_paths) != set(STAGED_UPLOAD_RELATIVE_PATHS):
        raise PrepareError("Goal5791 staged input labels drifted")
    expected_paths = {
        label: staging_root / relative
        for label, relative in STAGED_UPLOAD_RELATIVE_PATHS.items()
    }
    if any(staged_paths[label] != expected_paths[label]
           for label in expected_paths):
        raise PrepareError("Goal5791 staged input resolved paths drifted")
    expected_names = set(STAGED_UPLOAD_RELATIVE_PATHS.values()) | {
        UPLOAD_STAGING_RECEIPT_NAME}
    actual_names: set[str] = set()
    folded_names: set[str] = set()
    with os.scandir(staging_root) as entries:
        for entry in entries:
            folded = entry.name.casefold()
            if folded in folded_names:
                raise PrepareError("Goal5791 case-folding staging collision")
            actual_names.add(entry.name)
            folded_names.add(folded)
            info = entry.stat(follow_symlinks=False)
            if entry.is_symlink() or not stat.S_ISREG(info.st_mode):
                raise PrepareError(
                    "Goal5791 upload staging contains non-regular path")
            if info.st_mode & 0o222:
                raise PrepareError("Goal5791 staged payload remains writable")
    if actual_names != expected_names:
        raise PrepareError("Goal5791 upload staging exact file set drifted")
    receipt_path = staging_root / UPLOAD_STAGING_RECEIPT_NAME
    receipt = _strict_json(receipt_path)
    expected_receipt_keys = {
        "schema", "goal", "status",
        "owner_target_prepare_authority_file_sha256",
        "bootstrap_source_sha256",
        "bootstrap_source_verified_before_helper_exec",
        "staging_helper_source_sha256", "observed_staging_helper_size_bytes",
        "staging_helper_verified_before_exec", "python_executable_path",
        "python_executable_sha256", "python_version",
        "python_identity_verified_before_root_creation", "upload_staging_root",
        "target_materialization_root", "pod_endpoint",
        "both_roots_observed_absent_before_staging_creation",
        "upload_staging_root_created_create_only",
        "target_materialization_root_created_by_staging_helper",
        "expected_uploaded_relative_paths",
        "upload_staging_cleanup_disposition", "formal_worker_count",
        "registered_performance_timing_count", "receipt_sha256",
    }
    if set(receipt) != expected_receipt_keys:
        raise PrepareError("Goal5791 upload staging receipt fields drifted")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if claimed != _digest(unsigned) \
            or receipt["schema"] != UPLOAD_STAGING_RECEIPT_SCHEMA \
            or receipt["goal"] != 5791 \
            or receipt["status"] != UPLOAD_STAGING_RECEIPT_STATUS \
            or receipt["owner_target_prepare_authority_file_sha256"] \
                != owner_authority_sha256 \
            or receipt["staging_helper_source_sha256"] \
                != staging_helper_sha256 \
            or receipt["bootstrap_source_sha256"] \
                != first_entry_stdin_bootstrap["source_sha256"] \
            or receipt["bootstrap_source_verified_before_helper_exec"] \
                is not True \
            or receipt["observed_staging_helper_size_bytes"] \
                != staging_helper_size_bytes \
            or receipt["staging_helper_verified_before_exec"] is not True \
            or receipt["python_executable_path"] \
                != required_target["base_python_executable_path"] \
            or receipt["python_executable_sha256"] \
                != required_target["base_python_executable_sha256"] \
            or receipt["python_version"] \
                != required_target["base_python_version"] \
            or receipt["python_identity_verified_before_root_creation"] \
                is not True \
            or receipt["upload_staging_root"] != str(staging_root) \
            or receipt["target_materialization_root"] \
                != str(materialization_root) \
            or receipt["pod_endpoint"] != pod_endpoint \
            or receipt["both_roots_observed_absent_before_staging_creation"] \
                is not True \
            or receipt["upload_staging_root_created_create_only"] is not True \
            or receipt[
                "target_materialization_root_created_by_staging_helper"
            ] is not False \
            or receipt["expected_uploaded_relative_paths"] \
                != STAGED_UPLOAD_RELATIVE_PATHS \
            or receipt["upload_staging_cleanup_disposition"] \
                != UPLOAD_STAGING_CLEANUP_DISPOSITION \
            or receipt["formal_worker_count"] != 0 \
            or receipt["registered_performance_timing_count"] != 0:
        raise PrepareError("Goal5791 upload staging receipt drifted")
    rows = {}
    for label, path in {**staged_paths, "staging_open_receipt": receipt_path}.items():
        rows[label] = {
            "resolved_path": str(path),
            "size_bytes": path.stat().st_size,
            "sha256": _sha(path),
            "write_bits_absent": (path.stat().st_mode & 0o222) == 0,
        }
    body = {
        "schema": "rtdl.goal5791.upload_staging_identity.v1",
        "upload_staging_root": str(staging_root),
        "target_materialization_root": str(materialization_root),
        "staged_inputs": rows,
        "exact_regular_file_set": True,
        "all_staged_paths_without_write_bits": True,
        "link_or_special_path_count": 0,
        "staging_open_receipt_file_sha256": _sha(receipt_path),
        "upload_staging_cleanup_disposition": (
            UPLOAD_STAGING_CLEANUP_DISPOSITION),
        "upload_staging_cleanup_completed_by_target_prepare": False,
    }
    return {**body, "upload_staging_identity_sha256": _digest(body)}


def _pod_endpoint_identity_record(
    *, ssh_user: str, host: str, port: int,
) -> dict[str, object]:
    if not isinstance(ssh_user, str) or not ssh_user \
            or any(character.isspace() for character in ssh_user) \
            or not isinstance(host, str) or not host \
            or any(character.isspace() for character in host) \
            or isinstance(port, bool) or not isinstance(port, int) \
            or not 1 <= port <= 65_535:
        raise PrepareError("Goal5791 POD endpoint input is invalid")
    source = {"ssh_user": ssh_user, "host": host, "port": port}
    return {**source, "identity_sha256": _digest(source)}


def _observe_python_version(python: Path) -> str:
    completed = subprocess.run(
        [str(python), "-c", "import platform;print(platform.python_version())"],
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8"},
        text=True, encoding="utf-8", errors="strict", capture_output=True,
        check=False, timeout=30,
    )
    value = completed.stdout.strip()
    if completed.returncode or re.fullmatch(r"3\.12\.\d+", value) is None:
        raise PrepareError("Goal5791 base Python version probe failed")
    return value


def _remove_write_bits(path: Path) -> None:
    for item in sorted(path.rglob("*"), reverse=True):
        if item.is_symlink():
            raise PrepareError(f"cannot seal symlink: {item}")
        item.chmod(item.stat().st_mode & ~0o222)
    path.chmod(path.stat().st_mode & ~0o222)


def _normalize_and_seal_venv(venv: Path) -> None:
    """Materialize a link-free frozen venv for the exact formal runtime."""

    # CPython may create this redundant compatibility link even with
    # ``venv --copies``.  It is not used by the frozen Linux prefix and can be
    # removed only when it resolves to this venv's own ``lib`` directory.
    lib64 = venv / "lib64"
    if lib64.is_symlink():
        if lib64.resolve() != (venv / "lib").resolve():
            raise PrepareError("Goal5791 venv lib64 link escapes its lib tree")
        lib64.unlink()
    _remove_write_bits(venv)


def _write_k4(path: Path) -> None:
    edges = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    path.write_bytes(b"".join(struct.pack("<ii", *edge) for edge in edges))


def _traversal_ok(value: dict[str, object]) -> bool:
    snapshot = value.get("native_snapshot")
    return isinstance(snapshot, dict) and (
        value.get("physical_executor_classification")
            == "optix_traversal_observed"
        and snapshot.get("successful_launch_count", 0) > 0
        and snapshot.get("complete_context_launch_count")
            == snapshot.get("successful_launch_count")
        and snapshot.get("failed_launch_count") == 0
        and snapshot.get("incomplete_context_launch_count") == 0
        and snapshot.get("pending_context_at_finish") == 0
        and snapshot.get("session_error") == 0
    )


def _inside(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    parent = root.resolve()
    return resolved == parent or parent in resolved.parents


def _successful_absolute_trace_paths(
    trace: Path, syscall: str,
) -> set[Path]:
    if syscall not in {"execve", "openat"}:
        raise ValueError(f"unsupported traced syscall: {syscall}")

    # strace prints execve's pathname as argument one, but openat's pathname
    # as argument two after its directory fd.  Keep these grammars separate:
    # treating both as syscall("path", ...) silently misses every real openat.
    quoted = r'(?P<quoted>"(?:\\.|[^"\\])*")'
    if syscall == "execve":
        call = re.compile(rf'\bexecve\(\s*{quoted}')
    else:
        call = re.compile(rf'\bopenat\(\s*[^,]+,\s*{quoted}')
    completed = re.compile(r"\)\s+=\s+(?P<return>-?[0-9]+)\b")
    resumed = re.compile(
        rf'<\.\.\.\s+{re.escape(syscall)}\s+resumed>.*'
        r'=\s+(?P<return>-?[0-9]+)\b')
    prefix = re.compile(r"^\s*(?:\[pid\s+(?P<bracket>[0-9]+)\]|"
                        r"(?P<plain>[0-9]+))?\s*")

    def process_key(line: str) -> str:
        match = prefix.match(line)
        if match is None:
            return "main"
        return match.group("bracket") or match.group("plain") or "main"

    def absolute_path(quoted_path: str) -> Path | None:
        try:
            decoded = ast.literal_eval(quoted_path)
        except (SyntaxError, ValueError):
            return None
        if not isinstance(decoded, str) or not decoded.startswith("/"):
            return None
        return Path(decoded).resolve()

    result: set[Path] = set()
    pending: dict[str, Path] = {}
    for line in trace.read_text(encoding="utf-8", errors="strict").splitlines():
        key = process_key(line)
        resume_match = resumed.search(line)
        if resume_match is not None:
            path = pending.pop(key, None)
            if path is not None and int(resume_match.group("return")) >= 0:
                result.add(path)
            continue
        call_match = call.search(line)
        if call_match is None:
            continue
        path = absolute_path(call_match.group("quoted"))
        if path is None:
            continue
        if "<unfinished ...>" in line:
            pending[key] = path
            continue
        return_match = completed.search(line)
        if return_match is not None and int(return_match.group("return")) >= 0:
            result.add(path)
    return result


def _audit_native_build_trace(
    trace: Path, *, nvcc: Path,
) -> dict[str, object]:
    executed = _successful_absolute_trace_paths(trace, "execve")
    resolved_nvcc = nvcc.resolve()
    if resolved_nvcc not in executed:
        raise PrepareError(
            "Goal5791 target native build did not execute the frozen nvcc")
    host_pattern = re.compile(
        r"(?:x86_64-linux-gnu-)?(?:gcc|g\+\+|cc|c\+\+)(?:-[0-9.]+)?$")
    hosts = sorted(
        path for path in executed if host_pattern.fullmatch(path.name)
    )
    if not hosts:
        raise PrepareError(
            "Goal5791 target native build exposed no actual host compiler")
    return {
        "trace_sha256": _sha(trace),
        "nvcc_executed_path": str(resolved_nvcc),
        "nvcc_executed_sha256": _sha(resolved_nvcc),
        "host_compiler_executed_paths": [str(path) for path in hosts],
        "host_compiler_executed_sha256": {
            str(path): _sha(path) for path in hosts
        },
        "actual_execve_observed": True,
    }


def _is_cuda_producer_binary(path: Path) -> bool:
    name = path.name
    return bool(
        re.fullmatch(r"libnvrtc(?:-builtins)?\.so(?:\..+)?", name)
        or re.fullmatch(r"libnvvm\.so(?:\..+)?", name)
        or (name.startswith("libdevice") and name.endswith(".bc"))
    )


def _validate_target_producer_observation_fields(
    observation: dict[str, object], *, cuda: Path,
) -> dict[str, str]:
    expected_versions = EXPECTED_TARGET_PRODUCER_DEPENDENCY_VERSIONS
    expected_cuda_spelling = cuda.as_posix()
    if any(observation.get(name) != value
           for name, value in expected_versions.items()) \
            or observation.get("schema") \
                != "rtdl.goal5791.target_ptx_producer_observation.v1" \
            or observation.get("cuda_home") != expected_cuda_spelling \
            or observation.get("cuda_path") != expected_cuda_spelling \
            or observation.get("numba_selected_nvvm_by") != "CUDA_HOME" \
            or observation.get("numba_selected_libdevice_by") != "CUDA_HOME" \
            or observation.get("cupy_nvrtc_runtime_version") != [12, 8] \
            or observation.get("nvrtc_probe_output") != 5791 \
            or observation.get("private_cupy_cache_initially_empty") is not True \
            or observation.get("unique_pid_bearing_nvrtc_source") is not True \
            or observation.get("cache_payload_is_not_authoritative_evidence") \
                is not True \
            or observation.get("application_input_used") is not False \
            or observation.get("elapsed_values_recorded") is not False \
            or observation.get("registered_performance_timing_created") \
                is not False:
        raise PrepareError("Goal5791 target producer observation drifted")
    directives = observation.get("numba_probe_ptx_directives")
    if not isinstance(directives, dict) \
            or set(directives) != {"version", "target", "address_size"} \
            or directives.get("target") != "sm_89" \
            or directives.get("address_size") != "64":
        raise PrepareError("Goal5791 target Numba PTX directives drifted")
    return dict(expected_versions)


def _audit_target_producer_observation(
    observation: dict[str, object], *, trace: Path, cuda: Path,
) -> dict[str, object]:
    expected_versions = _validate_target_producer_observation_fields(
        observation, cuda=cuda)
    nvvm = Path(str(observation.get("numba_selected_nvvm_path"))).resolve()
    libdevice = Path(
        str(observation.get("numba_selected_libdevice_path"))).resolve()
    nvvm_paths = observation.get("loaded_nvvm_paths")
    nvrtc_paths = observation.get("loaded_nvrtc_family_paths")
    nvvm_hashes = observation.get("loaded_nvvm_sha256")
    nvrtc_hashes = observation.get("loaded_nvrtc_family_sha256")
    if not isinstance(nvvm_paths, list) or nvvm_paths != [str(nvvm)] \
            or not isinstance(nvrtc_paths, list) or len(nvrtc_paths) != 2 \
            or not isinstance(nvvm_hashes, dict) \
            or not isinstance(nvrtc_hashes, dict):
        raise PrepareError("Goal5791 target mapped producer set drifted")
    mapped = [nvvm, *[Path(str(item)).resolve() for item in nvrtc_paths]]
    if not nvvm.is_file() or not libdevice.is_file() \
            or any(not path.is_file() or not _inside(path, cuda)
                   for path in [*mapped, libdevice]) \
            or observation.get("numba_selected_nvvm_sha256") != _sha(nvvm) \
            or observation.get("numba_selected_libdevice_sha256") \
                != _sha(libdevice) \
            or nvvm_hashes != {str(nvvm): _sha(nvvm)} \
            or nvrtc_hashes != {
                str(path): _sha(path) for path in mapped[1:]
            }:
        raise PrepareError("Goal5791 target producer path/hash drifted")
    names = {path.name for path in mapped[1:]}
    if not any(name.startswith("libnvrtc.so") for name in names) \
            or not any(name.startswith("libnvrtc-builtins.so") for name in names):
        raise PrepareError("Goal5791 target NVRTC/builtins pair is incomplete")
    successful_opens = _successful_absolute_trace_paths(trace, "openat")
    producer_opens = {
        path for path in successful_opens if _is_cuda_producer_binary(path)
    }
    expected_opens = {nvvm, libdevice, *mapped[1:]}
    if not expected_opens.issubset(producer_opens):
        raise PrepareError("Goal5791 target producer trace missed expected bytes")
    foreign = sorted(producer_opens - expected_opens)
    if foreign:
        raise PrepareError(
            "Goal5791 target producer trace opened foreign producer bytes: "
            + repr([str(path) for path in foreign]))
    return {
        "observation_sha256": _digest(observation),
        "trace_sha256": _sha(trace),
        "dependency_versions": expected_versions,
        "numba_selected_nvvm_path": str(nvvm),
        "numba_selected_nvvm_sha256": _sha(nvvm),
        "numba_selected_libdevice_path": str(libdevice),
        "numba_selected_libdevice_sha256": _sha(libdevice),
        "loaded_nvrtc_family_paths": [str(path) for path in mapped[1:]],
        "loaded_nvrtc_family_sha256": {
            str(path): _sha(path) for path in mapped[1:]
        },
        "successful_exact_producer_opens": sorted(
            str(path) for path in expected_opens),
        "foreign_successful_producer_opens": [],
        "fresh_numba_compile_observed": True,
        "forced_unique_nvrtc_compile_and_launch_observed": True,
    }


def _target_build_environment(
    ambient: dict[str, str], *, source: Path, venv: Path, cuda: Path,
    optix_root: Path, numba_cache_root: Path,
) -> dict[str, str]:
    """Construct the preparation environment without producer/cache selectors."""

    value = dict(ambient)
    for name in tuple(value):
        if name in AMBIENT_DEVICE_OR_CACHE_SELECTORS \
                or name.startswith("RTDL_V4_FORMAL_LEAF_CACHE"):
            value.pop(name)
    value.update({
        "PYTHONPATH": os.pathsep.join((
            str(source / "src"), str(source), str(source / "scripts"))),
        "PATH": os.pathsep.join((str(venv / "bin"), str(cuda / "bin"),
                                  value.get("PATH", ""))),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        # PYTHONDONTWRITEBYTECODE suppresses .pyc payloads, but Numba's
        # cache=True locator can still create an empty package __pycache__.
        # Preparation runs while source is writable, so redirect the Numba
        # cache itself to the disposable, source-external cache root.
        "NUMBA_CACHE_DIR": str(numba_cache_root),
        "LC_ALL": "C.UTF-8",
        "CUDA_HOME": str(cuda),
        "CUDA_PATH": str(cuda),
        "LD_LIBRARY_PATH": os.pathsep.join((
            str(cuda / "lib64"), "/usr/lib/x86_64-linux-gnu")),
        "RTDL_V4_CUDA_PREFIX": str(cuda),
        "RTDL_V4_OPTIX_PREFIX": str(optix_root),
    })
    value.pop("LD_PRELOAD", None)
    return value


def _preserved_dependency_wheelhouse(path: Path) -> bytes:
    data = path.read_bytes()
    if _sha_bytes(data) != EXPECTED_WHEELHOUSE_SHA256:
        raise PrepareError(
            "Goal5791 preserved dependency wheelhouse bytes drifted")
    return data


def main() -> None:
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--data-bundle", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--optix-headers", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--upload-staging-root", type=Path, required=True)
    parser.add_argument(
        "--target-materialization-root", type=Path, required=True)
    parser.add_argument("--cuda-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--pod-ssh-user", required=True)
    parser.add_argument("--pod-host", required=True)
    parser.add_argument("--pod-port", type=int, required=True)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    data_bundle = args.data_bundle.resolve()
    wheelhouse_archive = args.wheelhouse.resolve()
    optix_archive = args.optix_headers.resolve()
    authority = args.authority.resolve()
    upload_staging_root = args.upload_staging_root.resolve()
    root = args.target_materialization_root.resolve()
    base_python_invocation = str(args.python)
    if base_python_invocation != "/usr/bin/python3":
        raise PrepareError(
            "Goal5791 Stage-A Python invocation must be exact /usr/bin/python3")
    base_python = args.python.resolve()
    target_prepare_path = Path(__file__).resolve()
    materialization_root_absence_observed_at_entry = not os.path.lexists(root)
    if not materialization_root_absence_observed_at_entry:
        raise FileExistsError(root)
    if not all(path.is_file() for path in (
        bundle, data_bundle, wheelhouse_archive, optix_archive, authority,
        target_prepare_path, base_python,
    )):
        raise FileNotFoundError("Goal5791 prepare input is absent")
    if _sha(data_bundle) != EXPECTED_DATA_SHA256 \
            or _sha(wheelhouse_archive) != EXPECTED_WHEELHOUSE_SHA256 \
            or _sha(optix_archive) != EXPECTED_OPTIX_HEADERS_SHA256:
        raise PrepareError("Goal5791 external upload bytes drifted")
    pod_endpoint = _pod_endpoint_identity_record(
        ssh_user=args.pod_ssh_user, host=args.pod_host, port=args.pod_port)
    outer, manifest = _owner_pinned_bundle_admission(
        authority=authority, bundle=bundle, materialization_root=root,
        upload_staging_root=upload_staging_root, pod_endpoint=pod_endpoint,
    )
    source_bytes = outer["SOURCE.tar.gz"]
    source_sha = _sha_bytes(source_bytes)

    nvidia_smi = Path("/usr/bin/nvidia-smi")
    if not nvidia_smi.is_file() or not os.access(nvidia_smi, os.X_OK):
        raise PrepareError(
            "Goal5791 target identity requires exact /usr/bin/nvidia-smi")
    nvidia = subprocess.run([
        str(nvidia_smi),
        "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ], text=True, encoding="utf-8", errors="replace", capture_output=True,
        check=True, timeout=30)
    rows = [line for line in nvidia.stdout.splitlines() if line.strip()]
    if len(rows) != 1 or len(rows[0].split(",")) != 4:
        raise PrepareError("Goal5791 requires exactly one visible target GPU")
    gpu_parts = [item.strip() for item in rows[0].split(",")]
    gpu = dict(zip(
        ("gpu_name", "gpu_uuid", "driver_version", "compute_capability"),
        gpu_parts, strict=True,
    ))
    if gpu["gpu_name"] != "NVIDIA RTX 4000 Ada Generation" \
            or gpu["compute_capability"] != "8.9":
        raise PrepareError("Goal5791 target is not the frozen RTX 4000 Ada")
    base_python_version = _observe_python_version(base_python)
    owner = _validate_owner(
        authority, bundle_sha=_sha(bundle), source_sha=source_sha,
        materialization_root=root,
        upload_staging_root=upload_staging_root, gpu=gpu,
        base_python_sha256=_sha(base_python),
        base_python_version=base_python_version,
        base_python_path=base_python_invocation, pod_endpoint=pod_endpoint,
    )
    _crossbind_owner_joint_home_chain(
        owner, outer=outer, manifest=manifest)
    # Cross-bind all frozen pretarget identities before creating the root.
    expected_owner_hashes = {
        "pretarget_preexecution_authority_file_sha256": _sha_bytes(
            outer["PRETARGET_PREEXECUTION_AUTHORITY.json"]),
        "formal_contract_sha256": manifest["formal_contract_sha256"],
        "schedule_sha256": manifest["schedule_sha256"],
        "runtime_budget_authority_file_sha256": _sha_bytes(
            outer["RUNTIME_BUDGET.json"]),
        "token_amendment_sha256": manifest["token_amendment_sha256"],
    }
    if any(owner[name] != expected
           for name, expected in expected_owner_hashes.items()):
        raise PermissionError("Goal5791 owner frozen authority binding drifted")

    staged_paths = {
        "bundle": bundle,
        "data_bundle": data_bundle,
        "wheelhouse": wheelhouse_archive,
        "optix_headers": optix_archive,
        "owner_authority": authority,
        "target_prepare": target_prepare_path,
    }
    staging_identity = _validate_upload_staging(
        staging_root=upload_staging_root, materialization_root=root,
        staged_paths=staged_paths,
        owner_authority_sha256=_sha(authority),
        staging_helper_sha256=_sha_bytes(
            outer["HARNESS/OPEN_UPLOAD_STAGING.py"]),
        staging_helper_size_bytes=len(
            outer["HARNESS/OPEN_UPLOAD_STAGING.py"]),
        first_entry_stdin_bootstrap=owner["first_entry_stdin_bootstrap"],
        required_target=owner["required_target"],
        pod_endpoint=pod_endpoint,
    )
    materialization_parent = root.parent.resolve()
    if not materialization_parent.is_dir() \
            or materialization_parent.is_symlink():
        raise PrepareError(
            "Goal5791 target materialization parent is not a real directory")
    required_free_bytes = owner["resource_confirmation"][
        "confirmed_free_disk_bytes"]
    observed_free_bytes = shutil.disk_usage(materialization_parent).free
    if observed_free_bytes < required_free_bytes \
            or observed_free_bytes < 20_000_000_000:
        raise PrepareError(
            "Goal5791 target materialization capacity admission failed")
    resource_admission_body = {
        "schema": "rtdl.goal5791.target_materialization_resource_admission.v1",
        "target_materialization_root": str(root),
        "target_materialization_parent_resolved_path": str(
            materialization_parent),
        "confirmed_free_disk_bytes": required_free_bytes,
        "minimum_required_free_disk_bytes": 20_000_000_000,
        "observed_free_disk_bytes_before_root_creation": observed_free_bytes,
        "observed_at_target_entry_before_materialization_root_creation": True,
        "admitted": True,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    resource_admission = {
        **resource_admission_body,
        "resource_admission_sha256": _digest(resource_admission_body),
    }
    # The initial observation is rechecked immediately before the exclusive
    # mkdir.  A same-host malicious race remains outside the stated TCB, but a
    # normal collision fails closed and cannot turn this into root reuse.
    if os.path.lexists(root):
        raise FileExistsError(root)

    root.mkdir(parents=True)
    logs = root / "logs"
    result = root / "result"
    logs.mkdir()
    result.mkdir()
    source_archive = result / "EXECUTION_SOURCE.tar.gz"
    source_archive.write_bytes(source_bytes)
    owner_prepare_authority_path = (
        result / "OWNER_TARGET_PREPARE_AUTHORITY.json")
    owner_prepare_authority_path.write_bytes(authority.read_bytes())
    if _sha(owner_prepare_authority_path) != _sha(authority):
        raise PrepareError("Goal5791 Stage-A owner authority copy drifted")
    staging_receipt_copy = result / UPLOAD_STAGING_RECEIPT_NAME
    staging_receipt_copy.write_bytes(
        (upload_staging_root / UPLOAD_STAGING_RECEIPT_NAME).read_bytes())
    if _sha(staging_receipt_copy) != staging_identity[
            "staging_open_receipt_file_sha256"]:
        raise PrepareError("Goal5791 staging receipt copy drifted")
    staging_receipt_copy.chmod(staging_receipt_copy.stat().st_mode & ~0o222)
    source_payloads = _read_regular_archive(source_archive)
    source = root / "source"
    _extract_payloads(source_payloads, source)
    source_manifest = _validate_source_payloads(source_payloads, source)
    source_manifest_file_sha = _sha(source / SOURCE_MANIFEST_MEMBER)
    _audit_exact_source_set(
        source, source_manifest,
        manifest_file_sha256=source_manifest_file_sha,
        require_read_only=False,
    )
    if source_manifest.get("source_tree_sha256") \
            != manifest["source_tree_sha256"] \
            or _sha(source / SOURCE_MANIFEST_MEMBER) \
                != manifest["source_manifest_sha256"]:
        raise PrepareError("Goal5791 extracted source identity drifted")
    sys.path.insert(0, str(source))
    from scripts import goal5791_formal_contract as contract
    if contract.contract_sha256() != manifest["formal_contract_sha256"] \
            or contract.schedule_sha256() != manifest["schedule_sha256"]:
        raise PrepareError("Goal5791 formal contract/schedule drifted")

    data_root = root / "data"
    data_paths = _extract_selected(
        data_bundle, {item["member"] for item in EXPECTED_DATA.values()},
        data_root,
    )
    datasets: dict[str, dict[str, object]] = {}
    for dataset_id, frozen in EXPECTED_DATA.items():
        path = data_paths[frozen["member"]]
        if path.stat().st_size != frozen["bytes"] or _sha(path) != frozen["sha256"]:
            raise PrepareError(f"Goal5791 extracted data drifted: {dataset_id}")
        path.chmod(path.stat().st_mode & ~0o222)
        datasets[dataset_id] = {
            "edge_path": str(path.resolve()),
            "input_sha256": frozen["sha256"],
            "size_bytes": frozen["bytes"],
            "expected_triangle_count": frozen["expected_triangle_count"],
            "oracle_authority_sha256": frozen["oracle_authority_sha256"],
        }

    wheelhouse_payloads = _read_regular_archive(wheelhouse_archive)
    wheelhouse = root / "wheelhouse"
    _extract_payloads(wheelhouse_payloads, wheelhouse)
    wheels = sorted(wheelhouse.rglob("*.whl"))
    if len(wheels) != 6:
        raise PrepareError("Goal5791 wheelhouse wheel count drifted")
    dependency_lock_body = {
        "schema": "rtdl.goal5791.target_dependency_lock.v1",
        "wheelhouse_archive_sha256": EXPECTED_WHEELHOUSE_SHA256,
        "wheels": [
            {"filename": path.name, "bytes": path.stat().st_size,
             "sha256": _sha(path)} for path in wheels
        ],
        "network_install_allowed": False,
    }
    dependency_lock = {
        **dependency_lock_body,
        "dependency_lock_sha256": _digest(dependency_lock_body),
    }
    dependency_lock_path = result / "DEPENDENCY_LOCK.json"
    _write_json_create_only(dependency_lock_path, dependency_lock)

    optix_payloads = _read_regular_archive(optix_archive)
    optix_root = root / "optix9"
    _extract_payloads(optix_payloads, optix_root)
    optix_include = optix_root / "include"
    header = (optix_include / "optix.h").read_text(
        encoding="utf-8", errors="strict")
    if re.search(r"#\s*define\s+OPTIX_VERSION\s+90000\b", header) is None:
        raise PrepareError("Goal5791 OptiX header authority is not 9.0")

    cuda = args.cuda_root.resolve()
    cuda_include = (
        cuda / "targets/x86_64-linux/include"
        if (cuda / "targets/x86_64-linux/include/cuda.h").is_file()
        else cuda / "include"
    )
    nvcc = cuda / "bin/nvcc"
    if not nvcc.is_file() or not (cuda_include / "cuda.h").is_file():
        raise PrepareError("Goal5791 target CUDA toolkit is incomplete")
    nvcc_text = _run(
        [str(nvcc), "--version"], cwd=root, env=dict(os.environ),
        log=logs / "nvcc.log", timeout=30,
    )
    if "release 12.8" not in nvcc_text:
        raise PrepareError("Goal5791 target CUDA toolkit is not 12.8")

    venv = root / "venv"
    _run(
        [str(base_python), "-m", "venv", "--copies", str(venv)], cwd=root,
        env=dict(os.environ), log=logs / "venv.log", timeout=300,
    )
    # Preserve the venv entrypoint spelling.  Resolving a symlink here would
    # accidentally invoke the base interpreter for the offline installation
    # and later misstate the formal runtime path.
    python = venv / "bin/python"
    if not python.is_file():
        raise PrepareError("Goal5791 target venv Python is absent")
    install_env = dict(os.environ)
    for name in tuple(install_env):
        if name in AMBIENT_DEVICE_OR_CACHE_SELECTORS \
                or name.startswith("RTDL_V4_FORMAL_LEAF_CACHE"):
            install_env.pop(name)
    install_env.update({
        "PIP_NO_INDEX": "1", "PYTHONNOUSERSITE": "1",
        "LC_ALL": "C.UTF-8",
        "CUDA_HOME": str(cuda), "CUDA_PATH": str(cuda),
        "LD_LIBRARY_PATH": os.pathsep.join((
            str(cuda / "lib64"), "/usr/lib/x86_64-linux-gnu")),
    })
    install_env.pop("LD_PRELOAD", None)
    _run([
        str(python), "-m", "pip", "install", "--no-index", "--no-deps",
        "--find-links", str(wheelhouse), *[str(path) for path in wheels],
    ], cwd=root, env=install_env, log=logs / "offline_install.log", timeout=1800)
    identity = json.loads(_run([
        str(python), "-c",
        "import json,platform,llvmlite,numba,numpy,cupy; "
        "from cupy.cuda import runtime; "
        "print(json.dumps({'python':platform.python_version(),"
        "'numba':numba.__version__,'numpy':numpy.__version__,"
        "'llvmlite':llvmlite.__version__,"
        "'cupy':cupy.__version__,'cuda_runtime_int':runtime.runtimeGetVersion()},"
        "sort_keys=True))",
    ], cwd=root, env=install_env, log=logs / "python_identity.log", timeout=120).strip())
    if identity != EXPECTED_TARGET_DEPENDENCY_IDENTITY:
        raise PrepareError(f"Goal5791 target dependency identity drifted: {identity!r}")

    prepare_cache_root = root / "prepare_cupy_and_numba_caches"
    prepare_cache_root.mkdir()
    numba_cache_root = prepare_cache_root / "numba"
    numba_cache_root.mkdir()
    build_env = _target_build_environment(
        dict(os.environ), source=source, venv=venv, cuda=cuda,
        optix_root=optix_root, numba_cache_root=numba_cache_root,
    )
    strace = Path("/usr/bin/strace")
    if not strace.is_file() or not os.access(strace, os.X_OK):
        raise PrepareError("Goal5791 target producer admission requires strace")
    native_build_trace = logs / "native_build_execve_openat.log"
    _run([
        str(strace), "-f", "-s", "4096", "-e", "trace=execve,openat",
        "-o", str(native_build_trace),
        "make", "build-optix", f"OPTIX_PREFIX={optix_root}",
        f"CUDA_PREFIX={cuda}", "OPTIX_CUDA_ARCH=sm_89",
    ], cwd=source, env=build_env, log=logs / "build.log", timeout=1800)
    native_build_audit = _audit_native_build_trace(
        native_build_trace, nvcc=nvcc)
    host_compiler_versions = {}
    for index, spelling in enumerate(
        native_build_audit["host_compiler_executed_paths"]
    ):
        path = Path(str(spelling))
        version_text = _run(
            [str(path), "--version"], cwd=root, env=build_env,
            log=logs / f"host_compiler_{index:02d}.log", timeout=30,
        )
        host_compiler_versions[str(path)] = version_text.splitlines()[0].strip()
    native_build_audit["host_compiler_version_first_line"] = (
        host_compiler_versions)
    built_native = (source / "build/librtdl_optix.so").resolve()
    if not built_native.is_file():
        raise PrepareError("Goal5791 fresh target native is absent")
    native_root = root / "native"
    native_root.mkdir()
    native = (native_root / "librtdl_optix.so").resolve()
    shutil.copy2(built_native, native)
    build_root = source / "build"
    if build_root.is_symlink() \
            or build_root.resolve().parent != source.resolve():
        raise PrepareError("Goal5791 native build cleanup target escaped source")
    shutil.rmtree(build_root.resolve())
    native_sha = _sha(native)
    build_env["RTDL_OPTIX_LIB"] = build_env["RTDL_OPTIX_LIBRARY"] = str(native)

    producer_cache = prepare_cache_root / "target_producer_probe"
    producer_cache.mkdir()
    producer_env = dict(build_env)
    producer_env["CUPY_CACHE_DIR"] = str(producer_cache)
    producer_observation_path = result / "TARGET_PTX_PRODUCER_OBSERVATION.json"
    producer_trace = logs / "target_producer_openat.log"
    _run([
        str(strace), "-f", "-s", "4096", "-e", "trace=openat",
        "-o", str(producer_trace), str(python),
        str(source / "scripts/goal5791_target_producer_probe.py"),
        "--output", str(producer_observation_path),
    ], cwd=source, env=producer_env,
        log=logs / "target_producer_probe.log", timeout=1800)
    producer_observation = _strict_json(producer_observation_path)
    producer_audit = _audit_target_producer_observation(
        producer_observation, trace=producer_trace, cuda=cuda)

    focused = _run([
        str(python), "-m", "unittest",
        "tests.goal5791_verified_fusion_execution_token_test",
        "tests.goal5791_segment_descriptors_test",
        "tests.goal5791_formal_contract_test",
        "tests.goal5791_formal_worker_controller_test",
        "tests.goal5791_formal_evaluator_recount_test",
    ], cwd=source, env=build_env, log=logs / "focused_tests.log", timeout=1800)
    if "OK" not in focused:
        raise PrepareError("Goal5791 target focused tests did not pass")

    helper = source / "scripts/goal5791_target_token_smoke.py"
    inspection_path = result / "TARGET_PROGRAM_INSPECTION.json"
    inspection_cache = prepare_cache_root / "inspect_target"
    inspection_cache.mkdir()
    inspection_env = dict(build_env)
    inspection_env["CUPY_CACHE_DIR"] = str(inspection_cache)
    common = [
        str(python), str(helper), "--source-root", str(source),
        "--native", str(native), "--optix-include", str(optix_include),
        "--cuda-include", str(cuda_include), "--compute-capability", "89",
    ]
    _run([
        *common, "--mode", "inspect-target", "--output", str(inspection_path),
    ], cwd=source, env=inspection_env,
        log=logs / "inspect_target.log", timeout=1800)
    inspection = _strict_json(inspection_path)
    if inspection.get("status") != "PASS__COMPILE_AND_IDENTITY_ONLY" \
            or inspection.get("native_library_sha256") != native_sha \
            or inspection.get("token_api_present") is not True:
        raise PrepareError("Goal5791 target inspection drifted")

    target_evidence_contract = {
        "schema": "rtdl.goal5791.target_evidence_contract.v1",
        "source_bytes_preserved": True,
        "native_bytes_preserved": True,
        "program_identity_and_composer_enforced_directives_recorded": True,
        "raw_composed_ptx_bytes_preserved": False,
        "independent_raw_ptx_reparse_supported": False,
        "dependency_wheelhouse_bytes_preserved": True,
        "dependency_wheelhouse_sha256": EXPECTED_WHEELHOUSE_SHA256,
        "upload_staging_open_receipt_preserved": True,
        "upload_staging_identity_preserved": True,
        "upload_staging_cleanup_incomplete_until_local_preservation": True,
        "target_materialization_resource_admission_preserved": True,
        "token_functional_smoke_required_before_postprepare_authority": True,
        "formal_workers_allowed": False,
        "registered_timings_allowed": False,
    }
    toolchain_identity = {
        "gpu": gpu,
        "nvidia_smi_path": str(nvidia_smi),
        "nvidia_smi_sha256": _sha(nvidia_smi),
        "cuda_toolkit_version": "12.8",
        "optix_sdk_version": "9.0.0",
        "python": identity,
        "python_executable_sha256": _sha(python),
        "native_build_producer_audit": native_build_audit,
        "ptx_producer_audit": producer_audit,
    }
    target_evidence_path = result / "TARGET_MATERIALIZATION_EVIDENCE.tar.gz"
    target_evidence_path.write_bytes(_deterministic_archive({
        "EXECUTION_SOURCE.tar.gz": source_archive.read_bytes(),
        "TARGET_NATIVE/librtdl_optix.so": native.read_bytes(),
        "TARGET_PROGRAM_INSPECTION.json": inspection_path.read_bytes(),
        "TARGET_PTX_PRODUCER_OBSERVATION.json": (
            producer_observation_path.read_bytes()),
        "TARGET_PTX_PRODUCER_OPENAT_TRACE.log": producer_trace.read_bytes(),
        "TARGET_PTX_PRODUCER_AUDIT.json": (
            json.dumps(producer_audit, indent=2, sort_keys=True) + "\n"
        ).encode(),
        "TARGET_NATIVE_BUILD_EXECVE_OPENAT_TRACE.log": (
            native_build_trace.read_bytes()),
        "TARGET_NATIVE_BUILD_PRODUCER_AUDIT.json": (
            json.dumps(native_build_audit, indent=2, sort_keys=True) + "\n"
        ).encode(),
        "SOURCE_MANIFEST.json": (source / SOURCE_MANIFEST_MEMBER).read_bytes(),
        "DEPENDENCY_LOCK.json": dependency_lock_path.read_bytes(),
        "DEPENDENCY_WHEELHOUSE.tar.gz": _preserved_dependency_wheelhouse(
            wheelhouse_archive),
        "UPLOAD_STAGING_OPEN_RECEIPT.json": (
            staging_receipt_copy.read_bytes()),
        "UPLOAD_STAGING_IDENTITY.json": (
            json.dumps(staging_identity, indent=2, sort_keys=True) + "\n"
        ).encode(),
        "TARGET_MATERIALIZATION_RESOURCE_ADMISSION.json": (
            json.dumps(resource_admission, indent=2, sort_keys=True) + "\n"
        ).encode(),
        "TOOLCHAIN_IDENTITY.json": (
            json.dumps(toolchain_identity, indent=2, sort_keys=True) + "\n").encode(),
        "TARGET_EVIDENCE_CONTRACT.json": (
            json.dumps(target_evidence_contract, indent=2, sort_keys=True)
            + "\n").encode(),
    }))

    product_authority_body = {
        "schema": "rtdl.v4.target_materialization_authority.v2",
        "shared_contract_freeze_sha256": _strict_json(
            source / SHARED_FREEZE_MEMBER)["shared_contract_freeze_sha256"],
        "execution_source_archive_sha256": source_sha,
        "execution_source_tree_sha256": source_manifest["source_tree_sha256"],
        "callback_ir_sha256": inspection["callback_ir_sha256"],
        "callback_authority_nonce": inspection["callback_authority_nonce"],
        "contract_sha256": inspection["contract_sha256"],
        "abi_sha256": inspection["abi_sha256"],
        "provider_identity": "optix",
        "program_bundle_identity": inspection["program_bundle_identity"],
        "composed_program_sha256": inspection["composed_program_sha256"],
        "cupy_version": identity["cupy"],
        "fusion_on_downstream_operation_recipe": inspection[
            "fusion_on_downstream_operation_recipe"],
        "fusion_off_downstream_operation_recipe": inspection[
            "fusion_off_downstream_operation_recipe"],
        "fusion_on_downstream_operation_recipe_sha256": inspection[
            "fusion_on_downstream_operation_recipe_sha256"],
        "fusion_off_downstream_operation_recipe_sha256": inspection[
            "fusion_off_downstream_operation_recipe_sha256"],
        "native_library_sha256": native_sha,
        "native_payload_sha256": native_sha,
        "target_identity_sha256": inspection["target_identity_sha256"],
        "materializer_source_sha256": _sha(
            source / "scripts/goal5791_target_prepare.py"),
        "source_manifest_sha256": _sha(source / SOURCE_MANIFEST_MEMBER),
        "evidence_archive_sha256": _sha(target_evidence_path),
        "materialization_nonce": secrets.token_hex(32),
        "actual_native_rehashed_from_preserved_payload": True,
        "actual_source_tree_recounted_from_preserved_archive": True,
        "cross_target_native_byte_reproducibility_claimed": False,
    }
    product_authority = {
        **product_authority_body,
        "receipt_sha256": _digest(product_authority_body),
    }
    product_authority_path = result / "TARGET_MATERIALIZATION_AUTHORITY.json"
    _write_json_create_only(product_authority_path, product_authority)

    k4 = result / "NEUTRAL_K4.edge"
    _write_k4(k4)
    k4_sha = _sha(k4)
    functional_root = result / "TARGET_FUNCTIONAL"
    functional_root.mkdir()
    smoke_files: list[Path] = []
    for lifecycle in ("cold", "prepared"):
        for variant in ("fusion_off", "fusion_on"):
            output = functional_root / f"{lifecycle}__{variant}.json"
            command = [
                *common, "--mode", "functional", "--shared-freeze",
                str(source / SHARED_FREEZE_MEMBER), "--target-materialization",
                str(product_authority_path), "--edge-file", str(k4),
                "--variant", variant, "--lifecycle", lifecycle,
                "--output", str(output),
            ]
            if lifecycle == "prepared":
                command.extend(["--neutral-prewarm-edge", str(k4)])
            lane_cache = prepare_cache_root / f"{lifecycle}__{variant}"
            lane_cache.mkdir()
            lane_env = dict(build_env)
            lane_env["CUPY_CACHE_DIR"] = str(lane_cache)
            _run(
                command, cwd=source, env=lane_env,
                log=logs / f"functional_{lifecycle}_{variant}.log", timeout=1800,
            )
            lane = _strict_json(output)
            expected_events = 2 if variant == "fusion_on" else 7
            segments = lane.get("segments")
            if lane.get("status") != "PASS__CREATE_ONLY_TOKEN_SMOKE" \
                    or lane.get("output") != 4 \
                    or lane.get("token_path_only") is not True \
                    or lane.get("fresh_private_cupy_cache_at_process_start") \
                        is not True \
                    or lane.get("registered_performance_timing_count") != 0 \
                    or not isinstance(segments, list) or len(segments) != 1 \
                    or segments[0]["operation_evidence_receipt"][
                        "successful_event_count"] != expected_events \
                    or not _traversal_ok(segments[0]["traversal_receipt"]):
                raise PrepareError("Goal5791 target token smoke drifted")
            smoke_files.append(output)
    functional_summary_body = {
        "schema": "rtdl.goal5791.target_token_functional_summary.v1",
        "lane_sha256": {path.name: _sha(path) for path in smoke_files},
        "lane_count": 4,
        "exact_lane_count": 4,
        "behavioral_true_optix_lane_count": 4,
        "token_only_lane_count": 4,
        "event_count_per_segment": {"fusion_off": 7, "fusion_on": 2},
        "cache_policy_sha256": _digest(contract.CACHE_POLICY),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "performance_or_compiler_fusion_claimed": False,
    }
    functional_summary = {
        **functional_summary_body,
        "summary_sha256": _digest(functional_summary_body),
    }
    functional_summary_path = functional_root / "SUMMARY.json"
    _write_json_create_only(functional_summary_path, functional_summary)
    shutil.rmtree(prepare_cache_root)
    if prepare_cache_root.exists() or prepare_cache_root.is_symlink():
        raise PrepareError("Goal5791 target prepare cache payload cleanup failed")

    freeze = _strict_json(source / SHARED_FREEZE_MEMBER)
    runtime_budget_authority = contract.validate_runtime_budget_authority(
        source / (
            "history/internal_docs/"
            "goal5791_pre_pod_conservative_runtime_budget_20260817.json"
        )
    )
    frozen_runtime_budget = runtime_budget_authority["frozen_budget"]
    worker_timeout_seconds = contract.FORMAL_EXECUTION_POLICY[
        "per_worker_timeout_seconds"]
    if isinstance(worker_timeout_seconds, bool) \
            or not isinstance(worker_timeout_seconds, (int, float)) \
            or float(worker_timeout_seconds) <= 0:
        raise PrepareError("Goal5791 formal worker timeout policy drifted")
    formal_sources = {
        name: _sha(source / name) for name in FORMAL_SOURCE_NAMES
    }
    runtime_identity = _digest({
        "schema": "rtdl.goal5791.runtime_identity.v1",
        "source_archive_sha256": source_sha,
        "source_tree_sha256": source_manifest["source_tree_sha256"],
        "native_library_sha256": native_sha,
        "dependency_lock_sha256": dependency_lock[
            "dependency_lock_sha256"],
        "toolchain_identity": toolchain_identity,
        "data_inputs": {
            key: value["input_sha256"] for key, value in datasets.items()
        },
    })
    prepared_identity_preimage = {
        "schema": "rtdl.goal5791.prepared_identity.v1",
        "runtime_identity_sha256": runtime_identity,
        "target_materialization_authority_sha256": _sha(product_authority_path),
        "target_evidence_archive_sha256": _sha(target_evidence_path),
        "target_functional_summary_sha256": _sha(functional_summary_path),
        "owner_prepare_authority_sha256": _sha(owner_prepare_authority_path),
        "upload_staging_identity_sha256": staging_identity[
            "upload_staging_identity_sha256"],
    }
    prepared_identity = _digest(prepared_identity_preimage)
    prepared_identity_record = {
        **prepared_identity_preimage,
        "prepared_identity_sha256": prepared_identity,
    }
    formal_identity_preimage = {
        "schema": "rtdl.goal5791.formal_identity.v1",
        "prepared_identity_sha256": prepared_identity,
        "runtime_identity_sha256": runtime_identity,
        "formal_contract_sha256": contract.contract_sha256(),
        "schedule_sha256": contract.schedule_sha256(),
        "formal_sources": formal_sources,
        "formal_worker_count": 96,
        "independent_row_count": 6,
    }
    formal_identity = _digest(formal_identity_preimage)
    formal_identity_record = {
        **formal_identity_preimage,
        "formal_identity_sha256": formal_identity,
    }
    recipes = {}
    for variant, operation_ids in (
        ("fusion_off", contract.FUSION_OFF_OPERATION_IDS),
        ("fusion_on", contract.FUSION_ON_OPERATION_IDS),
    ):
        actual = inspection[
            f"{variant}_downstream_operation_recipe"]
        wrapper = {
            "variant": variant,
            "mechanism_id": contract.MECHANISM_ID,
            "allowed_delta_id": contract.ALLOWED_DELTA_ID,
            "operation_ids": list(operation_ids),
        }
        recipes[variant] = {
            "actual_recipe": actual,
            "actual_recipe_sha256": _digest(actual),
            "claim_wrapper": wrapper,
            "claim_wrapper_sha256": _digest(wrapper),
        }
    hashes = {
        "execution_source_archive_sha256": source_sha,
        "execution_source_tree_sha256": source_manifest["source_tree_sha256"],
        "execution_source_manifest_sha256": _sha(source / SOURCE_MANIFEST_MEMBER),
        "native_library_sha256": native_sha,
        "native_payload_sha256": native_sha,
        "provider_library_sha256": native_sha,
        "provider_program_bundle_sha256": "f" * 64,
        "target_identity_sha256": inspection["target_identity_sha256"],
        "semantic_request_sha256": contract.SEMANTIC_REQUEST_SHA256,
        "physical_encoding_sha256": contract.PHYSICAL_ENCODING_SHA256,
        "reference_executable_family_sha256": _digest(
            freeze["executable_family_plan"]),
        "callback_ir_sha256": inspection["callback_ir_sha256"],
        "contract_sha256": inspection["contract_sha256"],
        "abi_sha256": inspection["abi_sha256"],
        "composed_program_sha256": inspection["composed_program_sha256"],
        "composed_ptx_sha256": inspection["composed_ptx_sha256"],
        "fusion_off_recipe_sha256": recipes["fusion_off"][
            "actual_recipe_sha256"],
        "fusion_on_recipe_sha256": recipes["fusion_on"][
            "actual_recipe_sha256"],
        "dependency_lock_sha256": dependency_lock["dependency_lock_sha256"],
        "materializer_sha256": _sha(source / "scripts/goal5791_target_prepare.py"),
        "target_source_manifest_sha256": _sha(source / SOURCE_MANIFEST_MEMBER),
        "target_evidence_contract_sha256": _digest(target_evidence_contract),
        "target_materialization_authority_sha256": _sha(product_authority_path),
        "runtime_identity_sha256": runtime_identity,
        "prepared_identity_sha256": prepared_identity,
        "formal_identity_sha256": formal_identity,
    }
    nonces = {
        "callback_authority_nonce": inspection["callback_authority_nonce"],
        "target_evidence_nonce": secrets.token_hex(32),
    }
    versions = {
        "gpu_uuid": gpu["gpu_uuid"],
        "compute_capability": "8.9",
        "driver_version": gpu["driver_version"],
        "cuda_runtime_version": "12.8.0",
        "optix_sdk_version": "9.0.0",
        "python_version": identity["python"],
        "cupy_version": identity["cupy"],
    }
    program_bundle = contract.provider_program_bundle_digest_record(
        hashes, nonces)
    hashes["provider_program_bundle_sha256"] = program_bundle["sha256"]
    binding_body = {
        "schema": contract.TARGET_BINDING_SCHEMA,
        "goal": 5791,
        "status": contract.TARGET_BINDING_STATUS,
        "hashes": hashes,
        "nonces": nonces,
        "versions": versions,
        "recipes": recipes,
        "derived_digests": {"provider_program_bundle": program_bundle},
        "cache_policy": deepcopy(contract.CACHE_POLICY),
    }
    binding = {**binding_body, "binding_sha256": _digest(binding_body)}
    contract.validate_target_materialization_binding(binding)
    binding_path = result / "TARGET_MATERIALIZATION_BINDING.json"
    _write_json_create_only(binding_path, binding)

    pretarget_path = source / PRETARGET_AUTHORITY_MEMBER
    pretarget = contract.load_preexecution_authority(
        pretarget_path, repository_root=source, require_target_binding=False)
    post_body = dict(pretarget)
    post_body.pop("authority_sha256")
    post_body["status"] = contract.POSTPREPARE_STATUS
    post_body["target_materialization_binding"] = binding
    post = {**post_body, "authority_sha256": _digest(post_body)}
    post_path = result / "GOAL5791_POSTPREPARE_PREEXECUTION_AUTHORITY.json"
    _write_json_create_only(post_path, post)
    contract.load_preexecution_authority(
        post_path, repository_root=source, require_target_binding=True)

    # Formal workers receive this exact minimal mapping plus their two private
    # dynamic cache paths (CUPY_CACHE_DIR and NUMBA_CACHE_DIR).  No ambient
    # environment is inherited by the controller.
    formal_environment = {
        "PYTHONPATH": os.pathsep.join((
            str(source / "src"), str(source), str(source / "scripts"))),
        "PATH": os.pathsep.join((str(venv / "bin"), str(cuda / "bin"),
                                  "/usr/bin", "/bin")),
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "LC_ALL": "C.UTF-8",
        "CUDA_HOME": str(cuda),
        "CUDA_PATH": str(cuda),
        "LD_LIBRARY_PATH": os.pathsep.join((
            str(cuda / "lib64"), "/usr/lib/x86_64-linux-gnu")),
        # Empty is an explicit frozen value: the formal controller passes the
        # key and worker observes it, while the dynamic loader preloads no
        # ambient library.
        "LD_PRELOAD": "",
        "RTDL_OPTIX_LIB": str(native),
        "RTDL_OPTIX_LIBRARY": str(native),
        "RTDL_V4_CUDA_PREFIX": str(cuda),
        "RTDL_V4_OPTIX_PREFIX": str(optix_root),
    }
    environment_contract = contract.FORMAL_WORKER_ENVIRONMENT_CONTRACT
    if list(formal_environment) != environment_contract["frozen_keys"] \
            or environment_contract["dynamic_keys"] \
                != ["CUPY_CACHE_DIR", "NUMBA_CACHE_DIR"] \
            or environment_contract["exact_live_key_set_required"] is not True \
            or environment_contract["ambient_environment_inherited"] is not False \
            or formal_environment["LC_ALL"] != environment_contract["lc_all"] \
            or formal_environment["LD_PRELOAD"] \
                != environment_contract["ld_preload"]:
        raise PrepareError(
            "Goal5791 runtime environment differs from formal contract")
    locale_probe = json.loads(_run([
        str(python), "-c",
        "import json,locale,os; "
        "print(json.dumps({'environment':dict(os.environ),"
        "'locale':locale.setlocale(locale.LC_ALL,'')},sort_keys=True))",
    ], cwd=root, env=formal_environment,
        log=logs / "formal_environment_locale_probe.log", timeout=60).strip())
    if locale_probe != {
        "environment": formal_environment,
        "locale": "C.UTF-8",
    }:
        raise PrepareError(
            "Goal5791 exact formal environment/locale probe drifted: "
            + repr(locale_probe))
    runtime_body = {
        "schema": "rtdl.goal5791.formal_runtime.v1",
        "goal": 5791,
        "status": "TARGET_PREPARED__FORMAL_AUTHORITY_STILL_REQUIRED",
        "formal_contract_sha256": contract.contract_sha256(),
        "schedule_sha256": contract.schedule_sha256(),
        "preexecution_authority_file_sha256": _sha(post_path),
        "target_materialization_binding_sha256": binding["binding_sha256"],
        "formal_identity_sha256": formal_identity,
        "runtime_budget_authority_sha256": contract.RUNTIME_BUDGET_AUTHORITY_FILE_SHA256,
        "execution_source_root": str(source),
        "execution_source_manifest_path": str(source / SOURCE_MANIFEST_MEMBER),
        "execution_source_manifest_file_sha256": _sha(
            source / SOURCE_MANIFEST_MEMBER),
        "formal_identity_record": formal_identity_record,
        "python_executable": str(python),
        "python_executable_sha256": _sha(python),
        "python_version": identity["python"],
        "numba_version": identity["numba"],
        "numpy_version": identity["numpy"],
        "llvmlite_version": identity["llvmlite"],
        "cupy_version": identity["cupy"],
        "native_library_path": str(native),
        "native_library_sha256": native_sha,
        "optix_include": str(optix_include),
        "cuda_include": str(cuda_include),
        "compute_capability": "8.9",
        "optix_sdk_version": "9.0.0",
        "shared_contract_freeze_path": str(source / SHARED_FREEZE_MEMBER),
        "shared_contract_freeze_file_sha256": _sha(source / SHARED_FREEZE_MEMBER),
        "target_materialization_authority_path": str(product_authority_path),
        "target_materialization_authority_file_sha256": _sha(product_authority_path),
        "max_relation_rows": 1_000_000,
        "datasets": datasets,
        "neutral_prewarm": {
            "edge_path": str(k4),
            "input_sha256": k4_sha,
            "size_bytes": k4.stat().st_size,
            "expected_triangle_count": 4,
            "purpose": "recipe_jit_cache_neutralization_only",
            "formal_input": False,
            "variant_order": ["fusion_off", "fusion_on"],
        },
        "formal_worker_environment": formal_environment,
        "worker_timeout_seconds": float(worker_timeout_seconds),
        "formal_conservative_budget_seconds": float(
            frozen_runtime_budget["formal_conservative_budget_seconds"]),
    }
    runtime = {**runtime_body, "runtime_sha256": _digest(runtime_body)}
    runtime_path = result / "RUNTIME.json"
    _write_json_create_only(runtime_path, runtime)

    # Seal the exact runtime before any owner Stage-B authority can exist.
    # Stage B must pin both the resulting file hash and the embedded runtime
    # seal; neither paths, environment, timeout, nor any other runtime field
    # may be edited/resealed after that owner authorization is created.
    source_set_before_seal = _audit_exact_source_set(
        source, source_manifest,
        manifest_file_sha256=source_manifest_file_sha,
        require_read_only=False,
    )
    for path in list(data_paths.values()) + [
        k4, product_authority_path, binding_path, post_path,
        functional_summary_path, dependency_lock_path, target_evidence_path,
        source_archive, runtime_path, native,
        owner_prepare_authority_path,
    ]:
        path.chmod(path.stat().st_mode & ~0o222)
    _remove_write_bits(data_root)
    _remove_write_bits(wheelhouse)
    _normalize_and_seal_venv(venv)
    _remove_write_bits(source)
    _remove_write_bits(native_root)
    source_set_after_seal = _audit_exact_source_set(
        source, source_manifest,
        manifest_file_sha256=source_manifest_file_sha,
        require_read_only=True,
    )
    source_policy = contract.SOURCE_ADMISSION_POLICY
    if source_policy != {
        "portable_manifest_is_non_self_referential": True,
        "expected_regular_file_set": "manifest_rows_plus_manifest_itself",
        "expected_directory_set": "root_plus_parents_implied_by_expected_files",
        "controller_full_rehash_and_exact_set_before_worker_zero": True,
        "every_worker_full_rehash_and_exact_set_before_product_import": True,
        "all_source_paths_without_write_bits_required": True,
        "extra_missing_symlink_reparse_or_special_paths_allowed": False,
        "worker_source_rehash_receipt_required": True,
        "same_host_malicious_root_race_excluded": False,
        "tcb_boundary": "does_not_exclude_a_malicious_same_host_root_race",
    }:
        raise PrepareError("Goal5791 source admission policy drifted")
    shutil.copy2(native, result / "librtdl_optix.so")
    (result / "librtdl_optix.so").chmod(
        (result / "librtdl_optix.so").stat().st_mode & ~0o222)

    receipt_body = {
        "schema": "rtdl.goal5791.create_only_target_prepare_result.v1",
        "status": "PASS__TARGET_PREPARED__STAGE_B_OWNER_AUTHORITY_ABSENT",
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": source_sha,
        "source_tree_sha256": source_manifest["source_tree_sha256"],
        "data_bundle_sha256": EXPECTED_DATA_SHA256,
        "wheelhouse_sha256": EXPECTED_WHEELHOUSE_SHA256,
        "optix_headers_sha256": EXPECTED_OPTIX_HEADERS_SHA256,
        "native_library_sha256": native_sha,
        "target_identity_sha256": inspection["target_identity_sha256"],
        "runtime_identity_sha256": runtime_identity,
        "prepared_identity_sha256": prepared_identity,
        "prepared_identity_record": prepared_identity_record,
        "formal_identity_sha256": formal_identity,
        "target_materialization_binding_sha256": binding["binding_sha256"],
        "target_materialization_authority_file_sha256": _sha(
            product_authority_path),
        "target_evidence_archive_file_sha256": _sha(target_evidence_path),
        "target_functional_summary_file_sha256": _sha(
            functional_summary_path),
        "postprepare_preexecution_authority_file_sha256": _sha(post_path),
        "runtime_file_sha256": _sha(runtime_path),
        "runtime_sha256": runtime["runtime_sha256"],
        "owner_target_prepare_authority_file_sha256": _sha(
            owner_prepare_authority_path),
        "pod_endpoint": pod_endpoint,
        "target_materialization_root": str(root),
        "target_materialization_root_observed_absent_before_creation": (
            materialization_root_absence_observed_at_entry),
        "target_materialization_root_created_by_target_prepare": True,
        "target_materialization_parent_resolved_path": str(
            materialization_parent),
        "target_materialization_parent_free_bytes_observed_before_creation": (
            observed_free_bytes),
        "target_materialization_required_free_disk_bytes": required_free_bytes,
        "target_materialization_capacity_admitted_before_creation": True,
        "target_materialization_resource_admission": resource_admission,
        "target_materialization_resource_admission_sha256": (
            resource_admission["resource_admission_sha256"]),
        "upload_staging_root": str(upload_staging_root),
        "upload_staging_identity": staging_identity,
        "upload_staging_identity_sha256": staging_identity[
            "upload_staging_identity_sha256"],
        "upload_staging_cleanup_disposition": (
            UPLOAD_STAGING_CLEANUP_DISPOSITION),
        "upload_staging_cleanup_completed_by_target_prepare": False,
        "runtime_read_only_before_owner_stage_b": (
            runtime_path.stat().st_mode & 0o222) == 0,
        "owner_stage_b_must_pin_exact_runtime_file_and_runtime_sha256": True,
        "runtime_reseal_after_owner_stage_b_allowed": False,
        "source_exact_set_after_prepare_and_functional_smoke": (
            source_set_before_seal),
        "source_exact_set_and_all_tree_paths_read_only": source_set_after_seal,
        "source_admission_policy_sha256": _digest(source_policy),
        "target_functional_lane_count": 4,
        "target_functional_exact_lane_count": 4,
        "target_functional_behavioral_true_optix_lane_count": 4,
        "target_functional_token_only_lane_count": 4,
        "target_ptx_producer_observation_file_sha256": _sha(
            producer_observation_path),
        "target_ptx_producer_trace_sha256": _sha(producer_trace),
        "target_ptx_producer_audit": producer_audit,
        "target_native_build_producer_audit": native_build_audit,
        "prepare_cupy_cache_payloads_removed_after_validation": True,
        "fusion_off_event_count_per_segment": 7,
        "fusion_on_event_count_per_segment": 2,
        "scheduled_data_members_extracted": sorted(data_paths),
        "unscheduled_data_member_bytes_opened": False,
        "scheduled_data_files_read_only": True,
        "runtime_native_file_and_parent_read_only": True,
        "operating_system_page_cache_controlled_or_dropped": (
            contract.CACHE_POLICY[
                "operating_system_page_cache_controlled_or_dropped"]),
        "operating_system_page_cache_scope": contract.CACHE_POLICY[
            "operating_system_page_cache_scope"],
        "preworker_full_rehash_can_warm_operating_system_page_cache": (
            contract.CACHE_POLICY[
                "preworker_full_rehash_can_warm_operating_system_page_cache"]),
        "cache_policy": deepcopy(contract.CACHE_POLICY),
        "cache_policy_sha256": _digest(contract.CACHE_POLICY),
        "cold_definition": contract.CACHE_POLICY["cold_definition"],
        "cold_claim_excludes": contract.CACHE_POLICY["cold_claim_excludes"],
        "cuda_driver_jit_cache_controlled_or_isolated": (
            contract.CACHE_POLICY[
                "cuda_driver_jit_cache_controlled_or_isolated"]),
        "optix_disk_cache_controlled_or_isolated": contract.CACHE_POLICY[
            "optix_disk_cache_controlled_or_isolated"],
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            contract.CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"]),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "owner_stage_b_formal_authority_created": False,
        "formal_execution_authorized": False,
        "performance_or_compiler_fusion_claimed": False,
    }
    receipt = {**receipt_body, "receipt_sha256": _digest(receipt_body)}
    prepared_result_path = result / "PREPARED.json"
    _write_json_create_only(prepared_result_path, receipt)
    prepared_result_path.chmod(prepared_result_path.stat().st_mode & ~0o222)
    if prepared_result_path.stat().st_mode & 0o222:
        raise PrepareError("Goal5791 PREPARED receipt did not seal read-only")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
