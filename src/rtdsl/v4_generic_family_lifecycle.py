"""Provider-neutral lifecycle for schema-admitted V4 protocol families.

The generic core owns admission, capability matching, identity binding, and
fail-closed lifecycle state. Providers own physical lowering and execution.
This module deliberately imports no concrete geometry, application, or fixed
protocol implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import os
import re
import threading
from types import MappingProxyType
from typing import Any

from .v4_family_schema import (
    CanonicalFamilyCompilationPlan,
    reverify_canonical_compilation_plan,
)


_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}\Z")
_PROVIDER_OPERATOR = "provider_operator"
FAMILY_BEHAVIOR_SCHEMA_ARTIFACT_ID = "rtdl.behavior.schema"
FAMILY_CALLBACK_ABI_ARTIFACT_ID = "rtdl.callback.abi"
FAMILY_CALLBACK_PROGRAM_ARTIFACT_ID = "rtdl.callback.program"
_REQUIRED_PROGRAM_ARTIFACT_IDS = frozenset({
    FAMILY_BEHAVIOR_SCHEMA_ARTIFACT_ID,
    FAMILY_CALLBACK_ABI_ARTIFACT_ID,
    FAMILY_CALLBACK_PROGRAM_ARTIFACT_ID,
})
_MAX_ARTIFACT_COUNT = 256
_MAX_ARTIFACT_BYTES = 64 << 20
_MAX_BUNDLE_BYTES = 256 << 20


class GenericFamilyLifecycleError(RuntimeError):
    """Stable fail-closed error raised by the generic lifecycle."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code}@{path}:{message}")


def _fail(code: str, path: str, message: str) -> None:
    raise GenericFamilyLifecycleError(code, path, message)


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise GenericFamilyLifecycleError(
            "GF001_CANONICAL_VALUE", "$", str(exc)
        ) from exc


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(value: object, path: str) -> str:
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        _fail("GF002_SHA256", path, repr(value))
    return value


