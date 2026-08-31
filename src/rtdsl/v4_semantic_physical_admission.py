"""App-neutral semantic-to-physical admission for V4 executable issuance.

This module is deliberately narrower than a planner.  It checks whether one
independently supplied semantic requirement is covered by one physical
guarantee, binds that judgment to live compiler identities, and requires one
and only one canonical candidate.  It neither discovers a plan nor estimates
performance.

The returned authority is process-local.  Its fields are evidence, not a
serialization format: reconstructing or unpickling an equal-looking object
does not enter the live-authority registry.  A family compiler must reverify
the authority against freshly derived live identities before it may issue an
executable.

This verifier proves compatibility of declarations.  The correctness of the
semantic specification and physical guarantee themselves remains in the
trusted computing base and must be supported separately by source/oracle
evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
import re
from typing import Mapping, Sequence
from weakref import WeakKeyDictionary


SEMANTIC_REQUIREMENT_SCHEMA = "rtdl.v4.semantic_requirement.v1"
PHYSICAL_GUARANTEE_SCHEMA = "rtdl.v4.physical_guarantee.v1"
LIVE_FAMILY_BINDING_SCHEMA = "rtdl.v4.live_family_binding.v1"
CANONICAL_CANDIDATE_SCHEMA = "rtdl.v4.canonical_candidate.v1"
ADMISSION_DECISION_SCHEMA = "rtdl.v4.semantic_physical_admission_decision.v1"
ADMISSION_AUTHORITY_SCHEMA = "rtdl.v4.semantic_physical_admission_authority.v1"
SEMANTIC_REQUIREMENT_AUTHORITY_SCHEMA = (
    "rtdl.v4.verified_semantic_requirement_authority.v1")
PHYSICAL_GUARANTEE_REGISTRY_SCHEMA = (
    "rtdl.v4.verified_physical_guarantee_registry.v1")
PHYSICAL_GUARANTEE_AUTHORITY_SCHEMA = (
    "rtdl.v4.verified_physical_guarantee_authority.v1")
COMPILER_PHYSICAL_REGISTRY_ISSUER_DOMAIN = (
    "rtdsl.compiler.physical_guarantee_registry.v1")
NO_ORIENTATION_CONTRACT_SHA256 = hashlib.sha256(
    b"rtdl.v4.orientation_contract.not_applicable.v1").hexdigest()

_SHA256 = re.compile(r"[0-9a-f]{64}")
_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)*")
_POLICY_KEYS = frozenset({
    "input_type",
    "output_type",
    "exactness",
    "tie_policy",
    "order_policy",
    "multiplicity",
    "numeric_precision",
    "overflow_policy",
})
_MAP_GRAPH = {
    "encode": (("semantic_input",), ("geometry", "query_state")),
    "ray": (("query_state",), ("ray",)),
    "trace": (("geometry", "ray"), ("hit_stream",)),
    "continuation": (("hit_stream",), ("candidate_output",)),
    "decode": (("candidate_output",), ("semantic_output",)),
}


class AdmissionVerdict(str, Enum):
    COMPATIBLE = "COMPATIBLE_FOR_DECLARED_DOMAIN"
    INCOMPATIBLE = "INCOMPATIBLE"
    UNKNOWN = "UNKNOWN"


class PhysicalEncodingEligibility(str, Enum):
    """Whether a registered encoding may participate in executable issuance."""

    CANONICAL_PRODUCTION = "CANONICAL_PRODUCTION"
    DIAGNOSTIC_NONREGISTRABLE = "DIAGNOSTIC_NONREGISTRABLE"


class AdmissionRuleId(str, Enum):
    """Stable public rule identifiers for diagnostics and tests."""

    MALFORMED_INPUT = "SP000_MALFORMED_INPUT"
    SEMANTIC_REQUIREMENT_UNKNOWN = "SP001_SEMANTIC_REQUIREMENT_UNKNOWN"
    PHYSICAL_GUARANTEE_UNKNOWN = "SP002_PHYSICAL_GUARANTEE_UNKNOWN"
    LIVE_BINDING_UNKNOWN = "SP003_LIVE_BINDING_UNKNOWN"
    CANONICAL_CANDIDATES_UNKNOWN = "SP004_CANONICAL_CANDIDATES_UNKNOWN"
    IDENTITY_INVALID = "SP010_IDENTITY_INVALID"
    DIGEST_INVALID = "SP011_DIGEST_INVALID"
    POLICY_INCOMPLETE = "SP020_POLICY_INCOMPLETE"
    POLICY_UNSUPPORTED_FIELD = "SP021_POLICY_UNSUPPORTED_FIELD"
    SEMANTIC_GUARANTEE_MISMATCH = "SP022_SEMANTIC_GUARANTEE_MISMATCH"
    REQUIRED_HIT_SEMANTIC_MISSING = "SP023_REQUIRED_HIT_SEMANTIC_MISSING"
    EXACTNESS_POLICY_MISMATCH = "SP024_EXACTNESS_POLICY_MISMATCH"
    TIE_POLICY_MISMATCH = "SP025_TIE_POLICY_MISMATCH"
    MULTIPLICITY_POLICY_MISMATCH = "SP026_MULTIPLICITY_POLICY_MISMATCH"
    OVERFLOW_POLICY_MISMATCH = "SP027_OVERFLOW_POLICY_MISMATCH"
    NUMERIC_PRECISION_POLICY_MISMATCH = (
        "SP028_NUMERIC_PRECISION_POLICY_MISMATCH")
    ORDER_POLICY_MISMATCH = "SP029_ORDER_POLICY_MISMATCH"
    MAP_STAGE_UNKNOWN = "SP030_MAP_STAGE_UNKNOWN"
    MAP_STAGE_DUPLICATE = "SP031_MAP_STAGE_DUPLICATE"
    MAP_GRAPH_MISMATCH = "SP032_MAP_GRAPH_MISMATCH"
    MAP_SOURCE_UNKNOWN = "SP033_MAP_SOURCE_UNKNOWN"
    MAP_SOURCE_DIGEST_MISMATCH = "SP034_MAP_SOURCE_DIGEST_MISMATCH"
    INPUT_TYPE_POLICY_MISMATCH = "SP035_INPUT_TYPE_POLICY_MISMATCH"
    OUTPUT_TYPE_POLICY_MISMATCH = "SP036_OUTPUT_TYPE_POLICY_MISMATCH"
    ALGORITHM_IDENTITY_MISMATCH = "SP037_ALGORITHM_IDENTITY_MISMATCH"
    DECLARED_DOMAIN_MISMATCH = "SP038_DECLARED_DOMAIN_MISMATCH"
    ORIENTATION_CONTRACT_MISMATCH = "SP039_ORIENTATION_CONTRACT_MISMATCH"
    GAS_CONTRACT_MISMATCH = "SP040_GAS_CONTRACT_MISMATCH"
    MAP_SOURCE_UNUSED = "SP041_MAP_SOURCE_UNUSED"
    CALLBACK_BINDING_MISMATCH = "SP050_CALLBACK_BINDING_MISMATCH"
    SCHEMA_BINDING_MISMATCH = "SP051_SCHEMA_BINDING_MISMATCH"
    TARGET_PROVIDER_MISMATCH = "SP052_TARGET_PROVIDER_MISMATCH"
    TARGET_CAPABILITY_MISSING = "SP053_TARGET_CAPABILITY_MISSING"
    CANONICAL_CANDIDATE_UNSUPPORTED = "SP060_CANONICAL_CANDIDATE_UNSUPPORTED"
    CANONICAL_CANDIDATE_AMBIGUOUS = "SP061_CANONICAL_CANDIDATE_AMBIGUOUS"
    CANONICAL_LIVE_BINDING_MISMATCH = "SP062_CANONICAL_LIVE_BINDING_MISMATCH"
    PHYSICAL_AUTHORITY_NONCANONICAL = "SP063_PHYSICAL_AUTHORITY_NONCANONICAL"
    AUTHORITY_NOT_LIVE = "SP070_AUTHORITY_NOT_LIVE"
    AUTHORITY_BINDING_DRIFT = "SP071_AUTHORITY_BINDING_DRIFT"


class SemanticPhysicalAdmissionError(ValueError):
    def __init__(self, code: str, path: str, message: str):
        super().__init__(f"{code} at {path}: {message}")
        self.code = code
        self.path = path
        self.message = message


@dataclass(frozen=True)
class AdmissionFinding:
    rule_id: AdmissionRuleId
    path: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id.value,
            "path": self.path,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class PhysicalMapEdgeV1:
    kind: str
    source_id: str
    source_sha256: str
    consumes: tuple[str, ...]
    produces: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "consumes": list(self.consumes),
            "produces": list(self.produces),
        }


@dataclass(frozen=True)
class SemanticRequirementV1:
    contract_id: str
    algorithm_identity: str
    declared_domain_sha256: str
    policy: tuple[tuple[str, str], ...]
    required_hit_semantics: tuple[str, ...]
    orientation_contract_sha256: str
    specification_source_sha256: str
    schema: str = SEMANTIC_REQUIREMENT_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "contract_id": self.contract_id,
            "algorithm_identity": self.algorithm_identity,
            "declared_domain_sha256": self.declared_domain_sha256,
            "policy": dict(self.policy),
            "required_hit_semantics": list(self.required_hit_semantics),
            "orientation_contract_sha256": self.orientation_contract_sha256,
            "specification_source_sha256": self.specification_source_sha256,
        }

    @property
    def requirement_sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True)
class PhysicalGuaranteeV1:
    encoding_id: str
    supported_algorithm_identity: str
    supported_domain_sha256: str
    orientation_contract_sha256: str
    geometry_family: str
    schema_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    guarantees: tuple[tuple[str, str], ...]
    maps: tuple[PhysicalMapEdgeV1, ...]
    hit_semantics: tuple[str, ...]
    gas_graph_depth: int
    gas_sbt_record_stride: int
    gas_update_policy: str
    buffer_contract_sha256: str
    required_target_capabilities: tuple[str, ...]
    source_manifest: tuple[tuple[str, str], ...]
    schema: str = PHYSICAL_GUARANTEE_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "encoding_id": self.encoding_id,
            "supported_algorithm_identity": self.supported_algorithm_identity,
            "supported_domain_sha256": self.supported_domain_sha256,
            "orientation_contract_sha256": self.orientation_contract_sha256,
            "geometry_family": self.geometry_family,
            "schema_sha256": self.schema_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "guarantees": dict(self.guarantees),
            "maps": [item.to_dict() for item in self.maps],
            "hit_semantics": list(self.hit_semantics),
            "gas_graph_depth": self.gas_graph_depth,
            "gas_sbt_record_stride": self.gas_sbt_record_stride,
            "gas_update_policy": self.gas_update_policy,
            "buffer_contract_sha256": self.buffer_contract_sha256,
            "required_target_capabilities": list(self.required_target_capabilities),
            "source_manifest": dict(self.source_manifest),
        }

    @property
    def guarantee_sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True, eq=False)
class VerifiedSemanticRequirementAuthority:
    """Process-local authority for one independently issued semantic request."""

    requirement: SemanticRequirementV1
    oracle_source_sha256: str
    issuer_domain: str
    authority_sha256: str
    authority_nonce: str
    schema: str = SEMANTIC_REQUIREMENT_AUTHORITY_SCHEMA

    def to_dict(self) -> dict[str, object]:
        """Return an inert evidence snapshot; it cannot recreate authority."""

        return {
            "schema": self.schema,
            "requirement": self.requirement.to_dict(),
            "oracle_source_sha256": self.oracle_source_sha256,
            "issuer_domain": self.issuer_domain,
            "authority_sha256": self.authority_sha256,
            "authority_nonce": self.authority_nonce,
        }

    def __reduce__(self):
        raise TypeError("semantic requirement authorities are process-local")

    def __reduce_ex__(self, protocol):
        del protocol
        raise TypeError("semantic requirement authorities are process-local")


@dataclass(frozen=True)
class PhysicalGuaranteeRegistryEntryV1:
    """Frozen compiler-classifier entry; inert without a live registry."""

    entry_id: str
    guarantee: PhysicalGuaranteeV1
    eligibility: PhysicalEncodingEligibility
    canonical_template_id: str | None
    classifier_source_sha256: str
    source_bytes_manifest_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_id": self.entry_id,
            "guarantee": self.guarantee.to_dict(),
            "eligibility": self.eligibility.value,
            "canonical_template_id": self.canonical_template_id,
            "classifier_source_sha256": self.classifier_source_sha256,
            "source_bytes_manifest_sha256": self.source_bytes_manifest_sha256,
        }

    @property
    def entry_sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True, eq=False)
class VerifiedPhysicalGuaranteeRegistryAuthority:
    """Live compiler-owned set of independently classified encodings."""

    entries: tuple[PhysicalGuaranteeRegistryEntryV1, ...]
    registry_source_sha256: str
    issuer_domain: str
    registry_sha256: str
    authority_nonce: str
    schema: str = PHYSICAL_GUARANTEE_REGISTRY_SCHEMA

    def to_dict(self) -> dict[str, object]:
        """Return the complete inert registry snapshot for independent audit."""

        return {
            "schema": self.schema,
            "entries": [entry.to_dict() for entry in self.entries],
            "registry_source_sha256": self.registry_source_sha256,
            "issuer_domain": self.issuer_domain,
            "registry_sha256": self.registry_sha256,
            "authority_nonce": self.authority_nonce,
        }

    def __reduce__(self):
        raise TypeError("physical guarantee registries are process-local")

    def __reduce_ex__(self, protocol):
        del protocol
        raise TypeError("physical guarantee registries are process-local")


@dataclass(frozen=True, eq=False)
class VerifiedPhysicalGuaranteeAuthority:
    """Live capability for one exact entry of a compiler-owned registry."""

    registry: VerifiedPhysicalGuaranteeRegistryAuthority
    entry: PhysicalGuaranteeRegistryEntryV1
    authority_sha256: str
    authority_nonce: str
    schema: str = PHYSICAL_GUARANTEE_AUTHORITY_SCHEMA

    @property
    def guarantee(self) -> PhysicalGuaranteeV1:
        return self.entry.guarantee

    @property
    def eligibility(self) -> PhysicalEncodingEligibility:
        return self.entry.eligibility

    def to_dict(self) -> dict[str, object]:
        """Return an inert audit record bound to the exact registry entry."""

        return {
            "schema": self.schema,
            "registry_sha256": self.registry.registry_sha256,
            "entry": self.entry.to_dict(),
            "entry_sha256": self.entry.entry_sha256,
            "authority_sha256": self.authority_sha256,
            "authority_nonce": self.authority_nonce,
        }

    def __reduce__(self):
        raise TypeError("physical guarantee authorities are process-local")

    def __reduce_ex__(self, protocol):
        del protocol
        raise TypeError("physical guarantee authorities are process-local")


@dataclass(frozen=True)
class LiveFamilyBindingV1:
    callback_ir_sha256: str
    effect_digest: str
    family_schema_sha256: str
    target_sha256: str
    target_provider: str
    target_capabilities: tuple[str, ...]
    canonical_artifact_sha256: str
    canonical_template_id: str
    family_authority_sha256: str
    family_authority_nonce: str
    schema: str = LIVE_FAMILY_BINDING_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "family_schema_sha256": self.family_schema_sha256,
            "target_sha256": self.target_sha256,
            "target_provider": self.target_provider,
            "target_capabilities": list(self.target_capabilities),
            "canonical_artifact_sha256": self.canonical_artifact_sha256,
            "canonical_template_id": self.canonical_template_id,
            "family_authority_sha256": self.family_authority_sha256,
            "family_authority_nonce": self.family_authority_nonce,
        }

    @property
    def binding_sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True)
class CanonicalCandidateV1:
    template_id: str
    canonical: bool
    algorithm_identity: str
    declared_domain_sha256: str
    orientation_contract_sha256: str
    geometry_family: str
    schema_sha256: str
    guarantees: tuple[tuple[str, str], ...]
    schema: str = CANONICAL_CANDIDATE_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "template_id": self.template_id,
            "canonical": self.canonical,
            "algorithm_identity": self.algorithm_identity,
            "declared_domain_sha256": self.declared_domain_sha256,
            "orientation_contract_sha256": self.orientation_contract_sha256,
            "geometry_family": self.geometry_family,
            "schema_sha256": self.schema_sha256,
            "guarantees": dict(self.guarantees),
        }


@dataclass(frozen=True)
class SemanticPhysicalAdmissionDecision:
    verdict: AdmissionVerdict
    findings: tuple[AdmissionFinding, ...]
    matching_candidate_count: int | None
    canonical_template_id: str | None
    schema: str = ADMISSION_DECISION_SCHEMA
    executable: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "verdict": self.verdict.value,
            "findings": [item.to_dict() for item in self.findings],
            "matching_candidate_count": self.matching_candidate_count,
            "canonical_template_id": self.canonical_template_id,
            "executable": self.executable,
        }

    @property
    def decision_sha256(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True, eq=False)
class VerifiedSemanticPhysicalAdmissionAuthority:
    semantic_authority: VerifiedSemanticRequirementAuthority
    physical_authority: VerifiedPhysicalGuaranteeAuthority
    live_binding: LiveFamilyBindingV1
    canonical_candidates: tuple[CanonicalCandidateV1, ...]
    canonical_template_id: str
    decision_sha256: str
    admission_sha256: str
    authority_nonce: str
    schema: str = ADMISSION_AUTHORITY_SCHEMA
    authorizes_executable_issuance: bool = True
    executable: bool = False

    @property
    def semantic_requirement(self) -> SemanticRequirementV1:
        return self.semantic_authority.requirement

    @property
    def physical_guarantee(self) -> PhysicalGuaranteeV1:
        return self.physical_authority.guarantee

    def __reduce__(self):
        raise TypeError("semantic-physical admission authorities are process-local")

    def __reduce_ex__(self, protocol):
        del protocol
        raise TypeError("semantic-physical admission authorities are process-local")


_LIVE_AUTHORITIES: WeakKeyDictionary[
    VerifiedSemanticPhysicalAdmissionAuthority, tuple[str, int]
] = WeakKeyDictionary()
_LIVE_SEMANTIC_AUTHORITIES: WeakKeyDictionary[
    VerifiedSemanticRequirementAuthority, tuple[str, int]
] = WeakKeyDictionary()
_LIVE_PHYSICAL_REGISTRIES: WeakKeyDictionary[
    VerifiedPhysicalGuaranteeRegistryAuthority, tuple[str, int]
] = WeakKeyDictionary()
_LIVE_PHYSICAL_AUTHORITIES: WeakKeyDictionary[
    VerifiedPhysicalGuaranteeAuthority, tuple[str, int]
] = WeakKeyDictionary()


SemanticInput = SemanticRequirementV1 | Mapping[str, object] | None
PhysicalInput = PhysicalGuaranteeV1 | Mapping[str, object] | None
BindingInput = LiveFamilyBindingV1 | Mapping[str, object] | None
CandidateInput = CanonicalCandidateV1 | Mapping[str, object]


def semantic_requirement_from_mapping(
    value: Mapping[str, object],
) -> SemanticRequirementV1:
    data = _exact_mapping(value, {
        "contract_id", "algorithm_identity", "declared_domain_sha256", "policy",
        "required_hit_semantics", "orientation_contract_sha256",
        "specification_source_sha256",
    }, "semantic_requirement")
    return SemanticRequirementV1(
        contract_id=_string(data["contract_id"], "semantic_requirement.contract_id"),
        algorithm_identity=_string(
            data["algorithm_identity"], "semantic_requirement.algorithm_identity"),
        declared_domain_sha256=_string(
            data["declared_domain_sha256"],
            "semantic_requirement.declared_domain_sha256"),
        policy=_string_map(data["policy"], "semantic_requirement.policy"),
        required_hit_semantics=_string_sequence(
            data["required_hit_semantics"],
            "semantic_requirement.required_hit_semantics"),
        orientation_contract_sha256=_string(
            data["orientation_contract_sha256"],
            "semantic_requirement.orientation_contract_sha256"),
        specification_source_sha256=_string(
            data["specification_source_sha256"],
            "semantic_requirement.specification_source_sha256"),
    )


def physical_guarantee_from_mapping(
    value: Mapping[str, object],
) -> PhysicalGuaranteeV1:
    data = _exact_mapping(value, {
        "encoding_id", "supported_algorithm_identity", "supported_domain_sha256",
        "orientation_contract_sha256", "geometry_family", "schema_sha256",
        "callback_ir_sha256",
        "effect_digest", "guarantees", "maps", "hit_semantics", "gas_graph_depth",
        "gas_sbt_record_stride", "gas_update_policy", "buffer_contract_sha256",
        "required_target_capabilities", "source_manifest",
    }, "physical_guarantee")
    raw_maps = _sequence(data["maps"], "physical_guarantee.maps")
    maps = tuple(_map_edge(item, index) for index, item in enumerate(raw_maps))
    return PhysicalGuaranteeV1(
        encoding_id=_string(data["encoding_id"], "physical_guarantee.encoding_id"),
        supported_algorithm_identity=_string(
            data["supported_algorithm_identity"],
            "physical_guarantee.supported_algorithm_identity"),
        supported_domain_sha256=_string(
            data["supported_domain_sha256"],
            "physical_guarantee.supported_domain_sha256"),
        orientation_contract_sha256=_string(
            data["orientation_contract_sha256"],
            "physical_guarantee.orientation_contract_sha256"),
        geometry_family=_string(
            data["geometry_family"], "physical_guarantee.geometry_family"),
        schema_sha256=_string(
            data["schema_sha256"], "physical_guarantee.schema_sha256"),
        callback_ir_sha256=_string(
            data["callback_ir_sha256"], "physical_guarantee.callback_ir_sha256"),
        effect_digest=_string(
            data["effect_digest"], "physical_guarantee.effect_digest"),
        guarantees=_string_map(data["guarantees"], "physical_guarantee.guarantees"),
        maps=maps,
        hit_semantics=_string_sequence(
            data["hit_semantics"], "physical_guarantee.hit_semantics"),
        gas_graph_depth=_plain_int(
            data["gas_graph_depth"], "physical_guarantee.gas_graph_depth"),
        gas_sbt_record_stride=_plain_int(
            data["gas_sbt_record_stride"],
            "physical_guarantee.gas_sbt_record_stride"),
        gas_update_policy=_string(
            data["gas_update_policy"], "physical_guarantee.gas_update_policy"),
        buffer_contract_sha256=_string(
            data["buffer_contract_sha256"],
            "physical_guarantee.buffer_contract_sha256"),
        required_target_capabilities=_string_sequence(
            data["required_target_capabilities"],
            "physical_guarantee.required_target_capabilities"),
        source_manifest=_string_map(
            data["source_manifest"], "physical_guarantee.source_manifest"),
    )


def live_family_binding_from_mapping(
    value: Mapping[str, object],
) -> LiveFamilyBindingV1:
    data = _exact_mapping(value, {
        "callback_ir_sha256", "effect_digest", "family_schema_sha256",
        "target_sha256", "target_provider", "target_capabilities",
        "canonical_artifact_sha256", "canonical_template_id",
        "family_authority_sha256", "family_authority_nonce",
    }, "live_binding")
    return LiveFamilyBindingV1(
        callback_ir_sha256=_string(
            data["callback_ir_sha256"], "live_binding.callback_ir_sha256"),
        effect_digest=_string(data["effect_digest"], "live_binding.effect_digest"),
        family_schema_sha256=_string(
            data["family_schema_sha256"], "live_binding.family_schema_sha256"),
        target_sha256=_string(data["target_sha256"], "live_binding.target_sha256"),
        target_provider=_string(data["target_provider"], "live_binding.target_provider"),
        target_capabilities=_string_sequence(
            data["target_capabilities"], "live_binding.target_capabilities"),
        canonical_artifact_sha256=_string(
            data["canonical_artifact_sha256"],
            "live_binding.canonical_artifact_sha256"),
        canonical_template_id=_string(
            data["canonical_template_id"], "live_binding.canonical_template_id"),
        family_authority_sha256=_string(
            data["family_authority_sha256"], "live_binding.family_authority_sha256"),
        family_authority_nonce=_string(
            data["family_authority_nonce"], "live_binding.family_authority_nonce"),
    )


def canonical_candidate_from_mapping(
    value: Mapping[str, object],
) -> CanonicalCandidateV1:
    data = _exact_mapping(value, {
        "template_id", "canonical", "algorithm_identity",
        "declared_domain_sha256", "orientation_contract_sha256",
        "geometry_family", "schema_sha256", "guarantees",
    }, "canonical_candidate")
    canonical = data["canonical"]
    if not isinstance(canonical, bool):
        _input_error("canonical_candidate.canonical", "expected bool")
    return CanonicalCandidateV1(
        template_id=_string(data["template_id"], "canonical_candidate.template_id"),
        canonical=canonical,
        algorithm_identity=_string(
            data["algorithm_identity"], "canonical_candidate.algorithm_identity"),
        declared_domain_sha256=_string(
            data["declared_domain_sha256"],
            "canonical_candidate.declared_domain_sha256"),
        orientation_contract_sha256=_string(
            data["orientation_contract_sha256"],
            "canonical_candidate.orientation_contract_sha256"),
        geometry_family=_string(
            data["geometry_family"], "canonical_candidate.geometry_family"),
        schema_sha256=_string(
            data["schema_sha256"], "canonical_candidate.schema_sha256"),
        guarantees=_string_map(data["guarantees"], "canonical_candidate.guarantees"),
    )


def issue_semantic_requirement_authority(
    semantic_requirement: SemanticRequirementV1 | Mapping[str, object],
    *,
    oracle_source_sha256: str,
    issuer_domain: str,
) -> VerifiedSemanticRequirementAuthority:
    """Issue one app-held semantic capability; it grants no physical authority."""

    requirement = _snapshot_semantic(semantic_requirement)
    assert requirement is not None
    unknown: list[AdmissionFinding] = []
    bad: list[AdmissionFinding] = []
    _validate_semantic(requirement, unknown, bad)
    if unknown or bad:
        finding = (unknown + bad)[0]
        raise SemanticPhysicalAdmissionError(
            finding.rule_id.value, finding.path, finding.detail)
    if not _is_sha(oracle_source_sha256):
        _input_error("semantic_authority.oracle_source_sha256", "expected sha256")
    if not _IDENTIFIER.fullmatch(issuer_domain):
        _input_error("semantic_authority.issuer_domain", "invalid issuer domain")
    payload = {
        "schema": SEMANTIC_REQUIREMENT_AUTHORITY_SCHEMA,
        "requirement_sha256": requirement.requirement_sha256,
        "specification_source_sha256": requirement.specification_source_sha256,
        "oracle_source_sha256": oracle_source_sha256,
        "issuer_domain": issuer_domain,
    }
    authority_sha = _digest(payload)
    nonce = _digest({"kind": SEMANTIC_REQUIREMENT_AUTHORITY_SCHEMA,
                     "authority_sha256": authority_sha})
    authority = VerifiedSemanticRequirementAuthority(
        requirement=requirement,
        oracle_source_sha256=oracle_source_sha256,
        issuer_domain=issuer_domain,
        authority_sha256=authority_sha,
        authority_nonce=nonce,
    )
    _LIVE_SEMANTIC_AUTHORITIES[authority] = _live_token(authority_sha)
    return authority


def reverify_semantic_requirement_authority(
    authority: VerifiedSemanticRequirementAuthority,
) -> VerifiedSemanticRequirementAuthority:
    if not isinstance(authority, VerifiedSemanticRequirementAuthority) \
            or _LIVE_SEMANTIC_AUTHORITIES.get(authority) \
            != _live_token(authority.authority_sha256):
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_NOT_LIVE.value,
            "semantic_authority",
            "expected the original process-local semantic authority",
        )
    payload = {
        "schema": SEMANTIC_REQUIREMENT_AUTHORITY_SCHEMA,
        "requirement_sha256": authority.requirement.requirement_sha256,
        "specification_source_sha256": (
            authority.requirement.specification_source_sha256),
        "oracle_source_sha256": authority.oracle_source_sha256,
        "issuer_domain": authority.issuer_domain,
    }
    authority_sha = _digest(payload)
    nonce = _digest({"kind": SEMANTIC_REQUIREMENT_AUTHORITY_SCHEMA,
                     "authority_sha256": authority_sha})
    if authority_sha != authority.authority_sha256 \
            or nonce != authority.authority_nonce:
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_BINDING_DRIFT.value,
            "semantic_authority",
            "semantic authority no longer rederives",
        )
    return authority


def physical_guarantee_registry_entry(
    entry_id: str,
    physical_guarantee: PhysicalGuaranteeV1 | Mapping[str, object],
    *,
    eligibility: PhysicalEncodingEligibility,
    canonical_template_id: str | None,
    classifier_source_sha256: str,
) -> PhysicalGuaranteeRegistryEntryV1:
    """Build inert registry data; only a compiler registry can make it trusted."""

    guarantee = _snapshot_physical(physical_guarantee)
    assert guarantee is not None
    if not isinstance(eligibility, PhysicalEncodingEligibility):
        _input_error("physical_registry_entry.eligibility", "expected eligibility")
    return PhysicalGuaranteeRegistryEntryV1(
        entry_id=entry_id,
        guarantee=guarantee,
        eligibility=eligibility,
        canonical_template_id=canonical_template_id,
        classifier_source_sha256=classifier_source_sha256,
        source_bytes_manifest_sha256=_digest(dict(guarantee.source_manifest)),
    )


def _issue_compiler_physical_guarantee_registry(
    entries: Sequence[PhysicalGuaranteeRegistryEntryV1],
    *,
    registry_source_sha256: str,
) -> VerifiedPhysicalGuaranteeRegistryAuthority:
    """Internal compiler capability issuer; never accepts an issuer name."""

    if not _is_sha(registry_source_sha256):
        _input_error("physical_registry.registry_source_sha256", "expected sha256")
    frozen_entries = tuple(entries)
    seen: set[str] = set()
    for index, entry in enumerate(frozen_entries):
        _validate_registry_entry(entry, index)
        if entry.entry_id in seen:
            _input_error("physical_registry.entries", "duplicate entry_id")
        seen.add(entry.entry_id)
    payload = {
        "schema": PHYSICAL_GUARANTEE_REGISTRY_SCHEMA,
        "issuer_domain": COMPILER_PHYSICAL_REGISTRY_ISSUER_DOMAIN,
        "registry_source_sha256": registry_source_sha256,
        "entries": [entry.to_dict() for entry in frozen_entries],
    }
    registry_sha = _digest(payload)
    nonce = _digest({"kind": PHYSICAL_GUARANTEE_REGISTRY_SCHEMA,
                     "registry_sha256": registry_sha})
    registry = VerifiedPhysicalGuaranteeRegistryAuthority(
        entries=frozen_entries,
        registry_source_sha256=registry_source_sha256,
        issuer_domain=COMPILER_PHYSICAL_REGISTRY_ISSUER_DOMAIN,
        registry_sha256=registry_sha,
        authority_nonce=nonce,
    )
    _LIVE_PHYSICAL_REGISTRIES[registry] = _live_token(registry_sha)
    return registry


def reverify_physical_guarantee_registry(
    registry: VerifiedPhysicalGuaranteeRegistryAuthority,
) -> VerifiedPhysicalGuaranteeRegistryAuthority:
    if not isinstance(registry, VerifiedPhysicalGuaranteeRegistryAuthority) \
            or _LIVE_PHYSICAL_REGISTRIES.get(registry) \
            != _live_token(registry.registry_sha256):
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_NOT_LIVE.value,
            "physical_registry",
            "expected the original compiler-owned registry",
        )
    for index, entry in enumerate(registry.entries):
        _validate_registry_entry(entry, index)
    payload = {
        "schema": PHYSICAL_GUARANTEE_REGISTRY_SCHEMA,
        "issuer_domain": registry.issuer_domain,
        "registry_source_sha256": registry.registry_source_sha256,
        "entries": [entry.to_dict() for entry in registry.entries],
    }
    registry_sha = _digest(payload)
    nonce = _digest({"kind": PHYSICAL_GUARANTEE_REGISTRY_SCHEMA,
                     "registry_sha256": registry_sha})
    if registry.issuer_domain != COMPILER_PHYSICAL_REGISTRY_ISSUER_DOMAIN \
            or registry_sha != registry.registry_sha256 \
            or nonce != registry.authority_nonce:
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_BINDING_DRIFT.value,
            "physical_registry",
            "registry no longer rederives",
        )
    return registry


def issue_registered_physical_guarantee_authority(
    registry: VerifiedPhysicalGuaranteeRegistryAuthority,
    entry_id: str,
) -> VerifiedPhysicalGuaranteeAuthority:
    registry = reverify_physical_guarantee_registry(registry)
    matching = tuple(entry for entry in registry.entries if entry.entry_id == entry_id)
    if len(matching) != 1:
        _input_error("physical_registry.entry_id", "expected one registered entry")
    entry = matching[0]
    payload = {
        "schema": PHYSICAL_GUARANTEE_AUTHORITY_SCHEMA,
        "registry_sha256": registry.registry_sha256,
        "entry_sha256": entry.entry_sha256,
        "entry_id": entry.entry_id,
        "eligibility": entry.eligibility.value,
    }
    authority_sha = _digest(payload)
    nonce = _digest({"kind": PHYSICAL_GUARANTEE_AUTHORITY_SCHEMA,
                     "authority_sha256": authority_sha,
                     "registry_nonce": registry.authority_nonce})
    authority = VerifiedPhysicalGuaranteeAuthority(
        registry=registry,
        entry=entry,
        authority_sha256=authority_sha,
        authority_nonce=nonce,
    )
    _LIVE_PHYSICAL_AUTHORITIES[authority] = _live_token(authority_sha)
    return authority


def reverify_registered_physical_guarantee_authority(
    authority: VerifiedPhysicalGuaranteeAuthority,
) -> VerifiedPhysicalGuaranteeAuthority:
    if not isinstance(authority, VerifiedPhysicalGuaranteeAuthority) \
            or _LIVE_PHYSICAL_AUTHORITIES.get(authority) \
            != _live_token(authority.authority_sha256):
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_NOT_LIVE.value,
            "physical_authority",
            "expected the original registered physical authority",
        )
    registry = reverify_physical_guarantee_registry(authority.registry)
    if not any(entry is authority.entry for entry in registry.entries):
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_BINDING_DRIFT.value,
            "physical_authority.entry",
            "entry is not the original registered object",
        )
    payload = {
        "schema": PHYSICAL_GUARANTEE_AUTHORITY_SCHEMA,
        "registry_sha256": registry.registry_sha256,
        "entry_sha256": authority.entry.entry_sha256,
        "entry_id": authority.entry.entry_id,
        "eligibility": authority.entry.eligibility.value,
    }
    authority_sha = _digest(payload)
    nonce = _digest({"kind": PHYSICAL_GUARANTEE_AUTHORITY_SCHEMA,
                     "authority_sha256": authority_sha,
                     "registry_nonce": registry.authority_nonce})
    if authority_sha != authority.authority_sha256 \
            or nonce != authority.authority_nonce:
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_BINDING_DRIFT.value,
            "physical_authority",
            "physical authority no longer rederives",
        )
    return authority


def canonical_candidates_from_registry(
    registry: VerifiedPhysicalGuaranteeRegistryAuthority,
    *,
    live_binding: LiveFamilyBindingV1,
    geometry_family: str,
) -> tuple[CanonicalCandidateV1, ...]:
    """Return the complete canonical set for exact live family identities."""

    registry = reverify_physical_guarantee_registry(registry)
    result: list[CanonicalCandidateV1] = []
    for entry in registry.entries:
        guarantee = entry.guarantee
        if entry.eligibility is not PhysicalEncodingEligibility.CANONICAL_PRODUCTION:
            continue
        if guarantee.callback_ir_sha256 != live_binding.callback_ir_sha256 \
                or guarantee.effect_digest != live_binding.effect_digest \
                or guarantee.schema_sha256 != live_binding.family_schema_sha256 \
                or guarantee.geometry_family != geometry_family \
                or not set(guarantee.required_target_capabilities) \
                <= set(live_binding.target_capabilities):
            continue
        assert entry.canonical_template_id is not None
        result.append(CanonicalCandidateV1(
            template_id=entry.canonical_template_id,
            canonical=True,
            algorithm_identity=guarantee.supported_algorithm_identity,
            declared_domain_sha256=guarantee.supported_domain_sha256,
            orientation_contract_sha256=guarantee.orientation_contract_sha256,
            geometry_family=guarantee.geometry_family,
            schema_sha256=guarantee.schema_sha256,
            guarantees=guarantee.guarantees,
        ))
    return tuple(result)


def evaluate_semantic_physical_admission(
    semantic_requirement: SemanticInput,
    physical_guarantee: PhysicalInput,
    *,
    live_binding: BindingInput,
    canonical_candidates: Sequence[CandidateInput] | None,
) -> SemanticPhysicalAdmissionDecision:
    """Return a three-valued inert judgment; never mint execution authority."""

    try:
        semantic = _snapshot_semantic(semantic_requirement)
        physical = _snapshot_physical(physical_guarantee)
        binding = _snapshot_binding(live_binding)
        candidates = _snapshot_candidates(canonical_candidates)
    except SemanticPhysicalAdmissionError as exc:
        finding = AdmissionFinding(
            AdmissionRuleId.MALFORMED_INPUT, exc.path, exc.message)
        return _decision(AdmissionVerdict.INCOMPATIBLE, (finding,), None, None)
    return _evaluate_snapshots(semantic, physical, binding, candidates)


def verify_semantic_physical_admission(
    semantic_authority: VerifiedSemanticRequirementAuthority,
    physical_authority: VerifiedPhysicalGuaranteeAuthority,
    *,
    live_binding: BindingInput,
) -> VerifiedSemanticPhysicalAdmissionAuthority:
    """Mint authority from live authorities and the complete compiler registry."""

    semantic_authority = reverify_semantic_requirement_authority(
        semantic_authority)
    physical_authority = reverify_registered_physical_guarantee_authority(
        physical_authority)
    semantic = semantic_authority.requirement
    physical = physical_authority.guarantee
    binding = _snapshot_binding(live_binding)
    candidates = (
        None if binding is None else canonical_candidates_from_registry(
            physical_authority.registry,
            live_binding=binding,
            geometry_family=physical.geometry_family,
        )
    )
    decision = _evaluate_snapshots(semantic, physical, binding, candidates)
    if decision.verdict is not AdmissionVerdict.COMPATIBLE:
        finding = decision.findings[0]
        raise SemanticPhysicalAdmissionError(
            finding.rule_id.value, finding.path, finding.detail)
    if physical_authority.eligibility \
            is not PhysicalEncodingEligibility.CANONICAL_PRODUCTION:
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.PHYSICAL_AUTHORITY_NONCANONICAL.value,
            "physical_authority.eligibility",
            "diagnostic physical encodings cannot authorize executables",
        )
    assert semantic is not None and physical is not None and binding is not None
    assert candidates is not None and decision.canonical_template_id is not None
    payload = _authority_payload(
        semantic_authority, physical_authority, binding, candidates,
        decision.canonical_template_id, decision.decision_sha256)
    admission_sha = _digest(payload)
    nonce = _digest({
        "kind": ADMISSION_AUTHORITY_SCHEMA,
        "admission_sha256": admission_sha,
        "family_authority_nonce": binding.family_authority_nonce,
    })
    authority = VerifiedSemanticPhysicalAdmissionAuthority(
        semantic_authority=semantic_authority,
        physical_authority=physical_authority,
        live_binding=binding,
        canonical_candidates=candidates,
        canonical_template_id=decision.canonical_template_id,
        decision_sha256=decision.decision_sha256,
        admission_sha256=admission_sha,
        authority_nonce=nonce,
    )
    _LIVE_AUTHORITIES[authority] = _live_token(admission_sha)
    return authority


def reverify_semantic_physical_admission(
    authority: VerifiedSemanticPhysicalAdmissionAuthority,
    semantic_authority: VerifiedSemanticRequirementAuthority,
    physical_authority: VerifiedPhysicalGuaranteeAuthority,
    *,
    live_binding: BindingInput,
) -> VerifiedSemanticPhysicalAdmissionAuthority:
    """Rebind one live authority to freshly derived compiler-side inputs."""

    if not isinstance(authority, VerifiedSemanticPhysicalAdmissionAuthority) \
            or _LIVE_AUTHORITIES.get(authority) \
            != _live_token(authority.admission_sha256):
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_NOT_LIVE.value,
            "authority",
            "expected the original process-local admission authority",
        )
    semantic_authority = reverify_semantic_requirement_authority(
        semantic_authority)
    physical_authority = reverify_registered_physical_guarantee_authority(
        physical_authority)
    if semantic_authority is not authority.semantic_authority \
            or physical_authority is not authority.physical_authority:
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_BINDING_DRIFT.value,
            "authority",
            "fresh semantic or physical authority is not the admitted object",
        )
    semantic = semantic_authority.requirement
    physical = physical_authority.guarantee
    binding = _snapshot_binding(live_binding)
    candidates = (
        None if binding is None else canonical_candidates_from_registry(
            physical_authority.registry,
            live_binding=binding,
            geometry_family=physical.geometry_family,
        )
    )
    decision = _evaluate_snapshots(semantic, physical, binding, candidates)
    if decision.verdict is not AdmissionVerdict.COMPATIBLE:
        finding = decision.findings[0]
        raise SemanticPhysicalAdmissionError(
            finding.rule_id.value, finding.path, finding.detail)
    if binding != authority.live_binding \
            or candidates != authority.canonical_candidates \
            or decision.canonical_template_id != authority.canonical_template_id:
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_BINDING_DRIFT.value,
            "authority",
            "fresh semantic, physical, live, or canonical identity differs",
        )
    payload = _authority_payload(
        semantic_authority, physical_authority, binding, candidates,
        authority.canonical_template_id, decision.decision_sha256)
    admission_sha = _digest(payload)
    nonce = _digest({
        "kind": ADMISSION_AUTHORITY_SCHEMA,
        "admission_sha256": admission_sha,
        "family_authority_nonce": binding.family_authority_nonce,
    })
    if admission_sha != authority.admission_sha256 \
            or decision.decision_sha256 != authority.decision_sha256 \
            or nonce != authority.authority_nonce:
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_BINDING_DRIFT.value,
            "authority",
            "authority digest or nonce does not rederive",
        )
    return authority


def _evaluate_snapshots(
    semantic: SemanticRequirementV1 | None,
    physical: PhysicalGuaranteeV1 | None,
    binding: LiveFamilyBindingV1 | None,
    candidates: tuple[CanonicalCandidateV1, ...] | None,
) -> SemanticPhysicalAdmissionDecision:
    unknown: list[AdmissionFinding] = []
    bad: list[AdmissionFinding] = []

    if semantic is None:
        unknown.append(_finding(
            AdmissionRuleId.SEMANTIC_REQUIREMENT_UNKNOWN,
            "semantic_requirement", "independent semantic requirement is absent"))
    if physical is None:
        unknown.append(_finding(
            AdmissionRuleId.PHYSICAL_GUARANTEE_UNKNOWN,
            "physical_guarantee", "physical guarantee is absent"))
    if binding is None:
        unknown.append(_finding(
            AdmissionRuleId.LIVE_BINDING_UNKNOWN,
            "live_binding", "live compiler binding is absent"))
    if candidates is None:
        unknown.append(_finding(
            AdmissionRuleId.CANONICAL_CANDIDATES_UNKNOWN,
            "canonical_candidates", "compiler candidate registry is absent"))

    if semantic is not None:
        _validate_semantic(semantic, unknown, bad)
    if physical is not None:
        _validate_physical(physical, unknown, bad)
    if binding is not None:
        _validate_binding(binding, bad)

    if semantic is not None and physical is not None:
        semantic_policy = dict(semantic.policy)
        physical_policy = dict(physical.guarantees)
        _compare_policy(semantic_policy, physical_policy, bad)
        if semantic.algorithm_identity != physical.supported_algorithm_identity:
            bad.append(_finding(
                AdmissionRuleId.ALGORITHM_IDENTITY_MISMATCH,
                "physical_guarantee.supported_algorithm_identity",
                f"physical={physical.supported_algorithm_identity!r} "
                f"semantic={semantic.algorithm_identity!r}",
            ))
        if semantic.declared_domain_sha256 != physical.supported_domain_sha256:
            bad.append(_finding(
                AdmissionRuleId.DECLARED_DOMAIN_MISMATCH,
                "physical_guarantee.supported_domain_sha256",
                f"physical={physical.supported_domain_sha256!r} "
                f"semantic={semantic.declared_domain_sha256!r}",
            ))
        if semantic.orientation_contract_sha256 \
                != physical.orientation_contract_sha256:
            bad.append(_finding(
                AdmissionRuleId.ORIENTATION_CONTRACT_MISMATCH,
                "physical_guarantee.orientation_contract_sha256",
                f"physical={physical.orientation_contract_sha256!r} "
                f"semantic={semantic.orientation_contract_sha256!r}",
            ))
        missing_hits = sorted(
            set(semantic.required_hit_semantics) - set(physical.hit_semantics))
        if missing_hits:
            bad.append(_finding(
                AdmissionRuleId.REQUIRED_HIT_SEMANTIC_MISSING,
                "physical_guarantee.hit_semantics", repr(missing_hits)))

    if physical is not None and binding is not None:
        if physical.callback_ir_sha256 != binding.callback_ir_sha256 \
                or physical.effect_digest != binding.effect_digest:
            bad.append(_finding(
                AdmissionRuleId.CALLBACK_BINDING_MISMATCH,
                "live_binding", "callback IR or effect digest differs"))
        if physical.schema_sha256 != binding.family_schema_sha256:
            bad.append(_finding(
                AdmissionRuleId.SCHEMA_BINDING_MISMATCH,
                "live_binding.family_schema_sha256",
                "live family schema differs from the physical guarantee"))
        if binding.target_provider != "optix":
            bad.append(_finding(
                AdmissionRuleId.TARGET_PROVIDER_MISMATCH,
                "live_binding.target_provider", binding.target_provider))
        missing_caps = sorted(
            set(physical.required_target_capabilities)
            - set(binding.target_capabilities))
        if missing_caps:
            bad.append(_finding(
                AdmissionRuleId.TARGET_CAPABILITY_MISSING,
                "live_binding.target_capabilities", repr(missing_caps)))

    matching: list[CanonicalCandidateV1] = []
    if candidates is not None and semantic is not None and physical is not None:
        for candidate in candidates:
            _validate_candidate(candidate, bad)
            if candidate.canonical \
                    and candidate.algorithm_identity == semantic.algorithm_identity \
                    and candidate.declared_domain_sha256 \
                    == semantic.declared_domain_sha256 \
                    and candidate.orientation_contract_sha256 \
                    == semantic.orientation_contract_sha256 \
                    and candidate.geometry_family == physical.geometry_family \
                    and candidate.schema_sha256 == physical.schema_sha256 \
                    and dict(candidate.guarantees) == dict(semantic.policy):
                matching.append(candidate)
        if not matching:
            bad.append(_finding(
                AdmissionRuleId.CANONICAL_CANDIDATE_UNSUPPORTED,
                "canonical_candidates", "zero canonical matches"))
        elif len(matching) > 1:
            bad.append(_finding(
                AdmissionRuleId.CANONICAL_CANDIDATE_AMBIGUOUS,
                "canonical_candidates", f"{len(matching)} canonical matches"))
        elif binding is not None \
                and matching[0].template_id != binding.canonical_template_id:
            bad.append(_finding(
                AdmissionRuleId.CANONICAL_LIVE_BINDING_MISMATCH,
                "live_binding.canonical_template_id",
                "live compiler selected another canonical template"))

    template_id = matching[0].template_id if len(matching) == 1 else None
    count = None if candidates is None else len(matching)
    if unknown:
        return _decision(
            AdmissionVerdict.UNKNOWN, tuple(unknown + bad), count, template_id)
    if bad:
        return _decision(AdmissionVerdict.INCOMPATIBLE, tuple(bad), count, template_id)
    return _decision(AdmissionVerdict.COMPATIBLE, (), count, template_id)


def _validate_semantic(value, unknown, bad) -> None:
    if value.schema != SEMANTIC_REQUIREMENT_SCHEMA \
            or not _IDENTIFIER.fullmatch(value.contract_id) \
            or not _IDENTIFIER.fullmatch(value.algorithm_identity):
        bad.append(_finding(
            AdmissionRuleId.IDENTITY_INVALID, "semantic_requirement",
            "schema, contract, or algorithm identity is invalid"))
    for path, digest_value in (
        ("declared_domain_sha256", value.declared_domain_sha256),
        ("orientation_contract_sha256", value.orientation_contract_sha256),
        ("specification_source_sha256", value.specification_source_sha256),
    ):
        if not _is_sha(digest_value):
            bad.append(_finding(
                AdmissionRuleId.DIGEST_INVALID,
                "semantic_requirement." + path, digest_value))
    _validate_policy(dict(value.policy), "semantic_requirement.policy", unknown, bad)


def _validate_physical(value, unknown, bad) -> None:
    if value.schema != PHYSICAL_GUARANTEE_SCHEMA \
            or not _IDENTIFIER.fullmatch(value.encoding_id) \
            or not _IDENTIFIER.fullmatch(value.supported_algorithm_identity) \
            or not _IDENTIFIER.fullmatch(value.geometry_family):
        bad.append(_finding(
            AdmissionRuleId.IDENTITY_INVALID, "physical_guarantee",
            "schema, encoding, or geometry identity is invalid"))
    for path, digest_value in (
        ("supported_domain_sha256", value.supported_domain_sha256),
        ("orientation_contract_sha256", value.orientation_contract_sha256),
        ("schema_sha256", value.schema_sha256),
        ("callback_ir_sha256", value.callback_ir_sha256),
        ("effect_digest", value.effect_digest),
        ("buffer_contract_sha256", value.buffer_contract_sha256),
    ):
        if not _is_sha(digest_value):
            bad.append(_finding(
                AdmissionRuleId.DIGEST_INVALID,
                "physical_guarantee." + path, digest_value))
    _validate_policy(dict(value.guarantees), "physical_guarantee.guarantees", unknown, bad)
    if value.gas_graph_depth != 1 or value.gas_sbt_record_stride != 1 \
            or value.gas_update_policy not in {"static", "declared_refit"}:
        bad.append(_finding(
            AdmissionRuleId.GAS_CONTRACT_MISMATCH,
            "physical_guarantee.gas", "only depth=1, stride=1, static/refit is admitted"))
    manifest = dict(value.source_manifest)
    for source_id, source_sha256 in manifest.items():
        if not source_id or not _is_sha(source_sha256):
            bad.append(_finding(
                AdmissionRuleId.DIGEST_INVALID,
                f"physical_guarantee.source_manifest.{source_id}",
                source_sha256,
            ))
    by_kind: dict[str, PhysicalMapEdgeV1] = {}
    for edge in value.maps:
        if not _is_sha(edge.source_sha256):
            bad.append(_finding(
                AdmissionRuleId.DIGEST_INVALID,
                f"physical_guarantee.maps.{edge.kind}.source_sha256",
                edge.source_sha256,
            ))
        if edge.kind not in _MAP_GRAPH:
            bad.append(_finding(
                AdmissionRuleId.MAP_GRAPH_MISMATCH,
                "physical_guarantee.maps", f"unknown stage {edge.kind!r}"))
            continue
        if edge.kind in by_kind:
            bad.append(_finding(
                AdmissionRuleId.MAP_STAGE_DUPLICATE,
                "physical_guarantee.maps", edge.kind))
            continue
        by_kind[edge.kind] = edge
        expected = _MAP_GRAPH[edge.kind]
        if edge.consumes != expected[0] or edge.produces != expected[1]:
            bad.append(_finding(
                AdmissionRuleId.MAP_GRAPH_MISMATCH,
                f"physical_guarantee.maps.{edge.kind}",
                "consume/produce edge differs from the closed graph"))
        authoritative = manifest.get(edge.source_id)
        if authoritative is None:
            unknown.append(_finding(
                AdmissionRuleId.MAP_SOURCE_UNKNOWN,
                f"physical_guarantee.maps.{edge.kind}.source_id", edge.source_id))
        elif authoritative != edge.source_sha256:
            bad.append(_finding(
                AdmissionRuleId.MAP_SOURCE_DIGEST_MISMATCH,
                f"physical_guarantee.maps.{edge.kind}.source_sha256",
                edge.source_sha256))
    for kind in sorted(set(_MAP_GRAPH) - set(by_kind)):
        unknown.append(_finding(
            AdmissionRuleId.MAP_STAGE_UNKNOWN,
            "physical_guarantee.maps", f"missing {kind}"))
    unused_sources = sorted(
        set(manifest) - {edge.source_id for edge in value.maps})
    if unused_sources:
        bad.append(_finding(
            AdmissionRuleId.MAP_SOURCE_UNUSED,
            "physical_guarantee.source_manifest",
            repr(unused_sources),
        ))


def _validate_binding(value, bad) -> None:
    if value.schema != LIVE_FAMILY_BINDING_SCHEMA \
            or not _IDENTIFIER.fullmatch(value.canonical_template_id):
        bad.append(_finding(
            AdmissionRuleId.IDENTITY_INVALID, "live_binding",
            "schema or canonical template identity is invalid"))
    for path in (
        "callback_ir_sha256", "effect_digest", "family_schema_sha256",
        "target_sha256", "canonical_artifact_sha256", "family_authority_sha256",
    ):
        digest_value = getattr(value, path)
        if not _is_sha(digest_value):
            bad.append(_finding(
                AdmissionRuleId.DIGEST_INVALID, "live_binding." + path, digest_value))
    if not value.family_authority_nonce:
        bad.append(_finding(
            AdmissionRuleId.IDENTITY_INVALID,
            "live_binding.family_authority_nonce", "empty nonce"))


def _validate_candidate(value, bad) -> None:
    if value.schema != CANONICAL_CANDIDATE_SCHEMA \
            or not _IDENTIFIER.fullmatch(value.template_id):
        bad.append(_finding(
            AdmissionRuleId.IDENTITY_INVALID,
            "canonical_candidate", "schema or template identity is invalid"))
    if not _is_sha(value.schema_sha256):
        bad.append(_finding(
            AdmissionRuleId.DIGEST_INVALID,
            "canonical_candidate.schema_sha256", value.schema_sha256))
    if not _is_sha(value.declared_domain_sha256):
        bad.append(_finding(
            AdmissionRuleId.DIGEST_INVALID,
            "canonical_candidate.declared_domain_sha256",
            value.declared_domain_sha256))
    if not _is_sha(value.orientation_contract_sha256):
        bad.append(_finding(
            AdmissionRuleId.DIGEST_INVALID,
            "canonical_candidate.orientation_contract_sha256",
            value.orientation_contract_sha256))


def _validate_registry_entry(
    entry: PhysicalGuaranteeRegistryEntryV1,
    index: int,
) -> None:
    path = f"physical_registry.entries[{index}]"
    if not isinstance(entry, PhysicalGuaranteeRegistryEntryV1):
        _input_error(path, "expected PhysicalGuaranteeRegistryEntryV1")
    if not _IDENTIFIER.fullmatch(entry.entry_id):
        _input_error(path + ".entry_id", "invalid entry identity")
    if not _is_sha(entry.classifier_source_sha256):
        _input_error(path + ".classifier_source_sha256", "expected sha256")
    if not _is_sha(entry.source_bytes_manifest_sha256):
        _input_error(path + ".source_bytes_manifest_sha256", "expected sha256")
    if entry.source_bytes_manifest_sha256 \
            != _digest(dict(entry.guarantee.source_manifest)):
        raise SemanticPhysicalAdmissionError(
            AdmissionRuleId.AUTHORITY_BINDING_DRIFT.value,
            path + ".source_bytes_manifest_sha256",
            "registered source manifest no longer rederives",
        )
    if entry.eligibility is PhysicalEncodingEligibility.CANONICAL_PRODUCTION:
        if entry.canonical_template_id is None \
                or not _IDENTIFIER.fullmatch(entry.canonical_template_id):
            _input_error(path + ".canonical_template_id", "canonical template required")
    elif entry.eligibility is PhysicalEncodingEligibility.DIAGNOSTIC_NONREGISTRABLE:
        if entry.canonical_template_id is not None:
            _input_error(
                path + ".canonical_template_id",
                "diagnostic entries cannot name a canonical template",
            )
    else:
        _input_error(path + ".eligibility", "unsupported eligibility")
    unknown: list[AdmissionFinding] = []
    bad: list[AdmissionFinding] = []
    _validate_physical(entry.guarantee, unknown, bad)
    if unknown or bad:
        finding = (unknown + bad)[0]
        raise SemanticPhysicalAdmissionError(
            finding.rule_id.value, finding.path, finding.detail)


def _validate_policy(value, path, unknown, bad) -> None:
    missing = sorted(_POLICY_KEYS - set(value))
    extra = sorted(set(value) - _POLICY_KEYS)
    if missing:
        unknown.append(_finding(
            AdmissionRuleId.POLICY_INCOMPLETE, path, repr(missing)))
    if extra:
        bad.append(_finding(
            AdmissionRuleId.POLICY_UNSUPPORTED_FIELD, path, repr(extra)))


def _compare_policy(semantic, physical, bad) -> None:
    rules = {
        "input_type": AdmissionRuleId.INPUT_TYPE_POLICY_MISMATCH,
        "output_type": AdmissionRuleId.OUTPUT_TYPE_POLICY_MISMATCH,
        "exactness": AdmissionRuleId.EXACTNESS_POLICY_MISMATCH,
        "tie_policy": AdmissionRuleId.TIE_POLICY_MISMATCH,
        "multiplicity": AdmissionRuleId.MULTIPLICITY_POLICY_MISMATCH,
        "overflow_policy": AdmissionRuleId.OVERFLOW_POLICY_MISMATCH,
        "numeric_precision": AdmissionRuleId.NUMERIC_PRECISION_POLICY_MISMATCH,
        "order_policy": AdmissionRuleId.ORDER_POLICY_MISMATCH,
    }
    for key in sorted(_POLICY_KEYS):
        if key in semantic and key in physical and semantic[key] != physical[key]:
            bad.append(_finding(
                rules.get(key, AdmissionRuleId.SEMANTIC_GUARANTEE_MISMATCH),
                f"physical_guarantee.guarantees.{key}",
                f"physical={physical[key]!r} semantic={semantic[key]!r}",
            ))


def _decision(verdict, findings, count, template_id):
    return SemanticPhysicalAdmissionDecision(
        verdict=verdict,
        findings=tuple(findings),
        matching_candidate_count=count,
        canonical_template_id=template_id,
    )


def _authority_payload(
    semantic_authority, physical_authority, binding, candidates,
    template_id, decision_sha,
):
    return {
        "schema": ADMISSION_AUTHORITY_SCHEMA,
        "semantic_authority_sha256": semantic_authority.authority_sha256,
        "semantic_requirement_sha256": (
            semantic_authority.requirement.requirement_sha256),
        "physical_authority_sha256": physical_authority.authority_sha256,
        "physical_registry_sha256": (
            physical_authority.registry.registry_sha256),
        "physical_guarantee_sha256": (
            physical_authority.guarantee.guarantee_sha256),
        "live_binding_sha256": binding.binding_sha256,
        "canonical_candidate_set_sha256": _digest(
            [item.to_dict() for item in candidates]),
        "canonical_template_id": template_id,
        "decision_sha256": decision_sha,
        "authorizes_executable_issuance": True,
        "executable": False,
    }


def _snapshot_semantic(value):
    if value is None:
        return None
    if isinstance(value, SemanticRequirementV1):
        return semantic_requirement_from_mapping(_semantic_mapping(value))
    if isinstance(value, Mapping):
        return semantic_requirement_from_mapping(value)
    _input_error("semantic_requirement", f"unexpected {type(value).__name__}")


def _snapshot_physical(value):
    if value is None:
        return None
    if isinstance(value, PhysicalGuaranteeV1):
        return physical_guarantee_from_mapping(_physical_mapping(value))
    if isinstance(value, Mapping):
        return physical_guarantee_from_mapping(value)
    _input_error("physical_guarantee", f"unexpected {type(value).__name__}")


def _snapshot_binding(value):
    if value is None:
        return None
    if isinstance(value, LiveFamilyBindingV1):
        return live_family_binding_from_mapping(_binding_mapping(value))
    if isinstance(value, Mapping):
        return live_family_binding_from_mapping(value)
    _input_error("live_binding", f"unexpected {type(value).__name__}")


def _snapshot_candidates(value):
    if value is None:
        return None
    if isinstance(value, (str, bytes)):
        _input_error("canonical_candidates", "expected a sequence of candidates")
    result = []
    for index, candidate in enumerate(value):
        if isinstance(candidate, CanonicalCandidateV1):
            result.append(canonical_candidate_from_mapping(_candidate_mapping(candidate)))
        elif isinstance(candidate, Mapping):
            result.append(canonical_candidate_from_mapping(candidate))
        else:
            _input_error(
                f"canonical_candidates[{index}]",
                f"unexpected {type(candidate).__name__}")
    return tuple(result)


def _semantic_mapping(value):
    result = value.to_dict()
    result.pop("schema")
    return result


def _physical_mapping(value):
    result = value.to_dict()
    result.pop("schema")
    return result


def _binding_mapping(value):
    result = value.to_dict()
    result.pop("schema")
    return result


def _candidate_mapping(value):
    result = value.to_dict()
    result.pop("schema")
    return result


def _map_edge(value, index):
    data = _exact_mapping(value, {
        "kind", "source_id", "source_sha256", "consumes", "produces",
    }, f"physical_guarantee.maps[{index}]")
    return PhysicalMapEdgeV1(
        kind=_string(data["kind"], f"physical_guarantee.maps[{index}].kind"),
        source_id=_string(
            data["source_id"], f"physical_guarantee.maps[{index}].source_id"),
        source_sha256=_string(
            data["source_sha256"],
            f"physical_guarantee.maps[{index}].source_sha256"),
        consumes=_string_sequence(
            data["consumes"], f"physical_guarantee.maps[{index}].consumes"),
        produces=_string_sequence(
            data["produces"], f"physical_guarantee.maps[{index}].produces"),
    )


def _exact_mapping(value, keys, path):
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        _input_error(path, "expected a string-keyed mapping")
    if set(value) != keys:
        _input_error(path, f"field delta {sorted(set(value) ^ keys)!r}")
    return dict(value)


def _string_map(value, path):
    if not isinstance(value, Mapping) or any(
            not isinstance(key, str) or not isinstance(item, str)
            for key, item in value.items()):
        _input_error(path, "expected string-to-string mapping")
    return tuple(sorted((str(key), str(item)) for key, item in value.items()))


def _string_sequence(value, path):
    rows = _sequence(value, path)
    if any(not isinstance(item, str) or not item for item in rows):
        _input_error(path, "expected nonempty strings")
    if len(set(rows)) != len(rows):
        _input_error(path, "duplicate string")
    return tuple(rows)


def _sequence(value, path):
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        _input_error(path, "expected sequence")
    return list(value)


def _string(value, path):
    if not isinstance(value, str) or not value:
        _input_error(path, "expected nonempty string")
    return value


def _plain_int(value, path):
    if not isinstance(value, int) or isinstance(value, bool):
        _input_error(path, "expected integer")
    return value


def _input_error(path, message):
    raise SemanticPhysicalAdmissionError(
        AdmissionRuleId.MALFORMED_INPUT.value, path, message)


def _finding(rule_id, path, detail):
    return AdmissionFinding(rule_id, path, detail)


def _is_sha(value):
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _live_token(identity_sha256: str) -> tuple[str, int]:
    """Bind live capabilities to the exact process, including across fork."""

    return identity_sha256, os.getpid()


__all__ = [
    "AdmissionFinding",
    "AdmissionRuleId",
    "AdmissionVerdict",
    "CanonicalCandidateV1",
    "LiveFamilyBindingV1",
    "NO_ORIENTATION_CONTRACT_SHA256",
    "PhysicalEncodingEligibility",
    "PhysicalGuaranteeV1",
    "PhysicalGuaranteeRegistryEntryV1",
    "PhysicalMapEdgeV1",
    "SemanticPhysicalAdmissionDecision",
    "SemanticPhysicalAdmissionError",
    "SemanticRequirementV1",
    "VerifiedPhysicalGuaranteeAuthority",
    "VerifiedPhysicalGuaranteeRegistryAuthority",
    "VerifiedSemanticRequirementAuthority",
    "VerifiedSemanticPhysicalAdmissionAuthority",
    "canonical_candidate_from_mapping",
    "canonical_candidates_from_registry",
    "evaluate_semantic_physical_admission",
    "issue_registered_physical_guarantee_authority",
    "issue_semantic_requirement_authority",
    "live_family_binding_from_mapping",
    "physical_guarantee_registry_entry",
    "physical_guarantee_from_mapping",
    "reverify_physical_guarantee_registry",
    "reverify_registered_physical_guarantee_authority",
    "reverify_semantic_requirement_authority",
    "semantic_requirement_from_mapping",
]
