"""Whole-callback protocol contract gate used by the bounded V4 lifecycle.

The ordinary Callback IR verifier checks individual callback programs.  This
module checks the remaining seam between the application declaration and the
compiler/runtime projection: cross-role effects, payload/attribute ownership,
physical field projection, status/continuation policy, and the exact generated
executable.  It does not execute an application and it cannot turn a failed
decision into an executable capability.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Mapping, Sequence


_SHA256 = re.compile(r"[0-9a-f]{64}")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


class ProtocolMechanism(str, Enum):
    ROLE_EFFECT_CLOSURE = "role_effect_closure"
    PAYLOAD_ATTRIBUTE_ABI_OWNERSHIP = "payload_attribute_abi_ownership"
    PHYSICAL_GEOMETRY_BINDING = "physical_geometry_binding"
    DEVICE_STATUS_CONTINUATION = "device_status_continuation"
    CHECKED_PROGRAM_EXECUTABLE_IDENTITY = "checked_program_executable_identity"


_REASON_BY_MECHANISM = {
    ProtocolMechanism.ROLE_EFFECT_CLOSURE: "CP001_ROLE_EFFECT_MISMATCH",
    ProtocolMechanism.PAYLOAD_ATTRIBUTE_ABI_OWNERSHIP:
        "CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH",
    ProtocolMechanism.PHYSICAL_GEOMETRY_BINDING:
        "CP003_PHYSICAL_BINDING_MISMATCH",
    ProtocolMechanism.DEVICE_STATUS_CONTINUATION:
        "CP004_CONTINUATION_STATUS_MISMATCH",
    ProtocolMechanism.CHECKED_PROGRAM_EXECUTABLE_IDENTITY:
        "CP005_EXECUTABLE_IDENTITY_MISMATCH",
}


class ProtocolContractError(ValueError):
    """Malformed protocol declaration or compiler projection."""


def _nonempty(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProtocolContractError(f"CP000_SCHEMA_INVALID@{path}: nonempty string required")
    return value


def _sha(value: object, path: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ProtocolContractError(f"CP000_SCHEMA_INVALID@{path}: sha256 required")
    return value


def _string_map(value: object, path: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, Mapping):
        raise ProtocolContractError(f"CP000_SCHEMA_INVALID@{path}: mapping required")
    rows = tuple(sorted(
        (_nonempty(key, path), _nonempty(item, f"{path}.{key}"))
        for key, item in value.items()
    ))
    if len(rows) != len({key for key, _ in rows}):
        raise ProtocolContractError(f"CP000_SCHEMA_INVALID@{path}: duplicate key")
    return rows


def _role_effects(value: object) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if not isinstance(value, Mapping):
        raise ProtocolContractError(
            "CP000_SCHEMA_INVALID@role_effects: mapping required")
    rows = []
    for role, raw_effects in value.items():
        role = _nonempty(role, "role_effects")
        if not isinstance(raw_effects, Sequence) or isinstance(raw_effects, (str, bytes)):
            raise ProtocolContractError(
                f"CP000_SCHEMA_INVALID@role_effects.{role}: sequence required")
        effects = tuple(sorted(_nonempty(item, f"role_effects.{role}") for item in raw_effects))
        if len(effects) != len(set(effects)):
            raise ProtocolContractError(
                f"CP000_SCHEMA_INVALID@role_effects.{role}: duplicate effect")
        rows.append((role, effects))
    return tuple(sorted(rows))


@dataclass(frozen=True)
class ProtocolContractDeclaration:
    family: str
    task_semantics_sha256: str
    role_effects: tuple[tuple[str, tuple[str, ...]], ...]
    attribute_abi_ownership: tuple[tuple[str, str], ...]
    physical_bindings: tuple[tuple[str, str], ...]
    continuation_policy: str
    checked_executable_sha256: str
    schema: str = "rtdl.v4.callback_protocol_contract.v1"

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "ProtocolContractDeclaration":
        expected = {
            "schema", "family", "task_semantics_sha256", "role_effects",
            "attribute_abi_ownership", "physical_bindings",
            "continuation_policy", "checked_executable_sha256",
            "contract_sha256",
        }
        if set(value) != expected or value.get("schema") != cls.schema:
            raise ProtocolContractError(
                "CP000_SCHEMA_INVALID@contract: exact v1 schema required")
        body = dict(value)
        observed_seal = body.pop("contract_sha256")
        if _sha(observed_seal, "contract.contract_sha256") != _digest(body):
            raise ProtocolContractError(
                "CP000_SCHEMA_INVALID@contract.contract_sha256: seal mismatch")
        return cls(
            family=_nonempty(value["family"], "contract.family"),
            task_semantics_sha256=_sha(
                value["task_semantics_sha256"], "contract.task_semantics_sha256"),
            role_effects=_role_effects(value["role_effects"]),
            attribute_abi_ownership=_string_map(
                value["attribute_abi_ownership"], "contract.attribute_abi_ownership"),
            physical_bindings=_string_map(
                value["physical_bindings"], "contract.physical_bindings"),
            continuation_policy=_nonempty(
                value["continuation_policy"], "contract.continuation_policy"),
            checked_executable_sha256=_sha(
                value["checked_executable_sha256"],
                "contract.checked_executable_sha256"),
        )

    def to_mapping(self) -> dict[str, object]:
        body = {
            "schema": self.schema,
            "family": self.family,
            "task_semantics_sha256": self.task_semantics_sha256,
            "role_effects": {key: list(value) for key, value in self.role_effects},
            "attribute_abi_ownership": dict(self.attribute_abi_ownership),
            "physical_bindings": dict(self.physical_bindings),
            "continuation_policy": self.continuation_policy,
            "checked_executable_sha256": self.checked_executable_sha256,
        }
        return {**body, "contract_sha256": _digest(body)}


@dataclass(frozen=True)
class CompilerProtocolProjection:
    family: str
    task_semantics_sha256: str
    role_effects: tuple[tuple[str, tuple[str, ...]], ...]
    attribute_abi_ownership: tuple[tuple[str, str], ...]
    physical_bindings: tuple[tuple[str, str], ...]
    continuation_policy: str
    actual_executable_sha256: str
    generated_device_source_sha256: str
    generated_host_source_sha256: str
    schema: str = "rtdl.v4.compiler_protocol_projection.v1"

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "CompilerProtocolProjection":
        expected = {
            "schema", "family", "task_semantics_sha256", "role_effects",
            "attribute_abi_ownership", "physical_bindings",
            "continuation_policy", "actual_executable_sha256",
            "generated_device_source_sha256", "generated_host_source_sha256",
            "projection_sha256",
        }
        if set(value) != expected or value.get("schema") != cls.schema:
            raise ProtocolContractError(
                "CP000_SCHEMA_INVALID@projection: exact v1 schema required")
        body = dict(value)
        observed_seal = body.pop("projection_sha256")
        if _sha(observed_seal, "projection.projection_sha256") != _digest(body):
            raise ProtocolContractError(
                "CP000_SCHEMA_INVALID@projection.projection_sha256: seal mismatch")
        return cls(
            family=_nonempty(value["family"], "projection.family"),
            task_semantics_sha256=_sha(
                value["task_semantics_sha256"], "projection.task_semantics_sha256"),
            role_effects=_role_effects(value["role_effects"]),
            attribute_abi_ownership=_string_map(
                value["attribute_abi_ownership"], "projection.attribute_abi_ownership"),
            physical_bindings=_string_map(
                value["physical_bindings"], "projection.physical_bindings"),
            continuation_policy=_nonempty(
                value["continuation_policy"], "projection.continuation_policy"),
            actual_executable_sha256=_sha(
                value["actual_executable_sha256"],
                "projection.actual_executable_sha256"),
            generated_device_source_sha256=_sha(
                value["generated_device_source_sha256"],
                "projection.generated_device_source_sha256"),
            generated_host_source_sha256=_sha(
                value["generated_host_source_sha256"],
                "projection.generated_host_source_sha256"),
        )

    def to_mapping(self) -> dict[str, object]:
        body = {
            "schema": self.schema,
            "family": self.family,
            "task_semantics_sha256": self.task_semantics_sha256,
            "role_effects": {key: list(value) for key, value in self.role_effects},
            "attribute_abi_ownership": dict(self.attribute_abi_ownership),
            "physical_bindings": dict(self.physical_bindings),
            "continuation_policy": self.continuation_policy,
            "actual_executable_sha256": self.actual_executable_sha256,
            "generated_device_source_sha256": self.generated_device_source_sha256,
            "generated_host_source_sha256": self.generated_host_source_sha256,
        }
        return {**body, "projection_sha256": _digest(body)}


@dataclass(frozen=True)
class ProtocolContractFinding:
    mechanism: ProtocolMechanism
    reason_id: str
    declared_sha256: str
    projected_sha256: str

    def to_mapping(self) -> dict[str, str]:
        return {
            "mechanism": self.mechanism.value,
            "reason_id": self.reason_id,
            "declared_sha256": self.declared_sha256,
            "projected_sha256": self.projected_sha256,
        }


@dataclass(frozen=True)
class ProtocolContractDecision:
    verdict: str
    findings: tuple[ProtocolContractFinding, ...]
    contract_sha256: str
    projection_sha256: str
    schema: str = "rtdl.v4.callback_protocol_contract_decision.v1"

    def verdict_with_mechanism_ablated(self, mechanism: ProtocolMechanism) -> str:
        """Evaluation-only counterfactual; never issues an executable capability."""

        return "ACCEPT" if all(
            finding.mechanism is mechanism for finding in self.findings
        ) else "REJECT"

    def to_mapping(self) -> dict[str, object]:
        body = {
            "schema": self.schema,
            "verdict": self.verdict,
            "findings": [finding.to_mapping() for finding in self.findings],
            "contract_sha256": self.contract_sha256,
            "projection_sha256": self.projection_sha256,
            "executable_capability_issued": False,
        }
        return {**body, "decision_sha256": _digest(body)}


def verify_protocol_contract(
    declaration: ProtocolContractDeclaration | Mapping[str, object],
    projection: CompilerProtocolProjection | Mapping[str, object],
) -> ProtocolContractDecision:
    """Compare all five seams and return every independent mismatch."""

    if isinstance(declaration, Mapping):
        declaration = ProtocolContractDeclaration.from_mapping(declaration)
    if isinstance(projection, Mapping):
        projection = CompilerProtocolProjection.from_mapping(projection)
    if not isinstance(declaration, ProtocolContractDeclaration) \
            or not isinstance(projection, CompilerProtocolProjection):
        raise ProtocolContractError(
            "CP000_SCHEMA_INVALID@inputs: declaration and projection required")

    findings: list[ProtocolContractFinding] = []

    def compare(mechanism: ProtocolMechanism, declared: object, actual: object) -> None:
        if _canonical(declared) != _canonical(actual):
            findings.append(ProtocolContractFinding(
                mechanism=mechanism,
                reason_id=_REASON_BY_MECHANISM[mechanism],
                declared_sha256=_digest(declared),
                projected_sha256=_digest(actual),
            ))

    # Family/task identities are deliberately part of physical binding.  They
    # cannot drift without producing a second, generic identity mechanism.
    compare(
        ProtocolMechanism.PHYSICAL_GEOMETRY_BINDING,
        (declaration.family, declaration.task_semantics_sha256,
         declaration.physical_bindings),
        (projection.family, projection.task_semantics_sha256,
         projection.physical_bindings),
    )
    compare(
        ProtocolMechanism.ROLE_EFFECT_CLOSURE,
        declaration.role_effects, projection.role_effects,
    )
    compare(
        ProtocolMechanism.PAYLOAD_ATTRIBUTE_ABI_OWNERSHIP,
        declaration.attribute_abi_ownership,
        projection.attribute_abi_ownership,
    )
    compare(
        ProtocolMechanism.DEVICE_STATUS_CONTINUATION,
        declaration.continuation_policy, projection.continuation_policy,
    )
    compare(
        ProtocolMechanism.CHECKED_PROGRAM_EXECUTABLE_IDENTITY,
        declaration.checked_executable_sha256,
        projection.actual_executable_sha256,
    )
    contract_mapping = declaration.to_mapping()
    projection_mapping = projection.to_mapping()
    return ProtocolContractDecision(
        verdict="ACCEPT" if not findings else "REJECT",
        findings=tuple(findings),
        contract_sha256=str(contract_mapping["contract_sha256"]),
        projection_sha256=str(projection_mapping["projection_sha256"]),
    )


__all__ = [
    "CompilerProtocolProjection",
    "ProtocolContractDecision",
    "ProtocolContractDeclaration",
    "ProtocolContractError",
    "ProtocolContractFinding",
    "ProtocolMechanism",
    "verify_protocol_contract",
]
