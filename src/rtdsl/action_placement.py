from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import product
import math
from typing import Mapping, NoReturn

from .action_ir import (
    ActionEffect,
    ActionScalarKind,
    ActionScalarType,
    ActionSpec,
    ActionTupleType,
    DeliveryEnforcement,
    ExtentKind,
    StateScope,
    evaluate_capacity,
    verify_action_spec,
)


ACTION_PLACEMENT_VERSION = "rtdl.action_placement.v1"
ACTION_COST_MODEL_VERSION = "rtdl.action_cost_model.private_candidate.v1"


def uniform_grid_candidate_density_upper_bound(points, radius: float) -> float:
    """Return a cheap conservative Euclidean-radius pair-density bound."""

    if not isinstance(radius, (int, float)) or not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius must be finite and positive")
    rows = [tuple(float(value) for value in row) for row in points]
    if not rows:
        raise ValueError("points must be nonempty")
    dimension = len(rows[0])
    if dimension < 1 or any(len(row) != dimension for row in rows):
        raise ValueError("points must have one stable positive dimension")
    if any(not math.isfinite(value) for row in rows for value in row):
        raise ValueError("point coordinates must be finite")
    cell_counts: dict[tuple[int, ...], int] = {}
    inverse_radius = 1.0 / float(radius)
    for row in rows:
        cell = tuple(math.floor(value * inverse_radius) for value in row)
        cell_counts[cell] = cell_counts.get(cell, 0) + 1
    offsets = tuple(product((-1, 0, 1), repeat=dimension))
    candidate_upper_bound = 0
    for cell, count in cell_counts.items():
        neighbor_count = sum(
            cell_counts.get(
                tuple(cell[axis] + offset[axis] for axis in range(dimension)),
                0,
            )
            for offset in offsets
        )
        candidate_upper_bound += count * neighbor_count
    row_count = len(rows)
    return min(1.0, float(candidate_upper_bound) / float(row_count * row_count))


class ActionPlacementKind(str, Enum):
    TRAVERSAL_FUSED = "traversal_fused"
    TRAVERSAL_DEVICE_CONTINUATION = "traversal_device_continuation"
    DEVICE_CONTINUATION = "device_continuation"
    HOST_CONTINUATION = "host_continuation"
    CPU_REFERENCE = "cpu_reference"


class ActionStateStorage(str, Enum):
    INLINE_PER_SCOPE = "inline_per_scope"
    DEVICE_GLOBAL = "device_global"
    HOST = "host"


class ActionCostModelStatus(str, Enum):
    NOT_REQUESTED = "not_requested"
    APPLIED = "applied"
    UNAVAILABLE_OR_OUT_OF_DOMAIN = "unavailable_or_out_of_domain"


class ActionTransferAccounting(str, Enum):
    INDEPENDENTLY_MEASURED = "independently_measured"
    PREDICTED_FROM_EXPLICIT_BYTES = "predicted_from_explicit_bytes"
    FOLDED_INELIGIBLE = "folded_ineligible"


class ActionCalibrationMode(str, Enum):
    COMPONENT_MODEL = "component_model"
    EXACT_OBSERVED_TOTAL = "exact_observed_total"


