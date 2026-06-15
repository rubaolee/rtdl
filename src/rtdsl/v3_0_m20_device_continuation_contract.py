from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import validate_v3_public_name


V3_M20_DEVICE_CONTINUATION_CONTRACT_VERSION = "rtdl.v3_0.device_continuation_contract.m20"
V3_M20_DEVICE_CONTINUATION_CONTRACT_STATUS = (
    "m20_prepared_native_output_partner_device_continuation_contract_internal_claims_gated"
)
V3_M20_GRAPH_ID = "prepared_native_output_partner_device_continuation"
V3_M20_CONTRACT_KEY = "prepared_native_device_payload_ordered_partner_finalize_v1"
V3_M20_ALLOWED_APP_STATES = (
    "clean_device_continuation_evidence_ready",
    "primitive_only_no_partner_needed",
    "needs_fused_or_prepared_device_continuation_bridge",
    "currently_not_a_rt_core_claim_target",
)
V3_M20_FORBIDDEN_CLAIM_FLAGS = (
    "public_speedup_claim_authorized",
    "rt_core_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "true_zero_copy_public_claim_authorized",
    "automatic_partner_selection_authorized",
    "paper_or_author_parity_claim_authorized",
)


@dataclass(frozen=True)
class V3M20ContractPhase:
    phase_id: str
    required_property: str
    measured_window_role: str
    materialization_policy: str

    def to_metadata(self) -> dict[str, object]:
        validate_v3_public_name(self.phase_id, label="M20 phase id")
        return {
            "phase_id": self.phase_id,
            "required_property": self.required_property,
            "measured_window_role": self.measured_window_role,
            "materialization_policy": self.materialization_policy,
        }


@dataclass(frozen=True)
class V3M20AppAuditRow:
    app: str
    state: str
    current_best_contract: str
    partner_position: str
    evidence_refs: tuple[str, ...]
    next_action: str
    detail_rows: tuple[str, ...] = ()
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    true_zero_copy_public_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    paper_or_author_parity_claim_authorized: bool = False

    def to_metadata(self) -> dict[str, object]:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise GraphValidationError(f"M20 row has unknown benchmark app {self.app!r}")
        if self.state not in V3_M20_ALLOWED_APP_STATES:
            raise GraphValidationError(f"{self.app}: unsupported M20 state {self.state!r}")
        if not self.current_best_contract:
            raise GraphValidationError(f"{self.app}: current_best_contract is required")
        if not self.partner_position:
            raise GraphValidationError(f"{self.app}: partner_position is required")
        if not self.evidence_refs:
            raise GraphValidationError(f"{self.app}: evidence_refs are required")
        if not self.next_action:
            raise GraphValidationError(f"{self.app}: next_action is required")
        metadata = {
            "app": self.app,
            "state": self.state,
            "current_best_contract": self.current_best_contract,
            "partner_position": self.partner_position,
            "evidence_refs": self.evidence_refs,
            "next_action": self.next_action,
            "detail_rows": self.detail_rows,
        }
        for flag in V3_M20_FORBIDDEN_CLAIM_FLAGS:
            value = bool(getattr(self, flag))
            if value:
                raise GraphValidationError(f"{self.app}: M20 must not authorize {flag}")
            metadata[flag] = False
        return metadata


def v3_m20_device_continuation_phases() -> tuple[dict[str, object], ...]:
    return tuple(phase.to_metadata() for phase in _PHASES)


def v3_m20_device_continuation_audit_rows() -> tuple[dict[str, object], ...]:
    return tuple(row.to_metadata() for row in _APP_ROWS)


def v3_m20_device_continuation_contract_packet() -> dict[str, object]:
    validate_v3_public_name(V3_M20_GRAPH_ID, label="M20 graph id")
    payload = {
        "version": V3_M20_DEVICE_CONTINUATION_CONTRACT_VERSION,
        "status": V3_M20_DEVICE_CONTINUATION_CONTRACT_STATUS,
        "graph_id": V3_M20_GRAPH_ID,
        "contract_key": V3_M20_CONTRACT_KEY,
        "phases": v3_m20_device_continuation_phases(),
        "app_audit_rows": v3_m20_device_continuation_audit_rows(),
        "summary": {},
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "paper_or_author_parity_claim_authorized": False,
            "reason": (
                "M20 consolidates internal V3 evidence into an app-agnostic prepared native "
                "device-output to ordered partner continuation to explicit finalize contract. "
                "It is a planning/readiness contract only, not a public performance claim."
            ),
        },
    }
    rows = tuple(payload["app_audit_rows"])
    state_counts = {state: sum(1 for row in rows if row["state"] == state) for state in V3_M20_ALLOWED_APP_STATES}
    payload["summary"] = {
        "promoted_app_count": len(V2_8_PROMOTED_BENCHMARK_APPS),
        "row_count": len(rows),
        "state_counts": state_counts,
        "ready_or_primitive_only_count": (
            state_counts["clean_device_continuation_evidence_ready"]
            + state_counts["primitive_only_no_partner_needed"]
        ),
        "bridge_debt_count": state_counts["needs_fused_or_prepared_device_continuation_bridge"],
        "public_claim_authorized": False,
    }
    validate_v3_m20_device_continuation_contract_packet(payload)
    return payload


