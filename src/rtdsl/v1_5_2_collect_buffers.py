from __future__ import annotations

import ctypes
from pathlib import Path
import time
from typing import Any

from .v1_5_1_collect_k_bounded import collect_k_bounded_rows
from .v1_5_1_collect_k_bounded import collect_native_i64_rows_into_prepared_output_buffer
from .v1_5_1_collect_k_bounded import collect_native_i64_rows_with_backend_symbol
from .v1_5_1_collect_k_bounded import validate_collect_k_bounded_result


V1_5_2_COLLECT_BUFFER_STATUS = "python_rtdl_buffer_contract_foundation"
V1_5_2_COLLECT_BUFFER_KINDS = ("result", "prepared_result")
V1_5_2_COLLECT_BUFFER_DEVICES = ("cpu", "cuda")
V1_5_2_COLLECT_BUFFER_DTYPES = ("int64",)
V1_5_2_COLLECT_BUFFER_LAYOUT = "row_major_dense_candidate_id_rows"
V1_5_2_COLLECT_BUFFER_OWNERS = ("python", "rtdl", "native")
V1_5_2_COLLECT_BUFFER_MUTABILITY = ("immutable", "mutable")
V1_5_2_COLLECT_BUFFER_COPY_BOUNDARIES = (
    "python_materialized_rows",
    "native_row_buffer_metadata",
    "prepared_host_buffer_reuse",
    "prepared_device_buffer_reuse",
)
V1_5_2_COLLECT_BUFFER_FORBIDDEN_CLAIMS = (
    "true_zero_copy",
    "public_speedup",
    "whole_app_speedup",
    "stable_public_primitive",
    "release_action",
)
V1_5_2_PREPARED_BUFFER_REUSE_GATE_STATUS = "evidence_complete_claims_blocked"
V1_5_2_PREPARED_BUFFER_REUSE_REQUIRED_EVIDENCE = (
    "native_abi_accepts_prepared_output_buffer_pointer",
    "python_wrapper_passes_prepared_output_buffer_pointer",
    "host_reuse_or_device_reuse_measured",
    "embree_optix_same_contract_parity",
    "overflow_fail_closed_with_prepared_buffer",
    "external_ai_review",
)
V1_5_2_PREPARED_BUFFER_REUSE_SATISFIED_EVIDENCE = (
    "native_abi_accepts_prepared_output_buffer_pointer",
    "python_wrapper_passes_prepared_output_buffer_pointer",
    "host_reuse_or_device_reuse_measured",
    "overflow_fail_closed_with_prepared_buffer",
    "embree_optix_same_contract_parity",
    "external_ai_review",
)
V1_5_2_PREPARED_BUFFER_REUSE_MISSING_EVIDENCE = ()
V1_5_2_PREPARED_BUFFER_REUSE_BLOCKED_CLAIMS = (
    "prepared_buffer_reuse_proven",
    "true_zero_copy",
    "public_speedup",
    "whole_app_speedup",
    "stable_public_primitive",
    "release_action",
)
V1_5_2_RELEASE_SURFACE_GATE_STATUS = (
    "candidate_docs_publicly_discoverable_pending_explicit_release_action"
)
V1_5_2_RELEASE_SURFACE_CLASSIFICATION = "documented_experimental_evidence_candidate"
V1_5_2_RELEASE_SURFACE_REQUIRED_DOCS = (
    "docs/release_reports/v1_5_2/README.md",
    "docs/release_reports/v1_5_2/prepared_host_output_buffers.md",
    "docs/release_reports/v1_5_2/release_surface_gate.md",
)
V1_5_2_RELEASE_SURFACE_REQUIRED_PHRASES = (
    "documented experimental evidence candidate",
    "prepared host-output",
    "COLLECT_K_BOUNDED",
    "Python+RTDL",
    "Embree and OptiX",
    "evidence_complete_claims_blocked",
    "prepared_buffer_reuse_proven remains False",
    "not stable primitive promotion",
    "no public speedup wording",
    "no zero-copy wording",
    "no whole-app claims",
    "no release tag action",
    "external release-surface review accepted",
    "public docs link accepted",
    "publicly discoverable",
    "PYTHONPATH=src:. python",
)
V1_5_2_RELEASE_SURFACE_FORBIDDEN_PHRASES = (
    "prepared buffer reuse is proven",
    "true zero-copy is authorized",
    "public speedup is authorized",
    "stable primitive promotion is authorized",
    "release tag action is authorized",
    "whole-app speedup is authorized",
)