@dataclass(frozen=True)
class ActionCostFeatures:
    """Application-neutral workload facts used only after legality succeeds."""

    producer_kind: str
    resident_representation: str
    search_count: int
    query_count: int
    candidate_density_upper_bound: float
    expected_query_batches: int
    module_ready: bool
    index_ready: bool
    predicted_h2d_bytes: int | None
    predicted_d2h_bytes: int | None
    transfer_accounting: ActionTransferAccounting
    calibration_version: str
    phase_evidence_digest: str
    predicted_output_bytes: int | None = None
    calibration_evidence_digest: str | None = None
    feature_acquisition_seconds: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "producer_kind",
            "resident_representation",
            "calibration_version",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value or any(char.isspace() for char in value):
                raise ValueError(f"{name} must be a nonempty identifier")
        for name in (
            "search_count",
            "query_count",
            "expected_query_batches",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.expected_query_batches < 1:
            raise ValueError("expected_query_batches must be at least one")
        density = self.candidate_density_upper_bound
        if not isinstance(density, (int, float)) or not math.isfinite(density):
            raise ValueError("candidate_density_upper_bound must be finite")
        if density < 0.0 or density > 1.0:
            raise ValueError("candidate_density_upper_bound must be in [0, 1]")
        if not isinstance(self.transfer_accounting, ActionTransferAccounting):
            raise ValueError("transfer_accounting must be an ActionTransferAccounting")
        for name in ("predicted_h2d_bytes", "predicted_d2h_bytes"):
            value = getattr(self, name)
            if value is None:
                if self.transfer_accounting is not ActionTransferAccounting.FOLDED_INELIGIBLE:
                    raise ValueError(
                        f"{name} may be unknown only for folded-ineligible accounting"
                    )
            elif not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer or None")
        if (
            self.predicted_output_bytes is not None
            and (
                not isinstance(self.predicted_output_bytes, int)
                or isinstance(self.predicted_output_bytes, bool)
                or self.predicted_output_bytes < 0
            )
        ):
            raise ValueError("predicted_output_bytes must be a nonnegative integer or None")
        _require_sha256(self.phase_evidence_digest, "phase_evidence_digest")
        if self.calibration_evidence_digest is not None:
            _require_sha256(
                self.calibration_evidence_digest,
                "calibration_evidence_digest",
            )
        if (
            not isinstance(self.feature_acquisition_seconds, (int, float))
            or not math.isfinite(self.feature_acquisition_seconds)
            or self.feature_acquisition_seconds < 0.0
        ):
            raise ValueError("feature_acquisition_seconds must be finite and nonnegative")

    def to_dict(self) -> dict[str, object]:
        return {
            "producer_kind": self.producer_kind,
            "resident_representation": self.resident_representation,
            "search_count": self.search_count,
            "query_count": self.query_count,
            "candidate_density_upper_bound": self.candidate_density_upper_bound,
            "expected_query_batches": self.expected_query_batches,
            "module_ready": self.module_ready,
            "index_ready": self.index_ready,
            "predicted_h2d_bytes": self.predicted_h2d_bytes,
            "predicted_d2h_bytes": self.predicted_d2h_bytes,
            "transfer_accounting": self.transfer_accounting.value,
            "calibration_version": self.calibration_version,
            "phase_evidence_digest": self.phase_evidence_digest,
            "predicted_output_bytes": self.predicted_output_bytes,
            "calibration_evidence_digest": self.calibration_evidence_digest,
            "feature_acquisition_seconds": self.feature_acquisition_seconds,
        }


@dataclass(frozen=True)
class ActionBackendCostCalibration:
    """One bounded calibration envelope; never extrapolated outside its domain."""

    backend: str
    calibration_version: str
    producer_kinds: tuple[str, ...]
    resident_representations: tuple[str, ...]
    min_search_count: int
    max_search_count: int
    min_query_count: int
    max_query_count: int
    max_expected_query_batches: int
    min_candidate_density: float
    max_candidate_density: float
    max_state_bytes: int
    max_output_bytes: int
    max_h2d_bytes: int
    max_d2h_bytes: int
    fixed_prepare_seconds: float
    module_prepare_seconds: float
    index_prepare_seconds: float
    per_search_prepare_seconds: float
    fixed_query_seconds: float
    per_query_seconds: float
    per_candidate_seconds: float
    per_state_byte_seconds: float
    per_output_byte_seconds: float
    per_h2d_byte_seconds: float
    per_d2h_byte_seconds: float
    uncertainty_fraction: float
    uncertainty_seconds: float
    source_evidence_digest: str
    transfer_calibration_eligible: bool = True
    uses_transfer_cost_terms: bool = True
    active: bool = True
    mode: ActionCalibrationMode = ActionCalibrationMode.COMPONENT_MODEL
    observed_total_seconds: float | None = None
    exact_expected_query_batches: int | None = None
    exact_module_ready: bool | None = None
    exact_index_ready: bool | None = None
    exact_state_bytes: int | None = None
    exact_output_bytes: int | None = None

    def __post_init__(self) -> None:
        if not self.backend or any(char.isspace() for char in self.backend):
            raise ValueError("backend must be a nonempty identifier")
        if not self.calibration_version:
            raise ValueError("calibration_version is required")
        if not self.producer_kinds or not self.resident_representations:
            raise ValueError("calibration domains must be nonempty")
        for minimum, maximum, name in (
            (self.min_search_count, self.max_search_count, "search_count"),
            (self.min_query_count, self.max_query_count, "query_count"),
        ):
            if minimum < 0 or maximum < minimum:
                raise ValueError(f"invalid {name} calibration envelope")
        for name in (
            "max_expected_query_batches",
            "max_state_bytes",
            "max_output_bytes",
            "max_h2d_bytes",
            "max_d2h_bytes",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.max_expected_query_batches < 1:
            raise ValueError("max_expected_query_batches must be at least one")
        if not (
            0.0
            <= self.min_candidate_density
            <= self.max_candidate_density
            <= 1.0
        ):
            raise ValueError("invalid candidate-density calibration envelope")
        for name in (
            "fixed_prepare_seconds",
            "module_prepare_seconds",
            "index_prepare_seconds",
            "per_search_prepare_seconds",
            "fixed_query_seconds",
            "per_query_seconds",
            "per_candidate_seconds",
            "per_state_byte_seconds",
            "per_output_byte_seconds",
            "per_h2d_byte_seconds",
            "per_d2h_byte_seconds",
            "uncertainty_fraction",
            "uncertainty_seconds",
        ):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        _require_sha256(self.source_evidence_digest, "source_evidence_digest")
        if not isinstance(self.mode, ActionCalibrationMode):
            raise ValueError("mode must be an ActionCalibrationMode")
        if not isinstance(self.uses_transfer_cost_terms, bool):
            raise ValueError("uses_transfer_cost_terms must be a bool")
        if self.mode is ActionCalibrationMode.COMPONENT_MODEL and not self.uses_transfer_cost_terms:
            if self.transfer_calibration_eligible:
                raise ValueError(
                    "a transfer-free total regression must not claim transfer calibration"
                )
            if self.per_h2d_byte_seconds != 0.0 or self.per_d2h_byte_seconds != 0.0:
                raise ValueError(
                    "a transfer-free total regression must have zero transfer coefficients"
                )
        if self.mode is ActionCalibrationMode.EXACT_OBSERVED_TOTAL:
            if (
                self.observed_total_seconds is None
                or not math.isfinite(self.observed_total_seconds)
                or self.observed_total_seconds < 0.0
            ):
                raise ValueError("exact observed calibration requires observed_total_seconds")
            if (
                self.min_search_count != self.max_search_count
                or self.min_query_count != self.max_query_count
                or self.min_candidate_density != self.max_candidate_density
            ):
                raise ValueError("exact observed calibration requires point envelopes")
            if (
                self.exact_expected_query_batches is None
                or self.exact_expected_query_batches < 1
            ):
                raise ValueError(
                    "exact observed calibration requires exact_expected_query_batches"
                )
            for name in (
                "exact_module_ready",
                "exact_index_ready",
                "exact_state_bytes",
                "exact_output_bytes",
            ):
                if getattr(self, name) is None:
                    raise ValueError(f"exact observed calibration requires {name}")
            if not isinstance(self.exact_module_ready, bool) or not isinstance(
                self.exact_index_ready, bool
            ):
                raise ValueError("exact observed readiness values must be bool")
            for name in ("exact_state_bytes", "exact_output_bytes"):
                value = getattr(self, name)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise ValueError(f"{name} must be a nonnegative integer")
            if self.transfer_calibration_eligible:
                raise ValueError(
                    "exact observed total must not claim component transfer calibration"
                )
        elif any(
            value is not None
            for value in (
                self.observed_total_seconds,
                self.exact_expected_query_batches,
                self.exact_module_ready,
                self.exact_index_ready,
                self.exact_state_bytes,
                self.exact_output_bytes,
            )
        ):
            raise ValueError("component calibration cannot carry exact-observed fields")


@dataclass(frozen=True)
class ActionCostPrediction:
    backend: str
    prepare_seconds: float
    per_batch_seconds: float
    total_seconds: float
    lower_seconds: float
    upper_seconds: float
    source_evidence_digest: str
    calibration_mode: ActionCalibrationMode
    component_transfer_calibrated: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "prepare_seconds": self.prepare_seconds,
            "per_batch_seconds": self.per_batch_seconds,
            "total_seconds": self.total_seconds,
            "lower_seconds": self.lower_seconds,
            "upper_seconds": self.upper_seconds,
            "source_evidence_digest": self.source_evidence_digest,
            "calibration_mode": self.calibration_mode.value,
            "component_transfer_calibrated": self.component_transfer_calibrated,
        }


@dataclass(frozen=True)
class ActionBackendCapability:
    backend: str
    placement: ActionPlacementKind
    supported_effect_sets: tuple[frozenset[ActionEffect], ...]
    state_storage: ActionStateStorage
    max_state_bytes: int | None
    max_output_bytes: int | None
    supports_proven_single: bool = True
    supports_keyed_dedup: bool = False
    available: bool = True
    priority: int = 100

    def __post_init__(self) -> None:
        if not self.backend or any(character.isspace() for character in self.backend):
            raise ValueError("backend must be a nonempty identifier")
        for value in (self.max_state_bytes, self.max_output_bytes):
            if value is not None and (not isinstance(value, int) or value < 0):
                raise ValueError("resource limits must be nonnegative integers or None")


@dataclass(frozen=True)
class ActionResourceEstimate:
    state_bytes_per_scope: int
    state_scope_count: int
    total_state_bytes: int
    bounded_output_rows: int
    bounded_output_bytes: int

    def to_dict(self) -> dict[str, int]:
        return {
            "state_bytes_per_scope": self.state_bytes_per_scope,
            "state_scope_count": self.state_scope_count,
            "total_state_bytes": self.total_state_bytes,
            "bounded_output_rows": self.bounded_output_rows,
            "bounded_output_bytes": self.bounded_output_bytes,
        }


@dataclass(frozen=True)
class ActionPlacementCandidate:
    backend: str
    placement: ActionPlacementKind
    legal: bool
    reasons: tuple[str, ...]
    state_bytes_charged: int
    output_bytes_charged: int
    priority: int

    def to_dict(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "placement": self.placement.value,
            "legal": self.legal,
            "reasons": list(self.reasons),
            "state_bytes_charged": self.state_bytes_charged,
            "output_bytes_charged": self.output_bytes_charged,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class ActionPlacementPlan:
    semantic_digest: str
    inferred_effects: tuple[ActionEffect, ...]
    resources: ActionResourceEstimate
    selected_backend: str
    selected_placement: ActionPlacementKind
    selection_reason: str
    candidates: tuple[ActionPlacementCandidate, ...]
    cost_model_status: ActionCostModelStatus = ActionCostModelStatus.NOT_REQUESTED
    cost_features: ActionCostFeatures | None = None
    cost_predictions: tuple[ActionCostPrediction, ...] = ()
    cost_fallback_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": ACTION_PLACEMENT_VERSION,
            "semantic_digest": self.semantic_digest,
            "inferred_effects": [effect.value for effect in self.inferred_effects],
            "resources": self.resources.to_dict(),
            "selected_backend": self.selected_backend,
            "selected_placement": self.selected_placement.value,
            "selection_reason": self.selection_reason,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "cost_model": {
                "contract": ACTION_COST_MODEL_VERSION,
                "status": self.cost_model_status.value,
                "features": (
                    self.cost_features.to_dict()
                    if self.cost_features is not None
                    else None
                ),
                "predictions": [
                    prediction.to_dict() for prediction in self.cost_predictions
                ],
                "fallback_reason": self.cost_fallback_reason,
                "selection_uses_conservative_upper_bound": (
                    self.cost_model_status is ActionCostModelStatus.APPLIED
                ),
            },
            "action_name_used_for_dispatch": False,
            "legality_checked_before_cost": True,
            "fallback_is_explicit": True,
        }


@dataclass(frozen=True)
class ActionPhysicalRefinementCertificate:
    """Evidence binding one executable route to a compiler-visible logical output."""

    action_semantic_digest: str
    logical_output_contract: str
    refinement_scope: str
    producer_kind: str
    backend: str
    executable_identity_digest: str
    differential_evidence_digest: str
    independent_reference_digest: str
    verified_case_count: int
    native_library_identity_digest: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "logical_output_contract",
            "refinement_scope",
            "producer_kind",
            "backend",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value or any(char.isspace() for char in value):
                raise ValueError(f"{name} must be a nonempty identifier")
        for name in (
            "action_semantic_digest",
            "executable_identity_digest",
            "differential_evidence_digest",
            "independent_reference_digest",
        ):
            _require_sha256(getattr(self, name), name)
        if self.native_library_identity_digest is not None:
            _require_sha256(
                self.native_library_identity_digest,
                "native_library_identity_digest",
            )
        if (
            not isinstance(self.verified_case_count, int)
            or isinstance(self.verified_case_count, bool)
            or self.verified_case_count < 1
        ):
            raise ValueError("verified_case_count must be a positive integer")

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": "rtdl.action_physical_refinement_certificate.private_candidate.v1",
            "action_semantic_digest": self.action_semantic_digest,
            "logical_output_contract": self.logical_output_contract,
            "refinement_scope": self.refinement_scope,
            "producer_kind": self.producer_kind,
            "backend": self.backend,
            "executable_identity_digest": self.executable_identity_digest,
            "differential_evidence_digest": self.differential_evidence_digest,
            "independent_reference_digest": self.independent_reference_digest,
            "verified_case_count": self.verified_case_count,
            "native_library_identity_digest": self.native_library_identity_digest,
            "same_action_lowering_claimed": False,
        }


