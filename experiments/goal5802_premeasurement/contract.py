"""Fail-closed Goal5802 premeasurement contract and schedule.

The contract is executable policy, not an execution authorization.  A later
controller must bind the whole frozen JSON file and a separate owner execution
authority before it can launch worker zero.
"""

from __future__ import annotations

import base64
import hashlib
import itertools
import json
from datetime import datetime
from pathlib import Path
import random
import subprocess
from typing import Any, Mapping

from .direct_source_audit import audit_direct_source
from .successor_forecast import (
    OPERATION_FORECAST_PROJECTION,
    SuccessorForecastError,
    validate_successor_forecast,
)
from .workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    canonical,
    digest,
    workload_authority,
)


SCHEMA = "rtdl.goal5802.local_premeasurement_freeze.v3"
ARMS = (
    "A_DIRECT_CUDA_OPTIX",
    "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY",
    "D_RTDL_CLEAN_INSTALLED_RTLEXE",
)
DIRECT, PYOPTIX, RTDL = ARMS
TASKS = (RELATION_TASK, TRIANGLE_TASK)
REGIMES = ("DEPLOYMENT_COLD", "PREPARE", "STEADY_E2E")
BLOCK_COUNT = 24
BUILD_COLD_BLOCK_COUNT = 12
STEADY_WARMUPS = 8
STEADY_REPETITIONS = 64
SCHEDULE_SEED = 58_020_240
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED_BASE = 58_020_000

LEGACY_WORKERS = (
    "experiments/goal5798_premeasurement/rtdl_worker.py",
    "experiments/goal5798_premeasurement/pyoptix_worker.py",
    "experiments/goal5798_premeasurement/direct_measurement.cpp",
)
PREDICTION_FREEZE = (
    "history/internal_docs/"
    "goal5802_premeasurement_three_survival_question_prediction_freeze_"
    "20260824.json"
)
PREDICTION_AUTHORITY_COMMIT = "c064fab001469a69e29219e24d2059c75316d0c2"
PREDICTION_AUTHORITY_GIT_BLOB = "a3818a4bce842d7ab30986c2cd0b5c8f11a1a654"
PREDICTION_AUTHORITY_BYTES = 10_538
PREDICTION_AUTHORITY_SHA256 = (
    "45812c3a5a371615752096e95f5156ded5ac7d19ed53466ed03239d6622855b6")


class ContractError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        digest_value = hashlib.sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest_value.update(block)
    return digest_value.hexdigest()


def _source_record(root: Path, relative: str) -> dict[str, object]:
    path = root / relative
    if not path.is_file():
        raise ContractError(f"required source absent: {relative}")
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _canonical_utf8_lf(path: Path, *, label: str) -> bytes:
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise ContractError(f"{label} is not readable UTF-8 text") from error
    canonical_text = text.replace("\r\n", "\n")
    if "\r" in canonical_text:
        raise ContractError(f"{label} has an unsupported bare CR")
    return canonical_text.encode("utf-8")


def _git_object_sha1(kind: str, payload: bytes) -> str:
    return hashlib.sha1(
        f"{kind} {len(payload)}\0".encode("ascii") + payload).hexdigest()


def _git_cat_file(root: Path, kind: str, object_id: str) -> bytes:
    """Read and rehash one exact object from the repository object database."""

    if kind not in {"commit", "tree"}:
        raise ContractError("unsupported historical Git proof object kind")
    try:
        observed_kind = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-t", object_id],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout.decode("ascii").strip()
        payload = subprocess.run(
            ["git", "-C", str(root), "cat-file", kind, object_id],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError, UnicodeError) as error:
        raise ContractError(
            "historical prediction Git object is unavailable") from error
    if observed_kind != kind or _git_object_sha1(kind, payload) != object_id:
        raise ContractError("historical prediction Git object rehash differs")
    return payload


def _parse_git_tree(payload: bytes) -> list[tuple[str, str, str]]:
    """Parse raw Git tree bytes without trusting ``git ls-tree`` text output."""

    rows: list[tuple[str, str, str]] = []
    cursor = 0
    while cursor < len(payload):
        space = payload.find(b" ", cursor)
        nul = payload.find(b"\0", space + 1)
        if space <= cursor or nul <= space or nul + 21 > len(payload):
            raise ContractError("historical prediction Git tree is malformed")
        try:
            mode = payload[cursor:space].decode("ascii")
            name = payload[space + 1:nul].decode("utf-8")
        except UnicodeError as error:
            raise ContractError(
                "historical prediction Git tree name is invalid") from error
        object_id = payload[nul + 1:nul + 21].hex()
        rows.append((mode, name, object_id))
        cursor = nul + 21
    if cursor != len(payload) or not rows:
        raise ContractError("historical prediction Git tree is malformed")
    return rows


def _build_prediction_git_path_proof(root: Path) -> dict[str, object]:
    """Build a self-contained commit/tree proof for the predecessor forecast."""

    commit_payload = _git_cat_file(
        root, "commit", PREDICTION_AUTHORITY_COMMIT)
    first_line = commit_payload.split(b"\n", 1)[0]
    if not first_line.startswith(b"tree ") or len(first_line) != 45:
        raise ContractError("historical prediction commit has no exact root tree")
    try:
        current_tree = first_line[5:].decode("ascii")
    except UnicodeError as error:
        raise ContractError(
            "historical prediction root tree is invalid") from error
    if any(ch not in "0123456789abcdef" for ch in current_tree):
        raise ContractError("historical prediction root tree is invalid")

    components = Path(PREDICTION_FREEZE).parts
    proof_rows: list[dict[str, object]] = []
    for index, component in enumerate(components):
        tree_payload = _git_cat_file(root, "tree", current_tree)
        matches = [row for row in _parse_git_tree(tree_payload)
                   if row[1] == component]
        if len(matches) != 1:
            raise ContractError(
                "historical prediction path is absent or ambiguous")
        mode, _, selected_object = matches[0]
        is_final = index == len(components) - 1
        expected_kind = "blob" if is_final else "tree"
        if (is_final and mode != "100644") \
                or (not is_final and mode not in {"40000", "040000"}):
            raise ContractError("historical prediction path mode differs")
        proof_rows.append({
            "component": component,
            "tree_sha1": current_tree,
            "tree_object_base64": base64.b64encode(
                tree_payload).decode("ascii"),
            "selected_mode": mode,
            "selected_kind": expected_kind,
            "selected_object_sha1": selected_object,
        })
        current_tree = selected_object
    if current_tree != PREDICTION_AUTHORITY_GIT_BLOB:
        raise ContractError("historical prediction path selects another blob")
    return {
        "proof_schema": "rtdl.goal5802.git_commit_path_proof.v1",
        "commit_object_base64": base64.b64encode(
            commit_payload).decode("ascii"),
        "root_tree_sha1": proof_rows[0]["tree_sha1"],
        "path_components": list(components),
        "tree_path_proof": proof_rows,
        "offline_commit_tree_blob_chain_rehash_required": True,
    }


