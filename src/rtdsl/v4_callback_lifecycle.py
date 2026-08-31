"""Public bounded lifecycle for two verified RTDL V4 protocol families.

This module is deliberately a facade over the already verified custom-AABB
bounded-relation and built-in-triangle reduction implementations.  It does not
accept arbitrary PTX, program groups, SBT records, native library objects, or
application identities.  Users select one admitted protocol family and keep
the same public lifecycle across CPU interpretation and GPU execution::

    compile -> materialize -> prepare -> execute -> close

The facade is process-local and thread-affine once target materialization has
started.  It keeps preparation cost explicit, consumes each materialized
executable at most once, rejects device/status failures before constructing a
public result, and makes ``close()`` genuinely idempotent.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from enum import Enum
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
from typing import Mapping, Sequence

from .v4_callback_abi import AnyHitProofAuthority
from .v4_callback_interpreter import execute_callback_role
from .v4_callback_ir import (
    AnyHitDeliveryContract,
    CallbackRole,
    VerifiedCallbackProgram,
)
from .v4_typed_physical_schema import ReferenceTargetProfile
from .v4_protocol_contract import (
    CompilerProtocolProjection,
    ProtocolContractDecision,
    ProtocolContractDeclaration,
    verify_protocol_contract,
)


_SHA256 = re.compile(r"[0-9a-f]{64}")
_PUBLIC_EXTERNAL_PROOF_KIND = (
    "external_machine_checked_order_independence_v1")


class ProtocolLifecycleError(RuntimeError):
    """Stable fail-closed diagnostic for the public V4 lifecycle."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 protocol lifecycle failed: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise ProtocolLifecycleError(code, path, message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_sha256(value: object, path: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        _fail("PL001_DIGEST_INVALID", path, repr(value))
    return value


def _nonempty(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("PL002_STRING_REQUIRED", path, repr(value))
    return value


class ProtocolFamily(str, Enum):
    BOUNDED_RELATION = "custom_aabb_bounded_relation_v1"
    TRIANGLE_REDUCTION = "builtin_triangle_reduction_v1"


class TriangleReductionMode(str, Enum):
    ALL_HIT_COUNT = "all_hit_count"
    WEIGHTED_HIT_COUNT = "weighted_hit_count"


@dataclass(frozen=True)
class AnyHitProtocolProof:
    """External proof evidence that RTDL binds to the exact compiled program.

    RTDL does not claim to prove an opaque external digest true.  It verifies
    that the evidence is well formed, then binds it to the exact callback IR,
    effect digest, and declared delivery contract before ABI compilation.
    """

    callback_ir_sha256: str
    effect_digest: str
    proof_sha256: str
    proof_kind: str
    delivery_contract: AnyHitDeliveryContract = (
        AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL)

    def __post_init__(self) -> None:
        _require_sha256(
            self.callback_ir_sha256, "any_hit_proof.callback_ir_sha256")
        _require_sha256(self.effect_digest, "any_hit_proof.effect_digest")
        _require_sha256(self.proof_sha256, "any_hit_proof.proof_sha256")
        _nonempty(self.proof_kind, "any_hit_proof.proof_kind")
        if self.proof_kind != _PUBLIC_EXTERNAL_PROOF_KIND:
            _fail(
                "PL003_PROOF_KIND_INVALID", "any_hit_proof.proof_kind",
                "the bounded public lifecycle accepts only externally "
                "machine-checked order-independence evidence",
            )
        if not isinstance(self.delivery_contract, AnyHitDeliveryContract):
            _fail(
                "PL003_PROOF_CONTRACT_INVALID",
                "any_hit_proof.delivery_contract",
                repr(self.delivery_contract),
            )

    def bind(self, callback: VerifiedCallbackProgram) -> AnyHitProofAuthority:
        if not isinstance(callback, VerifiedCallbackProgram):
            _fail("PL004_CALLBACK_REQUIRED", "callback", type(callback).__name__)
        if self.callback_ir_sha256 != callback.ir_sha256 \
                or self.effect_digest != callback.effect_digest:
            _fail(
                "PL035_PROOF_PROGRAM_MISMATCH", "any_hit_proof",
                "external authority does not identify the exact callback/effects",
            )
        return AnyHitProofAuthority(
            callback_ir_sha256=self.callback_ir_sha256,
            effect_digest=self.effect_digest,
            delivery_contract=self.delivery_contract,
            proof_sha256=self.proof_sha256,
            proof_kind=self.proof_kind,
        )


@dataclass(frozen=True)
class BoundedRelationProtocol:
    capacity: int
    minimum_overlap_f32: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.capacity, int) or isinstance(self.capacity, bool) \
                or self.capacity <= 0 or self.capacity >= 1 << 32:
            _fail(
                "PL005_CAPACITY_INVALID", "protocol.capacity",
                repr(self.capacity),
            )

    @property
    def family(self) -> ProtocolFamily:
        return ProtocolFamily.BOUNDED_RELATION

    def to_dict(self) -> dict[str, object]:
        return {
            "family": self.family.value,
            "capacity": self.capacity,
            "minimum_overlap_f32": float(self.minimum_overlap_f32),
            "output": "canonical_u32_relation_rows",
            "overflow": "fail_closed_no_partial_result",
        }


@dataclass(frozen=True)
class TriangleReductionProtocol:
    mode: TriangleReductionMode = TriangleReductionMode.WEIGHTED_HIT_COUNT

    def __post_init__(self) -> None:
        if not isinstance(self.mode, TriangleReductionMode):
            _fail("PL006_REDUCTION_MODE_INVALID", "protocol.mode", repr(self.mode))

    @property
    def family(self) -> ProtocolFamily:
        return ProtocolFamily.TRIANGLE_REDUCTION

    def to_dict(self) -> dict[str, object]:
        return {
            "family": self.family.value,
            "mode": self.mode.value,
            "overflow": "checked_u64_fail_closed",
        }


ProtocolSpec = BoundedRelationProtocol | TriangleReductionProtocol