def issue_action_physical_refinement_certificate(
    spec: ActionSpec,
    *,
    logical_output_contract: str,
    refinement_scope: str,
    producer_kind: str,
    backend: str,
    executable_identity_digest: str,
    differential_evidence_digest: str,
    independent_reference_digest: str,
    verified_case_count: int,
    native_library_identity_digest: str | None = None,
) -> ActionPhysicalRefinementCertificate:
    verified = verify_action_spec(spec)
    return ActionPhysicalRefinementCertificate(
        action_semantic_digest=verified.semantic_digest,
        logical_output_contract=logical_output_contract,
        refinement_scope=refinement_scope,
        producer_kind=producer_kind,
        backend=backend,
        executable_identity_digest=executable_identity_digest,
        differential_evidence_digest=differential_evidence_digest,
        independent_reference_digest=independent_reference_digest,
        verified_case_count=verified_case_count,
        native_library_identity_digest=native_library_identity_digest,
    )


@dataclass(frozen=True)
class ActionPhysicalAlternative:
    """One certified route for a shared compiler-visible logical output."""

    producer_kind: str
    capability: ActionBackendCapability
    cost_features: ActionCostFeatures
    cost_calibration: ActionBackendCostCalibration
    executable_identity_digest: str
    refinement_certificate: ActionPhysicalRefinementCertificate

    def __post_init__(self) -> None:
        if not self.producer_kind or any(char.isspace() for char in self.producer_kind):
            raise ValueError("producer_kind must be a nonempty identifier")
        if self.cost_features.producer_kind != self.producer_kind:
            raise ValueError("physical-alternative producer and cost features differ")
        if self.cost_calibration.backend != self.capability.backend:
            raise ValueError("physical-alternative backend and calibration differ")
        _require_sha256(self.executable_identity_digest, "executable_identity_digest")
        certificate = self.refinement_certificate
        if certificate.producer_kind != self.producer_kind:
            raise ValueError("physical-alternative producer and refinement certificate differ")
        if certificate.backend != self.capability.backend:
            raise ValueError("physical-alternative backend and refinement certificate differ")
        if certificate.executable_identity_digest != self.executable_identity_digest:
            raise ValueError("physical-alternative executable identity is uncertified")