def validate_v3_m20_device_continuation_contract_packet(payload: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise GraphValidationError("M20 payload must be a mapping")
    if payload.get("version") != V3_M20_DEVICE_CONTINUATION_CONTRACT_VERSION:
        raise GraphValidationError("unexpected M20 payload version")
    if payload.get("status") != V3_M20_DEVICE_CONTINUATION_CONTRACT_STATUS:
        raise GraphValidationError("unexpected M20 payload status")
    validate_v3_public_name(str(payload.get("graph_id", "")), label="M20 graph id")
    phases = tuple(payload.get("phases", ()))
    if len(phases) != len(_PHASES):
        raise GraphValidationError("M20 payload must include every contract phase")
    phase_ids = [str(phase.get("phase_id")) for phase in phases if isinstance(phase, Mapping)]
    if len(set(phase_ids)) != len(_PHASES):
        raise GraphValidationError("M20 phase ids must be unique")

    rows = tuple(payload.get("app_audit_rows", ()))
    apps = {str(row.get("app")) for row in rows if isinstance(row, Mapping)}
    if len(rows) != len(V2_8_PROMOTED_BENCHMARK_APPS) or len(apps) != len(rows):
        raise GraphValidationError("M20 audit rows must be unique and match the promoted app count")
    if apps != set(V2_8_PROMOTED_BENCHMARK_APPS):
        raise GraphValidationError("M20 audit must cover exactly the promoted benchmark apps")
    states = {state: 0 for state in V3_M20_ALLOWED_APP_STATES}
    for row in rows:
        if not isinstance(row, Mapping):
            raise GraphValidationError("M20 audit row must be a mapping")
        app = str(row.get("app"))
        state = str(row.get("state"))
        if state not in V3_M20_ALLOWED_APP_STATES:
            raise GraphValidationError(f"{app}: unsupported M20 audit state")
        states[state] += 1
        if not row.get("evidence_refs"):
            raise GraphValidationError(f"{app}: evidence_refs are required")
        if not row.get("next_action"):
            raise GraphValidationError(f"{app}: next_action is required")
        for flag in V3_M20_FORBIDDEN_CLAIM_FLAGS:
            if bool(row.get(flag)):
                raise GraphValidationError(f"{app}: M20 must not authorize {flag}")

    if states["clean_device_continuation_evidence_ready"] < 1:
        raise GraphValidationError("M20 requires at least one measured clean device-continuation row")
    if states["needs_fused_or_prepared_device_continuation_bridge"] < 1:
        raise GraphValidationError("M20 must preserve remaining bridge debt")
    summary = payload.get("summary", {})
    if not isinstance(summary, Mapping):
        raise GraphValidationError("M20 payload requires summary")
    if int(summary.get("row_count", -1)) != len(V2_8_PROMOTED_BENCHMARK_APPS):
        raise GraphValidationError("M20 summary row_count mismatch")
    if bool(summary.get("public_claim_authorized")):
        raise GraphValidationError("M20 summary must not authorize public claims")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("M20 payload requires claim boundary")
    for flag in V3_M20_FORBIDDEN_CLAIM_FLAGS:
        if bool(boundary.get(flag)):
            raise GraphValidationError(f"M20 claim boundary must not authorize {flag}")
    return {
        "status": V3_M20_DEVICE_CONTINUATION_CONTRACT_STATUS,
        "phase_count": len(phases),
        "row_count": len(rows),
        "state_counts": states,
        "public_claim_authorized": False,
    }


_PHASES = (
    V3M20ContractPhase(
        phase_id="prepared_native_producer",
        required_property="native scene/query/output state is prepared or explicitly resident before the hot window",
        measured_window_role="prepare window is recorded separately when it performs initial uploads or graph build",
        materialization_policy="no result materialization is allowed in the hot continuation window",
    ),
    V3M20ContractPhase(
        phase_id="device_payload_handoff",
        required_property="native output is represented as typed device payload columns or partial rows",
        measured_window_role="payload pointer, size, stream/order token, and ownership metadata are explicit",
        materialization_policy="host row materialization before partner handoff blocks the clean-device state",
    ),
    V3M20ContractPhase(
        phase_id="ordered_partner_device_continuation",
        required_property="partner continuation runs on the same stream or waits on an explicit producer event",
        measured_window_role="transfer counter must show no named-column H2D, no D2H, no D2D, and no unknown copies",
        materialization_policy="partner may produce device summaries, flags, compact rows, or grouped aggregates",
    ),
    V3M20ContractPhase(
        phase_id="explicit_finalize",
        required_property="validation or user-facing materialization is a named finalization phase after the hot window",
        measured_window_role="finalize timing is reported separately from native traversal plus partner device continuation",
        materialization_policy="finalize may copy compact summaries to host but must not be counted as hot zero-copy evidence",
    ),
)


_APP_ROWS = (
    V3M20AppAuditRow(
        app="hausdorff_xhd",
        state="needs_fused_or_prepared_device_continuation_bridge",
        current_best_contract="typed nearest-witness stream plus grouped max-distance continuation",
        partner_position="Numba exact continuation remains the likely reference; CuPy is a useful CUDA-core comparison row",
        evidence_refs=("v2.8 typed nearest-witness metadata", "M13-M17 hit-stream no-hidden-copy evidence"),
        next_action=(
            "turn nearest-witness output into a prepared device payload plus ordered max-reduction finalize window"
        ),
    ),
    V3M20AppAuditRow(
        app="spatial_rayjoin",
        state="needs_fused_or_prepared_device_continuation_bridge",
        current_best_contract="scalar LSI/PIP rows plus overlay decomposition with device-column point-location work",
        partner_position=(
            "LSI/PIP scalar-count rows need no hidden partner; overlay still needs an explicit fused/prepared "
            "device continuation for point-location and compose phases"
        ),
        evidence_refs=("M18 grouped device contract", "Goal4376 overlay device-column evidence", "RayJoin closeout report"),
        next_action="build a reusable overlay-style point-location continuation contract before public overlay wording",
        detail_rows=("lsi_scalar_count", "pip_scalar_count", "overlay_lsi_point_location_compose"),
    ),
    V3M20AppAuditRow(
        app="rt_dbscan",
        state="needs_fused_or_prepared_device_continuation_bridge",
        current_best_contract="fixed-radius core flags plus explicit component-label continuation",
        partner_position="Numba is required for the reference component-label continuation; CuPy should remain the best CUDA-core row",
        evidence_refs=("M10 same-stream evidence", "M16/M17 partner device-ray evidence"),
        next_action="connect fixed-radius core/border outputs to same-stream component labeling with transfer-counter evidence",
    ),
    V3M20AppAuditRow(
        app="robot_collision",
        state="primitive_only_no_partner_needed",
        current_best_contract="prepared grouped segment any-hit flags",
        partner_position="primitive-only row unless later collision-response logic becomes part of the measured contract",
        evidence_refs=("v2.14 cleanup matrix", "prepared any-hit route evidence"),
        next_action="refresh same-contract OptiX/Embree measurement and keep response logic outside the RT hot row",
    ),
    V3M20AppAuditRow(
        app="contact_manifold",
        state="primitive_only_no_partner_needed",
        current_best_contract="generic AABB broadphase collect-k candidates",
        partner_position="primitive-only broadphase; exact manifold interpretation remains app logic after candidate output",
        evidence_refs=("v2.14 cleanup matrix", "AABB collect-k comparison packets"),
        next_action="refresh large prepared broadphase measurement and explain candidate compactness/materialization cost",
    ),
    V3M20AppAuditRow(
        app="raydb_style",
        state="primitive_only_no_partner_needed",
        current_best_contract="prepared ray-triangle grouped i64 native reduction",
        partner_position="native grouped reduction is the preferred row; partner rows only for intentionally unfused variants",
        evidence_refs=("v2.14 cleanup matrix", "grouped i64 primitive evidence"),
        next_action="rerun prepared grouped reduction and preserve primitive-first wording",
    ),
    V3M20AppAuditRow(
        app="barnes_hut",
        state="needs_fused_or_prepared_device_continuation_bridge",
        current_best_contract="prepared fixed-radius node-coverage threshold decision",
        partner_position="Numba exact-force remains a separated reference path, not hidden inside the RT-core row",
        evidence_refs=("v2.14 cleanup matrix", "node-coverage route evidence"),
        next_action="separate coverage decision, device-side ranked summary, and exact force finalize windows",
    ),
    V3M20AppAuditRow(
        app="librts_spatial_index",
        state="primitive_only_no_partner_needed",
        current_best_contract="generic prepared AABB index query 2D all-ops",
        partner_position="primitive-only all-ops row; no partner is needed for the current comparison contract",
        evidence_refs=("v2.14 cleanup matrix", "native AABB index query cleanup"),
        next_action="refresh prepared all-ops OptiX/Embree evidence at human-scale query sizes",
    ),
    V3M20AppAuditRow(
        app="rtnn",
        state="clean_device_continuation_evidence_ready",
        current_best_contract="prepared fixed-radius ranked-summary graph partial rows plus same-stream device reduction",
        partner_position="CuPy is the best CUDA-core partner row; Numba is the no-C++ reference row after CUDA 12.4 NVVM alignment",
        evidence_refs=("M19 ranked-summary bridge artifact", "M19 toolchain note"),
        next_action="carry M19 into the benchmark matrix, but keep public speedup and paper-parity wording disabled",
    ),
    V3M20AppAuditRow(
        app="triangle_counting",
        state="currently_not_a_rt_core_claim_target",
        current_best_contract="RT-2A1 generic ray/triangle any-hit summary",
        partner_position="primitive-only summary row; graph counting semantics remain outside current RT hot-window evidence",
        evidence_refs=("v2.14 cleanup matrix", "RT-2A1 any-hit summary evidence"),
        next_action="refresh primitive summary row and avoid claiming whole graph acceleration",
    ),
)