def v1_5_2_collect_buffer_contract() -> dict[str, Any]:
    """Return the v1.5.2 app-generic collect result-buffer contract."""
    return {
        "status": V1_5_2_COLLECT_BUFFER_STATUS,
        "track": "python_rtdl",
        "buffer_kinds": V1_5_2_COLLECT_BUFFER_KINDS,
        "dtype_scope": V1_5_2_COLLECT_BUFFER_DTYPES,
        "device_scope": V1_5_2_COLLECT_BUFFER_DEVICES,
        "layout": V1_5_2_COLLECT_BUFFER_LAYOUT,
        "owner_scope": V1_5_2_COLLECT_BUFFER_OWNERS,
        "mutability_scope": V1_5_2_COLLECT_BUFFER_MUTABILITY,
        "required_fields": (
            "primitive",
            "buffer_kind",
            "dtype",
            "layout",
            "shape",
            "capacity",
            "valid_count",
            "row_width",
            "device",
            "owner",
            "mutability",
            "copy_boundary",
            "overflowed",
            "fail_closed",
        ),
        "copy_boundaries": V1_5_2_COLLECT_BUFFER_COPY_BOUNDARIES,
        "forbidden_claims": V1_5_2_COLLECT_BUFFER_FORBIDDEN_CLAIMS,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "v1.5.2 collect buffer descriptors define app-generic metadata "
            "for Python+RTDL result buffers only. They do not authorize true "
            "zero-copy, public speedup wording, whole-app claims, stable "
            "public primitive wording, partner tensor handoff, or release action."
        ),
    }


def validate_v1_5_2_collect_buffer_contract() -> dict[str, Any]:
    contract = v1_5_2_collect_buffer_contract()
    if contract["status"] != V1_5_2_COLLECT_BUFFER_STATUS:
        raise ValueError("invalid v1.5.2 collect buffer contract status")
    if tuple(contract["buffer_kinds"]) != V1_5_2_COLLECT_BUFFER_KINDS:
        raise ValueError("collect buffer kind scope changed")
    if tuple(contract["dtype_scope"]) != V1_5_2_COLLECT_BUFFER_DTYPES:
        raise ValueError("collect buffer dtype scope changed")
    if tuple(contract["device_scope"]) != V1_5_2_COLLECT_BUFFER_DEVICES:
        raise ValueError("collect buffer device scope changed")
    if tuple(contract["owner_scope"]) != V1_5_2_COLLECT_BUFFER_OWNERS:
        raise ValueError("collect buffer owner scope changed")
    if tuple(contract["mutability_scope"]) != V1_5_2_COLLECT_BUFFER_MUTABILITY:
        raise ValueError("collect buffer mutability scope changed")
    false_flags = (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "release_action_authorized",
    )
    for flag in false_flags:
        if contract[flag] is not False:
            raise ValueError(f"v1.5.2 collect buffer contract must keep {flag}=False")
    for phrase in (
        "do not authorize true zero-copy",
        "public speedup wording",
        "whole-app claims",
        "release action",
    ):
        if phrase not in contract["claim_boundary"]:
            raise ValueError("collect buffer claim boundary is incomplete")
    return contract


def v1_5_2_prepared_buffer_reuse_gate() -> dict[str, Any]:
    """Return the evidence gate for future prepared-buffer reuse claims."""
    return {
        "status": V1_5_2_PREPARED_BUFFER_REUSE_GATE_STATUS,
        "track": "python_rtdl",
        "primitive": "COLLECT_K_BOUNDED",
        "current_envelopes": (
            "python_reference_prepared_descriptor_envelope",
            "native_generic_symbol_prepared_descriptor_envelope",
        ),
        "required_evidence": V1_5_2_PREPARED_BUFFER_REUSE_REQUIRED_EVIDENCE,
        "satisfied_evidence": V1_5_2_PREPARED_BUFFER_REUSE_SATISFIED_EVIDENCE,
        "missing_evidence": V1_5_2_PREPARED_BUFFER_REUSE_MISSING_EVIDENCE,
        "blocked_claims": V1_5_2_PREPARED_BUFFER_REUSE_BLOCKED_CLAIMS,
        "prepared_buffer_reuse_proven": False,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "v1.5.2 prepared collect-buffer envelopes now include source-level "
            "native ABI pointer shape and Python wrapper host ctypes output "
            "pointer plumbing with Python-wrapper host buffer reuse measurement. "
            "Embree/OptiX parity is accepted for the same prepared "
            "host-output contract, and external claim review is accepted. "
            "Prepared-buffer reuse, true zero-copy, public speedup wording, "
            "whole-app claims, stable primitive wording, and release action "
            "remain blocked for separate claim-specific gates."
        ),
    }