@dataclass(frozen=True)
class ActionPhysicalAlternativePlan:
    semantic_digest: str
    selected_backend: str
    selected_producer_kind: str
    selected_placement: ActionPlacementKind
    alternatives: tuple[ActionPlacementPlan, ...]
    logical_output_contract: str
    refinement_certificates: tuple[ActionPhysicalRefinementCertificate, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": "rtdl.action_physical_alternative_plan.private_candidate.v1",
            "semantic_digest": self.semantic_digest,
            "selected_backend": self.selected_backend,
            "selected_producer_kind": self.selected_producer_kind,
            "selected_placement": self.selected_placement.value,
            "alternatives": [plan.to_dict() for plan in self.alternatives],
            "logical_output_contract": self.logical_output_contract,
            "refinement_certificates": [
                certificate.to_dict() for certificate in self.refinement_certificates
            ],
            "selection_reason": "minimum_conservative_cost_across_legal_producers",
            "action_name_used_for_dispatch": False,
            "legality_checked_before_cost": True,
            "same_action_lowering_claimed": False,
            "empirical_refinement_required": True,
        }


@dataclass(frozen=True)
class ActionPlanningIssue:
    code: str
    path: str
    message: str


class ActionPlanningError(ValueError):
    def __init__(self, issue: ActionPlanningIssue) -> None:
        self.issue = issue
        super().__init__(f"Action planning failed: {issue.code}@{issue.path}: {issue.message}")