def _identifier(value: object, path: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        _fail("GF003_IDENTIFIER", path, repr(value))
    return value


def _identifiers(value: object, path: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        _fail("GF004_SEQUENCE", path, repr(value))
    result = tuple(_identifier(item, f"{path}[{index}]")
                   for index, item in enumerate(value))
    if len(result) != len(set(result)):
        _fail("GF005_DUPLICATE", path, repr(result))
    return tuple(sorted(result))


def _readonly(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _readonly(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_readonly(item) for item in value)
    return value


def _json_document(value: object, path: str) -> object:
    try:
        encoded = _canonical(value)
        decoded = json.loads(encoded)
    except (json.JSONDecodeError, GenericFamilyLifecycleError) as exc:
        raise GenericFamilyLifecycleError(
            "GF001_CANONICAL_VALUE", path, str(exc)
        ) from exc
    return decoded


def derive_family_target_sha256(target: object) -> str:
    """Derive target identity without consulting the selected provider."""

    direct = getattr(target, "target_sha256", None)
    if isinstance(direct, str):
        return _sha(direct, "target.target_sha256")
    profile = getattr(target, "profile", None)
    profiled = getattr(profile, "target_sha256", None)
    if isinstance(profiled, str):
        return _sha(profiled, "target.profile.target_sha256")
    if isinstance(target, (Mapping, list, tuple, str, int, float, bool)) \
            or target is None:
        return _digest(_json_document(target, "target"))
    _fail(
        "GF031_TARGET_IDENTITY",
        "target",
        "target_sha256, profile.target_sha256, or canonical JSON target required",
    )


@dataclass(frozen=True, slots=True, init=False)
class FamilyArtifactV1:
    """One immutable opaque artifact whose semantics are provider-verified."""

    artifact_id: str
    format_id: str
    payload: bytes
    payload_bytes: int
    payload_sha256: str

    def __init__(self, artifact_id: str, format_id: str, payload: object) -> None:
        artifact_id = _identifier(artifact_id, "artifact.artifact_id")
        format_id = _identifier(format_id, "artifact.format_id")
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            _fail("GF034_ARTIFACT_PAYLOAD", "artifact.payload", "bytes required")
        detached = bytes(payload)
        if not detached or len(detached) > _MAX_ARTIFACT_BYTES:
            _fail(
                "GF034_ARTIFACT_PAYLOAD",
                "artifact.payload",
                f"size must be 1..{_MAX_ARTIFACT_BYTES}",
            )
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "format_id", format_id)
        object.__setattr__(self, "payload", detached)
        object.__setattr__(self, "payload_bytes", len(detached))
        object.__setattr__(
            self, "payload_sha256", hashlib.sha256(detached).hexdigest()
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "format_id": self.format_id,
            "payload_bytes": self.payload_bytes,
            "payload_sha256": self.payload_sha256,
        }


@dataclass(frozen=True, slots=True, init=False)
class FamilyProgramArtifactsV1:
    """Identity-bound program inputs passed through the generic provider SPI."""

    plan_sha256: str
    callback_source_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    abi_sha256: str
    behavior_schema_sha256: str
    artifacts: tuple[FamilyArtifactV1, ...]
    bundle_sha256: str

    def __init__(
        self,
        plan: CanonicalFamilyCompilationPlan,
        artifacts: Sequence[FamilyArtifactV1],
        *,
        _token: object,
        _verified_plan_token: object | None = None,
    ) -> None:
        if _token is not _CONSTRUCTION_TOKEN:
            _fail(
                "GF012_LIVE_CAPABILITY",
                "artifacts",
                "use bind_family_program_artifacts",
            )
        if _verified_plan_token is _VERIFIED_PLAN_CONSTRUCTION_TOKEN:
            if not isinstance(plan, CanonicalFamilyCompilationPlan):
                _fail("GF003_PLAN", "plan", "CanonicalFamilyCompilationPlan required")
            verified = plan
        else:
            verified = reverify_canonical_compilation_plan(plan)
        if not isinstance(artifacts, Sequence) or isinstance(
            artifacts, (str, bytes, bytearray, memoryview)
        ):
            _fail("GF004_SEQUENCE", "artifacts", repr(type(artifacts).__name__))
        rows = tuple(artifacts)
        if not rows or len(rows) > _MAX_ARTIFACT_COUNT:
            _fail(
                "GF035_ARTIFACT_BUNDLE",
                "artifacts",
                f"count must be 1..{_MAX_ARTIFACT_COUNT}",
            )
        if any(not isinstance(row, FamilyArtifactV1) for row in rows):
            _fail("GF035_ARTIFACT_BUNDLE", "artifacts", "FamilyArtifactV1 required")
        rows = tuple(sorted(rows, key=lambda row: row.artifact_id))
        ids = tuple(row.artifact_id for row in rows)
        if len(ids) != len(set(ids)):
            _fail("GF005_DUPLICATE", "artifacts.artifact_id", repr(ids))
        missing = sorted(_REQUIRED_PROGRAM_ARTIFACT_IDS - set(ids))
        if missing:
            _fail("GF035_ARTIFACT_BUNDLE", "artifacts", f"missing {missing!r}")
        if sum(len(row.payload) for row in rows) > _MAX_BUNDLE_BYTES:
            _fail(
                "GF035_ARTIFACT_BUNDLE",
                "artifacts",
                f"total bytes exceed {_MAX_BUNDLE_BYTES}",
            )
        document = verified.to_dict()
        identity = {
            "schema": "rtdl.family_program_artifacts.v1",
            "plan_sha256": verified.plan_sha256,
            "callback_source_sha256": document["callback_source_sha256"],
            "callback_ir_sha256": document["callback_ir_sha256"],
            "effect_digest": document["effect_digest"],
            "abi_sha256": document["abi_sha256"],
            "behavior_schema_sha256": document["behavior_schema_sha256"],
            "artifacts": [row.to_dict() for row in rows],
        }
        for name in (
            "plan_sha256",
            "callback_source_sha256",
            "callback_ir_sha256",
            "effect_digest",
            "abi_sha256",
            "behavior_schema_sha256",
        ):
            object.__setattr__(self, name, identity[name])
        object.__setattr__(self, "artifacts", rows)
        object.__setattr__(self, "bundle_sha256", _digest(identity))

    @property
    def artifact_formats(self) -> tuple[tuple[str, str], ...]:
        return tuple((row.artifact_id, row.format_id) for row in self.artifacts)

    def artifact(self, artifact_id: str) -> FamilyArtifactV1:
        artifact_id = _identifier(artifact_id, "artifact_id")
        matches = tuple(row for row in self.artifacts if row.artifact_id == artifact_id)
        if len(matches) != 1:
            _fail("GF036_ARTIFACT_LOOKUP", "artifact_id", artifact_id)
        return matches[0]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "rtdl.family_program_artifacts.v1",
            "plan_sha256": self.plan_sha256,
            "callback_source_sha256": self.callback_source_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "abi_sha256": self.abi_sha256,
            "behavior_schema_sha256": self.behavior_schema_sha256,
            "artifacts": [row.to_dict() for row in self.artifacts],
            "bundle_sha256": self.bundle_sha256,
        }


def bind_family_program_artifacts(
    plan: CanonicalFamilyCompilationPlan,
    artifacts: Sequence[FamilyArtifactV1],
) -> FamilyProgramArtifactsV1:
    return FamilyProgramArtifactsV1(plan, artifacts, _token=_CONSTRUCTION_TOKEN)


def _bind_family_program_artifacts_verified(
    plan: CanonicalFamilyCompilationPlan,
    artifacts: Sequence[FamilyArtifactV1],
) -> FamilyProgramArtifactsV1:
    """Bind rows to a plan just issued by the same trusted route builder."""

    return FamilyProgramArtifactsV1(
        plan,
        artifacts,
        _token=_CONSTRUCTION_TOKEN,
        _verified_plan_token=_VERIFIED_PLAN_CONSTRUCTION_TOKEN,
    )


def reverify_family_program_artifacts(
    plan: CanonicalFamilyCompilationPlan,
    bundle: FamilyProgramArtifactsV1,
) -> FamilyProgramArtifactsV1:
    verified = reverify_canonical_compilation_plan(plan)
    return _reverify_family_program_artifacts_verified(verified, bundle)


def _reverify_family_program_artifacts_verified(
    verified: CanonicalFamilyCompilationPlan,
    bundle: FamilyProgramArtifactsV1,
) -> FamilyProgramArtifactsV1:
    """Rebuild a bundle against a plan verified at this trust edge."""

    if not isinstance(bundle, FamilyProgramArtifactsV1):
        _fail("GF035_ARTIFACT_BUNDLE", "artifacts", type(bundle).__name__)
    fresh_rows = tuple(
        FamilyArtifactV1(row.artifact_id, row.format_id, row.payload)
        for row in bundle.artifacts
    )
    fresh = _bind_family_program_artifacts_verified(verified, fresh_rows)
    if fresh.to_dict() != bundle.to_dict():
        _fail("GF037_ARTIFACT_DRIFT", "artifacts", "bundle identity changed")
    return fresh


@dataclass(frozen=True, slots=True)
class FamilyPlanRequirementsV1:
    graph_kinds: tuple[str, ...]
    primitive_kinds: tuple[str, ...]
    callback_roles: tuple[str, ...]
    provider_builtins: tuple[str, ...]
    operator_contracts: tuple[tuple[str, str], ...]
    capabilities: tuple[str, ...]
    requirements_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "rtdl.family_plan_requirements.v1",
            "graph_kinds": list(self.graph_kinds),
            "primitive_kinds": list(self.primitive_kinds),
            "callback_roles": list(self.callback_roles),
            "provider_builtins": list(self.provider_builtins),
            "operator_contracts": [
                {"operator_id": name, "operator_contract_sha256": digest}
                for name, digest in self.operator_contracts
            ],
            "capabilities": list(self.capabilities),
            "requirements_sha256": self.requirements_sha256,
        }


