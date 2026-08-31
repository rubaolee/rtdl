"""Fail-closed protocol support for the Goal5814 Particle measurement.

The scientific preaction freezes the design but does not authorize worker
zero.  The exact owner-message receipt supplies only the owner's broad bounded
scope.  A project-prepared request binds the target without claiming owner
exact-byte approval, and a separate project closure binds the complete local
execution transaction under that broad scope.  Internal seals protect local
integrity; they are never represented as an external signature.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence


PREACTION_SCHEMA = (
    "rtdl.goal5814.particle_tracking_scientific_scope_and_measurement_policy_"
    "preaction.v1")
TARGET_MANIFEST_SCHEMA = "rtdl.goal5814.particle_measurement_target.v2"
EXECUTION_REQUEST_SCHEMA = (
    "rtdl.goal5814.particle_measurement_execution_request.v2")
# Compatibility name for callers that have not yet renamed their local symbol.
# The accepted document is deliberately a non-authorizing project request, not
# an exact-byte owner authority.
EXECUTION_AUTHORITY_SCHEMA = EXECUTION_REQUEST_SCHEMA
PROJECT_CLOSURE_SCHEMA = (
    "rtdl.goal5814.particle_measurement_project_closure.v2")
PROJECT_CLOSURE_ENV = "RTDL_GOAL5814_PROJECT_CLOSURE_PATH"

PREACTION_RELATIVE_PATH = (
    "history/internal_docs/"
    "goal5814_particle_tracking_scientific_scope_and_measurement_policy_"
    "preaction_20260828.json")
PREACTION_BYTES = 10_431
PREACTION_SHA256 = (
    "79f0d56f8765894666eaaec363f7e149c92de68e85d35ce43d3aa765132e625e")
OWNER_DIRECTIVE_RECEIPT_RELATIVE_PATH = (
    "history/internal_docs/"
    "goal5814_owner_directive_receipt_pod8h_20260828.json")
OWNER_DIRECTIVE_RECEIPT_BYTES = 1_258
OWNER_DIRECTIVE_RECEIPT_SHA256 = (
    "490bf43a5c1ec1f9632fc068dea4a8fafc2329ec9976499d6718a8c23d49aaa8")
OWNER_DIRECTIVE_MESSAGE = (
    "POD会开8个小时，你需要持续工作！中间不送审，不等待，但是需要严格自审！开干！ "
    "ssh root@69.30.85.207 -p 22028")
OWNER_DIRECTIVE_MESSAGE_BYTES = 143
OWNER_DIRECTIVE_MESSAGE_SHA256 = (
    "059b8d3a6b6dc8c7061c964822ab2f47cdbffd37b23cc2e079eee794b1651cd9")
SCIENTIFIC_MANIFEST_BYTES = 3_650
SCIENTIFIC_MANIFEST_SHA256 = (
    "911f02302fd48356935ab370911fc31303dc7fe56ffb7232cc060958d42e861b")
EXECUTABLE_MANIFEST_BYTES = 6_316
EXECUTABLE_MANIFEST_SHA256 = (
    "9b0f0bfb783df30a0799c6943b7623e797ccdc4e4d213fe5500be90db6093145")
TARGET_KAT_V3_PREACTION_RELATIVE_PATH = (
    "history/internal_docs/goal5814_particle_rtxa5000_untimed_exact_core_"
    "kat_v3_preaction_20260828.json")
TARGET_KAT_V3_PREACTION_BYTES = 9_203
TARGET_KAT_V3_PREACTION_SHA256 = (
    "32d07fb0224c2e76971f695138431008332bac9922b43494133acbf91bf8e870")
TARGET_KAT_V3_FAILURE_RELATIVE_PATH = (
    "history/internal_docs/goal5814_particle_rtxa5000_untimed_exact_core_"
    "kat_v3_zero_execute_failure_20260828.json")
TARGET_KAT_V3_FAILURE_BYTES = 2_675
TARGET_KAT_V3_FAILURE_SHA256 = (
    "c76d6e5c8d35eb2b8e908f3456adbea47d057876e18d4ed11470cf173474f404")
TARGET_KAT_PREACTION_RELATIVE_PATH = (
    "history/internal_docs/goal5814_particle_rtxa5000_untimed_exact_core_"
    "kat_v4_readonly_view_repair_preaction_20260828.json")
TARGET_KAT_PREACTION_BYTES = 4_938
TARGET_KAT_PREACTION_SHA256 = (
    "492b2e29e4923819697aecae0c048fd5686490581b2628396ffa2cb3e148da79")
TARGET_KAT_RESULT_RELATIVE_PATH = (
    "history/internal_docs/goal5814_particle_rtxa5000_untimed_exact_core_"
    "kat_v4_result_20260828.json")
TARGET_KAT_RESULT_BYTES = 4_495
TARGET_KAT_RESULT_SHA256 = (
    "a08463c82025988bea5b10c8c48cc99bd2ca19d8d9f2ad6ea4179c2831590f6a")
TARGET_KAT_ENTRY_BYTES = 1_190
TARGET_KAT_ENTRY_SHA256 = (
    "378b6d3339eb07056d240b092260fce0abf003627a42cef7939b556d47bd4dfd")
TARGET_NATIVE_RELATIVE_DIRECTORY = (
    "history/internal_docs/goal5814_particle_target_native_cc86_v3_20260828")
TARGET_ARTIFACT_BYTES = 30_376
TARGET_ARTIFACT_SHA256 = (
    "14e3688ada1f9297a6dbb628e4debcbac4e6ad790ceeb3619717d7a12d76f099")
TARGET_NATIVE_BYTES = 7_040_840
TARGET_NATIVE_SHA256 = (
    "b1943322c4e5e22634acb7345363f9ee9e232d9b7415427d25dde48f305a16d7")
TARGET_PTX_BYTES = 8_201
TARGET_PTX_SHA256 = (
    "ee229b3588ad40cc6994e96e78643bbb4d03991284ef0590c07565152e526cc9")
TARGET_DESCRIPTOR_BYTES = 2_611
TARGET_DESCRIPTOR_SHA256 = (
    "a20f483211ff86ae364e44cb782bf2ee856c07a49426a124a249a8043936b21d")
TARGET_TEMPLATE_SOURCE_BYTES = 4_580
TARGET_TEMPLATE_SOURCE_SHA256 = (
    "9484a5a4e600885d335cff16130e9cbbc0d1c5d8ed6d24297e2ecb202e0c6e67")
TARGET_PROTOCOL_DECISION_SHA256 = (
    "a9d72b2b4627d6da0f5c037637e6de138d74be4690c5165370e4b88b3f8c26bc")
TARGET_SPECIALIZATION_BINDING_SHA256 = (
    "0c4c0e38df7d453ff1e201a847efadea94330127bd42e46a725423ed2e70543c")
TARGET_TEMPLATE_SEMANTIC_SHA256 = (
    "4378dddd0e3089517d16a295c00d7172e0327f52e8715424d6c834da53076fbb")
TARGET_SOURCE_SEMANTICS_SHA256 = (
    "e67c909d6bea027dc882189aacce4b6f82fde8e6a28c41315b46037692d3b8b7")
TARGET_MANIFEST_BODY_SHA256 = (
    "08420d729ee633dd56251ad9c3e6eee4a432846575d75a530a0d2a3061b96b24")
TARGET_EXTERNAL_LOAD_RECEIPT_BYTES = 1_018
TARGET_EXTERNAL_LOAD_RECEIPT_SHA256 = (
    "6e900a006a07bb32802927b482dbc4597bdd915839e723dff962d4b23e38b184")
PYOPTIX_EXTENSION_BYTES = 2_630_616
PYOPTIX_EXTENSION_SHA256 = (
    "2e546d0daa497511c878dfd97c93266689ba4a3de1f563d4732137ac23ba0a36")
PYOPTIX_WHEEL_BYTES = 620_161
PYOPTIX_WHEEL_SHA256 = (
    "a659ed6df6125daa9cd37481c957e592c234f1cf423edb6b55d91a0f00683c4b")
CUPY_WHEEL_BYTES = 134_613_763
CUPY_WHEEL_SHA256 = (
    "9f0c81c3509f77be3ae8444759d5b314201b2dfcbbf2ae0d0b5fb7a61f20893c")
NUMPY_WHEEL_BYTES = 16_645_480
NUMPY_WHEEL_SHA256 = (
    "81f4a14bee47aec54f883e0cad2d73986640c1590eb9bfaaba7ad17394481e6e")

ARM_B = "B_PUBLIC_PYOPTIX"
ARM_D = "D_PUBLIC_VERIFIED_RTDSLEXE"
ARMS = (ARM_B, ARM_D)
REGIMES = (
    "DEPLOYMENT_COLD",
    "PREPARE",
    "STEADY_DYNAMIC_E2E",
)
BLOCK_COUNT = 24
STEADY_WARMUPS = 8
STEADY_REPETITIONS = 64
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_CI_INDICES = (249, 9_749)
BOOTSTRAP_SEED_BASE = 58_140_000
TOTAL_WORKER_COUNT = len(REGIMES) * BLOCK_COUNT * len(ARMS)

# These details are implementation supplements, not facts claimed to have
# been frozen by the scientific preaction.  A future owner authority must bind
# them byte-for-byte before worker zero.
CLOCK_RULE = "TIME_PERF_COUNTER_NS"
STEADY_MEDIAN_RULE = (
    "PYTHON_STATISTICS_MEDIAN__EVEN_PAIR_ARITHMETIC_MEAN__NO_TRUNCATION")
BOOTSTRAP_RULE = (
    "PYTHON_RANDOM_RANDOM_CHOICES_WITH_REPLACEMENT_K24__"
    "STATISTICS_MEDIAN__SORT_THEN_FIXED_INDICES_249_9749")
BLOCK_ORDER_RULE = "EVEN_BLOCK_B_THEN_D__ODD_BLOCK_D_THEN_B"
EXECUTION_CONCURRENCY_RULE = "SEQUENTIAL__ONE_ACTIVE_WORKER"
CACHE_RULE = (
    "FRESH_WORKER_LOCAL_DIRS__CUDA_CACHE_DISABLED__OPTIX_CACHE_DISABLED__"
    "RTDL_CUBIN_CACHE_DISABLED__NO_FILES_AFTER_WORKER")
WORKER_TIMEOUT_SECONDS = 3_600
INVALID_ROW_RULE = (
    "TERMINAL_MISSING_RESULT__PRESERVE_RAW_FAILURE__NO_EVALUATION__"
    "NO_RETRY_RESUME_REPLACEMENT_OR_ROW_DROP")

SOURCE_ROLE_PATHS = {
    "goal5814_init": "experiments/goal5814_particle/__init__.py",
    "measurement_protocol": "experiments/goal5814_particle/measurement_protocol.py",
    "formal_worker": "experiments/goal5814_particle/formal_worker.py",
    "measurement_preflight": (
        "experiments/goal5814_particle/measurement_preflight.py"),
    "controller": "experiments/goal5814_particle/controller.py",
    "evaluator": "experiments/goal5814_particle/evaluate.py",
    "independent_recount": (
        "experiments/goal5814_particle/independent_recount.py"),
    "kat_runner": "experiments/goal5814_particle/untimed_dual_arm_kat.py",
    "public_pyoptix_owner": (
        "experiments/goal5814_particle/public_pyoptix_owner.py"),
    "public_d_lifecycle": "src/rtdsl/v4_particle_rtdlexe.py",
    "rtdsl_init": "src/rtdsl/__init__.py",
    "target_kat_entry": (
        "experiments/goal5814_particle/untimed_dual_arm_kat_rtxa5000_cc86.py"),
}
ASSET_FILE_ROLES = {
    "preaction",
    "scientific_manifest",
    "executable_manifest",
    "prebuilt_ptx",
    "native_dso",
    "rtdlexe",
    "nvidia_smi",
    "python_executable",
    "numpy_module",
    "cupy_module",
    "optix_module",
    "pyoptix_extension",
    "pyoptix_wheel",
    "cupy_wheel",
    "numpy_wheel",
    "target_kat_preaction",
    "target_kat_result",
}
TARGET_FILE_ROLES = ASSET_FILE_ROLES | set(SOURCE_ROLE_PATHS)
LARGE_WHEEL_ROLES = {"pyoptix_wheel", "cupy_wheel", "numpy_wheel"}
_SHA256 = re.compile(r"[0-9a-f]{64}")


class MeasurementProtocolError(RuntimeError):
    """A frozen identity, target, schedule, or authority differs."""


@dataclass(frozen=True)
class WorkerSpec:
    ordinal: int
    regime: str
    block: int
    position: int
    arm: str
    worker_id: str


def canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise MeasurementProtocolError(
            "Goal5814 value is not canonical-JSON serializable") from error


def canonical_document(value: object) -> bytes:
    return canonical(value) + b"\n"


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise MeasurementProtocolError(
                f"Goal5814 JSON contains duplicate key: {key}")
        value[key] = item
    return value


def strict_json_bytes(payload: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"nonfinite JSON constant {token}")),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise MeasurementProtocolError(
            f"Goal5814 {label} is not strict UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise MeasurementProtocolError(f"Goal5814 {label} root is not an object")
    return value


def read_strict_json(path: Path, *, label: str) -> tuple[dict[str, Any], bytes]:
    resolved = Path(path).resolve(strict=True)
    if not resolved.is_file():
        raise MeasurementProtocolError(f"Goal5814 {label} is not a file")
    payload = resolved.read_bytes()
    return strict_json_bytes(payload, label=label), payload


def file_record(path: Path) -> dict[str, object]:
    resolved = Path(path).resolve(strict=True)
    if not resolved.is_file():
        raise MeasurementProtocolError(f"Goal5814 target is not a file: {resolved}")
    payload = resolved.read_bytes()
    return {
        "path": str(resolved),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _root_from_preaction(preaction_path: Path) -> Path:
    resolved = Path(preaction_path).resolve(strict=True)
    candidate = resolved
    for _ in Path(PREACTION_RELATIVE_PATH).parts:
        candidate = candidate.parent
    expected = (candidate / PREACTION_RELATIVE_PATH).resolve(strict=True)
    if expected != resolved:
        raise MeasurementProtocolError(
            "Goal5814 preaction is not under the expected repository root")
    return candidate


def owner_directive_receipt_path(*, root: Path) -> Path:
    resolved_root = Path(root).resolve(strict=True)
    return (resolved_root / OWNER_DIRECTIVE_RECEIPT_RELATIVE_PATH).resolve(
        strict=True)


def validate_owner_directive_receipt(
        path: Path, *, root: Path) -> dict[str, Any]:
    """Validate the exact broad owner message without widening its meaning."""

    resolved = Path(path).resolve(strict=True)
    expected_path = owner_directive_receipt_path(root=root)
    value, payload = read_strict_json(resolved, label="owner directive receipt")
    if resolved != expected_path \
            or len(payload) != OWNER_DIRECTIVE_RECEIPT_BYTES \
            or hashlib.sha256(payload).hexdigest() \
            != OWNER_DIRECTIVE_RECEIPT_SHA256:
        raise MeasurementProtocolError(
            "Goal5814 owner directive receipt exact bytes differ")
    _require_exact_keys(value, {
        "schema", "date", "status", "rendered_owner_message_utf8",
        "rendered_owner_message_utf8_bytes",
        "rendered_owner_message_utf8_sha256", "owner_directive",
        "scope_interpretation",
    }, "owner directive receipt")
    directive = _require_exact_keys(value["owner_directive"], {
        "pod_endpoint", "pod_window_hours",
        "continuous_in_scope_work_required",
        "external_review_during_window_required",
        "waiting_for_external_review_during_window_allowed",
        "strict_internal_self_review_required",
    }, "owner directive")
    scope = _require_exact_keys(value["scope_interpretation"], {
        "goal", "formal_execution_requires_all_frozen_scientific_and_local_"
        "gates_to_pass",
        "owner_message_does_not_relax_exact_correctness_or_measurement_"
        "symmetry",
        "owner_message_does_not_authorize_retry_resume_replacement_or_row_"
        "drop",
        "owner_message_does_not_authorize_threshold_or_confirmatory_claims",
        "owner_message_does_not_authorize_generalization_or_usability_claims",
    }, "owner directive scope")
    rendered = value["rendered_owner_message_utf8"]
    encoded = rendered.encode("utf-8") if isinstance(rendered, str) else b""
    if value["schema"] != "rtdl.goal5814.owner_directive_receipt.v1" \
            or value["date"] != "2026-08-28" \
            or value["status"] \
            != "OWNER_DIRECTIVE_RECORDED_BEFORE_FORMAL_WORKER_ZERO" \
            or rendered != OWNER_DIRECTIVE_MESSAGE \
            or len(encoded) != OWNER_DIRECTIVE_MESSAGE_BYTES \
            or hashlib.sha256(encoded).hexdigest() \
            != OWNER_DIRECTIVE_MESSAGE_SHA256 \
            or value["rendered_owner_message_utf8_bytes"] \
            != OWNER_DIRECTIVE_MESSAGE_BYTES \
            or value["rendered_owner_message_utf8_sha256"] \
            != OWNER_DIRECTIVE_MESSAGE_SHA256 \
            or directive != {
                "pod_endpoint": "root@69.30.85.207:22028",
                "pod_window_hours": 8,
                "continuous_in_scope_work_required": True,
                "external_review_during_window_required": False,
                "waiting_for_external_review_during_window_allowed": False,
                "strict_internal_self_review_required": True,
            } \
            or scope != {
                "goal": 5814,
                "formal_execution_requires_all_frozen_scientific_and_local_"
                "gates_to_pass": True,
                "owner_message_does_not_relax_exact_correctness_or_"
                "measurement_symmetry": True,
                "owner_message_does_not_authorize_retry_resume_replacement_"
                "or_row_drop": True,
                "owner_message_does_not_authorize_threshold_or_confirmatory_"
                "claims": True,
                "owner_message_does_not_authorize_generalization_or_"
                "usability_claims": True,
            }:
        raise MeasurementProtocolError(
            "Goal5814 owner directive receipt semantics differ")
    return value


def _require_exact_keys(
        value: Any, expected: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        actual = sorted(value) if isinstance(value, Mapping) else type(value).__name__
        raise MeasurementProtocolError(
            f"Goal5814 {label} keys differ: expected={sorted(expected)}, "
            f"actual={actual}")
    return value


def _require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise MeasurementProtocolError(f"Goal5814 {label} SHA-256 is invalid")
    return value


def validate_preaction(path: Path) -> dict[str, Any]:
    value, payload = read_strict_json(path, label="scientific preaction")
    if len(payload) != PREACTION_BYTES \
            or hashlib.sha256(payload).hexdigest() != PREACTION_SHA256:
        raise MeasurementProtocolError(
            "Goal5814 scientific preaction exact bytes differ")
    schedule = value.get("formal_schedule_if_and_only_if_all_local_gates_close")
    work = value.get("per_execute_work_contract")
    regimes = value.get("regimes")
    arms = value.get("matched_arms")
    if value.get("schema") != PREACTION_SCHEMA \
            or not isinstance(regimes, Mapping) \
            or tuple(regimes) != REGIMES \
            or not isinstance(arms, Mapping) \
            or arms.get("B") != "IDIOMATIC_PUBLIC_PYOPTIX_HOST_ORCHESTRATION" \
            or arms.get("D") != "PUBLIC_VERIFIED_RTDLEXE_LIFECYCLE" \
            or not isinstance(work, Mapping) \
            or work.get("query_representation") != "SEVEN_SOA_F32_COLUMNS" \
            or work.get("query_h2d_bytes") != 140_000 \
            or work.get("query_h2d_async_copy_count") != 7 \
            or work.get("optix_launch_count") != 1 \
            or work.get("control_d2h_bytes") != 16 \
            or work.get("successful_output_d2h_bytes") != 60_000 \
            or work.get("exact_np_array_equal_inside_timer") is not True \
            or not isinstance(schedule, Mapping) \
            or schedule.get("regime_count") != 3 \
            or schedule.get("balanced_paired_blocks_per_regime") != BLOCK_COUNT \
            or schedule.get("B_then_D_blocks_per_regime") != 12 \
            or schedule.get("D_then_B_blocks_per_regime") != 12 \
            or schedule.get("fresh_process_per_arm_and_position") is not True \
            or schedule.get("total_worker_count") != TOTAL_WORKER_COUNT \
            or schedule.get("primary_ratio") != "RTDL_OVER_PYOPTIX" \
            or schedule.get("steady_worker_value") \
            != "MEDIAN_OF_64_REPETITIONS" \
            or schedule.get("bootstrap_draw_count") != BOOTSTRAP_DRAWS \
            or schedule.get("bootstrap_seed_rule") \
            != "58140000_PLUS_ZERO_BASED_RESULT_ROW_INDEX" \
            or schedule.get("bootstrap_ci_indices") \
            != list(BOOTSTRAP_CI_INDICES) \
            or schedule.get("threshold_count") != 0 \
            or schedule.get("confirmatory_noninferiority_claim") is not False \
            or schedule.get("retry_resume_replacement_or_row_drop_allowed") \
            is not False:
        raise MeasurementProtocolError(
            "Goal5814 scientific preaction semantics differ")
    return value


def schedule() -> tuple[WorkerSpec, ...]:
    rows: list[WorkerSpec] = []
    ordinal = 0
    for regime in REGIMES:
        for block in range(BLOCK_COUNT):
            order = (ARMS if block % 2 == 0 else tuple(reversed(ARMS)))
            for position, arm in enumerate(order):
                short_arm = "b" if arm == ARM_B else "d"
                worker_id = (
                    f"{regime.lower()}-block-{block:02d}-"
                    f"position-{position}-{short_arm}")
                rows.append(WorkerSpec(
                    ordinal, regime, block, position, arm, worker_id))
                ordinal += 1
    if len(rows) != TOTAL_WORKER_COUNT:
        raise AssertionError("Goal5814 internal schedule cardinality differs")
    return tuple(rows)


def schedule_document() -> list[dict[str, object]]:
    return [
        {
            "ordinal": row.ordinal,
            "regime": row.regime,
            "block": row.block,
            "position": row.position,
            "arm": row.arm,
            "worker_id": row.worker_id,
        }
        for row in schedule()
    ]


SCHEDULE_SHA256 = digest(schedule_document())


def require_worker_spec(
        *, ordinal: int, regime: str, block: int, position: int,
        arm: str, worker_id: str) -> WorkerSpec:
    if type(ordinal) is not int or not 0 <= ordinal < TOTAL_WORKER_COUNT:
        raise MeasurementProtocolError("Goal5814 worker ordinal differs")
    expected = schedule()[ordinal]
    observed = WorkerSpec(ordinal, regime, block, position, arm, worker_id)
    if observed != expected:
        raise MeasurementProtocolError(
            f"Goal5814 worker coordinate differs: expected={expected}, "
            f"actual={observed}")
    return expected


def _validate_record(value: Any, label: str, *, rehash: bool) -> dict[str, Any]:
    record = dict(_require_exact_keys(
        value, {"path", "bytes", "sha256"}, f"{label} record"))
    if not isinstance(record["path"], str) or not Path(record["path"]).is_absolute() \
            or type(record["bytes"]) is not int or record["bytes"] <= 0:
        raise MeasurementProtocolError(f"Goal5814 {label} record differs")
    _require_sha(record["sha256"], label)
    if rehash and record != file_record(Path(record["path"])):
        raise MeasurementProtocolError(f"Goal5814 {label} bytes differ")
    return record


_KAT_COMMON_LEDGER = {
    "blocking_boundary_count": 2,
    "control_d2h_bytes": 16,
    "control_d2h_copy_call_count": 1,
    "control_reset_h2d_bytes": 16,
    "control_reset_h2d_copy_call_count": 1,
    "h2d_bytes": 140_136,
    "h2d_copy_call_count": 9,
    "optix_launch_call_count": 1,
    "output_d2h_after_status_failure": 0,
    "output_d2h_bytes": 60_000,
    "output_d2h_copy_call_count": 1,
    "parameter_h2d_bytes": 120,
    "parameter_h2d_copy_call_count": 1,
    "query_h2d_bytes": 140_000,
    "query_h2d_copy_call_count": 7,
    "raygen_invocation_count": 5_000,
    "status_before_output": True,
}


def _read_exact_root_json(
        *, root: Path, relative: str, expected_bytes: int,
        expected_sha256: str, label: str) -> tuple[dict[str, Any], Path]:
    path = (Path(root) / relative).resolve(strict=True)
    value, payload = read_strict_json(path, label=label)
    if len(payload) != expected_bytes \
            or hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise MeasurementProtocolError(
            f"Goal5814 {label} exact identity differs")
    return value, path


def _relative_record(relative: str, size: int, sha256: str) -> dict[str, Any]:
    return {"path": relative, "bytes": size, "sha256": sha256}


def _validate_target_kat(
        *, root: Path, target: Mapping[str, Any],
        files: Mapping[str, Mapping[str, Any]]) -> None:
    """Bind the terminal v3 lineage, controlling v4 KAT, and final assets."""

    resolved_root = Path(root).resolve(strict=True)
    native_root = (
        resolved_root / TARGET_NATIVE_RELATIVE_DIRECTORY).resolve(strict=True)
    expected_paths = {
        "target_kat_preaction": (
            resolved_root / TARGET_KAT_PREACTION_RELATIVE_PATH).resolve(
                strict=True),
        "target_kat_result": (
            resolved_root / TARGET_KAT_RESULT_RELATIVE_PATH).resolve(
                strict=True),
        "target_kat_entry": (
            resolved_root / SOURCE_ROLE_PATHS["target_kat_entry"]).resolve(
                strict=True),
        "executable_manifest": (native_root / "executable_manifest.json").resolve(
            strict=True),
        "rtdlexe": (native_root / (
            TARGET_ARTIFACT_SHA256 + ".rtdlexe")).resolve(strict=True),
        "native_dso": (native_root / "librtdl_optix.so").resolve(strict=True),
        "prebuilt_ptx": (native_root / (
            TARGET_TEMPLATE_SOURCE_SHA256 + ".compute_86.pass1.ptx")).resolve(
                strict=True),
    }
    identities = {
        "target_kat_preaction": (
            TARGET_KAT_PREACTION_BYTES, TARGET_KAT_PREACTION_SHA256),
        "target_kat_result": (TARGET_KAT_RESULT_BYTES, TARGET_KAT_RESULT_SHA256),
        "target_kat_entry": (TARGET_KAT_ENTRY_BYTES, TARGET_KAT_ENTRY_SHA256),
        "executable_manifest": (
            EXECUTABLE_MANIFEST_BYTES, EXECUTABLE_MANIFEST_SHA256),
        "rtdlexe": (TARGET_ARTIFACT_BYTES, TARGET_ARTIFACT_SHA256),
        "native_dso": (TARGET_NATIVE_BYTES, TARGET_NATIVE_SHA256),
        "prebuilt_ptx": (TARGET_PTX_BYTES, TARGET_PTX_SHA256),
    }
    for role, (expected_bytes, expected_sha) in identities.items():
        record = files[role]
        if Path(record["path"]) != expected_paths[role] \
                or type(record["bytes"]) is not int \
                or record["bytes"] != expected_bytes \
                or record["sha256"] != expected_sha:
            raise MeasurementProtocolError(
                f"Goal5814 {role} exact identity differs")

    v3_preaction, _ = _read_exact_root_json(
        root=resolved_root, relative=TARGET_KAT_V3_PREACTION_RELATIVE_PATH,
        expected_bytes=TARGET_KAT_V3_PREACTION_BYTES,
        expected_sha256=TARGET_KAT_V3_PREACTION_SHA256,
        label="terminal v3 KAT preaction")
    v3_failure, _ = _read_exact_root_json(
        root=resolved_root, relative=TARGET_KAT_V3_FAILURE_RELATIVE_PATH,
        expected_bytes=TARGET_KAT_V3_FAILURE_BYTES,
        expected_sha256=TARGET_KAT_V3_FAILURE_SHA256,
        label="terminal v3 zero-execute failure")
    kat_preaction, _ = _read_exact_root_json(
        root=resolved_root, relative=TARGET_KAT_PREACTION_RELATIVE_PATH,
        expected_bytes=TARGET_KAT_PREACTION_BYTES,
        expected_sha256=TARGET_KAT_PREACTION_SHA256,
        label="controlling v4 KAT preaction")
    result, _ = _read_exact_root_json(
        root=resolved_root, relative=TARGET_KAT_RESULT_RELATIVE_PATH,
        expected_bytes=TARGET_KAT_RESULT_BYTES,
        expected_sha256=TARGET_KAT_RESULT_SHA256,
        label="controlling v4 KAT result")

    expected_owner = {
        **_relative_record(
            OWNER_DIRECTIVE_RECEIPT_RELATIVE_PATH,
            OWNER_DIRECTIVE_RECEIPT_BYTES,
            OWNER_DIRECTIVE_RECEIPT_SHA256),
        "owner_target_bound_exact_bytes_approval_claimed": False,
        "project_materialized_under_owner_scope": True,
    }
    expected_v3_authority = {
        "deployment_id": (
            "goal5814/rtx-a5000-cc86/particle-strict-interior/"
            "freeze-v3-contract-bound"),
        "manifest_bytes": EXECUTABLE_MANIFEST_BYTES,
        "manifest_sha256": EXECUTABLE_MANIFEST_SHA256,
        "manifest_body_sha256": TARGET_MANIFEST_BODY_SHA256,
        "artifact_bytes": TARGET_ARTIFACT_BYTES,
        "artifact_sha256": TARGET_ARTIFACT_SHA256,
        "native_dso_bytes": TARGET_NATIVE_BYTES,
        "native_dso_sha256": TARGET_NATIVE_SHA256,
        "ptx_bytes": TARGET_PTX_BYTES,
        "ptx_sha256": TARGET_PTX_SHA256,
        "ptx_two_passes_byte_identical": True,
        "template_source_sha256": TARGET_TEMPLATE_SOURCE_SHA256,
        "descriptor_bytes": TARGET_DESCRIPTOR_BYTES,
        "descriptor_sha256": TARGET_DESCRIPTOR_SHA256,
        "target_protocol_verdict": "ACCEPT",
        "target_protocol_decision_sha256": TARGET_PROTOCOL_DECISION_SHA256,
        "specialization_binding_sha256": TARGET_SPECIALIZATION_BINDING_SHA256,
        "template_semantic_sha256": TARGET_TEMPLATE_SEMANTIC_SHA256,
        "source_semantics_sha256": TARGET_SOURCE_SEMANTICS_SHA256,
        "runtime_product_abi_symbol_count": 6,
        "external_public_load_close_receipt_bytes": (
            TARGET_EXTERNAL_LOAD_RECEIPT_BYTES),
        "external_public_load_close_receipt_sha256": (
            TARGET_EXTERNAL_LOAD_RECEIPT_SHA256),
    }
    v3_target = v3_preaction.get("target")
    v3_transaction = v3_preaction.get("single_transaction")
    v3_sources = v3_preaction.get("exact_sources")
    if v3_preaction.get("schema") != (
            "rtdl.goal5814.particle_rtxa5000_untimed_exact_core_kat_"
            "preaction.v3") \
            or v3_preaction.get("status") != (
                "FROZEN_BEFORE_V3_EXACT_CORE_TARGET_EXECUTION__ONE_"
                "UNTIMED_TRANSACTION_ONLY") \
            or v3_preaction.get("owner_directive_receipt") != expected_owner \
            or v3_preaction.get("request_external_authority_v3") \
            != expected_v3_authority \
            or not isinstance(v3_target, Mapping) \
            or v3_target.get("hostname") != target["hostname"] \
            or v3_target.get("gpu") != target["gpu_name"] \
            or v3_target.get("gpu_uuid") != target["gpu_uuid"] \
            or v3_target.get("compute_capability") \
            != target["compute_capability"] \
            or v3_target.get("driver") != target["driver_version"] \
            or v3_target.get("python") != target["python_version"] \
            or v3_target.get("numpy") != target["numpy_version"] \
            or v3_target.get("cupy") != target["cupy_version"] \
            or v3_target.get("pyoptix") \
            != target["pyoptix_distribution_version"] \
            or not isinstance(v3_transaction, Mapping) \
            or v3_transaction.get("retry_resume_replacement_allowed") is not False \
            or v3_transaction.get("registered_timing_count") != 0 \
            or not isinstance(v3_sources, Mapping) \
            or v3_sources.get("base_kat") != _relative_record(
                SOURCE_ROLE_PATHS["kat_runner"], 73_709,
                "2d923810849a6e4fab05ecdd2a0035e225a97fcd43c9372db30d2c21fc2965e4") \
            or v3_sources.get("target_entry") != _relative_record(
                SOURCE_ROLE_PATHS["target_kat_entry"],
                TARGET_KAT_ENTRY_BYTES, TARGET_KAT_ENTRY_SHA256) \
            or v3_sources.get("formal_worker") != _relative_record(
                SOURCE_ROLE_PATHS["formal_worker"], 24_523,
                "da2b7e0737dd860d059d0c85ec70e082a667769a2d044b104072b6c35de519ca"):
        raise MeasurementProtocolError(
            "Goal5814 terminal v3 authority binding differs")

    expected_v3_preaction_record = _relative_record(
        TARGET_KAT_V3_PREACTION_RELATIVE_PATH,
        TARGET_KAT_V3_PREACTION_BYTES, TARGET_KAT_V3_PREACTION_SHA256)
    failure = v3_failure.get("failure")
    if v3_failure.get("schema") != (
            "rtdl.goal5814.particle_rtxa5000_untimed_exact_core_kat_"
            "failure.v3") \
            or v3_failure.get("status") != (
                "TERMINAL_V3_ADMISSION_FAILURE__OUTPUT_ABSENT__ZERO_"
                "PARTICLE_EXECUTE__ZERO_TIMING") \
            or v3_failure.get("preaction") != expected_v3_preaction_record \
            or v3_failure.get("target_assets") != {
                "executable_manifest_sha256": EXECUTABLE_MANIFEST_SHA256,
                "artifact_sha256": TARGET_ARTIFACT_SHA256,
                "native_dso_sha256": TARGET_NATIVE_SHA256,
                "ptx_sha256": TARGET_PTX_SHA256,
            } \
            or not isinstance(failure, Mapping) \
            or failure.get("stage") != (
                "B_ARM_ADMIT_EXACT_CORE_INPUT_AFTER_B_AND_D_PREPARE__"
                "BEFORE_FIRST_EXACT_CORE") \
            or failure.get("output_file_present_after_failure") is not False \
            or any(type(failure.get(key)) is not int or failure.get(key) != 0
                   for key in (
                       "particle_exact_core_call_count",
                       "particle_execute_or_optix_launch_count",
                       "registered_performance_timing_count", "retry_count",
                       "resume_count", "replacement_count")) \
            or v3_failure.get("successor_rule") != (
                "V3_MUST_NOT_RUN_AGAIN__A_NEW_PREACTION_MAY_ACCEPT_READ_ONLY_"
                "C_CONTIGUOUS_NONOWNING_INPUT_ONLY_IF_IT_STILL_COPIES_TO_"
                "IMMUTABLE_BACKING_AND_ADDS_HOSTILE_VIEW_TESTS"):
        raise MeasurementProtocolError(
            "Goal5814 terminal v3 zero-execute disposition differs")

    predecessor = kat_preaction.get("controlling_predecessor")
    repair = kat_preaction.get("repair")
    unchanged = kat_preaction.get("unchanged_target_authority")
    changed_sources = kat_preaction.get("exact_changed_sources")
    transaction = kat_preaction.get("single_transaction")
    expected_v3_failure_record = _relative_record(
        TARGET_KAT_V3_FAILURE_RELATIVE_PATH,
        TARGET_KAT_V3_FAILURE_BYTES, TARGET_KAT_V3_FAILURE_SHA256)
    if kat_preaction.get("schema") != (
            "rtdl.goal5814.particle_rtxa5000_untimed_exact_core_kat_"
            "repair_preaction.v4") \
            or kat_preaction.get("status") != (
                "FROZEN_BEFORE_V4_EXECUTION__V3_TERMINAL__ONE_NEW_"
                "UNTIMED_TRANSACTION_ONLY") \
            or predecessor != {
                "v3_preaction": expected_v3_preaction_record,
                "v3_failure": expected_v3_failure_record,
                "v3_may_run_again": False,
                "v3_particle_execute_count": 0,
                "v3_registered_performance_timing_count": 0,
            } \
            or not isinstance(repair, Mapping) \
            or repair.get("mutable_source_still_rejected") is not True \
            or repair.get("sealed_token_provenance_pointer_identity_and_"
                          "bytes_backing_unchanged") is not True \
            or any(repair.get(key) is not False for key in (
                "native_dso_change", "rtdlexe_artifact_change",
                "ptx_or_device_program_change", "formal_worker_or_clock_change",
                "scientific_input_or_oracle_change")) \
            or unchanged != {
                "executable_manifest": {
                    "bytes": EXECUTABLE_MANIFEST_BYTES,
                    "sha256": EXECUTABLE_MANIFEST_SHA256},
                "artifact": {"bytes": TARGET_ARTIFACT_BYTES,
                             "sha256": TARGET_ARTIFACT_SHA256},
                "native_dso": {"bytes": TARGET_NATIVE_BYTES,
                               "sha256": TARGET_NATIVE_SHA256},
                "ptx": {"bytes": TARGET_PTX_BYTES,
                        "sha256": TARGET_PTX_SHA256},
                "protocol_decision_sha256": TARGET_PROTOCOL_DECISION_SHA256,
                "specialization_binding_sha256": (
                    TARGET_SPECIALIZATION_BINDING_SHA256),
            } \
            or not isinstance(changed_sources, Mapping) \
            or not isinstance(transaction, Mapping) \
            or transaction.get("inherits_v3_exact_execution_order_and_"
                               "ledger_requirements") is not True \
            or transaction.get("retry_resume_replacement_allowed") is not False \
            or transaction.get("registered_timing_count") != 0 \
            or kat_preaction.get("success_disposition") != (
                "V4_EXACT_CORE_TARGET_GATE_CLOSED__FORMAL_PERFORMANCE_STILL_"
                "REQUIRES_ATOMIC_FINAL_CONSTANT_BIND_AND_FULL_SELF_REVIEW"):
        raise MeasurementProtocolError(
            "Goal5814 controlling v4 preaction semantic binding differs")
    for name, relative in (
            ("public_pyoptix_owner", SOURCE_ROLE_PATHS["public_pyoptix_owner"]),
            ("public_rtdlexe_lifecycle", SOURCE_ROLE_PATHS["public_d_lifecycle"]),
            ("public_pyoptix_owner_test",
             "tests/goal5814_particle_public_pyoptix_owner_test.py"),
            ("public_rtdlexe_lifecycle_test",
             "tests/goal5814_particle_rtdlexe_lifecycle_test.py")):
        live = file_record(resolved_root / relative)
        expected = {"path": relative, "bytes": live["bytes"],
                    "sha256": live["sha256"]}
        if changed_sources.get(name) != expected:
            raise MeasurementProtocolError(
                f"Goal5814 controlling v4 changed source differs: {name}")

    manifest_relative = TARGET_NATIVE_RELATIVE_DIRECTORY + \
        "/executable_manifest.json"
    descriptor_relative = TARGET_NATIVE_RELATIVE_DIRECTORY + "/" + \
        TARGET_DESCRIPTOR_SHA256 + ".particle_descriptor.json"
    artifact_relative = TARGET_NATIVE_RELATIVE_DIRECTORY + "/" + \
        TARGET_ARTIFACT_SHA256 + ".rtdlexe"
    source_relative = TARGET_NATIVE_RELATIVE_DIRECTORY + "/" + \
        TARGET_TEMPLATE_SOURCE_SHA256 + ".particle_strict_interior.cu"
    receipt_relative = TARGET_NATIVE_RELATIVE_DIRECTORY + \
        "/external_load_close_receipt.json"
    manifest, _ = _read_exact_root_json(
        root=resolved_root, relative=manifest_relative,
        expected_bytes=EXECUTABLE_MANIFEST_BYTES,
        expected_sha256=EXECUTABLE_MANIFEST_SHA256,
        label="v3 executable manifest")
    descriptor, _ = _read_exact_root_json(
        root=resolved_root, relative=descriptor_relative,
        expected_bytes=TARGET_DESCRIPTOR_BYTES,
        expected_sha256=TARGET_DESCRIPTOR_SHA256,
        label="v3 standalone descriptor")
    artifact, _ = _read_exact_root_json(
        root=resolved_root, relative=artifact_relative,
        expected_bytes=TARGET_ARTIFACT_BYTES,
        expected_sha256=TARGET_ARTIFACT_SHA256,
        label="v3 RTDL executable artifact")
    external_receipt, _ = _read_exact_root_json(
        root=resolved_root, relative=receipt_relative,
        expected_bytes=TARGET_EXTERNAL_LOAD_RECEIPT_BYTES,
        expected_sha256=TARGET_EXTERNAL_LOAD_RECEIPT_SHA256,
        label="v3 external public load-close receipt")
    source_record = file_record(resolved_root / source_relative)
    pass2_record = file_record(native_root / (
        TARGET_TEMPLATE_SOURCE_SHA256 + ".compute_86.pass2.ptx"))
    manifest_identities = manifest.get("identities")
    manifest_protocol = manifest.get("standard_protocol")
    runtime_boundary = manifest.get("runtime_boundary")
    if manifest.get("schema") != (
            "rtdl.goal5814.particle_strict_interior_executable_manifest.v1") \
            or manifest.get("status") != (
                "PASS__EXACT_PUBLIC_ARTIFACT_BUILT_AND_LOAD_VERIFIED__"
                "NO_EXECUTE") \
            or manifest.get("manifest_body_sha256") \
            != TARGET_MANIFEST_BODY_SHA256 \
            or not isinstance(manifest_identities, Mapping) \
            or manifest_identities.get("artifact_bytes") \
            != TARGET_ARTIFACT_BYTES \
            or manifest_identities.get("artifact_sha256") \
            != TARGET_ARTIFACT_SHA256 \
            or manifest_identities.get("descriptor_sha256") \
            != TARGET_DESCRIPTOR_SHA256 \
            or manifest_identities.get("native_sha256") \
            != TARGET_NATIVE_SHA256 \
            or manifest_identities.get("ptx_bytes") != TARGET_PTX_BYTES \
            or manifest_identities.get("ptx_sha256") != TARGET_PTX_SHA256 \
            or manifest_identities.get("ptx_passes_byte_identical") is not True \
            or manifest_identities.get("template_source_sha256") \
            != TARGET_TEMPLATE_SOURCE_SHA256 \
            or manifest_identities.get("specialization_binding_sha256") \
            != TARGET_SPECIALIZATION_BINDING_SHA256 \
            or manifest_identities.get("template_semantic_sha256") \
            != TARGET_TEMPLATE_SEMANTIC_SHA256 \
            or not isinstance(manifest_protocol, Mapping) \
            or manifest_protocol.get("verdict") != "ACCEPT" \
            or manifest_protocol.get("decision_sha256") \
            != TARGET_PROTOCOL_DECISION_SHA256 \
            or manifest_protocol.get("source_semantics_sha256") \
            != TARGET_SOURCE_SEMANTICS_SHA256 \
            or not isinstance(runtime_boundary, Mapping) \
            or runtime_boundary.get("runtime_product_abi_symbol_count") != 6 \
            or runtime_boundary.get("formal_worker_zero_authorized") is not False \
            or runtime_boundary.get("performance_claimed") is not False \
            or runtime_boundary.get("real_prepare_or_execute_attempted") is not False:
        raise MeasurementProtocolError(
            "Goal5814 v3 executable manifest semantic authority differs")
    descriptor_transfer = descriptor.get("transfer_contract")
    if descriptor.get("schema") \
            != "rtdl.v4.particle_strict_interior_template.v1" \
            or descriptor.get("native_abi") \
            != "rtdl.v4.prepared_particle_strict_interior.v3" \
            or descriptor.get("semantic_sha256") \
            != TARGET_TEMPLATE_SEMANTIC_SHA256 \
            or descriptor.get("source_sha256") \
            != TARGET_TEMPLATE_SOURCE_SHA256 \
            or descriptor.get("source_bytes") != TARGET_TEMPLATE_SOURCE_BYTES \
            or not isinstance(descriptor_transfer, Mapping) \
            or descriptor_transfer.get("execute_abi_version") != 3 \
            or descriptor_transfer.get("control_before_output") is not True \
            or descriptor_transfer.get("failure_output_d2h_bytes") != 0 \
            or source_record != {
                "path": str((resolved_root / source_relative).resolve(
                    strict=True)),
                "bytes": TARGET_TEMPLATE_SOURCE_BYTES,
                "sha256": TARGET_TEMPLATE_SOURCE_SHA256,
            } \
            or pass2_record["bytes"] != TARGET_PTX_BYTES \
            or pass2_record["sha256"] != TARGET_PTX_SHA256:
        raise MeasurementProtocolError(
            "Goal5814 v3 descriptor/source/PTX authority differs")
    artifact_protocol = artifact.get("standard_protocol")
    artifact_decision = artifact_protocol.get("decision") \
        if isinstance(artifact_protocol, Mapping) else None
    if artifact.get("schema") \
            != "rtdl.v4.particle_strict_interior.rtdlexe.v1" \
            or artifact.get("native_library_sha256") != TARGET_NATIVE_SHA256 \
            or artifact.get("ptx_sha256") != TARGET_PTX_SHA256 \
            or artifact.get("source_sha256") != TARGET_TEMPLATE_SOURCE_SHA256 \
            or artifact.get("descriptor_sha256") != TARGET_DESCRIPTOR_SHA256 \
            or artifact.get("template_semantic_sha256") \
            != TARGET_TEMPLATE_SEMANTIC_SHA256 \
            or not isinstance(artifact_decision, Mapping) \
            or artifact_decision.get("verdict") != "ACCEPT" \
            or artifact_decision.get("findings") != [] \
            or artifact_decision.get("decision_sha256") \
            != TARGET_PROTOCOL_DECISION_SHA256:
        raise MeasurementProtocolError(
            "Goal5814 v3 artifact protocol/template binding differs")
    if external_receipt.get("schema") != (
            "rtdl.goal5814.particle_rtdlexe_external_manifest_load_kat.v1") \
            or external_receipt.get("status") != (
                "PASS__EXTERNAL_MANIFEST_AUTHORITY__PUBLIC_LOAD_CLOSE") \
            or external_receipt.get("artifact_sha256") \
            != TARGET_ARTIFACT_SHA256 \
            or external_receipt.get("external_expected_manifest_sha256") \
            != EXECUTABLE_MANIFEST_SHA256 \
            or external_receipt.get("external_expected_supplied_via_cli") \
            is not True \
            or external_receipt.get("prepare_execute_attempted") is not False \
            or external_receipt.get("registered_timing_count") != 0 \
            or external_receipt.get("ptx_bytes") != TARGET_PTX_BYTES \
            or external_receipt.get("ptx_sha256") != TARGET_PTX_SHA256:
        raise MeasurementProtocolError(
            "Goal5814 v3 external manifest authority receipt differs")

    expected_capability = {
        "schema": "rtdl.goal5814.particle_dual_arm_deployment_capability.v1",
        "artifact": {
            "path": TARGET_ARTIFACT_SHA256 + ".rtdlexe",
            "bytes": TARGET_ARTIFACT_BYTES,
            "sha256": TARGET_ARTIFACT_SHA256},
        "descriptor": {
            "path": TARGET_DESCRIPTOR_SHA256 + ".particle_descriptor.json",
            "bytes": TARGET_DESCRIPTOR_BYTES,
            "sha256": TARGET_DESCRIPTOR_SHA256},
        "native": {"path": "librtdl_optix.so", "bytes": TARGET_NATIVE_BYTES,
                   "sha256": TARGET_NATIVE_SHA256},
        "protocol_decision": {
            "location": "artifact.standard_protocol.decision",
            "sha256": TARGET_PROTOCOL_DECISION_SHA256},
        "ptx": {
            "path": TARGET_TEMPLATE_SOURCE_SHA256 + ".compute_86.pass1.ptx",
            "bytes": TARGET_PTX_BYTES, "sha256": TARGET_PTX_SHA256},
        "source": {
            "path": TARGET_TEMPLATE_SOURCE_SHA256 +
                    ".particle_strict_interior.cu",
            "bytes": TARGET_TEMPLATE_SOURCE_BYTES,
            "sha256": TARGET_TEMPLATE_SOURCE_SHA256},
        "template_semantic": {
            "location": "artifact.template_semantic_sha256",
            "sha256": TARGET_TEMPLATE_SEMANTIC_SHA256},
    }
    result_identities = result.get("identities")
    capability = result_identities.get("deployment_capability") \
        if isinstance(result_identities, Mapping) else None
    if result.get("schema") \
            != "rtdl.goal5814.particle_dual_arm_untimed_kat_result.v1" \
            or result.get("status") != "PASS__UNTIMED_DUAL_ARM_KAT" \
            or result.get("timed") is not False \
            or type(result.get("retry_count")) is not int \
            or result.get("retry_count") != 0 \
            or type(result.get("replacement_count")) is not int \
            or result.get("replacement_count") != 0 \
            or result.get("execution_order") \
            != ["B_SUCCESS", "D_SUCCESS", "B_MISS", "D_MISS"] \
            or not isinstance(result_identities, Mapping) \
            or result_identities.get("scientific_input_manifest") != {
                "bytes": SCIENTIFIC_MANIFEST_BYTES,
                "sha256": SCIENTIFIC_MANIFEST_SHA256} \
            or result_identities.get("executable_manifest") != {
                "bytes": EXECUTABLE_MANIFEST_BYTES,
                "sha256": EXECUTABLE_MANIFEST_SHA256} \
            or capability != expected_capability:
        raise MeasurementProtocolError(
            "Goal5814 controlling v4 KAT result identity/envelope differs")
    steps = result.get("steps")
    if not isinstance(steps, Mapping) or set(steps) != {
            "B_SUCCESS", "D_SUCCESS", "B_MISS", "D_MISS"}:
        raise MeasurementProtocolError("Goal5814 target KAT step set differs")
    for name, arm in (
            ("B_SUCCESS", ARM_B), ("D_SUCCESS", ARM_D)):
        step = steps[name]
        if not isinstance(step, Mapping) or step.get("arm") != arm \
                or step.get("kind") != "SUCCESS" \
                or step.get("exact") is not True \
                or step.get("output_read_only") is not True \
                or step.get("control") != {
                    "validated_row_count": 5_000,
                    "first_error": 0xFFFFFFFF,
                    "error_code": 0,
                    "status": 0} \
                or step.get("ledger") != _KAT_COMMON_LEDGER:
            raise MeasurementProtocolError(
                f"Goal5814 target KAT success differs: {name}")
    failure_ledger = dict(_KAT_COMMON_LEDGER)
    failure_ledger.update({
        "blocking_boundary_count": 1,
        "output_d2h_bytes": 0,
        "output_d2h_copy_call_count": 0,
    })
    for name, arm in (("B_MISS", ARM_B), ("D_MISS", ARM_D)):
        step = steps[name]
        if not isinstance(step, Mapping) or step.get("arm") != arm \
                or step.get("kind") != "EXPECTED_DEVICE_MISS" \
                or step.get("device_status_failure") is not True \
                or step.get("control") != {
                    "validated_row_count": 4_999,
                    "first_error": 0,
                    "error_code": 1,
                    "status": 1} \
                or step.get("ledger") != failure_ledger:
            raise MeasurementProtocolError(
                f"Goal5814 target KAT miss differs: {name}")
    if files["rtdlexe"]["bytes"] != TARGET_ARTIFACT_BYTES \
            or files["rtdlexe"]["sha256"] != TARGET_ARTIFACT_SHA256 \
            or files["native_dso"]["bytes"] != TARGET_NATIVE_BYTES \
            or files["native_dso"]["sha256"] != TARGET_NATIVE_SHA256 \
            or files["prebuilt_ptx"]["bytes"] != TARGET_PTX_BYTES \
            or files["prebuilt_ptx"]["sha256"] != TARGET_PTX_SHA256:
        raise MeasurementProtocolError(
            "Goal5814 measurement assets differ from target KAT assets")


def validate_target_manifest(
        path: Path, *, root: Path, rehash: bool = True,
        rehash_wheels: bool = True) -> dict[str, Any]:
    value, payload = read_strict_json(path, label="target manifest")
    if payload != canonical_document(value):
        raise MeasurementProtocolError(
            "Goal5814 target manifest is not exact canonical JSON")
    required = {
        "schema", "status", "target", "scientific_input_directory",
        "files", "clock_read_count", "gpu_kernel_launch_count",
        "registered_performance_timing_count", "formal_worker_count",
        "target_manifest_sha256",
    }
    _require_exact_keys(value, required, "target manifest")
    unsigned = dict(value)
    observed_seal = unsigned.pop("target_manifest_sha256")
    if value["schema"] != TARGET_MANIFEST_SCHEMA \
            or value["status"] != "PREPARED_TARGET_PRODUCTS__WORKER_ZERO" \
            or observed_seal != digest(unsigned) \
            or any(type(value[key]) is not int or value[key] != 0 for key in (
                "clock_read_count", "gpu_kernel_launch_count",
                "registered_performance_timing_count", "formal_worker_count")):
        raise MeasurementProtocolError("Goal5814 target manifest seal differs")
    target = _require_exact_keys(value["target"], {
        "hostname", "gpu_selector", "gpu_uuid", "gpu_name",
        "compute_capability", "driver_version", "gpu_memory_total_mib",
        "cuda_visible_devices", "python_version", "numpy_version",
        "cupy_version", "pyoptix_distribution_version", "optix_api_version",
        "ld_library_path", "ld_preload",
    }, "target identity")
    for key in (
            "hostname", "gpu_selector", "gpu_uuid", "gpu_name",
            "compute_capability", "driver_version", "cuda_visible_devices",
            "python_version", "numpy_version", "cupy_version",
            "pyoptix_distribution_version", "optix_api_version"):
        if not isinstance(target[key], str) or not target[key]:
            raise MeasurementProtocolError(
                f"Goal5814 target identity is empty: {key}")
    if type(target["gpu_memory_total_mib"]) is not int \
            or target["gpu_memory_total_mib"] <= 0:
        raise MeasurementProtocolError(
            "Goal5814 target GPU memory identity differs")
    for key in ("ld_library_path", "ld_preload"):
        if target[key] is not None and not isinstance(target[key], str):
            raise MeasurementProtocolError(
                f"Goal5814 target loader identity differs: {key}")
    directory = Path(str(value["scientific_input_directory"]))
    if not directory.is_absolute() or rehash and not directory.resolve(strict=True).is_dir():
        raise MeasurementProtocolError(
            "Goal5814 scientific input directory differs")
    files = _require_exact_keys(value["files"], TARGET_FILE_ROLES, "target files")
    validated = {
        role: _validate_record(
            row, role,
            rehash=rehash and (rehash_wheels or role not in LARGE_WHEEL_ROLES))
        for role, row in files.items()
    }
    resolved_root = Path(root).resolve(strict=True)
    for role, relative in SOURCE_ROLE_PATHS.items():
        expected = (resolved_root / relative).resolve(strict=True)
        if Path(validated[role]["path"]) != expected:
            raise MeasurementProtocolError(
                f"Goal5814 source role path differs: {role}")
    expected_preaction = (resolved_root / PREACTION_RELATIVE_PATH).resolve(strict=True)
    if Path(validated["preaction"]["path"]) != expected_preaction \
            or validated["preaction"]["bytes"] != PREACTION_BYTES \
            or validated["preaction"]["sha256"] != PREACTION_SHA256:
        raise MeasurementProtocolError("Goal5814 target preaction identity differs")
    if validated["scientific_manifest"]["bytes"] \
            != SCIENTIFIC_MANIFEST_BYTES \
            or validated["scientific_manifest"]["sha256"] \
            != SCIENTIFIC_MANIFEST_SHA256 \
            or Path(validated["scientific_manifest"]["path"]) \
            != directory / "SCIENTIFIC_INPUT_MANIFEST.json":
        raise MeasurementProtocolError(
            "Goal5814 target scientific manifest identity differs")
    if validated["executable_manifest"]["bytes"] \
            != EXECUTABLE_MANIFEST_BYTES \
            or validated["executable_manifest"]["sha256"] \
            != EXECUTABLE_MANIFEST_SHA256:
        raise MeasurementProtocolError(
            "Goal5814 target executable manifest identity differs")
    exact_runtime_files = {
        "pyoptix_extension": (
            PYOPTIX_EXTENSION_BYTES, PYOPTIX_EXTENSION_SHA256),
        "pyoptix_wheel": (PYOPTIX_WHEEL_BYTES, PYOPTIX_WHEEL_SHA256),
        "cupy_wheel": (CUPY_WHEEL_BYTES, CUPY_WHEEL_SHA256),
        "numpy_wheel": (NUMPY_WHEEL_BYTES, NUMPY_WHEEL_SHA256),
    }
    for role, (expected_bytes, expected_sha) in exact_runtime_files.items():
        if validated[role]["bytes"] != expected_bytes \
                or validated[role]["sha256"] != expected_sha:
            raise MeasurementProtocolError(
                f"Goal5814 exact runtime identity differs: {role}")
    _validate_target_kat(
        root=resolved_root, target=target, files=validated)
    if Path(validated["python_executable"]["path"]) \
            != Path(str(validated["python_executable"]["path"])).resolve(strict=True):
        raise MeasurementProtocolError(
            "Goal5814 target Python executable path is not resolved")
    return value


def validate_execution_request(
        path: Path, *, preaction_path: Path, target_manifest_path: Path,
        target_manifest: Mapping[str, Any],
        owner_receipt_path: Path | None = None) -> dict[str, Any]:
    """Validate a target-bound project request that cannot authorize itself."""

    value, payload = read_strict_json(path, label="execution request")
    if payload != canonical_document(value):
        raise MeasurementProtocolError(
            "Goal5814 execution request is not exact canonical JSON")
    required = {
        "schema", "status", "owner_directive_receipt_file",
        "preaction_file", "scientific_manifest", "executable_manifest",
        "target_manifest_file", "schedule_sha256",
        "clock_rule", "steady_median_rule", "bootstrap_rule",
        "block_order_rule", "execution_concurrency_rule", "cache_rule",
        "worker_timeout_seconds", "authorization_not_before_utc",
        "authorization_not_after_utc", "invalid_row_rule",
        "owner_target_bound_exact_bytes_approval_claimed",
        "project_materialized_under_owner_scope",
        "formal_worker_zero_authorized", "pod_gpu_timing_authorized",
        "descriptive_unconditional_acceptance",
        "confirmatory_noninferiority_claim", "threshold_count",
        "retry_resume_replacement_or_row_drop_allowed", "total_worker_count",
        "registered_performance_timing_count", "formal_worker_count",
        "execution_request_sha256",
    }
    _require_exact_keys(value, required, "execution request")
    unsigned = dict(value)
    observed_seal = unsigned.pop("execution_request_sha256")
    expected_preaction = file_record(preaction_path)
    expected_target = file_record(target_manifest_path)
    root = _root_from_preaction(preaction_path)
    expected_owner_path = owner_directive_receipt_path(root=root) \
        if owner_receipt_path is None else Path(owner_receipt_path).resolve(
            strict=True)
    validate_owner_directive_receipt(expected_owner_path, root=root)
    expected_owner = file_record(expected_owner_path)
    scientific = target_manifest["files"]["scientific_manifest"]
    executable = target_manifest["files"]["executable_manifest"]
    if value["schema"] != EXECUTION_REQUEST_SCHEMA \
            or value["status"] \
            != "PROJECT_PREPARED__TARGET_BOUND__NONAUTHORIZING_REQUEST" \
            or observed_seal != digest(unsigned) \
            or value["owner_directive_receipt_file"] != expected_owner \
            or value["preaction_file"] != expected_preaction \
            or value["target_manifest_file"] != expected_target \
            or value["scientific_manifest"] != scientific \
            or value["executable_manifest"] != executable \
            or value["schedule_sha256"] != SCHEDULE_SHA256 \
            or value["clock_rule"] != CLOCK_RULE \
            or value["steady_median_rule"] != STEADY_MEDIAN_RULE \
            or value["bootstrap_rule"] != BOOTSTRAP_RULE \
            or value["block_order_rule"] != BLOCK_ORDER_RULE \
            or value["execution_concurrency_rule"] != EXECUTION_CONCURRENCY_RULE \
            or value["cache_rule"] != CACHE_RULE \
            or type(value["worker_timeout_seconds"]) is not int \
            or value["worker_timeout_seconds"] != WORKER_TIMEOUT_SECONDS \
            or value["invalid_row_rule"] != INVALID_ROW_RULE \
            or value["owner_target_bound_exact_bytes_approval_claimed"] \
            is not False \
            or value["project_materialized_under_owner_scope"] is not True \
            or value["formal_worker_zero_authorized"] is not False \
            or value["pod_gpu_timing_authorized"] is not False \
            or value["descriptive_unconditional_acceptance"] is not True \
            or value["confirmatory_noninferiority_claim"] is not False \
            or type(value["threshold_count"]) is not int \
            or value["threshold_count"] != 0 \
            or value["retry_resume_replacement_or_row_drop_allowed"] is not False \
            or type(value["total_worker_count"]) is not int \
            or value["total_worker_count"] != TOTAL_WORKER_COUNT \
            or type(value["registered_performance_timing_count"]) is not int \
            or value["registered_performance_timing_count"] != 0 \
            or type(value["formal_worker_count"]) is not int \
            or value["formal_worker_count"] != 0:
        raise MeasurementProtocolError(
            "Goal5814 execution request is absent, incomplete, or differs")
    return value


def validate_execution_authority(
        path: Path, *, preaction_path: Path, target_manifest_path: Path,
        target_manifest: Mapping[str, Any],
        owner_receipt_path: Path | None = None) -> dict[str, Any]:
    """Worker compatibility gate requiring the controller-bound closure.

    Offline builders and preflight code validate the request and closure
    explicitly.  A formal worker still calls this historical function name;
    requiring the controller-supplied closure path here prevents a bare,
    self-sealed request from becoming a worker-zero authorization surface.
    """

    request = validate_execution_request(
        path, preaction_path=preaction_path,
        target_manifest_path=target_manifest_path,
        target_manifest=target_manifest,
        owner_receipt_path=owner_receipt_path,
    )
    closure_raw = os.environ.get(PROJECT_CLOSURE_ENV)
    if not closure_raw:
        raise MeasurementProtocolError(
            "Goal5814 formal worker lacks controller-bound project closure")
    closure_path = Path(closure_raw)
    if not closure_path.is_absolute():
        raise MeasurementProtocolError(
            "Goal5814 controller-bound project closure path is not absolute")
    closure = validate_project_closure(
        closure_path, preaction_path=preaction_path,
        target_manifest_path=target_manifest_path,
        execution_request_path=path, target_manifest=target_manifest,
        execution_request=request, owner_receipt_path=owner_receipt_path,
    )
    return closure


def validate_project_closure(
        path: Path, *, preaction_path: Path, target_manifest_path: Path,
        execution_request_path: Path, target_manifest: Mapping[str, Any],
        execution_request: Mapping[str, Any],
        owner_receipt_path: Path | None = None) -> dict[str, Any]:
    """Validate the project closure derived under the exact broad owner scope.

    This closure is intentionally not represented as a target-bound exact-byte
    owner signature.  Its internal seal protects integrity; its explicit false
    literal prevents that stronger provenance claim from being inferred.
    """

    value, payload = read_strict_json(path, label="project closure")
    if payload != canonical_document(value):
        raise MeasurementProtocolError(
            "Goal5814 project closure is not exact canonical JSON")
    required = {
        "schema", "status", "owner_directive_receipt_file",
        "preaction_file", "scientific_manifest", "executable_manifest",
        "target_manifest_file", "execution_request_file", "schedule_sha256",
        "clock_rule", "steady_median_rule", "bootstrap_rule",
        "block_order_rule", "execution_concurrency_rule", "cache_rule",
        "worker_timeout_seconds", "authorization_not_before_utc",
        "authorization_not_after_utc", "invalid_row_rule",
        "owner_target_bound_exact_bytes_approval_claimed",
        "project_materialized_under_owner_scope",
        "formal_worker_zero_authorized_under_owner_scope",
        "pod_gpu_timing_authorized_under_owner_scope",
        "descriptive_unconditional_acceptance",
        "confirmatory_noninferiority_claim", "threshold_count",
        "retry_resume_replacement_or_row_drop_allowed", "total_worker_count",
        "registered_performance_timing_count", "formal_worker_count",
        "project_closure_sha256",
    }
    _require_exact_keys(value, required, "project closure")
    unsigned = dict(value)
    observed_seal = unsigned.pop("project_closure_sha256")
    root = _root_from_preaction(preaction_path)
    expected_owner_path = owner_directive_receipt_path(root=root) \
        if owner_receipt_path is None else Path(owner_receipt_path).resolve(
            strict=True)
    validate_owner_directive_receipt(expected_owner_path, root=root)
    expected_owner = file_record(expected_owner_path)
    expected_preaction = file_record(preaction_path)
    expected_target = file_record(target_manifest_path)
    expected_request = file_record(execution_request_path)
    scientific = target_manifest["files"]["scientific_manifest"]
    executable = target_manifest["files"]["executable_manifest"]
    expected_status = (
        "PROJECT_CLOSED_UNDER_EXACT_BROAD_OWNER_SCOPE__NOT_OWNER_"
        "EXACT_BYTE_APPROVAL")
    if value["schema"] != PROJECT_CLOSURE_SCHEMA \
            or value["status"] != expected_status \
            or observed_seal != digest(unsigned) \
            or value["owner_directive_receipt_file"] != expected_owner \
            or value["preaction_file"] != expected_preaction \
            or value["target_manifest_file"] != expected_target \
            or value["execution_request_file"] != expected_request \
            or value["scientific_manifest"] != scientific \
            or value["executable_manifest"] != executable \
            or value["schedule_sha256"] != SCHEDULE_SHA256 \
            or value["clock_rule"] != CLOCK_RULE \
            or value["steady_median_rule"] != STEADY_MEDIAN_RULE \
            or value["bootstrap_rule"] != BOOTSTRAP_RULE \
            or value["block_order_rule"] != BLOCK_ORDER_RULE \
            or value["execution_concurrency_rule"] \
            != EXECUTION_CONCURRENCY_RULE \
            or value["cache_rule"] != CACHE_RULE \
            or type(value["worker_timeout_seconds"]) is not int \
            or value["worker_timeout_seconds"] != WORKER_TIMEOUT_SECONDS \
            or value["authorization_not_before_utc"] \
            != execution_request["authorization_not_before_utc"] \
            or value["authorization_not_after_utc"] \
            != execution_request["authorization_not_after_utc"] \
            or value["invalid_row_rule"] != INVALID_ROW_RULE \
            or value["owner_target_bound_exact_bytes_approval_claimed"] \
            is not False \
            or value["project_materialized_under_owner_scope"] is not True \
            or value["formal_worker_zero_authorized_under_owner_scope"] \
            is not True \
            or value["pod_gpu_timing_authorized_under_owner_scope"] \
            is not True \
            or value["descriptive_unconditional_acceptance"] is not True \
            or value["confirmatory_noninferiority_claim"] is not False \
            or type(value["threshold_count"]) is not int \
            or value["threshold_count"] != 0 \
            or value["retry_resume_replacement_or_row_drop_allowed"] \
            is not False \
            or type(value["total_worker_count"]) is not int \
            or value["total_worker_count"] != TOTAL_WORKER_COUNT \
            or type(value["registered_performance_timing_count"]) is not int \
            or value["registered_performance_timing_count"] != 0 \
            or type(value["formal_worker_count"]) is not int \
            or value["formal_worker_count"] != 0:
        raise MeasurementProtocolError(
            "Goal5814 project closure is absent, incomplete, or differs")
    # Parse and bound the closure window even when a caller is only performing
    # an offline structural validation.  Live membership is checked separately.
    before = _parse_utc(value["authorization_not_before_utc"],
                        "authorization start")
    after = _parse_utc(value["authorization_not_after_utc"],
                       "authorization end")
    if after <= before or (after - before).total_seconds() > 8 * 60 * 60:
        raise MeasurementProtocolError(
            "Goal5814 project closure authority window differs")
    return value


def _parse_utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise MeasurementProtocolError(
            f"Goal5814 {label} is not a UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise MeasurementProtocolError(
            f"Goal5814 {label} is not a UTC timestamp") from error
    if parsed.tzinfo != timezone.utc:
        raise MeasurementProtocolError(
            f"Goal5814 {label} is not canonical UTC")
    return parsed


def validate_authority_window(
        authority: Mapping[str, Any], *, now: datetime | None = None) -> float:
    before = _parse_utc(
        authority.get("authorization_not_before_utc"),
        "authorization start")
    after = _parse_utc(
        authority.get("authorization_not_after_utc"),
        "authorization end")
    observed = datetime.now(timezone.utc) if now is None else now
    if observed.tzinfo is None:
        raise MeasurementProtocolError("Goal5814 authority check time is naive")
    observed = observed.astimezone(timezone.utc)
    if after <= before or (after - before).total_seconds() > 8 * 60 * 60 \
            or not before <= observed <= after:
        raise MeasurementProtocolError(
            "Goal5814 execution is outside the bounded owner authority window")
    return (after - observed).total_seconds()


def validate_live_target(
        target_manifest: Mapping[str, Any], *,
        run: Callable[..., Any] = subprocess.run,
        hostname: str | None = None,
        python_executable: str | None = None,
        python_version: str | None = None,
        runtime_identity: Mapping[str, str] | None = None,
        environment: Mapping[str, str] | None = None,
        ) -> dict[str, str]:
    """Re-observe the selected GPU and process identity without a clock."""

    target = target_manifest["target"]
    files = target_manifest["files"]
    current_environment: Mapping[str, str] = (
        os.environ if environment is None else environment)
    observed_host = platform.node() if hostname is None else hostname
    observed_python = str(Path(sys.executable).resolve()) \
        if python_executable is None else str(Path(python_executable).resolve())
    observed_version = platform.python_version() \
        if python_version is None else python_version
    if runtime_identity is None:
        numpy_module = importlib.import_module("numpy")
        cupy_module = importlib.import_module("cupy")
        optix_module = importlib.import_module("optix")
        extension_module = importlib.import_module("optix._optix")
        runtime_identity = {
            "numpy_version": str(numpy_module.__version__),
            "cupy_version": str(cupy_module.__version__),
            "pyoptix_distribution_version": importlib.metadata.version("pyoptix"),
            "optix_api_version": ".".join(
                str(item) for item in optix_module.version()),
            "numpy_module": str(Path(numpy_module.__file__).resolve()),
            "cupy_module": str(Path(cupy_module.__file__).resolve()),
            "optix_module": str(Path(optix_module.__file__).resolve()),
            "pyoptix_extension": str(Path(extension_module.__file__).resolve()),
        }
    expected_python = str(Path(files["python_executable"]["path"]).resolve())
    if observed_host != target["hostname"] \
            or observed_python != expected_python \
            or observed_version != target["python_version"] \
            or runtime_identity.get("numpy_version") != target["numpy_version"] \
            or runtime_identity.get("cupy_version") != target["cupy_version"] \
            or runtime_identity.get("pyoptix_distribution_version") \
            != target["pyoptix_distribution_version"] \
            or runtime_identity.get("optix_api_version") \
            != target["optix_api_version"] \
            or any(runtime_identity.get(role) != files[role]["path"] for role in (
                "numpy_module", "cupy_module", "optix_module",
                "pyoptix_extension")) \
            or current_environment.get("CUDA_VISIBLE_DEVICES") \
            != target["cuda_visible_devices"] \
            or current_environment.get("LD_LIBRARY_PATH") \
            != target["ld_library_path"] \
            or current_environment.get("LD_PRELOAD") != target["ld_preload"]:
        raise MeasurementProtocolError(
            "Goal5814 live host/Python/loader environment differs")
    command = [
        files["nvidia_smi"]["path"],
        f"--id={target['gpu_selector']}",
        "--query-gpu=uuid,name,compute_cap,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    ]
    completed = run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    stdout = completed.stdout.decode("utf-8") \
        if isinstance(completed.stdout, bytes) else str(completed.stdout)
    rows = stdout.strip().splitlines()
    fields = [item.strip() for item in rows[0].split(",")] \
        if len(rows) == 1 else []
    expected = [
        target["gpu_uuid"], target["gpu_name"],
        target["compute_capability"], target["driver_version"],
        str(target["gpu_memory_total_mib"]),
    ]
    if completed.returncode != 0 or fields != expected:
        raise MeasurementProtocolError(
            "Goal5814 live selected GPU differs from target authority")
    return {
        "hostname": observed_host,
        "python_executable": observed_python,
        "python_version": observed_version,
        "gpu_uuid": fields[0],
        "gpu_name": fields[1],
        "compute_capability": fields[2],
        "driver_version": fields[3],
        "gpu_memory_total_mib": fields[4],
        "numpy_version": target["numpy_version"],
        "cupy_version": target["cupy_version"],
        "pyoptix_distribution_version": target[
            "pyoptix_distribution_version"],
        "optix_api_version": target["optix_api_version"],
    }


def positive_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(float(value)) or float(value) <= 0:
        raise MeasurementProtocolError(f"Goal5814 {label} is not positive finite")
    return float(value)