def plan_action_placement(
    spec: ActionSpec,
    capabilities: tuple[ActionBackendCapability, ...],
    *,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, int] | None = None,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
    discharged_termination_certificates: frozenset[str] = frozenset(),
    producer_kind: str | None = None,
    cost_features: ActionCostFeatures | None = None,
    cost_calibrations: tuple[ActionBackendCostCalibration, ...] = (),
) -> ActionPlacementPlan:
    """Choose among compiler-registered capabilities after legality and resource checks."""

    verified = verify_action_spec(spec)
    if not capabilities:
        _fail("no_backend_capabilities", "capabilities", "at least one backend is required")
    proof_reference = spec.logical_event.proof_reference
    if (
        spec.logical_event.enforcement is DeliveryEnforcement.PROVEN_SINGLE
        and (not proof_reference or proof_reference not in discharged_delivery_proofs)
    ):
        _fail(
            "delivery_proof_not_discharged",
            "logical_event.proof_reference",
            str(proof_reference),
        )
    missing_termination = sorted(
        proof.certificate
        for proof in spec.termination_proofs
        if proof.certificate not in discharged_termination_certificates
    )
    if missing_termination:
        _fail(
            "termination_certificate_not_discharged",
            "termination_proofs",
            ",".join(missing_termination),
        )
    resources = _estimate_resources(spec, extents=extents, parameters=parameters or {})
    effects = frozenset(verified.inferred_effects)
    candidates: list[ActionPlacementCandidate] = []
    for capability in capabilities:
        reasons: list[str] = []
        if not capability.available:
            reasons.append("backend_unavailable")
        if effects not in capability.supported_effect_sets:
            reasons.append("effect_set_not_supported")
        if (
            spec.logical_event.enforcement is DeliveryEnforcement.KEYED_DEDUP
            and not capability.supports_keyed_dedup
        ):
            reasons.append("keyed_dedup_not_supported")
        if (
            spec.logical_event.enforcement is DeliveryEnforcement.PROVEN_SINGLE
            and not capability.supports_proven_single
        ):
            reasons.append("proven_single_delivery_not_supported")
        if spec.logical_event.enforcement is DeliveryEnforcement.REJECT_FUSED and (
            capability.placement is ActionPlacementKind.TRAVERSAL_FUSED
        ):
            reasons.append("delivery_contract_rejects_fusion")
        state_bytes = (
            resources.state_bytes_per_scope
            if capability.state_storage is ActionStateStorage.INLINE_PER_SCOPE
            else resources.total_state_bytes
        )
        if capability.max_state_bytes is not None and state_bytes > capability.max_state_bytes:
            reasons.append("state_resource_limit_exceeded")
        if (
            capability.max_output_bytes is not None
            and resources.bounded_output_bytes > capability.max_output_bytes
        ):
            reasons.append("output_resource_limit_exceeded")
        candidates.append(
            ActionPlacementCandidate(
                backend=capability.backend,
                placement=capability.placement,
                legal=not reasons,
                reasons=tuple(reasons),
                state_bytes_charged=state_bytes,
                output_bytes_charged=resources.bounded_output_bytes,
                priority=capability.priority,
            )
        )
    legal = [candidate for candidate in candidates if candidate.legal]
    if not legal:
        _fail(
            "no_legal_placement",
            "capabilities",
            "; ".join(
                f"{candidate.backend}:{','.join(candidate.reasons)}" for candidate in candidates
            ),
        )
    priority_selected = min(
        legal, key=lambda candidate: (candidate.priority, candidate.backend)
    )
    selected = priority_selected
    cost_model_status = ActionCostModelStatus.NOT_REQUESTED
    cost_predictions: tuple[ActionCostPrediction, ...] = ()
    cost_fallback_reason: str | None = None
    if cost_features is not None:
        if producer_kind is not None and cost_features.producer_kind != producer_kind:
            _fail(
                "cost_feature_producer_mismatch",
                "cost_features.producer_kind",
                f"{cost_features.producer_kind}!={producer_kind}",
            )
        selected_by_cost, predictions, fallback = _select_by_cost(
            legal,
            resources,
            cost_features,
            cost_calibrations,
        )
        cost_predictions = predictions
        if selected_by_cost is None:
            cost_model_status = ActionCostModelStatus.UNAVAILABLE_OR_OUT_OF_DOMAIN
            cost_fallback_reason = fallback
        else:
            selected = selected_by_cost
            cost_model_status = ActionCostModelStatus.APPLIED
    rejected_preferred = [
        candidate
        for candidate in candidates
        if candidate.priority < selected.priority and not candidate.legal
    ]
    if cost_model_status is ActionCostModelStatus.APPLIED:
        reason = (
            "minimum_conservative_exact_observed_cost"
            if all(
                prediction.calibration_mode
                is ActionCalibrationMode.EXACT_OBSERVED_TOTAL
                for prediction in cost_predictions
            )
            else "minimum_conservative_predicted_cost"
        )
    else:
        reason = "lowest_priority_legal_placement"
    if (
        cost_model_status is not ActionCostModelStatus.APPLIED
        and rejected_preferred
    ):
        reason = "fallback_after_" + "+".join(
            sorted({reason for item in rejected_preferred for reason in item.reasons})
        )
    if cost_model_status is ActionCostModelStatus.UNAVAILABLE_OR_OUT_OF_DOMAIN:
        reason = "cost_model_fallback_to_" + reason
    return ActionPlacementPlan(
        semantic_digest=verified.semantic_digest,
        inferred_effects=verified.inferred_effects,
        resources=resources,
        selected_backend=selected.backend,
        selected_placement=selected.placement,
        selection_reason=reason,
        candidates=tuple(candidates),
        cost_model_status=cost_model_status,
        cost_features=cost_features,
        cost_predictions=cost_predictions,
        cost_fallback_reason=cost_fallback_reason,
    )