@dataclass(frozen=True)
class ProtocolPhysicalPlan:
    """Typed, backend-neutral physical obligations for one closed family.

    The plan is visible and identity-bearing, but deliberately contains no
    user-supplied PTX, SBT, pipeline, program-group, or native handle.
    """

    family: ProtocolFamily
    geometry_family: str
    callback_roles: tuple[str, ...]
    template_id: str
    output_contract: str
    callback_ir_sha256: str
    effect_digest: str
    reducer_algebra: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.family, ProtocolFamily):
            _fail("PL033_PHYSICAL_PLAN_INVALID", "physical_plan.family", repr(self.family))
        _nonempty(self.geometry_family, "physical_plan.geometry_family")
        _nonempty(self.template_id, "physical_plan.template_id")
        _nonempty(self.output_contract, "physical_plan.output_contract")
        _require_sha256(
            self.callback_ir_sha256, "physical_plan.callback_ir_sha256")
        _require_sha256(self.effect_digest, "physical_plan.effect_digest")
        roles = tuple(_nonempty(item, "physical_plan.callback_roles")
                      for item in self.callback_roles)
        if not roles or len(set(roles)) != len(roles):
            _fail(
                "PL033_PHYSICAL_PLAN_INVALID", "physical_plan.callback_roles",
                repr(roles),
            )
        if self.reducer_algebra is not None:
            _nonempty(self.reducer_algebra, "physical_plan.reducer_algebra")
        object.__setattr__(self, "callback_roles", roles)

    @property
    def plan_sha256(self) -> str:
        return _digest(self.to_dict())

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "rtdl.v4.public_protocol_physical_plan.v1",
            "family": self.family.value,
            "geometry_family": self.geometry_family,
            "callback_roles": list(self.callback_roles),
            "template_id": self.template_id,
            "output_contract": self.output_contract,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "reducer_algebra": self.reducer_algebra,
            "user_ptx_or_sbt_allowed": False,
        }


def standard_protocol_physical_plan(protocol: ProtocolSpec) -> ProtocolPhysicalPlan:
    """Construct the sole admitted public plan for a closed protocol."""

    if isinstance(protocol, BoundedRelationProtocol):
        from .v4_box_relation_callback import compile_callback

        callback = compile_callback()
        return ProtocolPhysicalPlan(
            family=protocol.family,
            geometry_family="custom_aabb",
            callback_roles=(
                "any_hit", "bounds", "closest_hit", "finalize",
                "intersection", "make_ray", "miss",
            ),
            template_id="custom_aabb_bounded_relation_emission_v1",
            output_contract="canonical_u32_relation_rows",
            callback_ir_sha256=callback.ir_sha256,
            effect_digest=callback.effect_digest,
        )
    if isinstance(protocol, TriangleReductionProtocol):
        from .v4_triangle_standard_library import compile_count_callback

        callback = compile_count_callback()
        return ProtocolPhysicalPlan(
            family=protocol.family,
            geometry_family="builtin_triangle",
            callback_roles=("any_hit", "finalize", "make_ray", "miss"),
            template_id="builtin_triangle_checked_reduction_v1",
            output_contract="checked_u64_scalar",
            callback_ir_sha256=callback.ir_sha256,
            effect_digest=callback.effect_digest,
            reducer_algebra=(
                "checked_u64_product_sum"
                if protocol.mode is TriangleReductionMode.WEIGHTED_HIT_COUNT
                else "checked_u64_sum"
            ),
        )
    _fail("PL014_PROTOCOL_UNSUPPORTED", "protocol", type(protocol).__name__)


@dataclass(frozen=True)
class V4Target:
    profile: ReferenceTargetProfile
    native_library_path: Path

    def __post_init__(self) -> None:
        if not isinstance(self.profile, ReferenceTargetProfile):
            _fail("PL007_TARGET_PROFILE_REQUIRED", "target.profile", type(self.profile).__name__)
        path = Path(self.native_library_path).expanduser().resolve()
        if not path.is_file():
            _fail("PL008_NATIVE_MISSING", "target.native_library_path", str(path))
        observed = _file_sha256(path)
        if observed != self.profile.native_sha256:
            _fail(
                "PL009_NATIVE_IDENTITY_MISMATCH", "target.native_library_path",
                f"expected {self.profile.native_sha256}, observed {observed}",
            )
        object.__setattr__(self, "native_library_path", path)

    @classmethod
    def from_native(
        cls,
        native_library_path: str | Path,
        *,
        optix_sdk: str,
        compute_capability: str | tuple[int, int],
        provider: str = "optix",
        supports_custom_aabb: bool = True,
        supports_builtin_triangle: bool = True,
        max_graph_depth: int = 1,
    ) -> "V4Target":
        path = Path(native_library_path).expanduser().resolve()
        if not path.is_file():
            _fail("PL008_NATIVE_MISSING", "native_library_path", str(path))
        if isinstance(compute_capability, tuple):
            if len(compute_capability) != 2:
                _fail("PL010_COMPUTE_CAPABILITY_INVALID", "compute_capability", repr(compute_capability))
            capability = f"{int(compute_capability[0])}.{int(compute_capability[1])}"
        else:
            capability = _nonempty(compute_capability, "compute_capability")
        profile = ReferenceTargetProfile(
            provider=_nonempty(provider, "provider"),
            optix_sdk=_nonempty(optix_sdk, "optix_sdk"),
            compute_capability=capability,
            native_sha256=_file_sha256(path),
            supports_custom_aabb=bool(supports_custom_aabb),
            supports_builtin_triangle=bool(supports_builtin_triangle),
            max_graph_depth=max_graph_depth,
        )
        return cls(profile, path)


