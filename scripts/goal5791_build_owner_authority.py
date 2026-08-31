#!/usr/bin/env python3
"""Create one explicitly requested Goal5791 owner authority, CPU-only.

``target-prepare`` seals the owner's assertion that the named create-only
target root is absent and authorizes Stage A with zero workers/timings.  The
target-side prepare entrypoint, not this local CPU-only generator, makes the
live absence observation immediately before it creates that root.  ``formal``
can run only after
the immutable PREPARED/RUNTIME/POSTPREPARE outputs exist and authorizes the
exact 96-worker Stage B.  This program never connects to a POD, creates a
target root, launches a worker, or supplies an authorization default.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil

from scripts import goal5791_formal_contract as contract
from scripts import goal5791_independent_portable_audit as independent_audit
from scripts import goal5791_open_upload_staging as staging_helper
from scripts import goal5791_target_prepare as target_prepare


STAGE_A_REQUEST_SCHEMA = "rtdl.goal5791.owner_target_prepare_request.v1"
STAGE_A_REQUEST_STATUS = (
    "OWNER_REQUESTS_EXACTLY_ONE_CREATE_ONLY_TARGET_PREPARE_AUTHORITY")
STAGE_B_REQUEST_SCHEMA = "rtdl.goal5791.owner_formal_execution_request.v1"
STAGE_B_REQUEST_STATUS = (
    "OWNER_REQUESTS_EXACTLY_ONE_BOUND_GOAL5791_FORMAL_AUTHORITY")
STAGE_A_CONFIRMATIONS = {
    "all_input_paths_and_hashes_reviewed": True,
    "pod_endpoint_and_both_create_only_roots_reviewed": True,
    "upload_staging_and_target_materialization_roots_required_absent_at_first_target_entry": True,
    "exact_staged_upload_relative_paths_reviewed": True,
    "stage_a_only_zero_workers_zero_registered_timings": True,
    "stage_b_authority_not_requested_or_created": True,
    "strict_joint_bundle_home_evidence_audit_reviewed": True,
    "third_paid_transaction_goal5788_a1_correction_justification_reviewed": True,
}
STAGE_B_CONFIRMATIONS = {
    "prepared_runtime_and_postprepare_bytes_reviewed": True,
    "runtime_will_not_be_edited_or_resealed": True,
    "same_stage_a_endpoint_and_target_materialization_root_reviewed": True,
    "distinct_create_only_formal_output_and_controller_staging_roots_reviewed": True,
    "seven_hour_twenty_gb_resources_confirmed_before_worker_zero": True,
    "exact_96_worker_once_only_matrix_requested": True,
    "retry_resume_replacement_relabel_or_row_drop_forbidden": True,
}


class OwnerAuthorityError(RuntimeError):
    pass


def _admit_loaded_generator_modules() -> None:
    scripts_root = Path(__file__).resolve().parent
    expected = {
        Path(contract.__file__).resolve(): scripts_root / (
            "goal5791_formal_contract.py"),
        Path(staging_helper.__file__).resolve(): scripts_root / (
            "goal5791_open_upload_staging.py"),
        Path(independent_audit.__file__).resolve(): scripts_root / (
            "goal5791_independent_portable_audit.py"),
        Path(target_prepare.__file__).resolve(): scripts_root / (
            "goal5791_target_prepare.py"),
    }
    if any(actual != wanted for actual, wanted in expected.items()):
        raise OwnerAuthorityError(
            "owner generator imported a Goal5791 module outside its source")


def _strict_json(path: Path) -> dict[str, object]:
    def pairs(rows):
        value: dict[str, object] = {}
        for key, item in rows:
            if key in value:
                raise OwnerAuthorityError(
                    f"duplicate JSON key in {path}: {key}")
            value[key] = item
        return value

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                OwnerAuthorityError(f"non-finite JSON value: {token}")),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OwnerAuthorityError(f"cannot read strict JSON: {path}") from exc
    if not isinstance(value, dict):
        raise OwnerAuthorityError(f"expected one JSON object: {path}")
    return value


def _exact_keys(value: object, expected: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise OwnerAuthorityError(f"{label} keys drifted")
    return value


def _nonce(value: object, label: str) -> str:
    if not isinstance(value, str) \
            or re.fullmatch(r"[0-9a-f]{64}", value) is None \
            or value == "0" * 64:
        raise OwnerAuthorityError(f"{label} is not a non-placeholder nonce")
    return value


def _sealed_request(
    path: Path, *, schema: str, status: str, keys: set[str],
) -> dict[str, object]:
    value = _strict_json(path)
    _exact_keys(value, keys | {"request_sha256"}, "owner request")
    unsigned = dict(value)
    claimed = unsigned.pop("request_sha256")
    if value.get("schema") != schema or value.get("goal") != 5791 \
            or value.get("status") != status \
            or claimed != contract.digest(unsigned):
        raise OwnerAuthorityError("owner request header/seal drifted")
    _nonce(value.get("owner_authorization_nonce"),
           "owner_authorization_nonce")
    return value


def _write_create_only(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def _require_read_only_authority(path: Path) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o222:
        raise OwnerAuthorityError(
            "owner authority is not a regular non-link read-only file")


def _seal_validated_authority(path: Path) -> None:
    path.chmod(path.stat().st_mode & ~0o222)
    _require_read_only_authority(path)


def _input_paths(value: object, expected: set[str]) -> dict[str, Path]:
    mapping = _exact_keys(value, expected, "request inputs")
    result: dict[str, Path] = {}
    for name, spelling in mapping.items():
        if not isinstance(spelling, str) or not spelling:
            raise OwnerAuthorityError(f"request input path is invalid: {name}")
        supplied = Path(spelling)
        if not supplied.is_absolute() or supplied.is_symlink():
            raise OwnerAuthorityError(
                f"request input is not an absolute non-link path: {name}")
        path = supplied.resolve()
        if not path.is_file():
            raise OwnerAuthorityError(
                f"request input is not one regular file: {name}")
        result[name] = path
    if len(set(result.values())) != len(result):
        raise OwnerAuthorityError("request input paths collide")
    return result


def _endpoint(value: object) -> dict[str, object]:
    raw = _exact_keys(value, {"ssh_user", "host", "port"}, "POD endpoint")
    try:
        return contract.pod_endpoint_identity_record(
            ssh_user=raw["ssh_user"], host=raw["host"], port=raw["port"])
    except contract.Goal5791ContractError as exc:
        raise OwnerAuthorityError("POD endpoint is invalid") from exc


def _remote_root(value: object) -> str:
    if not isinstance(value, str):
        raise OwnerAuthorityError("narrow target root is invalid")
    pure = PurePosixPath(value)
    if pure.as_posix() != value or not pure.is_absolute() \
            or value in ("/", "/root", "/tmp", "/workspace") \
            or any(part in (".", "..") for part in pure.parts) \
            or "goal5791" not in pure.name.lower():
        raise OwnerAuthorityError("target root is not narrow")
    return value


def _resource(value: object, *, formal: bool) -> dict[str, object]:
    if formal:
        result = _exact_keys(value, {
            "owner_confirmed_uninterrupted_window_hours",
            "confirmed_free_disk_bytes",
            "confirmed_before_formal_worker_zero",
        }, "formal resource confirmation")
        window_key = "owner_confirmed_uninterrupted_window_hours"
        boolean_key = "confirmed_before_formal_worker_zero"
        minimum = 7.0
    else:
        result = _exact_keys(value, {
            "owner_confirmed_prepare_window_hours", "confirmed_free_disk_bytes",
            "confirmed_before_target_materialization_root_creation",
        }, "prepare resource confirmation")
        window_key = "owner_confirmed_prepare_window_hours"
        boolean_key = "confirmed_before_target_materialization_root_creation"
        minimum = 1.0
    window = result[window_key]
    disk = result["confirmed_free_disk_bytes"]
    if isinstance(window, bool) or not isinstance(window, (int, float)) \
            or not math.isfinite(float(window)) or float(window) < minimum \
            or isinstance(disk, bool) or not isinstance(disk, int) \
            or disk < 20_000_000_000 or result[boolean_key] is not True:
        raise OwnerAuthorityError("owner resource confirmation is insufficient")
    return deepcopy(result)


def _joint_delivery_audit_record(
    *, inputs: dict[str, Path], expected: object,
) -> dict[str, object]:
    bundle = inputs["bundle"].read_bytes()
    bundle_twin = inputs["bundle_twin"].read_bytes()
    home_evidence = inputs["home_evidence"].read_bytes()
    home_evidence_twin = inputs["home_evidence_twin"].read_bytes()
    if bundle != bundle_twin or home_evidence != home_evidence_twin:
        raise OwnerAuthorityError(
            "joint delivery bundle/Home evidence twins differ")
    try:
        recomputed = independent_audit.joint_bundle_audit_receipt(
            bundle=bundle, bundle_twin=bundle_twin,
            home_evidence=home_evidence,
            home_evidence_twin=home_evidence_twin,
        )
    except independent_audit.IndependentPortableAuditError as exc:
        raise OwnerAuthorityError(
            "strict joint delivery audit failed before Stage-A authority") \
            from exc
    receipt = _strict_json(inputs["joint_bundle_audit_receipt"])
    if receipt != recomputed:
        raise OwnerAuthorityError(
            "joint delivery audit receipt differs from strict recomputation")
    record = {
        "joint_bundle_audit_receipt_file_sha256": target_prepare._sha(
            inputs["joint_bundle_audit_receipt"]),
        "joint_bundle_audit_receipt_sha256": receipt["receipt_sha256"],
        "independent_portable_auditor_sha256": target_prepare._sha(
            Path(independent_audit.__file__).resolve()),
        "bundle_sha256": target_prepare._sha_bytes(bundle),
        "bundle_twin_sha256": target_prepare._sha_bytes(bundle_twin),
        "bundle_twin_byte_identical": True,
        "home_evidence_sha256": target_prepare._sha_bytes(home_evidence),
        "home_evidence_twin_sha256": target_prepare._sha_bytes(
            home_evidence_twin),
        "home_evidence_twin_byte_identical": True,
        "strict_joint_audit_passed": True,
        "home_independent_raw_recount_reexecuted_and_byte_identical": (
            receipt[
                "home_independent_raw_recount_reexecuted_and_byte_identical"]),
    }
    if expected != record:
        raise OwnerAuthorityError(
            "owner-requested joint delivery audit identity drifted")
    return record


def _stage_a_authority(
    *, bundle_sha256: str, source_sha256: str, data_sha256: str,
    wheelhouse_sha256: str, optix_headers_sha256: str,
    pretarget_file_sha256: str, formal_contract_sha256: str,
    schedule_sha256: str, runtime_budget_file_sha256: str,
    token_amendment_sha256: str, required_target: dict[str, object],
    first_entry_stdin_bootstrap: dict[str, object],
    materialization_root: str, upload_staging_root: str,
    endpoint: dict[str, object],
    resource: dict[str, object], nonce: str,
    joint_delivery_audit: dict[str, object],
) -> dict[str, object]:
    body = {
        "schema": target_prepare.OWNER_SCHEMA,
        "goal": 5791,
        "status": target_prepare.OWNER_STATUS,
        "bundle_sha256": bundle_sha256,
        "source_archive_sha256": source_sha256,
        "data_bundle_sha256": data_sha256,
        "wheelhouse_sha256": wheelhouse_sha256,
        "optix_headers_sha256": optix_headers_sha256,
        "pretarget_preexecution_authority_file_sha256": (
            pretarget_file_sha256),
        "formal_contract_sha256": formal_contract_sha256,
        "schedule_sha256": schedule_sha256,
        "runtime_budget_authority_file_sha256": runtime_budget_file_sha256,
        "token_amendment_sha256": token_amendment_sha256,
        "joint_delivery_audit": deepcopy(joint_delivery_audit),
        "required_target": deepcopy(required_target),
        "first_entry_stdin_bootstrap": deepcopy(first_entry_stdin_bootstrap),
        "execution_target": {
            "target_materialization_root": materialization_root,
            "upload_staging_root": upload_staging_root,
            "upload_staging_and_target_materialization_roots_required_absent_at_first_target_entry": True,
            "preexisting_or_shared_roots_allowed": False,
            "pod_endpoint": deepcopy(endpoint),
            "staged_upload_relative_paths": deepcopy(
                target_prepare.STAGED_UPLOAD_RELATIVE_PATHS),
            "upload_staging_cleanup_disposition": (
                target_prepare.UPLOAD_STAGING_CLEANUP_DISPOSITION),
        },
        "resource_confirmation": deepcopy(resource),
        "paid_transaction_justification": deepcopy(
            contract.STAGE_A_THIRD_POD_JUSTIFICATION
        ),
        "owner_authorization_nonce": nonce,
        "authorization": {
            "authorizes_pod_connection": True,
            "authorizes_create_only_upload_staging_root": True,
            "authorizes_exact_staged_uploads": True,
            "authorizes_create_only_target_materialization_root": True,
            "authorizes_exact_target_prepare": True,
            "authorizes_formal_worker_zero": False,
            "authorizes_registered_timing": False,
            "authorizes_owner_formal_authority_creation": False,
            "authorizes_any_other_goal_target_or_matrix": False,
        },
    }
    return {**body, "authority_sha256": contract.digest(body)}


def build_stage_a(request_path: Path, output: Path) -> dict[str, object]:
    _admit_loaded_generator_modules()
    request = _sealed_request(
        request_path, schema=STAGE_A_REQUEST_SCHEMA,
        status=STAGE_A_REQUEST_STATUS,
        keys={
            "schema", "goal", "status", "inputs", "required_target",
            "execution_target", "resource_confirmation",
            "paid_transaction_justification",
            "joint_delivery_audit", "owner_authorization_nonce",
            "confirmations",
        },
    )
    if request["confirmations"] != STAGE_A_CONFIRMATIONS:
        raise OwnerAuthorityError("Stage-A owner confirmations are incomplete")
    if request["paid_transaction_justification"] \
            != contract.STAGE_A_THIRD_POD_JUSTIFICATION:
        raise OwnerAuthorityError(
            "Stage-A third paid-transaction justification drifted")
    inputs = _input_paths(request["inputs"], {
        "bundle", "bundle_twin", "home_evidence", "home_evidence_twin",
        "joint_bundle_audit_receipt", "data_bundle", "wheelhouse",
        "optix_headers", "pretarget",
    })
    joint_delivery_audit = _joint_delivery_audit_record(
        inputs=inputs, expected=request["joint_delivery_audit"])
    outer, manifest = target_prepare._validate_bundle(inputs["bundle"])
    if target_prepare._sha(inputs["data_bundle"]) \
            != target_prepare.EXPECTED_DATA_SHA256 \
            or target_prepare._sha(inputs["wheelhouse"]) \
                != target_prepare.EXPECTED_WHEELHOUSE_SHA256 \
            or target_prepare._sha(inputs["optix_headers"]) \
                != target_prepare.EXPECTED_OPTIX_HEADERS_SHA256 \
            or inputs["pretarget"].read_bytes() \
                != outer["PRETARGET_PREEXECUTION_AUTHORITY.json"]:
        raise OwnerAuthorityError("Stage-A input bytes drifted")
    required_request = _exact_keys(request["required_target"], {
        "gpu_name", "gpu_uuid", "driver_version", "compute_capability",
        "cuda_toolkit_version", "optix_sdk_version",
        "base_python_executable_sha256", "base_python_version",
        "base_python_executable_path",
    }, "required target")
    if required_request["gpu_name"] != "NVIDIA RTX 4000 Ada Generation" \
            or required_request["compute_capability"] != "8.9" \
            or required_request["cuda_toolkit_version"] != "12.8" \
            or required_request["optix_sdk_version"] != "9.0.0" \
            or required_request["base_python_version"] != "3.12.3" \
            or required_request["base_python_executable_path"] \
                != "/usr/bin/python3" \
            or re.fullmatch(
                r"[0-9a-f]{64}",
                str(required_request["base_python_executable_sha256"]),
            ) is None \
            or required_request["base_python_executable_sha256"] == "0" * 64 \
            or not all(isinstance(required_request[name], str)
                       and required_request[name]
                       for name in ("gpu_uuid", "driver_version")):
        raise OwnerAuthorityError("Stage-A required target drifted")
    execution = _exact_keys(request["execution_target"], {
        "target_materialization_root", "upload_staging_root", "pod_endpoint",
    }, "Stage-A execution target")
    materialization_root = _remote_root(
        execution["target_materialization_root"])
    upload_staging_root = _remote_root(execution["upload_staging_root"])
    remote_pure = PurePosixPath(materialization_root)
    staging_pure = PurePosixPath(upload_staging_root)
    if remote_pure == staging_pure or remote_pure in staging_pure.parents \
            or staging_pure in remote_pure.parents:
        raise OwnerAuthorityError(
            "Stage-A upload and materialization roots overlap")
    endpoint = _endpoint(execution["pod_endpoint"])
    required_target = deepcopy(required_request)
    bootstrap_source = staging_helper.FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE
    first_entry_stdin_bootstrap = {
        "source": bootstrap_source,
        "source_sha256": hashlib.sha256(
            bootstrap_source.encode("utf-8")).hexdigest(),
        "actual_source_rehashed_from_proc_cmdline_before_helper_exec": True,
        "honest_owner_exact_ssh_command_is_operational_tcb": True,
    }
    value = _stage_a_authority(
        bundle_sha256=target_prepare._sha(inputs["bundle"]),
        source_sha256=manifest["source_archive_sha256"],
        data_sha256=target_prepare._sha(inputs["data_bundle"]),
        wheelhouse_sha256=target_prepare._sha(inputs["wheelhouse"]),
        optix_headers_sha256=target_prepare._sha(inputs["optix_headers"]),
        pretarget_file_sha256=target_prepare._sha(inputs["pretarget"]),
        formal_contract_sha256=manifest["formal_contract_sha256"],
        schedule_sha256=manifest["schedule_sha256"],
        runtime_budget_file_sha256=target_prepare._sha_bytes(
            outer["RUNTIME_BUDGET.json"]),
        token_amendment_sha256=manifest["token_amendment_sha256"],
        required_target=required_target,
        first_entry_stdin_bootstrap=first_entry_stdin_bootstrap,
        materialization_root=materialization_root,
        upload_staging_root=upload_staging_root,
        endpoint=endpoint,
        resource=_resource(request["resource_confirmation"], formal=False),
        nonce=_nonce(request["owner_authorization_nonce"],
                     "owner_authorization_nonce"),
        joint_delivery_audit=joint_delivery_audit,
    )
    _write_create_only(output, value)
    target_prepare._validate_owner(
        output, bundle_sha=value["bundle_sha256"],
        source_sha=value["source_archive_sha256"],
        materialization_root=materialization_root,
        upload_staging_root=upload_staging_root,
        gpu={
            name: required_target[name] for name in (
                "gpu_name", "gpu_uuid", "driver_version",
                "compute_capability")
        },
        base_python_sha256=required_target["base_python_executable_sha256"],
        base_python_version=required_target["base_python_version"],
        base_python_path=required_target["base_python_executable_path"],
        pod_endpoint=endpoint,
    )
    # Only a semantically validated authority is sealed as an operational
    # output.  The final chmod is deliberately after the strict loader.
    _seal_validated_authority(output)
    return value


def _validate_stage_a_lineage(
    path: Path, *, prepared: dict[str, object], materialization_root: str,
    upload_staging_root: str, endpoint: dict[str, object],
) -> dict[str, object]:
    value = _strict_json(path)
    _exact_keys(value, {
        "schema", "goal", "status", "bundle_sha256",
        "source_archive_sha256", "data_bundle_sha256", "wheelhouse_sha256",
        "optix_headers_sha256",
        "pretarget_preexecution_authority_file_sha256",
        "formal_contract_sha256", "schedule_sha256",
        "runtime_budget_authority_file_sha256", "token_amendment_sha256",
        "joint_delivery_audit",
        "required_target", "first_entry_stdin_bootstrap", "execution_target",
        "resource_confirmation", "paid_transaction_justification",
        "owner_authorization_nonce", "authorization", "authority_sha256",
    }, "Stage-A owner lineage")
    unsigned = dict(value)
    claimed = unsigned.pop("authority_sha256", None)
    if claimed != contract.digest(unsigned) \
            or value.get("schema") != target_prepare.OWNER_SCHEMA \
            or value.get("status") != target_prepare.OWNER_STATUS \
            or value.get("execution_target") != {
                "target_materialization_root": materialization_root,
                "upload_staging_root": upload_staging_root,
                "upload_staging_and_target_materialization_roots_required_absent_at_first_target_entry": True,
                "preexisting_or_shared_roots_allowed": False,
                "pod_endpoint": endpoint,
                "staged_upload_relative_paths": (
                    target_prepare.STAGED_UPLOAD_RELATIVE_PATHS),
                "upload_staging_cleanup_disposition": (
                    target_prepare.UPLOAD_STAGING_CLEANUP_DISPOSITION),
                } \
            or value.get("first_entry_stdin_bootstrap") != {
                "source": staging_helper.FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE,
                "source_sha256": (
                    staging_helper.FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE_SHA256),
                "actual_source_rehashed_from_proc_cmdline_before_helper_exec": True,
                "honest_owner_exact_ssh_command_is_operational_tcb": True,
            } \
            or value.get("authorization", {}).get(
                "authorizes_formal_worker_zero") is not False \
            or value.get("paid_transaction_justification") \
                != contract.STAGE_A_THIRD_POD_JUSTIFICATION \
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
            or target_prepare._sha(path) != prepared.get(
                "owner_target_prepare_authority_file_sha256"):
        raise OwnerAuthorityError("Stage-A owner lineage drifted")
    try:
        target_prepare._validate_joint_delivery_audit_authority(
            value.get("joint_delivery_audit"),
            bundle_sha=str(value.get("bundle_sha256")),
        )
    except PermissionError as exc:
        raise OwnerAuthorityError(
            "Stage-A joint delivery audit lineage drifted") from exc
    return value


def build_stage_b(request_path: Path, output: Path) -> dict[str, object]:
    _admit_loaded_generator_modules()
    request = _sealed_request(
        request_path, schema=STAGE_B_REQUEST_SCHEMA,
        status=STAGE_B_REQUEST_STATUS,
        keys={
            "schema", "goal", "status", "inputs", "execution_target",
            "resource_confirmation", "owner_authorization_nonce",
            "confirmations",
        },
    )
    if request["confirmations"] != STAGE_B_CONFIRMATIONS:
        raise OwnerAuthorityError("Stage-B owner confirmations are incomplete")
    inputs = _input_paths(request["inputs"], {
        "prepared", "runtime", "postprepare_preexecution_authority",
        "stage_a_owner_authority",
    })
    prepared = _strict_json(inputs["prepared"])
    runtime = _strict_json(inputs["runtime"])
    if prepared.get("schema") \
            != "rtdl.goal5791.create_only_target_prepare_result.v1" \
            or prepared.get("status") \
                != "PASS__TARGET_PREPARED__STAGE_B_OWNER_AUTHORITY_ABSENT" \
            or prepared.get("formal_worker_count") != 0 \
            or prepared.get("registered_performance_timing_count") != 0 \
            or prepared.get("owner_stage_b_formal_authority_created") is not False \
            or runtime.get("schema") != "rtdl.goal5791.formal_runtime.v1" \
            or runtime.get("status") \
                != "TARGET_PREPARED__FORMAL_AUTHORITY_STILL_REQUIRED":
        raise OwnerAuthorityError("Stage-B prepared/runtime header drifted")
    prepared_unsigned = dict(prepared)
    prepared_claimed = prepared_unsigned.pop("receipt_sha256", None)
    if prepared_claimed != contract.digest(prepared_unsigned):
        raise OwnerAuthorityError("Stage-B PREPARED receipt seal drifted")
    prepared_record = _exact_keys(prepared.get("prepared_identity_record"), {
        "schema", "runtime_identity_sha256",
        "target_materialization_authority_sha256",
        "target_evidence_archive_sha256",
        "target_functional_summary_sha256",
        "owner_prepare_authority_sha256",
        "upload_staging_identity_sha256", "prepared_identity_sha256",
    }, "Stage-B prepared identity record")
    prepared_preimage = dict(prepared_record)
    prepared_record_sha = prepared_preimage.pop("prepared_identity_sha256")
    if prepared_record.get("schema") \
            != "rtdl.goal5791.prepared_identity.v1" \
            or prepared_record_sha != contract.digest(prepared_preimage) \
            or prepared_record_sha != prepared.get("prepared_identity_sha256") \
            or prepared_record.get("upload_staging_identity_sha256") \
                != prepared.get("upload_staging_identity_sha256") \
            or prepared_record.get("runtime_identity_sha256") \
                != prepared.get("runtime_identity_sha256") \
            or prepared_record.get("owner_prepare_authority_sha256") \
                != prepared.get(
                    "owner_target_prepare_authority_file_sha256") \
            or prepared_record.get(
                "target_materialization_authority_sha256") \
                != prepared.get(
                    "target_materialization_authority_file_sha256") \
            or prepared_record.get("target_evidence_archive_sha256") \
                != prepared.get("target_evidence_archive_file_sha256") \
            or prepared_record.get("target_functional_summary_sha256") \
                != prepared.get("target_functional_summary_file_sha256"):
        raise OwnerAuthorityError("Stage-B prepared identity record drifted")
    runtime_unsigned = dict(runtime)
    runtime_claimed = runtime_unsigned.pop("runtime_sha256", None)
    if runtime_claimed != contract.digest(runtime_unsigned) \
            or target_prepare._sha(inputs["runtime"]) \
                != prepared.get("runtime_file_sha256") \
            or runtime_claimed != prepared.get("runtime_sha256") \
            or inputs["runtime"].stat().st_mode & 0o222 \
            or inputs["prepared"].stat().st_mode & 0o222 \
            or inputs["postprepare_preexecution_authority"].stat().st_mode & 0o222 \
            or inputs["stage_a_owner_authority"].stat().st_mode & 0o222:
        raise OwnerAuthorityError("Stage-B runtime bytes/seal/read-only drifted")
    execution = _exact_keys(request["execution_target"], {
        "target_materialization_root", "create_only_formal_output_root",
        "pod_endpoint",
    }, "Stage-B execution target")
    materialization_root = _remote_root(
        execution["target_materialization_root"])
    formal_output_root = _remote_root(
        execution["create_only_formal_output_root"])
    materialization_pure = PurePosixPath(materialization_root)
    formal_output_pure = PurePosixPath(formal_output_root)
    controller_staging_pure = formal_output_pure.with_name(
        f".{formal_output_pure.name}.goal5791_incomplete")
    controller_staging_root = _remote_root(controller_staging_pure.as_posix())
    if materialization_pure.parent != formal_output_pure.parent \
            or materialization_pure == formal_output_pure \
            or controller_staging_pure.parent != materialization_pure.parent \
            or controller_staging_pure in (
                materialization_pure, formal_output_pure):
        raise OwnerAuthorityError(
            "Stage-B roots are not distinct same-parent siblings")
    endpoint = _endpoint(execution["pod_endpoint"])
    raw_materialization_path = Path(materialization_root)
    root_path = raw_materialization_path.resolve()
    formal_output_path = Path(formal_output_root)
    controller_staging_path = Path(controller_staging_root)
    if raw_materialization_path != root_path \
            or formal_output_path.resolve() != formal_output_path \
            or controller_staging_path.resolve() != controller_staging_path \
            or raw_materialization_path.is_symlink():
        raise OwnerAuthorityError("Stage-B root spelling/resolution drifted")
    result_root = root_path / "result"
    exact_input_paths = {
        "prepared": result_root / "PREPARED.json",
        "runtime": result_root / "RUNTIME.json",
        "postprepare_preexecution_authority": (
            result_root / "GOAL5791_POSTPREPARE_PREEXECUTION_AUTHORITY.json"),
        "stage_a_owner_authority": (
            result_root / "OWNER_TARGET_PREPARE_AUTHORITY.json"),
    }
    expected_output_path = result_root / "OWNER_FORMAL_EXECUTION_AUTHORITY.json"
    if any(inputs[name].resolve() != expected
           for name, expected in exact_input_paths.items()) \
            or output.resolve() != expected_output_path \
            or not result_root.is_dir() or result_root.is_symlink():
        raise OwnerAuthorityError("Stage-B exact input/output paths drifted")
    expected_files = {
        inputs["prepared"].resolve(), inputs["runtime"].resolve(),
        inputs["postprepare_preexecution_authority"].resolve(),
        inputs["stage_a_owner_authority"].resolve(),
    }
    if not root_path.is_dir() or any(
        root_path not in path.parents for path in expected_files
    ) or runtime.get("execution_source_root") != str(root_path / "source") \
            or prepared.get("target_materialization_root") \
                != materialization_root:
        raise OwnerAuthorityError("Stage-B input/root lineage drifted")
    source_root = root_path / "source"
    source_manifest_path = source_root / target_prepare.SOURCE_MANIFEST_MEMBER
    if Path(__file__).resolve() \
            != source_root / "scripts/goal5791_build_owner_authority.py" \
            or Path(contract.__file__).resolve() \
                != source_root / "scripts/goal5791_formal_contract.py" \
            or Path(target_prepare.__file__).resolve() \
                != source_root / "scripts/goal5791_target_prepare.py" \
            or runtime.get("execution_source_manifest_path") \
                != str(source_manifest_path) \
            or runtime.get("execution_source_manifest_file_sha256") \
                != target_prepare._sha(source_manifest_path):
        raise OwnerAuthorityError("Stage-B loaded source entrypoint drifted")
    source_manifest = _strict_json(source_manifest_path)
    try:
        target_prepare._audit_exact_source_set(
            source_root, source_manifest,
            manifest_file_sha256=target_prepare._sha(source_manifest_path),
            require_read_only=True,
        )
    except target_prepare.PrepareError as exc:
        raise OwnerAuthorityError(
            "Stage-B exact read-only source admission failed") from exc
    formal_environment = runtime.get("formal_worker_environment")
    if not isinstance(formal_environment, dict) \
            or dict(os.environ) != formal_environment \
            or "CUPY_CACHE_DIR" in formal_environment \
            or "NUMBA_CACHE_DIR" in formal_environment:
        raise OwnerAuthorityError(
            "Stage-B builder environment is not exact frozen-14 env")
    if prepared.get("pod_endpoint") != endpoint:
        raise OwnerAuthorityError("Stage-B endpoint differs from Stage A")
    upload_staging_root = prepared.get("upload_staging_root")
    upload_staging_pure = (
        PurePosixPath(upload_staging_root)
        if isinstance(upload_staging_root, str) else None)
    if not isinstance(upload_staging_root, str) \
            or _remote_root(upload_staging_root) != upload_staging_root \
            or any(
                upload_staging_pure == candidate
                or upload_staging_pure in candidate.parents
                or candidate in upload_staging_pure.parents
                for candidate in (
                    formal_output_pure, controller_staging_pure,
                    materialization_pure,
                )
            ):
        raise OwnerAuthorityError("Stage-B staging lineage drifted")
    _validate_stage_a_lineage(
        inputs["stage_a_owner_authority"], prepared=prepared,
        materialization_root=materialization_root,
        upload_staging_root=upload_staging_root,
        endpoint=endpoint,
    )
    if os.path.lexists(formal_output_path) \
            or os.path.lexists(controller_staging_path):
        raise OwnerAuthorityError(
            "Stage-B formal output or controller staging root already exists")
    formal_output_parent = formal_output_path.parent.resolve()
    if formal_output_parent != root_path.parent.resolve() \
            or not formal_output_parent.is_dir() \
            or formal_output_parent.is_symlink():
        raise OwnerAuthorityError("Stage-B formal output parent drifted")
    resource_confirmation = _resource(
        request["resource_confirmation"], formal=True)
    observed_free_bytes = shutil.disk_usage(formal_output_parent).free
    if observed_free_bytes < resource_confirmation[
            "confirmed_free_disk_bytes"] \
            or observed_free_bytes < 20_000_000_000:
        raise OwnerAuthorityError("Stage-B live capacity admission failed")
    resource_confirmation.update({
        "formal_output_parent_resolved_path": str(formal_output_parent),
        "formal_output_parent_free_bytes_observed_at_authority_creation": (
            observed_free_bytes),
        "minimum_required_free_disk_bytes": 20_000_000_000,
    })
    post_path = inputs["postprepare_preexecution_authority"]
    post = contract.load_preexecution_authority(
        post_path, repository_root=root_path / "source",
        require_target_binding=True,
    )
    target = post["target_materialization_binding"]
    if not isinstance(target, dict) or (
        target.get("binding_sha256")
            != prepared.get("target_materialization_binding_sha256")
        or target.get("hashes", {}).get("formal_identity_sha256")
            != prepared.get("formal_identity_sha256")
        or runtime.get("preexecution_authority_file_sha256")
            != target_prepare._sha(post_path)
        or runtime.get("target_materialization_binding_sha256")
            != target.get("binding_sha256")
        or runtime.get("formal_identity_sha256")
            != prepared.get("formal_identity_sha256")
    ):
        raise OwnerAuthorityError("Stage-B target/formal identity drifted")
    body = {
        "schema": contract.OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA,
        "goal": 5791,
        "status": contract.OWNER_FORMAL_EXECUTION_STATUS,
        "formal_contract_sha256": contract.contract_sha256(),
        "schedule_sha256": contract.schedule_sha256(),
        "preexecution_authority_file_sha256": target_prepare._sha(post_path),
        "target_materialization_binding_sha256": target["binding_sha256"],
        "formal_identity_sha256": prepared["formal_identity_sha256"],
        "runtime_budget_authority_sha256": post["authority_records"]
            ["runtime_budget_authority"]["sha256"],
        "runtime_file_sha256": target_prepare._sha(inputs["runtime"]),
        "runtime_sha256": runtime["runtime_sha256"],
        "owner_authorization_nonce": _nonce(
            request["owner_authorization_nonce"],
            "owner_authorization_nonce"),
        "independent_row_count": len(contract.statistical_rows()),
        "formal_worker_count": len(contract.schedule()),
        "resource_confirmation": resource_confirmation,
        "execution_target": {
            "target_materialization_root": materialization_root,
            "create_only_formal_output_root": formal_output_root,
            "controller_incomplete_staging_root": controller_staging_root,
            "pod_endpoint": endpoint,
            "target_materialization_root_observed_existing_and_bound_at_authority_creation": True,
            "formal_output_root_observed_absent_at_authority_creation": True,
            "controller_incomplete_staging_root_observed_absent_at_authority_creation": True,
            "preexisting_or_shared_formal_output_root_allowed": False,
        },
        "execution_policy": deepcopy(contract.FORMAL_EXECUTION_POLICY),
        "authorization": deepcopy(contract.FORMAL_AUTHORIZATION),
    }
    value = {**body, "authority_sha256": contract.digest(body)}
    _write_create_only(output, value)
    contract.load_owner_formal_execution_authority(
        output, preexecution_authority_path=post_path,
        repository_root=root_path / "source",
    )
    # The controller rejects a writable formal authority before its marker.
    # Seal only after the final shared-contract validation has succeeded.
    _seal_validated_authority(output)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", required=True, choices=("target-prepare", "formal"))
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    if args.mode == "target-prepare":
        value = build_stage_a(args.request.resolve(), args.output.resolve())
    else:
        value = build_stage_b(args.request.resolve(), args.output.resolve())
    print(json.dumps({
        "mode": args.mode,
        "output": str(args.output.resolve()),
        "authority_sha256": value["authority_sha256"],
        "formal_worker_count_authorized": (
            value.get("formal_worker_count", 0)),
        "generator_connected_to_pod": False,
        "generator_executed_worker": False,
        "generator_created_registered_timing": False,
        "output_regular_nonlink_read_only": (
            args.output.is_file() and not args.output.is_symlink()
            and args.output.stat().st_mode & 0o222 == 0),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