def _balanced_orders(task: str, regime: str) -> list[tuple[str, ...]]:
    permutations = list(itertools.permutations(ARMS))
    seed_bytes = hashlib.sha256(
        canonical({
            "domain": "GOAL5802-BALANCED-ORDER-V1",
            "seed": SCHEDULE_SEED,
            "task": task,
            "regime": regime,
        })
    ).digest()
    generator = random.Random(int.from_bytes(seed_bytes, "big"))
    result: list[tuple[str, ...]] = []
    for _ in range(BLOCK_COUNT // len(permutations)):
        batch = list(permutations)
        generator.shuffle(batch)
        result.extend(batch)
    if len(result) != BLOCK_COUNT:
        raise ContractError("block count must be divisible by six")
    return result


def build_schedule() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    ordinal = 0
    for task in TASKS:
        for regime in REGIMES:
            for block, order in enumerate(_balanced_orders(task, regime), 1):
                for position, arm in enumerate(order, 1):
                    ordinal += 1
                    rows.append({
                        "ordinal": ordinal,
                        "worker_id": (
                            f"G5802_{ordinal:04d}_{task}_{regime}_{arm}"),
                        "task": task,
                        "regime": regime,
                        "block": block,
                        "position": position,
                        "arm": arm,
                    })
    if len(rows) != len(TASKS) * len(REGIMES) * BLOCK_COUNT * len(ARMS):
        raise ContractError("schedule row count drift")
    return rows


def build_cold_schedule() -> list[dict[str, object]]:
    """Separate absolute diagnostic; these rows never enter noninferiority."""

    rows: list[dict[str, object]] = []
    ordinal = 0
    permutations = list(itertools.permutations(ARMS))
    for task in TASKS:
        seed_bytes = hashlib.sha256(canonical({
            "domain": "GOAL5802-BUILD-COLD-BALANCED-ORDER-V1",
            "seed": SCHEDULE_SEED,
            "task": task,
        })).digest()
        generator = random.Random(int.from_bytes(seed_bytes, "big"))
        orders: list[tuple[str, ...]] = []
        for _ in range(BUILD_COLD_BLOCK_COUNT // len(permutations)):
            batch = list(permutations)
            generator.shuffle(batch)
            orders.extend(batch)
        if len(orders) != BUILD_COLD_BLOCK_COUNT:
            raise ContractError("BUILD_COLD block count must be divisible by six")
        for block, order in enumerate(orders, 1):
            for position, arm in enumerate(order, 1):
                ordinal += 1
                rows.append({
                    "ordinal": ordinal,
                    "worker_id": f"G5802_BUILD_{ordinal:04d}_{task}_{arm}",
                    "task": task,
                    "regime": "BUILD_COLD_ABSOLUTE_DIAGNOSTIC",
                    "block": block,
                    "position": position,
                    "arm": arm,
                })
    expected = len(TASKS) * BUILD_COLD_BLOCK_COUNT * len(ARMS)
    if len(rows) != expected:
        raise ContractError("BUILD_COLD schedule row count drift")
    return rows


def operation_contract() -> dict[str, object]:
    """Freeze the exact dynamic work required from all three measured arms."""

    relation_common = {
        "optix_launch_count": 2,
        "semantic_compaction_launch_count": 1,
        "semantic_compaction_key_capacity": 8192,
        "semantic_compaction_scratch_bytes": 98312,
        "compact_status_control_d2h_bytes": 16,
        "application_output_d2h_bytes": 32768,
        "total_success_d2h_bytes": 32784,
        # These are the status gate and application-output gate.  Dynamic
        # source setup is separately counted below and may not be hidden here.
        "status_output_commit_blocking_boundary_count": 2,
        "per_ray_d2h_bytes": 0,
    }
    triangle_common = {
        "optix_launch_count": 1,
        "compact_status_control_d2h_bytes": 4,
        "application_output_d2h_bytes": 8,
        "total_success_d2h_bytes": 12,
        "status_output_commit_blocking_boundary_count": 2,
        "per_ray_d2h_bytes": 0,
    }
    return {
        "schema": "rtdl.goal5802.three_arm_operation_contract.v1",
        "status": "EXACT_DYNAMIC_WORK_TARGET__PREWORKER_KAT_REQUIRED",
        "forecast_cost_projection": dict(OPERATION_FORECAST_PROJECTION),
        "common_semantics": {
            "relation_user_visible_product": (
                "canonical_sorted_unique_u32_pair_rows"),
            "triangle_user_visible_product": "checked_u64_scalar",
            "triangle_per_ray_host_output": False,
            "triangle_per_ray_d2h_bytes": 0,
            "status_must_be_consumed_before_scalar": True,
            "optix_traversal_launch_count_is_task_specific": True,
            "oracle_comparison_inside_steady_e2e_timer": True,
            "receipt_serialization_inside_timer": False,
            "forensic_hashing_inside_timer": False,
            "failed_compact_status_forbids_application_output_d2h": True,
            "relation_raw_capacity_equals_two_times_semantic_capacity": True,
            "relation_k_plus_one_unique_device_failure_kat_required": True,
            "relation_k_plus_one_application_output_d2h_bytes_required": 0,
            "relation_control_layout_u32": [
                "raw_event_count", "unique_event_count", "overflowed",
                "status"],
            "relation_device_semantic_compaction_required": True,
        },
        "relation": {
            "analytic_expected_unique_rows": 4096,
            "expected_raw_two_orientation_rows": 8192,
            "user_visible_output_bytes": 32768,
            **{arm: dict(relation_common) for arm in ARMS},
        },
        "triangle": {
            **{arm: dict(triangle_common) for arm in ARMS},
        },
        "synchronization_ruling": {
            "same_status_then_output_semantics_required": True,
            "same_status_output_commit_blocking_boundary_count_required": 2,
            "raw_host_blocking_boundary_counts_claimed_equal": False,
            "raw_total_blocking_boundary_count_known": False,
            "allocator_and_api_internal_blocking_excluded_from_commit_count": True,
            "raw_per_arm_counts_and_bytes_must_be_published": True,
            "goal5799_same_sync_counts_literal_narrowed": True,
            "baseline_padding_to_match_rtdl_allowed": False,
            "rtdl_compact_status_abi_successor_required": True,
        },
        "unmatched_internal_work": {
            "device_internal_or_h2d_counts_may_differ": True,
            "every_observed_arm_specific_count_must_be_published": True,
            "rtdl_internal_helper_kernel_counts_must_be_published": True,
            "difference_may_not_be_removed_from_timer": True,
            "causal_attribution_from_difference_alone": False,
            "exact_per_arm_success_path": {
                DIRECT: {
                    "relation_auxiliary_cuda_kernel_launch_count": 1,
                    "triangle_auxiliary_cuda_kernel_launch_count": 0,
                    "relation_stream_ordered_memset_call_count": 4,
                    "triangle_stream_ordered_memset_call_count": 3,
                    "relation_execution_parameter_h2d_bytes": 240,
                    "triangle_execution_parameter_h2d_bytes": 120,
                },
                PYOPTIX: {
                    "relation_auxiliary_cuda_kernel_launch_count": 1,
                    "triangle_auxiliary_cuda_kernel_launch_count": 0,
                    "relation_stream_ordered_memset_call_count": 4,
                    "triangle_stream_ordered_memset_call_count": 3,
                    "relation_execution_parameter_h2d_bytes": 240,
                    "triangle_execution_parameter_h2d_bytes": 120,
                },
                RTDL: {
                    "relation_auxiliary_cuda_kernel_launch_count": 7,
                    "triangle_auxiliary_cuda_kernel_launch_count": 6,
                    "relation_stream_ordered_memset_call_count": 9,
                    "triangle_stream_ordered_memset_call_count": 4,
                    "relation_execution_parameter_h2d_bytes": 224,
                    "triangle_execution_parameter_h2d_bytes": 200,
                },
            },
        },
        "dynamic_input_lifecycle": {
            "public_rtdl_prepare_call_accepts_static_input_only": True,
            "dynamic_host_batch_materialized_and_retained_during_prepare": True,
            "dynamic_device_representation_absent_at_prepare_return": True,
            "dynamic_device_upload_and_dynamic_gas_first_execute": True,
            "first_execute_by_arm": {
                DIRECT: {
                    "relation": {
                        "dynamic_device_upload_call_count": 2,
                        "dynamic_device_upload_bytes": 212992,
                        "dynamic_accel_build_count": 1,
                    },
                    "triangle": {
                        "dynamic_device_upload_call_count": 2,
                        "dynamic_device_upload_bytes": 524288,
                        "dynamic_accel_build_count": 0,
                    },
                },
                PYOPTIX: {
                    "relation": {
                        "dynamic_device_upload_call_count": 2,
                        "dynamic_device_upload_bytes": 212992,
                        "dynamic_accel_build_count": 1,
                    },
                    "triangle": {
                        "dynamic_device_upload_call_count": 2,
                        "dynamic_device_upload_bytes": 524288,
                        "dynamic_accel_build_count": 0,
                    },
                },
                RTDL: {
                    "relation": {
                        "dynamic_device_upload_call_count": 2,
                        "dynamic_device_upload_bytes": 212992,
                        "dynamic_accel_build_count": 1,
                    },
                    # The clean product's generic triangle ABI uploads seven
                    # SoA float columns (including per-query tmax) plus weights.
                    # This real product cost is published, never rewritten to
                    # resemble the two-buffer baseline representation.
                    "triangle": {
                        "dynamic_device_upload_call_count": 8,
                        "dynamic_device_upload_bytes": 589824,
                        "dynamic_accel_build_count": 0,
                    },
                },
            },
            "first_execute_common": {
                "prepared_input_reused": False,
                "dynamic_input_generation": 1,
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
            },
            "every_later_execute": {
                "prepared_input_reused": True,
                "dynamic_device_upload_call_count": 0,
                "dynamic_device_upload_bytes": 0,
                "dynamic_accel_build_count": 0,
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "dynamic_input_generation": 1,
            },
            "regime_receipt_counts": {
                "DEPLOYMENT_COLD": 1,
                "PREPARE": 1,
                "STEADY_E2E": STEADY_WARMUPS + STEADY_REPETITIONS,
            },
            "first_execute_is_never_untimed_priming_before_deployment_cold": True,
            "setup_sync_may_not_be_omitted_from_total_sync_claim": True,
            "target_status_output_commit_blocking_boundaries_per_execute": 2,
            "machine_receipt_and_exact_source_guard_required": True,
        },
    }


def _validate_product_binding(
        binding: Mapping[str, Any], root: Path | None = None) -> dict[str, Any]:
    required = {
        "schema", "status", "clean_install_verifier_status", "wheel_sha256",
        "clean_install_verifier_sha256", "clean_install_run_sha256",
        "clean_install_result_sha256",
        "native_sha256", "trust_root_sha256", "trust_head_sha256",
        "native_custody_verifier_status", "native_custody_verifier_sha256",
        "native_custody_manifest_sha256", "native_custody_custody_sha256",
        "native_custody_source_file_count",
        "native_custody_dependency_file_count",
        "native_custody_toolchain_payload_count",
        "native_custody_source_commit", "native_custody_source_tree",
        "native_custody_hermetic_native_rebuild_claimed",
        "trust_predecessor_package_sha256", "trust_package_sha256",
        "triangle_artifact_sha256",
        "triangle_authority_sha256", "triangle_deployment_id",
        "triangle_executable_identity_sha256",
        "relation_artifact_sha256", "relation_authority_sha256",
        "relation_deployment_id", "relation_executable_identity_sha256",
        "source_commit", "source_tree",
        "source_package_file_count", "rtdsl_package_file_count",
        "rtdsl_package_tree_sha256", "rtdsl_init_sha256",
        "rtdlexe_module_sha256",
    }
    if set(binding) != required:
        raise ContractError(
            f"product binding keys differ: {sorted(set(binding) ^ required)}")
    if binding["schema"] != "rtdl.goal5802.final_clean_rtdlexe_binding.v4" \
            or binding["status"] != "PASS__FINAL_CLEAN_INSTALLED_RTLEXE" \
            or binding["clean_install_verifier_status"] \
            != "PASS__INDEPENDENT_CLEAN_INSTALL_V3_VERIFICATION" \
            or binding["native_custody_verifier_status"] \
            != "PASS__INDEPENDENT_NATIVE_CUSTODY_VERIFICATION" \
            or binding["native_custody_hermetic_native_rebuild_claimed"] is not False:
        raise ContractError("final clean-install binding is not a pass")
    for key in required:
        if key.endswith("_sha256"):
            value = binding[key]
            if not isinstance(value, str) or len(value) != 64 \
                    or any(ch not in "0123456789abcdef" for ch in value):
                raise ContractError(f"invalid product binding digest: {key}")
    for key in ("source_package_file_count", "rtdsl_package_file_count"):
        if type(binding[key]) is not int or binding[key] <= 0:
            raise ContractError(f"invalid source package file count: {key}")
    if binding["source_package_file_count"] \
            != binding["rtdsl_package_file_count"]:
        raise ContractError("wheel/source package file counts differ")
    for key in (
            "native_custody_source_file_count",
            "native_custody_dependency_file_count",
            "native_custody_toolchain_payload_count"):
        if type(binding[key]) is not int or binding[key] <= 0:
            raise ContractError(f"invalid native-custody count: {key}")
    for key in ("source_commit", "source_tree",
                "native_custody_source_commit", "native_custody_source_tree"):
        value = binding[key]
        if not isinstance(value, str) or len(value) != 40 \
                or any(ch not in "0123456789abcdef" for ch in value):
            raise ContractError(f"invalid product binding Git identity: {key}")
    if binding["native_custody_source_commit"] != binding["source_commit"] \
            or binding["native_custody_source_tree"] != binding["source_tree"]:
        raise ContractError("native custody differs from final product Git identity")
    if root is not None:
        cross_bindings = {
            "clean_install_verifier_sha256": (
                "scripts/goal5801_a3_verify_clean_install.py"),
            "native_custody_verifier_sha256": (
                "scripts/goal5801_a3_verify_native_custody.py"),
            "rtdsl_init_sha256": "src/rtdsl/__init__.py",
            "rtdlexe_module_sha256": "src/rtdsl/v4_rtdlexe.py",
        }
        for key, relative in cross_bindings.items():
            if binding[key] != _source_record(root, relative)["sha256"]:
                raise ContractError(
                    f"product binding/source cross-binding differs: {key}")
    return dict(binding)


def _bind_premeasurement_prediction(
        root: Path, product_binding: Mapping[str, Any]) -> dict[str, object]:
    """Bind the unchanged pre-final prediction to the final product identity.

    The probability values stay exclusively in the earlier sealed document.
    This successor records no revised probability and therefore cannot quietly
    move the forecast after the final implementation became visible.
    """

    path = root / PREDICTION_FREEZE
    prediction_bytes = _canonical_utf8_lf(
        path, label="premeasurement prediction")
    prediction_sha = hashlib.sha256(prediction_bytes).hexdigest()
    prediction_blob = hashlib.sha1(
        f"blob {len(prediction_bytes)}\0".encode("ascii")
        + prediction_bytes).hexdigest()
    if len(prediction_bytes) != PREDICTION_AUTHORITY_BYTES \
            or prediction_sha != PREDICTION_AUTHORITY_SHA256 \
            or prediction_blob != PREDICTION_AUTHORITY_GIT_BLOB:
        raise ContractError("premeasurement historical authority tuple differs")
    try:
        prediction = json.loads(prediction_bytes)
    except json.JSONDecodeError as error:
        raise ContractError("premeasurement prediction cannot be loaded") from error
    if not isinstance(prediction, Mapping) \
            or prediction.get("schema") \
            != "rtdl.goal5802.three_survival_question_prediction_freeze.v1" \
            or prediction.get("status") \
            != ("PREMEASUREMENT_PREDICTION_FROZEN__ZERO_NEW_TIMINGS__"
                "FORMAL_EXECUTION_LOCKED"):
        raise ContractError("premeasurement prediction envelope differs")
    authorization = prediction.get("authorization")
    if not isinstance(authorization, Mapping) \
            or type(authorization.get("new_registered_timing_count")) is not int \
            or authorization.get("new_registered_timing_count") != 0 \
            or authorization.get("formal_worker_zero_authorized") is not False \
            or authorization.get("pod_or_modern_rtx_timing_authorized") is not False \
            or authorization.get(
                "prediction_change_after_formal_result_allowed") is not False:
        raise ContractError("premeasurement prediction authorization differs")
    questions = prediction.get("survival_questions")
    if not isinstance(questions, Mapping) or set(questions) != {
            "Q1_public_system", "Q2_owl_pyoptix_residual_novelty",
            "Q3_performance_noninferiority"}:
        raise ContractError("premeasurement survival-question set differs")
    basis = prediction.get("evidence_basis")
    if not isinstance(basis, list) or not basis:
        raise ContractError("premeasurement evidence basis absent")
    transported_basis = []
    for row in basis:
        if not isinstance(row, Mapping) \
                or not isinstance(row.get("path"), str) \
                or not isinstance(row.get("sha256"), str):
            raise ContractError("premeasurement evidence row malformed")
        evidence = root / str(row["path"])
        if not evidence.is_file():
            raise ContractError(
                f"premeasurement evidence drift: {row.get('path')}")
        canonical_lf = _canonical_utf8_lf(
            evidence, label=f"premeasurement evidence {row.get('path')}")
        reconstructed_crlf = canonical_lf.replace(b"\n", b"\r\n")
        canonical_sha = hashlib.sha256(canonical_lf).hexdigest()
        crlf_sha = hashlib.sha256(reconstructed_crlf).hexdigest()
        recorded_sha = str(row["sha256"])
        if recorded_sha == canonical_sha:
            transport = "RECORDED_BYTES_ARE_CANONICAL_UTF8_LF"
        elif recorded_sha == crlf_sha:
            transport = (
                "RECORDED_WINDOWS_CRLF_RECONSTRUCTED_FROM_CANONICAL_UTF8_LF")
        else:
            raise ContractError(
                f"premeasurement evidence drift: {row.get('path')}")
        transported_basis.append({
            "path": row["path"],
            "recorded_sha256": recorded_sha,
            "canonical_utf8_lf_bytes": len(canonical_lf),
            "canonical_utf8_lf_sha256": canonical_sha,
            "transport": transport,
        })
    old_product = questions["Q1_public_system"].get("current_evidence")
    if not isinstance(old_product, Mapping) \
            or not isinstance(old_product.get("product_commit"), str):
        raise ContractError("premeasurement predecessor product identity absent")
    git_path_proof = _build_prediction_git_path_proof(root)
    return {
        "schema": "rtdl.goal5802.final_identity_prediction_binding.v1",
        "status": (
            "BOUND_TO_FINAL_PRODUCT__PREMEASUREMENT_PROBABILITIES_UNCHANGED"),
        "prediction_historical_authority": {
            "path": PREDICTION_FREEZE,
            "authority_commit": PREDICTION_AUTHORITY_COMMIT,
            "git_blob_sha1": PREDICTION_AUTHORITY_GIT_BLOB,
            "canonical_utf8_lf_bytes": PREDICTION_AUTHORITY_BYTES,
            "canonical_utf8_lf_sha256": PREDICTION_AUTHORITY_SHA256,
            "current_canonical_bytes_exactly_equal_historical_blob": True,
            "git_commit_path_proof": git_path_proof,
        },
        "prediction_document_schema": prediction["schema"],
        "predecessor_product_commit": old_product["product_commit"],
        "final_product_identity": {
            **{
                key: product_binding[key] for key in (
                    "source_commit", "source_tree", "wheel_sha256",
                    "native_sha256", "rtdlexe_module_sha256",
                    "native_custody_manifest_sha256",
                    "native_custody_custody_sha256",
                    "triangle_executable_identity_sha256",
                    "relation_executable_identity_sha256")
            },
            "complete_product_binding_sha256": digest(dict(product_binding)),
        },
        "survival_question_ids": sorted(questions),
        "evidence_basis_transport": transported_basis,
        "evidence_basis_rehashed_or_reconstructed_exactly": True,
        "actual_unrecorded_execution_absence_attested": False,
        "registered_performance_observation_count_since_prediction_claimed": False,
        "current_freeze_authorizes_formal_worker_zero": False,
        "probability_values_reestimated_or_rewritten": False,
        "probability_values_authority": (
            "EXACT_WHOLE_PREDICTION_DOCUMENT__NO_DUPLICATED_SUCCESSOR_VALUES"),
    }


def _validate_engineering_effort_ledger(
        ledger: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Require the exact per-arm disclosure frozen by Goal5799.

    This deliberately accepts no aggregate ``files changed = 0`` shortcut.
    The final freeze builder must be given all registered fields and every
    named file must exist in the exact source tree being frozen.  Historical
    time that was not instrumented is represented by null, never estimated;
    that truthfully lowers the engineering-comparability claim.
    """

    required_top = {
        "schema", "status", "goal5798_result_seen_before_successor_work",
        "active_minutes_are_best_effort_human_or_agent_time_not_wall_time",
        "engineering_time_comparability_established",
        "rtdl_received_approximately_one_week_product_engineering_before_baseline_successor",
        "baseline_successors_built_after_goal5798_result",
        "rows",
    }
    if set(ledger) != required_top \
            or ledger.get("schema") \
            != "rtdl.goal5802.per_arm_engineering_effort_ledger.v1" \
            or ledger.get("status") != "FINAL_VALUES_FOR_EXACT_FREEZE" \
            or ledger.get("goal5798_result_seen_before_successor_work") is not True \
            or ledger.get(
                "active_minutes_are_best_effort_human_or_agent_time_not_wall_time") \
            is not True \
            or ledger.get(
                "rtdl_received_approximately_one_week_product_engineering_before_baseline_successor") \
            is not True \
            or ledger.get("baseline_successors_built_after_goal5798_result") is not True:
        raise ContractError("engineering-effort ledger envelope differs")
    rows = ledger.get("rows")
    fields = {
        "arm", "engineer_or_agent", "start_utc", "stop_utc",
        "active_minutes", "files_changed", "purpose",
        "result_seen_before_change", "evidence_kind",
    }
    if not isinstance(rows, list) or len(rows) != len(ARMS):
        raise ContractError("engineering-effort ledger must have one row per arm")
    observed_arms: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != fields:
            raise ContractError("engineering-effort row fields differ")
        arm = row.get("arm")
        if arm not in ARMS or arm in observed_arms:
            raise ContractError("engineering-effort arm is absent or duplicated")
        observed_arms.add(str(arm))
        if not isinstance(row.get("engineer_or_agent"), str) \
                or not row["engineer_or_agent"].strip() \
                or not isinstance(row.get("purpose"), str) \
                or not row["purpose"].strip() \
                or row.get("result_seen_before_change") is not True:
            raise ContractError("engineering-effort disclosure is incomplete")
        evidence_kind = row.get("evidence_kind")
        if evidence_kind == "CONTEMPORANEOUS_INSTRUMENTED":
            active = row.get("active_minutes")
            if isinstance(active, bool) or not isinstance(active, int) or active <= 0:
                raise ContractError(
                    "instrumented engineering active minutes must be positive")
            try:
                start = datetime.fromisoformat(
                    str(row.get("start_utc")).replace("Z", "+00:00"))
                stop = datetime.fromisoformat(
                    str(row.get("stop_utc")).replace("Z", "+00:00"))
            except ValueError as error:
                raise ContractError("engineering-effort UTC timestamp invalid") from error
            if start.tzinfo is None or stop.tzinfo is None or stop < start:
                raise ContractError("engineering-effort time interval invalid")
        elif evidence_kind == "HISTORICAL_UNINSTRUMENTED__UNKNOWN_NOT_ESTIMATED":
            if row.get("active_minutes") is not None \
                    or row.get("start_utc") is not None \
                    or row.get("stop_utc") is not None:
                raise ContractError(
                    "uninstrumented history must remain null, never estimated")
        else:
            raise ContractError("engineering-effort evidence kind invalid")
        changed = row.get("files_changed")
        if not isinstance(changed, list) or not changed \
                or len(changed) != len(set(changed)) \
                or not all(isinstance(item, str) and item \
                           and not Path(item).is_absolute()
                           and (root / item).is_file() for item in changed):
            raise ContractError("engineering-effort changed-file list invalid")
    if observed_arms != set(ARMS):
        raise ContractError("engineering-effort arm set differs")
    any_unknown = any(
        row["evidence_kind"]
        == "HISTORICAL_UNINSTRUMENTED__UNKNOWN_NOT_ESTIMATED"
        for row in rows)
    if ledger.get("engineering_time_comparability_established") is (not any_unknown):
        pass
    else:
        raise ContractError("engineering-time comparability disposition differs")
    return json.loads(json.dumps(ledger, allow_nan=False))


def _instrument_context() -> tuple[str, tuple[str, ...]]:
    """Return the exact source-set inputs without including a forecast file.

    The external successor forecast binds the digest of this manifest, but the
    forecast document itself is deliberately not a member.  That makes the
    dependency one-way and avoids a forecast/sealed-freeze self-reference.
    """

    repaired_contract = (
        "history/internal_docs/"
        "goal5799_a1_repaired_performance_and_evidence_contract_20260824.json"
    )
    source_paths = (
        ".gitattributes",
        "experiments/goal5802_premeasurement/workload.py",
        "experiments/goal5802_premeasurement/__init__.py",
        "experiments/goal5802_premeasurement/contract.py",
        "experiments/goal5802_premeasurement/pyoptix_scalar_arm.py",
        "experiments/goal5802_premeasurement/rtdlexe_arm.py",
        "experiments/goal5802_premeasurement/direct_scalar_worker.cpp",
        "experiments/goal5802_premeasurement/direct_source_audit.py",
        "experiments/goal5802_premeasurement/controller.py",
        "experiments/goal5802_premeasurement/python_worker.py",
        "experiments/goal5802_premeasurement/runtime_manifest.py",
        "experiments/goal5802_premeasurement/build_cold_worker.py",
        "experiments/goal5802_premeasurement/evaluate.py",
        "experiments/goal5802_premeasurement/independent_recount.py",
        "experiments/goal5802_premeasurement/successor_forecast.py",
        "scripts/goal5801_a3_capture_native_custody.py",
        "scripts/goal5801_a4_export_origin_authority.py",
        "scripts/goal5801_a4_run_native_build.py",
        "scripts/goal5802_bind_final_clean_install.py",
        "scripts/goal5802_build_combined_runtime_untimed.py",
        "scripts/goal5802_build_direct_recipe.py",
        "scripts/goal5802_build_direct_worker_untimed.py",
        "scripts/goal5802_build_exact_source_packet.py",
        "scripts/goal5802_build_header_projection_untimed.py",
        "scripts/goal5802_build_local_premeasurement_freeze.py",
        "scripts/goal5802_build_offline_python_wheelhouse.py",
        "scripts/goal5802_build_pod_s0_config.py",
        "scripts/goal5802_build_rtdl_wheel_double_seed_untimed.py",
        "scripts/goal5802_build_successor_forecast.py",
        "scripts/goal5802_build_target_runtime_manifest.py",
        "scripts/goal5802_build_trust_postuse_custody_receipt.py",
        "scripts/goal5802_capture_target_untimed.py",
        "scripts/goal5802_capture_rtdsl_package_import_untimed.py",
        "scripts/goal5802_capture_host_runtime_provenance.py",
        "scripts/goal5802_clean_install_pyoptix_offline.py",
        "scripts/goal5802_export_freeze_inputs_untimed.py",
        "scripts/goal5802_materialize_pyoptix_build_provenance.py",
        "scripts/goal5802_nvrtc_compile_child.py",
        "scripts/goal5802_prepare_matched_ptx_untimed.py",
        "scripts/goal5802_run_direct_operation_kat_untimed.py",
        "scripts/goal5802_run_pod_s0_untimed.py",
        "scripts/goal5802_run_pyoptix_operation_kat_untimed.py",
        "scripts/goal5802_run_rtdl_operation_kat_untimed.py",
        "scripts/goal5802_sign_pod_s0_trust_request_offline.py",
        "scripts/goal5802_verify_exact_source_packet.py",
        "scripts/goal5802_verify_header_projection_untimed.py",
        "scripts/goal5802_verify_local_premeasurement_freeze.py",
        "scripts/goal5802_verify_preformal_runtime_dual_untimed.py",
        "scripts/goal5801_a3_run_clean_install.py",
        "scripts/goal5801_a3_verify_clean_install.py",
        "scripts/goal5801_a3_verify_native_custody.py",
        "scripts/goal5801_rtdlexe_trust.py",
        "tests/goal5801_a3_custody_and_clean_install_test.py",
        "tests/goal5802_local_premeasurement_test.py",
        "tests/goal5802_header_projection_replay_test.py",
        "tests/goal5802_direct_nvrtc_identity_test.py",
        "tests/goal5802_warm_process_cold_boundary_test.py",
        "tests/goal5802_target_runtime_preflight_test.py",
        "tests/goal5802_rtdsl_package_identity_test.py",
        "tests/goal5802_successor_forecast_test.py",
        "tests/goal5802_successor_forecast_cli_test.py",
        "tests/goal5802_exact_source_packet_test.py",
        "tests/goal5802_offline_python_environment_test.py",
        "tests/goal5802_offline_trust_response_signer_test.py",
        "tests/goal5802_pod_s0_config_builder_test.py",
        "tests/goal5802_pod_s0_helpers_test.py",
        "tests/goal5802_pod_s0_orchestrator_test.py",
        "tests/goal5802_preformal_runtime_dual_validator_test.py",
        "tests/goal5802_pyoptix_build_provenance_test.py",
        "tests/goal5802_rtdl_wheel_double_seed_test.py",
        "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py",
        "experiments/goal5796_matched/pyoptix_baseline.py",
        ("experiments/goal5802_premeasurement/"
         "matched_device_semantic_capacity.cu"),
        ("experiments/goal5802_premeasurement/"
         "relation_semantic_compaction.cu"),
        "experiments/goal5796_matched/direct_optix.cpp",
        "src/rtdsl/__init__.py",
        "src/rtdsl/v4_rtdlexe.py",
        ("history/internal_docs/"
         "goal5802_test_trust_public_root_20260825.json"),
        ("history/internal_docs/"
         "goal5802_test_trust_key_custody_receipt_20260825.json"),
        ("history/internal_docs/"
         "goal5802_retired_test_trust_root_e379_seq2_retirement_20260825.json"),
        ("history/internal_docs/"
         "goal5802_rtx_measurement_test_trust_root_v3_terminal_after_a4500_s0_20260826.json"),
        ("history/internal_docs/"
         "goal5802_rtx_measurement_test_trust_public_root_v4_20260826.json"),
        ("history/internal_docs/"
         "goal5802_rtx_measurement_test_trust_key_custody_v4_20260826.json"),
        ("history/internal_docs/"
         "goal5802_rtx_measurement_test_trust_root_v4_terminal_after_a4500_s0_20260826.json"),
        ("history/internal_docs/"
         "goal5802_rtx_measurement_test_trust_public_root_v5_20260826.json"),
        ("history/internal_docs/"
         "goal5802_rtx_measurement_test_trust_key_custody_v5_20260826.json"),
        ("history/internal_docs/"
         "goal5802_per_arm_engineering_effort_ledger_20260825.json"),
        ("history/internal_docs/"
         "goal5802_final_successor_forecast_manual_judgement_20260825.json"),
        ("history/internal_docs/"
         "goal5802_shared_bundled_python_pollution_pre_repair_manifest_"
         "20260825.json"),
        ("history/internal_docs/"
         "goal5802_shared_bundled_python_pollution_post_repair_result_"
         "20260825.json"),
        ("history/internal_docs/"
         "goal5802_retired_test_trust_root_a9b199_seq4_20260825/root.json"),
        ("history/internal_docs/"
         "goal5802_retired_test_trust_root_a9b199_seq4_20260825/"
         "package_seq4.json"),
        ("history/internal_docs/"
         "goal5802_retired_test_trust_root_a9b199_seq4_20260825/"
         "head_seq4.json"),
        ("history/internal_docs/"
         "goal5801_rtdlexe_lx1_untimed_evidence_20260824/"
         "test_trust_public/root.json"),
        ("history/internal_docs/"
         "goal5801_rtdlexe_lx1_untimed_evidence_20260824/"
         "test_trust_public/package_seq1.json"),
        ("history/internal_docs/"
         "goal5801_rtdlexe_lx1_untimed_evidence_20260824/"
         "test_trust_public/package_seq2.json"),
        ("history/internal_docs/"
         "goal5801_rtdlexe_lx1_untimed_evidence_20260824/"
         "test_trust_public/package_seq3.json"),
        ("history/internal_docs/"
         "goal5801_rtdlexe_lx1_untimed_evidence_20260824/"
         "test_trust_public/head_seq2.json"),
        ("history/internal_docs/"
         "goal5801_rtdlexe_lx1_untimed_evidence_20260824/"
         "test_trust_public/head_seq3.json"),
        PREDICTION_FREEZE,
        repaired_contract,
    )
    return repaired_contract, source_paths


def successor_forecast_identity_binding(
        root: Path, product_binding: Mapping[str, Any]) -> dict[str, str]:
    """Derive all seven exact identities required by the external forecast.

    This helper emits no probabilities and does not build a forecast.  It is
    safe to call only after the final product and complete instrument bytes
    exist; changing any bound byte makes an already sealed forecast invalid.
    """

    root = root.resolve()
    repaired_contract, source_paths = _instrument_context()
    validated_product = _validate_product_binding(product_binding, root)
    authority = workload_authority()
    operation = operation_contract()
    schedule = build_schedule()
    absolute_build_schedule = build_cold_schedule()
    source_manifest = [_source_record(root, path) for path in source_paths]
    repaired_record = _source_record(root, repaired_contract)
    return {
        "complete_product_binding_sha256": digest(validated_product),
        "workload_authority_sha256": digest(authority),
        "operation_contract_sha256": digest(operation),
        "comparative_schedule_sha256": digest(schedule),
        "build_cold_absolute_schedule_sha256": digest(
            absolute_build_schedule),
        "complete_instrument_source_manifest_sha256": digest(source_manifest),
        "goal5799_repaired_contract_sha256": str(repaired_record["sha256"]),
    }


def build_freeze(
        root: Path, product_binding: Mapping[str, Any],
        engineering_effort_ledger: Mapping[str, Any],
        successor_forecast: Mapping[str, Any],
        postresult_instrument_repair: Mapping[str, Any] | None = None,
        ) -> dict[str, object]:
    root = root.resolve()
    repaired_contract, source_paths = _instrument_context()
    schedule = build_schedule()
    absolute_build_schedule = build_cold_schedule()
    authority = workload_authority()
    operation = operation_contract()
    source_manifest = [_source_record(root, path) for path in source_paths]
    forecast_identity = successor_forecast_identity_binding(root, product_binding)
    repair_keys = {
        "schema", "status", "predecessor_freeze_file_sha256",
        "predecessor_controller_result_file_sha256",
        "predecessor_primary_evaluation_file_sha256",
        "predecessor_independent_recount_file_sha256",
        "predecessor_forecast_file_sha256",
        "predecessor_forecast_sha256", "observed_worker_counts",
        "repair_ids", "unchanged_scientific_dimensions",
        "postresult_probability_modified", "result_acceptance",
        "confirmatory_performance_claim_authorized",
        "descriptive_performance_evidence_authorized",
    }
    if postresult_instrument_repair is not None:
        if set(postresult_instrument_repair) != repair_keys \
                or postresult_instrument_repair.get("schema") \
                != "rtdl.goal5802.postresult_instrument_repair.v1" \
                or postresult_instrument_repair.get("status") \
                != "FROZEN_BEFORE_CORRECTIVE_SUCCESSOR_WORKER_ZERO" \
                or postresult_instrument_repair.get(
                    "postresult_probability_modified") is not False \
                or postresult_instrument_repair.get("result_acceptance") \
                != "UNCONDITIONAL_INCLUDING_ALL_LOSSES_AND_FAILURES" \
                or postresult_instrument_repair.get(
                    "confirmatory_performance_claim_authorized") is not False \
                or postresult_instrument_repair.get(
                    "descriptive_performance_evidence_authorized") is not True:
            raise ContractError("postresult instrument-repair record differs")
        for key in (
                "predecessor_freeze_file_sha256",
                "predecessor_controller_result_file_sha256",
                "predecessor_primary_evaluation_file_sha256",
                "predecessor_independent_recount_file_sha256",
                "predecessor_forecast_file_sha256",
                "predecessor_forecast_sha256"):
            value = postresult_instrument_repair.get(key)
            if not isinstance(value, str) or len(value) != 64 \
                    or any(character not in "0123456789abcdef"
                           for character in value):
                raise ContractError(
                    f"postresult instrument-repair digest differs: {key}")
        forecast_identity = successor_forecast.get("identity_binding")
        if not isinstance(forecast_identity, Mapping):
            raise ContractError("inherited predecessor forecast identity absent")
    try:
        validated_forecast = validate_successor_forecast(
            successor_forecast,
            expected_identity_binding=forecast_identity,
            expected_operation_contract=operation,
        )
    except SuccessorForecastError as error:
        raise ContractError(
            f"external successor forecast differs: {error}") from error
    freeze: dict[str, object] = {
        "schema": SCHEMA,
        "status": "FROZEN_LOCAL_PREMEASUREMENT__FORMAL_WORKER_ZERO_LOCKED",
        "authorization": {
            "local_plan_and_untimed_tests": True,
            "formal_worker_zero": False,
            "registered_gpu_timing": False,
            "pod_execution": False,
            "performance_claim": False,
            "required_future_keys": [
                "external_exact_byte_CFR_P0_0_P1_0",
                "separate_owner_execution_authority",
            ],
        },
        "postresult_instrument_repair": (
            dict(postresult_instrument_repair)
            if postresult_instrument_repair is not None else None),
        "forecast_disposition": (
            "INHERITED_PREDECESSOR_FORECAST__CALIBRATION_ONLY__NOT_A_BLIND_"
            "PREDICTION_FOR_CORRECTIVE_SUCCESSOR"
            if postresult_instrument_repair is not None
            else "CURRENT_BLIND_PREMEASUREMENT_FORECAST"),
        "goal5799_repaired_contract_whole_file": _source_record(
            root, repaired_contract),
        "product_binding": _validate_product_binding(product_binding, root),
        "workload_authority": authority,
        "operation_contract": operation,
        "direct_source_operation_audit": audit_direct_source(
            root / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"),
        "arms": list(ARMS),
        "tasks": list(TASKS),
        "regimes": {
            "BUILD_COLD_ABSOLUTE_DIAGNOSTIC": {
                "comparative_gate": False,
                "estimand": (
                    "fresh-process source-to-arm-local PRE_SIGNING_PRE_DEPLOYMENT "
                    "build product; RTDL builds an unsigned checked .rtdlexe plus "
                    "detached unsigned authority, PyOptiX NVRTC-compiles matched "
                    "device source to PTX, and Direct compiles the matched host "
                    "executable then NVRTC-compiles the same device source to PTX"),
                "build_boundary": "PRE_SIGNING_PRE_DEPLOYMENT_BUILD_PRODUCT",
                "deployable_product_claimed": False,
                "samples_per_task_arm": BUILD_COLD_BLOCK_COUNT,
                "why_12_not_24": (
                    "absolute non-gated diagnostic: two complete six-order cycles; "
                    "comparative regimes use four cycles because paired CI gates, "
                    "not BUILD_COLD, carry noninferiority claims"),
                "publication": (
                    "UNCONDITIONAL_ABSOLUTE_MEDIAN_RANGE_AND_ALL_RAW_ROWS"),
                "signing_or_trust_governance_inside_timer": False,
                "reason_signing_excluded": (
                    "the registered diagnostic stops before signing/trust-package "
                    "append for every arm; it is not a deployment-latency claim"),
                "excluded_cost_must_be_prominent": (
                    "RTDL signing, trust-root/package governance, installation, and "
                    "all arm-specific deployment work are excluded from B and may "
                    "not be implied to be free"),
                "prebuilt_product_read_counts_as_success": False,
                "any_arm_not_executing_declared_build": (
                    "FAILED_BUILD_ROW__PRESERVE__NO_RETRY_OR_REPLACEMENT"),
            },
            "DEPLOYMENT_COLD": {
                "wire_regime_id_retained_for_schedule_compatibility": (
                    "DEPLOYMENT_COLD"),
                "primary_estimator": "WARM_PROCESS_DEPLOYMENT_COLD",
                "estimand": (
                    "warm-process arm-local deployment/load plus prepare plus first "
                    "complete exact result after interpreter, Direct pre-main DSO, "
                    "and selected runtime import admission; common input generation "
                    "also precedes the primary timer"),
                "fresh_process_primary_estimator_claimed": False,
                "process_startup_and_admission": (
                    "SEPARATELY_METERED_AND_PUBLISHED__OUTSIDE_PRIMARY__"
                    "NOT_FREE_OR_OMITTED"),
                "primary_boundary_import_policy": "REJECT_ALL_NOT_PRELOADED",
                "samples_per_task_arm": BLOCK_COUNT,
                "warmups": 0,
                "within_worker_repetitions": 1,
            },
            "PREPARE": {
                "estimand": (
                    "accepted executable/PTX and common static input to reusable "
                    "prepared owner, including timed dynamic host-batch shaping "
                    "and retention; dynamic device representation/upload/GAS is "
                    "absent at prepare return, then one exact first execute "
                    "follows outside the primary "
                    "PREPARE timer and must report reuse=false plus real setup"),
                "samples_per_task_arm": BLOCK_COUNT,
                "warmups": 0,
                "within_worker_repetitions": 1,
            },
            "STEADY_E2E": {
                "estimand": (
                    "prepared execute through status, complete user output "
                    "materialization and route-independent exact comparison"),
                "samples_per_task_arm": BLOCK_COUNT,
                "warmups": STEADY_WARMUPS,
                "within_worker_repetitions": STEADY_REPETITIONS,
                "block_value": "median_of_64_worker_samples",
            },
        },
        "timer_boundary": {
            "clock": "CLOCK_MONOTONIC_PERF_COUNTER_NS_OR_CPP_STEADY_CLOCK",
            "common_input_materialization_inside_timer": False,
            "required_status_and_output_d2h_inside_timer": True,
            "canonicalization_and_exact_oracle_compare_inside_timer": True,
            "receipt_json_or_hashing_inside_timer": False,
            "diagnostic_or_forensic_rows_inside_timer": False,
            "close_inside_primary_timer": False,
            "close_separate_phase_required": True,
            "controller_process_envelope_separately_metered": True,
            "worker_startup_and_admission_outside_primary_timer": True,
            "worker_startup_and_admission_included_in_phase_coverage": True,
            "post_execution_identity_validation_outside_primary_timer": True,
            "post_execution_identity_validation_included_in_phase_coverage": True,
            "comparative_cache_state": (
                "NO_MANUAL_FILE_PAGE_CONDITIONING__OS_PAGE_CACHE_"
                "UNCONTROLLED__BALANCED_SIX_ORDER"),
            "os_shared_library_and_driver_cache_state": (
                "UNCONTROLLED__DISCLOSED"),
            "per_worker_cuda_cache": "FRESH_EMPTY_AND_DISABLED",
            "per_worker_optix_cache": "FRESH_EMPTY_AND_DISABLED",
            "per_worker_cupy_xdg_home_cache_roots": "FRESH_EMPTY_ISOLATED",
        },
        "worker_zero_runtime_preflight": {
            "required": True,
            "execution_order": "AFTER_FULL_ADMISSION__BEFORE_FORMAL_WORKER_ZERO",
            "python_startup": {
                "flags_exact": ["-I", "-S", "-B", "-P", "-c"],
                "site_initialization": "DISABLED",
                "site_packages": "EXACT_COMBINED_RUNTIME_PATH_INJECTED",
                "host_code": "READ_ONLY_FROZEN_SNAPSHOT_PATH_INJECTED",
                "pth_execution_in_build_kat_preflight_or_formal": False,
            },
            "target_reobservation": (
                "EXACT_CLEAN_PYTHON_SUBPROCESS__FROZEN_CAPTURE_SCRIPT__"
                "NVIDIA_SMI_NVCC_CUDA_DRIVER_OPTIX_FIELDS_ALL_EQUAL"),
            "loader_environment": {
                "PATH": "FROZEN_EXACT__ONLY_NONEMPTY_ABSOLUTE_ENTRIES",
                "LD_LIBRARY_PATH": (
                    "FROZEN_EXACT__ONLY_NONEMPTY_ABSOLUTE_ENTRIES_OR_UNSET"),
                "LD_PRELOAD": "MUST_BE_UNSET",
            },
            "direct_nvrtc_identity": (
                "LIVE_MINIMAL_COMPILE__LIBNVRTC_AND_BUILTINS_BYTES_VERSION"),
            "python_nvrtc_identity": (
                "FRESH_PROCESS_MATCHED_SOURCE_COMPILE__LIBNVRTC_AND_BUILTINS_"
                "BYTES_VERSION__PTX_BYTE_IDENTICAL"),
            "rtdsl_package_import_identity": (
                "CLEAN_PYTHON_ISOLATED_NO_BYTECODE_IMPORT__ALL_REQUIRED_AND_"
                "ALL_LOADED_RTDSL_MODULES_FROM_WHEEL_EQUAL_SEALED_PACKAGE"),
            "evidence": "SEALED_FIRST_CLASS_CONTROLLER_PREFLIGHT_RECEIPT",
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "formal_worker_count": 0,
            "any_mismatch": "TERMINATE_BEFORE_WORKER_ZERO",
        },
        "post_execution_runtime_revalidation": {
            "required": True,
            "scope": (
                "ALL_RUNTIME_FILES_AND_TREES_INCLUDING_COMPLETE_RECEIPTED_"
                "COMBINED_VENV_AND_COMPLETE_RTDSL_PACKAGE"),
            "timing_scope": "AFTER_FINAL_FORMAL_WORKER__OUTSIDE_PRIMARY_TIMERS",
            "any_mismatch": "INVALIDATE_COMPLETE_TRANSACTION",
        },
        "phase_attribution": {
            "required_goal5799_named_phases": [
                "input materialization",
                "protocol validation and code generation",
                "device compilation",
                "GAS/static preparation",
                "module/program/pipeline/SBT preparation",
                "complete execute including required output materialization",
                "close",
                "controller/process envelope",
            ],
            "worker_exclusive_metered_fields": [
                "process_startup_and_admission", "input_materialization",
                "load_or_deploy", "prepare",
                "steady_warmups", "complete_execute",
                "measurement_evidence_materialization", "close",
                "post_execution_identity_validation",
            ],
            "comparative_device_compilation": (
                "SOURCE_TO_PTX_OR_CUBIN_NOT_EXECUTED__OPTIX_PTX_TO_DEVICE_"
                "MODULE_WORK_REMAINS_INSIDE_COMBINED_PREPARE"),
            "load_or_deploy_mapping": {
                "RTDL": (
                    "deployment load plus protocol/authority validation; code "
                    "generation and device compilation are not executed"),
                "PYOPTIX_AND_DIRECT": (
                    "prebuilt PTX/cubin read; source-to-PTX/cubin generation is "
                    "not executed; OptiX PTX module compilation remains in prepare"),
            },
            "prepare_split": (
                "PUBLIC_RTLEXE_PREPARE_DOES_NOT_EXPOSE_A_CAUSALLY_SEPARABLE "
                "GAS_VS_MODULE_PIPELINE_SBT_BOUNDARY"),
            "prepare_publication": (
                "publish one directly metered combined prepare phase; both "
                "required subphase names are marked COMBINED_NOT_SEPARATELY_OBSERVABLE"),
            "controller_residual": (
                "controller_process_envelope minus exclusive worker phases is "
                "published as process startup/import/serialization/unaccounted "
                "residual and never causally attributed"),
            "startup_and_admission_mapping": (
                "process startup, authority and sealed-document admission; no "
                "manual page-cache conditioning; separately metered, non-primary"),
            "directly_metered_wall_fraction_is_diagnostic": True,
            "coverage_admission": (
                "ALL_NAMED_PHASES_REQUIRED_AND_RESIDUAL_PUBLISHED__NO_"
                "ARBITRARY_FRACTION_THRESHOLD"),
            "subtraction_residual_is_not_causal_attribution": True,
            "unaccounted_time_must_be_named_not_dropped": True,
        },
        "statistics": {
            "pairing_unit": "task_regime_block",
            "primary_ratio": "RTDL_BLOCK_NS/PYOPTIX_BLOCK_NS",
            "primary_ratio_direction": (
                "greater_than_1_means_RTDL_slower; less_than_1_means_RTDL_faster"),
            "context_ratios_required": [
                "DIRECT_BLOCK_NS/PYOPTIX_BLOCK_NS",
                "RTDL_BLOCK_NS/DIRECT_BLOCK_NS",
            ],
            "context_ratio_directions": {
                "DIRECT_BLOCK_NS/PYOPTIX_BLOCK_NS": (
                    "greater_than_1_means_Direct_slower; less_than_1_means_"
                    "PyOptiX_slower"),
                "RTDL_BLOCK_NS/DIRECT_BLOCK_NS": (
                    "greater_than_1_means_RTDL_slower; less_than_1_means_"
                    "Direct_slower"),
            },
            "point_estimator": "median_of_24_paired_block_ratios",
            "confidence_interval": "paired_block_percentile_bootstrap",
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": (
                "58020000 + 1000*task_index + 100*regime_index + ratio_index"),
            "bootstrap_lower_index_zero_based": 249,
            "bootstrap_upper_index_zero_based": 9749,
            "noninferiority": {
                "STEADY_E2E": "CI_UPPER_LE_1.05",
                "PREPARE": "CI_UPPER_LE_1.10",
                "DEPLOYMENT_COLD": "CI_UPPER_LE_1.10",
            },
            "all_row_claim_lattice": {
                "ALL_SIX_PRIMARY_ROWS_PASS": "bounded three-regime noninferiority",
                "ANY_PRIMARY_ROW_FAILS": (
                    "no all-row noninferiority; publish every row and only name "
                    "the exact passing task/regime rows"),
                "ANY_ROW_MISSING_OR_INVALID": (
                    "that row is not noninferior; no replacement or denominator shrink"),
                "DIRECT_PYOPTIX_ALWAYS_FIRST_CLASS": True,
                "python_host_tax_may_not_be_attributed_to_RTDL": True,
            },
        },
        "schedule": schedule,
        "schedule_sha256": digest(schedule),
        "schedule_seed": SCHEDULE_SEED,
        "worker_row_count": len(schedule),
        "build_cold_absolute_schedule": absolute_build_schedule,
        "build_cold_absolute_schedule_sha256": digest(absolute_build_schedule),
        "build_cold_absolute_worker_row_count": len(absolute_build_schedule),
        "failure_policy": {
            "retry": False,
            "resume": False,
            "replacement": False,
            "outlier_exclusion": False,
            "row_dropping": False,
            "cross_regime_substitution": False,
            "any_timeout_crash_missing_or_nonexact_worker": (
                "ROW_NOT_NONINFERIOR__PRESERVE_AND_REPORT"),
            "formal_result_acceptance": "UNCONDITIONAL_INCLUDING_ALL_LOSSES",
        },
        "baseline_quality": {
            "pyoptix_lineage": (
                "Goal5800 v7 persistent idiomatic compatibility arm"),
            "pyoptix_binding_scope": (
                "NVIDIA otk-pyoptix 9.1.0 source built against OptiX 9.0 API"),
            "not_claimed_stock_current_9_1_api": True,
            "no_per_element_python_timed_loop": True,
            "no_per_ray_triangle_d2h": True,
            "mandatory_external_question": (
                "Would a competent PyOptiX developer write and time this "
                "scalar-only arm this way?"),
            "acceptable_answer_before_worker_zero": "YES_WITH_P0_0_P1_0",
            "owl_timing_branch_present": False,
            "owl_performance_claim_allowed": False,
            "shared_16B_application_visible_work_question": (
                "Do all three relation arms implement the same device semantic-"
                "capacity gate, 16-byte status/control commit, device compaction, "
                "and 32768-byte unique application-output boundary?"),
            "required_answer_before_worker_zero": "YES_WITH_MACHINE_EVIDENCE",
        },
        "engineering_effort_ledger": _validate_engineering_effort_ledger(
            engineering_effort_ledger, root),
        "amortization": {
            "equation": (
                "B_RTDL + D_RTDL + N*S_RTDL <= "
                "D_PYOPTIX + N*S_PYOPTIX"),
            "build_statistic": "median_of_12_absolute_BUILD_COLD_rows",
            "deployment_statistic": "median_of_24_DEPLOYMENT_COLD_rows",
            "steady_statistic": "median_of_24_block_medians",
            "break_even_rule": (
                "ceil(max(0,B_RTDL+D_RTDL-D_PYOPTIX) / "
                "(S_PYOPTIX-S_RTDL))"),
            "B_PYOPTIX_publication": (
                "absolute diagnostic published but excluded from the exact "
                "Goal5799 registered break-even equation"),
            "if_steady_rtdl_not_less_than_pyoptix": "NEVER",
            "scenario_assumptions_required": True,
            "all_build_cold_rows_unconditionally_published": True,
        },
        "legacy_goal5798": {
            "worker_paths": list(LEGACY_WORKERS),
            "execution_allowed": False,
            "reason": (
                "old RTDL route is not .rtdlexe and old triangle arms expose "
                "per-ray host output"),
        },
        "source_manifest": source_manifest,
        "registered_performance_timing_count": 0,
        "performance_noninferiority_established": False,
        "generalization_exam_count": 0,
        "third_party_user_count": 0,
        "successor_subjective_forecast": validated_forecast,
    }
    freeze["freeze_sha256"] = digest(freeze)
    return freeze


def validate_freeze(value: Mapping[str, Any], root: Path) -> None:
    if value.get("schema") != SCHEMA:
        raise ContractError("freeze schema mismatch")
    if value.get("status") != \
            "FROZEN_LOCAL_PREMEASUREMENT__FORMAL_WORKER_ZERO_LOCKED":
        raise ContractError("freeze status mismatch")
    authorization = value.get("authorization")
    if not isinstance(authorization, Mapping) \
            or authorization.get("formal_worker_zero") is not False \
            or authorization.get("registered_gpu_timing") is not False \
            or authorization.get("pod_execution") is not False:
        raise ContractError("local freeze attempts to authorize execution")
    copy = dict(value)
    observed = copy.pop("freeze_sha256", None)
    if observed != digest(copy):
        raise ContractError("freeze self-digest mismatch")
    if value.get("schedule") != build_schedule() \
            or value.get("schedule_sha256") != digest(build_schedule()):
        raise ContractError("schedule differs from frozen generator")
    if value.get("build_cold_absolute_schedule") != build_cold_schedule() \
            or value.get("build_cold_absolute_schedule_sha256") \
            != digest(build_cold_schedule()):
        raise ContractError("BUILD_COLD schedule differs from frozen generator")
    manifest = value.get("source_manifest")
    if not isinstance(manifest, list):
        raise ContractError("source manifest absent")
    for row in manifest:
        if not isinstance(row, Mapping):
            raise ContractError("source manifest row invalid")
        expected = _source_record(root, str(row.get("path")))
        if dict(row) != expected:
            raise ContractError(f"source drift: {row.get('path')}")
    if any(str(row.get("path")) in LEGACY_WORKERS for row in manifest):
        raise ContractError("legacy Goal5798 worker entered source manifest")
    direct_audit = audit_direct_source(
        root / "experiments/goal5802_premeasurement/direct_scalar_worker.cpp")
    if value.get("direct_source_operation_audit") != direct_audit:
        raise ContractError("Direct source operation audit differs")
    _validate_product_binding(value.get("product_binding", {}), root)
    expected = build_freeze(
        root, value.get("product_binding", {}),
        value.get("engineering_effort_ledger", {}),
        value.get("successor_subjective_forecast", {}),
        value.get("postresult_instrument_repair"))
    if dict(value) != expected:
        raise ContractError(
            "freeze differs from the complete v3 executable contract")