def derive_family_plan_requirements(
    plan: CanonicalFamilyCompilationPlan,
) -> FamilyPlanRequirementsV1:
    verified = reverify_canonical_compilation_plan(plan)
    return _derive_family_plan_requirements_verified(verified)


def _derive_family_plan_requirements_verified(
    verified: CanonicalFamilyCompilationPlan,
) -> FamilyPlanRequirementsV1:
    """Project requirements from a plan verified at the current trust edge."""

    shape = verified.to_dict()["family_shape"]
    graph_kinds = tuple(sorted({str(row["kind"]) for row in shape["graph_nodes"]}))
    primitive_kinds = tuple(sorted({
        str(row["primitive_kind"])
        for row in shape["graph_nodes"]
        if row["primitive_kind"] != "none"
    }))
    callback_roles = tuple(sorted(
        str(row["role"]) for row in shape["callback"]["roles"]
    ))
    provider_builtins = tuple(sorted({
        str(row["producer"]["builtin"])
        for row in shape["channels"]
        if row["producer"]["kind"] == "provider_builtin"
    } | {
        str(row["provider_builtin"])
        for row in shape["events"]
        if row["source"] == "provider_builtin"
    }))
    operator_contracts: list[tuple[str, str]] = []
    for row in shape["result_pipeline"]:
        if row["operator"] == _PROVIDER_OPERATOR:
            operator_contracts.append((
                str(row["operator_id"]),
                str(row["operator_contract_sha256"]),
            ))
        else:
            operator_id = f"rtdl.legacy.{row['operator']}.v1"
            operator_contracts.append((operator_id, _digest({
                "schema": "rtdl.legacy_result_operator.v1",
                "operator": row["operator"],
            })))
    operator_contracts = sorted(set(operator_contracts))
    capabilities = tuple(sorted(str(item) for item in shape["capabilities"]))
    body = {
        "schema": "rtdl.family_plan_requirements.v1",
        "graph_kinds": list(graph_kinds),
        "primitive_kinds": list(primitive_kinds),
        "callback_roles": list(callback_roles),
        "provider_builtins": list(provider_builtins),
        "operator_contracts": [
            {"operator_id": name, "operator_contract_sha256": digest}
            for name, digest in operator_contracts
        ],
        "capabilities": list(capabilities),
    }
    return FamilyPlanRequirementsV1(
        graph_kinds,
        primitive_kinds,
        callback_roles,
        provider_builtins,
        tuple(operator_contracts),
        capabilities,
        _digest(body),
    )


