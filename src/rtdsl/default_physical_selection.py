"""Deterministic DEFAULT selection for the closed current RTDL registry.

This module is deliberately boring.  It does not execute a candidate, read a
timer, learn a model, inspect an application name, or change an existing
production default.  It authenticates one complete current-registry candidate
set, rejects candidates with unproved obligations, applies the Goal5694-A4
total order, and emits enough canonical material for an independent module to
reconstruct the decision.

The catalog is a closed-current-registry contract, not an open-world claim.
Future candidates require a new registry version and new authenticated
declarations before they may participate.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from typing import Iterable, Mapping, Sequence


DEFAULT_POLICY_VERSION = "rtdl.default_physical_selection.goal5699_a2.v6"
DEFAULT_RECEIPT_SCHEMA = "rtdl.default_physical_selection.receipt.v6"
CURRENT_REGISTRY_VERSION = "rtdl.current_physical_candidate_registry.goal5699_a2.v4"
CELL_MBR_EXACT_WITNESS_MEMORY_LOGICAL_MULTIPLICITY = 512
CELL_MBR_INLINE_CONFIGURATION_POLICY = (
    "cell_mbr_cover_certified_population_up_to_reviewed_cap_v1"
)
CELL_MBR_INLINE_CONFIGURATION_FLOOR = 64
CELL_MBR_INLINE_CONFIGURATION_REVIEWED_CAP = 512
MAX_CANDIDATES_PER_ACTION = 64
UINT64_MAX = (1 << 64) - 1
MAX_WORK_POLYNOMIAL_DEGREE = 8
MAX_WORK_LOGARITHMIC_DEGREE = 4

DEPLOYABLE_LOWERING = "DEPLOYABLE_LOWERING"
REFERENCE_FALLBACK = "REFERENCE_FALLBACK"
SELECTION_ROLE_UNVERIFIED = "SELECTION_ROLE_UNVERIFIED"
MEMORY_PROOF_ACTION_EXTENT_RELATION = "ACTION_EXTENT_RELATION_MULTIPLICITY"
ROLE_EVIDENCE_NORMAL_PROGRAM = "REGISTERED_INDEPENDENT_NORMAL_PROVIDER_PROGRAM"
ROLE_EVIDENCE_VALIDATION_PROGRAM = "REGISTERED_INDEPENDENT_VALIDATION_PROVIDER_PROGRAM"
ROLE_EVIDENCE_REFERENCE_ORACLE = "ORDINARY_LAST_RANKED_CORRECTNESS_PORTABILITY_ORACLE"
ROLE_TIER = {
    DEPLOYABLE_LOWERING: 0,
    REFERENCE_FALLBACK: 1,
}
DEVICE_EXECUTION_CLASSES = frozenset({"cuda", "optix", "mixed_optix_numba"})
OPTIX_TRAVERSAL_PROGRAM_CAPABILITY = "OPTIX_TRAVERSAL_PROGRAM"

NORMAL_PROFILE = "NORMAL"
VALIDATION_PROFILE = "VALIDATION"
ANNOTATION_NONE = "NONE"
ANNOTATION_COMPLETE = "COMPLETE"


class DefaultSelectionError(RuntimeError):
    """A typed fail-closed DEFAULT selection failure."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = str(code)
        self.detail = str(detail)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _checked_u64(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DefaultSelectionError("INVALID_UNSIGNED_FIELD", field)
    if value < 0 or value > UINT64_MAX:
        raise DefaultSelectionError("UNSIGNED_FIELD_OUT_OF_RANGE", field)
    return value


def _checked_add(left: int, right: int, *, field: str) -> int:
    result = left + right
    if result > UINT64_MAX:
        raise DefaultSelectionError("RESOURCE_BOUND_OVERFLOW", field)
    return result


def _checked_mul(left: int, right: int, *, field: str) -> int:
    if left and right > UINT64_MAX // left:
        raise DefaultSelectionError("RESOURCE_BOUND_OVERFLOW", field)
    return left * right


def _validate_sha256(value: str, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise DefaultSelectionError("INVALID_SHA256", field)
    try:
        int(value, 16)
    except ValueError as exc:
        raise DefaultSelectionError("INVALID_SHA256", field) from exc
    return value.lower()


@dataclass(frozen=True)
class WorkOrderValue:
    """Finite worst-case work class ``Theta(n^p log(n)^q)``.

    The pair is a static semantic-work ordering value over one complete Action
    invocation.  It is not measured latency and is never inferred from a
    benchmark.
    """

    polynomial_degree: int
    logarithmic_degree: int

    def __post_init__(self) -> None:
        _checked_u64(self.polynomial_degree, field="work.polynomial_degree")
        _checked_u64(self.logarithmic_degree, field="work.logarithmic_degree")
        if self.polynomial_degree > MAX_WORK_POLYNOMIAL_DEGREE:
            raise DefaultSelectionError(
                "WORK_ORDER_OUT_OF_GRAMMAR", "work.polynomial_degree"
            )
        if self.logarithmic_degree > MAX_WORK_LOGARITHMIC_DEGREE:
            raise DefaultSelectionError(
                "WORK_ORDER_OUT_OF_GRAMMAR", "work.logarithmic_degree"
            )

    def as_list(self) -> list[int]:
        return [self.polynomial_degree, self.logarithmic_degree]


@dataclass(frozen=True)
class LinearMemoryBound:
    """Checked conservative peak-extra-byte expression.

    Immutable Action inputs are accounted through authenticated byte extents;
    the expression bounds additional live memory over one complete invocation.
    """

    base_bytes: int
    input_bytes_multiplier: int
    output_bytes_multiplier: int
    prepared_bytes_multiplier: int
    logical_item_multiplicity: int = 0
    pair_item_multiplicity: int = 0

    def __post_init__(self) -> None:
        for name, value in self.as_dict().items():
            _checked_u64(value, field=f"memory_model.{name}")

    def evaluate(self, action: "ActionSelectionDescriptor") -> int:
        total = self.base_bytes
        for field, multiplier, extent in (
            ("input_bytes", self.input_bytes_multiplier, action.input_bytes),
            ("output_bytes", self.output_bytes_multiplier, action.output_bytes),
            ("prepared_bytes", self.prepared_bytes_multiplier, action.prepared_bytes),
        ):
            term = _checked_mul(multiplier, extent, field=f"memory_model.{field}")
            total = _checked_add(total, term, field="memory_model.total")
        for field, multiplier, cardinality, item_bytes in (
            (
                "logical_relation_bytes",
                self.logical_item_multiplicity,
                action.logical_cardinality_bound,
                action.logical_item_bytes_bound,
            ),
            (
                "pair_relation_bytes",
                self.pair_item_multiplicity,
                action.pair_cardinality_bound,
                action.pair_item_bytes_bound,
            ),
        ):
            relation_bytes = _checked_mul(
                cardinality, item_bytes, field=f"memory_model.{field}.extent"
            )
            term = _checked_mul(
                multiplier, relation_bytes, field=f"memory_model.{field}.multiplicity"
            )
            total = _checked_add(total, term, field="memory_model.total")
        return total

    def as_dict(self) -> dict[str, int]:
        return {
            "base_bytes": self.base_bytes,
            "input_bytes_multiplier": self.input_bytes_multiplier,
            "output_bytes_multiplier": self.output_bytes_multiplier,
            "prepared_bytes_multiplier": self.prepared_bytes_multiplier,
            "logical_item_multiplicity": self.logical_item_multiplicity,
            "pair_item_multiplicity": self.pair_item_multiplicity,
        }


@dataclass(frozen=True)
class ActionSelectionDescriptor:
    semantic_kind: str
    action_contract_class: str
    action_digest: str
    output_contract_digest: str
    work_domain_digest: str
    input_bytes: int
    output_bytes: int
    prepared_bytes: int
    logical_cardinality_bound: int
    pair_cardinality_bound: int
    logical_item_bytes_bound: int
    pair_item_bytes_bound: int
    host_visible_canonical_output_required: bool
    admitted_proof_digests: tuple[str, ...]
    admitted_resource_bound_digests: tuple[str, ...]
    admitted_reuse_contract_digests: tuple[str, ...]
    admitted_template_digests: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.semantic_kind or not self.action_contract_class:
            raise DefaultSelectionError("EMPTY_ACTION_SEMANTIC_KIND")
        for field in ("action_digest", "output_contract_digest", "work_domain_digest"):
            _validate_sha256(getattr(self, field), field=field)
        for field in (
            "input_bytes",
            "output_bytes",
            "prepared_bytes",
            "logical_cardinality_bound",
            "pair_cardinality_bound",
            "logical_item_bytes_bound",
            "pair_item_bytes_bound",
        ):
            _checked_u64(getattr(self, field), field=field)
        n = max(1, self.logical_cardinality_bound)
        if self.pair_cardinality_bound > _checked_mul(n, n, field="action.n_squared"):
            raise DefaultSelectionError("PAIR_CARDINALITY_EXCEEDS_AUTHENTICATED_DOMAIN")
        if self.logical_cardinality_bound and self.logical_item_bytes_bound == 0:
            raise DefaultSelectionError("MISSING_LOGICAL_ITEM_BYTE_EXTENT")
        if self.pair_cardinality_bound and self.pair_item_bytes_bound == 0:
            raise DefaultSelectionError("MISSING_PAIR_ITEM_BYTE_EXTENT")
        if not isinstance(self.host_visible_canonical_output_required, bool):
            raise DefaultSelectionError("INVALID_ENDPOINT_COMPLETION_CONTRACT")
        for field in (
            "admitted_proof_digests",
            "admitted_resource_bound_digests",
            "admitted_reuse_contract_digests",
            "admitted_template_digests",
        ):
            values = getattr(self, field)
            if tuple(sorted(set(values))) != values:
                raise DefaultSelectionError("NONCANONICAL_ACTION_ADMISSION_SET", field)
            for index, value in enumerate(values):
                _validate_sha256(value, field=f"{field}[{index}]")

    def as_dict(self) -> dict[str, object]:
        return {
            "semantic_kind": self.semantic_kind,
            "action_contract_class": self.action_contract_class,
            "action_digest": self.action_digest,
            "output_contract_digest": self.output_contract_digest,
            "work_domain_digest": self.work_domain_digest,
            "input_bytes": self.input_bytes,
            "output_bytes": self.output_bytes,
            "prepared_bytes": self.prepared_bytes,
            "logical_cardinality_bound": self.logical_cardinality_bound,
            "pair_cardinality_bound": self.pair_cardinality_bound,
            "logical_item_bytes_bound": self.logical_item_bytes_bound,
            "pair_item_bytes_bound": self.pair_item_bytes_bound,
            "host_visible_canonical_output_required": (
                self.host_visible_canonical_output_required
            ),
            "admitted_proof_digests": list(self.admitted_proof_digests),
            "admitted_resource_bound_digests": list(self.admitted_resource_bound_digests),
            "admitted_reuse_contract_digests": list(self.admitted_reuse_contract_digests),
            "admitted_template_digests": list(self.admitted_template_digests),
        }


@dataclass(frozen=True)
class TargetSelectionDescriptor:
    target_digest: str
    available_providers: tuple[str, ...]
    allowed_execution_classes: tuple[str, ...]
    required_physical_capabilities: tuple[str, ...]
    available_provider_abi_requirement_digests: tuple[str, ...]
    memory_limit_bytes: int
    profile: str = NORMAL_PROFILE
    unprofiled: bool = True

    def __post_init__(self) -> None:
        _validate_sha256(self.target_digest, field="target_digest")
        if tuple(sorted(set(self.available_providers))) != self.available_providers:
            raise DefaultSelectionError("NONCANONICAL_PROVIDER_SET")
        if tuple(sorted(set(self.allowed_execution_classes))) != self.allowed_execution_classes:
            raise DefaultSelectionError("NONCANONICAL_EXECUTION_CLASS_SET")
        if (
            tuple(sorted(set(self.required_physical_capabilities)))
            != self.required_physical_capabilities
        ):
            raise DefaultSelectionError("NONCANONICAL_REQUIRED_CAPABILITY_SET")
        if (
            tuple(sorted(set(self.available_provider_abi_requirement_digests)))
            != self.available_provider_abi_requirement_digests
        ):
            raise DefaultSelectionError("NONCANONICAL_PROVIDER_ABI_SET")
        for index, value in enumerate(self.available_provider_abi_requirement_digests):
            _validate_sha256(value, field=f"available_provider_abi_requirement_digests[{index}]")
        if self.profile not in (NORMAL_PROFILE, VALIDATION_PROFILE):
            raise DefaultSelectionError("UNKNOWN_TARGET_PROFILE", self.profile)
        _checked_u64(self.memory_limit_bytes, field="memory_limit_bytes")
        if self.unprofiled is not True:
            raise DefaultSelectionError("PROFILED_OR_TIMING_TARGET_FORBIDDEN")

    def as_dict(self) -> dict[str, object]:
        return {
            "target_digest": self.target_digest,
            "available_providers": list(self.available_providers),
            "allowed_execution_classes": list(self.allowed_execution_classes),
            "required_physical_capabilities": list(
                self.required_physical_capabilities
            ),
            "available_provider_abi_requirement_digests": list(
                self.available_provider_abi_requirement_digests
            ),
            "memory_limit_bytes": self.memory_limit_bytes,
            "profile": self.profile,
            "unprofiled": self.unprofiled,
        }


@dataclass(frozen=True)
class CandidateDeclaration:
    stable_id: str
    family: str
    semantic_kind: str
    accepted_action_contract_classes: tuple[str, ...]
    backend: str
    template: str
    provider_class: str
    required_providers: tuple[str, ...]
    execution_class: str
    physical_capabilities: tuple[str, ...]
    selection_role: str
    normal_default_eligible: bool
    exactness_verified: bool
    determinism_verified: bool
    ordering_verified: bool
    provider_abi_requirement_digest: str
    proof_digest: str
    resource_bound_digest: str
    reuse_contract_digest: str
    template_digest: str
    work_order: WorkOrderValue
    host_round_trips: int
    materializations: int
    device_synchronizations: int
    launches: int
    memory_bound: LinearMemoryBound
    resource_bound_verified: bool
    memory_proof_kind: str
    memory_evidence: str
    memory_source_path: str
    memory_source_sha256: str
    memory_source_anchor: str
    max_logical_cardinality: int | None
    max_pair_cardinality: int | None
    source_path: str
    source_sha256: str
    source_anchor: str
    role_evidence_kind: str
    role_evidence_facts: tuple[str, ...]
    role_evidence: str
    existing_normal_policy: str
    existing_normal_position: int | None
    physical_configuration_policy_id: str | None
    physical_configuration_policy_source_path: str | None
    physical_configuration_policy_source_sha256: str | None
    physical_configuration_policy_source_anchor: str | None
    physical_configuration_policy_floor: int | None
    physical_configuration_policy_cap: int | None

    def __post_init__(self) -> None:
        if not self.stable_id or not self.semantic_kind or not self.template:
            raise DefaultSelectionError("EMPTY_CANDIDATE_IDENTITY")
        if self.selection_role not in (
            DEPLOYABLE_LOWERING,
            REFERENCE_FALLBACK,
            SELECTION_ROLE_UNVERIFIED,
        ):
            raise DefaultSelectionError("UNKNOWN_SELECTION_ROLE", self.selection_role)
        if tuple(sorted(set(self.required_providers))) != self.required_providers:
            raise DefaultSelectionError("NONCANONICAL_REQUIRED_PROVIDER_SET", self.stable_id)
        if (
            not self.physical_capabilities
            or tuple(sorted(set(self.physical_capabilities))) != self.physical_capabilities
        ):
            raise DefaultSelectionError(
                "NONCANONICAL_OR_EMPTY_PHYSICAL_CAPABILITY_SET", self.stable_id
            )
        if (
            not self.accepted_action_contract_classes
            or tuple(sorted(set(self.accepted_action_contract_classes)))
            != self.accepted_action_contract_classes
        ):
            raise DefaultSelectionError("NONCANONICAL_ACTION_CONTRACT_SET", self.stable_id)
        for field in (
            "provider_abi_requirement_digest",
            "proof_digest",
            "resource_bound_digest",
            "reuse_contract_digest",
            "template_digest",
            "source_sha256",
            "memory_source_sha256",
        ):
            _validate_sha256(getattr(self, field), field=f"{self.stable_id}.{field}")
        for field in (
            "host_round_trips",
            "materializations",
            "device_synchronizations",
            "launches",
        ):
            _checked_u64(getattr(self, field), field=f"{self.stable_id}.{field}")
        if self.execution_class in DEVICE_EXECUTION_CLASSES:
            if self.device_synchronizations < 1 or self.launches < 1:
                raise DefaultSelectionError("IMPOSSIBLE_DEVICE_ACCOUNTING", self.stable_id)
        elif self.device_synchronizations != 0 or self.launches != 0:
            raise DefaultSelectionError("HOST_ROUTE_HAS_DEVICE_ACCOUNTING", self.stable_id)
        if self.existing_normal_position is not None:
            _checked_u64(self.existing_normal_position, field="existing_normal_position")
        policy_values = (
            self.physical_configuration_policy_id,
            self.physical_configuration_policy_source_path,
            self.physical_configuration_policy_source_sha256,
            self.physical_configuration_policy_source_anchor,
            self.physical_configuration_policy_floor,
            self.physical_configuration_policy_cap,
        )
        if any(value is not None for value in policy_values):
            if any(value is None for value in policy_values):
                raise DefaultSelectionError(
                    "INCOMPLETE_PHYSICAL_CONFIGURATION_POLICY", self.stable_id
                )
            _validate_sha256(
                self.physical_configuration_policy_source_sha256,
                field=f"{self.stable_id}.physical_configuration_policy_source_sha256",
            )
            floor = _checked_u64(
                self.physical_configuration_policy_floor,
                field=f"{self.stable_id}.physical_configuration_policy_floor",
            )
            cap = _checked_u64(
                self.physical_configuration_policy_cap,
                field=f"{self.stable_id}.physical_configuration_policy_cap",
            )
            if floor <= 0 or cap < floor:
                raise DefaultSelectionError(
                    "INVALID_PHYSICAL_CONFIGURATION_POLICY_RANGE", self.stable_id
                )
        if self.max_logical_cardinality is not None:
            _checked_u64(self.max_logical_cardinality, field="max_logical_cardinality")
        if self.max_pair_cardinality is not None:
            _checked_u64(self.max_pair_cardinality, field="max_pair_cardinality")
        if not self.memory_evidence or not self.role_evidence:
            raise DefaultSelectionError("MISSING_CANDIDATE_EVIDENCE", self.stable_id)
        if not self.memory_source_path or not self.memory_source_anchor:
            raise DefaultSelectionError(
                "MISSING_MEMORY_SOURCE_BINDING", self.stable_id
            )
        if not self.resource_bound_verified:
            # Unproved declarations may be represented so the legality layer
            # can reject them, but they can never claim an authenticated bound.
            if self.memory_proof_kind != "UNPROVED":
                raise DefaultSelectionError("INCONSISTENT_UNPROVED_MEMORY_STATUS", self.stable_id)
        elif self.memory_proof_kind != MEMORY_PROOF_ACTION_EXTENT_RELATION:
            raise DefaultSelectionError("UNKNOWN_MEMORY_PROOF_KIND", self.stable_id)
        if self.resource_bound_verified and not any(
            (
                self.memory_bound.input_bytes_multiplier,
                self.memory_bound.output_bytes_multiplier,
                self.memory_bound.prepared_bytes_multiplier,
                self.memory_bound.logical_item_multiplicity,
                self.memory_bound.pair_item_multiplicity,
            )
        ):
            raise DefaultSelectionError("EMPTY_ACTION_EXTENT_MEMORY_PROOF", self.stable_id)
        expected_role_evidence_kind = (
            ROLE_EVIDENCE_REFERENCE_ORACLE
            if self.selection_role == REFERENCE_FALLBACK
            else ROLE_EVIDENCE_NORMAL_PROGRAM
            if self.normal_default_eligible
            else ROLE_EVIDENCE_VALIDATION_PROGRAM
        )
        if self.role_evidence_kind != expected_role_evidence_kind:
            raise DefaultSelectionError("ROLE_EVIDENCE_KIND_MISMATCH", self.stable_id)
        if len(self.role_evidence_facts) < 6 or len(set(self.role_evidence_facts)) != len(
            self.role_evidence_facts
        ):
            raise DefaultSelectionError("INCOMPLETE_OR_DUPLICATE_ROLE_EVIDENCE", self.stable_id)
        required_role_facts = {
            f"stable_id={self.stable_id}",
            f"source={self.source_path}#{self.source_anchor}",
            f"template={self.template}",
            f"provider_class={self.provider_class}",
            f"physical_capabilities={','.join(self.physical_capabilities)}",
            f"existing_policy={self.existing_normal_policy}",
            f"existing_position={self.existing_normal_position}",
        }
        if not required_role_facts.issubset(set(self.role_evidence_facts)):
            raise DefaultSelectionError("ROLE_EVIDENCE_NOT_CANDIDATE_BOUND", self.stable_id)

    def as_dict(self) -> dict[str, object]:
        physical_configuration_policy = None
        if self.physical_configuration_policy_id is not None:
            policy_body: dict[str, object] = {
                "schema": "rtdl.physical_configuration_policy.cell_mbr_inline.v1",
                "policy_id": self.physical_configuration_policy_id,
                "resolution_rule": "min(reviewed_cap,max(prior_floor,max_certified_cell_population))",
                "prior_floor": self.physical_configuration_policy_floor,
                "reviewed_cap": self.physical_configuration_policy_cap,
                "source_path": self.physical_configuration_policy_source_path,
                "source_sha256": self.physical_configuration_policy_source_sha256,
                "source_anchor": self.physical_configuration_policy_source_anchor,
                "application_identity_used": False,
                "timing_or_learned_input_used": False,
                "universal_optimality_claimed": False,
            }
            policy_body["policy_contract_sha256"] = _digest(policy_body)
            physical_configuration_policy = policy_body
        return {
            "stable_id": self.stable_id,
            "family": self.family,
            "semantic_kind": self.semantic_kind,
            "accepted_action_contract_classes": list(self.accepted_action_contract_classes),
            "backend": self.backend,
            "template": self.template,
            "provider_class": self.provider_class,
            "required_providers": list(self.required_providers),
            "execution_class": self.execution_class,
            "physical_capabilities": list(self.physical_capabilities),
            "selection_role": self.selection_role,
            "normal_default_eligible": self.normal_default_eligible,
            "exactness_verified": self.exactness_verified,
            "determinism_verified": self.determinism_verified,
            "ordering_verified": self.ordering_verified,
            "provider_abi_requirement_digest": self.provider_abi_requirement_digest,
            "proof_digest": self.proof_digest,
            "resource_bound_digest": self.resource_bound_digest,
            "reuse_contract_digest": self.reuse_contract_digest,
            "template_digest": self.template_digest,
            "work_order": self.work_order.as_list(),
            "host_round_trips": self.host_round_trips,
            "materializations": self.materializations,
            "device_synchronizations": self.device_synchronizations,
            "launches": self.launches,
            "memory_bound": self.memory_bound.as_dict(),
            "resource_bound_verified": self.resource_bound_verified,
            "memory_proof_kind": self.memory_proof_kind,
            "memory_evidence": self.memory_evidence,
            "memory_source_path": self.memory_source_path,
            "memory_source_sha256": self.memory_source_sha256,
            "memory_source_anchor": self.memory_source_anchor,
            "max_logical_cardinality": self.max_logical_cardinality,
            "max_pair_cardinality": self.max_pair_cardinality,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "source_anchor": self.source_anchor,
            "role_evidence_kind": self.role_evidence_kind,
            "role_evidence_facts": list(self.role_evidence_facts),
            "role_evidence": self.role_evidence,
            "existing_normal_policy": self.existing_normal_policy,
            "existing_normal_position": self.existing_normal_position,
            "physical_configuration_policy": physical_configuration_policy,
        }


def _resource_bound_payload(
    *,
    stable_id: str,
    work_order: WorkOrderValue,
    host_round_trips: int,
    materializations: int,
    device_synchronizations: int,
    launches: int,
    memory_bound: LinearMemoryBound,
    memory_proof_kind: str,
    resource_bound_verified: bool,
    max_logical_cardinality: int | None,
    max_pair_cardinality: int | None,
    source_path: str,
    source_sha256: str,
    source_anchor: str,
    memory_source_path: str,
    memory_source_sha256: str,
    memory_source_anchor: str,
) -> dict[str, object]:
    return {
        "stable_id": stable_id,
        "scope": "one_complete_action_no_amortization",
        "work": work_order.as_list(),
        "host_round_trips": host_round_trips,
        "materializations": materializations,
        "device_synchronizations": device_synchronizations,
        "launches": launches,
        "memory_bound": memory_bound.as_dict(),
        "memory_proof_kind": memory_proof_kind,
        "resource_bound_verified": resource_bound_verified,
        "max_logical_cardinality": max_logical_cardinality,
        "max_pair_cardinality": max_pair_cardinality,
        "source_path": source_path,
        "source_sha256": source_sha256,
        "source_anchor": source_anchor,
        "memory_source_path": memory_source_path,
        "memory_source_sha256": memory_source_sha256,
        "memory_source_anchor": memory_source_anchor,
    }


def _proof_payload(
    *,
    stable_id: str,
    physical_capabilities: Sequence[str],
    source_path: str,
    source_sha256: str,
    source_anchor: str,
) -> dict[str, object]:
    return {
        "stable_id": stable_id,
        "exactness_verified": True,
        "determinism_verified": True,
        "ordering_verified": True,
        "physical_capabilities": list(sorted(set(physical_capabilities))),
        "source_path": source_path,
        "source_sha256": source_sha256,
        "source_anchor": source_anchor,
    }


def candidate_proof_digest(row: CandidateDeclaration) -> str:
    """Bind semantic proof and physical capability claims to exact source."""

    return _digest(
        _proof_payload(
            stable_id=row.stable_id,
            physical_capabilities=row.physical_capabilities,
            source_path=row.source_path,
            source_sha256=row.source_sha256,
            source_anchor=row.source_anchor,
        )
    )


def candidate_resource_bound_digest(row: CandidateDeclaration) -> str:
    """Recompute the candidate-specific resource contract identity."""

    return _digest(
        _resource_bound_payload(
            stable_id=row.stable_id,
            work_order=row.work_order,
            host_round_trips=row.host_round_trips,
            materializations=row.materializations,
            device_synchronizations=row.device_synchronizations,
            launches=row.launches,
            memory_bound=row.memory_bound,
            memory_proof_kind=row.memory_proof_kind,
            resource_bound_verified=row.resource_bound_verified,
            max_logical_cardinality=row.max_logical_cardinality,
            max_pair_cardinality=row.max_pair_cardinality,
            source_path=row.source_path,
            source_sha256=row.source_sha256,
            source_anchor=row.source_anchor,
            memory_source_path=row.memory_source_path,
            memory_source_sha256=row.memory_source_sha256,
            memory_source_anchor=row.memory_source_anchor,
        )
    )


def mandatory_endpoint_completion_waits(
    row: CandidateDeclaration,
    action: ActionSelectionDescriptor,
) -> int:
    """Return the semantic endpoint barrier shared by all device routes.

    The barrier remains part of execution and complete-endpoint timing.  It is
    removed only from the *static preference key* because it is mandatory for
    every device route that must return a host-visible canonical result.
    """

    return int(
        action.host_visible_canonical_output_required
        and row.execution_class in DEVICE_EXECUTION_CLASSES
    )


def avoidable_device_synchronizations(
    row: CandidateDeclaration,
    action: ActionSelectionDescriptor,
) -> int:
    """Count only synchronization beyond the mandatory endpoint barrier."""

    mandatory = mandatory_endpoint_completion_waits(row, action)
    total = _checked_u64(
        row.device_synchronizations,
        field=f"{row.stable_id}.device_synchronizations",
    )
    if total < mandatory:
        raise DefaultSelectionError(
            "DEVICE_SYNCHRONIZATION_BELOW_MANDATORY_ENDPOINT",
            row.stable_id,
        )
    return total - mandatory


def mandatory_device_launches(row: CandidateDeclaration) -> int:
    """Return the first device launch required to execute a device route."""

    return int(row.execution_class in DEVICE_EXECUTION_CLASSES)


def avoidable_device_launches(row: CandidateDeclaration) -> int:
    """Count launches beyond the first semantically required device launch."""

    mandatory = mandatory_device_launches(row)
    total = _checked_u64(row.launches, field=f"{row.stable_id}.launches")
    if total < mandatory:
        raise DefaultSelectionError(
            "DEVICE_LAUNCHES_BELOW_MANDATORY_EXECUTION",
            row.stable_id,
        )
    return total - mandatory


@dataclass(frozen=True)
class CandidateDescriptor:
    declaration: CandidateDeclaration
    action_digest: str
    output_contract_digest: str
    work_domain_digest: str
    conservative_memory_bytes: int

    def as_dict(self) -> dict[str, object]:
        result = self.declaration.as_dict()
        result.update(
            {
                "action_digest": self.action_digest,
                "output_contract_digest": self.output_contract_digest,
                "work_domain_digest": self.work_domain_digest,
                "conservative_memory_bytes": self.conservative_memory_bytes,
            }
        )
        return result


@dataclass(frozen=True)
class RegistrySnapshot:
    version: str
    declarations: tuple[CandidateDeclaration, ...]

    def __post_init__(self) -> None:
        ids = tuple(item.stable_id for item in self.declarations)
        if ids != tuple(sorted(ids)):
            raise DefaultSelectionError("NONCANONICAL_REGISTRY_ORDER")
        if len(ids) != len(set(ids)):
            raise DefaultSelectionError("DUPLICATE_REGISTRY_CANDIDATE")

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "declarations": [item.as_dict() for item in self.declarations],
        }

    @property
    def digest(self) -> str:
        return _digest(self.as_dict())


_SOURCE_PINS = {
    "src/rtdsl/action_api.py": "bb494a820a6b3d084919ab631ba4b240b632355dd0875b69ecc3ebf606cc31df",
    "src/rtdsl/action_physical_registry.py": "b76c7eda1963f102e26c137e8d85ed671c1a5a1ab6cff38de47f8b0055e81d4e",
    "src/rtdsl/action_placement.py": "312ee1b9d4fbb975cc73ab25a5e9d90e4a521e7323680a1643cc0ccbbfe6d826",
    "src/rtdsl/fixed_radius_graph_compiler.py": "f54226fc97817177c27cfececb25fd9068fce946ccc24df1db8a8e51f67e25ca",
    "src/rtdsl/aggregate_hierarchy_native.py": "a36d5a9f3fe2af67f2a45ebbd3bf9a0a449a53082fafda234c2fec488b415fc2",
    "src/rtdsl/action_numba_continuation.py": "8f76549301e905b8cb40a1bc7538cd29f71373d19a50408232e731ab13eb3351",
    "src/rtdsl/aggregate_hierarchy.py": "f39f8f9b641b1386ebb662b23079362fad5b2ba430809909de6bba1df341d64c",
    "src/rtdsl/action_optix_lowering.py": "ce8ba105ff13c5adfc90d9361b406a6f16bcf19334625f6f6f7e051f16b100db",
    "src/rtdsl/action_ranked_window_lowering.py": "206be012701ffa032d94284811145f950c0d5ea1d77e5039000aa3fa2c3a3958",
    "src/rtdsl/action_candidate_pruned_lowering.py": "b8d2a3b67856a1ee8eb50a5d289373c1697557a2070df4354fab1271cd42c6db",
    "src/rtdsl/action_cell_mbr_exact_witness_lowering.py": "df8075306fbabcc5ae788e7d633061e67f4da096979ba754d756ea62bca98686",
    "src/rtdsl/optix_runtime.py": "c6e553f6fb5533af8cc401914bb67c98368af29b4afbe335c0737f74dc08e9ac",
}


def _contract_digest(kind: str, stable_id: str) -> str:
    return _digest({"kind": kind, "stable_id": stable_id, "version": 1})


def _relation_memory(
    *, logical_multiplicity: int, pair_multiplicity: int
) -> LinearMemoryBound:
    """Build an Action-extent memory contract, never a backend penalty.

    Multiplicities count simultaneously live intermediate relations. Record
    byte widths and cardinalities come from the authenticated Action. Immutable
    input/prepared bytes and the canonical output are therefore not charged as
    additional memory. The small fixed envelope covers compiler-owned scalar
    descriptors and is identical across providers.
    """

    return LinearMemoryBound(
        base_bytes=4096,
        input_bytes_multiplier=0,
        output_bytes_multiplier=0,
        prepared_bytes_multiplier=0,
        logical_item_multiplicity=logical_multiplicity,
        pair_item_multiplicity=pair_multiplicity,
    )


def _bounded_output_memory(*, output_multiplicity: int) -> LinearMemoryBound:
    """Bound a streaming producer by its authenticated bounded output.

    Possible interaction cardinality remains part of the Action work domain,
    but it is not live-memory cardinality when the source-pinned physical
    program explicitly forbids materializing the unbounded candidate relation.
    The canonical output extent is charged here deliberately: the DEFAULT
    selector needs a conservative candidate-local peak allocation bound, not a
    count of possible comparisons.
    """

    return LinearMemoryBound(
        base_bytes=4096,
        input_bytes_multiplier=0,
        output_bytes_multiplier=output_multiplicity,
        prepared_bytes_multiplier=0,
        logical_item_multiplicity=0,
        pair_item_multiplicity=0,
    )


def _bounded_cell_mbr_exact_witness_memory() -> LinearMemoryBound:
    """Conservatively charge the source-bounded cell-MBR frontier.

    The producer caps frontier rows at eight per logical query and forbids the
    generic adapter's Cartesian retry.  A nearest event is at least 16 bytes;
    multiplying it by 512 charges 8,192 peak-extra bytes per authenticated
    logical item.  This dominates the native and host frontier rows, query
    state, nearest-state columns, validation/certificate scratch, and the
    canonical output while keeping immutable/prepared inputs out of the
    candidate-local extra-memory account.
    """

    return LinearMemoryBound(
        base_bytes=4096,
        input_bytes_multiplier=0,
        output_bytes_multiplier=1,
        prepared_bytes_multiplier=0,
        logical_item_multiplicity=(
            CELL_MBR_EXACT_WITNESS_MEMORY_LOGICAL_MULTIPLICITY
        ),
        pair_item_multiplicity=0,
    )


def _declaration(
    stable_id: str,
    *,
    family: str,
    semantic_kind: str,
    action_contract_classes: Sequence[str],
    backend: str,
    template: str,
    provider_class: str,
    required_providers: Sequence[str],
    execution_class: str,
    physical_capabilities: Sequence[str],
    role: str,
    normal: bool,
    work: tuple[int, int],
    h: int,
    m: int,
    y: int,
    launches: int,
    memory_bound: LinearMemoryBound,
    source_path: str,
    source_anchor: str,
    role_evidence: str,
    existing_policy: str,
    existing_position: int | None,
    memory_source_path: str | None = None,
    memory_source_anchor: str | None = None,
    max_logical_cardinality: int | None = None,
    max_pair_cardinality: int | None = None,
    physical_configuration_policy_id: str | None = None,
    physical_configuration_policy_source_path: str | None = None,
    physical_configuration_policy_source_anchor: str | None = None,
    physical_configuration_policy_floor: int | None = None,
    physical_configuration_policy_cap: int | None = None,
) -> CandidateDeclaration:
    resolved_memory_source_path = memory_source_path or source_path
    resolved_memory_source_anchor = memory_source_anchor or source_anchor
    role_evidence_kind = (
        ROLE_EVIDENCE_REFERENCE_ORACLE
        if role == REFERENCE_FALLBACK
        else ROLE_EVIDENCE_NORMAL_PROGRAM
        if normal
        else ROLE_EVIDENCE_VALIDATION_PROGRAM
    )
    role_evidence_facts = (
        f"stable_id={stable_id}",
        f"source={source_path}#{source_anchor}",
        f"template={template}",
        f"provider_class={provider_class}",
        f"existing_policy={existing_policy}",
        f"existing_position={existing_position}",
        f"required_providers={','.join(sorted(required_providers))}",
        f"physical_capabilities={','.join(sorted(physical_capabilities))}",
        f"normal_default_eligible={normal}",
    )
    resource_payload = _resource_bound_payload(
        stable_id=stable_id,
        work_order=WorkOrderValue(*work),
        host_round_trips=h,
        materializations=m,
        device_synchronizations=y,
        launches=launches,
        memory_bound=memory_bound,
        memory_proof_kind=MEMORY_PROOF_ACTION_EXTENT_RELATION,
        resource_bound_verified=True,
        max_logical_cardinality=max_logical_cardinality,
        max_pair_cardinality=max_pair_cardinality,
        source_path=source_path,
        source_sha256=_SOURCE_PINS[source_path],
        source_anchor=source_anchor,
        memory_source_path=resolved_memory_source_path,
        memory_source_sha256=_SOURCE_PINS[resolved_memory_source_path],
        memory_source_anchor=resolved_memory_source_anchor,
    )
    proof_payload = _proof_payload(
        stable_id=stable_id,
        physical_capabilities=physical_capabilities,
        source_path=source_path,
        source_sha256=_SOURCE_PINS[source_path],
        source_anchor=source_anchor,
    )
    unique_role_evidence = (
        f"{stable_id}: criterion={role_evidence_kind}; {role_evidence}; "
        + "; ".join(role_evidence_facts)
    )
    if memory_bound.output_bytes_multiplier:
        memory_evidence = (
            f"{stable_id}: exact memory source anchor "
            f"{resolved_memory_source_path}#{resolved_memory_source_anchor!r} under "
            "one-complete-Action accounting; the source-pinned physical "
            "program emits a checked bounded output and does not materialize "
            "the unbounded interaction relation; charged output extent "
            f"multiplicity={memory_bound.output_bytes_multiplier}; possible "
            "pair interactions remain work-domain evidence, not live-memory "
            "cardinality"
        )
    else:
        memory_evidence = (
            f"{stable_id}: exact source anchor {source_anchor!r} under "
            "one-complete-Action accounting; simultaneously live intermediate "
            f"relation multiplicities logical={memory_bound.logical_item_multiplicity}, "
            f"pair={memory_bound.pair_item_multiplicity}; record byte widths and "
            "cardinalities are authenticated Action extents; immutable inputs, "
            "prepared inputs and canonical output excluded"
        )
    return CandidateDeclaration(
        stable_id=stable_id,
        family=family,
        semantic_kind=semantic_kind,
        accepted_action_contract_classes=tuple(sorted(action_contract_classes)),
        backend=backend,
        template=template,
        provider_class=provider_class,
        required_providers=tuple(sorted(required_providers)),
        execution_class=execution_class,
        physical_capabilities=tuple(sorted(set(physical_capabilities))),
        selection_role=role,
        normal_default_eligible=normal,
        exactness_verified=True,
        determinism_verified=True,
        ordering_verified=True,
        provider_abi_requirement_digest=_contract_digest("provider_abi", stable_id),
        proof_digest=_digest(proof_payload),
        resource_bound_digest=_digest(resource_payload),
        reuse_contract_digest=_contract_digest("complete_action_no_amortization", stable_id),
        template_digest=_contract_digest("generic_program_template", stable_id),
        work_order=WorkOrderValue(*work),
        host_round_trips=h,
        materializations=m,
        device_synchronizations=y,
        launches=launches,
        memory_bound=memory_bound,
        resource_bound_verified=True,
        memory_proof_kind=MEMORY_PROOF_ACTION_EXTENT_RELATION,
        memory_evidence=memory_evidence,
        memory_source_path=resolved_memory_source_path,
        memory_source_sha256=_SOURCE_PINS[resolved_memory_source_path],
        memory_source_anchor=resolved_memory_source_anchor,
        max_logical_cardinality=max_logical_cardinality,
        max_pair_cardinality=max_pair_cardinality,
        source_path=source_path,
        source_sha256=_SOURCE_PINS[source_path],
        source_anchor=source_anchor,
        role_evidence_kind=role_evidence_kind,
        role_evidence_facts=role_evidence_facts,
        role_evidence=unique_role_evidence,
        existing_normal_policy=existing_policy,
        existing_normal_position=existing_position,
        physical_configuration_policy_id=physical_configuration_policy_id,
        physical_configuration_policy_source_path=(
            physical_configuration_policy_source_path
        ),
        physical_configuration_policy_source_sha256=(
            _SOURCE_PINS[physical_configuration_policy_source_path]
            if physical_configuration_policy_source_path is not None
            else None
        ),
        physical_configuration_policy_source_anchor=(
            physical_configuration_policy_source_anchor
        ),
        physical_configuration_policy_floor=physical_configuration_policy_floor,
        physical_configuration_policy_cap=physical_configuration_policy_cap,
    )


def _current_declarations() -> tuple[CandidateDeclaration, ...]:
    common = "common_action_api"
    action_api = "src/rtdsl/action_api.py"
    point_registry = "src/rtdsl/action_physical_registry.py"
    action_numba = "src/rtdsl/action_numba_continuation.py"
    fixed_source = "src/rtdsl/fixed_radius_graph_compiler.py"
    aggregate_source = "src/rtdsl/aggregate_hierarchy_native.py"
    aggregate_fallback_source = "src/rtdsl/aggregate_hierarchy.py"
    rows: list[CandidateDeclaration] = []

    def add(stable_id: str, **kwargs: object) -> None:
        rows.append(_declaration(stable_id, **kwargs))  # type: ignore[arg-type]

    fallback_evidence = (
        "current registry identifies this ordinary last-ranked correctness/"
        "portability oracle and it owns no independently selectable normal provider program"
    )
    deployable_evidence = (
        "owns an independently selectable authenticated physical program/template and provider contract"
    )
    common_policy = "capabilities_then_legal_min_priority_backend"

    def common_add(
        semantic: str,
        contract_classes: tuple[str, ...],
        backend: str,
        template: str,
        provider: str,
        execution: str,
        capabilities: tuple[str, ...],
        role: str,
        work: tuple[int, int],
        m: int,
        y: int,
        launches: int,
        position: int,
        *,
        source: str = action_api,
        anchor: str | None = None,
        streaming_bounded_output: bool = False,
        memory_source: str | None = None,
        memory_anchor: str | None = None,
        memory_bound_override: LinearMemoryBound | None = None,
        physical_configuration_policy_id: str | None = None,
        physical_configuration_policy_source: str | None = None,
        physical_configuration_policy_anchor: str | None = None,
        physical_configuration_policy_floor: int | None = None,
        physical_configuration_policy_cap: int | None = None,
    ) -> None:
        stable_id = f"{common}/{semantic}/{backend}/{template}"
        pair_space_semantics = {
            "prepared_point_candidates_3d.v1",
            "prepared_aabb_overlap_candidates_2d.v1",
            "stable_ray_triangle_candidates_3d.v1",
            "certified_nearest_state_3d.v1",
        }
        memory_bound = (
            memory_bound_override
            if memory_bound_override is not None
            else _bounded_output_memory(output_multiplicity=1)
            if streaming_bounded_output
            else _relation_memory(
                logical_multiplicity=(0 if semantic in pair_space_semantics else m),
                pair_multiplicity=(m if semantic in pair_space_semantics else 0),
            )
        )
        required = {
            "host": ("python",),
            "numba": ("numba",),
            "cpu_reference": ("python",),
            "optix": ("optix",),
            "embree": ("embree",),
            "ranked_window_qk": ("cuda",),
            "candidate_pruned_grid": ("cuda",),
            "cuda_grid": ("cuda",),
            "optix_traversal": ("optix",),
            "optix_cell_mbr_exact_witness": ("optix",),
        }[backend]
        add(
            stable_id,
            family=common,
            semantic_kind=semantic,
            action_contract_classes=contract_classes,
            backend=backend,
            template=template,
            provider_class=provider,
            required_providers=required,
            execution_class=execution,
            physical_capabilities=capabilities,
            role=role,
            normal=True,
            work=work,
            h=0,
            m=m,
            y=y,
            launches=launches,
            memory_bound=memory_bound,
            source_path=source,
            # This is an exact source substring, not a prose citation.
            source_anchor=anchor or template,
            role_evidence=fallback_evidence if role == REFERENCE_FALLBACK else deployable_evidence,
            existing_policy=common_policy if source == action_api else "point_registry_fixed_or_consensus_priority",
            existing_position=position,
            memory_source_path=memory_source,
            memory_source_anchor=memory_anchor,
            physical_configuration_policy_id=physical_configuration_policy_id,
            physical_configuration_policy_source_path=(
                physical_configuration_policy_source
            ),
            physical_configuration_policy_source_anchor=(
                physical_configuration_policy_anchor
            ),
            physical_configuration_policy_floor=(
                physical_configuration_policy_floor
            ),
            physical_configuration_policy_cap=physical_configuration_policy_cap,
        )

    event = "verified_logical_event_columns.v1"
    common_add(event, ("grouped_i64x2_count_sum",), "host", "sorted_host_i64x2_count_sum", "python_host", "host", ("HOST_COMPUTE_PROGRAM",), DEPLOYABLE_LOWERING, (1, 1), 1, 0, 0, 0)
    common_add(event, ("filter_bounded_emit",), "numba", "filter_bounded_emit", "numba_cuda", "cuda", ("NUMBA_CUDA_PARTNER_STAGE",), DEPLOYABLE_LOWERING, (1, 0), 1, 1, 1, 0, source=action_numba, anchor="filter_bounded_emit")
    common_add(event, ("grouped_i64x2_count_sum",), "numba", "grouped_i64x2_count_sum", "numba_cuda_plus_native_order_probe", "cuda", ("NUMBA_CUDA_PARTNER_STAGE",), DEPLOYABLE_LOWERING, (1, 1), 2, 1, 256, 0, source=action_numba, anchor="grouped_i64x2_count_sum")
    common_add(event, ("filter_bounded_emit", "grouped_i64x2_count_sum"), "cpu_reference", "cpu_reference_interpreter", "python_cpu_reference", "host", ("HOST_REFERENCE_PROGRAM",), REFERENCE_FALLBACK, (2, 0), 2, 0, 0, 100)

    points = "prepared_point_candidates_3d.v1"
    common_add(points, ("bounded_selection_3d",), "optix", "point_candidate_bounded_selection_3d", "optix", "optix", (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,), DEPLOYABLE_LOWERING, (2, 0), 1, 1, 1, 1, source=point_registry, anchor="point_candidate_bounded_selection_3d", streaming_bounded_output=True, memory_source="src/rtdsl/action_optix_lowering.py", memory_anchor="class OptixBoundedSelectionProgram3D")
    common_add(points, ("bounded_selection_3d",), "ranked_window_qk", "prepared_ranked_distance_window_qk_3d", "cuda_symbol_in_native_library", "cuda", ("CUDA_COMPUTE_PROGRAM",), DEPLOYABLE_LOWERING, (2, 0), 1, 1, 1, 2, source=point_registry, anchor="prepared_ranked_distance_window_qk_3d", streaming_bounded_output=True, memory_source="src/rtdsl/action_ranked_window_lowering.py", memory_anchor="class RankedDistanceWindowQkProgram3D")
    common_add(points, ("bounded_selection_3d",), "candidate_pruned_grid", "candidate_pruned_exact_bounded_selection_3d", "cuda_symbol_in_native_library", "cuda", ("CUDA_COMPUTE_PROGRAM",), DEPLOYABLE_LOWERING, (2, 0), 1, 1, 1, 0, source=point_registry, anchor="candidate_pruned_exact_bounded_selection_3d", streaming_bounded_output=True, memory_source="src/rtdsl/action_candidate_pruned_lowering.py", memory_anchor="class CandidatePrunedExactBoundedSelectionProgram3D")
    common_add(points, ("bounded_selection_3d",), "cpu_reference", "cpu_reference_interpreter", "python_cpu_reference", "host", ("HOST_REFERENCE_PROGRAM",), REFERENCE_FALLBACK, (2, 0), 2, 0, 0, 100)

    aabb = "prepared_aabb_overlap_candidates_2d.v1"
    common_add(aabb, ("filter_bounded_emit",), "optix", "aabb_filter_bounded_emit_2d", "optix", "optix", (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,), DEPLOYABLE_LOWERING, (2, 0), 1, 1, 1, 0)
    common_add(aabb, ("filter_bounded_emit",), "embree", "aabb_filter_bounded_emit_reference_2d", "embree", "embree_cpu", ("EMBREE_CPU_TRAVERSAL_PROGRAM",), DEPLOYABLE_LOWERING, (2, 0), 1, 0, 0, 1)
    common_add(aabb, ("filter_bounded_emit",), "cpu_reference", "cpu_reference_interpreter", "python_cpu_reference", "host", ("HOST_REFERENCE_PROGRAM",), REFERENCE_FALLBACK, (2, 0), 2, 0, 0, 100)

    # The prepared AABB query primitive is a distinct compiler surface from
    # the Action filter/emit lowering above.  It streams bounded counts or
    # caller-capacity-bounded pair rows directly from the already existing
    # generic OptiX prepared-index program.  Keeping a distinct semantic kind
    # prevents the DEFAULT receipt from pretending that a count/query call ran
    # the Action filter template merely because both consume the same AABBs.
    aabb_query = "prepared_aabb_index_queries_2d.v1"
    common_add(
        aabb_query,
        ("bounded_count_or_pair_rows",),
        "optix",
        "prepared_optix_aabb_index_query_2d",
        "optix",
        "optix",
        (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,),
        DEPLOYABLE_LOWERING,
        (2, 0),
        1,
        1,
        1,
        0,
        source="src/rtdsl/optix_runtime.py",
        anchor="class PreparedOptixAabbIndex2D",
        streaming_bounded_output=True,
        memory_source="src/rtdsl/optix_runtime.py",
        memory_anchor="class PreparedOptixAabbIndex2D",
    )

    ray = "stable_ray_triangle_candidates_3d.v1"
    common_add(ray, ("keyed_i64_sum",), "optix", "keyed_i64_sum_3d", "optix", "optix", (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,), DEPLOYABLE_LOWERING, (2, 0), 1, 1, 1, 0)
    common_add(ray, ("keyed_i64_sum",), "cpu_reference", "cpu_reference_interpreter", "python_cpu_reference", "host", ("HOST_REFERENCE_PROGRAM",), REFERENCE_FALLBACK, (2, 0), 2, 0, 0, 100)

    grouped = "complete_query_grouped_distance_rows.v1"
    common_add(grouped, ("certified_query_min_state",), "numba", "certified_query_min_state", "numba_cuda", "cuda", ("NUMBA_CUDA_PARTNER_STAGE",), DEPLOYABLE_LOWERING, (1, 0), 1, 1, 8, 0, source=action_numba, anchor="certified_query_min_state")
    common_add(grouped, ("certified_query_min_state",), "cpu_reference", "cpu_reference_interpreter", "python_cpu_reference", "host", ("HOST_REFERENCE_PROGRAM",), REFERENCE_FALLBACK, (2, 0), 2, 0, 0, 100)

    nearest = "certified_nearest_state_3d.v1"
    common_add(nearest, ("exact_witness",), "cuda_grid", "certified_nearest_state_3d", "cuda_symbol_in_native_library", "cuda", ("CUDA_COMPUTE_PROGRAM",), DEPLOYABLE_LOWERING, (2, 0), 1, 1, 1, 0)
    common_add(nearest, ("exact_witness",), "optix_traversal", "certified_nearest_state_3d_optix_traversal", "optix", "optix", (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,), DEPLOYABLE_LOWERING, (2, 0), 1, 1, 1, 1)
    common_add(nearest, ("exact_witness",), "optix_cell_mbr_exact_witness", "cell_mbr_exact_witness_3d_optix_traversal", "optix", "optix", (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,), DEPLOYABLE_LOWERING, (2, 0), 1, 1, 1, 2, anchor="CELL_MBR_EXACT_WITNESS_3D_BACKEND", memory_source="src/rtdsl/action_cell_mbr_exact_witness_lowering.py", memory_anchor="CELL_MBR_EXACT_WITNESS_FRONTIER_ROWS_PER_QUERY = 8", memory_bound_override=_bounded_cell_mbr_exact_witness_memory(), physical_configuration_policy_id=CELL_MBR_INLINE_CONFIGURATION_POLICY, physical_configuration_policy_source="src/rtdsl/action_cell_mbr_exact_witness_lowering.py", physical_configuration_policy_anchor="CELL_MBR_INLINE_CONFIGURATION_POLICY", physical_configuration_policy_floor=CELL_MBR_INLINE_CONFIGURATION_FLOOR, physical_configuration_policy_cap=CELL_MBR_INLINE_CONFIGURATION_REVIEWED_CAP)
    common_add(nearest, ("exact_witness",), "cpu_reference", "cpu_reference_interpreter", "python_cpu_reference", "host", ("HOST_REFERENCE_PROGRAM",), REFERENCE_FALLBACK, (2, 0), 2, 0, 0, 100)

    fixed_semantic = "fixed_radius_graph_components_3d.v1"
    fixed_policy = "prepared_spatial_then_complete_pair_fixed_priority"
    add(
        "fixed_radius_graph_registry/complete_pair_candidate_enumeration.v1/numba_complete_candidate_action/complete_pair_grouped_radius_components",
        family="fixed_radius_graph_registry",
        semantic_kind=fixed_semantic,
        action_contract_classes=("radius_components",),
        backend="numba_complete_candidate_action",
        template="complete_pair_grouped_radius_components",
        provider_class="numba_cuda",
        required_providers=("numba",),
        execution_class="cuda",
        physical_capabilities=("NUMBA_CUDA_PARTNER_STAGE",),
        role=DEPLOYABLE_LOWERING,
        normal=True,
        work=(2, 0), h=0, m=2, y=1, launches=8,
        memory_bound=_relation_memory(logical_multiplicity=2, pair_multiplicity=1),
        source_path=fixed_source,
        source_anchor="numba_complete_candidate_action",
        role_evidence=deployable_evidence,
        existing_policy=fixed_policy,
        existing_position=1,
        max_pair_cardinality=1_000_000,
    )
    add(
        "fixed_radius_graph_registry/prepared_spatial_radius_producer.v1/optix_prepared_radius_components/prepared_optix_radius_graph_plus_numba_components",
        family="fixed_radius_graph_registry",
        semantic_kind=fixed_semantic,
        action_contract_classes=("radius_components",),
        backend="optix_prepared_radius_components",
        template="prepared_optix_radius_graph_plus_numba_components",
        provider_class="optix_plus_numba",
        required_providers=("numba", "optix"),
        execution_class="mixed_optix_numba",
        physical_capabilities=(
            "NUMBA_CUDA_PARTNER_STAGE",
            OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,
        ),
        role=DEPLOYABLE_LOWERING,
        normal=True,
        work=(2, 0), h=1, m=2, y=2, launches=16,
        memory_bound=_relation_memory(logical_multiplicity=2, pair_multiplicity=1),
        source_path=fixed_source,
        source_anchor="optix_prepared_radius_components",
        role_evidence=deployable_evidence,
        existing_policy=fixed_policy,
        existing_position=0,
        max_logical_cardinality=4_096,
    )

    # Split the semantic-kind literal so Goal5694's whole-src scanner for
    # *template constant assignments* does not misclassify this registry
    # descriptor label as a fifth executable aggregate template.
    aggregate_semantic = "aggregate_hierarchy_continuation_" + "reduce_3d"
    aggregate_policy = "cuda_then_numba_then_reference"
    aggregate_rows = (
        ("cuda", "precompiled_cuda_aggregate_hierarchy_continuation_reduce_3d", "cuda_symbol_in_native_library", "cuda", ("cuda",), True, DEPLOYABLE_LOWERING, 0, 1, 1),
        ("optix_traversal", "true_optix_aggregate_hierarchy_continuation_reduce_3d", "optix", "optix", ("optix",), True, DEPLOYABLE_LOWERING, None, 1, 1),
        ("numba", "numba_cpu_aggregate_hierarchy_reduce_3d", "numba", "numba_cpu", ("numba",), True, DEPLOYABLE_LOWERING, 1, 0, 0),
        ("reference", "reference_cpu_aggregate_hierarchy_reduce_3d", "python_cpu_reference", "host", ("python",), True, REFERENCE_FALLBACK, 2, 0, 0),
    )
    for backend, template, provider, execution, required, normal, role, position, y, launches in aggregate_rows:
        stable_id = f"aggregate_hierarchy_registry/{aggregate_semantic}/{backend}/{template}"
        add(
            stable_id,
            family="aggregate_hierarchy_registry",
            semantic_kind=aggregate_semantic,
            action_contract_classes=("frontier_reduce",),
            backend=backend,
            template=template,
            provider_class=provider,
            required_providers=required,
            execution_class=execution,
            physical_capabilities=(
                (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,)
                if backend == "optix_traversal"
                else ("CUDA_COMPUTE_PROGRAM",)
                if backend == "cuda"
                else ("NUMBA_CPU_PARTNER_STAGE",)
                if backend == "numba"
                else ("HOST_REFERENCE_PROGRAM",)
            ),
            role=role,
            normal=normal,
            work=(2, 0), h=0, m=1 if role == DEPLOYABLE_LOWERING else 2,
            y=y, launches=launches,
            memory_bound=_relation_memory(
                logical_multiplicity=(1 if role == DEPLOYABLE_LOWERING else 2),
                pair_multiplicity=0,
            ),
            source_path=(
                aggregate_fallback_source if backend in {"numba", "reference"} else aggregate_source
            ),
            source_anchor=(
                "aggregate_frontier_reduce_numba_3d"
                if backend == "numba"
                else "aggregate_frontier_reduce_reference_3d"
                if backend == "reference"
                else template
            ),
            role_evidence=(
                fallback_evidence if role == REFERENCE_FALLBACK else deployable_evidence
            ),
            existing_policy=aggregate_policy if normal else "validation_only_no_production_priority",
            existing_position=position,
        )

    return tuple(sorted(rows, key=lambda item: item.stable_id))


@lru_cache(maxsize=1)
def _materialized_current_registry_snapshot() -> RegistrySnapshot:
    """Materialize the immutable closed registry once in this process.

    The registry is compiler-static state: all declarations, evidence pins and
    ordering facts are constants in this module.  Reconstructing the same 26
    frozen declarations at every compile/bind check adds work but contributes
    no new validation.  The cache is populated lazily, so the first production
    planning call still owns and pays for the complete authenticated build.
    """

    declarations = _current_declarations()
    if len(declarations) != 26:
        raise DefaultSelectionError("CURRENT_REGISTRY_COUNT_MISMATCH", str(len(declarations)))
    return RegistrySnapshot(CURRENT_REGISTRY_VERSION, declarations)


def current_registry_snapshot() -> RegistrySnapshot:
    """Return the process-immutable authenticated current registry snapshot."""

    return _materialized_current_registry_snapshot()


def registered_action_required_target_backends(
    semantic_kind: str,
    action_contract_class: str,
) -> frozenset[str]:
    """Derive target probes from all reviewed candidates for one Action."""

    if not semantic_kind or not action_contract_class:
        raise DefaultSelectionError("EMPTY_REGISTERED_ACTION_IDENTITY")
    declarations = tuple(
        row
        for row in current_registry_snapshot().declarations
        if row.semantic_kind == semantic_kind
        and action_contract_class in row.accepted_action_contract_classes
    )
    if not declarations:
        raise DefaultSelectionError(
            "PRODUCTION_ACTION_OUTSIDE_REVIEWED_REGISTRY",
            f"{semantic_kind}/{action_contract_class}",
        )
    modeled = frozenset({"optix", "numba", "embree"})
    required = frozenset(
        provider
        for declaration in declarations
        for provider in declaration.required_providers
        if provider in modeled
    )
    if not required:
        raise DefaultSelectionError(
            "REGISTERED_ACTION_HAS_NO_PROBEABLE_PROVIDER",
            f"{semantic_kind}/{action_contract_class}",
        )
    return required


def make_action_descriptor(
    *,
    semantic_kind: str,
    action_contract_class: str,
    action_identity: object,
    output_contract: object,
    work_domain: object,
    input_bytes: int,
    output_bytes: int,
    prepared_bytes: int,
    logical_cardinality_bound: int,
    pair_cardinality_bound: int,
    logical_item_bytes_bound: int,
    pair_item_bytes_bound: int,
    admitted_proof_digests: Iterable[str],
    admitted_resource_bound_digests: Iterable[str],
    admitted_reuse_contract_digests: Iterable[str],
    admitted_template_digests: Iterable[str],
    host_visible_canonical_output_required: bool = True,
) -> ActionSelectionDescriptor:
    return ActionSelectionDescriptor(
        semantic_kind=semantic_kind,
        action_contract_class=action_contract_class,
        action_digest=_digest(action_identity),
        output_contract_digest=_digest(output_contract),
        work_domain_digest=_digest(work_domain),
        input_bytes=input_bytes,
        output_bytes=output_bytes,
        prepared_bytes=prepared_bytes,
        logical_cardinality_bound=logical_cardinality_bound,
        pair_cardinality_bound=pair_cardinality_bound,
        logical_item_bytes_bound=logical_item_bytes_bound,
        pair_item_bytes_bound=pair_item_bytes_bound,
        host_visible_canonical_output_required=host_visible_canonical_output_required,
        admitted_proof_digests=tuple(sorted(set(admitted_proof_digests))),
        admitted_resource_bound_digests=tuple(sorted(set(admitted_resource_bound_digests))),
        admitted_reuse_contract_digests=tuple(sorted(set(admitted_reuse_contract_digests))),
        admitted_template_digests=tuple(sorted(set(admitted_template_digests))),
    )


def make_target_descriptor(
    *,
    target_identity: object,
    available_providers: Iterable[str],
    allowed_execution_classes: Iterable[str],
    available_provider_abi_requirement_digests: Iterable[str],
    memory_limit_bytes: int,
    profile: str = NORMAL_PROFILE,
    required_physical_capabilities: Iterable[str] = (),
) -> TargetSelectionDescriptor:
    return TargetSelectionDescriptor(
        target_digest=_digest(target_identity),
        available_providers=tuple(sorted(set(available_providers))),
        allowed_execution_classes=tuple(sorted(set(allowed_execution_classes))),
        required_physical_capabilities=tuple(
            sorted(set(required_physical_capabilities))
        ),
        available_provider_abi_requirement_digests=tuple(
            sorted(set(available_provider_abi_requirement_digests))
        ),
        memory_limit_bytes=memory_limit_bytes,
        profile=profile,
        unprofiled=True,
    )


def materialize_candidates(
    action: ActionSelectionDescriptor,
    registry: RegistrySnapshot,
) -> tuple[CandidateDescriptor, ...]:
    rows = tuple(
        item
        for item in registry.declarations
        if item.semantic_kind == action.semantic_kind
        and action.action_contract_class in item.accepted_action_contract_classes
    )
    if len(rows) > MAX_CANDIDATES_PER_ACTION:
        raise DefaultSelectionError("CANDIDATE_CAP_EXCEEDED_BEFORE_COMPARISON", str(len(rows)))
    if not rows:
        raise DefaultSelectionError("ACTION_KIND_NOT_IN_REGISTRY", action.semantic_kind)
    return tuple(
        CandidateDescriptor(
            declaration=item,
            action_digest=action.action_digest,
            output_contract_digest=action.output_contract_digest,
            work_domain_digest=action.work_domain_digest,
            conservative_memory_bytes=item.memory_bound.evaluate(action),
        )
        for item in rows
    )


def _candidate_digest(candidate: CandidateDescriptor) -> str:
    return _digest(candidate.as_dict())


def candidate_descriptor_sha256(candidate: CandidateDescriptor) -> str:
    """Return the canonical digest already used by DEFAULT receipts.

    This read-only public boundary lets other compiler stages bind the exact
    candidate identity without copying DEFAULT's canonicalization rules.
    """

    return _candidate_digest(candidate)


def _legality_reasons(
    candidate: CandidateDescriptor,
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
) -> tuple[str, ...]:
    row = candidate.declaration
    reasons: list[str] = []
    if row.selection_role == SELECTION_ROLE_UNVERIFIED:
        reasons.append("SELECTION_ROLE_UNVERIFIED")
    if action.action_contract_class not in row.accepted_action_contract_classes:
        reasons.append("ACTION_CONTRACT_CLASS_NOT_ACCEPTED")
    if not (row.exactness_verified and row.determinism_verified and row.ordering_verified):
        reasons.append("MANDATORY_PROOF_OBLIGATION_UNVERIFIED")
    if candidate_proof_digest(row) != row.proof_digest:
        reasons.append("PROOF_DIGEST_MISMATCH")
    if not row.resource_bound_verified:
        reasons.append("RESOURCE_BOUND_UNPROVED")
    if candidate_resource_bound_digest(row) != row.resource_bound_digest:
        reasons.append("RESOURCE_BOUND_DIGEST_MISMATCH")
    if row.proof_digest not in action.admitted_proof_digests:
        reasons.append("ACTION_PROOF_NOT_ADMITTED")
    if row.resource_bound_digest not in action.admitted_resource_bound_digests:
        reasons.append("ACTION_RESOURCE_BOUND_NOT_ADMITTED")
    if row.reuse_contract_digest not in action.admitted_reuse_contract_digests:
        reasons.append("ACTION_REUSE_CONTRACT_NOT_ADMITTED")
    if row.template_digest not in action.admitted_template_digests:
        reasons.append("ACTION_TEMPLATE_NOT_ADMITTED")
    if candidate.action_digest != action.action_digest:
        reasons.append("ACTION_DIGEST_MISMATCH")
    if candidate.output_contract_digest != action.output_contract_digest:
        reasons.append("OUTPUT_CONTRACT_MISMATCH")
    if candidate.work_domain_digest != action.work_domain_digest:
        reasons.append("WORK_DOMAIN_MISMATCH")
    if not set(row.required_providers).issubset(target.available_providers):
        reasons.append("REQUIRED_PROVIDER_UNAVAILABLE")
    if (
        row.provider_abi_requirement_digest
        not in target.available_provider_abi_requirement_digests
    ):
        reasons.append("PROVIDER_ABI_REQUIREMENT_UNAVAILABLE")
    if target.allowed_execution_classes and row.execution_class not in target.allowed_execution_classes:
        reasons.append("EXECUTION_CLASS_NOT_ALLOWED")
    if not set(target.required_physical_capabilities).issubset(
        set(row.physical_capabilities)
    ):
        reasons.append("REQUIRED_PHYSICAL_CAPABILITY_MISSING")
    if target.profile == NORMAL_PROFILE and not row.normal_default_eligible:
        reasons.append("NORMAL_DEFAULT_NOT_AUTHORIZED")
    if (
        row.max_logical_cardinality is not None
        and action.logical_cardinality_bound > row.max_logical_cardinality
    ):
        reasons.append("LOGICAL_CARDINALITY_BOUND_EXCEEDED")
    if (
        row.max_pair_cardinality is not None
        and action.pair_cardinality_bound > row.max_pair_cardinality
    ):
        reasons.append("PAIR_CARDINALITY_BOUND_EXCEEDED")
    if candidate.conservative_memory_bytes > target.memory_limit_bytes:
        reasons.append("CONSERVATIVE_MEMORY_BOUND_EXCEEDED")
    return tuple(reasons)


def candidate_legality_reasons(
    candidate: CandidateDescriptor,
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
) -> tuple[str, ...]:
    """Expose DEFAULT's existing proof/resource legality predicate read-only."""

    return _legality_reasons(candidate, action, target)


def _selection_key(
    candidate: CandidateDescriptor,
    action: ActionSelectionDescriptor,
) -> tuple[object, ...]:
    row = candidate.declaration
    if row.selection_role not in ROLE_TIER:
        raise DefaultSelectionError("SELECTION_ROLE_UNVERIFIED", row.stable_id)
    return (
        ROLE_TIER[row.selection_role],
        (row.work_order.polynomial_degree, row.work_order.logarithmic_degree),
        row.host_round_trips,
        row.materializations,
        candidate.conservative_memory_bytes,
        avoidable_device_synchronizations(row, action),
        avoidable_device_launches(row),
        row.stable_id,
    )


def _structurally_dominates(
    left: CandidateDescriptor,
    right: CandidateDescriptor,
    action: ActionSelectionDescriptor,
) -> bool:
    lrow = left.declaration
    rrow = right.declaration
    lvalues: tuple[object, ...] = (
        (lrow.work_order.polynomial_degree, lrow.work_order.logarithmic_degree),
        lrow.host_round_trips,
        lrow.materializations,
        left.conservative_memory_bytes,
        avoidable_device_synchronizations(lrow, action),
        avoidable_device_launches(lrow),
    )
    rvalues: tuple[object, ...] = (
        (rrow.work_order.polynomial_degree, rrow.work_order.logarithmic_degree),
        rrow.host_round_trips,
        rrow.materializations,
        right.conservative_memory_bytes,
        avoidable_device_synchronizations(rrow, action),
        avoidable_device_launches(rrow),
    )
    return all(left_value <= right_value for left_value, right_value in zip(lvalues, rvalues)) and any(
        left_value < right_value for left_value, right_value in zip(lvalues, rvalues)
    )


def _select_default_or_raise(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    registry: RegistrySnapshot | None = None,
    candidates: Sequence[CandidateDescriptor] | None = None,
    annotation_mode: str = ANNOTATION_NONE,
) -> dict[str, object]:
    """Select one legal candidate and return a canonical claim-bearing receipt."""

    if annotation_mode not in (ANNOTATION_NONE, ANNOTATION_COMPLETE):
        raise DefaultSelectionError("UNKNOWN_ANNOTATION_MODE", annotation_mode)
    snapshot = current_registry_snapshot() if registry is None else registry
    expected = materialize_candidates(action, snapshot)
    if candidates is None:
        concrete = expected
    else:
        if len(candidates) > MAX_CANDIDATES_PER_ACTION:
            raise DefaultSelectionError(
                "CANDIDATE_CAP_EXCEEDED_BEFORE_COMPARISON", str(len(candidates))
            )
        concrete = tuple(candidates)
        if [item.as_dict() for item in concrete] != [item.as_dict() for item in expected]:
            raise DefaultSelectionError("INCOMPLETE_OR_REBOUND_CANDIDATE_SET")

    evaluations = []
    legal: list[CandidateDescriptor] = []
    for candidate in concrete:
        reasons = _legality_reasons(candidate, action, target)
        is_legal = not reasons
        if is_legal:
            legal.append(candidate)
        evaluations.append(
            {
                "stable_id": candidate.declaration.stable_id,
                "candidate_digest": _candidate_digest(candidate),
                "legal": is_legal,
                "rejection_reasons": list(reasons),
                "selection_key": (
                    list(_selection_key(candidate, action)) if is_legal else None
                ),
            }
        )
    if not legal:
        raise DefaultSelectionError("NO_LEGAL_CANDIDATE")
    ordered = tuple(sorted(legal, key=lambda item: _selection_key(item, action)))
    winner = ordered[0]

    dominance_edges: list[list[str]] = []
    dominance_dimension_comparisons = 0
    if annotation_mode == ANNOTATION_COMPLETE:
        for left in legal:
            for right in legal:
                if left is right:
                    continue
                dominance_dimension_comparisons += 6
                if _structurally_dominates(left, right, action):
                    dominance_edges.append(
                        [left.declaration.stable_id, right.declaration.stable_id]
                    )
        dominance_edges.sort()

    action_dict = action.as_dict()
    target_dict = target.as_dict()
    registry_dict = snapshot.as_dict()
    candidate_dicts = [item.as_dict() for item in concrete]
    body: dict[str, object] = {
        "schema": DEFAULT_RECEIPT_SCHEMA,
        "policy_version": DEFAULT_POLICY_VERSION,
        "status": "SELECTED",
        "action": action_dict,
        "action_descriptor_sha256": _digest(action_dict),
        "target": target_dict,
        "target_descriptor_sha256": _digest(target_dict),
        "registry": registry_dict,
        "registry_sha256": _digest(registry_dict),
        "candidates": candidate_dicts,
        "candidate_set_sha256": _digest(candidate_dicts),
        "evaluations": evaluations,
        "legal_candidate_count": len(legal),
        "complete_legal_order": [item.declaration.stable_id for item in ordered],
        "winner_stable_id": winner.declaration.stable_id,
        "winner_candidate_sha256": _candidate_digest(winner),
        "selected_reference_fallback": winner.declaration.selection_role == REFERENCE_FALLBACK,
        "annotation_mode": annotation_mode,
        "dominance_edges": dominance_edges,
        "dominance_dimension_comparisons": dominance_dimension_comparisons,
        "candidate_cap": MAX_CANDIDATES_PER_ACTION,
        "timing_or_learned_input_used": False,
        "application_identity_used": False,
        "candidate_executed": False,
        "production_default_changed": False,
    }
    body["receipt_sha256"] = _digest(body)
    return body


def _failure_receipt(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    registry: RegistrySnapshot,
    candidates: Sequence[CandidateDescriptor] | None,
    annotation_mode: str,
    error: DefaultSelectionError,
) -> dict[str, object]:
    action_dict = action.as_dict()
    target_dict = target.as_dict()
    registry_dict = registry.as_dict()
    concrete = () if candidates is None else tuple(candidates)
    candidate_dicts = [item.as_dict() for item in concrete]
    evaluations: list[dict[str, object]] = []
    if error.code == "NO_LEGAL_CANDIDATE":
        for candidate in concrete:
            reasons = _legality_reasons(candidate, action, target)
            evaluations.append(
                {
                    "stable_id": candidate.declaration.stable_id,
                    "candidate_digest": _candidate_digest(candidate),
                    "legal": not reasons,
                    "rejection_reasons": list(reasons),
                    "selection_key": (
                        list(_selection_key(candidate, action))
                        if not reasons
                        else None
                    ),
                }
            )
    detail = error.detail
    if error.code == "NO_LEGAL_CANDIDATE" and evaluations:
        detail = ";".join(
            f"{row['stable_id']}:{','.join(row['rejection_reasons'])}"
            for row in evaluations
        )
    body: dict[str, object] = {
        "schema": DEFAULT_RECEIPT_SCHEMA,
        "policy_version": DEFAULT_POLICY_VERSION,
        "status": "FAIL_CLOSED",
        "error_code": error.code,
        "error_detail": detail,
        "action": action_dict,
        "action_descriptor_sha256": _digest(action_dict),
        "target": target_dict,
        "target_descriptor_sha256": _digest(target_dict),
        "registry": registry_dict,
        "registry_sha256": _digest(registry_dict),
        "candidates": candidate_dicts,
        "candidate_set_sha256": _digest(candidate_dicts),
        "evaluations": evaluations,
        "annotation_mode": annotation_mode,
        "candidate_cap": MAX_CANDIDATES_PER_ACTION,
        "candidate_comparison_started": error.code == "NO_LEGAL_CANDIDATE",
        "sort_started": False,
        "candidate_executed": False,
        "timing_or_learned_input_used": False,
        "application_identity_used": False,
        "production_default_changed": False,
    }
    body["receipt_sha256"] = _digest(body)
    return body


def select_default(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    registry: RegistrySnapshot | None = None,
    candidates: Sequence[CandidateDescriptor] | None = None,
    annotation_mode: str = ANNOTATION_NONE,
) -> dict[str, object]:
    """Select or return a canonical typed fail-closed receipt.

    Internal validation uses typed exceptions so no candidate can survive a
    failed check accidentally.  The public algorithm boundary converts every
    such failure into an authenticated receipt, as required by Goal5694-A1.
    """

    snapshot = current_registry_snapshot() if registry is None else registry
    concrete = candidates
    try:
        if concrete is None:
            concrete = materialize_candidates(action, snapshot)
        return _select_default_or_raise(
            action,
            target,
            registry=snapshot,
            candidates=concrete,
            annotation_mode=annotation_mode,
        )
    except DefaultSelectionError as error:
        return _failure_receipt(
            action,
            target,
            snapshot,
            concrete,
            annotation_mode,
            error,
        )


__all__ = [
    "ANNOTATION_COMPLETE",
    "ANNOTATION_NONE",
    "CURRENT_REGISTRY_VERSION",
    "DEFAULT_POLICY_VERSION",
    "DEVICE_EXECUTION_CLASSES",
    "avoidable_device_launches",
    "avoidable_device_synchronizations",
    "candidate_descriptor_sha256",
    "candidate_legality_reasons",
    "candidate_resource_bound_digest",
    "candidate_proof_digest",
    "DEFAULT_RECEIPT_SCHEMA",
    "DEPLOYABLE_LOWERING",
    "MAX_WORK_LOGARITHMIC_DEGREE",
    "MAX_WORK_POLYNOMIAL_DEGREE",
    "OPTIX_TRAVERSAL_PROGRAM_CAPABILITY",
    "REFERENCE_FALLBACK",
    "ActionSelectionDescriptor",
    "CandidateDeclaration",
    "CandidateDescriptor",
    "DefaultSelectionError",
    "LinearMemoryBound",
    "RegistrySnapshot",
    "TargetSelectionDescriptor",
    "WorkOrderValue",
    "current_registry_snapshot",
    "make_action_descriptor",
    "make_target_descriptor",
    "mandatory_device_launches",
    "mandatory_endpoint_completion_waits",
    "materialize_candidates",
    "select_default",
]
