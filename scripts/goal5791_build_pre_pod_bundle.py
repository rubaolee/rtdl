#!/usr/bin/env python3
"""Build the deterministic Goal5791 pre-POD packet and byte-identical twin.

The packet contains the already frozen native-free source, frozen authorities,
reviewable harness bytes, and the exact fresh Home functional closure.  It
contains no real data, wheelhouse, OptiX headers, target native, owner
authority, formal worker output, registered timing, or credential.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from scripts import goal5791_build_portable_source as source_builder
from scripts import goal5791_formal_contract as contract
from scripts import goal5791_independent_portable_audit as independent_audit
from scripts.goal5791_home_clean_validate import (
    HOME_EVIDENCE_BOUND_CLOSURE_KEYS,
    HOME_FUNCTIONAL_CLOSURE_KEYS,
)


SOURCE_MANIFEST_MEMBER = source_builder.NEW_MANIFEST
PRETARGET_PATH = (
    "history/internal_docs/"
    "goal5791_pretarget_preexecution_authority_v9_20260820.json"
)
PREREGISTRATION_PATH = (
    "history/internal_docs/goal5791_preregistration_v9_20260820.json"
)
SOURCE_AUTHORITY_PATH = (
    "history/internal_docs/goal5791_successor_source_authority_v2_20260817.json"
)
CLAIM_FREEZE_PATH = (
    "history/internal_docs/"
    "goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json"
)
EXPECTED_VALUE_PATH = (
    "history/internal_docs/"
    "goal5790_preregistered_expected_value_and_fallback_20260816.json"
)
RUNTIME_BUDGET_PATH = (
    "history/internal_docs/"
    "goal5791_pre_pod_conservative_runtime_budget_20260817.json"
)
SHARED_FREEZE_PATH = (
    "history/internal_docs/goal5789_contract_evidence_20260816/"
    "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json"
)
A1_RESULT_PATH = (
    "history/internal_docs/"
    "goal5791_amendment_a1_pretimer_fusion_execution_token_result_20260817.json"
)
A2_RESULT_PATH = (
    "history/internal_docs/"
    "goal5791_amendment_a2_segment_plan_input_token_binding_result_20260817.json"
)
V4_LINEAGE_AUTHORITY_PATH = (
    "history/internal_docs/"
    "goal5791_v4_successor_lineage_authority_20260817.json"
)
EXTERNAL_UPLOADS = {
    "data_bundle_sha256": (
        "f186cd28a5ae767f968eaa1372cd66285934be430bceb77ff14c6cf94e33e6eb"),
    "wheelhouse_sha256": (
        "d0c0f75365a78792cf0c2f548e0bdd144f0ad7175e0d8f83efcf335eb3b311f3"),
    "optix_headers_sha256": (
        "7fae86ce3dca2fbc2a47be075f02465cf6ee9d9eafd204234f2882fbdeebee54"),
}
CANONICAL_STAGED_BUNDLE_BASENAME = "GOAL5791_PRE_POD_BUNDLE.tar.gz"
HARNESS_MEMBERS = {
    "HARNESS/CLEAN_VALIDATE.py": "scripts/goal5791_home_clean_validate.py",
    "HARNESS/HOME_TOKEN_WORKER.py": (
        "scripts/goal5791_home_token_validation.py"),
    "HARNESS/HOME_INDEPENDENT_RECOUNT.py": (
        "scripts/goal5791_independent_home_recount.py"),
    "HARNESS/INDEPENDENT_PORTABLE_AUDIT.py": (
        "scripts/goal5791_independent_portable_audit.py"),
    "HARNESS/TARGET_PREPARE.py": "scripts/goal5791_target_prepare.py",
    "HARNESS/TARGET_PRODUCER_PROBE.py": (
        "scripts/goal5791_target_producer_probe.py"),
    "HARNESS/OPEN_UPLOAD_STAGING.py": (
        "scripts/goal5791_open_upload_staging.py"),
    "HARNESS/OWNER_AUTHORITY_BUILDER.py": (
        "scripts/goal5791_build_owner_authority.py"),
    "HARNESS/FORMAL_CONTROLLER.py": "scripts/goal5791_formal_controller.py",
    "HARNESS/FORMAL_WORKER.py": "scripts/goal5791_formal_worker.py",
    "HARNESS/EVALUATE.py": "scripts/goal5791_formal_evaluate.py",
    "HARNESS/INDEPENDENT_RECOUNT.py": (
        "scripts/goal5791_formal_independent_recount.py"),
}
OUTER_TO_SOURCE_AUTHORITY_MEMBERS = {
    "CLAIM_AND_RELATED_WORK_FREEZE.json": CLAIM_FREEZE_PATH,
    "EXPECTED_VALUE_AND_FALLBACK.json": EXPECTED_VALUE_PATH,
    "PREREGISTRATION.json": PREREGISTRATION_PATH,
    "PRETARGET_PREEXECUTION_AUTHORITY.json": PRETARGET_PATH,
    "RUNTIME_BUDGET.json": RUNTIME_BUDGET_PATH,
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
    BUNDLE_FIXED_PAYLOAD_MEMBERS | frozenset(HARNESS_MEMBERS)
)
EXPECTED_BUNDLE_OUTER_MEMBERS = (
    EXPECTED_BUNDLE_PAYLOAD_MEMBERS | {"BUNDLE_MANIFEST.json"}
)
SOURCE_RECEIPT_KEYS = frozenset({
    "schema", "goal", "status", "base_source_archive_path",
    "base_source_archive_sha256", "base_source_manifest_sha256",
    "base_source_tree_sha256", "base_manifest_rehashed", "output_path",
    "preserved_base_manifest_member", "preserved_base_manifest_sha256",
    "twin_path", "source_archive_sha256", "source_archive_bytes",
    "source_twin_sha256", "source_twin_byte_identical",
    "source_manifest_member", "source_manifest_sha256",
    "source_manifest_non_self_referential", "source_tree_sha256",
    "source_file_count_excluding_manifest",
    "archive_payload_count_including_manifest", "archive_payload_bytes",
    "builder_path", "builder_sha256", "overlay_sha256", "product_delta",
    "changed_product_file_count", "changed_native_file_count",
    "deep_blob_audit", "unsafe_member_count",
    "prebuilt_native_or_device_binary_count", "nested_container_count",
    "private_cache_member_count", "empty_directory_extract_rehash_passed",
    "clean_extraction_exact_set_before_tests",
    "clean_extraction_exact_set_after_tests", "cpu_test_gate_helper_member",
    "cpu_test_gate_helper_sha256", "workspace_cpu_test_gate_result",
    "clean_cpu_test_gate_result", "cpu_test_timeout_seconds",
    "home_or_target_execution_count", "gpu_execution_count",
    "pod_execution_count", "formal_worker_count",
    "registered_performance_timing_count", "reported_elapsed_value_count",
    "test_or_scientific_clock_sample_count",
    "operational_timeout_watchdog_uses_host_clock",
    "operational_watchdog_clock_not_persisted_or_registered",
    "home_performance_observation_created",
    "home_performance_diagnostic_used",
    "requires_fresh_home_token_path_qualification",
    "requires_separate_owner_target_prepare_authority",
    "requires_separate_postprepare_owner_formal_authority",
    "performance_or_compiler_fusion_claimed",
})
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


class BundleError(RuntimeError):
    pass


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_home_performance_observations(
    value: object, *, label: str,
) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            folded = key.casefold()
            if key in _HOME_ZERO_COUNT_KEYS:
                if type(item) is not int or item != 0:
                    raise BundleError(
                        f"Home observation count is not exact zero: "
                        f"{label}.{key}")
            elif key in _HOME_FALSE_OBSERVATION_KEYS:
                if item is not False:
                    raise BundleError(
                        f"Home observation marker is not false: "
                        f"{label}.{key}")
            elif key in _HOME_TRUE_OPERATIONAL_CLOCK_KEYS:
                if item is not True:
                    raise BundleError(
                        f"operational watchdog disclosure is not true: "
                        f"{label}.{key}")
            elif key in _SOURCE_OPERATIONAL_TIMEOUT_FIELDS:
                if type(item) is not int \
                        or item != _SOURCE_OPERATIONAL_TIMEOUT_FIELDS[key]:
                    raise BundleError(
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
                    raise BundleError(
                        "source overlay digest map shape drifted")
                # These keys are exact source member paths and may contain
                # words such as "pretimer".  The complete map is compared
                # with the independently reconstructed source overlay below.
                continue
            elif key == "timer_contract_sha256":
                if item != contract.digest(_HOME_TIMER_CONTRACT):
                    raise BundleError(
                        f"Home zero-observation contract digest drifted: "
                        f"{label}.{key}")
            elif any(token in folded
                     for token in _HOME_FORBIDDEN_OBSERVATION_KEY_TOKENS) \
                    or folded.endswith(
                        _HOME_FORBIDDEN_OBSERVATION_KEY_SUFFIXES):
                raise BundleError(
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
        raise BundleError(
            "Goal5791 bundle outer membership is not the frozen exact set: "
            f"missing={sorted(EXPECTED_BUNDLE_OUTER_MEMBERS - actual)!r}, "
            f"extra={sorted(actual - EXPECTED_BUNDLE_OUTER_MEMBERS)!r}"
        )


def _strict_json(path: Path) -> dict[str, object]:
    def pairs(rows):
        value: dict[str, object] = {}
        for key, item in rows:
            if key in value:
                raise BundleError(f"duplicate JSON key in {path}: {key}")
            value[key] = item
        return value

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(
            BundleError(f"non-finite JSON constant: {token}")),
    )
    if not isinstance(value, dict):
        raise BundleError(f"expected one JSON object: {path}")
    return value


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def _validate_source_cpu_gate_binding(
    receipt: dict[str, object], *, source_payloads: dict[str, bytes],
) -> None:
    if receipt.get("schema") \
            != "rtdl.goal5791.portable_source_build_receipt.v26" \
            or type(receipt.get("cpu_test_timeout_seconds")) is not int \
            or receipt.get("cpu_test_timeout_seconds") \
                != source_builder.CPU_TEST_TIMEOUT_SECONDS:
        raise BundleError("Goal5791 source CPU gate timeout binding drifted")
    try:
        independent_audit._validate_source_receipt_governance(
            receipt,
            builder_bytes=source_payloads[source_builder.BUILDER_MEMBER],
            helper_bytes=source_payloads[source_builder.CPU_TEST_GATE_MEMBER],
        )
    except (KeyError, independent_audit.IndependentPortableAuditError) as exc:
        raise BundleError("Goal5791 source CPU gate binding drifted") from exc
    empty_outcomes = {
        "failures": [], "errors": [], "skipped": [],
        "expectedFailures": [], "unexpectedSuccesses": [],
    }
    for field, scope in (
        ("workspace_cpu_test_gate_result", "workspace"),
        ("clean_cpu_test_gate_result", "clean"),
    ):
        gate = receipt.get(field)
        if not isinstance(gate, dict) \
                or gate.get("schema") \
                    != "rtdl.goal5791.cpu_test_gate_result.v2" \
                or gate.get("scope") != scope \
                or gate.get("outcome_test_ids") != empty_outcomes \
                or gate.get("outcome_test_ids_sha256") \
                    != independent_audit._digest(empty_outcomes) \
                or gate.get("failure_test_ids") != [] \
                or gate.get("error_test_ids") != [] \
                or gate.get("failure_exception_summaries") != [] \
                or gate.get("error_exception_summaries") != [] \
                or gate.get("success") is not True:
            raise BundleError(
                "Goal5791 successful source CPU outcome evidence drifted")


def _source(
    source_archive: Path, source_twin: Path, source_receipt: Path,
    source_independent_audit: Path,
) -> tuple[bytes, dict[str, object], dict[str, bytes], dict[str, object]]:
    archive_bytes = source_archive.read_bytes()
    twin_bytes = source_twin.read_bytes()
    if twin_bytes != archive_bytes:
        raise BundleError("Goal5791 portable source/twin bytes differ")
    receipt = _strict_json(source_receipt)
    _reject_home_performance_observations(
        receipt, label="SOURCE_BASE_AND_OVERLAY_AUTHORITY.json")
    if set(receipt) != SOURCE_RECEIPT_KEYS \
            or receipt.get("schema") \
            != "rtdl.goal5791.portable_source_build_receipt.v26" \
            or receipt.get("goal") != 5791 \
            or receipt.get("base_source_archive_path") \
                != "history/internal_docs/goal5790_a1_portable_source_v4_20260816.tar.gz" \
            or receipt.get("output_path") \
                != source_builder.CANONICAL_OUTPUT_PATH \
            or receipt.get("twin_path") \
                != source_builder.CANONICAL_TWIN_PATH \
            or receipt.get("source_archive_sha256") != _sha_bytes(archive_bytes) \
            or receipt.get("source_archive_bytes") != len(archive_bytes) \
            or receipt.get("source_twin_sha256") != _sha_bytes(twin_bytes) \
            or receipt.get("source_twin_byte_identical") is not True \
            or receipt.get("base_source_archive_sha256") \
                != source_builder.BASE_SOURCE_SHA256 \
            or receipt.get("base_source_manifest_sha256") \
                != source_builder.BASE_MANIFEST_SHA256 \
            or receipt.get("base_source_tree_sha256") \
                != source_builder.BASE_TREE_SHA256 \
            or receipt.get("base_manifest_rehashed") is not True \
            or receipt.get("preserved_base_manifest_member") \
                != source_builder.PRESERVED_BASE_MANIFEST_MEMBER \
            or receipt.get("preserved_base_manifest_sha256") \
                != source_builder.BASE_MANIFEST_SHA256 \
            or receipt.get("prebuilt_native_or_device_binary_count") != 0 \
            or receipt.get("nested_container_count") != 0 \
            or receipt.get("unsafe_member_count") != 0 \
            or receipt.get("private_cache_member_count") != 0 \
            or receipt.get("changed_product_file_count") \
                != len(source_builder.PRODUCT_DELTA) \
            or receipt.get("changed_native_file_count") != 0 \
            or type(receipt.get("cpu_test_timeout_seconds")) is not int \
            or receipt.get("cpu_test_timeout_seconds") \
                != source_builder.CPU_TEST_TIMEOUT_SECONDS \
            or receipt.get("home_or_target_execution_count") != 0 \
            or receipt.get("gpu_execution_count") != 0 \
            or receipt.get("pod_execution_count") != 0 \
            or receipt.get("formal_worker_count") != 0 \
            or type(receipt.get("registered_performance_timing_count")) is not int \
            or receipt.get("registered_performance_timing_count") != 0 \
            or type(receipt.get("reported_elapsed_value_count")) is not int \
            or receipt.get("reported_elapsed_value_count") != 0 \
            or type(receipt.get(
                "test_or_scientific_clock_sample_count")) is not int \
            or receipt.get("test_or_scientific_clock_sample_count") != 0 \
            or receipt.get(
                "operational_timeout_watchdog_uses_host_clock") is not True \
            or receipt.get(
                "operational_watchdog_clock_not_persisted_or_registered") \
                is not True \
            or receipt.get("home_performance_observation_created") is not False \
            or receipt.get("home_performance_diagnostic_used") is not False \
            or receipt.get("performance_or_compiler_fusion_claimed") is not False:
        raise BundleError("Goal5791 portable source receipt drifted")
    payloads = source_builder._read_archive(archive_bytes)
    _validate_source_cpu_gate_binding(receipt, source_payloads=payloads)
    manifest_bytes = payloads.get(SOURCE_MANIFEST_MEMBER)
    if manifest_bytes is None:
        raise BundleError("Goal5791 source manifest is absent")
    manifest = json.loads(manifest_bytes)
    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise BundleError("Goal5791 source manifest rows are absent")
    expected = {
        str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
        for row in rows
    }
    actual = {
        name: (len(data), _sha_bytes(data)) for name, data in payloads.items()
        if name != SOURCE_MANIFEST_MEMBER
    }
    if len(expected) != len(rows) or expected != actual \
            or manifest.get("source_tree_sha256") \
                != source_builder._tree_sha(source_builder._canonical_rows({
                    name: data for name, data in payloads.items()
                    if name != SOURCE_MANIFEST_MEMBER
                })) \
            or receipt.get("source_tree_sha256") \
                != manifest.get("source_tree_sha256") \
            or receipt.get("source_manifest_sha256") \
                != _sha_bytes(manifest_bytes):
        raise BundleError("Goal5791 portable source does not independently rehash")
    without_manifest = {
        name: data for name, data in payloads.items()
        if name != SOURCE_MANIFEST_MEMBER
    }
    deep = source_builder._deep_audit(without_manifest)
    expected_overlay = {
        name: _sha_bytes(payloads[name])
        for name in sorted(
            set(source_builder.OVERLAY_PATHS) | {source_builder.BUILDER_MEMBER})
    }
    if receipt.get("source_manifest_member") != SOURCE_MANIFEST_MEMBER \
            or receipt.get("source_manifest_non_self_referential") is not True \
            or receipt.get("source_file_count_excluding_manifest") \
                != len(without_manifest) \
            or receipt.get("archive_payload_count_including_manifest") \
                != len(payloads) \
            or receipt.get("archive_payload_bytes") \
                != sum(len(data) for data in payloads.values()) \
            or receipt.get("builder_path") != source_builder.BUILDER_MEMBER \
            or receipt.get("builder_sha256") \
                != _sha_bytes(payloads[source_builder.BUILDER_MEMBER]) \
            or receipt.get("overlay_sha256") != expected_overlay \
            or receipt.get("product_delta") != source_builder.PRODUCT_DELTA \
            or receipt.get("deep_blob_audit") != deep \
            or receipt.get("empty_directory_extract_rehash_passed") is not True:
        raise BundleError("Goal5791 portable source receipt cross-binding drifted")
    with tempfile.TemporaryDirectory(prefix="goal5791_bundle_source_reaudit_") as temp:
        extracted = Path(temp) / "source"
        source_builder._extract(payloads, extracted)
        exact_set = source_builder._audit_extracted_exact_set(
            extracted, payloads)
    if receipt.get("clean_extraction_exact_set_before_tests") != exact_set \
            or receipt.get("clean_extraction_exact_set_after_tests") != exact_set:
        raise BundleError("Goal5791 source clean-extraction receipt drifted")
    _validate_source_cpu_gate_binding(receipt, source_payloads=payloads)
    source_audit = _strict_json(source_independent_audit)
    _reject_home_performance_observations(
        source_audit, label="SOURCE_INDEPENDENT_AUDIT.json")
    independent_audit._require_goal_5791(
        source_audit, label="SOURCE_INDEPENDENT_AUDIT.json")
    recomputed_audit = independent_audit.audit_source(archive_bytes)
    expected_source_audit_keys = set(recomputed_audit) | {
        "schema", "goal", "status", "kind", "twin_sha256",
        "twin_byte_identical", "implementation_imports_primary_builder",
        "home_or_target_execution_count", "pod_execution_count",
    }
    if set(source_audit) != expected_source_audit_keys \
            or source_audit.get("schema") \
            != "rtdl.goal5791.independent_portable_audit.v1" \
            or source_audit.get("status") \
                != "PASS__INDEPENDENT_DEEP_ARCHIVE_AND_TWIN_AUDIT" \
            or source_audit.get("kind") != "source" \
            or source_audit.get("goal") != 5791 \
            or source_audit.get("archive_sha256") != _sha_bytes(archive_bytes) \
            or source_audit.get("twin_sha256") != _sha_bytes(twin_bytes) \
            or source_audit.get("twin_byte_identical") is not True \
            or source_audit.get("implementation_imports_primary_builder") is not False \
            or source_audit.get("home_or_target_execution_count") != 0 \
            or source_audit.get("pod_execution_count") != 0 \
            or any(source_audit.get(key) != value
                   for key, value in recomputed_audit.items()):
        raise BundleError("Goal5791 independent source audit chain drifted")
    return archive_bytes, receipt, payloads, manifest


def _home_chain(
    *, home_result: Path, home_evidence: Path, home_evidence_twin: Path,
    home_evidence_independent_audit: Path, source_bytes: bytes,
    source_payloads: dict[str, bytes], source_tree_sha256: str,
    source_manifest_sha256: str,
) -> tuple[dict[str, object], dict[str, object], bytes, bytes]:
    home = _strict_json(home_result)
    if set(home) != HOME_FUNCTIONAL_CLOSURE_KEYS:
        raise BundleError("Goal5791 Home closure exact key set drifted")
    _reject_home_performance_observations(
        home, label="HOME_FUNCTIONAL_CLOSURE.json")
    evidence_bytes = home_evidence.read_bytes()
    twin_bytes = home_evidence_twin.read_bytes()
    if evidence_bytes != twin_bytes:
        raise BundleError("Goal5791 Home evidence/twin bytes differ")
    evidence_audit = _strict_json(home_evidence_independent_audit)
    _reject_home_performance_observations(
        evidence_audit, label="HOME_EVIDENCE_INDEPENDENT_AUDIT.json")
    recomputed_audit = independent_audit.audit_home_evidence(evidence_bytes)
    expected_audit_keys = set(recomputed_audit) | {
        "schema", "goal", "status", "kind", "twin_sha256",
        "twin_byte_identical", "implementation_imports_primary_builder",
        "home_or_target_execution_count", "pod_execution_count",
    }
    if set(evidence_audit) != expected_audit_keys \
            or evidence_audit.get("schema") \
                != "rtdl.goal5791.independent_portable_audit.v1" \
            or evidence_audit.get("status") \
                != "PASS__INDEPENDENT_DEEP_ARCHIVE_AND_TWIN_AUDIT" \
            or evidence_audit.get("kind") != "home-evidence" \
            or evidence_audit.get("twin_sha256") != _sha_bytes(twin_bytes) \
            or evidence_audit.get("twin_byte_identical") is not True \
            or evidence_audit.get("implementation_imports_primary_builder") is not False \
            or evidence_audit.get("home_or_target_execution_count") != 0 \
            or evidence_audit.get("pod_execution_count") != 0 \
            or any(evidence_audit.get(key) != value
                   for key, value in recomputed_audit.items()):
        raise BundleError("Goal5791 Home independent evidence audit drifted")
    evidence_payloads = independent_audit._archive(
        evidence_bytes, label="bundle Home evidence", source=False)
    evidence_manifest = independent_audit._strict_json_bytes(
        evidence_payloads["EVIDENCE_MANIFEST.json"],
        "EVIDENCE_MANIFEST.json",
    )
    recount = independent_audit._strict_json_bytes(
        evidence_payloads["FUNCTIONAL_RECOUNT.json"],
        "FUNCTIONAL_RECOUNT.json",
    )
    target_authority = independent_audit._strict_json_bytes(
        evidence_payloads["TARGET_MATERIALIZATION_AUTHORITY.json"],
        "TARGET_MATERIALIZATION_AUTHORITY.json",
    )
    inspection = independent_audit._strict_json_bytes(
        evidence_payloads["TARGET_PROGRAM_INSPECTION.json"],
        "TARGET_PROGRAM_INSPECTION.json",
    )
    source_sha256 = _sha_bytes(source_bytes)
    native_sha256 = _sha_bytes(
        evidence_payloads["TARGET_NATIVE/librtdl_optix.so"])
    evidence_bound_facts = evidence_manifest.get("home_functional_facts")
    if not isinstance(evidence_bound_facts, dict) \
            or set(evidence_bound_facts) != HOME_EVIDENCE_BOUND_CLOSURE_KEYS \
            or any(home.get(key) != value
                   for key, value in evidence_bound_facts.items()):
        raise BundleError(
            "Goal5791 Home closure differs from evidence-bound facts")
    expected_zero_counts = {
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
    }
    if home.get("schema") \
            != "rtdl.goal5791.home_token_functional_closure.v1" \
            or home.get("status") \
                != "PASS__10_OF_10_TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX" \
            or home.get("execution_source_archive_sha256") != source_sha256 \
            or home.get("execution_source_tree_sha256") != source_tree_sha256 \
            or home.get("source_manifest_sha256") != source_manifest_sha256 \
            or home.get("native_library_sha256") != native_sha256 \
            or home.get("home_evidence_sha256") != _sha_bytes(evidence_bytes) \
            or home.get("home_evidence_twin_sha256") != _sha_bytes(twin_bytes) \
            or home.get("home_evidence_twin_byte_identical") is not True \
            or home.get("home_evidence_manifest_sha256") \
                != _sha_bytes(evidence_payloads["EVIDENCE_MANIFEST.json"]) \
            or home.get("home_evidence_independent_audit_sha256") \
                != _sha(home_evidence_independent_audit) \
            or home.get("home_evidence_payload_count") != len(evidence_payloads) \
            or home.get("target_materialization_receipt_sha256") \
                != target_authority.get("receipt_sha256") \
            or home.get("target_materialization_evidence_sha256") \
                != _sha_bytes(evidence_payloads[
                    "TARGET_MATERIALIZATION_EVIDENCE.tar.gz"]) \
            or home.get("ptx_program_identity_sha256") \
                != inspection.get("ptx_program_identity_sha256") \
            or home.get("exact_lane_count") != 10 \
            or home.get("behavioral_true_optix_lane_count") != 10 \
            or home.get("token_only_lane_count") != 10 \
            or home.get("pod_used") is not False \
            or any(home.get(key) != value
                   for key, value in expected_zero_counts.items()):
        raise BundleError("Goal5791 Home closure/evidence chain drifted")
    if evidence_manifest.get("execution_source_archive_sha256") != source_sha256 \
            or evidence_manifest.get("execution_source_tree_sha256") \
                != source_tree_sha256 \
            or evidence_manifest.get("source_manifest_sha256") \
                != source_manifest_sha256 \
            or evidence_manifest.get("native_library_sha256") != native_sha256 \
            or evidence_manifest.get("functional_recount_sha256") \
                != _sha_bytes(evidence_payloads["FUNCTIONAL_RECOUNT.json"]):
        raise BundleError("Goal5791 Home evidence manifest cross-binding drifted")
    for key in (
        "exact_lane_count", "behavioral_true_optix_lane_count",
        "token_only_lane_count", "fresh_parent_pid_count",
        "operation_receipt_count", "successful_operation_event_count_by_variant",
        "target_materialization_receipt_sha256",
        "ptx_program_identity_sha256",
    ):
        if home.get(key) != recount.get(key):
            raise BundleError(f"Goal5791 Home/recount field drifted: {key}")
    with tempfile.TemporaryDirectory(prefix="goal5791_home_recount_replay_") as temp:
        temp_root = Path(temp)
        extracted_source = temp_root / "source"
        extracted_home = temp_root / "home"
        source_builder._extract(source_payloads, extracted_source)
        source_builder._extract(evidence_payloads, extracted_home)
        replay = temp_root / "FUNCTIONAL_RECOUNT_REPLAY.json"
        environment = dict(os.environ)
        environment.update({
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": os.pathsep.join((
                str(extracted_source / "src"), str(extracted_source))),
        })
        completed = subprocess.run([
            sys.executable,
            str(extracted_source /
                "scripts/goal5791_independent_home_recount.py"),
            "--raw", str(extracted_home / "RAW"),
            "--inputs", str(extracted_home / "INPUTS"),
            "--expected-source-archive-sha256", source_sha256,
            "--expected-source-tree-sha256", source_tree_sha256,
            "--expected-native-sha256", native_sha256,
            "--output", str(replay),
        ], cwd=extracted_source, env=environment, text=True,
            encoding="utf-8", errors="replace", stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=600, check=False)
        if completed.returncode != 0 \
                or replay.read_bytes() \
                    != evidence_payloads["FUNCTIONAL_RECOUNT.json"]:
            raise BundleError(
                "Goal5791 exact independent Home recount replay drifted: "
                + completed.stdout[-4000:])
    return home, {
        "home_evidence_sha256": _sha_bytes(evidence_bytes),
        "home_evidence_twin_sha256": _sha_bytes(twin_bytes),
        "home_evidence_independent_audit_file_sha256": _sha(
            home_evidence_independent_audit),
        "home_evidence_manifest_sha256": _sha_bytes(
            evidence_payloads["EVIDENCE_MANIFEST.json"]),
        "home_functional_recount_sha256": _sha_bytes(
            evidence_payloads["FUNCTIONAL_RECOUNT.json"]),
        "home_target_materialization_authority_sha256": _sha_bytes(
            evidence_payloads["TARGET_MATERIALIZATION_AUTHORITY.json"]),
        "home_target_materialization_evidence_sha256": _sha_bytes(
            evidence_payloads["TARGET_MATERIALIZATION_EVIDENCE.tar.gz"]),
        "home_target_program_inspection_sha256": _sha_bytes(
            evidence_payloads["TARGET_PROGRAM_INSPECTION.json"]),
        "home_independent_recount_reexecuted_and_byte_identical": True,
    }, evidence_payloads["FUNCTIONAL_RECOUNT.json"], \
        evidence_payloads["EVIDENCE_MANIFEST.json"]


def _semantic_authority(
    *, source_archive_sha256: str, source_tree_sha256: str,
    source_manifest_sha256: str, home: dict[str, object],
    source_payloads: dict[str, bytes],
) -> bytes:
    shared_bytes = source_payloads[SHARED_FREEZE_PATH]
    source_policy_bytes = source_payloads[SOURCE_AUTHORITY_PATH]
    a1_bytes = source_payloads[A1_RESULT_PATH]
    a2_bytes = source_payloads[A2_RESULT_PATH]
    lineage_bytes = source_payloads[V4_LINEAGE_AUTHORITY_PATH]
    shared = independent_audit._strict_json_bytes(
        shared_bytes, SHARED_FREEZE_PATH)
    source_policy = independent_audit._strict_json_bytes(
        source_policy_bytes, SOURCE_AUTHORITY_PATH)
    a1 = independent_audit._strict_json_bytes(a1_bytes, A1_RESULT_PATH)
    a2 = independent_audit._strict_json_bytes(a2_bytes, A2_RESULT_PATH)
    lineage = independent_audit._strict_json_bytes(
        lineage_bytes, V4_LINEAGE_AUTHORITY_PATH)
    body = {
        "schema": "rtdl.goal5791.semantic_physical_variant_successor_authority.v1",
        "goal": 5791,
        "status": "FROZEN_PRE_POD_SUCCESSOR_IDENTITY__NOT_EXECUTION_AUTHORITY",
        "source": {
            "archive_sha256": source_archive_sha256,
            "tree_sha256": source_tree_sha256,
            "manifest_sha256": source_manifest_sha256,
            "successor_source_policy_file_sha256": _sha_bytes(
                source_policy_bytes),
            "successor_source_policy_sha256": source_policy["authority_sha256"],
            "exact_product_delta": {
                name: _sha_bytes(source_payloads[name]) for name in sorted(
                    source_builder.PRODUCT_DELTA)
            },
            "v4_successor_lineage_authority_path": V4_LINEAGE_AUTHORITY_PATH,
            "v4_successor_lineage_authority_file_sha256": _sha_bytes(
                lineage_bytes),
            "v4_successor_lineage_authority_sha256": lineage[
                "authority_sha256"],
        },
        "shared_freeze": {
            "path": SHARED_FREEZE_PATH,
            "file_sha256": _sha_bytes(shared_bytes),
            "shared_contract_freeze_sha256": shared[
                "shared_contract_freeze_sha256"],
            "semantic_request_sha256": shared["semantic_request_sha256"],
            "physical_encoding_sha256": shared["physical_encoding_sha256"],
        },
        "token_amendments": [
            {
                "amendment_id": "Goal5791-A1",
                "file_sha256": _sha_bytes(a1_bytes),
                "canonical_content_sha256": a1["canonical_content_sha256"],
            },
            {
                "amendment_id": "Goal5791-A2",
                "file_sha256": _sha_bytes(a2_bytes),
                "canonical_content_sha256": a2["canonical_content_sha256"],
            },
        ],
        "causal_pair": {
            "paper_algorithm": "RT-2A1",
            "mechanism_id": contract.MECHANISM_ID,
            "same_semantic_ir_required": True,
            "same_physical_encoding_required": True,
            "same_optix_per_ray_producer_required": True,
            "same_source_native_target_and_cohort_required": True,
            "fusion_on_operation_ids": list(contract.FUSION_ON_OPERATION_IDS),
            "fusion_off_operation_ids": list(contract.FUSION_OFF_OPERATION_IDS),
            "sole_allowed_delta": contract.ALLOWED_DELTA_ID,
            "compiler_fusion_performance_claim_authorized_before_result": False,
        },
        "home_functional_closure": {
            "source_archive_sha256": home["execution_source_archive_sha256"],
            "source_tree_sha256": home["execution_source_tree_sha256"],
            "native_library_sha256": home["native_library_sha256"],
            "home_evidence_sha256": home["home_evidence_sha256"],
            "home_evidence_twin_sha256": home[
                "home_evidence_twin_sha256"],
            "home_evidence_manifest_sha256": home[
                "home_evidence_manifest_sha256"],
            "home_evidence_independent_audit_sha256": home[
                "home_evidence_independent_audit_sha256"],
            "exact_lane_count": home["exact_lane_count"],
            "behavioral_true_optix_lane_count": home[
                "behavioral_true_optix_lane_count"],
            "token_only_lane_count": home["token_only_lane_count"],
            "registered_performance_timing_count": home[
                "registered_performance_timing_count"],
            "elapsed_value_count": home["elapsed_value_count"],
            "clock_sample_count": home["clock_sample_count"],
            "home_performance_observation_created": home[
                "home_performance_observation_created"],
            "home_performance_diagnostic_used": home[
                "home_performance_diagnostic_used"],
            "home_native_is_not_target_native": True,
        },
        "authorization": {
            "authorizes_target_prepare": False,
            "authorizes_pod": False,
            "authorizes_formal_worker_zero": False,
            "authorizes_registered_timing": False,
            "authorizes_performance_claim": False,
            "authorizes_publication_or_submission": False,
        },
    }
    value = {**body, "authority_sha256": contract.digest(body)}
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _readme(
    *, source_sha256: str, source_tree_sha256: str,
) -> bytes:
    return independent_audit.canonical_readme(
        source_sha256=source_sha256,
        source_tree_sha256=source_tree_sha256,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-twin", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--source-independent-audit", type=Path, required=True)
    parser.add_argument("--home-result", type=Path, required=True)
    parser.add_argument("--home-evidence", type=Path, required=True)
    parser.add_argument("--home-evidence-twin", type=Path, required=True)
    parser.add_argument(
        "--home-evidence-independent-audit", type=Path, required=True)
    parser.add_argument("--semantic-authority-output", type=Path, required=True)
    parser.add_argument("--runbook-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    outputs = (
        args.semantic_authority_output, args.runbook_output, args.output,
        args.twin, args.receipt,
    )
    if len({path.resolve() for path in outputs}) != len(outputs) \
            or any(path.exists() or path.is_symlink() for path in outputs):
        raise FileExistsError("Goal5791 bundle outputs collide or already exist")

    source_bytes, source_receipt, source_payloads, source_manifest = _source(
        args.source, args.source_twin, args.source_receipt,
        args.source_independent_audit)
    loaded_contract_path = Path(str(contract.__file__)).resolve()
    if not loaded_contract_path.is_file() \
            or loaded_contract_path.read_bytes() != source_payloads[
                "scripts/goal5791_formal_contract.py"
            ]:
        raise BundleError(
            "loaded Goal5791 formal contract differs from frozen source bytes")
    source_sha = _sha_bytes(source_bytes)
    source_tree = str(source_manifest["source_tree_sha256"])
    source_manifest_sha = _sha_bytes(source_payloads[SOURCE_MANIFEST_MEMBER])
    home, home_chain, home_recount_bytes, home_manifest_bytes = _home_chain(
        home_result=args.home_result,
        home_evidence=args.home_evidence,
        home_evidence_twin=args.home_evidence_twin,
        home_evidence_independent_audit=(
            args.home_evidence_independent_audit),
        source_bytes=source_bytes, source_payloads=source_payloads,
        source_tree_sha256=source_tree,
        source_manifest_sha256=source_manifest_sha,
    )
    if (
        home.get("schema") != "rtdl.goal5791.home_token_functional_closure.v1"
        or home.get("status")
            != "PASS__10_OF_10_TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX"
        or home.get("execution_source_archive_sha256") != source_sha
        or home.get("execution_source_tree_sha256") != source_tree
        or home.get("source_manifest_sha256") != source_manifest_sha
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
    ):
        raise BundleError("Goal5791 fresh Home result does not bind this source")

    semantic = _semantic_authority(
        source_archive_sha256=source_sha, source_tree_sha256=source_tree,
        source_manifest_sha256=source_manifest_sha, home=home,
        source_payloads=source_payloads,
    )
    semantic_value = json.loads(semantic)
    _reject_home_performance_observations(
        semantic_value["home_functional_closure"],
        label=("SEMANTIC_PHYSICAL_VARIANT_SUCCESSOR_AUTHORITY.json."
               "home_functional_closure"),
    )
    readme = _readme(
        source_sha256=source_sha, source_tree_sha256=source_tree,
    )
    prereg_bytes = source_payloads[PREREGISTRATION_PATH]
    pretarget_bytes = source_payloads[PRETARGET_PATH]
    prereg = independent_audit._strict_json_bytes(
        prereg_bytes, PREREGISTRATION_PATH)
    pretarget = independent_audit._strict_json_bytes(
        pretarget_bytes, PRETARGET_PATH)
    prereg_unsigned = dict(prereg)
    prereg_claimed = prereg_unsigned.pop("preregistration_sha256", None)
    pretarget_unsigned = dict(pretarget)
    pretarget_claimed = pretarget_unsigned.pop("authority_sha256", None)
    if prereg.get("formal_contract_sha256") != contract.contract_sha256() \
            or prereg.get("schedule_sha256") != contract.schedule_sha256() \
            or prereg_claimed != contract.digest(prereg_unsigned) \
            or pretarget.get("formal_contract_sha256") \
                != contract.contract_sha256() \
            or pretarget.get("schedule_sha256") != contract.schedule_sha256() \
            or pretarget_claimed != contract.digest(pretarget_unsigned):
        raise BundleError("Goal5791 final preregistration/pretarget drifted")
    a2 = independent_audit._strict_json_bytes(
        source_payloads[A2_RESULT_PATH], A2_RESULT_PATH)

    payloads = {
        "SOURCE.tar.gz": source_bytes,
        "SOURCE_BASE_AND_OVERLAY_AUTHORITY.json": args.source_receipt.read_bytes(),
        "SOURCE_INDEPENDENT_AUDIT.json": (
            args.source_independent_audit.read_bytes()),
        "CLAIM_AND_RELATED_WORK_FREEZE.json": source_payloads[
            CLAIM_FREEZE_PATH],
        "SEMANTIC_PHYSICAL_VARIANT_SUCCESSOR_AUTHORITY.json": semantic,
        "EXPECTED_VALUE_AND_FALLBACK.json": source_payloads[
            EXPECTED_VALUE_PATH],
        "PREREGISTRATION.json": prereg_bytes,
        "PRETARGET_PREEXECUTION_AUTHORITY.json": pretarget_bytes,
        "RUNTIME_BUDGET.json": source_payloads[RUNTIME_BUDGET_PATH],
        "OWNER_AUTHORITY_REQUEST_PROTOCOL.md": source_payloads[
            OUTER_TO_SOURCE_AUTHORITY_MEMBERS[
                "OWNER_AUTHORITY_REQUEST_PROTOCOL.md"]],
        "HOME_FUNCTIONAL_CLOSURE.json": args.home_result.read_bytes(),
        "HOME_EVIDENCE_MANIFEST.json": home_manifest_bytes,
        "HOME_EVIDENCE_INDEPENDENT_AUDIT.json": (
            args.home_evidence_independent_audit.read_bytes()),
        "HOME_FUNCTIONAL_RECOUNT.json": home_recount_bytes,
        "README.md": readme,
        **{
            outer: source_payloads[inner]
            for outer, inner in HARNESS_MEMBERS.items()
        },
    }
    for outer_name, source_name in OUTER_TO_SOURCE_AUTHORITY_MEMBERS.items():
        if payloads.get(outer_name) != source_payloads.get(source_name):
            raise BundleError(
                f"Goal5791 outer/source authority bytes drifted: {outer_name}")
    if any(
        name != "SOURCE.tar.gz" and (
            name.lower().endswith(source_builder._CONTAINER_SUFFIXES)
            or source_builder._blob_kind(data) is not None
        )
        for name, data in payloads.items()
    ):
        raise BundleError("Goal5791 bundle has an unauthorized nested container/binary")
    rows = source_builder._canonical_rows(payloads)
    manifest = (json.dumps({
        "schema": "rtdl.goal5791.pre_pod_bundle.v3",
        "goal": 5791,
        "status": "FROZEN_PRE_POD_PACKET__SEPARATE_OWNER_AUTHORITIES_REQUIRED",
        "manifest_is_non_self_referential": True,
        "source_archive_sha256": source_sha,
        "source_tree_sha256": source_tree,
        "source_manifest_sha256": source_manifest_sha,
        "source_build_receipt_file_sha256": _sha(args.source_receipt),
        "source_independent_audit_file_sha256": _sha(
            args.source_independent_audit),
        "home_functional_closure_file_sha256": _sha(args.home_result),
        "home_evidence_sha256": home["home_evidence_sha256"],
        "home_evidence_twin_sha256": home_chain[
            "home_evidence_twin_sha256"],
        "home_evidence_independent_audit_file_sha256": home_chain[
            "home_evidence_independent_audit_file_sha256"],
        "home_evidence_manifest_sha256": home_chain[
            "home_evidence_manifest_sha256"],
        "home_functional_recount_sha256": home_chain[
            "home_functional_recount_sha256"],
        "home_independent_recount_reexecuted_and_byte_identical": True,
        "formal_contract_file_sha256": _sha_bytes(
            source_payloads["scripts/goal5791_formal_contract.py"]),
        "formal_contract_sha256": contract.contract_sha256(),
        "schedule_sha256": contract.schedule_sha256(),
        "token_amendment_sha256": a2["canonical_content_sha256"],
        "token_amendment_chain_sha256": contract.digest([
            "8d832bcc0c8e93d4b288d84f7eeaec36a109cd6cdfad922f9e61e5e39be4d4ca",
            a2["canonical_content_sha256"],
        ]),
        "external_uploads": EXTERNAL_UPLOADS,
        "payload_count_excluding_manifest": len(rows),
        "payload_bytes_excluding_manifest": sum(len(data) for data in payloads.values()),
        "source_is_only_nested_container": True,
        "source_deep_container_depth": 0,
        "contains_real_scale_data": False,
        "contains_wheelhouse": False,
        "contains_optix_headers": False,
        "contains_prebuilt_target_native": False,
        "contains_owner_prepare_authority": False,
        "contains_owner_formal_authority": False,
        "formal_worker_count_executed": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "payloads": rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    outer = {**payloads, "BUNDLE_MANIFEST.json": manifest}
    _require_exact_bundle_member_set(outer)
    _reject_home_performance_observations(
        json.loads(manifest), label="BUNDLE_MANIFEST.json")
    archive = source_builder._archive(outer)
    twin = source_builder._archive(outer)
    if archive != twin or source_builder._read_archive(archive) != outer:
        raise BundleError("Goal5791 deterministic bundle/twin reopen failed")
    with tempfile.TemporaryDirectory(prefix="goal5791_bundle_audit_") as temp:
        extracted = Path(temp) / "bundle"
        source_builder._extract(outer, extracted)
        exact_set = source_builder._audit_extracted_exact_set(extracted, outer)

    receipt_value = {
        "schema": "rtdl.goal5791.pre_pod_bundle_build_receipt.v3",
        "goal": 5791,
        "status": "PASS__DETERMINISTIC_PRE_POD_PACKET__NO_EXECUTION_AUTHORITY",
        "bundle_sha256": _sha_bytes(archive),
        "bundle_bytes": len(archive),
        "twin_sha256": _sha_bytes(twin),
        "twin_byte_identical": archive == twin,
        "manifest_sha256": _sha_bytes(manifest),
        "payload_count_excluding_manifest": len(payloads),
        "payload_bytes_excluding_manifest": sum(len(data) for data in payloads.values()),
        "source_archive_sha256": source_sha,
        "source_tree_sha256": source_tree,
        "source_manifest_sha256": source_manifest_sha,
        "source_build_receipt_file_sha256": _sha(args.source_receipt),
        "source_independent_audit_file_sha256": _sha(
            args.source_independent_audit),
        "home_functional_closure_file_sha256": _sha(args.home_result),
        "home_evidence_sha256": home["home_evidence_sha256"],
        "home_evidence_twin_sha256": home_chain[
            "home_evidence_twin_sha256"],
        "home_evidence_independent_audit_file_sha256": home_chain[
            "home_evidence_independent_audit_file_sha256"],
        "home_evidence_manifest_sha256": home_chain[
            "home_evidence_manifest_sha256"],
        "home_functional_recount_sha256": home_chain[
            "home_functional_recount_sha256"],
        "home_independent_recount_reexecuted_and_byte_identical": True,
        "semantic_authority_sha256": json.loads(semantic)["authority_sha256"],
        "runbook_sha256": _sha_bytes(readme),
        "clean_extraction_exact_set": exact_set,
        "deep_source_audit_reperformed": True,
        "source_is_only_nested_container": True,
        "prebuilt_native_or_device_binary_count": 0,
        "owner_authority_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "pod_execution_count": 0,
    }
    receipt = (json.dumps(receipt_value, indent=2, sort_keys=True) + "\n").encode()
    _write(args.semantic_authority_output, semantic)
    _write(args.runbook_output, readme)
    _write(args.output, archive)
    _write(args.twin, twin)
    _write(args.receipt, receipt)
    print(json.dumps(receipt_value, sort_keys=True))


if __name__ == "__main__":
    main()