def plan_action_physical_alternatives(
    spec: ActionSpec,
    alternatives: tuple[ActionPhysicalAlternative, ...],
    *,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, int] | None = None,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
    discharged_termination_certificates: frozenset[str] = frozenset(),
) -> ActionPhysicalAlternativePlan:
    """Cost distinct legal producers only after each one passes normal planning."""

    if not alternatives:
        _fail(
            "no_physical_alternatives",
            "alternatives",
            "at least one physical alternative is required",
        )
    backend_names = [alternative.capability.backend for alternative in alternatives]
    if len(set(backend_names)) != len(backend_names):
        _fail(
            "duplicate_physical_alternative_backend",
            "alternatives",
            ",".join(backend_names),
        )
    verified = verify_action_spec(spec)
    logical_output_contracts = {
        alternative.refinement_certificate.logical_output_contract
        for alternative in alternatives
    }
    refinement_scopes = {
        alternative.refinement_certificate.refinement_scope
        for alternative in alternatives
    }
    independent_references = {
        alternative.refinement_certificate.independent_reference_digest
        for alternative in alternatives
    }
    if len(logical_output_contracts) != 1:
        _fail(
            "physical_alternative_output_contract_mismatch",
            "alternatives",
            ",".join(sorted(logical_output_contracts)),
        )
    if len(refinement_scopes) != 1 or len(independent_references) != 1:
        _fail(
            "physical_alternative_refinement_evidence_mismatch",
            "alternatives",
            "all alternatives must share one refinement scope and independent reference",
        )
    plans: list[ActionPlacementPlan] = []
    for index, alternative in enumerate(alternatives):
        certificate = alternative.refinement_certificate
        if certificate.action_semantic_digest != verified.semantic_digest:
            _fail(
                "physical_alternative_action_digest_mismatch",
                f"alternatives[{index}].refinement_certificate",
                certificate.action_semantic_digest,
            )
        if certificate.differential_evidence_digest != alternative.cost_calibration.source_evidence_digest:
            _fail(
                "physical_alternative_evidence_digest_mismatch",
                f"alternatives[{index}].refinement_certificate",
                "refinement and calibration evidence differ",
            )
        plan = plan_action_placement(
            spec,
            (alternative.capability,),
            extents=extents,
            parameters=parameters,
            discharged_delivery_proofs=discharged_delivery_proofs,
            discharged_termination_certificates=discharged_termination_certificates,
            producer_kind=alternative.producer_kind,
            cost_features=alternative.cost_features,
            cost_calibrations=(alternative.cost_calibration,),
        )
        if plan.cost_model_status is not ActionCostModelStatus.APPLIED:
            _fail(
                "physical_alternative_cost_unavailable",
                f"alternatives[{index}]",
                str(plan.cost_fallback_reason),
            )
        if len(plan.cost_predictions) != 1:
            _fail(
                "physical_alternative_prediction_count",
                f"alternatives[{index}]",
                str(len(plan.cost_predictions)),
            )
        plans.append(plan)
    semantic_digests = {plan.semantic_digest for plan in plans}
    if len(semantic_digests) != 1:
        _fail(
            "physical_alternative_semantic_mismatch",
            "alternatives",
            ",".join(sorted(semantic_digests)),
        )
    selected = min(
        plans,
        key=lambda plan: (
            plan.cost_predictions[0].upper_seconds,
            next(
                alternative.capability.priority
                for alternative in alternatives
                if alternative.capability.backend == plan.selected_backend
            ),
            plan.selected_backend,
        ),
    )
    producer_kind = next(
        alternative.producer_kind
        for alternative in alternatives
        if alternative.capability.backend == selected.selected_backend
    )
    return ActionPhysicalAlternativePlan(
        semantic_digest=selected.semantic_digest,
        selected_backend=selected.selected_backend,
        selected_producer_kind=producer_kind,
        selected_placement=selected.selected_placement,
        alternatives=tuple(plans),
        logical_output_contract=next(iter(logical_output_contracts)),
        refinement_certificates=tuple(
            alternative.refinement_certificate for alternative in alternatives
        ),
    )