@dataclass(frozen=True, slots=True)
class FamilyProviderDescriptorV1:
    provider_id: str
    provider_version: str
    target_api: str
    implementation_sha256: str
    graph_kinds: tuple[str, ...]
    primitive_kinds: tuple[str, ...]
    callback_roles: tuple[str, ...]
    provider_builtins: tuple[str, ...]
    artifact_formats: tuple[tuple[str, str], ...]
    operator_contracts: tuple[tuple[str, str], ...]
    capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.provider_id, "provider.provider_id")
        _identifier(self.provider_version, "provider.provider_version")
        _identifier(self.target_api, "provider.target_api")
        _sha(self.implementation_sha256, "provider.implementation_sha256")
        for name, values in (
            ("graph_kinds", self.graph_kinds),
            ("primitive_kinds", self.primitive_kinds),
            ("callback_roles", self.callback_roles),
            ("provider_builtins", self.provider_builtins),
            ("capabilities", self.capabilities),
        ):
            normalized = _identifiers(values, f"provider.{name}")
            if normalized != values:
                _fail("GF007_CANONICAL_ORDER", f"provider.{name}", repr(values))
        if not isinstance(self.operator_contracts, tuple):
            _fail(
                "GF008_OPERATOR_CONTRACT",
                "provider.operator_contracts",
                "tuple required",
            )
        normalized_operators = []
        operator_ids: dict[str, str] = {}
        for index, row in enumerate(self.operator_contracts):
            if not isinstance(row, tuple) or len(row) != 2:
                _fail("GF008_OPERATOR_CONTRACT", f"provider.operator_contracts[{index}]", repr(row))
            operator_id = _identifier(
                row[0], f"provider.operator_contracts[{index}].operator_id"
            )
            contract_sha256 = _sha(
                row[1], f"provider.operator_contracts[{index}].sha256"
            )
            previous = operator_ids.setdefault(operator_id, contract_sha256)
            if previous != contract_sha256:
                _fail(
                    "GF032_OPERATOR_IDENTITY",
                    f"provider.operator_contracts[{index}]",
                    "one operator_id cannot name multiple contracts",
                )
            normalized_operators.append((operator_id, contract_sha256))
        if tuple(sorted(set(normalized_operators))) != self.operator_contracts:
            _fail("GF007_CANONICAL_ORDER", "provider.operator_contracts", repr(self.operator_contracts))
        if not isinstance(self.artifact_formats, tuple):
            _fail(
                "GF038_ARTIFACT_FORMAT",
                "provider.artifact_formats",
                "tuple required",
            )
        normalized_artifacts = []
        artifact_ids: set[str] = set()
        for index, row in enumerate(self.artifact_formats):
            if not isinstance(row, tuple) or len(row) != 2:
                _fail(
                    "GF038_ARTIFACT_FORMAT",
                    f"provider.artifact_formats[{index}]",
                    repr(row),
                )
            artifact_id = _identifier(
                row[0], f"provider.artifact_formats[{index}].artifact_id"
            )
            format_id = _identifier(
                row[1], f"provider.artifact_formats[{index}].format_id"
            )
            if artifact_id in artifact_ids:
                _fail(
                    "GF005_DUPLICATE",
                    "provider.artifact_formats",
                    artifact_id,
                )
            artifact_ids.add(artifact_id)
            normalized_artifacts.append((artifact_id, format_id))
        if tuple(sorted(normalized_artifacts)) != self.artifact_formats:
            _fail(
                "GF007_CANONICAL_ORDER",
                "provider.artifact_formats",
                repr(self.artifact_formats),
            )

    @property
    def descriptor_sha256(self) -> str:
        return _digest(self.to_dict(include_digest=False))

    def to_dict(self, *, include_digest: bool = True) -> dict[str, object]:
        body = {
            "schema": "rtdl.family_provider_descriptor.v1",
            "provider_id": self.provider_id,
            "provider_version": self.provider_version,
            "target_api": self.target_api,
            "implementation_sha256": self.implementation_sha256,
            "graph_kinds": list(self.graph_kinds),
            "primitive_kinds": list(self.primitive_kinds),
            "callback_roles": list(self.callback_roles),
            "provider_builtins": list(self.provider_builtins),
            "artifact_formats": [
                {"artifact_id": name, "format_id": format_id}
                for name, format_id in self.artifact_formats
            ],
            "operator_contracts": [
                {"operator_id": name, "operator_contract_sha256": digest}
                for name, digest in self.operator_contracts
            ],
            "capabilities": list(self.capabilities),
        }
        if include_digest:
            body["descriptor_sha256"] = self.descriptor_sha256
        return body


def reverify_family_provider_descriptor(
    descriptor: FamilyProviderDescriptorV1,
) -> FamilyProviderDescriptorV1:
    if not isinstance(descriptor, FamilyProviderDescriptorV1):
        _fail("GF027_PROVIDER_DESCRIPTOR", "provider.descriptor", type(descriptor).__name__)
    fresh = FamilyProviderDescriptorV1(**{
        name: getattr(descriptor, name)
        for name in FamilyProviderDescriptorV1.__dataclass_fields__
    })
    if fresh != descriptor or fresh.descriptor_sha256 != descriptor.descriptor_sha256:
        _fail("GF039_PROVIDER_DESCRIPTOR_DRIFT", "provider.descriptor", "identity changed")
    return fresh


@dataclass(frozen=True, slots=True)
class FamilyProviderProjectionV1:
    provider_descriptor_sha256: str
    plan_sha256: str
    family_shape_sha256: str
    protocol_instance_sha256: str
    callback_source_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    abi_sha256: str
    behavior_schema_sha256: str
    canonical_template_id: str
    requirements_sha256: str
    artifact_bundle_sha256: str

    def __post_init__(self) -> None:
        for name in (
            "provider_descriptor_sha256", "plan_sha256", "family_shape_sha256",
            "protocol_instance_sha256", "callback_source_sha256",
            "callback_ir_sha256", "effect_digest", "abi_sha256",
            "behavior_schema_sha256", "requirements_sha256",
            "artifact_bundle_sha256",
        ):
            _sha(getattr(self, name), f"projection.{name}")
        _identifier(self.canonical_template_id, "projection.canonical_template_id")

    @property
    @lru_cache(maxsize=4096)
    def projection_sha256(self) -> str:
        return _digest(self.to_dict(include_digest=False))

    def to_dict(self, *, include_digest: bool = True) -> dict[str, object]:
        body = {
            "schema": "rtdl.family_provider_projection.v1",
            "provider_descriptor_sha256": self.provider_descriptor_sha256,
            "plan_sha256": self.plan_sha256,
            "family_shape_sha256": self.family_shape_sha256,
            "protocol_instance_sha256": self.protocol_instance_sha256,
            "callback_source_sha256": self.callback_source_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "abi_sha256": self.abi_sha256,
            "behavior_schema_sha256": self.behavior_schema_sha256,
            "canonical_template_id": self.canonical_template_id,
            "requirements_sha256": self.requirements_sha256,
            "artifact_bundle_sha256": self.artifact_bundle_sha256,
        }
        if include_digest:
            body["projection_sha256"] = self.projection_sha256
        return body