def validate_v1_5_2_prepared_buffer_reuse_gate() -> dict[str, Any]:
    gate = v1_5_2_prepared_buffer_reuse_gate()
    if gate["status"] != V1_5_2_PREPARED_BUFFER_REUSE_GATE_STATUS:
        raise ValueError("invalid v1.5.2 prepared buffer reuse gate status")
    if tuple(gate["required_evidence"]) != V1_5_2_PREPARED_BUFFER_REUSE_REQUIRED_EVIDENCE:
        raise ValueError("prepared buffer reuse required evidence changed")
    if tuple(gate["satisfied_evidence"]) != V1_5_2_PREPARED_BUFFER_REUSE_SATISFIED_EVIDENCE:
        raise ValueError("prepared buffer reuse satisfied evidence changed")
    if tuple(gate["missing_evidence"]) != V1_5_2_PREPARED_BUFFER_REUSE_MISSING_EVIDENCE:
        raise ValueError("prepared buffer reuse missing evidence changed")
    if tuple(gate["blocked_claims"]) != V1_5_2_PREPARED_BUFFER_REUSE_BLOCKED_CLAIMS:
        raise ValueError("prepared buffer reuse blocked claims changed")
    false_flags = (
        "prepared_buffer_reuse_proven",
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "release_action_authorized",
    )
    for flag in false_flags:
        if gate[flag] is not False:
            raise ValueError(f"v1.5.2 prepared buffer reuse gate must keep {flag}=False")
    for phrase in (
        "source-level native ABI pointer shape",
        "Python wrapper host ctypes output pointer plumbing",
        "host buffer reuse measurement",
        "Embree/OptiX parity",
        "true zero-copy",
        "public speedup wording",
        "external claim review",
    ):
        if phrase not in gate["claim_boundary"]:
            raise ValueError("prepared buffer reuse gate claim boundary is incomplete")
    return gate


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_release_surface_doc(relative_path: str) -> str:
    path = _repo_root() / relative_path
    if not path.exists():
        raise ValueError(f"missing v1.5.2 release-surface candidate doc: {relative_path}")
    return path.read_text(encoding="utf-8")


def v1_5_2_prepared_host_output_release_surface_gate() -> dict[str, Any]:
    """Return the v1.5.2 candidate-doc gate for prepared host-output evidence."""
    evidence_gate = validate_v1_5_2_prepared_buffer_reuse_gate()
    docs = {
        relative_path: _read_release_surface_doc(relative_path)
        for relative_path in V1_5_2_RELEASE_SURFACE_REQUIRED_DOCS
    }
    combined = "\n".join(docs.values())
    missing_required_phrases = tuple(
        phrase for phrase in V1_5_2_RELEASE_SURFACE_REQUIRED_PHRASES if phrase not in combined
    )
    present_forbidden_phrases = tuple(
        phrase for phrase in V1_5_2_RELEASE_SURFACE_FORBIDDEN_PHRASES if phrase in combined
    )
    return {
        "status": V1_5_2_RELEASE_SURFACE_GATE_STATUS,
        "primitive": evidence_gate["primitive"],
        "track": evidence_gate["track"],
        "classification": V1_5_2_RELEASE_SURFACE_CLASSIFICATION,
        "prepared_evidence_gate_status": evidence_gate["status"],
        "required_docs": V1_5_2_RELEASE_SURFACE_REQUIRED_DOCS,
        "required_phrases": V1_5_2_RELEASE_SURFACE_REQUIRED_PHRASES,
        "forbidden_phrases": V1_5_2_RELEASE_SURFACE_FORBIDDEN_PHRASES,
        "public_doc_link_consensus": (
            "docs/reports/three_ai_goal1458_v1_5_2_public_docs_link_consensus_2026-05-07.md"
        ),
        "missing_required_phrases": missing_required_phrases,
        "present_forbidden_phrases": present_forbidden_phrases,
        "candidate_docs_drafted": not missing_required_phrases and not present_forbidden_phrases,
        "external_release_surface_review_required": False,
        "external_release_surface_review_accepted": True,
        "public_docs_link_review_required": False,
        "public_docs_link_accepted": True,
        "publicly_discoverable": True,
        "explicit_release_approval_required": True,
        "public_docs_change_authorized_by_this_gate": False,
        "prepared_buffer_reuse_claim_authorized_by_this_gate": False,
        "stable_promotion_authorized_by_this_gate": False,
        "public_speedup_wording_authorized_by_this_gate": False,
        "zero_copy_wording_authorized_by_this_gate": False,
        "whole_app_speedup_claim_authorized_by_this_gate": False,
        "release_tag_action_authorized_by_this_gate": False,
        "allowed_next_actions": (
            "keep_candidate_docs_discoverable_without_broader_claims",
            "continue_python_rtdl_track_hardening",
            "request_explicit_v1_5_2_release_action_if_user_wants_release",
        ),
        "claim_boundary": (
            "The v1.5.2 prepared host-output candidate docs are publicly "
            "discoverable after Goal1458 3-AI public-doc-link consensus. "
            "This gate does not authorize public docs claims beyond the "
            "accepted candidate-doc link, prepared-buffer reuse claims, stable "
            "promotion, speedup wording, zero-copy wording, whole-app claims, "
            "or release tag action."
        ),
    }