@dataclass(frozen=True)
class V4Toolchain:
    compute_capability: tuple[int, int]
    optix_include: Path
    cuda_include: Path
    expected_python_version: str
    expected_numba_version: str
    expected_numpy_version: str

    def __post_init__(self) -> None:
        capability = tuple(int(item) for item in self.compute_capability)
        if len(capability) != 2 or any(item < 0 or item > 99 for item in capability):
            _fail(
                "PL010_COMPUTE_CAPABILITY_INVALID", "toolchain.compute_capability",
                repr(self.compute_capability),
            )
        optix = Path(self.optix_include).expanduser().resolve()
        cuda = Path(self.cuda_include).expanduser().resolve()
        if not optix.is_dir():
            _fail("PL011_INCLUDE_MISSING", "toolchain.optix_include", str(optix))
        if not cuda.is_dir():
            _fail("PL011_INCLUDE_MISSING", "toolchain.cuda_include", str(cuda))
        for name in (
            "expected_python_version", "expected_numba_version",
            "expected_numpy_version",
        ):
            _nonempty(getattr(self, name), f"toolchain.{name}")
        object.__setattr__(self, "compute_capability", capability)
        object.__setattr__(self, "optix_include", optix)
        object.__setattr__(self, "cuda_include", cuda)

    @classmethod
    def current(
        cls,
        *,
        compute_capability: tuple[int, int],
        optix_include: str | Path,
        cuda_include: str | Path,
    ) -> "V4Toolchain":
        return cls(
            compute_capability=compute_capability,
            optix_include=Path(optix_include),
            cuda_include=Path(cuda_include),
            expected_python_version=(
                f"{sys.version_info.major}.{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            ),
            expected_numba_version=importlib.metadata.version("numba"),
            expected_numpy_version=importlib.metadata.version("numpy"),
        )


@dataclass(frozen=True)
class BoundedRelationStaticInput:
    indexed_boxes: tuple[tuple[object, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "indexed_boxes", tuple(tuple(row) for row in self.indexed_boxes))


@dataclass(frozen=True)
class BoundedRelationBatch:
    source_boxes: tuple[tuple[object, ...], ...]
    expected_rows: tuple[tuple[int, int], ...] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "source_boxes", tuple(tuple(row) for row in self.source_boxes))
        if self.expected_rows is not None:
            object.__setattr__(
                self, "expected_rows",
                tuple((int(left), int(right)) for left, right in self.expected_rows),
            )


def _freeze_metadata(
    value: Mapping[str, Sequence[int]], path: str,
) -> tuple[tuple[str, tuple[int, ...]], ...]:
    if not isinstance(value, Mapping):
        _fail("PL012_METADATA_MAPPING_REQUIRED", path, type(value).__name__)
    rows = []
    for key, values in value.items():
        if not isinstance(key, str) or not key:
            _fail("PL012_METADATA_MAPPING_REQUIRED", path, repr(key))
        rows.append((key, tuple(int(item) for item in values)))
    return tuple(sorted(rows))


@dataclass(frozen=True)
class TriangleReductionStaticInput:
    vertices: tuple[tuple[object, object, object], ...]
    triangles: tuple[tuple[int, int, int], ...]
    primitive_metadata: Mapping[str, Sequence[int]]
    event_capacity: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "vertices", tuple(tuple(row) for row in self.vertices))
        object.__setattr__(
            self, "triangles",
            tuple(tuple(int(item) for item in row) for row in self.triangles),
        )
        object.__setattr__(
            self, "primitive_metadata",
            _freeze_metadata(self.primitive_metadata, "primitive_metadata"),
        )
        if not isinstance(self.event_capacity, int) or isinstance(self.event_capacity, bool) \
                or self.event_capacity <= 0:
            _fail("PL005_CAPACITY_INVALID", "event_capacity", repr(self.event_capacity))

    def metadata_dict(self) -> dict[str, tuple[int, ...]]:
        return dict(self.primitive_metadata)


@dataclass(frozen=True)
class TriangleReductionBatch:
    queries: tuple[tuple[object, object, object], ...]
    query_metadata: Mapping[str, Sequence[int]]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "queries",
            tuple((tuple(origin), tuple(direction), tmax)
                  for origin, direction, tmax in self.queries),
        )
        object.__setattr__(
            self, "query_metadata",
            _freeze_metadata(self.query_metadata, "query_metadata"),
        )

    def metadata_dict(self) -> dict[str, tuple[int, ...]]:
        return dict(self.query_metadata)


@dataclass(frozen=True)
class ProtocolProgramIdentity:
    family: str
    callback_ir_sha256: str
    effect_digest: str
    protocol_sha256: str
    physical_plan_sha256: str
    any_hit_proof_sha256: str
    any_hit_proof_kind: str

    @property
    def identity_sha256(self) -> str:
        return _digest(self.to_dict())

    def to_dict(self) -> dict[str, object]:
        return {
            "family": self.family,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "protocol_sha256": self.protocol_sha256,
            "physical_plan_sha256": self.physical_plan_sha256,
            "any_hit_proof_sha256": self.any_hit_proof_sha256,
            "any_hit_proof_kind": self.any_hit_proof_kind,
        }


@dataclass(frozen=True)
class ProtocolExecutableIdentity:
    program: ProtocolProgramIdentity
    target_sha256: str
    physical_schema_sha256: str
    contract_sha256: str
    abi_sha256: str
    generated_executable_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str

    @property
    def identity_sha256(self) -> str:
        return _digest(self.to_dict())

    def to_dict(self) -> dict[str, object]:
        return {
            "program_identity_sha256": self.program.identity_sha256,
            "target_sha256": self.target_sha256,
            "physical_schema_sha256": self.physical_schema_sha256,
            "contract_sha256": self.contract_sha256,
            "abi_sha256": self.abi_sha256,
            "generated_executable_sha256": self.generated_executable_sha256,
            "composed_ptx_sha256": self.composed_ptx_sha256,
            "native_library_sha256": self.native_library_sha256,
        }