def expected_provider_projection(
    plan: CanonicalFamilyCompilationPlan,
    descriptor: FamilyProviderDescriptorV1,
    artifacts: FamilyProgramArtifactsV1,
) -> FamilyProviderProjectionV1:
    verified = reverify_canonical_compilation_plan(plan)
    artifacts = _reverify_family_program_artifacts_verified(
        verified, artifacts
    )
    descriptor = reverify_family_provider_descriptor(descriptor)
    return _expected_provider_projection_verified(
        verified, descriptor, artifacts
    )


def _expected_provider_projection_verified(
    verified: CanonicalFamilyCompilationPlan,
    descriptor: FamilyProviderDescriptorV1,
    artifacts: FamilyProgramArtifactsV1,
) -> FamilyProviderProjectionV1:
    """Project a provider after the caller has verified all three inputs."""

    document = verified.to_dict()
    protocol = document["protocol_instance"]
    requirements = _derive_family_plan_requirements_verified(verified)
    return FamilyProviderProjectionV1(
        descriptor.descriptor_sha256,
        verified.plan_sha256,
        document["family_shape_sha256"],
        document["protocol_instance_sha256"],
        document["callback_source_sha256"],
        document["callback_ir_sha256"],
        document["effect_digest"],
        document["abi_sha256"],
        document["behavior_schema_sha256"],
        document["canonical_template_id"],
        requirements.requirements_sha256,
        artifacts.bundle_sha256,
    )


def _require_provider_coverage(
    requirements: FamilyPlanRequirementsV1,
    descriptor: FamilyProviderDescriptorV1,
) -> None:
    checks = (
        ("graph_kinds", requirements.graph_kinds, descriptor.graph_kinds),
        ("primitive_kinds", requirements.primitive_kinds, descriptor.primitive_kinds),
        ("callback_roles", requirements.callback_roles, descriptor.callback_roles),
        (
            "provider_builtins",
            requirements.provider_builtins,
            descriptor.provider_builtins,
        ),
        ("operator_contracts", requirements.operator_contracts, descriptor.operator_contracts),
        ("capabilities", requirements.capabilities, descriptor.capabilities),
    )
    for name, required, supported in checks:
        missing = sorted(set(required) - set(supported))
        if missing:
            _fail("GF009_PROVIDER_CAPABILITY", f"provider.{name}", repr(missing))


@dataclass(frozen=True, slots=True)
class FamilyExecutableIdentityV1:
    provider_descriptor_sha256: str
    provider_projection_sha256: str
    plan_sha256: str
    target_sha256: str
    executable_sha256: str
    provider_artifact_sha256: str
    generated_artifact_sha256: str

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            _sha(getattr(self, name), f"executable_identity.{name}")

    @property
    @lru_cache(maxsize=4096)
    def identity_sha256(self) -> str:
        return _digest(self.to_dict(include_digest=False))

    def to_dict(self, *, include_digest: bool = True) -> dict[str, object]:
        body = {
            "schema": "rtdl.family_executable_identity.v1",
            **{name: getattr(self, name) for name in self.__dataclass_fields__},
        }
        if include_digest:
            body["identity_sha256"] = self.identity_sha256
        return body


@dataclass(frozen=True, slots=True)
class FamilyProviderExecutionV1:
    plan_sha256: str
    executable_identity_sha256: str
    status: str
    status_code: int
    output_document: object | None
    output_sha256: str | None
    traversal_receipt: Mapping[str, object]

    def __post_init__(self) -> None:
        _sha(self.plan_sha256, "execution.plan_sha256")
        _sha(
            self.executable_identity_sha256,
            "execution.executable_identity_sha256",
        )
        if self.status not in {"OK", "ERROR"}:
            _fail("GF010_STATUS", "execution.status", repr(self.status))
        if type(self.status_code) is not int or not 0 <= self.status_code < 1 << 32:
            _fail("GF010_STATUS", "execution.status_code", repr(self.status_code))
        if not isinstance(self.traversal_receipt, Mapping):
            _fail(
                "GF021_EXECUTION_ENVELOPE",
                "execution.traversal_receipt",
                "mapping required",
            )
        receipt = _json_document(
            dict(self.traversal_receipt), "execution.traversal_receipt"
        )
        object.__setattr__(self, "traversal_receipt", _readonly(receipt))
        if self.status == "OK":
            if self.status_code != 0 or self.output_document is None:
                _fail("GF010_STATUS", "execution", "OK requires code 0 and output")
            output = _json_document(self.output_document, "execution.output_document")
            expected = _digest(output)
            if self.output_sha256 != expected:
                _fail("GF011_OUTPUT_IDENTITY", "execution.output_sha256", repr(self.output_sha256))
            object.__setattr__(self, "output_document", _readonly(output))
        elif self.status_code == 0 or self.output_document is not None \
                or self.output_sha256 is not None:
            _fail("GF010_STATUS", "execution", "ERROR must expose no output")