def validate_v1_5_2_prepared_host_output_release_surface_gate() -> dict[str, Any]:
    gate = v1_5_2_prepared_host_output_release_surface_gate()
    if gate["status"] != V1_5_2_RELEASE_SURFACE_GATE_STATUS:
        raise ValueError("invalid v1.5.2 release-surface gate status")
    if gate["classification"] != V1_5_2_RELEASE_SURFACE_CLASSIFICATION:
        raise ValueError("invalid v1.5.2 release-surface classification")
    if tuple(gate["required_docs"]) != V1_5_2_RELEASE_SURFACE_REQUIRED_DOCS:
        raise ValueError("v1.5.2 release-surface required docs mismatch")
    if tuple(gate["missing_required_phrases"]) != ():
        raise ValueError(
            "v1.5.2 release-surface docs are missing required phrases: "
            f"{gate['missing_required_phrases']}"
        )
    if tuple(gate["present_forbidden_phrases"]) != ():
        raise ValueError(
            "v1.5.2 release-surface docs contain forbidden phrases: "
            f"{gate['present_forbidden_phrases']}"
        )
    if gate["candidate_docs_drafted"] is not True:
        raise ValueError("v1.5.2 candidate docs must be drafted")
    if gate["external_release_surface_review_required"] is not False:
        raise ValueError("v1.5.2 release surface external review should be complete")
    if gate["external_release_surface_review_accepted"] is not True:
        raise ValueError("v1.5.2 release surface must have accepted external review")
    if gate["public_docs_link_review_required"] is not False:
        raise ValueError("v1.5.2 public docs link review should be complete")
    if gate["public_docs_link_accepted"] is not True:
        raise ValueError("v1.5.2 public docs link must be accepted")
    if gate["publicly_discoverable"] is not True:
        raise ValueError("v1.5.2 candidate docs must be publicly discoverable")
    if gate["explicit_release_approval_required"] is not True:
        raise ValueError("v1.5.2 release surface must still require explicit release approval")
    false_flags = (
        "public_docs_change_authorized_by_this_gate",
        "prepared_buffer_reuse_claim_authorized_by_this_gate",
        "stable_promotion_authorized_by_this_gate",
        "public_speedup_wording_authorized_by_this_gate",
        "zero_copy_wording_authorized_by_this_gate",
        "whole_app_speedup_claim_authorized_by_this_gate",
        "release_tag_action_authorized_by_this_gate",
    )
    for flag in false_flags:
        if gate[flag] is not False:
            raise ValueError(f"v1.5.2 release-surface gate must keep {flag}=False")
    for phrase in (
        "publicly discoverable",
        "Goal1458 3-AI public-doc-link consensus",
        "does not authorize public docs claims beyond the accepted candidate-doc link",
        "prepared-buffer reuse claims",
        "stable promotion",
        "speedup wording",
        "zero-copy wording",
        "whole-app claims",
        "release tag action",
    ):
        if phrase not in gate["claim_boundary"]:
            raise ValueError("v1.5.2 release-surface claim boundary is incomplete")
    return gate


