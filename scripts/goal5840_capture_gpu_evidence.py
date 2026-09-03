#!/usr/bin/env python3
"""Capture Goal5840's four exact-mode true-OptiX evidence bundles."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Mapping

from rtdsl.v4_callback_lifecycle import V4Target, V4Toolchain
from rtdsl.v4_sphere_any_hit_count import V4SphereTarget
from rtdsl.v4_target_evidence_capture import capture_real_target_evidence_bundle
from scripts import goal5840_freeze_attempt04_repair_inputs as attempt04_freezer
from scripts import goal5840_freeze_attempt03_repair_inputs as attempt03_freezer
from scripts.goal5840_freeze_attempt02_repair_inputs import (
    ALLOWED_CHANGED_PATHS as ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS,
    ATTEMPT_02_INCIDENT_SHA256,
    BASE_COMMIT as ATTEMPT_02_SOURCE_COMMIT,
    DOMAIN as ATTEMPT_02_REPAIR_AUTHORITY_DOMAIN,
    SOURCE_PATHS as ATTEMPT_02_REPAIR_AUTHORITY_SOURCE_PATHS,
)
from scripts.goal5840_freeze_repair_inputs import (
    ALLOWED_CHANGED_PATHS as REPAIR_ALLOWED_CHANGED_PATHS,
    BASE_COMMIT as ATTEMPT_01_SOURCE_COMMIT,
    DOMAIN as REPAIR_AUTHORITY_DOMAIN,
    SOURCE_PATHS as REPAIR_AUTHORITY_SOURCE_PATHS,
)
from scripts.goal5840_gpu_cases import goal5840_mode_cases


ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = (
    ROOT
    / "history/internal_docs/goal5840_independent_lowering_refinement_20260903"
)
PREREGISTRATION = GOAL_ROOT / "GOAL5840_PREREGISTRATION.json"
PRE_POD_AUTHORITY = GOAL_ROOT / "PRE_POD_INPUT_AUTHORITY.json"
ATTEMPT_01_INCIDENT = GOAL_ROOT / "ATTEMPT_01_ENGINEERING_FAILURE.md"
REPAIR_AUTHORITY = GOAL_ROOT / "POST_ATTEMPT_01_REPAIR_AUTHORITY.json"
ATTEMPT_02_INCIDENT = GOAL_ROOT / "ATTEMPT_02_ENGINEERING_FAILURE.md"
ATTEMPT_02_REPAIR_AUTHORITY = (
    GOAL_ROOT / "POST_ATTEMPT_02_REPAIR_AUTHORITY.json"
)
ATTEMPT_03_INCIDENT = GOAL_ROOT / "ATTEMPT_03_ENGINEERING_FAILURE.md"
ATTEMPT_03_REPAIR_AUTHORITY = (
    GOAL_ROOT / "POST_ATTEMPT_03_REPAIR_AUTHORITY.json"
)
ATTEMPT_04_INCIDENT = GOAL_ROOT / "ATTEMPT_04_ENGINEERING_FAILURE.md"
ATTEMPT_04_REPAIR_AUTHORITY = (
    GOAL_ROOT / "POST_ATTEMPT_04_REPAIR_AUTHORITY.json"
)
CHECKER = ROOT / "scripts/goal5840_independent_target_checker.py"
MUTATION_RUNNER = ROOT / "scripts/goal5840_mutation_suite.py"
SUMMARY_DOMAIN = b"rtdl.goal5840.true_optix_target_evidence.v5\0"
TRUST_ROOT_DOMAIN = b"rtdl.goal5840.runtime_trust_roots.v1\0"
NATIVE_BUILD_DOMAIN = b"rtdl.goal5838.selected_sphere_optix_provider_build.v2\0"
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
SOURCE_PATHS = (
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_gpu_inputs.py",
    "scripts/goal5840_freeze_attempt02_repair_inputs.py",
    "scripts/goal5840_freeze_attempt03_repair_inputs.py",
    "scripts/goal5840_freeze_attempt04_repair_inputs.py",
    "scripts/goal5840_freeze_repair_inputs.py",
    "scripts/goal5840_gpu_cases.py",
    "scripts/goal5840_independent_target_checker.py",
    "scripts/goal5840_mutation_suite.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_control_flow_evidence.py",
    "src/rtdsl/v4_target_evidence_bundle.py",
    "src/rtdsl/v4_target_evidence_capture.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
    "src/rtdsl/v4_callback_ptx_composer.py",
    "src/rtdsl/v4_inline_cuda_codegen.py",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "GOAL5840_PREREGISTRATION.json",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "PRE_POD_INPUT_AUTHORITY.json",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_01_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_01_REPAIR_AUTHORITY.json",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_02_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_02_REPAIR_AUTHORITY.json",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_03_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_03_REPAIR_AUTHORITY.json",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_04_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_04_REPAIR_AUTHORITY.json",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _git_blob(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"git show {commit}:{path}: {completed.stderr.decode(errors='replace')}"
        )
    return completed.stdout


def _repository_custody(expected_commit: str) -> dict[str, object]:
    if len(expected_commit) != 40 or any(
        character not in "0123456789abcdef" for character in expected_commit
    ):
        raise RuntimeError("--expected-commit must be one full lowercase commit")
    if _git("rev-parse", "HEAD") != expected_commit:
        raise RuntimeError("checkout does not equal --expected-commit")
    if _git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("GPU capture requires a clean Git worktree")
    rows = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        working = path.read_bytes()
        committed = subprocess.run(
            ["git", "show", f"{expected_commit}:{relative}"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
        if working != committed:
            raise RuntimeError(f"working source differs from commit: {relative}")
        rows.append({
            "path": relative,
            "bytes": len(working),
            "sha256": hashlib.sha256(working).hexdigest(),
        })
    return {
        "expected_commit": expected_commit,
        "head_before": expected_commit,
        "branch": _git("branch", "--show-current"),
        "origin": _git("remote", "get-url", "origin"),
        "clean_before": True,
        "source_files": rows,
    }


def _finish_repository_custody(
    before: dict[str, object], expected_commit: str
) -> dict[str, object]:
    if _git("rev-parse", "HEAD") != expected_commit or _git(
        "status", "--porcelain=v1", "--untracked-files=all"
    ):
        raise RuntimeError("repository changed during GPU capture")
    return {**before, "head_after": expected_commit, "clean_after": True}


def _outside_repository(path: Path) -> Path:
    result = path.expanduser().resolve()
    if result == ROOT or ROOT in result.parents:
        raise RuntimeError("GPU evidence output must be outside the Git tree")
    if result.exists():
        raise FileExistsError(result)
    result.mkdir(parents=True)
    return result


def _machine() -> dict[str, object]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--id=0",
            "--query-gpu=name,uuid,driver_version,pci.bus_id,compute_cap,memory.total",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"nvidia-smi failed: {completed.stderr.strip()}")
    rows = [
        [part.strip() for part in line.split(",")]
        for line in completed.stdout.splitlines()
        if line.strip()
    ]
    if len(rows) != 1 or len(rows[0]) != 6:
        raise RuntimeError(f"one selected GPU required: {rows!r}")
    return dict(zip(
        ("name", "uuid", "driver", "pci_bus_id", "compute_capability", "memory_mib"),
        rows[0],
        strict=True,
    ))


def _verify_frozen_core() -> dict[str, object]:
    seal_path = (
        ROOT
        / "history/internal_docs/goal5838_generic_core_exam_20260902/"
        "GENERIC_CORE_SEAL.json"
    )
    seal = json.loads(seal_path.read_text(encoding="ascii"))
    rows = []
    for row in seal["frozen_core_files"]:
        path = ROOT / row["path"]
        observed = _sha_file(path)
        if observed != row["sha256"]:
            raise RuntimeError(f"Goal5838 frozen core changed: {row['path']}")
        rows.append({
            "path": row["path"],
            "bytes": path.stat().st_size,
            "sha256": observed,
        })
    return {
        "seal_sha256": seal["seal_sha256"],
        "files": rows,
        "changed_file_count": 0,
    }


def _verify_pre_pod_authority() -> dict[str, object]:
    authority_bytes = PRE_POD_AUTHORITY.read_bytes()
    relative = str(PRE_POD_AUTHORITY.relative_to(ROOT))
    if authority_bytes != _git_blob(ATTEMPT_01_SOURCE_COMMIT, relative):
        raise RuntimeError("pre-pod authority differs from Attempt-01 commit")
    authority = json.loads(authority_bytes.decode("ascii"))
    body = dict(authority)
    observed = body.pop("authority_sha256", None)
    body["authority_sha256"] = ""
    expected = hashlib.sha256(
        b"rtdl.goal5840.pre_pod_input_authority.v1\0" + _canonical(body)
    ).hexdigest()
    if observed != expected:
        raise RuntimeError("pre-pod input authority seal differs")
    if (
        authority.get("schema")
        != "rtdl.goal5840.pre_pod_input_authority.v1"
        or authority.get("stage") != "BEFORE_ANY_GOAL5840_GPU_EXECUTION"
        or authority.get("required_mode_count") != 4
        or authority.get("route_bundle_group_count") != 3
        or authority.get("execution_counts_at_freeze")
        != {
            "goal5840_gpu_launches": 0,
            "goal5840_positive_target_bundles": 0,
            "goal5840_exact_bundle_mutations": 0,
        }
    ):
        raise RuntimeError("pre-pod input authority contract differs")
    source_rows = authority.get("source_files")
    if not isinstance(source_rows, list):
        raise RuntimeError("pre-pod input authority source inventory is absent")
    for row in source_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("pre-pod source inventory row is invalid")
        relative = str(row["path"])
        blob = _git_blob(ATTEMPT_01_SOURCE_COMMIT, relative)
        if (
            len(blob) != row.get("bytes")
            or hashlib.sha256(blob).hexdigest() != row.get("sha256")
        ):
            raise RuntimeError(f"pre-pod source differs at base commit: {relative}")
    return authority


def _verify_repair_authority(
    original: Mapping[str, object],
    preregistration: Mapping[str, object],
    expected_commit: str,
    *,
    require_current_source_match: bool = True,
) -> dict[str, object]:
    authority = json.loads(REPAIR_AUTHORITY.read_text(encoding="ascii"))
    body = dict(authority)
    observed = body.get("authority_sha256")
    body["authority_sha256"] = ""
    expected = hashlib.sha256(
        REPAIR_AUTHORITY_DOMAIN + _canonical(body)
    ).hexdigest()
    if observed != expected:
        raise RuntimeError("post-Attempt-01 repair authority seal differs")
    if (
        authority.get("schema")
        != "rtdl.goal5840.post_attempt_01_repair_authority.v1"
        or authority.get("stage")
        != "AFTER_ATTEMPT_01_BEFORE_ATTEMPT_02_GPU_EXECUTION"
        or authority.get("status")
        != "FROZEN_BOUNDED_EVIDENCE_TRANSPORT_REPAIR__NO_ACCEPTED_RESULT"
        or authority.get("route_bundle_group_count") != 3
        or authority.get("required_mode_count") != 4
        or authority.get("mode_cases") != original.get("mode_cases")
        or authority.get("goal5838_frozen_core")
        != original.get("goal5838_frozen_core")
        or authority.get("preregistration") != original.get("preregistration")
    ):
        raise RuntimeError("post-Attempt-01 repair authority contract differs")

    base = authority.get("base_attempt")
    scope = authority.get("repair_scope")
    counts = authority.get("execution_counts_at_repair_freeze")
    if not isinstance(base, dict) or not isinstance(scope, dict):
        raise RuntimeError("repair authority base/scope is absent")
    pre_pod_ref = base.get("pre_pod_input_authority")
    incident_ref = base.get("attempt_01_incident")
    if not isinstance(pre_pod_ref, dict) or not isinstance(incident_ref, dict):
        raise RuntimeError("repair authority chain reference is absent")
    if (
        base.get("source_commit") != ATTEMPT_01_SOURCE_COMMIT
        or pre_pod_ref
        != {
            "path": str(PRE_POD_AUTHORITY.relative_to(ROOT)),
            "bytes": PRE_POD_AUTHORITY.stat().st_size,
            "file_sha256": _sha_file(PRE_POD_AUTHORITY),
            "authority_sha256": original.get("authority_sha256"),
        }
        or incident_ref.get("path")
        != str(ATTEMPT_01_INCIDENT.relative_to(ROOT))
        or incident_ref.get("bytes") != ATTEMPT_01_INCIDENT.stat().st_size
        or incident_ref.get("file_sha256") != _sha_file(ATTEMPT_01_INCIDENT)
        or incident_ref.get("classification")
        != "EVIDENCE_TRANSPORT_ENGINEERING_FAILURE"
    ):
        raise RuntimeError("repair authority base-attempt identity differs")
    expected_observed_counts = {
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
    if (
        base.get("observed_counts") != expected_observed_counts
        or counts != expected_repair_counts
        or scope.get("allowed_changed_paths") != list(REPAIR_ALLOWED_CHANGED_PATHS)
        or scope.get("exact_changed_paths_since_base")
        != list(REPAIR_ALLOWED_CHANGED_PATHS)
        or scope.get("nonsemantic_harness_hardening")
        != "generate_pod_mutation_report_under_python_isolated_mode"
        or any(
            scope.get(field) is not False
            for field in (
                "route_change_allowed",
                "fixture_or_oracle_change_allowed",
                "declaration_or_control_root_change_allowed",
                "property_or_mutation_change_allowed",
                "native_engine_change_allowed",
                "frozen_core_change_allowed",
            )
        )
    ):
        raise RuntimeError("repair authority scope/counts differ")
    changed = tuple(sorted(
        line
        for line in _git(
            "diff",
            "--name-only",
            f"{ATTEMPT_01_SOURCE_COMMIT}..{expected_commit}",
            "--",
        ).splitlines()
        if line
    ))
    if changed != REPAIR_ALLOWED_CHANGED_PATHS:
        raise RuntimeError(f"committed repair path set differs: {changed!r}")

    source_rows = authority.get("source_files")
    if not isinstance(source_rows, list):
        raise RuntimeError("repair authority source inventory is absent")
    observed_paths = set()
    for row in source_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("repair authority source row is invalid")
        relative = str(row["path"])
        blob = _git_blob(expected_commit, relative)
        if (
            relative in observed_paths
            or len(blob) != row.get("bytes")
            or hashlib.sha256(blob).hexdigest() != row.get("sha256")
            or (
                require_current_source_match
                and (ROOT / relative).read_bytes() != blob
            )
        ):
            raise RuntimeError(f"repair source custody differs: {relative}")
        observed_paths.add(relative)
    if observed_paths != set(REPAIR_AUTHORITY_SOURCE_PATHS):
        raise RuntimeError("repair authority source denominator differs")

    frozen_preregistration = authority.get("preregistration")
    if (
        not isinstance(frozen_preregistration, dict)
        or frozen_preregistration.get("file_sha256") != _sha_file(PREREGISTRATION)
        or frozen_preregistration.get("authority_sha256")
        != preregistration.get("authority_sha256")
    ):
        raise RuntimeError("repair authority preregistration differs")
    return authority


def _verify_attempt02_repair_authority(
    original: Mapping[str, object],
    prior: Mapping[str, object],
    preregistration: Mapping[str, object],
    expected_commit: str,
    *,
    require_current_source_match: bool = True,
) -> dict[str, object]:
    authority = json.loads(
        ATTEMPT_02_REPAIR_AUTHORITY.read_text(encoding="ascii")
    )
    body = dict(authority)
    observed = body.get("authority_sha256")
    body["authority_sha256"] = ""
    expected = hashlib.sha256(
        ATTEMPT_02_REPAIR_AUTHORITY_DOMAIN + _canonical(body)
    ).hexdigest()
    if observed != expected:
        raise RuntimeError("post-Attempt-02 repair authority seal differs")
    if (
        authority.get("schema")
        != "rtdl.goal5840.post_attempt_02_repair_authority.v1"
        or authority.get("stage")
        != "AFTER_ATTEMPT_02_BEFORE_ATTEMPT_03_GPU_EXECUTION"
        or authority.get("status")
        != "FROZEN_BOUNDED_EXECUTABLE_IDENTITY_REPAIR__NO_ACCEPTED_RESULT"
        or authority.get("route_bundle_group_count") != 3
        or authority.get("required_mode_count") != 4
        or authority.get("mode_cases") != prior.get("mode_cases")
        or authority.get("mode_cases") != original.get("mode_cases")
        or authority.get("goal5838_frozen_core")
        != prior.get("goal5838_frozen_core")
        or authority.get("preregistration") != prior.get("preregistration")
    ):
        raise RuntimeError("post-Attempt-02 repair authority contract differs")

    chain = authority.get("base_chain")
    scope = authority.get("repair_scope")
    counts = authority.get("execution_counts_at_repair_freeze")
    if not isinstance(chain, dict) or not isinstance(scope, dict):
        raise RuntimeError("Attempt-02 repair authority chain/scope is absent")
    prior_ref = chain.get("post_attempt_01_repair_authority")
    incident_ref = chain.get("attempt_02_incident")
    formal_counts = chain.get("formal_observed_counts_through_attempt_02")
    diagnostic_counts = chain.get("post_failure_diagnostics")
    if not isinstance(prior_ref, dict) or not isinstance(incident_ref, dict):
        raise RuntimeError("Attempt-02 repair authority references are absent")
    if (
        chain.get("attempt_01_source_commit") != ATTEMPT_01_SOURCE_COMMIT
        or chain.get("attempt_01_repair_commit") != ATTEMPT_02_SOURCE_COMMIT
        or prior_ref
        != {
            "path": str(REPAIR_AUTHORITY.relative_to(ROOT)),
            "bytes": REPAIR_AUTHORITY.stat().st_size,
            "file_sha256": _sha_file(REPAIR_AUTHORITY),
            "authority_sha256": prior.get("authority_sha256"),
        }
        or incident_ref.get("path")
        != str(ATTEMPT_02_INCIDENT.relative_to(ROOT))
        or incident_ref.get("bytes") != ATTEMPT_02_INCIDENT.stat().st_size
        or incident_ref.get("file_sha256") != ATTEMPT_02_INCIDENT_SHA256
        or _sha_file(ATTEMPT_02_INCIDENT) != ATTEMPT_02_INCIDENT_SHA256
        or incident_ref.get("classification")
        != (
            "EVIDENCE_EXECUTABLE_IDENTITY_CANONICALIZATION_"
            "ENGINEERING_FAILURE"
        )
    ):
        raise RuntimeError("Attempt-02 repair authority identity chain differs")
    if formal_counts != {
        "runner_processes_started": 2,
        "frozen_modes_entered": 2,
        "public_route_expected_outputs_returned": 2,
        "published_evidence_bundles": 0,
        "published_independent_property_reports": 0,
        "published_mutation_applications": 0,
        "accepted_positive_evidence_rows": 0,
    } or diagnostic_counts != {
        "diagnostic_processes": 2,
        "diagnostic_mode_executions": 2,
        "diagnostic_expected_outputs_returned": 2,
        "diagnostic_evidence_files_published": 0,
        "accepted_positive_evidence_rows": 0,
    } or counts != {
        "formal_runner_processes": 2,
        "formal_entered_modes": 2,
        "formal_returned_expected_outputs": 2,
        "diagnostic_processes": 2,
        "diagnostic_mode_executions": 2,
        "published_evidence_bundles": 0,
        "published_independent_property_reports": 0,
        "published_mutation_applications": 0,
        "accepted_goal5840_positive_evidence_rows": 0,
    }:
        raise RuntimeError("Attempt-02 repair execution history differs")
    if (
        scope.get("defect")
        != "str_derived_enum_role_stringified_to_enum_qualname"
        or scope.get("repair")
        != "preserve_and_validate_underlying_string_enum_value"
        or scope.get("allowed_changed_paths")
        != list(ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS)
        or scope.get("exact_changed_paths_since_base")
        != list(ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS)
        or any(
            scope.get(field) is not False
            for field in (
                "route_change_allowed",
                "fixture_or_oracle_change_allowed",
                "declaration_or_control_root_change_allowed",
                "property_or_mutation_change_allowed",
                "native_engine_change_allowed",
                "frozen_core_change_allowed",
            )
        )
    ):
        raise RuntimeError("Attempt-02 repair scope differs")
    changed = tuple(sorted(
        line
        for line in _git(
            "diff",
            "--name-only",
            f"{ATTEMPT_02_SOURCE_COMMIT}..{expected_commit}",
            "--",
        ).splitlines()
        if line
    ))
    if changed != ATTEMPT_02_REPAIR_ALLOWED_CHANGED_PATHS:
        raise RuntimeError(f"Attempt-02 committed repair paths differ: {changed!r}")

    source_rows = authority.get("source_files")
    if not isinstance(source_rows, list):
        raise RuntimeError("Attempt-02 repair source inventory is absent")
    observed_paths = set()
    for row in source_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("Attempt-02 repair source row is invalid")
        relative = str(row["path"])
        blob = _git_blob(expected_commit, relative)
        if (
            relative in observed_paths
            or len(blob) != row.get("bytes")
            or hashlib.sha256(blob).hexdigest() != row.get("sha256")
            or (
                require_current_source_match
                and (ROOT / relative).read_bytes() != blob
            )
        ):
            raise RuntimeError(
                f"Attempt-02 repair source custody differs: {relative}"
            )
        observed_paths.add(relative)
    if observed_paths != set(ATTEMPT_02_REPAIR_AUTHORITY_SOURCE_PATHS):
        raise RuntimeError("Attempt-02 repair source denominator differs")

    frozen_preregistration = authority.get("preregistration")
    claims = authority.get("claim_boundary")
    if (
        not isinstance(frozen_preregistration, dict)
        or frozen_preregistration.get("file_sha256")
        != _sha_file(PREREGISTRATION)
        or frozen_preregistration.get("authority_sha256")
        != preregistration.get("authority_sha256")
        or not isinstance(claims, dict)
        or claims.get("append_only_engineering_repair_authority") is not True
        or claims.get("two_prior_formal_failures_preserved") is not True
        or claims.get("diagnostic_launches_not_accepted_as_evidence") is not True
        or claims.get("scientific_inputs_unchanged") is not True
        or claims.get("accepted_goal5840_result") is not False
        or claims.get("lowering_preservation_established") is not False
        or claims.get("performance_or_speedup") is not False
        or claims.get("application_correctness") is not False
        or claims.get("external_review_or_consensus") is not False
    ):
        raise RuntimeError("Attempt-02 repair preregistration/claims differ")
    return authority


def _verify_attempt03_repair_authority(
    original: Mapping[str, object],
    prior: Mapping[str, object],
    preregistration: Mapping[str, object],
    expected_commit: str,
) -> dict[str, object]:
    authority = json.loads(
        ATTEMPT_03_REPAIR_AUTHORITY.read_text(encoding="ascii")
    )
    rebuilt = attempt03_freezer.build_authority(
        str(authority.get("frozen_at_utc"))
    )
    if authority != rebuilt:
        raise RuntimeError("post-Attempt-03 repair authority differs")
    frozen_preregistration = authority.get("preregistration")
    if (
        _git("rev-parse", "HEAD") != expected_commit
        or authority.get("schema")
        != "rtdl.goal5840.post_attempt_03_repair_authority.v1"
        or authority.get("stage")
        != "AFTER_ATTEMPT_03_BEFORE_ATTEMPT_04_GPU_EXECUTION"
        or authority.get("status")
        != "FROZEN_INLINE_SPECIALIZATION_CHECKER_REPAIR__NO_ACCEPTED_RESULT"
        or authority.get("route_bundle_group_count") != 3
        or authority.get("required_mode_count") != 4
        or authority.get("mode_cases") != prior.get("mode_cases")
        or authority.get("mode_cases") != original.get("mode_cases")
        or authority.get("preregistration") != prior.get("preregistration")
        or not isinstance(frozen_preregistration, dict)
        or frozen_preregistration.get("authority_sha256")
        != preregistration.get("authority_sha256")
    ):
        raise RuntimeError("post-Attempt-03 repair authority contract differs")
    claims = authority.get("claim_boundary")
    counts = authority.get("execution_counts_at_repair_freeze")
    if (
        not isinstance(claims, dict)
        or not isinstance(counts, dict)
        or claims.get("three_prior_formal_failures_preserved") is not True
        or claims.get("failure_bundle_and_reject_report_not_accepted") is not True
        or claims.get("scientific_inputs_unchanged") is not True
        or claims.get("accepted_goal5840_result") is not False
        or counts.get("formal_runner_processes") != 3
        or counts.get("published_evidence_bundles") != 1
        or counts.get("published_independent_property_reports") != 1
        or counts.get("independently_accepted_reports") != 0
        or counts.get("accepted_goal5840_positive_evidence_rows") != 0
    ):
        raise RuntimeError("post-Attempt-03 repair history/claims differ")
    return authority


def _verify_attempt04_repair_authority(
    original: Mapping[str, object],
    prior: Mapping[str, object],
    preregistration: Mapping[str, object],
    expected_commit: str,
) -> dict[str, object]:
    authority = json.loads(
        ATTEMPT_04_REPAIR_AUTHORITY.read_text(encoding="ascii")
    )
    rebuilt = attempt04_freezer.build_authority(
        str(authority.get("frozen_at_utc"))
    )
    if authority != rebuilt:
        raise RuntimeError("post-Attempt-04 repair authority differs")
    frozen_preregistration = authority.get("preregistration")
    if (
        _git("rev-parse", "HEAD") != expected_commit
        or authority.get("schema")
        != "rtdl.goal5840.post_attempt_04_repair_authority.v1"
        or authority.get("stage")
        != "AFTER_ATTEMPT_04_BEFORE_ATTEMPT_05_GPU_EXECUTION"
        or authority.get("status")
        != (
            "FROZEN_TRIANGLE_STATUS_FLOW_CHECKER_REPAIR__"
            "NO_COMPLETE_ACCEPTED_RESULT"
        )
        or authority.get("route_bundle_group_count") != 3
        or authority.get("required_mode_count") != 4
        or authority.get("mode_cases") != prior.get("mode_cases")
        or authority.get("mode_cases") != original.get("mode_cases")
        or authority.get("preregistration") != prior.get("preregistration")
        or not isinstance(frozen_preregistration, dict)
        or frozen_preregistration.get("authority_sha256")
        != preregistration.get("authority_sha256")
    ):
        raise RuntimeError("post-Attempt-04 repair authority contract differs")
    claims = authority.get("claim_boundary")
    counts = authority.get("execution_counts_at_repair_freeze")
    if (
        not isinstance(claims, dict)
        or not isinstance(counts, dict)
        or claims.get("four_prior_formal_failures_preserved") is not True
        or claims.get("attempt_04_mode_01_acceptance_preserved") is not True
        or claims.get("attempt_04_incomplete_run_not_accepted_as_goal_result")
        is not True
        or claims.get("scientific_inputs_unchanged") is not True
        or claims.get("accepted_goal5840_result") is not False
        or counts.get("formal_runner_processes") != 4
        or counts.get("published_evidence_bundles") != 3
        or counts.get("published_independent_property_reports") != 3
        or counts.get("independently_accepted_per_mode_reports") != 1
        or counts.get("accepted_goal5840_complete_results") != 0
    ):
        raise RuntimeError("post-Attempt-04 repair history/claims differ")
    return authority


def _verify_native_build(path: Path, native: Path, expected_commit: str) -> dict[str, object]:
    manifest_path = path.expanduser().resolve(strict=True)
    document = json.loads(manifest_path.read_text(encoding="ascii"))
    repository = document.get("repository")
    output = document.get("native_output")
    if not isinstance(repository, dict) or not isinstance(output, dict):
        raise RuntimeError("native build manifest is incomplete")
    body = dict(document)
    observed_result_sha256 = body.get("result_sha256")
    body["result_sha256"] = ""
    if observed_result_sha256 != hashlib.sha256(
        NATIVE_BUILD_DOMAIN + _canonical(body)
    ).hexdigest():
        raise RuntimeError("native build manifest seal differs")
    build_input = document.get("build_input")
    source_rows = repository.get("source_files")
    if not isinstance(build_input, dict) or not isinstance(source_rows, list):
        raise RuntimeError("native build input/source custody is incomplete")
    observed_sources = set()
    for row in source_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("native build source row is invalid")
        relative = str(row["path"])
        source = ROOT / relative
        if (
            relative in observed_sources
            or not source.is_file()
            or source.stat().st_size != row.get("bytes")
            or _sha_file(source) != row.get("sha256")
        ):
            raise RuntimeError(f"native build source custody differs: {relative}")
        observed_sources.add(relative)
    if (
        observed_sources != NATIVE_BUILD_SOURCE_PATHS
        or document.get("build_input_sha256") != _digest(build_input)
        or build_input.get("builder_path")
        != "scripts/goal5838_build_selected_sphere_optix_provider.py"
        or build_input.get("builder_sha256")
        != _sha_file(ROOT / str(build_input["builder_path"]))
    ):
        raise RuntimeError("native build source/input identity differs")
    if (
        document.get("schema")
        != "rtdl.goal5838.selected_sphere_optix_provider_build.v2"
        or document.get("status")
        != "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
        or document.get("all_required_symbols_exported") is not True
        or repository.get("expected_commit") != expected_commit
        or repository.get("head_before") != expected_commit
        or repository.get("head_after") != expected_commit
        or output.get("sha256") != _sha_file(native)
        or output.get("bytes") != native.stat().st_size
        or Path(str(output.get("path"))).resolve() != native
    ):
        raise RuntimeError("native build manifest does not bind commit/DSO")
    return {
        "path": str(manifest_path),
        "bytes": manifest_path.stat().st_size,
        "sha256": _sha_file(manifest_path),
        "schema": document.get("schema"),
        "status": document.get("status"),
        "result_sha256": document.get("result_sha256"),
    }


def _verify_goal5840_native_symbols(native: Path) -> dict[str, object]:
    nm = shutil.which("nm")
    if nm is None:
        raise RuntimeError("nm is required for Goal5840 native ABI verification")
    completed = subprocess.run(
        [nm, "-D", "-g", "--defined-only", str(native)],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"Goal5840 nm check failed: {completed.stderr.strip()}")
    names = sorted({
        line.split()[-1]
        for line in completed.stdout.splitlines()
        if line.split()
    })
    missing = [
        symbol for symbol in GOAL5840_REQUIRED_NATIVE_SYMBOLS
        if symbol not in names
    ]
    if missing:
        raise RuntimeError(f"Goal5840 native ABI symbols are missing: {missing}")
    return {
        "schema": "rtdl.goal5840.required_native_symbols.v1",
        "method": "gnu_nm_dynamic_external_defined_exact_name",
        "required_symbols": list(GOAL5840_REQUIRED_NATIVE_SYMBOLS),
        "all_required_symbols_exported": True,
        "exported_symbol_count": len(names),
        "exported_symbol_names_sha256": _digest(names),
        "nm_path": str(Path(nm).resolve()),
    }


def _write_exclusive(path: Path, value: object) -> None:
    with path.open("x", encoding="ascii") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True))
        stream.write("\n")


def _progress(stage: str, **fields: object) -> None:
    print(json.dumps({"stage": stage, **fields}, sort_keys=True), flush=True)


def _run_checker(
    bundle_path: Path,
    report_path: Path,
    roots: Mapping[str, str],
) -> dict[str, object]:
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            str(CHECKER),
            str(bundle_path),
            "--trusted-declaration-sha256",
            roots["declaration_sha256"],
            "--trusted-executable-identity-sha256",
            roots["executable_identity_sha256"],
            "--trusted-control-flow-manifest-sha256",
            roots["control_flow_manifest_sha256"],
            "--output",
            str(report_path),
        ],
        cwd=ROOT,
        env={"PATH": os.environ.get("PATH", "")},
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"independent checker rejected {bundle_path.name}: "
            f"{completed.stdout}\n{completed.stderr}"
        )
    report = json.loads(report_path.read_text(encoding="ascii"))
    if report.get("verdict") != "ACCEPT" or report.get("pass_count") != 5:
        raise RuntimeError(f"independent checker result differs: {report}")
    return report


def _mode_file_stem(index: int, mode: str) -> str:
    return f"mode_{index:02d}_{mode}"


def run(args: argparse.Namespace) -> dict[str, object]:
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "0":
        raise RuntimeError("CUDA_VISIBLE_DEVICES=0 is required")
    output = _outside_repository(args.output)
    _progress("preflight_started", output=str(output))
    repository = _repository_custody(args.expected_commit)
    frozen_core = _verify_frozen_core()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="ascii"))
    input_authority = _verify_pre_pod_authority()
    repair_authority = _verify_repair_authority(
        input_authority,
        preregistration,
        ATTEMPT_02_SOURCE_COMMIT,
        require_current_source_match=False,
    )
    attempt02_repair_authority = _verify_attempt02_repair_authority(
        input_authority,
        repair_authority,
        preregistration,
        attempt03_freezer.BASE_COMMIT,
        require_current_source_match=False,
    )
    attempt04_repair_authority = _verify_attempt04_repair_authority(
        input_authority,
        attempt02_repair_authority,
        preregistration,
        args.expected_commit,
    )
    attempt03_repair_authority = json.loads(
        ATTEMPT_03_REPAIR_AUTHORITY.read_text(encoding="ascii")
    )
    frozen_preregistration = input_authority.get("preregistration")
    if (
        not isinstance(frozen_preregistration, dict)
        or frozen_preregistration.get("file_sha256")
        != _sha_file(PREREGISTRATION)
        or frozen_preregistration.get("authority_sha256")
        != preregistration.get("authority_sha256")
    ):
        raise RuntimeError("live preregistration differs from pre-pod authority")
    native = args.native.expanduser().resolve(strict=True)
    native_build = _verify_native_build(
        args.native_build_manifest, native, args.expected_commit
    )
    native_symbols = _verify_goal5840_native_symbols(native)
    machine = _machine()
    _progress(
        "preflight_passed",
        gpu=machine["name"],
        compute_capability=machine["compute_capability"],
        native_sha256=_sha_file(native),
    )
    if machine["compute_capability"] != args.compute_capability:
        raise RuntimeError("selected GPU compute capability differs from argument")
    capability = tuple(int(item) for item in args.compute_capability.split("."))
    if len(capability) != 2:
        raise RuntimeError("compute capability must have major.minor form")
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.expanduser().resolve(strict=True),
        cuda_include=args.cuda_include.expanduser().resolve(strict=True),
    )
    stable_target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    sphere_target = V4SphereTarget.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    expected_by_key = {
        row["key"]: row for row in attempt04_repair_authority["mode_cases"]
    }
    if len(expected_by_key) != 4:
        raise RuntimeError("pre-pod authority has duplicate or missing mode keys")
    bundles = []
    bundle_paths = []
    mode_records = []
    trust_roots: dict[str, dict[str, str]] = {}
    declaration_authority = str(preregistration["authority_sha256"])

    for index, case in enumerate(goal5840_mode_cases(), start=1):
        _progress("mode_started", index=index, key=case.key)
        frozen = expected_by_key.get(case.key)
        if not isinstance(frozen, dict):
            raise RuntimeError(f"mode absent from pre-pod authority: {case.key}")
        if frozen.get("plan_sha256") != case.route.plan.plan_sha256:
            raise RuntimeError(f"mode plan differs from pre-pod authority: {case.key}")
        fixture_sha256 = _digest(_jsonable(case.fixture_document))
        expected_output = _jsonable(case.expected_output)
        expected_output_sha256 = _digest(expected_output)
        if (
            frozen.get("fixture_sha256") != fixture_sha256
            or frozen.get("expected_output_sha256") != expected_output_sha256
            or frozen.get("expected_output") != expected_output
        ):
            raise RuntimeError(
                f"fixture/oracle differs from pre-pod authority: {case.key}"
            )
        target = sphere_target if case.target_kind == "sphere" else stable_target
        program = case.route.compile()
        materialized = program.materialize(target=target, toolchain=toolchain)
        prepared = materialized.prepare(case.static_input)
        try:
            result = prepared.execute(case.batch)
            observed_output = _jsonable(result.output)
            if observed_output != expected_output:
                raise RuntimeError(
                    f"output mismatch for {case.key}: "
                    f"{observed_output!r} != {expected_output!r}"
                )
            bundle = capture_real_target_evidence_bundle(
                route_id=case.route_id,
                mode=case.mode,
                route=case.route,
                program=program,
                materialized=materialized,
                result=result,
                target=target,
                toolchain=toolchain,
                declaration_authority_sha256=declaration_authority,
                repository_root=ROOT,
            )
        finally:
            prepared.close()
            prepared.close()

        if bundle["declaration"]["declaration_sha256"] != frozen.get(
            "declaration_sha256"
        ) or bundle["physical_evidence"]["target_control_flow_evidence"][
            "manifest_sha256"
        ] != frozen.get("control_flow_manifest_sha256"):
            raise RuntimeError(f"pre-pod trust root differs for {case.key}")
        stem = _mode_file_stem(index, case.mode)
        bundle_path = output / f"{stem}_bundle.json"
        checker_path = output / f"{stem}_independent_check.json"
        _write_exclusive(bundle_path, bundle)
        roots = {
            "declaration_sha256": bundle["declaration"]["declaration_sha256"],
            "executable_identity_sha256": bundle["physical_evidence"][
                "executable_identity"
            ]["identity_sha256"],
            "control_flow_manifest_sha256": bundle["physical_evidence"][
                "target_control_flow_evidence"
            ]["manifest_sha256"],
        }
        checker_report = _run_checker(bundle_path, checker_path, roots)
        _progress(
            "mode_passed",
            index=index,
            key=case.key,
            bundle_sha256=bundle["bundle_sha256"],
            independent_property_pass_count=checker_report["pass_count"],
        )
        trust_roots[case.key] = roots
        bundles.append(bundle)
        bundle_paths.append(bundle_path)
        mode_records.append({
            "key": case.key,
            "route_id": case.route_id,
            "mode": case.mode,
            "fixture_sha256": fixture_sha256,
            "expected_output": expected_output,
            "expected_output_sha256": _digest(expected_output),
            "observed_output": observed_output,
            "observed_output_sha256": result.output_sha256,
            "bundle_file": bundle_path.name,
            "bundle_sha256": bundle["bundle_sha256"],
            "independent_check_file": checker_path.name,
            "independent_check_sha256": checker_report["report_sha256"],
            "independent_property_pass_count": checker_report["pass_count"],
            "true_optix": (
                result.traversal_receipt.get("physical_executor_classification")
                == "optix_traversal_observed"
            ),
        })

    trust_document: dict[str, object] = {
        "schema": "rtdl.goal5840.runtime_trust_roots.v1",
        "source": (
            "captured_from_live_generic_lifecycle_objects_before_bundle_"
            "independent_check; capture_runner_remains_in_tcb"
        ),
        "trust_roots": trust_roots,
        "claim_boundary": {
            "pre_pod_declaration_and_control_roots": True,
            "post_materialization_executable_identity_root": True,
            "independent_hardware_attestation": False,
        },
        "trust_roots_sha256": "",
    }
    trust_document["trust_roots_sha256"] = hashlib.sha256(
        TRUST_ROOT_DOMAIN + _canonical(trust_document)
    ).hexdigest()
    trust_path = output / "RUNTIME_TRUST_ROOTS.json"
    _write_exclusive(trust_path, trust_document)

    mutation_path = output / "EXACT_BUNDLE_MUTATION_RESULT.json"
    mutation_command = [
        sys.executable,
        "-I",
        str(MUTATION_RUNNER),
        "--trust-roots",
        str(trust_path),
        "--output",
        str(mutation_path),
    ]
    for bundle_path in bundle_paths:
        mutation_command.extend(("--bundle", str(bundle_path)))
    mutation = subprocess.run(
        mutation_command,
        cwd=output,
        env={"PATH": os.environ.get("PATH", "")},
        text=True,
        capture_output=True,
        check=False,
    )
    if mutation.returncode:
        raise RuntimeError(
            f"exact bundle mutation suite failed: {mutation.stdout}\n{mutation.stderr}"
        )
    mutation_report = json.loads(mutation_path.read_text(encoding="ascii"))
    _progress(
        "mutation_suite_passed",
        unique_claim_units=mutation_report["preregistered_claim_unit_count"],
        mode_replications=mutation_report["mode_replication_application_count"],
    )
    repository = _finish_repository_custody(repository, args.expected_commit)
    summary: dict[str, object] = {
        "schema": "rtdl.goal5840.true_optix_target_evidence.v5",
        "status": "PASS__FOUR_MODES_TRUE_OPTIX_AND_15_UNIQUE_MUTATIONS_REJECTED",
        "formal_attempt_number": 5,
        "repository": repository,
        "machine": machine,
        "runtime": {
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numba": importlib.metadata.version("numba"),
            "numpy": importlib.metadata.version("numpy"),
            "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"],
            "optix_sdk": args.optix_sdk,
            "compute_capability": args.compute_capability,
            "optix_include": str(toolchain.optix_include),
            "cuda_include": str(toolchain.cuda_include),
        },
        "native": {
            "path": str(native),
            "bytes": native.stat().st_size,
            "sha256": _sha_file(native),
            "build_manifest": native_build,
            "goal5840_required_symbol_check": native_symbols,
        },
        "preregistration": {
            "path": str(PREREGISTRATION.relative_to(ROOT)),
            "file_sha256": _sha_file(PREREGISTRATION),
            "authority_sha256": preregistration["authority_sha256"],
        },
        "pre_pod_input_authority": {
            "path": str(PRE_POD_AUTHORITY.relative_to(ROOT)),
            "file_sha256": _sha_file(PRE_POD_AUTHORITY),
            "authority_sha256": input_authority["authority_sha256"],
            "source_commit": ATTEMPT_01_SOURCE_COMMIT,
        },
        "attempt_01_engineering_failure": {
            "path": str(ATTEMPT_01_INCIDENT.relative_to(ROOT)),
            "bytes": ATTEMPT_01_INCIDENT.stat().st_size,
            "file_sha256": _sha_file(ATTEMPT_01_INCIDENT),
            "accepted_positive_evidence_rows": 0,
        },
        "post_attempt_01_repair_authority": {
            "path": str(REPAIR_AUTHORITY.relative_to(ROOT)),
            "file_sha256": _sha_file(REPAIR_AUTHORITY),
            "authority_sha256": repair_authority["authority_sha256"],
        },
        "attempt_02_engineering_failure": {
            "path": str(ATTEMPT_02_INCIDENT.relative_to(ROOT)),
            "bytes": ATTEMPT_02_INCIDENT.stat().st_size,
            "file_sha256": _sha_file(ATTEMPT_02_INCIDENT),
            "accepted_positive_evidence_rows": 0,
            "diagnostic_launches_accepted_as_evidence": 0,
        },
        "post_attempt_02_repair_authority": {
            "path": str(ATTEMPT_02_REPAIR_AUTHORITY.relative_to(ROOT)),
            "file_sha256": _sha_file(ATTEMPT_02_REPAIR_AUTHORITY),
            "authority_sha256": attempt02_repair_authority["authority_sha256"],
        },
        "attempt_03_engineering_failure": {
            "path": str(ATTEMPT_03_INCIDENT.relative_to(ROOT)),
            "bytes": ATTEMPT_03_INCIDENT.stat().st_size,
            "file_sha256": _sha_file(ATTEMPT_03_INCIDENT),
            "published_failure_bundle_count": 1,
            "published_reject_report_count": 1,
            "accepted_positive_evidence_rows": 0,
            "post_failure_gpu_diagnostic_launches": 0,
        },
        "post_attempt_03_repair_authority": {
            "path": str(ATTEMPT_03_REPAIR_AUTHORITY.relative_to(ROOT)),
            "file_sha256": _sha_file(ATTEMPT_03_REPAIR_AUTHORITY),
            "authority_sha256": attempt03_repair_authority["authority_sha256"],
        },
        "attempt_04_engineering_failure": {
            "path": str(ATTEMPT_04_INCIDENT.relative_to(ROOT)),
            "bytes": ATTEMPT_04_INCIDENT.stat().st_size,
            "file_sha256": _sha_file(ATTEMPT_04_INCIDENT),
            "published_failure_bundle_count": 2,
            "published_independent_report_count": 2,
            "independently_accepted_per_mode_report_count": 1,
            "accepted_complete_goal5840_result_count": 0,
            "post_failure_gpu_diagnostic_launches": 0,
        },
        "post_attempt_04_repair_authority": {
            "path": str(ATTEMPT_04_REPAIR_AUTHORITY.relative_to(ROOT)),
            "file_sha256": _sha_file(ATTEMPT_04_REPAIR_AUTHORITY),
            "authority_sha256": attempt04_repair_authority["authority_sha256"],
        },
        "frozen_core": frozen_core,
        "route_bundle_group_count": 3,
        "required_mode_bundle_count": len(mode_records),
        "true_optix_mode_count": sum(row["true_optix"] for row in mode_records),
        "independent_property_pass_count": sum(
            int(row["independent_property_pass_count"]) for row in mode_records
        ),
        "preregistered_unique_mutation_count": mutation_report[
            "preregistered_claim_unit_count"
        ],
        "mode_replication_mutation_count": mutation_report[
            "mode_replication_application_count"
        ],
        "mode_cases": mode_records,
        "runtime_trust_roots_file": trust_path.name,
        "runtime_trust_roots_sha256": trust_document["trust_roots_sha256"],
        "mutation_result_file": mutation_path.name,
        "mutation_result_sha256": mutation_report["report_sha256"],
        "claim_boundary": {
            "three_bounded_routes_only": True,
            "four_required_modes": True,
            "target_side_structural_refinement_evidence": True,
            "attempt_01_preserved_as_unaccepted_engineering_failure": True,
            "attempt_02_preserved_as_unaccepted_engineering_failure": True,
            "attempt_03_preserved_as_unaccepted_engineering_failure": True,
            "attempt_04_preserved_as_incomplete_engineering_failure": True,
            "attempt_04_mode_01_acceptance_preserved_without_goal_promotion": (
                True
            ),
            "diagnostic_launches_preserved_as_unaccepted_engineering_work": True,
            "append_only_repair_authority_chain_verified": True,
            "general_compiler_soundness": False,
            "application_correctness": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        },
        "summary_sha256": "",
    }
    if (
        summary["required_mode_bundle_count"] != 4
        or summary["true_optix_mode_count"] != 4
        or summary["independent_property_pass_count"] != 20
        or summary["preregistered_unique_mutation_count"] != 15
        or summary["mode_replication_mutation_count"] != 20
    ):
        raise RuntimeError("Goal5840 positive/mutation denominator differs")
    summary["summary_sha256"] = hashlib.sha256(
        SUMMARY_DOMAIN + _canonical(summary)
    ).hexdigest()
    _write_exclusive(output / "RESULT.json", summary)
    _progress("capture_passed", summary_sha256=summary["summary_sha256"])
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args)
    print(json.dumps({
        "status": result["status"],
        "summary_sha256": result["summary_sha256"],
        "output": str(args.output.expanduser().resolve() / "RESULT.json"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