class FamilyPreparedHandleV1(ABC):
    @property
    @abstractmethod
    def lifecycle_receipt(self) -> Mapping[str, object]:
        raise NotImplementedError

    @abstractmethod
    def execute(self, batch: object) -> FamilyProviderExecutionV1:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class FamilyMaterializedHandleV1(ABC):
    @property
    @abstractmethod
    def identity(self) -> FamilyExecutableIdentityV1:
        raise NotImplementedError

    @abstractmethod
    def prepare(self, static_input: object) -> FamilyPreparedHandleV1:
        raise NotImplementedError


class FamilyProviderV1(ABC):
    @property
    @abstractmethod
    def descriptor(self) -> FamilyProviderDescriptorV1:
        raise NotImplementedError

    @abstractmethod
    def project(
        self,
        plan: CanonicalFamilyCompilationPlan,
        artifacts: FamilyProgramArtifactsV1,
    ) -> FamilyProviderProjectionV1:
        raise NotImplementedError

    @abstractmethod
    def materialize(
        self,
        plan: CanonicalFamilyCompilationPlan,
        projection: FamilyProviderProjectionV1,
        artifacts: FamilyProgramArtifactsV1,
        *,
        target: object,
        toolchain: object,
    ) -> FamilyMaterializedHandleV1:
        raise NotImplementedError


class VerifiedGenericFamilyProgram:
    def __init__(
        self,
        plan: CanonicalFamilyCompilationPlan,
        provider: FamilyProviderV1,
        projection: FamilyProviderProjectionV1,
        artifacts: FamilyProgramArtifactsV1,
        descriptor: FamilyProviderDescriptorV1,
        *,
        _token: object,
    ) -> None:
        if _token is not _CONSTRUCTION_TOKEN:
            _fail("GF012_LIVE_CAPABILITY", "program", "use compile_generic_family_program")
        self._plan = plan
        self._provider = provider
        self._projection = projection
        self._artifacts = artifacts
        self._descriptor = descriptor
        self._plan_snapshot = (plan.plan_sha256, bytes(plan.canonical_bytes))
        self._artifact_snapshot = _family_artifact_snapshot(artifacts)
        self._descriptor_snapshot = _dataclass_snapshot(descriptor)
        self._projection_snapshot = _dataclass_snapshot(projection)

    def _check_live_inputs(self) -> None:
        if (
            not isinstance(self._plan, CanonicalFamilyCompilationPlan)
            or (self._plan.plan_sha256, bytes(self._plan.canonical_bytes))
                != self._plan_snapshot
        ):
            _fail("GF050_PLAN_LIVE_DRIFT", "plan", "identity changed")
        if _family_artifact_snapshot(self._artifacts) != self._artifact_snapshot:
            _fail("GF037_ARTIFACT_DRIFT", "artifacts", "identity changed")
        if _dataclass_snapshot(self._projection) != self._projection_snapshot:
            _fail("GF013_PROJECTION_DRIFT", "provider_projection", "changed")
        if _dataclass_snapshot(self._provider.descriptor) != self._descriptor_snapshot:
            _fail("GF039_PROVIDER_DESCRIPTOR_DRIFT", "provider.descriptor", "changed")

    @property
    def plan(self) -> CanonicalFamilyCompilationPlan:
        return self._plan

    @property
    def provider_projection(self) -> FamilyProviderProjectionV1:
        return self._projection

    @property
    def artifacts(self) -> FamilyProgramArtifactsV1:
        return self._artifacts

    def materialize(
        self, *, target: object, toolchain: object,
    ) -> "MaterializedGenericFamilyProgram":
        # ``compile_generic_family_program`` performed the expensive structural
        # rederivation at the public trust edge.  These objects are immutable
        # live capabilities; subsequent layers check byte/digest snapshots
        # rather than reparsing the same canonical document many times.
        self._check_live_inputs()
        plan = self._plan
        artifacts = self._artifacts
        handle = self._provider.materialize(
            plan,
            self._projection,
            artifacts,
            target=target,
            toolchain=toolchain,
        )
        self._check_live_inputs()
        if not isinstance(handle, FamilyMaterializedHandleV1):
            _fail("GF014_MATERIALIZED_HANDLE", "provider.materialize", type(handle).__name__)
        identity = handle.identity
        if not isinstance(identity, FamilyExecutableIdentityV1):
            _fail("GF015_EXECUTABLE_IDENTITY", "provider.identity", type(identity).__name__)
        if identity.provider_descriptor_sha256 != self._descriptor.descriptor_sha256 \
                or identity.provider_projection_sha256 != self._projection.projection_sha256 \
                or identity.plan_sha256 != plan.plan_sha256 \
                or identity.target_sha256 != derive_family_target_sha256(target):
            _fail("GF015_EXECUTABLE_IDENTITY", "provider.identity", "plan/provider mismatch")
        identity_snapshot = FamilyExecutableIdentityV1(**{
            name: getattr(identity, name)
            for name in FamilyExecutableIdentityV1.__dataclass_fields__
        })
        return MaterializedGenericFamilyProgram(
            self,
            handle,
            identity_snapshot,
            _token=_CONSTRUCTION_TOKEN,
        )