def collect_k_result_buffer_descriptor(
    result: dict[str, Any],
    *,
    row_width: int,
    backend: str | None = None,
    device: str = "cpu",
    owner: str = "python",
    mutability: str = "immutable",
    copy_boundary: str = "python_materialized_rows",
) -> dict[str, Any]:
    """Describe a completed collect-k result as an app-generic result buffer."""
    contract = validate_v1_5_2_collect_buffer_contract()
    if device not in V1_5_2_COLLECT_BUFFER_DEVICES:
        raise ValueError(f"unsupported collect buffer device: {device}")
    if copy_boundary not in V1_5_2_COLLECT_BUFFER_COPY_BOUNDARIES:
        raise ValueError(f"unsupported collect buffer copy_boundary: {copy_boundary}")
    validated = validate_collect_k_bounded_result(
        result,
        row_width=int(row_width),
        backend=backend,
    )
    capacity = int(validated["capacity"])
    valid_count = int(validated["valid_count"])
    descriptor = {
        "primitive": validated["primitive"],
        "status": contract["status"],
        "track": contract["track"],
        "buffer_kind": "result",
        "backend": validated.get("backend", backend),
        "dtype": "int64",
        "layout": contract["layout"],
        "shape": (capacity, int(row_width)),
        "valid_shape": (valid_count, int(row_width)),
        "capacity": capacity,
        "valid_count": valid_count,
        "row_width": int(row_width),
        "device": device,
        "owner": str(owner),
        "mutability": str(mutability),
        "copy_boundary": copy_boundary,
        "overflowed": False,
        "fail_closed": True,
        "materialized_python_rows_present": "candidate_id_rows" in validated,
        "candidate_id_rows_present": "candidate_id_rows" in validated,
        "source_result_layout": validated["result_layout"],
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": contract["claim_boundary"],
    }
    return validate_collect_result_buffer_descriptor(descriptor)


def prepare_collect_k_result_buffer_descriptor(
    *,
    capacity: int,
    row_width: int,
    backend: str | None = None,
    device: str = "cpu",
    owner: str = "rtdl",
    mutability: str = "mutable",
    copy_boundary: str = "prepared_host_buffer_reuse",
) -> dict[str, Any]:
    """Describe a caller-prepared collect-k output buffer before execution."""
    contract = validate_v1_5_2_collect_buffer_contract()
    capacity = int(capacity)
    row_width = int(row_width)
    descriptor = {
        "primitive": "COLLECT_K_BOUNDED",
        "status": contract["status"],
        "track": contract["track"],
        "buffer_kind": "prepared_result",
        "backend": backend,
        "dtype": "int64",
        "layout": contract["layout"],
        "shape": (capacity, row_width),
        "valid_shape": (0, row_width),
        "capacity": capacity,
        "valid_count": 0,
        "row_width": row_width,
        "device": device,
        "owner": str(owner),
        "mutability": str(mutability),
        "copy_boundary": copy_boundary,
        "overflowed": False,
        "fail_closed": True,
        "materialized_python_rows_present": False,
        "candidate_id_rows_present": False,
        "source_result_layout": None,
        "prepared_before_execution": True,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": contract["claim_boundary"],
    }
    return validate_collect_result_buffer_descriptor(descriptor)


def complete_prepared_collect_k_result_buffer_descriptor(
    prepared_descriptor: dict[str, Any],
    result: dict[str, Any],
    *,
    backend: str | None = None,
) -> dict[str, Any]:
    """Bind a validated collect-k result to a compatible prepared descriptor."""
    prepared = validate_collect_result_buffer_descriptor(prepared_descriptor)
    if prepared["buffer_kind"] != "prepared_result":
        raise ValueError("prepared collect buffer completion requires buffer_kind=prepared_result")
    if "row_width" in result and int(result["row_width"]) != prepared["row_width"]:
        raise ValueError("completed collect result row_width does not match prepared buffer")
    result_backend = backend if backend is not None else result.get("backend")
    result_descriptor = collect_k_result_buffer_descriptor(
        result,
        row_width=prepared["row_width"],
        backend=result_backend,
        device=prepared["device"],
        owner=prepared["owner"],
        mutability=prepared["mutability"],
        copy_boundary=prepared["copy_boundary"],
    )
    if result_descriptor["capacity"] > prepared["capacity"]:
        raise RuntimeError("completed collect result exceeds prepared buffer capacity")
    if result_descriptor["device"] != prepared["device"]:
        raise ValueError("completed collect result device does not match prepared buffer")
    prepared_backend = prepared.get("backend")
    completed_backend = result_descriptor.get("backend")
    if prepared_backend is not None and completed_backend is not None:
        if completed_backend != prepared_backend:
            raise ValueError("completed collect result backend mismatch")
    completed = {
        **result_descriptor,
        "buffer_kind": "result",
        "prepared_buffer_kind": prepared["buffer_kind"],
        "prepared_backend": prepared_backend,
        "prepared_before_execution": bool(prepared.get("prepared_before_execution", False)),
        "prepared_capacity": prepared["capacity"],
        "prepared_shape": prepared["shape"],
        "prepared_valid_shape": prepared["valid_shape"],
        "prepared_copy_boundary": prepared["copy_boundary"],
        "prepared_descriptor_compatible": True,
    }
    return validate_collect_result_buffer_descriptor(completed)


