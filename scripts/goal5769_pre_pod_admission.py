#!/usr/bin/env python3
"""Fail-closed Goal5769 authority, toolchain and exact-test admission.

This module is deliberately independent of the application front doors.  It
does not authorize a transaction; it validates exact owner-provided authority
and immutable bundle policies before any GPU application worker may start.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


REVIEW_ABSORPTION_SCHEMA = (
    "rtdl.goal5769.owner_returned_external_review_absorption.v1")
TOOLCHAIN_POLICY_SCHEMA = "rtdl.goal5769.target_toolchain_policy.v1"
TEST_MANIFEST_SCHEMA = "rtdl.goal5769.exact_test_manifest.v1"
FORMAL_REVIEW_ABSORPTION_SCHEMA = (
    "rtdl.goal5769.owner_returned_prepared_review_absorption.v1")
OWNER_DIRECT_PREPARE_AUTHORITY_SCHEMA = (
    "rtdl.goal5769.owner_direct_stage_a_authority.v1")
OWNER_DIRECT_PREPARE_REVIEW_SCHEMA = (
    "rtdl.goal5769.owner_direct_stage_a_internal_review.v1")
OWNER_DIRECT_FORMAL_AUTHORITY_SCHEMA = (
    "rtdl.goal5769.owner_direct_stage_b_authority.v1")
OWNER_DIRECT_FORMAL_REVIEW_SCHEMA = (
    "rtdl.goal5769.owner_direct_stage_b_internal_review.v1")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest(value: object) -> str:
    return sha256_bytes(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8"))


def _require_sha256(value: object, name: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise PermissionError(f"{name} is not a lowercase SHA-256")
    return value


def validate_prepare_authority_files(
    authority: dict[str, Any], *, owner_review_path: Path,
    review_absorption_path: Path, bundle_sha256: str, source_sha256: str,
    toolchain_policy_sha256: str, test_manifest_sha256: str,
    cc: str, optix_sdk: str, cuda_toolkit: str,
) -> dict[str, Any]:
    """Validate a real review file and structured owner-returned absorption.

    The authority is owner-authored and self-digested.  The review and
    absorption remain separate inputs so a self-review, stale review, or a
    review of different bundle bytes cannot be substituted by editing the
    authority JSON.
    """

    body = dict(authority)
    claimed = body.pop("authority_sha256", None)
    if claimed != canonical_digest(body):
        raise PermissionError("prepare authority digest mismatch")

    if authority.get("schema") == OWNER_DIRECT_PREPARE_AUTHORITY_SCHEMA:
        directive_sha = sha256_file(owner_review_path)
        internal_review_sha = sha256_file(review_absorption_path)
        if authority.get("owner_continuous_directive_sha256") != directive_sha:
            raise PermissionError("owner continuous directive digest mismatch")
        if authority.get("strict_internal_review_sha256") != internal_review_sha:
            raise PermissionError("strict internal review digest mismatch")
        review = json.loads(review_absorption_path.read_text(encoding="utf-8"))
        if review.get("schema") != OWNER_DIRECT_PREPARE_REVIEW_SCHEMA \
                or review.get("review_kind") != "strict_internal_self_review" \
                or review.get("self_review") is not True \
                or review.get("external_review_claimed") is not False \
                or review.get("p0") != 0 or review.get("p1") != 0 \
                or review.get("stage_a_create_only_prepare_recommended") is not True \
                or review.get("stage_b_formal_execution_authorized") is not False:
            raise PermissionError("owner-direct Stage-A internal review is invalid")
        exact_review_bindings = {
            "successor_bundle_sha256": bundle_sha256,
            "successor_source_archive_sha256": source_sha256,
            "toolchain_policy_sha256": toolchain_policy_sha256,
            "test_manifest_sha256": test_manifest_sha256,
            "owner_continuous_directive_sha256": directive_sha,
        }
        for name, expected in exact_review_bindings.items():
            if review.get(name) != expected:
                raise PermissionError(f"owner-direct Stage-A review mismatch: {name}")
        if review.get("baseline_v24_terminal_failure_preserved") is not True \
                or review.get("v4_product_or_native_changed") is not False \
                or review.get("formal_worker_or_timing_reused") is not False:
            raise PermissionError("owner-direct Stage-A delta boundary was weakened")
        changed = review.get("changed_source_paths")
        if changed != [
            "scripts/goal5768_formal_controller.py",
            "scripts/goal5768_target_prepare.py",
            "scripts/goal5768_three_way_worker.py",
            "scripts/goal5769_pre_pod_admission.py",
            "tests/goal5768_formal_harness_test.py",
            "tests/goal5769_pre_pod_admission_test.py",
        ]:
            raise PermissionError("owner-direct Stage-A source delta is not exact")
        authority_bindings = {
            "bundle_sha256": bundle_sha256,
            "source_archive_sha256": source_sha256,
            "toolchain_policy_sha256": toolchain_policy_sha256,
            "test_manifest_sha256": test_manifest_sha256,
            "required_compute_capability": cc,
            "required_optix_sdk": optix_sdk,
            "required_cuda_toolkit": cuda_toolkit,
        }
        for name, expected in authority_bindings.items():
            if authority.get(name) != expected:
                raise PermissionError(f"owner-direct prepare authority mismatch: {name}")
        if authority.get("owner_authorized_create_only_prepare") is not True \
                or authority.get("external_preexecution_review_claimed") is not False \
                or authority.get("formal_worker_allowed") is not False \
                or authority.get("registered_formal_timing_allowed") is not False \
                or authority.get("stage_b_formal_execution_authorized") is not False:
            raise PermissionError("owner-direct Stage-A scope was weakened")
        for name in (
            "required_gpu_name", "required_gpu_uuid", "required_driver_version",
        ):
            value = authority.get(name)
            if not isinstance(value, str) or not value:
                raise PermissionError(f"owner-direct authority lacks exact {name}")
        _require_sha256(authority.get("required_python_executable_sha256"),
                        "required_python_executable_sha256")
        return review

    review_sha = sha256_file(owner_review_path)
    absorption_sha = sha256_file(review_absorption_path)
    if authority.get("owner_returned_external_review_sha256") != review_sha:
        raise PermissionError("owner review file digest mismatch")
    if authority.get("owner_returned_review_absorption_sha256") != absorption_sha:
        raise PermissionError("owner review absorption file digest mismatch")

    absorption = json.loads(review_absorption_path.read_text(encoding="utf-8"))
    if absorption.get("schema") != REVIEW_ABSORPTION_SCHEMA:
        raise PermissionError("unexpected owner review absorption schema")
    if absorption.get("review_kind") != "owner_returned_external_review" \
            or absorption.get("self_review") is not False \
            or absorption.get("exact_byte_external_review") is not True:
        raise PermissionError("self-review or non-exact review cannot authorize prepare")
    if absorption.get("normalized_review_sha256") != review_sha:
        raise PermissionError("review absorption does not bind review bytes")
    if absorption.get("p0") != 0 or absorption.get("p1") != 0:
        raise PermissionError("owner-returned external review has blocking findings")
    if absorption.get("stage_a_create_only_prepare_recommended") is not True \
            or absorption.get("stage_b_formal_execution_authorized") is not False:
        raise PermissionError("review scope does not recommend only Stage A")

    exact_bindings = {
        "reviewed_bundle_sha256": bundle_sha256,
        "reviewed_source_archive_sha256": source_sha256,
        "reviewed_toolchain_policy_sha256": toolchain_policy_sha256,
        "reviewed_test_manifest_sha256": test_manifest_sha256,
    }
    for name, expected in exact_bindings.items():
        if absorption.get(name) != expected:
            raise PermissionError(f"owner review absorption mismatch: {name}")

    authority_bindings = {
        "bundle_sha256": bundle_sha256,
        "source_archive_sha256": source_sha256,
        "toolchain_policy_sha256": toolchain_policy_sha256,
        "test_manifest_sha256": test_manifest_sha256,
        "required_compute_capability": cc,
        "required_optix_sdk": optix_sdk,
        "required_cuda_toolkit": cuda_toolkit,
    }
    for name, expected in authority_bindings.items():
        if authority.get(name) != expected:
            raise PermissionError(f"prepare authority mismatch: {name}")
    if authority.get("owner_authorized_create_only_prepare") is not True:
        raise PermissionError("create-only prepare lacks owner authorization")
    if authority.get("formal_worker_allowed") is not False \
            or authority.get("registered_formal_timing_allowed") is not False:
        raise PermissionError("prepare authority must forbid formal work/timing")
    if authority.get("stage_b_formal_execution_authorized") is not False:
        raise PermissionError("Stage-A authority cannot authorize Stage B")
    for name in (
        "required_gpu_name", "required_gpu_uuid", "required_driver_version",
    ):
        value = authority.get(name)
        if not isinstance(value, str) or not value:
            raise PermissionError(f"prepare authority lacks exact {name}")
    _require_sha256(authority.get("required_python_executable_sha256"),
                    "required_python_executable_sha256")
    return absorption


def validate_formal_authority_files(
    plan: dict[str, Any], authority: dict[str, Any], *,
    owner_review_path: Path, review_absorption_path: Path,
) -> dict[str, Any]:
    """Bind Stage B to a separate review of the exact prepared identity."""
    if authority.get("schema") == OWNER_DIRECT_FORMAL_AUTHORITY_SCHEMA:
        directive_sha = sha256_file(owner_review_path)
        internal_review_sha = sha256_file(review_absorption_path)
        if authority.get("owner_continuous_directive_sha256") != directive_sha \
                or authority.get("strict_internal_review_sha256") != internal_review_sha:
            raise PermissionError("owner-direct formal review bytes mismatch")
        review = json.loads(review_absorption_path.read_text(encoding="utf-8"))
        if review.get("schema") != OWNER_DIRECT_FORMAL_REVIEW_SCHEMA \
                or review.get("review_kind") != "strict_internal_self_review" \
                or review.get("self_review") is not True \
                or review.get("external_review_claimed") is not False \
                or review.get("p0") != 0 or review.get("p1") != 0 \
                or review.get("stage_b_formal_execution_recommended") is not True:
            raise PermissionError("owner-direct Stage-B internal review is invalid")
        for name in (
            "plan_sha256", "formal_identity_sha256", "bundle_sha256",
            "prepared_identity_sha256", "target_identity_sha256",
        ):
            if review.get(f"reviewed_{name}") != plan.get(name):
                raise PermissionError(f"owner-direct formal review mismatch: {name}")
        if review.get("reviewed_expected_worker_count") != 312 \
                or review.get("owner_continuous_directive_sha256") != directive_sha \
                or review.get("stage_a_functional_worker_count") != 39 \
                or review.get("stage_a_all_correct_and_behavioral_true_optix") is not True \
                or review.get("formal_observation_reuse_allowed") is not False:
            raise PermissionError("owner-direct formal review scope was weakened")
        if authority.get("external_preexecution_review_claimed") is not False:
            raise PermissionError("owner-direct formal execution cannot claim external review")
        return review

    review_sha = sha256_file(owner_review_path)
    absorption_sha = sha256_file(review_absorption_path)
    if authority.get("owner_returned_external_review_sha256") != review_sha \
            or authority.get("owner_returned_review_absorption_sha256") != absorption_sha:
        raise PermissionError("formal authority review bytes mismatch")
    absorption = json.loads(review_absorption_path.read_text(encoding="utf-8"))
    if absorption.get("schema") != FORMAL_REVIEW_ABSORPTION_SCHEMA \
            or absorption.get("review_kind") != "owner_returned_external_review" \
            or absorption.get("self_review") is not False \
            or absorption.get("exact_byte_external_review") is not True \
            or absorption.get("normalized_review_sha256") != review_sha:
        raise PermissionError("formal review is not an exact owner-returned review")
    if absorption.get("p0") != 0 or absorption.get("p1") != 0 \
            or absorption.get("stage_b_formal_execution_recommended") is not True:
        raise PermissionError("formal review does not recommend Stage B")
    for name in (
        "plan_sha256", "formal_identity_sha256", "bundle_sha256",
        "prepared_identity_sha256", "target_identity_sha256",
    ):
        if absorption.get(f"reviewed_{name}") != plan.get(name):
            raise PermissionError(f"formal review absorption mismatch: {name}")
    if absorption.get("reviewed_expected_worker_count") != 312:
        raise PermissionError("formal review does not bind 312 workers")
    return absorption


def validate_toolchain_policy(policy: dict[str, Any], *, payloads: dict[str, bytes]) -> None:
    if policy.get("schema") != TOOLCHAIN_POLICY_SCHEMA:
        raise RuntimeError("unexpected toolchain policy schema")
    required = {
        "python": "3.12.3",
        "numba": "0.65.1",
        "numpy": "2.2.6",
        "llvmlite": "0.47.0",
        "cupy": "14.0.1",
        "cuda_toolkit": "12.8",
        "cuda_nvcc": "12.8.93",
        "cuda_runtime": "12.8.90",
        "optix_sdk": "9.0.0",
    }
    if policy.get("versions") != required:
        raise RuntimeError("toolchain policy version matrix changed")
    if policy.get("python_executable") != "/usr/bin/python3.12":
        raise RuntimeError("toolchain policy lacks exact Python executable")
    rows = policy.get("payloads")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("toolchain policy lacks exact payloads")
    expected_paths = set()
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("malformed toolchain payload row")
        name = row.get("path")
        if not isinstance(name, str) or name in expected_paths:
            raise RuntimeError("duplicate or malformed toolchain payload")
        expected_paths.add(name)
        data = payloads.get(name)
        if data is None or len(data) != row.get("size_bytes") \
                or sha256_bytes(data) != row.get("sha256"):
            raise RuntimeError(f"toolchain payload mismatch: {name}")
    if expected_paths != {
        name for name in payloads if name.startswith("TOOLCHAIN/")
        and name != "TOOLCHAIN/TOOLCHAIN_POLICY.json"
    }:
        raise RuntimeError("toolchain payload membership differs from policy")


def validate_exact_test_manifest(source: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != TEST_MANIFEST_SCHEMA:
        raise RuntimeError("unexpected exact-test manifest schema")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("exact-test manifest lacks files")
    declared: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("malformed exact-test manifest row")
        if row["path"] in declared:
            raise RuntimeError("duplicate exact-test manifest path")
        declared[row["path"]] = row
    patterns = manifest.get("discovery_patterns")
    if patterns != [
        {"pattern": "goal57*_v4_*test.py", "expected_test_case_count": 201},
        {"pattern": "goal5768_*test.py", "expected_test_case_count": 22},
        {"pattern": "goal5769_*test.py", "expected_test_case_count": 30},
    ]:
        raise RuntimeError("exact-test manifest discovery contract changed")
    observed_paths: set[str] = set()
    for entry in patterns:
        if not isinstance(entry, dict) or not isinstance(entry.get("pattern"), str):
            raise RuntimeError("malformed test discovery row")
        observed_paths.update(
            path.relative_to(source).as_posix()
            for path in (source / "tests").glob(entry["pattern"]) if path.is_file())
        count = entry.get("expected_test_case_count")
        if type(count) is not int or count <= 0:
            raise RuntimeError("test discovery row lacks exact case count")
    if set(declared) != observed_paths:
        raise RuntimeError("test file membership differs from exact manifest")
    for name, row in declared.items():
        path = source / name
        if not path.is_file() or path.stat().st_size != row.get("size_bytes") \
                or sha256_file(path) != row.get("sha256"):
            raise RuntimeError(f"test file differs from exact manifest: {name}")


def expected_test_count(manifest: dict[str, Any], pattern: str) -> int:
    for row in manifest["discovery_patterns"]:
        if row["pattern"] == pattern:
            return int(row["expected_test_case_count"])
    raise KeyError(pattern)


def parse_unittest_count(output: str) -> int:
    matches = re.findall(r"^Ran ([0-9]+) tests? in ", output, flags=re.MULTILINE)
    if len(matches) != 1:
        raise RuntimeError("unittest output lacks one exact test count")
    return int(matches[0])