class MaterializedGenericFamilyProgram:
    def __init__(
        self,
        program: VerifiedGenericFamilyProgram,
        handle: FamilyMaterializedHandleV1,
        identity: FamilyExecutableIdentityV1,
        *,
        _token: object,
    ) -> None:
        if _token is not _CONSTRUCTION_TOKEN:
            _fail("GF012_LIVE_CAPABILITY", "materialized", "use program.materialize")
        self._program = program
        self._handle = handle
        self._identity = identity
        self._pid = os.getpid()
        self._thread_id = threading.get_ident()
        self._state = "materialized"
        self._lock = threading.Lock()

    def __getstate__(self):
        _fail("GF030_NONSERIALIZABLE", "materialized", "cannot be serialized")

    @property
    def identity(self) -> FamilyExecutableIdentityV1:
        return self._identity

    @property
    def state(self) -> str:
        return self._state

    def _check_owner(self) -> None:
        if os.getpid() != self._pid:
            _fail("GF016_PROCESS_AFFINITY", "materialized", "process changed")
        if threading.get_ident() != self._thread_id:
            _fail("GF017_THREAD_AFFINITY", "materialized", "thread changed")

    def _check_reported_identity(self) -> None:
        reported = self._handle.identity
        if not isinstance(reported, FamilyExecutableIdentityV1) \
                or reported != self._identity:
            _fail(
                "GF033_EXECUTABLE_IDENTITY_DRIFT",
                "provider.identity",
                "identity changed after materialization",
            )

    def prepare(self, static_input: object) -> "PreparedGenericFamilyProgram":
        self._check_owner()
        if not self._lock.acquire(blocking=False):
            _fail("GF020_REENTRANT", "materialized.prepare", "already active")
        try:
            if self._state != "materialized":
                _fail("GF018_STATE", "materialized.prepare", self._state)
            self._state = "preparing"
            prepared: FamilyPreparedHandleV1 | None = None
            try:
                self._check_reported_identity()
                prepared = self._handle.prepare(static_input)
                if not isinstance(prepared, FamilyPreparedHandleV1):
                    _fail("GF019_PREPARED_HANDLE", "provider.prepare", type(prepared).__name__)
                self._check_reported_identity()
            except Exception as primary:
                self._state = "failed"
                if isinstance(prepared, FamilyPreparedHandleV1):
                    try:
                        prepared.close()
                    except Exception as cleanup:
                        primary.add_note(
                            "provider prepared-handle cleanup also failed: "
                            f"{type(cleanup).__name__}: {cleanup}"
                        )
                raise
            self._state = "prepared"
            return PreparedGenericFamilyProgram(
                self, prepared, _token=_CONSTRUCTION_TOKEN
            )
        finally:
            self._lock.release()


@dataclass(frozen=True, slots=True)
class GenericFamilyExecutionResultV1:
    output: object
    output_sha256: str
    executable_identity_sha256: str
    provider_projection_sha256: str
    traversal_receipt: Mapping[str, object]


class PreparedGenericFamilyProgram:
    def __init__(
        self,
        materialized: MaterializedGenericFamilyProgram,
        handle: FamilyPreparedHandleV1,
        *,
        _token: object,
    ) -> None:
        if _token is not _CONSTRUCTION_TOKEN:
            _fail("GF012_LIVE_CAPABILITY", "prepared", "use materialized.prepare")
        self._materialized = materialized
        self._handle = handle
        self._closed = False
        self._active = threading.Lock()

    def __getstate__(self):
        _fail("GF030_NONSERIALIZABLE", "prepared", "cannot be serialized")

    @property
    def lifecycle_receipt(self) -> Mapping[str, object]:
        self._materialized._check_owner()
        self._materialized._check_reported_identity()
        if self._closed:
            _fail("GF018_STATE", "prepared.lifecycle_receipt", "closed")
        raw_receipt = self._handle.lifecycle_receipt
        if not isinstance(raw_receipt, Mapping):
            _fail(
                "GF021_EXECUTION_ENVELOPE",
                "prepared.lifecycle_receipt",
                "provider receipt must be a mapping",
            )
        provider_receipt = _json_document(
            dict(raw_receipt), "prepared.lifecycle_receipt"
        )
        receipt = {
            "schema": "rtdl.generic_family_lifecycle.v1",
            "plan_sha256": self._materialized._program.plan.plan_sha256,
            "executable_identity_sha256": self._materialized.identity.identity_sha256,
            "provider_projection_sha256": (
                self._materialized._program.provider_projection.projection_sha256
            ),
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "nonreentrant": True,
            "idempotent_close": True,
            "provider_receipt": provider_receipt,
        }
        return _readonly(receipt)  # type: ignore[return-value]

    def execute(self, batch: object) -> GenericFamilyExecutionResultV1:
        self._materialized._check_owner()
        if self._closed:
            _fail("GF018_STATE", "prepared.execute", "closed")
        if not self._active.acquire(blocking=False):
            _fail("GF020_REENTRANT", "prepared.execute", "already active")
        try:
            self._materialized._check_reported_identity()
            execution = self._handle.execute(batch)
            self._materialized._check_reported_identity()
            if not isinstance(execution, FamilyProviderExecutionV1):
                _fail("GF021_EXECUTION_ENVELOPE", "provider.execute", type(execution).__name__)
            identity = self._materialized.identity
            plan = self._materialized._program.plan
            if execution.plan_sha256 != plan.plan_sha256 \
                    or execution.executable_identity_sha256 != identity.identity_sha256:
                _fail("GF022_EXECUTION_IDENTITY", "provider.execute", "identity mismatch")
            if execution.status != "OK":
                _fail("GF023_PROVIDER_STATUS", "provider.execute", str(execution.status_code))
            if execution.output_document is None or execution.output_sha256 is None:
                _fail("GF024_OUTPUT_ABSENT", "provider.execute", "OK output absent")
            return GenericFamilyExecutionResultV1(
                execution.output_document,
                execution.output_sha256,
                identity.identity_sha256,
                self._materialized._program.provider_projection.projection_sha256,
                execution.traversal_receipt,
            )
        finally:
            self._active.release()

    def close(self) -> None:
        self._materialized._check_owner()
        if self._closed:
            return
        if not self._active.acquire(blocking=False):
            _fail("GF020_REENTRANT", "prepared.close", "execution active")
        try:
            self._handle.close()
        finally:
            # A provider destroy failure leaves no safe capability to reuse.
            self._closed = True
            self._active.release()

    def __enter__(self) -> "PreparedGenericFamilyProgram":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