def _select_by_cost(
    legal: list[ActionPlacementCandidate],
    resources: ActionResourceEstimate,
    features: ActionCostFeatures,
    calibrations: tuple[ActionBackendCostCalibration, ...],
) -> tuple[
    ActionPlacementCandidate | None,
    tuple[ActionCostPrediction, ...],
    str | None,
]:
    by_backend: dict[str, list[ActionBackendCostCalibration]] = {}
    for calibration in calibrations:
        by_backend.setdefault(calibration.backend, []).append(calibration)
    resolved: list[tuple[ActionPlacementCandidate, ActionBackendCostCalibration]] = []
    for candidate in legal:
        matches = by_backend.get(candidate.backend, [])
        if len(matches) != 1:
            reason = (
                "missing_calibration"
                if not matches
                else "ambiguous_calibration"
            )
            return None, (), f"{candidate.backend}:{reason}"
        calibration = matches[0]
        ineligible = _calibration_ineligibility(
            calibration,
            candidate,
            resources,
            features,
        )
        if ineligible is not None:
            return None, (), f"{candidate.backend}:{ineligible}"
        resolved.append((candidate, calibration))
    predictions = tuple(
        _predict_cost(candidate, resources, features, calibration)
        for candidate, calibration in resolved
    )
    selected_prediction = min(
        predictions,
        key=lambda prediction: (
            prediction.upper_seconds,
            next(
                candidate.priority
                for candidate in legal
                if candidate.backend == prediction.backend
            ),
            prediction.backend,
        ),
    )
    selected = next(
        candidate
        for candidate in legal
        if candidate.backend == selected_prediction.backend
    )
    return selected, predictions, None


def _calibration_ineligibility(
    calibration: ActionBackendCostCalibration,
    candidate: ActionPlacementCandidate,
    resources: ActionResourceEstimate,
    features: ActionCostFeatures,
) -> str | None:
    if not calibration.active:
        return "calibration_inactive"
    if calibration.mode is ActionCalibrationMode.COMPONENT_MODEL:
        if calibration.uses_transfer_cost_terms:
            if not calibration.transfer_calibration_eligible:
                return "transfer_calibration_ineligible"
            if features.transfer_accounting is ActionTransferAccounting.FOLDED_INELIGIBLE:
                return "transfer_or_synchronization_phase_folded_ineligible"
            if features.predicted_h2d_bytes is None or features.predicted_d2h_bytes is None:
                return "transfer_byte_estimate_unavailable"
    if calibration.calibration_version != features.calibration_version:
        return "calibration_version_mismatch"
    if features.calibration_evidence_digest is None:
        return "calibration_evidence_unbound"
    if features.calibration_evidence_digest != calibration.source_evidence_digest:
        return "calibration_evidence_digest_mismatch"
    if features.producer_kind not in calibration.producer_kinds:
        return "producer_kind_out_of_domain"
    if features.resident_representation not in calibration.resident_representations:
        return "resident_representation_out_of_domain"
    if not (
        calibration.min_search_count
        <= features.search_count
        <= calibration.max_search_count
    ):
        return "search_count_out_of_domain"
    if not (
        calibration.min_query_count
        <= features.query_count
        <= calibration.max_query_count
    ):
        return "query_count_out_of_domain"
    if features.expected_query_batches > calibration.max_expected_query_batches:
        return "query_batch_count_out_of_domain"
    if (
        calibration.mode is ActionCalibrationMode.EXACT_OBSERVED_TOTAL
        and features.expected_query_batches
        != calibration.exact_expected_query_batches
    ):
        return "query_batch_count_not_exact_observed_point"
    if calibration.mode is ActionCalibrationMode.EXACT_OBSERVED_TOTAL:
        if features.module_ready is not calibration.exact_module_ready:
            return "module_readiness_not_exact_observed_point"
        if features.index_ready is not calibration.exact_index_ready:
            return "index_readiness_not_exact_observed_point"
        if candidate.state_bytes_charged != calibration.exact_state_bytes:
            return "state_bytes_not_exact_observed_point"
        if candidate.output_bytes_charged != calibration.exact_output_bytes:
            return "output_bytes_not_exact_observed_point"
    if not (
        calibration.min_candidate_density
        <= features.candidate_density_upper_bound
        <= calibration.max_candidate_density
    ):
        return "candidate_density_out_of_domain"
    if candidate.state_bytes_charged > calibration.max_state_bytes:
        return "state_bytes_out_of_domain"
    if candidate.output_bytes_charged > calibration.max_output_bytes:
        return "output_bytes_out_of_domain"
    if (
        features.predicted_output_bytes is not None
        and features.predicted_output_bytes > calibration.max_output_bytes
    ):
        return "predicted_output_bytes_out_of_domain"
    if (
        features.predicted_h2d_bytes is not None
        and features.predicted_h2d_bytes > calibration.max_h2d_bytes
    ):
        return "h2d_bytes_out_of_domain"
    if (
        features.predicted_d2h_bytes is not None
        and features.predicted_d2h_bytes > calibration.max_d2h_bytes
    ):
        return "d2h_bytes_out_of_domain"
    return None