def run_collect_k_bounded_rows_with_prepared_result_buffer(
    candidate_rows: Any,
    prepared_descriptor: dict[str, Any],
) -> dict[str, Any]:
    """Run the Python reference collector through a prepared descriptor envelope."""
    prepared = validate_collect_result_buffer_descriptor(prepared_descriptor)
    if prepared["buffer_kind"] != "prepared_result":
        raise ValueError("prepared collect buffer execution requires buffer_kind=prepared_result")
    result = collect_k_bounded_rows(
        candidate_rows,
        k=prepared["capacity"],
        row_width=prepared["row_width"],
    )
    completed_descriptor = complete_prepared_collect_k_result_buffer_descriptor(
        prepared,
        result,
    )
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": prepared["status"],
        "track": prepared["track"],
        "execution_mode": "python_reference_prepared_descriptor_envelope",
        "backend": prepared.get("backend"),
        "prepared_descriptor": prepared,
        "result": result,
        "result_buffer_descriptor": completed_descriptor,
        "prepared_descriptor_compatible": completed_descriptor["prepared_descriptor_compatible"],
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Python reference execution envelope over prepared collect-buffer "
            "metadata only; this does not allocate native memory, prove buffer "
            "reuse, authorize zero-copy wording, or authorize performance claims."
        ),
    }


def run_native_collect_k_bounded_rows_with_prepared_result_buffer(
    candidate_rows: Any,
    prepared_descriptor: dict[str, Any],
    *,
    library: Any,
    symbol_name: str,
    candidate_source_symbol: str,
    backend: str | None = None,
) -> dict[str, Any]:
    """Run the native generic collect-k symbol through a prepared descriptor envelope."""
    prepared = validate_collect_result_buffer_descriptor(prepared_descriptor)
    if prepared["buffer_kind"] != "prepared_result":
        raise ValueError("native prepared collect execution requires buffer_kind=prepared_result")
    resolved_backend = backend if backend is not None else prepared.get("backend")
    if not resolved_backend:
        raise ValueError("native prepared collect execution requires an explicit backend")
    if prepared.get("backend") is not None and prepared.get("backend") != resolved_backend:
        raise ValueError("native prepared collect execution backend mismatch")
    result = collect_native_i64_rows_with_backend_symbol(
        candidate_rows,
        capacity=prepared["capacity"],
        row_width=prepared["row_width"],
        backend=str(resolved_backend),
        library=library,
        symbol_name=str(symbol_name),
        candidate_source_symbol=str(candidate_source_symbol),
    )
    completed_descriptor = complete_prepared_collect_k_result_buffer_descriptor(
        prepared,
        result,
        backend=str(resolved_backend),
    )
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": prepared["status"],
        "track": prepared["track"],
        "execution_mode": "native_generic_symbol_prepared_descriptor_envelope",
        "backend": str(resolved_backend),
        "symbol_name": str(symbol_name),
        "candidate_source_symbol": str(candidate_source_symbol),
        "prepared_descriptor": prepared,
        "result": result,
        "result_buffer_descriptor": completed_descriptor,
        "prepared_descriptor_compatible": completed_descriptor["prepared_descriptor_compatible"],
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Native generic symbol execution envelope over prepared "
            "collect-buffer metadata only. The current Python wrapper still "
            "marshals rows through ctypes-managed buffers; this does not prove "
            "prepared-buffer reuse, authorize zero-copy wording, or authorize "
            "performance claims."
        ),
    }