_CONSTRUCTION_TOKEN = object()
_VERIFIED_PLAN_CONSTRUCTION_TOKEN = object()


def _dataclass_snapshot(value: object) -> tuple[object, ...]:
    fields = getattr(value, "__dataclass_fields__", None)
    if not isinstance(fields, dict):
        return (type(value), value)
    return (type(value), *(getattr(value, name) for name in fields))


def _family_artifact_snapshot(
    bundle: FamilyProgramArtifactsV1,
) -> tuple[object, ...]:
    if not isinstance(bundle, FamilyProgramArtifactsV1):
        _fail("GF035_ARTIFACT_BUNDLE", "artifacts", type(bundle).__name__)
    rows = []
    for row in bundle.artifacts:
        payload = row.payload
        if not isinstance(payload, bytes):
            _fail("GF037_ARTIFACT_DRIFT", "artifacts", "payload type changed")
        observed_sha = hashlib.sha256(payload).hexdigest()
        rows.append((
            row.artifact_id,
            row.format_id,
            row.payload_bytes,
            row.payload_sha256,
            len(payload),
            observed_sha,
        ))
    return (
        bundle.plan_sha256,
        bundle.callback_source_sha256,
        bundle.callback_ir_sha256,
        bundle.effect_digest,
        bundle.abi_sha256,
        bundle.behavior_schema_sha256,
        bundle.bundle_sha256,
        tuple(rows),
    )


def compile_generic_family_program(
    plan: CanonicalFamilyCompilationPlan,
    provider: FamilyProviderV1,
    *,
    artifacts: FamilyProgramArtifactsV1,
) -> VerifiedGenericFamilyProgram:
    if not isinstance(plan, CanonicalFamilyCompilationPlan):
        _fail("GF025_PLAN", "plan", type(plan).__name__)
    if not isinstance(provider, FamilyProviderV1):
        _fail("GF026_PROVIDER", "provider", type(provider).__name__)
    verified = reverify_canonical_compilation_plan(plan)
    artifacts = _reverify_family_program_artifacts_verified(
        verified, artifacts
    )
    descriptor = reverify_family_provider_descriptor(provider.descriptor)
    requirements = _derive_family_plan_requirements_verified(verified)
    _require_provider_coverage(requirements, descriptor)
    missing_artifact_formats = sorted(
        set(artifacts.artifact_formats) - set(descriptor.artifact_formats)
    )
    if missing_artifact_formats:
        _fail(
            "GF009_PROVIDER_CAPABILITY",
            "provider.artifact_formats",
            repr(missing_artifact_formats),
        )
    projection = provider.project(verified, artifacts)
    reported_descriptor = reverify_family_provider_descriptor(provider.descriptor)
    if reported_descriptor != descriptor:
        _fail("GF039_PROVIDER_DESCRIPTOR_DRIFT", "provider.descriptor", "changed")
    if not isinstance(projection, FamilyProviderProjectionV1):
        _fail("GF028_PROVIDER_PROJECTION", "provider.project", type(projection).__name__)
    expected = _expected_provider_projection_verified(
        verified, descriptor, artifacts
    )
    if projection != expected:
        _fail("GF029_PROVIDER_PROJECTION_MISMATCH", "provider.project", "not exact")
    return VerifiedGenericFamilyProgram(
        verified,
        provider,
        projection,
        artifacts,
        descriptor,
        _token=_CONSTRUCTION_TOKEN,
    )


__all__ = [
    "FamilyExecutableIdentityV1",
    "FamilyArtifactV1",
    "FAMILY_BEHAVIOR_SCHEMA_ARTIFACT_ID",
    "FAMILY_CALLBACK_ABI_ARTIFACT_ID",
    "FAMILY_CALLBACK_PROGRAM_ARTIFACT_ID",
    "FamilyMaterializedHandleV1",
    "FamilyPlanRequirementsV1",
    "FamilyProgramArtifactsV1",
    "FamilyPreparedHandleV1",
    "FamilyProviderDescriptorV1",
    "FamilyProviderExecutionV1",
    "FamilyProviderProjectionV1",
    "FamilyProviderV1",
    "GenericFamilyExecutionResultV1",
    "GenericFamilyLifecycleError",
    "MaterializedGenericFamilyProgram",
    "PreparedGenericFamilyProgram",
    "VerifiedGenericFamilyProgram",
    "compile_generic_family_program",
    "bind_family_program_artifacts",
    "derive_family_plan_requirements",
    "derive_family_target_sha256",
    "expected_provider_projection",
    "reverify_family_program_artifacts",
    "reverify_family_provider_descriptor",
]