@dataclass(frozen=True)
class ProtocolExecutionResult:
    output: object
    launch_status: Sequence[Mapping[str, int]]
    role_counters: tuple[int, ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    executable_identity: ProtocolExecutableIdentity
    details: dict[str, object]


class VerifiedProtocolProgram:
    """Verified backend-neutral program for one admitted public family."""

    def __init__(
        self,
        protocol: ProtocolSpec,
        physical_plan: ProtocolPhysicalPlan,
        callback: VerifiedCallbackProgram,
        proof: AnyHitProofAuthority,
    ) -> None:
        self._protocol = protocol
        self._physical_plan = physical_plan
        self._callback = callback
        self._proof = proof
        self._identity = ProtocolProgramIdentity(
            family=protocol.family.value,
            callback_ir_sha256=callback.ir_sha256,
            effect_digest=callback.effect_digest,
            protocol_sha256=_digest(protocol.to_dict()),
            physical_plan_sha256=physical_plan.plan_sha256,
            any_hit_proof_sha256=proof.proof_sha256,
            any_hit_proof_kind=proof.proof_kind,
        )

    @property
    def protocol(self) -> ProtocolSpec:
        return self._protocol

    @property
    def callback(self) -> VerifiedCallbackProgram:
        return self._callback

    @property
    def physical_plan(self) -> ProtocolPhysicalPlan:
        return self._physical_plan

    @property
    def identity(self) -> ProtocolProgramIdentity:
        return self._identity

    def interpret(self, role: CallbackRole, arguments: Mapping[str, object]):
        return execute_callback_role(self._callback, role, arguments)

    def materialize(
        self, *, target: V4Target, toolchain: V4Toolchain,
    ) -> "MaterializedProtocolProgram":
        return materialize_protocol_program(self, target=target, toolchain=toolchain)


def compile_protocol_program(
    protocol: ProtocolSpec,
    *,
    physical_plan: ProtocolPhysicalPlan,
    any_hit_proof: AnyHitProtocolProof,
) -> VerifiedProtocolProgram:
    """Verify one closed public protocol family without importing GPU code."""

    if not isinstance(any_hit_proof, AnyHitProtocolProof):
        _fail("PL013_PROOF_REQUIRED", "any_hit_proof", type(any_hit_proof).__name__)
    if not isinstance(physical_plan, ProtocolPhysicalPlan):
        _fail(
            "PL033_PHYSICAL_PLAN_INVALID", "physical_plan",
            type(physical_plan).__name__,
        )
    if physical_plan != standard_protocol_physical_plan(protocol):
        _fail(
            "PL034_PHYSICAL_PLAN_MISMATCH", "physical_plan",
            "plan is not the exact closed-family projection",
        )
    if isinstance(protocol, BoundedRelationProtocol):
        from .v4_box_relation_callback import compile_callback

        callback = compile_callback()
    elif isinstance(protocol, TriangleReductionProtocol):
        from .v4_triangle_standard_library import compile_count_callback

        callback = compile_count_callback()
    else:
        _fail("PL014_PROTOCOL_UNSUPPORTED", "protocol", type(protocol).__name__)
    actual_roles = tuple(function.role.value for function in callback.program.functions)
    if actual_roles != physical_plan.callback_roles:
        _fail(
            "PL034_PHYSICAL_PLAN_MISMATCH", "physical_plan.callback_roles",
            f"declared={physical_plan.callback_roles}, actual={actual_roles}",
        )
    proof = any_hit_proof.bind(callback)
    return VerifiedProtocolProgram(protocol, physical_plan, callback, proof)


def _check_target_toolchain(
    program: VerifiedProtocolProgram,
    target: V4Target,
    toolchain: V4Toolchain,
) -> None:
    if not isinstance(program, VerifiedProtocolProgram):
        _fail("PL015_VERIFIED_PROGRAM_REQUIRED", "program", type(program).__name__)
    if not isinstance(target, V4Target):
        _fail("PL007_TARGET_PROFILE_REQUIRED", "target", type(target).__name__)
    if not isinstance(toolchain, V4Toolchain):
        _fail("PL016_TOOLCHAIN_REQUIRED", "toolchain", type(toolchain).__name__)
    profile_cc = tuple(int(item) for item in target.profile.compute_capability.split("."))
    if profile_cc != toolchain.compute_capability:
        _fail(
            "PL017_TARGET_TOOLCHAIN_MISMATCH", "compute_capability",
            f"target={profile_cc}, toolchain={toolchain.compute_capability}",
        )
    if program.protocol.family is ProtocolFamily.BOUNDED_RELATION \
            and not target.profile.supports_custom_aabb:
        _fail("PL018_TARGET_CAPABILITY_MISSING", "target", "custom_aabb")
    if program.protocol.family is ProtocolFamily.TRIANGLE_REDUCTION \
            and not target.profile.supports_builtin_triangle:
        _fail("PL018_TARGET_CAPABILITY_MISSING", "target", "builtin_triangle")


def _declared_role_effects(
    callback: VerifiedCallbackProgram,
) -> dict[str, tuple[str, ...]]:
    """Derive the intended role/effect contract from verified Callback IR."""

    def walk(value, effects: set[str]) -> None:
        if isinstance(value, Mapping):
            if value.get("kind") == "return_effect":
                effect = value.get("effect")
                if isinstance(effect, Mapping) and isinstance(effect.get("kind"), str):
                    effects.add(str(effect["kind"]))
                    fields = effect.get("fields")
                    if isinstance(fields, Mapping) and "payload" in fields:
                        effects.add("payload_write")
            for item in value.values():
                walk(item, effects)
        elif isinstance(value, (list, tuple)):
            for item in value:
                walk(item, effects)

    result = {}
    for function in callback.program.functions:
        if function.role is None:
            continue
        effects: set[str] = set()
        walk(function.to_dict().get("body"), effects)
        result[function.role.value] = tuple(sorted(effects))
    return result


def _compiled_role_effects(abi) -> dict[str, tuple[str, ...]]:
    """Project effects from the independently compiled callback ABI.

    This deliberately does not read ``VerifiedCallbackProgram``.  The ABI is
    regenerated and reverified by each target compiler before an executable is
    minted, so comparing it with the IR-side declaration catches drift at the
    IR-to-ABI boundary instead of comparing one Python mapping with itself.
    """

    result: dict[str, tuple[str, ...]] = {}
    for role in abi.roles:
        effects = {variant.kind.value for variant in role.effects}
        if any(
            ".payload." in field.path or field.path.endswith(".payload")
            for variant in role.effects for field in variant.fields
        ):
            effects.add("payload_write")
        result[role.role.value] = tuple(sorted(effects))
    return result


def _declared_attribute_ownership(
    program: VerifiedProtocolProgram,
) -> dict[str, str]:
    if program.protocol.family is ProtocolFamily.BOUNDED_RELATION:
        return {
            "attr0": "verified_intersection_attribute0_item_id",
        }
    return {}


def _compiled_attribute_ownership(program, authority, contract) -> dict[str, str]:
    if program.protocol.family is ProtocolFamily.BOUNDED_RELATION:
        row_sources = tuple(getattr(contract, "row_sources", ()))
        return {
            "attr0": (
                row_sources[1]
                if len(row_sources) == 2
                else "INVALID_OR_MISSING_ATTRIBUTE0_SOURCE"
            ),
        }
    attribute_slots = getattr(authority.callback, "attribute_u32_slots", None)
    return {} if attribute_slots == 0 else {
        "attribute_layout": f"unexpected_{attribute_slots!r}_u32_slots",
    }


def _declared_physical_bindings(
    program: VerifiedProtocolProgram,
) -> dict[str, str]:
    plan = program.physical_plan
    return {
        "geometry_family": plan.geometry_family,
        "output_contract": plan.output_contract,
        "reducer_algebra": plan.reducer_algebra or "none",
        "template_id": plan.template_id,
    }


def _compiled_protocol_facts(program, authority, contract, abi):
    """Project target-compiler artifacts without consulting the public plan."""

    status_codes = dict(abi.runtime_status_codes)
    has_fail_status = (
        status_codes.get("ok") == 0
        and any(value != 0 for value in status_codes.values())
    )
    if program.protocol.family is ProtocolFamily.BOUNDED_RELATION:
        semantic = contract.semantic_dict()
        relation_schema = authority.schema.semantic_dict()
        task = {
            "family": ProtocolFamily.BOUNDED_RELATION.value,
            "capacity": contract.capacity,
            "minimum_overlap_f32": float(contract.minimum_overlap_f32),
            "output": "canonical_u32_relation_rows",
            "overflow": "fail_closed_no_partial_result",
        }
        relation_is_complete = (
            semantic.get("overflow_policy")
                == "fail_closed_reject_complete_result"
            and relation_schema.get("row_type") == ["u32", "u32"]
            and semantic.get("raw_device_order_is_semantic") is False
        )
        physical = {
            "geometry_family": authority.physical.schema.geometry_family.value,
            "output_contract": (
                "canonical_u32_relation_rows"
                if relation_is_complete
                else "INVALID_BOUNDED_RELATION_OUTPUT_CONTRACT"
            ),
            "reducer_algebra": "none",
            "template_id": contract.template_id,
        }
        continuation = (
            "REQUIRE_COMPLETE_BEFORE_CONSUME"
            if has_fail_status and relation_is_complete
            else "MISSING_FAIL_CLOSED_STATUS_OR_CONTINUATION"
        )
        family = ProtocolFamily.BOUNDED_RELATION.value
    else:
        reducer = dict(contract.reducer)
        algebra = str(reducer.get("algebra"))
        if algebra == "checked_u64_product_sum":
            mode = TriangleReductionMode.WEIGHTED_HIT_COUNT.value
        elif algebra == "checked_u64_sum":
            mode = TriangleReductionMode.ALL_HIT_COUNT.value
        else:
            mode = f"INVALID_REDUCER_ALGEBRA:{algebra}"
        task = {
            "family": ProtocolFamily.TRIANGLE_REDUCTION.value,
            "mode": mode,
            "overflow": "checked_u64_fail_closed",
        }
        reducer_is_complete = (
            reducer.get("overflow_policy") == "fail_closed"
            and reducer.get("output_capacity") == 1
            and mode in {
                TriangleReductionMode.WEIGHTED_HIT_COUNT.value,
                TriangleReductionMode.ALL_HIT_COUNT.value,
            }
        )
        physical = {
            "geometry_family": "builtin_triangle",
            "output_contract": (
                "checked_u64_scalar"
                if reducer_is_complete
                else "INVALID_TRIANGLE_REDUCTION_OUTPUT_CONTRACT"
            ),
            "reducer_algebra": algebra,
            "template_id": contract.template_id,
        }
        continuation = (
            "REQUIRE_COMPLETE_BEFORE_CONSUME"
            if has_fail_status and reducer_is_complete
            else "MISSING_FAIL_CLOSED_STATUS_OR_CONTINUATION"
        )
        family = ProtocolFamily.TRIANGLE_REDUCTION.value
    return family, _digest(task), physical, continuation


def _declared_protocol_contract(
    program: VerifiedProtocolProgram, *, executable_sha256: str,
) -> ProtocolContractDeclaration:
    return ProtocolContractDeclaration(
        family=program.protocol.family.value,
        task_semantics_sha256=program.identity.protocol_sha256,
        role_effects=tuple(sorted(
            _declared_role_effects(program.callback).items())),
        attribute_abi_ownership=tuple(sorted(
            _declared_attribute_ownership(program).items())),
        physical_bindings=tuple(sorted(
            _declared_physical_bindings(program).items())),
        continuation_policy="REQUIRE_COMPLETE_BEFORE_CONSUME",
        checked_executable_sha256=executable_sha256,
    )


def _compiled_protocol_projection(
    program: VerifiedProtocolProgram,
    *, authority, contract, abi, executable_sha256: str,
    composed_ptx_sha256: str,
) -> CompilerProtocolProjection:
    family, task_sha, physical, continuation = _compiled_protocol_facts(
        program, authority, contract, abi)
    return CompilerProtocolProjection(
        family=family,
        task_semantics_sha256=task_sha,
        role_effects=tuple(sorted(_compiled_role_effects(abi).items())),
        attribute_abi_ownership=tuple(sorted(
            _compiled_attribute_ownership(program, authority, contract).items())),
        physical_bindings=tuple(sorted(physical.items())),
        continuation_policy=continuation,
        actual_executable_sha256=executable_sha256,
        generated_device_source_sha256=composed_ptx_sha256,
        generated_host_source_sha256=_file_sha256(Path(__file__)),
    )


def _materialized_protocol_contract_decision(
    program: VerifiedProtocolProgram,
    *, authority, contract, abi, executable_sha256: str,
    composed_ptx_sha256: str,
) -> ProtocolContractDecision:
    """Compare independently derived public and target-compiler facts."""

    declaration = _declared_protocol_contract(
        program, executable_sha256=executable_sha256)
    projection = _compiled_protocol_projection(
        program, authority=authority, contract=contract, abi=abi,
        executable_sha256=executable_sha256,
        composed_ptx_sha256=composed_ptx_sha256,
    )
    return verify_protocol_contract(declaration, projection)


def materialize_protocol_program(
    program: VerifiedProtocolProgram,
    *,
    target: V4Target,
    toolchain: V4Toolchain,
) -> "MaterializedProtocolProgram":
    """Compile one exact target-bound executable; does not create GPU state."""

    _check_target_toolchain(program, target, toolchain)
    started = time.perf_counter()
    options = dict(
        compute_capability=toolchain.compute_capability,
        optix_include=toolchain.optix_include,
        cuda_include=toolchain.cuda_include,
        expected_python_version=toolchain.expected_python_version,
        expected_numba_version=toolchain.expected_numba_version,
        expected_numpy_version=toolchain.expected_numpy_version,
    )
    if isinstance(program.protocol, BoundedRelationProtocol):
        from .v4_bounded_relation_optix_compiler import (
            compile_verified_bounded_relation_executable,
        )
        from .v4_bounded_relation_standard_library import (
            compile_standard_bounded_relation_authority,
        )

        authority, contract, abi = compile_standard_bounded_relation_authority(
            target.profile,
            program._proof,
            capacity=program.protocol.capacity,
            minimum_overlap_f32=program.protocol.minimum_overlap_f32,
        )
        if authority.physical.callback != program.callback:
            _fail("PL019_CALLBACK_REDERIVATION_DRIFT", "program", "bounded relation")
        if (
            authority.physical.schema.geometry_family.value
                != program.physical_plan.geometry_family
            or contract.template_id != program.physical_plan.template_id
        ):
            _fail(
                "PL034_PHYSICAL_PLAN_MISMATCH", "physical_plan",
                "bounded authority is not the declared public plan",
            )
        executable, compiler_log = compile_verified_bounded_relation_executable(
            authority, contract, abi,
            any_hit_proof_authority=program._proof,
            **options,
        )
        physical_sha = authority.physical.schema.schema_sha256
        backend = {
            "authority": authority,
            "contract": contract,
            "abi": abi,
            "proof": program._proof,
            "executable": executable,
        }
    else:
        from .v4_triangle_standard_library import (
            all_hit_count_schema,
            compile_standard_triangle_program,
            weighted_hit_count_schema,
        )

        assert isinstance(program.protocol, TriangleReductionProtocol)
        schema = (
            weighted_hit_count_schema(program.callback)
            if program.protocol.mode is TriangleReductionMode.WEIGHTED_HIT_COUNT
            else all_hit_count_schema(program.callback)
        )
        standard = compile_standard_triangle_program(
            program.callback, schema, target.profile, program._proof, **options)
        authority = standard.authority
        contract = standard.contract
        abi = standard.abi
        executable = standard.executable
        compiler_log = standard.compiler_log
        if (
            authority.schema.semantic_dict()["geometry_family"]
                != program.physical_plan.geometry_family
            or contract.template_id != program.physical_plan.template_id
            or tuple(contract.role_topology)
                != program.physical_plan.callback_roles
            or authority.schema.reducer.algebra.value
                != program.physical_plan.reducer_algebra
        ):
            _fail(
                "PL034_PHYSICAL_PLAN_MISMATCH", "physical_plan",
                "triangle authority is not the declared public plan",
            )
        physical_sha = authority.schema.schema_sha256
        backend = {
            "authority": authority,
            "contract": contract,
            "abi": abi,
            "proof": standard.proof,
            "executable": executable,
        }
    composed_sha = getattr(getattr(executable, "composed", None), "ptx_sha256", None)
    executable_sha = getattr(executable, "executable_sha256", None)
    _require_sha256(executable_sha, "executable.executable_sha256")
    _require_sha256(composed_sha, "executable.composed.ptx_sha256")
    identity = ProtocolExecutableIdentity(
        program=program.identity,
        target_sha256=target.profile.target_sha256,
        physical_schema_sha256=physical_sha,
        contract_sha256=contract.contract_sha256,
        abi_sha256=abi.abi_sha256,
        generated_executable_sha256=executable_sha,
        composed_ptx_sha256=composed_sha,
        native_library_sha256=target.profile.native_sha256,
    )
    protocol_contract_decision = _materialized_protocol_contract_decision(
        program,
        authority=authority,
        contract=contract,
        abi=abi,
        executable_sha256=executable_sha,
        composed_ptx_sha256=composed_sha,
    )
    if protocol_contract_decision.verdict != "ACCEPT":
        _fail(
            "PL036_PROTOCOL_CONTRACT_REJECTED", "materialize.protocol_contract",
            ",".join(
                finding.reason_id
                for finding in protocol_contract_decision.findings),
        )
    return MaterializedProtocolProgram(
        program=program,
        target=target,
        toolchain=toolchain,
        identity=identity,
        backend=backend,
        compiler_log_sha256=hashlib.sha256(compiler_log.encode("utf-8")).hexdigest(),
        materialize_seconds=time.perf_counter() - started,
        protocol_contract_decision=protocol_contract_decision,
    )


def _load_exact_native_library(target: V4Target):
    """Load only the exact public target path and register its identity."""

    path = target.native_library_path
    before = _file_sha256(path)
    if before != target.profile.native_sha256:
        _fail("PL009_NATIVE_IDENTITY_MISMATCH", "target", "bytes changed before load")
    from . import optix_runtime

    optix_runtime._ensure_cuda_driver_initialized()
    try:
        library = ctypes.CDLL(str(path))
    except OSError as error:
        _fail("PL030_NATIVE_LOAD_FAILED", "target.native_library_path", str(error))
    after = _file_sha256(path)
    if after != before:
        _fail("PL009_NATIVE_IDENTITY_MISMATCH", "target", "bytes changed during load")
    resolved = str(path.resolve())
    library._rtdl_library_path = resolved
    library._rtdl_loaded_library_path = resolved
    library._rtdl_loaded_library_sha256 = after
    from .physical_execution_provenance import _register_loaded_provider_identity

    _register_loaded_provider_identity(library, path, after)
    optix_runtime._register_argtypes(library)
    return library


def _prepare_bounded_relation_backend(backend, static_input, target, library):
    from .v4_bounded_relation_prepared_runtime import prepare_bounded_relation_callback

    return prepare_bounded_relation_callback(
        authority=backend["authority"],
        contract=backend["contract"],
        abi=backend["abi"],
        executable=backend["executable"],
        any_hit_proof_authority=backend["proof"],
        indexed_boxes=static_input.indexed_boxes,
        library=library,
        native_library_path=target.native_library_path,
    )


def _prepare_triangle_reduction_backend(backend, static_input, target, library):
    from .v4_triangle_reduction_prepared_runtime import prepare_triangle_reduction_callback

    return prepare_triangle_reduction_callback(
        authority=backend["authority"],
        contract=backend["contract"],
        abi=backend["abi"],
        any_hit_proof_authority=backend["proof"],
        executable=backend["executable"],
        vertices=static_input.vertices,
        triangles=static_input.triangles,
        metadata=static_input.metadata_dict(),
        event_capacity=static_input.event_capacity,
        library=library,
        native_library_path=target.native_library_path,
    )


class MaterializedProtocolProgram:
    """Single-use target executable that has not yet allocated GPU state."""

    def __init__(
        self,
        *,
        program: VerifiedProtocolProgram,
        target: V4Target,
        toolchain: V4Toolchain,
        identity: ProtocolExecutableIdentity,
        backend: dict[str, object],
        compiler_log_sha256: str,
        materialize_seconds: float,
        protocol_contract_decision: ProtocolContractDecision,
    ) -> None:
        self._program = program
        self._target = target
        self._toolchain = toolchain
        self._identity = identity
        self._backend = backend
        self._compiler_log_sha256 = compiler_log_sha256
        self.materialize_seconds = float(materialize_seconds)
        self._protocol_contract_decision = protocol_contract_decision
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._lock = threading.Lock()
        self._state = "materialized"

    def __getstate__(self):
        raise ProtocolLifecycleError(
            "PL020_NONSERIALIZABLE", "materialized", "cannot be serialized")

    @property
    def identity(self) -> ProtocolExecutableIdentity:
        return self._identity

    @property
    def compiler_log_sha256(self) -> str:
        return self._compiler_log_sha256

    @property
    def protocol_contract_decision(self) -> ProtocolContractDecision:
        return self._protocol_contract_decision

    @property
    def state(self) -> str:
        return self._state

    def _check_thread(self) -> None:
        if os.getpid() != self._pid:
            _fail("PL021_PROCESS_BOUNDARY", "materialized", "crossed process boundary")
        if threading.get_ident() != self._thread:
            _fail("PL022_THREAD_BOUNDARY", "materialized", "crossed thread boundary")

    def prepare(
        self,
        static_input: BoundedRelationStaticInput | TriangleReductionStaticInput,
    ) -> "PreparedProtocolProgram":
        self._check_thread()
        if not self._lock.acquire(blocking=False):
            _fail("PL023_REENTRANT", "materialized.prepare", "already active")
        try:
            if self._state != "materialized":
                _fail("PL024_EXECUTABLE_CONSUMED", "materialized", self._state)
            if self._protocol_contract_decision.verdict != "ACCEPT":
                _fail(
                    "PL036_PROTOCOL_CONTRACT_REJECTED",
                    "materialized.protocol_contract",
                    ",".join(
                        finding.reason_id
                        for finding in self._protocol_contract_decision.findings),
                )
            self._state = "preparing"
            try:
                library = _load_exact_native_library(self._target)
                if self._program.protocol.family is ProtocolFamily.BOUNDED_RELATION:
                    if not isinstance(static_input, BoundedRelationStaticInput):
                        _fail("PL025_STATIC_INPUT_MISMATCH", "static_input", type(static_input).__name__)
                    owner = _prepare_bounded_relation_backend(
                        self._backend, static_input, self._target, library)
                else:
                    if not isinstance(static_input, TriangleReductionStaticInput):
                        _fail("PL025_STATIC_INPUT_MISMATCH", "static_input", type(static_input).__name__)
                    owner = _prepare_triangle_reduction_backend(
                        self._backend, static_input, self._target, library)
            except Exception:
                self._state = "failed"
                raise
            self._state = "prepared"
            return PreparedProtocolProgram(
                family=self._program.protocol.family,
                owner=owner,
                identity=self._identity,
                materialize_seconds=self.materialize_seconds,
                protocol_contract_decision=self._protocol_contract_decision,
            )
        finally:
            self._lock.release()


class PreparedProtocolProgram:
    """Process-local prepared owner with idempotent public cleanup."""

    def __init__(
        self,
        *,
        family: ProtocolFamily,
        owner: object,
        identity: ProtocolExecutableIdentity,
        materialize_seconds: float,
        protocol_contract_decision: ProtocolContractDecision,
    ) -> None:
        self._family = family
        self._owner = owner
        self._identity = identity
        self.materialize_seconds = float(materialize_seconds)
        self._protocol_contract_decision = protocol_contract_decision
        self.prepare_seconds = float(getattr(owner, "prepare_seconds", 0.0))
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._closed = False
        self._execution_count = 0

    def __getstate__(self):
        raise ProtocolLifecycleError(
            "PL020_NONSERIALIZABLE", "prepared", "cannot be serialized")

    @property
    def identity(self) -> ProtocolExecutableIdentity:
        return self._identity

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        self._check_open()
        return {
            "schema": "rtdl.v4.public_protocol_lifecycle.v1",
            "family": self._family.value,
            "executable_identity_sha256": self._identity.identity_sha256,
            "process_bound": True,
            "thread_bound": True,
            "nonserializable": True,
            "nonreentrant": True,
            "idempotent_close": True,
            "materialize_seconds_reported_separately": True,
            "prepare_seconds_reported_separately": True,
            "materialize_seconds": self.materialize_seconds,
            "prepare_seconds": self.prepare_seconds,
            "execution_count": self._execution_count,
            "protocol_contract_verdict": self._protocol_contract_decision.verdict,
            "protocol_contract_decision_sha256": (
                self._protocol_contract_decision.to_mapping()["decision_sha256"]),
        }

    def _check_owner_thread(self) -> None:
        if os.getpid() != self._pid:
            _fail("PL021_PROCESS_BOUNDARY", "prepared", "crossed process boundary")
        if threading.get_ident() != self._thread:
            _fail("PL022_THREAD_BOUNDARY", "prepared", "crossed thread boundary")

    def _check_open(self) -> None:
        self._check_owner_thread()
        if self._closed:
            _fail("PL026_USE_AFTER_CLOSE", "prepared", "is closed")

    def execute(
        self,
        batch: BoundedRelationBatch | TriangleReductionBatch,
    ) -> ProtocolExecutionResult:
        self._check_open()
        if not self._active.acquire(blocking=False):
            _fail("PL023_REENTRANT", "prepared.execute", "already active")
        try:
            if self._family is ProtocolFamily.BOUNDED_RELATION:
                if not isinstance(batch, BoundedRelationBatch):
                    _fail("PL027_BATCH_MISMATCH", "batch", type(batch).__name__)
                raw = self._owner.execute(
                    batch.source_boxes, expected_rows=batch.expected_rows)
                output = raw.rows
                details = {
                    "raw_rows": raw.raw_rows,
                    "raw_event_count": raw.raw_event_count,
                    "duplicate_count": raw.duplicate_count,
                }
            else:
                if not isinstance(batch, TriangleReductionBatch):
                    _fail("PL027_BATCH_MISMATCH", "batch", type(batch).__name__)
                raw = self._owner.execute(
                    batch.queries, query_metadata=batch.metadata_dict())
                output = raw.reduced_output
                details = {
                    "per_ray_u64": raw.per_ray_u64,
                    "raw_reducer_rows": raw.raw_reducer_rows,
                }
            if raw.composed_ptx_sha256 != self._identity.composed_ptx_sha256 \
                    or raw.native_library_sha256 != self._identity.native_library_sha256:
                _fail(
                    "PL028_EXECUTION_IDENTITY_MISMATCH", "result",
                    "executed PTX/native differs from materialized identity",
                )
            if getattr(raw.launch_status, "native_validated_all_ok", False) is not True:
                required_status = {"first_error_claimed", "error_code"}
                if any(not required_status.issubset(row)
                       for row in raw.launch_status):
                    _fail(
                        "PL029_DEVICE_STATUS_INVALID", "result.launch_status",
                        "status row lacks the public failure fields",
                    )
                if any(int(row["first_error_claimed"]) or int(row["error_code"])
                       for row in raw.launch_status):
                    _fail(
                        "PL029_DEVICE_STATUS_INVALID", "result.launch_status",
                        "device failure cannot produce an application result",
                    )
            output_sha256 = _require_sha256(
                raw.output_sha256, "result.output_sha256")
            if _digest(output) != output_sha256:
                _fail(
                    "PL031_OUTPUT_IDENTITY_MISMATCH", "result.output_sha256",
                    "public output bytes do not match the backend digest",
                )
            receipt = dict(raw.traversal_receipt)
            expected_route = (
                "v4_callback_ir:custom_aabb_bounded_relation_v1"
                if self._family is ProtocolFamily.BOUNDED_RELATION else
                "v4_builtin_triangle_callback_ir:checked_reduction_v1"
            )
            if (
                receipt.get("physical_executor_classification")
                    != "optix_traversal_observed"
                or receipt.get("provider_library_sha256")
                    != self._identity.native_library_sha256
                or receipt.get("output_digest") != output_sha256
                or receipt.get("route_identity") != expected_route
                or receipt.get("expected_program_observed_at_receipt_edge") is not True
            ):
                _fail(
                    "PL032_TRAVERSAL_RECEIPT_INVALID", "result.traversal_receipt",
                    "receipt does not bind executor, route, native and output",
                )
            _require_sha256(
                receipt.get("receipt_sha256"),
                "result.traversal_receipt.receipt_sha256",
            )
            receipt_body = dict(receipt)
            receipt_sha256 = receipt_body.pop("receipt_sha256")
            if _digest(receipt_body) != receipt_sha256:
                _fail(
                    "PL032_TRAVERSAL_RECEIPT_INVALID", "result.traversal_receipt",
                    "receipt self-digest does not reproduce",
                )
            result = ProtocolExecutionResult(
                output=output,
                launch_status=raw.launch_status,
                role_counters=tuple(int(item) for item in raw.role_counters),
                traversal_receipt=receipt,
                output_sha256=output_sha256,
                executable_identity=self._identity,
                details=details,
            )
            self._execution_count += 1
            return result
        finally:
            self._active.release()

    def close(self) -> None:
        if self._closed:
            return
        self._check_owner_thread()
        if not self._active.acquire(blocking=False):
            _fail("PL023_REENTRANT", "prepared.close", "execute is active")
        try:
            if self._closed:
                return
            try:
                self._owner.close()
            finally:
                # A destroy failure leaves no safe public object to reuse.
                self._closed = True
        finally:
            self._active.release()

    def __enter__(self) -> "PreparedProtocolProgram":
        self._check_open()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


__all__ = [
    "AnyHitProtocolProof",
    "BoundedRelationBatch",
    "BoundedRelationProtocol",
    "BoundedRelationStaticInput",
    "MaterializedProtocolProgram",
    "PreparedProtocolProgram",
    "ProtocolExecutableIdentity",
    "ProtocolExecutionResult",
    "ProtocolFamily",
    "ProtocolLifecycleError",
    "ProtocolPhysicalPlan",
    "ProtocolProgramIdentity",
    "TriangleReductionBatch",
    "TriangleReductionMode",
    "TriangleReductionProtocol",
    "TriangleReductionStaticInput",
    "V4Target",
    "V4Toolchain",
    "VerifiedProtocolProgram",
    "compile_protocol_program",
    "materialize_protocol_program",
    "standard_protocol_physical_plan",
]