def run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
    candidate_rows: Any,
    prepared_descriptor: dict[str, Any],
    *,
    output_buffer: Any,
    library: Any,
    symbol_name: str,
    candidate_source_symbol: str,
    backend: str | None = None,
) -> dict[str, Any]:
    """Run the native generic collect-k symbol into caller-owned host storage."""
    prepared = validate_collect_result_buffer_descriptor(prepared_descriptor)
    if prepared["buffer_kind"] != "prepared_result":
        raise ValueError("native prepared host output execution requires buffer_kind=prepared_result")
    if prepared["device"] != "cpu":
        raise ValueError("native prepared host output execution requires device=cpu")
    if prepared["copy_boundary"] != "prepared_host_buffer_reuse":
        raise ValueError(
            "native prepared host output execution requires copy_boundary=prepared_host_buffer_reuse"
        )
    resolved_backend = backend if backend is not None else prepared.get("backend")
    if not resolved_backend:
        raise ValueError("native prepared host output execution requires an explicit backend")
    if prepared.get("backend") is not None and prepared.get("backend") != resolved_backend:
        raise ValueError("native prepared host output execution backend mismatch")
    result = collect_native_i64_rows_into_prepared_output_buffer(
        candidate_rows,
        output_buffer=output_buffer,
        capacity=prepared["capacity"],
        row_width=prepared["row_width"],
        backend=str(resolved_backend),
        library=library,
        symbol_name=str(symbol_name),
        candidate_source_symbol=str(candidate_source_symbol),
    )
    completed_descriptor = complete_prepared_collect_k_result_buffer_descriptor(
        prepared,
        result,
        backend=str(resolved_backend),
    )
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": prepared["status"],
        "track": prepared["track"],
        "execution_mode": "native_generic_symbol_prepared_host_output_envelope",
        "backend": str(resolved_backend),
        "symbol_name": str(symbol_name),
        "candidate_source_symbol": str(candidate_source_symbol),
        "prepared_descriptor": prepared,
        "result": result,
        "result_buffer_descriptor": completed_descriptor,
        "prepared_descriptor_compatible": completed_descriptor["prepared_descriptor_compatible"],
        "prepared_output_buffer_supplied": result["prepared_output_buffer_supplied"],
        "prepared_output_buffer_kind": result["prepared_output_buffer_kind"],
        "prepared_output_buffer_reused_by_python_wrapper": result[
            "prepared_output_buffer_reused_by_python_wrapper"
        ],
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Native generic symbol execution envelope over caller-owned "
            "ctypes host output storage. This proves Python-wrapper host "
            "pointer passing only; it does not prove measured reuse, "
            "device-resident output, true zero-copy, or performance claims."
        ),
    }


def measure_native_collect_k_prepared_host_output_reuse(
    candidate_rows: Any,
    prepared_descriptor: dict[str, Any],
    *,
    output_buffer: Any,
    library: Any,
    symbol_name: str,
    candidate_source_symbol: str,
    backend: str | None = None,
    iterations: int = 3,
) -> dict[str, Any]:
    """Measure repeated host-output envelope use of one caller-owned buffer."""
    iteration_count = int(iterations)
    if iteration_count <= 0:
        raise ValueError("prepared host output reuse measurement requires iterations > 0")
    runs = []
    elapsed_total_s = 0.0
    for iteration in range(iteration_count):
        if output_buffer is None:
            iteration_buffer_address = None
        else:
            iteration_buffer_address = ctypes.addressof(output_buffer)
        start = time.perf_counter()
        envelope = run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
            candidate_rows,
            prepared_descriptor,
            output_buffer=output_buffer,
            library=library,
            symbol_name=symbol_name,
            candidate_source_symbol=candidate_source_symbol,
            backend=backend,
        )
        elapsed_s = time.perf_counter() - start
        elapsed_total_s += elapsed_s
        runs.append(
            {
                "iteration": iteration,
                "output_buffer_address": iteration_buffer_address,
                "elapsed_s": elapsed_s,
                "valid_shape": envelope["result_buffer_descriptor"]["valid_shape"],
                "valid_count": envelope["result"]["valid_count"],
                "prepared_descriptor_compatible": envelope["prepared_descriptor_compatible"],
            }
        )
    addresses = tuple(run["output_buffer_address"] for run in runs)
    stable_address = len(set(addresses)) <= 1
    buffer_address = addresses[0]
    return {
        "primitive": "COLLECT_K_BOUNDED",
        "status": "host_prepared_output_reuse_measured_python_wrapper_scope",
        "track": "python_rtdl",
        "iterations": iteration_count,
        "output_buffer_address": buffer_address,
        "stable_output_buffer_address": stable_address,
        "runs": tuple(runs),
        "elapsed_total_s": elapsed_total_s,
        "average_elapsed_s": elapsed_total_s / iteration_count,
        "host_reuse_or_device_reuse_measured": True,
        "measurement_scope": "python_wrapper_ctypes_host_output_buffer_reuse_only",
        "device_reuse_measured": False,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This measurement observes repeated Python-wrapper use of one "
            "caller-owned ctypes host output buffer address only. It does not "
            "measure device reuse, true zero-copy, public speedup, whole-app "
            "speedup, stable primitive readiness, or release readiness."
        ),
    }