def _predict_cost(
    candidate: ActionPlacementCandidate,
    resources: ActionResourceEstimate,
    features: ActionCostFeatures,
    calibration: ActionBackendCostCalibration,
) -> ActionCostPrediction:
    del resources
    if calibration.mode is ActionCalibrationMode.EXACT_OBSERVED_TOTAL:
        total = float(calibration.observed_total_seconds) + float(
            features.feature_acquisition_seconds
        )
        uncertainty = (
            calibration.uncertainty_seconds
            + calibration.uncertainty_fraction * total
        )
        return ActionCostPrediction(
            backend=candidate.backend,
            prepare_seconds=0.0,
            per_batch_seconds=total / features.expected_query_batches,
            total_seconds=total,
            lower_seconds=max(0.0, total - uncertainty),
            upper_seconds=total + uncertainty,
            source_evidence_digest=calibration.source_evidence_digest,
            calibration_mode=calibration.mode,
            component_transfer_calibrated=False,
        )
    prepare = (
        features.feature_acquisition_seconds
        + calibration.fixed_prepare_seconds
        + (0.0 if features.module_ready else calibration.module_prepare_seconds)
        + (0.0 if features.index_ready else calibration.index_prepare_seconds)
        + (
            0.0
            if features.index_ready
            else calibration.per_search_prepare_seconds * features.search_count
        )
    )
    candidate_upper_bound = (
        float(features.search_count)
        * float(features.query_count)
        * float(features.candidate_density_upper_bound)
    )
    transfer_cost = 0.0
    if calibration.uses_transfer_cost_terms:
        transfer_cost = (
            calibration.per_h2d_byte_seconds * int(features.predicted_h2d_bytes)
            + calibration.per_d2h_byte_seconds * int(features.predicted_d2h_bytes)
        )
    per_batch = (
        calibration.fixed_query_seconds
        + calibration.per_query_seconds * features.query_count
        + calibration.per_candidate_seconds * candidate_upper_bound
        + calibration.per_state_byte_seconds * candidate.state_bytes_charged
        + calibration.per_output_byte_seconds
        * (
            candidate.output_bytes_charged
            if features.predicted_output_bytes is None
            else features.predicted_output_bytes
        )
        + transfer_cost
    )
    total = prepare + features.expected_query_batches * per_batch
    uncertainty = (
        calibration.uncertainty_seconds
        + calibration.uncertainty_fraction * total
    )
    return ActionCostPrediction(
        backend=candidate.backend,
        prepare_seconds=prepare,
        per_batch_seconds=per_batch,
        total_seconds=total,
        lower_seconds=max(0.0, total - uncertainty),
        upper_seconds=total + uncertainty,
        source_evidence_digest=calibration.source_evidence_digest,
        calibration_mode=calibration.mode,
        component_transfer_calibrated=calibration.uses_transfer_cost_terms,
    )


def _estimate_resources(
    spec: ActionSpec,
    *,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, int],
) -> ActionResourceEstimate:
    state_bytes_per_scope = sum(_value_width_bytes(state.value_type) for state in spec.states)
    normalized_extents = {
        key if isinstance(key, ExtentKind) else ExtentKind(key): int(value)
        for key, value in extents.items()
    }
    scope_counts: list[int] = []
    for state in spec.states:
        extent = (
            ExtentKind.QUERY_COUNT
            if state.scope is StateScope.PER_QUERY
            else ExtentKind.PARTITION_COUNT
        )
        if extent not in normalized_extents:
            _fail("missing_state_scope_extent", f"extents.{extent.value}", state.name)
        count = normalized_extents[extent]
        if count < 0:
            _fail("negative_extent", f"extents.{extent.value}", str(count))
        scope_counts.append(count)
    state_scope_count = max(scope_counts, default=0)
    total_state_bytes = sum(
        _value_width_bytes(state.value_type)
        * normalized_extents[
            ExtentKind.QUERY_COUNT
            if state.scope is StateScope.PER_QUERY
            else ExtentKind.PARTITION_COUNT
        ]
        for state in spec.states
    )
    output_rows = 0
    output_bytes = 0
    for emit in spec.emits:
        try:
            capacity = evaluate_capacity(
                emit.capacity,
                extents=normalized_extents,
                parameters=parameters,
                allocator_limit=(1 << 63) - 1,
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            _fail("capacity_evaluation_failed", f"emits.{emit.name}.capacity", str(exc))
        row_width = sum(_value_width_bytes(field.value_type) for field in emit.record_type.fields)
        output_rows += capacity
        output_bytes += capacity * row_width
    return ActionResourceEstimate(
        state_bytes_per_scope=state_bytes_per_scope,
        state_scope_count=state_scope_count,
        total_state_bytes=total_state_bytes,
        bounded_output_rows=output_rows,
        bounded_output_bytes=output_bytes,
    )


def _value_width_bytes(value_type) -> int:
    if isinstance(value_type, ActionTupleType):
        return sum(_value_width_bytes(item) for item in value_type.items)
    if not isinstance(value_type, ActionScalarType):
        _fail("unsupported_value_type", "resource_estimate", type(value_type).__name__)
    return {
        ActionScalarKind.BOOL: 1,
        ActionScalarKind.I32: 4,
        ActionScalarKind.I64: 8,
        ActionScalarKind.U32: 4,
        ActionScalarKind.U64: 8,
        ActionScalarKind.F32: 4,
        ActionScalarKind.F64: 8,
    }[value_type.kind]


def _require_sha256(value: str, name: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value.lower())
    ):
        raise ValueError(f"{name} must be a 64-character SHA-256 hex digest")


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise ActionPlanningError(ActionPlanningIssue(code, path, message))