def validate_native_collect_k_prepared_host_output_overflow_fail_closed(
    candidate_rows: Any,
    prepared_descriptor: dict[str, Any],
    *,
    output_buffer: Any,
    library: Any,
    symbol_name: str,
    candidate_source_symbol: str,
    backend: str | None = None,
) -> dict[str, Any]:
    """Validate that prepared host-output execution fails closed on overflow."""
    try:
        run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
            candidate_rows,
            prepared_descriptor,
            output_buffer=output_buffer,
            library=library,
            symbol_name=symbol_name,
            candidate_source_symbol=candidate_source_symbol,
            backend=backend,
        )
    except RuntimeError as exc:
        message = str(exc)
        if "overflowed capacity" not in message:
            raise
        return {
            "primitive": "COLLECT_K_BOUNDED",
            "status": "prepared_host_output_overflow_fail_closed_validated",
            "track": "python_rtdl",
            "overflow_fail_closed_with_prepared_buffer": True,
            "partial_result_returned": False,
            "exception_type": type(exc).__name__,
            "exception_message": message,
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "release_action_authorized": False,
            "claim_boundary": (
                "Prepared host-output overflow validation confirms fail-closed "
                "Python-wrapper behavior for caller-owned ctypes host output "
                "storage only. It does not prove Embree/OptiX parity, true "
                "zero-copy, speedup, stable promotion, or release readiness."
            ),
        }
    raise AssertionError("prepared host-output overflow validation did not fail closed")


def validate_collect_result_buffer_descriptor(descriptor: dict[str, Any]) -> dict[str, Any]:
    contract = validate_v1_5_2_collect_buffer_contract()
    missing = [field for field in contract["required_fields"] if field not in descriptor]
    if missing:
        raise ValueError(f"collect result buffer descriptor missing fields: {tuple(missing)}")
    if descriptor["buffer_kind"] not in V1_5_2_COLLECT_BUFFER_KINDS:
        raise ValueError("collect result buffer descriptor has invalid buffer_kind")
    if descriptor["dtype"] not in V1_5_2_COLLECT_BUFFER_DTYPES:
        raise ValueError("collect result buffer descriptor has invalid dtype")
    if descriptor["layout"] != V1_5_2_COLLECT_BUFFER_LAYOUT:
        raise ValueError("collect result buffer descriptor has invalid layout")
    if descriptor["device"] not in V1_5_2_COLLECT_BUFFER_DEVICES:
        raise ValueError("collect result buffer descriptor has invalid device")
    if descriptor["owner"] not in V1_5_2_COLLECT_BUFFER_OWNERS:
        raise ValueError("collect result buffer descriptor has invalid owner")
    if descriptor["mutability"] not in V1_5_2_COLLECT_BUFFER_MUTABILITY:
        raise ValueError("collect result buffer descriptor has invalid mutability")
    if descriptor["copy_boundary"] not in V1_5_2_COLLECT_BUFFER_COPY_BOUNDARIES:
        raise ValueError("collect result buffer descriptor has invalid copy_boundary")
    capacity = int(descriptor["capacity"])
    valid_count = int(descriptor["valid_count"])
    row_width = int(descriptor["row_width"])
    if capacity < 0 or valid_count < 0 or row_width <= 0:
        raise ValueError("collect result buffer descriptor has invalid dimensions")
    if valid_count > capacity:
        raise ValueError("collect result buffer descriptor valid_count exceeds capacity")
    if tuple(descriptor["shape"]) != (capacity, row_width):
        raise ValueError("collect result buffer descriptor shape mismatch")
    if tuple(descriptor.get("valid_shape", (valid_count, row_width))) != (valid_count, row_width):
        raise ValueError("collect result buffer descriptor valid_shape mismatch")
    if descriptor["overflowed"] is not False:
        raise RuntimeError("collect result buffer descriptor must fail closed on overflow")
    if descriptor["fail_closed"] is not True:
        raise RuntimeError("collect result buffer descriptor must declare fail_closed=True")
    false_flags = (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "release_action_authorized",
    )
    for flag in false_flags:
        if descriptor.get(flag) is not False:
            raise ValueError(f"collect result buffer descriptor must keep {flag}=False")
    return {
        **descriptor,
        "capacity": capacity,
        "valid_count": valid_count,
        "row_width": row_width,
        "shape": (capacity, row_width),
        "valid_shape": (valid_count, row_width),
    }
