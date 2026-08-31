"""Public lifecycle for user-authored restricted built-in-triangle callbacks.

This module exposes the already-existing generic Callback-IR-to-OptiX path
without adding another named application family.  The current executable
template is intentionally narrow: one static built-in-triangle GAS, a
``Query(origin, direction, tmax)`` input, exactly three ``u32`` payload and
output fields, and two primitive-aligned read-only ``u32`` metadata views.
Within that shape, callback source, manifest, record field names, expressions,
and physical field identifiers are supplied by the user and are compiled from
verified Callback IR.  User code never supplies PTX, SBT records, a pipeline,
or a native/provider callback.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import threading
from typing import Mapping

from .v4_callback_abi import CompiledCallbackAbi, compile_callback_abi
from .v4_callback_frontend import parse_callback_source
from .v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackModuleManifest,
    CallbackRole,
    VerifiedCallbackProgram,
)
from .v4_callback_lifecycle import V4Target, V4Toolchain
from .v4_protocol_contract import (
    CompilerProtocolProjection,
    ProtocolContractDecision,
    ProtocolContractDeclaration,
    verify_protocol_contract,
)
from .v4_typed_physical_schema import (
    AdjacencySide,
    BufferAccess,
    BufferDomain,
    BufferFieldSchema,
    BufferSemantic,
    CanonicalPhysicalPlan,
    CountRelation,
    GasSchema,
    GasUpdatePolicy,
    GeometryFamily,
    HitChannelProducer,
    HitChannelSchema,
    HitChannelSemantic,
    HitMetadataBinding,
    PhysicalValueType,
    ReferenceTemplateId,
    TriangleOrientationAuthority,
    TriangleWindingPolicy,
    TypedPhysicalSchemaV1,
    VerifiedPhysicalSchemaAuthority,
    default_reference_templates,
    lower_canonical_reference_plan,
    triangle_author_semantics_sha256,
    verify_callback_program_for_geometry,
    verify_typed_physical_schema,
)


_CONSTRUCTION_TOKEN = object()
_EXPECTED_PREPARED_RUNTIME_SHA256 = (
    "e79d599040be5695892f10fcd0e5138c5aab27f3622bbf1436456f047bdfa12a"
)
_EXPECTED_PREPARED_RUNTIME_SYMBOLS = (
    "rtdl_optix_v4_prepare_builtin_triangle_callback_v1",
    "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_v1",
    "rtdl_optix_v4_destroy_prepared_builtin_triangle_callback_v1",
)


class PublicCallbackLifecycleError(RuntimeError):
    """Stable fail-closed diagnostic for the public generic lifecycle."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise PublicCallbackLifecycleError(code, path, message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


_BULK_U32X3_DIGEST_DOMAIN = (
    b"rtdl.v4.builtin_triangle.bulk_output.u32x3.v1\x00"
)


def _bulk_u32x3_digest(value: object) -> str:
    """Independently hash exact bulk-output bytes without Python row objects."""

    try:
        import numpy as _np
    except ImportError:  # pragma: no cover - bulk construction already requires it
        _fail(
            "GC025_OUTPUT_IDENTITY_MISMATCH", "execute.output",
            "bulk output identity requires NumPy",
        )
    if not isinstance(value, _np.ndarray) \
            or value.ndim != 2 or value.shape[1] != 3 \
            or value.dtype.str != "<u4" or not value.flags.c_contiguous:
        _fail(
            "GC025_OUTPUT_IDENTITY_MISMATCH", "execute.output",
            "bulk execution did not return a contiguous little-endian Nx3 u32 array",
        )
    digest = hashlib.sha256()
    digest.update(_BULK_U32X3_DIGEST_DOMAIN)
    digest.update(int(value.shape[0]).to_bytes(8, "little", signed=False))
    digest.update(memoryview(value).cast("B"))
    return digest.hexdigest()


def _source_text_sha256(path: Path) -> str:
    """Hash Python source semantics without checkout newline transport noise."""

    # Git export/check-out policy may transport the same Python source with LF
    # or CRLF bytes.  Python itself reads both through universal-newline mode.
    # Bind that exact parser-visible UTF-8 text, while retaining raw file hashes
    # separately in evidence manifests for byte custody.
    with path.open("r", encoding="utf-8", newline=None) as stream:
        source = stream.read()
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass(frozen=True)
class BuiltinTriangleU32x3FieldIds:
    """User-selected physical field identifiers for the reviewed template."""

    vertex_positions: str
    triangle_indices: str
    first_primitive_values: str
    second_primitive_values: str
    queries: str
    outputs: str
    status: str

    def __post_init__(self) -> None:
        values = tuple(getattr(self, field) for field in self.__dataclass_fields__)
        if any(not isinstance(value, str) or not value for value in values):
            _fail("GC028_FIELD_ID_INVALID", "field_ids", "nonempty strings required")
        if len(values) != len(set(values)):
            _fail("GC028_FIELD_ID_INVALID", "field_ids", "field IDs must be unique")


@dataclass(frozen=True)
class BuiltinTriangleOrientationDeclaration:
    """Explicit user declaration for target front/back orientation semantics."""

    contract_name: str
    independent_cpu_oracle_sha256: str
    winding_policy: TriangleWindingPolicy
    front_hit_kind: int
    back_hit_kind: int
    callback_front_hit_kind_constant: str
    callback_back_hit_kind_constant: str
    front_hit_selects: AdjacencySide
    back_hit_selects: AdjacencySide

    def __post_init__(self) -> None:
        if not isinstance(self.contract_name, str) or not self.contract_name:
            _fail(
                "GC030_ORIENTATION_DECLARATION_INVALID", "orientation.contract_name",
                "nonempty string required",
            )
        if not _is_sha256(self.independent_cpu_oracle_sha256):
            _fail(
                "GC030_ORIENTATION_DECLARATION_INVALID",
                "orientation.independent_cpu_oracle_sha256", "sha256 required",
            )
        if not isinstance(self.winding_policy, TriangleWindingPolicy):
            _fail(
                "GC030_ORIENTATION_DECLARATION_INVALID", "orientation.winding_policy",
                type(self.winding_policy).__name__,
            )
        for name, value in (
            ("front_hit_kind", self.front_hit_kind),
            ("back_hit_kind", self.back_hit_kind),
        ):
            if not isinstance(value, int) or isinstance(value, bool) \
                    or value < 0 or value > 0xFF:
                _fail(
                    "GC030_ORIENTATION_DECLARATION_INVALID", f"orientation.{name}",
                    "u8 integer required",
                )
        if self.front_hit_kind == self.back_hit_kind:
            _fail(
                "GC030_ORIENTATION_DECLARATION_INVALID", "orientation.hit_kinds",
                "front and back hit kinds must differ",
            )
        for name, value in (
            ("callback_front_hit_kind_constant", self.callback_front_hit_kind_constant),
            ("callback_back_hit_kind_constant", self.callback_back_hit_kind_constant),
        ):
            if not isinstance(value, str) or not value:
                _fail(
                    "GC030_ORIENTATION_DECLARATION_INVALID", f"orientation.{name}",
                    "nonempty constant name required",
                )
        if self.front_hit_selects is not AdjacencySide.FRONT \
                or self.back_hit_selects is not AdjacencySide.BACK:
            _fail(
                "GC030_ORIENTATION_DECLARATION_INVALID", "orientation.adjacency",
                "reviewed v1 requires front-to-FRONT and back-to-BACK",
            )


@dataclass(frozen=True)
class BuiltinTriangleCallbackPhysicalPlan:
    """User-authored typed plan plus its external orientation authority."""

    schema: TypedPhysicalSchemaV1
    orientation_authority: TriangleOrientationAuthority

    def __post_init__(self) -> None:
        if not isinstance(self.schema, TypedPhysicalSchemaV1):
            _fail("GC001_PLAN_REQUIRED", "physical_plan.schema", type(self.schema).__name__)
        if not isinstance(self.orientation_authority, TriangleOrientationAuthority):
            _fail(
                "GC001_PLAN_REQUIRED", "physical_plan.orientation_authority",
                type(self.orientation_authority).__name__,
            )
        if self.schema.geometry_family is not GeometryFamily.BUILTIN_TRIANGLE:
            _fail(
                "GC002_TEMPLATE_UNSUPPORTED", "physical_plan.schema.geometry_family",
                self.schema.geometry_family.value,
            )
        if self.schema.triangle_orientation_authority_sha256 \
                != self.orientation_authority.authority_sha256:
            _fail(
                "GC003_ORIENTATION_BINDING", "physical_plan.schema",
                "schema does not bind the supplied orientation authority",
            )

    @property
    def plan_sha256(self) -> str:
        return _digest({
            "schema_sha256": self.schema.schema_sha256,
            "orientation_authority_sha256": self.orientation_authority.authority_sha256,
        })


def build_builtin_triangle_u32x3_physical_plan(
    verified_source: "VerifiedBuiltinTriangleCallbackSource",
    *,
    field_ids: BuiltinTriangleU32x3FieldIds,
    orientation: BuiltinTriangleOrientationDeclaration,
    first_metadata_argument_index: int,
    second_metadata_argument_index: int,
) -> BuiltinTriangleCallbackPhysicalPlan:
    """Build the reviewed physical template without caller-computed hashes.

    Types, access modes, count relations, hit-channel producers, GAS shape,
    and the u32x3 ceiling are properties of the reviewed backend template.
    The caller still names every physical field, explicitly binds each trailing
    closest-hit metadata view, and declares the orientation semantics and CPU
    oracle identity.  Callback/effect/source hashes are derived from the live
    verified source rather than copied from user input.
    """

    if not isinstance(verified_source, VerifiedBuiltinTriangleCallbackSource):
        _fail("GC005_VERIFIED_SOURCE_REQUIRED", "verified_source", type(verified_source).__name__)
    if not isinstance(field_ids, BuiltinTriangleU32x3FieldIds):
        _fail("GC001_PLAN_REQUIRED", "field_ids", type(field_ids).__name__)
    if not isinstance(orientation, BuiltinTriangleOrientationDeclaration):
        _fail("GC001_PLAN_REQUIRED", "orientation", type(orientation).__name__)
    for name, index in (
        ("first_metadata_argument_index", first_metadata_argument_index),
        ("second_metadata_argument_index", second_metadata_argument_index),
    ):
        if not isinstance(index, int) or isinstance(index, bool) or index < 2:
            _fail("GC029_METADATA_ARGUMENT_INVALID", name, repr(index))
    if first_metadata_argument_index == second_metadata_argument_index:
        _fail(
            "GC029_METADATA_ARGUMENT_INVALID", "metadata_argument_indices",
            "two distinct trailing arguments are required",
        )
    callback = verified_source.callback
    authority = TriangleOrientationAuthority(
        contract_name=orientation.contract_name,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        vertex_positions_semantic=BufferSemantic.VERTEX_POSITIONS,
        triangle_indices_semantic=BufferSemantic.TRIANGLE_INDICES,
        front_values_semantic=BufferSemantic.PRIMITIVE_FRONT_VALUE,
        back_values_semantic=BufferSemantic.PRIMITIVE_BACK_VALUE,
        winding_policy=orientation.winding_policy,
        front_hit_kind=orientation.front_hit_kind,
        back_hit_kind=orientation.back_hit_kind,
        callback_front_hit_kind_constant=orientation.callback_front_hit_kind_constant,
        callback_back_hit_kind_constant=orientation.callback_back_hit_kind_constant,
        front_hit_selects=orientation.front_hit_selects,
        back_hit_selects=orientation.back_hit_selects,
        author_source_sha256=verified_source.source_sha256,
        author_semantics_sha256=triangle_author_semantics_sha256(
            front_hit_kind=orientation.front_hit_kind,
            back_hit_kind=orientation.back_hit_kind,
            front_hit_selects=orientation.front_hit_selects,
            back_hit_selects=orientation.back_hit_selects,
        ),
        independent_cpu_oracle_sha256=orientation.independent_cpu_oracle_sha256,
    )
    read_only = BufferAccess.READ_ONLY
    hit_roles = (CallbackRole.CLOSEST_HIT,)
    schema = TypedPhysicalSchemaV1(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        geometry_family=GeometryFamily.BUILTIN_TRIANGLE,
        buffers=(
            BufferFieldSchema(field_ids.vertex_positions, BufferSemantic.VERTEX_POSITIONS, BufferDomain.VERTEX, PhysicalValueType.VEC3F32, read_only, CountRelation.VERTEX_COUNT, 16),
            BufferFieldSchema(field_ids.triangle_indices, BufferSemantic.TRIANGLE_INDICES, BufferDomain.PRIMITIVE, PhysicalValueType.VEC3U32, read_only, CountRelation.PRIMITIVE_COUNT, 16),
            BufferFieldSchema(field_ids.first_primitive_values, BufferSemantic.PRIMITIVE_FRONT_VALUE, BufferDomain.PRIMITIVE, PhysicalValueType.U32, read_only, CountRelation.PRIMITIVE_COUNT),
            BufferFieldSchema(field_ids.second_primitive_values, BufferSemantic.PRIMITIVE_BACK_VALUE, BufferDomain.PRIMITIVE, PhysicalValueType.U32, read_only, CountRelation.PRIMITIVE_COUNT),
            BufferFieldSchema(field_ids.queries, BufferSemantic.QUERY_INPUT, BufferDomain.QUERY, PhysicalValueType.OPAQUE_RECORD, read_only, CountRelation.QUERY_COUNT, 16),
            BufferFieldSchema(field_ids.outputs, BufferSemantic.OUTPUT_VALUE, BufferDomain.OUTPUT, PhysicalValueType.OPAQUE_RECORD, BufferAccess.WRITE_ONLY, CountRelation.OUTPUT_COUNT_EQUALS_QUERY_COUNT, 16),
            BufferFieldSchema(field_ids.status, BufferSemantic.STATUS, BufferDomain.LAUNCH_PARAM, PhysicalValueType.STATUS_RECORD, BufferAccess.INTERNAL_STATUS, CountRelation.SINGLETON, 16),
        ),
        hit_channels=(
            HitChannelSchema(HitChannelSemantic.PRIMITIVE_INDEX, PhysicalValueType.U32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
            HitChannelSchema(HitChannelSemantic.TRIANGLE_FRONT_BACK_HIT_KIND, PhysicalValueType.U32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
            HitChannelSchema(HitChannelSemantic.TRIANGLE_BARYCENTRICS, PhysicalValueType.VEC2F32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
            HitChannelSchema(HitChannelSemantic.PRIMITIVE_METADATA, PhysicalValueType.U32, HitChannelProducer.COMPILER_METADATA_LOOKUP, hit_roles),
        ),
        hit_metadata_bindings=(
            HitMetadataBinding(CallbackRole.CLOSEST_HIT, first_metadata_argument_index, BufferSemantic.PRIMITIVE_FRONT_VALUE),
            HitMetadataBinding(CallbackRole.CLOSEST_HIT, second_metadata_argument_index, BufferSemantic.PRIMITIVE_BACK_VALUE),
        ),
        gas=GasSchema(
            GeometryFamily.BUILTIN_TRIANGLE,
            (BufferSemantic.VERTEX_POSITIONS, BufferSemantic.TRIANGLE_INDICES),
            GasUpdatePolicy.STATIC,
            1,
            1,
        ),
        triangle_winding=orientation.winding_policy,
        triangle_orientation_authority_sha256=authority.authority_sha256,
    )
    return BuiltinTriangleCallbackPhysicalPlan(schema, authority)


def _exact_contiguous_column(
    value: object,
    *,
    path: str,
    dtype_string: str,
    trailing_width: int | None,
) -> object | None:
    """Return a zero-copy NumPy view for a shaped buffer, or ``None``.

    Lists and tuples deliberately remain on the original small-input route.
    Anything exporting the buffer protocol, however, is treated as an
    explicit bulk-input request and must already have the native ABI's exact
    dtype, byte order, shape, and C contiguity.  The public boundary never
    silently casts or copies a multi-million-row input.
    """

    try:
        view = memoryview(value)
    except TypeError:
        return None
    try:
        import numpy as _np
    except ImportError:  # pragma: no cover - V4 target environments pin NumPy
        _fail(
            "GC031_BULK_INPUT_INVALID", path,
            "NumPy is required to consume a public bulk buffer",
        )
    try:
        # Going through memoryview makes the zero-copy ownership relation
        # explicit and avoids invoking a user-defined Python iterator.
        array = _np.asarray(view)
    except (TypeError, ValueError, BufferError) as error:
        _fail("GC031_BULK_INPUT_INVALID", path, f"invalid shaped buffer: {error}")
    expected_ndim = 1 if trailing_width is None else 2
    if array.ndim != expected_ndim:
        _fail(
            "GC031_BULK_INPUT_INVALID", path,
            f"expected {expected_ndim} dimensions, observed {array.ndim}",
        )
    if trailing_width is not None and array.shape[1] != trailing_width:
        _fail(
            "GC031_BULK_INPUT_INVALID", path,
            f"expected shape (N,{trailing_width}), observed {tuple(array.shape)}",
        )
    if array.dtype.str != dtype_string:
        _fail(
            "GC031_BULK_INPUT_INVALID", path,
            f"expected exact little-endian {dtype_string}, observed {array.dtype.str}",
        )
    if not bool(array.flags.c_contiguous):
        _fail(
            "GC031_BULK_INPUT_INVALID", path,
            "C-contiguous buffer required; implicit packing is forbidden",
        )
    return array


@dataclass(frozen=True)
class BuiltinTriangleCallbackStaticInput:
    vertices: object
    triangles: object
    first_primitive_values: object
    second_primitive_values: object

    def __post_init__(self) -> None:
        bulk = (
            _exact_contiguous_column(
                self.vertices, path="static_input.vertices",
                dtype_string="<f4", trailing_width=3),
            _exact_contiguous_column(
                self.triangles, path="static_input.triangles",
                dtype_string="<u4", trailing_width=3),
            _exact_contiguous_column(
                self.first_primitive_values,
                path="static_input.first_primitive_values",
                dtype_string="<u4", trailing_width=None),
            _exact_contiguous_column(
                self.second_primitive_values,
                path="static_input.second_primitive_values",
                dtype_string="<u4", trailing_width=None),
        )
        if any(item is not None for item in bulk):
            if not all(item is not None for item in bulk):
                _fail(
                    "GC031_BULK_INPUT_INVALID", "static_input",
                    "bulk static input requires all four fields as exact buffers",
                )
            vertices, triangles, first_values, second_values = bulk
            if len(vertices) == 0:
                _fail("GC031_BULK_INPUT_INVALID", "static_input.vertices", "rows required")
            if len(triangles) == 0:
                _fail("GC031_BULK_INPUT_INVALID", "static_input.triangles", "rows required")
            if len(first_values) != len(triangles) \
                    or len(second_values) != len(triangles):
                _fail(
                    "GC031_BULK_INPUT_INVALID", "static_input.primitive_values",
                    "front/back metadata cardinality must equal triangle count",
                )
            object.__setattr__(self, "vertices", vertices)
            object.__setattr__(self, "triangles", triangles)
            object.__setattr__(self, "first_primitive_values", first_values)
            object.__setattr__(self, "second_primitive_values", second_values)
            return

        # Preserve the original ergonomic route and exact public behaviour for
        # small Python sequences.
        object.__setattr__(self, "vertices", tuple(tuple(row) for row in self.vertices))
        object.__setattr__(
            self, "triangles", tuple(tuple(int(item) for item in row) for row in self.triangles),
        )
        object.__setattr__(
            self, "first_primitive_values", tuple(int(item) for item in self.first_primitive_values),
        )
        object.__setattr__(
            self, "second_primitive_values", tuple(int(item) for item in self.second_primitive_values),
        )

    @property
    def uses_contiguous_columns(self) -> bool:
        """Whether prepare will take the runtime's object-free column route."""

        return not isinstance(self.vertices, tuple)


@dataclass(frozen=True)
class BuiltinTriangleCallbackBatch:
    queries: object

    def __post_init__(self) -> None:
        bulk = _exact_contiguous_column(
            self.queries, path="batch.queries",
            dtype_string="<f4", trailing_width=7,
        )
        if bulk is not None:
            if len(bulk) == 0:
                _fail("GC031_BULK_INPUT_INVALID", "batch.queries", "rows required")
            object.__setattr__(self, "queries", bulk)
            return
        object.__setattr__(
            self, "queries",
            tuple((tuple(origin), tuple(direction), tmax)
                  for origin, direction, tmax in self.queries),
        )

    @property
    def uses_contiguous_columns(self) -> bool:
        """Whether execute requests NumPy-column output from the runtime."""

        return not isinstance(self.queries, tuple)


@dataclass(frozen=True)
class BuiltinTriangleCallbackProgramIdentity:
    source_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    physical_plan_sha256: str
    target_sha256: str

    @property
    def identity_sha256(self) -> str:
        return _digest({
            "source_sha256": self.source_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "physical_plan_sha256": self.physical_plan_sha256,
            "target_sha256": self.target_sha256,
        })


@dataclass(frozen=True)
class BuiltinTriangleCallbackExecutableIdentity:
    program_identity_sha256: str
    physical_schema_sha256: str
    canonical_plan_sha256: str
    callback_abi_sha256: str
    wrapper_source_sha256: str
    generated_executable_sha256: str
    composed_ptx_sha256: str
    native_library_sha256: str

    @property
    def identity_sha256(self) -> str:
        return _digest({
            "program_identity_sha256": self.program_identity_sha256,
            "physical_schema_sha256": self.physical_schema_sha256,
            "canonical_plan_sha256": self.canonical_plan_sha256,
            "callback_abi_sha256": self.callback_abi_sha256,
            "wrapper_source_sha256": self.wrapper_source_sha256,
            "generated_executable_sha256": self.generated_executable_sha256,
            "composed_ptx_sha256": self.composed_ptx_sha256,
            "native_library_sha256": self.native_library_sha256,
        })


@dataclass(frozen=True)
class BuiltinTriangleCallbackExecutionResult:
    output: object
    hit_observations: tuple[dict[str, int | float | None], ...]
    role_counters: tuple[int, ...]
    launch_status: tuple[dict[str, int], ...]
    traversal_receipt: dict[str, object]
    output_sha256: str
    executable_identity: BuiltinTriangleCallbackExecutableIdentity
    protocol_contract_decision: ProtocolContractDecision


class VerifiedBuiltinTriangleCallbackSource:
    """Target-neutral verified source; created only by the public verifier."""

    def __init__(
        self, source: str, manifest: CallbackModuleManifest,
        callback: VerifiedCallbackProgram,
        *, _construction_token: object,
    ) -> None:
        if _construction_token is not _CONSTRUCTION_TOKEN:
            _fail("GC027_LIVE_AUTHORITY_REQUIRED", "verified_source", "use the public verifier")
        self._source = source
        self._manifest = manifest
        self._callback = callback
        self._source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()

    @property
    def callback(self) -> VerifiedCallbackProgram:
        return self._callback

    @property
    def source_sha256(self) -> str:
        return self._source_sha256

    def compile(
        self, *, physical_plan: BuiltinTriangleCallbackPhysicalPlan,
        target: V4Target,
    ) -> "VerifiedBuiltinTriangleCallbackProgram":
        return compile_builtin_triangle_callback_program(
            self, physical_plan=physical_plan, target=target)


def verify_builtin_triangle_callback_source(
    source: str,
    manifest: CallbackModuleManifest,
) -> VerifiedBuiltinTriangleCallbackSource:
    """Parse text without executing it and verify built-in-triangle roles."""

    if not isinstance(manifest, CallbackModuleManifest):
        _fail("GC004_MANIFEST_REQUIRED", "manifest", type(manifest).__name__)
    spec = parse_callback_source(
        source, manifest,
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    )
    callback = verify_callback_program_for_geometry(
        spec, GeometryFamily.BUILTIN_TRIANGLE)
    return VerifiedBuiltinTriangleCallbackSource(
        source, manifest, callback, _construction_token=_CONSTRUCTION_TOKEN)


class VerifiedBuiltinTriangleCallbackProgram:
    """Verified source, typed physical authority, and target-neutral ABI."""

    def __init__(
        self, *, verified_source: VerifiedBuiltinTriangleCallbackSource,
        physical_plan: BuiltinTriangleCallbackPhysicalPlan,
        target: V4Target,
        authority: VerifiedPhysicalSchemaAuthority,
        canonical_plan: CanonicalPhysicalPlan,
        abi: CompiledCallbackAbi,
        expected_wrapper: object,
        _construction_token: object,
    ) -> None:
        if _construction_token is not _CONSTRUCTION_TOKEN:
            _fail("GC027_LIVE_AUTHORITY_REQUIRED", "program", "use the public compiler")
        self._verified_source = verified_source
        self._physical_plan = physical_plan
        self._target = target
        self._authority = authority
        self._canonical_plan = canonical_plan
        self._abi = abi
        self._expected_wrapper = expected_wrapper
        self._declared_physical_bindings = _declared_physical_facts(
            authority,
            canonical_plan,
            expected_wrapper,
            abi,
        )
        self._identity = BuiltinTriangleCallbackProgramIdentity(
            source_sha256=verified_source.source_sha256,
            callback_ir_sha256=authority.callback.ir_sha256,
            effect_digest=authority.callback.effect_digest,
            physical_plan_sha256=physical_plan.plan_sha256,
            target_sha256=target.profile.target_sha256,
        )

    @property
    def callback(self) -> VerifiedCallbackProgram:
        return self._authority.callback

    @property
    def physical_plan(self) -> BuiltinTriangleCallbackPhysicalPlan:
        return self._physical_plan

    @property
    def identity(self) -> BuiltinTriangleCallbackProgramIdentity:
        return self._identity

    def materialize(
        self, *, toolchain: V4Toolchain,
    ) -> "MaterializedBuiltinTriangleCallbackProgram":
        return materialize_builtin_triangle_callback_program(
            self, toolchain=toolchain)


def compile_builtin_triangle_callback_program(
    verified_source: VerifiedBuiltinTriangleCallbackSource,
    *,
    physical_plan: BuiltinTriangleCallbackPhysicalPlan,
    target: V4Target,
) -> VerifiedBuiltinTriangleCallbackProgram:
    """Bind user source to a typed target plan and validate the v1 shape.

    This phase performs no native load, NVRTC invocation, GPU allocation, or
    launch.  Reverification means a source mutation cannot reuse a stale plan.
    """

    if not isinstance(verified_source, VerifiedBuiltinTriangleCallbackSource):
        _fail("GC005_VERIFIED_SOURCE_REQUIRED", "verified_source", type(verified_source).__name__)
    if not isinstance(physical_plan, BuiltinTriangleCallbackPhysicalPlan):
        _fail("GC001_PLAN_REQUIRED", "physical_plan", type(physical_plan).__name__)
    if not isinstance(target, V4Target):
        _fail("GC006_TARGET_REQUIRED", "target", type(target).__name__)
    fresh = verify_builtin_triangle_callback_source(
        verified_source._source, verified_source._manifest)
    if fresh.callback != verified_source.callback \
            or fresh.source_sha256 != verified_source.source_sha256:
        _fail("GC007_SOURCE_IDENTITY_DRIFT", "verified_source", "source does not reverify")
    authority = verify_typed_physical_schema(
        fresh.callback,
        physical_plan.schema,
        target=target.profile,
        orientation_authorities={
            physical_plan.orientation_authority.authority_sha256:
                physical_plan.orientation_authority,
        },
    )
    canonical_plan = lower_canonical_reference_plan(
        authority, default_reference_templates())
    if canonical_plan.template_id is not ReferenceTemplateId.BUILTIN_TRIANGLE_V1:
        _fail("GC002_TEMPLATE_UNSUPPORTED", "physical_plan", canonical_plan.template_id.value)
    abi = compile_callback_abi(
        fresh.callback, physical_schema_authority=authority)
    # Pure code generation is the earliest exact check of the deliberately
    # narrow u32x3/query/two-view executable template.  It does not invoke a
    # compiler or load a provider.
    from .v4_triangle_optix_wrapper_codegen import (
        generate_trusted_optix_triangle_wrapper_v1,
    )
    expected_wrapper = generate_trusted_optix_triangle_wrapper_v1(
        authority, canonical_plan, abi)
    return VerifiedBuiltinTriangleCallbackProgram(
        verified_source=fresh,
        physical_plan=physical_plan,
        target=target,
        authority=authority,
        canonical_plan=canonical_plan,
        abi=abi,
        expected_wrapper=expected_wrapper,
        _construction_token=_CONSTRUCTION_TOKEN,
    )


def _record_signature(callback: VerifiedCallbackProgram, name: str) -> tuple[tuple[str, str], ...]:
    record = next((item for item in callback.program.records if item.name == name), None)
    if record is None:
        _fail("GC008_RECORD_MISSING", "callback.records", name)
    rows = []
    for field in record.fields:
        description = field.value_type.to_dict()
        scalar = description.get("scalar")
        if description.get("kind") != "scalar" or not isinstance(scalar, str):
            rows.append((field.name, "INVALID_NONSCALAR_FIELD"))
        else:
            rows.append((field.name, scalar))
    return tuple(rows)


def _declared_role_effects(callback: VerifiedCallbackProgram) -> dict[str, tuple[str, ...]]:
    def walk(value: object, effects: set[str]) -> None:
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

    result: dict[str, tuple[str, ...]] = {}
    for function in callback.program.functions:
        if function.role is not None:
            effects: set[str] = set()
            walk(function.to_dict().get("body"), effects)
            result[function.role.value] = tuple(sorted(effects))
    return result


def _compiled_role_effects(abi: CompiledCallbackAbi) -> dict[str, tuple[str, ...]]:
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


def _abi_effect_signature(
    abi: CompiledCallbackAbi,
    role_name: str,
    effect_name: str,
    prefix: str,
) -> tuple[tuple[str, str], ...]:
    role = next((item for item in abi.roles if item.role.value == role_name), None)
    if role is None:
        return ()
    variant = next((item for item in role.effects if item.kind.value == effect_name), None)
    if variant is None:
        return ()
    rows = []
    for field in variant.fields:
        if field.path.startswith(prefix):
            rows.append((field.path[len(prefix):], field.scalar))
    return tuple(rows)


def _declared_ownership(callback: VerifiedCallbackProgram) -> dict[str, str]:
    manifest = callback.program.manifest
    payload = _digest(_record_signature(callback, manifest.payload_record))
    output = _digest(_record_signature(callback, manifest.output_record))
    attributes = (
        "compiler_owned_builtin_triangle_channels;user_attribute_slots=0"
        if not manifest.attribute_types
        else "INVALID_USER_ATTRIBUTE_SLOTS"
    )
    return {
        "make_ray_payload": payload,
        "closest_hit_payload": payload,
        "miss_payload": payload,
        "finalize_output": output,
        "attribute_channels": attributes,
    }


def _projected_ownership(
    authority: VerifiedPhysicalSchemaAuthority,
    abi: CompiledCallbackAbi,
) -> dict[str, str]:
    return {
        "make_ray_payload": _digest(_abi_effect_signature(
            abi, "make_ray", "trace_request", "out.trace_request.payload.")),
        "closest_hit_payload": _digest(_abi_effect_signature(
            abi, "closest_hit", "payload", "out.payload.payload.")),
        "miss_payload": _digest(_abi_effect_signature(
            abi, "miss", "payload", "out.payload.payload.")),
        "finalize_output": _digest(_abi_effect_signature(
            abi, "finalize", "output", "out.output.value.")),
        "attribute_channels": (
            "compiler_owned_builtin_triangle_channels;user_attribute_slots=0"
            if not authority.callback.program.manifest.attribute_types
            else "INVALID_USER_ATTRIBUTE_SLOTS"
        ),
    }


def _declared_runtime_binding_facts() -> dict[str, str]:
    """Frozen reviewed host-runtime authority, independent of live bytes."""

    return {
        "prepared_runtime_sha256": _EXPECTED_PREPARED_RUNTIME_SHA256,
        "native_prepare_symbol": _EXPECTED_PREPARED_RUNTIME_SYMBOLS[0],
        "native_execute_symbol": _EXPECTED_PREPARED_RUNTIME_SYMBOLS[1],
        "native_destroy_symbol": _EXPECTED_PREPARED_RUNTIME_SYMBOLS[2],
    }


def _projected_runtime_binding_facts() -> dict[str, str]:
    """Rehash and extract the host runtime that will actually prepare/execute."""

    runtime_path = Path(__file__).with_name("v4_triangle_prepared_runtime.py")
    runtime_source = runtime_path.read_text(encoding="utf-8")
    return {
        "prepared_runtime_sha256": _source_text_sha256(runtime_path),
        "native_prepare_symbol": (
            "rtdl_optix_v4_prepare_builtin_triangle_callback_v1"
            if "rtdl_optix_v4_prepare_builtin_triangle_callback_v1" in runtime_source
            else "MISSING_PREPARE_SYMBOL"
        ),
        "native_execute_symbol": (
            "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_v1"
            if "rtdl_optix_v4_execute_prepared_builtin_triangle_callback_v1" in runtime_source
            else "MISSING_EXECUTE_SYMBOL"
        ),
        "native_destroy_symbol": (
            "rtdl_optix_v4_destroy_prepared_builtin_triangle_callback_v1"
            if "rtdl_optix_v4_destroy_prepared_builtin_triangle_callback_v1" in runtime_source
            else "MISSING_DESTROY_SYMBOL"
        ),
    }


def _wrapper_binding_facts(wrapper: object) -> dict[str, str]:
    source = str(getattr(wrapper, "source", ""))
    template = str(getattr(wrapper, "physical_template", ""))
    expected_fragments = {
        "vertices": "const float3* vertices",
        "triangle_indices": "const uint3* triangle_indices",
        "first_primitive_values": "const unsigned int* front_values",
        "second_primitive_values": "const unsigned int* back_values",
        "query_origin": "const float* query_ox",
        "query_direction": "const float* query_dx",
        "query_tmax": "const float* query_tmax",
        "output_u32x3": "unsigned int* output_0; unsigned int* output_1; unsigned int* output_2",
        "per_query_status": "V4TriangleLaunchStatus* status",
    }
    return {
        "wrapper_physical_template": template,
        "wrapper_source_sha256": str(getattr(wrapper, "source_sha256", "")),
        "wrapper_callback_ir_sha256": str(getattr(wrapper, "callback_ir_sha256", "")),
        "wrapper_callback_abi_sha256": str(getattr(wrapper, "callback_abi_sha256", "")),
        "producer_bindings_sha256": _digest({
            key: fragment in source for key, fragment in expected_fragments.items()
        }),
    }


def _physical_authority_sha256(
    authority: VerifiedPhysicalSchemaAuthority,
) -> str:
    orientation = authority.triangle_orientation_authority
    return _digest({
        "callback_ir_sha256": authority.callback.ir_sha256,
        "callback_effect_digest": authority.callback.effect_digest,
        "schema_sha256": authority.schema.schema_sha256,
        "target_sha256": authority.target.target_sha256,
        "triangle_orientation_authority_sha256": (
            None if orientation is None else orientation.authority_sha256
        ),
        "authority_nonce": authority.authority_nonce,
    })


def _declared_physical_facts(
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    expected_wrapper: object,
    abi: CompiledCallbackAbi,
) -> dict[str, str]:
    schema = authority.schema
    result = {
        "geometry_family": schema.geometry_family.value,
        "template_id": plan.template_id.value,
        "physical_authority_sha256": _physical_authority_sha256(authority),
        "canonical_plan_sha256": plan.plan_sha256,
        "payload_output_shape": "u32x3_to_u32x3_per_query",
        "callback_abi_sha256": abi.abi_sha256,
    }
    result.update(_wrapper_binding_facts(expected_wrapper))
    result.update(_declared_runtime_binding_facts())
    return result


def _projected_physical_facts(
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
    executable: object,
) -> dict[str, str]:
    """Project bindings from emitted wrapper/runtime producer artifacts.

    The projection intentionally does not copy the public input schema's
    buffer/channel/GAS dictionaries.  Their expected digests remain on the
    declaration side; the compiler side binds them through the exact authority
    and plan identities carried by the executable plus concrete wrapper/runtime
    producer bindings.
    """

    result = {
        "geometry_family": (
            GeometryFamily.BUILTIN_TRIANGLE.value
            if getattr(executable.wrapper, "physical_template", None)
                == "builtin_triangle_adjacency_u32x3_v1"
            else "INVALID_WRAPPER_GEOMETRY_FAMILY"
        ),
        "template_id": (
            ReferenceTemplateId.BUILTIN_TRIANGLE_V1.value
            if getattr(executable.wrapper, "physical_template", None)
                == "builtin_triangle_adjacency_u32x3_v1"
            else "INVALID_WRAPPER_TEMPLATE"
        ),
        "physical_authority_sha256": str(
            getattr(executable, "authority_sha256", "")),
        "canonical_plan_sha256": str(getattr(executable, "plan_sha256", "")),
        "payload_output_shape": (
            "u32x3_to_u32x3_per_query"
            if all(len(_abi_effect_signature(abi, *arguments)) == 3 for arguments in (
                ("make_ray", "trace_request", "out.trace_request.payload."),
                ("closest_hit", "payload", "out.payload.payload."),
                ("miss", "payload", "out.payload.payload."),
                ("finalize", "output", "out.output.value."),
            ))
            else "INVALID_PAYLOAD_OUTPUT_SHAPE"
        ),
        "callback_abi_sha256": str(getattr(executable, "abi_sha256", "")),
    }
    result.update(_wrapper_binding_facts(executable.wrapper))
    result.update(_projected_runtime_binding_facts())
    return result


def _task_semantics_from_callback(
    callback: VerifiedCallbackProgram,
    schema: TypedPhysicalSchemaV1,
    plan: CanonicalPhysicalPlan,
) -> str:
    manifest = callback.program.manifest
    return _digest({
        "schema": "rtdl.v4.public_builtin_triangle_task.v1",
        "callback_ir_sha256": callback.ir_sha256,
        "effect_digest": callback.effect_digest,
        "geometry_family": schema.geometry_family.value,
        "role_topology": sorted(
            item.role.value for item in callback.program.functions
            if item.role is not None),
        "payload_signature": _record_signature(callback, manifest.payload_record),
        "output_signature": _record_signature(callback, manifest.output_record),
        "template_id": plan.template_id.value,
    })


def _task_semantics_from_compiler(
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    ownership = _projected_ownership(authority, abi)
    return _digest({
        "schema": "rtdl.v4.public_builtin_triangle_task.v1",
        "callback_ir_sha256": abi.callback_ir_sha256,
        "effect_digest": abi.callback_effect_digest,
        "geometry_family": authority.schema.geometry_family.value,
        "role_topology": sorted(item.role.value for item in abi.roles),
        "payload_signature": _abi_effect_signature(
            abi, "make_ray", "trace_request", "out.trace_request.payload."),
        "output_signature": _abi_effect_signature(
            abi, "finalize", "output", "out.output.value."),
        "template_id": plan.template_id.value,
    })


def _continuation_projection(executable: object, abi: CompiledCallbackAbi) -> str:
    status_codes = dict(abi.runtime_status_codes)
    source = str(getattr(getattr(executable, "wrapper", None), "source", ""))
    output_position = source.find("params.output_0[query]")
    final_status_position = source.rfind("v4_commit_leaf_status", 0, output_position)
    error_guard_position = source.rfind("first_error_claimed", 0, output_position)
    runtime_path = Path(__file__).with_name("v4_triangle_prepared_runtime.py")
    runtime_source = runtime_path.read_text(encoding="utf-8")
    runtime_withholds = (
        "prepared built-in triangle returned device error" in runtime_source
        and "raise RuntimeError" in runtime_source
        and "return V4TriangleCallbackResult" in runtime_source
    )
    complete = (
        status_codes.get("ok") == 0
        and any(value != 0 for value in status_codes.values())
        and output_position > 0
        and final_status_position > 0
        and error_guard_position > 0
        and final_status_position < output_position
        and error_guard_position < output_position
        and runtime_withholds
    )
    return (
        "REQUIRE_COMPLETE_BEFORE_CONSUME"
        if complete else "MISSING_FAIL_CLOSED_STATUS_OR_CONTINUATION"
    )


def _generic_contract_decision(
    program: VerifiedBuiltinTriangleCallbackProgram,
    executable: object,
) -> ProtocolContractDecision:
    authority = program._authority
    plan = program._canonical_plan
    abi = program._abi
    checked_executable_sha = _rederive_checked_executable_sha256(
        executable, authority, plan, abi)
    actual_executable_sha = str(
        getattr(executable, "executable_sha256", ""))
    composed_sha = str(getattr(getattr(executable, "composed", None), "ptx_sha256", ""))
    declaration = ProtocolContractDeclaration(
        family="builtin_triangle_callback_ir",
        task_semantics_sha256=_task_semantics_from_callback(
            program.callback, authority.schema, plan),
        role_effects=tuple(sorted(_declared_role_effects(program.callback).items())),
        attribute_abi_ownership=tuple(sorted(_declared_ownership(program.callback).items())),
        physical_bindings=tuple(sorted(
            program._declared_physical_bindings.items())),
        continuation_policy="REQUIRE_COMPLETE_BEFORE_CONSUME",
        checked_executable_sha256=checked_executable_sha,
    )
    lifecycle_path = Path(__file__)
    runtime_path = lifecycle_path.with_name("v4_triangle_prepared_runtime.py")
    projection = CompilerProtocolProjection(
        family="builtin_triangle_callback_ir",
        task_semantics_sha256=_task_semantics_from_compiler(authority, plan, abi),
        role_effects=tuple(sorted(_compiled_role_effects(abi).items())),
        attribute_abi_ownership=tuple(sorted(_projected_ownership(authority, abi).items())),
        physical_bindings=tuple(sorted(_projected_physical_facts(
            authority, plan, abi, executable).items())),
        continuation_policy=_continuation_projection(executable, abi),
        actual_executable_sha256=actual_executable_sha,
        generated_device_source_sha256=composed_sha,
        generated_host_source_sha256=_digest({
            "public_lifecycle": _source_text_sha256(lifecycle_path),
            "prepared_runtime": _source_text_sha256(runtime_path),
        }),
    )
    return verify_protocol_contract(declaration, projection)


def _rederive_checked_executable_sha256(
    executable: object,
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    from .v4_triangle_optix_compiler import (
        rederive_verified_triangle_executable_sha256,
    )
    return rederive_verified_triangle_executable_sha256(
        executable, authority, plan, abi)


class MaterializedBuiltinTriangleCallbackProgram:
    """Single-use generated executable; no GPU state exists yet."""

    def __init__(
        self, *, program: VerifiedBuiltinTriangleCallbackProgram,
        toolchain: V4Toolchain, executable: object, compiler_log: str,
        identity: BuiltinTriangleCallbackExecutableIdentity,
        decision: ProtocolContractDecision,
        _construction_token: object,
    ) -> None:
        if _construction_token is not _CONSTRUCTION_TOKEN:
            _fail("GC027_LIVE_AUTHORITY_REQUIRED", "materialized", "use public materialize")
        self._program = program
        self._toolchain = toolchain
        self._executable = executable
        self._identity = identity
        self._decision = decision
        self._compiler_log_sha256 = hashlib.sha256(
            compiler_log.encode("utf-8")).hexdigest()
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._state = "materialized"

    def __getstate__(self):
        _fail("GC009_NONSERIALIZABLE", "materialized", "cannot be serialized")

    @property
    def identity(self) -> BuiltinTriangleCallbackExecutableIdentity:
        return self._identity

    @property
    def protocol_contract_decision(self) -> ProtocolContractDecision:
        return self._decision

    @property
    def compiler_log_sha256(self) -> str:
        return self._compiler_log_sha256

    @property
    def state(self) -> str:
        return self._state

    def _check(self) -> None:
        if os.getpid() != self._pid:
            _fail("GC010_PROCESS_BOUNDARY", "materialized", "crossed process boundary")
        if threading.get_ident() != self._thread:
            _fail("GC011_THREAD_BOUNDARY", "materialized", "crossed thread boundary")

    def prepare(
        self, static_input: BuiltinTriangleCallbackStaticInput,
    ) -> "PreparedBuiltinTriangleCallbackProgram":
        self._check()
        if not self._active.acquire(blocking=False):
            _fail("GC012_REENTRANT", "materialized.prepare", "already active")
        try:
            if self._state != "materialized":
                _fail("GC013_EXECUTABLE_CONSUMED", "materialized", self._state)
            if self._decision.verdict != "ACCEPT":
                _fail("GC014_PROTOCOL_CONTRACT_REJECTED", "materialized.contract", self._decision.verdict)
            if not isinstance(static_input, BuiltinTriangleCallbackStaticInput):
                _fail("GC015_STATIC_INPUT_REQUIRED", "static_input", type(static_input).__name__)
            self._state = "preparing"
            try:
                # The helper is implementation-private, as in the existing
                # public closed-family lifecycle.  It is never exposed to or
                # invoked by user code and binds the exact target bytes.
                from .v4_callback_lifecycle import _load_exact_native_library
                from .v4_triangle_prepared_runtime import (
                    prepare_builtin_triangle_callback,
                )
                library = _load_exact_native_library(self._program._target)
                owner = prepare_builtin_triangle_callback(
                    authority=self._program._authority,
                    plan=self._program._canonical_plan,
                    abi=self._program._abi,
                    executable=self._executable,
                    vertices=static_input.vertices,
                    triangles=static_input.triangles,
                    front_values=static_input.first_primitive_values,
                    back_values=static_input.second_primitive_values,
                    library=library,
                    native_library_path=self._program._target.native_library_path,
                )
            except BaseException:
                self._state = "failed"
                raise
            self._state = "prepared"
            return PreparedBuiltinTriangleCallbackProgram(
                owner=owner,
                identity=self._identity,
                decision=self._decision,
                _construction_token=_CONSTRUCTION_TOKEN,
            )
        finally:
            self._active.release()


def materialize_builtin_triangle_callback_program(
    program: VerifiedBuiltinTriangleCallbackProgram,
    *,
    toolchain: V4Toolchain,
) -> MaterializedBuiltinTriangleCallbackProgram:
    """Generate one exact target executable; do not create GPU state."""

    if not isinstance(program, VerifiedBuiltinTriangleCallbackProgram):
        _fail("GC016_PROGRAM_REQUIRED", "program", type(program).__name__)
    if not isinstance(toolchain, V4Toolchain):
        _fail("GC017_TOOLCHAIN_REQUIRED", "toolchain", type(toolchain).__name__)
    profile_cc = tuple(
        int(item) for item in program._target.profile.compute_capability.split("."))
    if profile_cc != toolchain.compute_capability:
        _fail(
            "GC018_TARGET_TOOLCHAIN_MISMATCH", "compute_capability",
            f"target={profile_cc}, toolchain={toolchain.compute_capability}",
        )
    if not program._target.profile.supports_builtin_triangle:
        _fail("GC019_TARGET_CAPABILITY_MISSING", "target", "builtin_triangle")
    from .v4_triangle_optix_compiler import (
        compile_verified_triangle_executable,
        consume_verified_triangle_executable,
    )
    executable, compiler_log = compile_verified_triangle_executable(
        program._authority,
        program._canonical_plan,
        program._abi,
        compute_capability=toolchain.compute_capability,
        optix_include=toolchain.optix_include,
        cuda_include=toolchain.cuda_include,
        expected_python_version=toolchain.expected_python_version,
        expected_numba_version=toolchain.expected_numba_version,
        expected_numpy_version=toolchain.expected_numpy_version,
    )
    try:
        if executable.wrapper != program._expected_wrapper:
            _fail("GC020_WRAPPER_IDENTITY_DRIFT", "materialize.wrapper", "compile-time shape changed")
        decision = _generic_contract_decision(program, executable)
        if decision.verdict != "ACCEPT":
            _fail(
                "GC014_PROTOCOL_CONTRACT_REJECTED", "materialize.contract",
                ",".join(item.reason_id for item in decision.findings),
            )
    except BaseException:
        # Revoke the process-local single-use executable even though no native
        # or GPU action has occurred.
        try:
            consume_verified_triangle_executable(
                executable, program._authority, program._canonical_plan, program._abi)
        except BaseException:
            pass
        raise
    identity = BuiltinTriangleCallbackExecutableIdentity(
        program_identity_sha256=program.identity.identity_sha256,
        physical_schema_sha256=program._authority.schema.schema_sha256,
        canonical_plan_sha256=program._canonical_plan.plan_sha256,
        callback_abi_sha256=program._abi.abi_sha256,
        wrapper_source_sha256=executable.wrapper.source_sha256,
        generated_executable_sha256=executable.executable_sha256,
        composed_ptx_sha256=executable.composed.ptx_sha256,
        native_library_sha256=program._target.profile.native_sha256,
    )
    return MaterializedBuiltinTriangleCallbackProgram(
        program=program,
        toolchain=toolchain,
        executable=executable,
        compiler_log=compiler_log,
        identity=identity,
        decision=decision,
        _construction_token=_CONSTRUCTION_TOKEN,
    )


class PreparedBuiltinTriangleCallbackProgram:
    """Process-local public owner with execute and idempotent close."""

    def __init__(
        self, *, owner: object,
        identity: BuiltinTriangleCallbackExecutableIdentity,
        decision: ProtocolContractDecision,
        _construction_token: object,
    ) -> None:
        if _construction_token is not _CONSTRUCTION_TOKEN:
            _fail("GC027_LIVE_AUTHORITY_REQUIRED", "prepared", "use public prepare")
        self._owner = owner
        self._identity = identity
        self._decision = decision
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._closed = False

    def __getstate__(self):
        _fail("GC009_NONSERIALIZABLE", "prepared", "cannot be serialized")

    @property
    def identity(self) -> BuiltinTriangleCallbackExecutableIdentity:
        return self._identity

    @property
    def protocol_contract_decision(self) -> ProtocolContractDecision:
        return self._decision

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def lifecycle_receipt(self) -> dict[str, object]:
        self._check_open()
        return {
            **dict(self._owner.lifecycle_receipt),
            "schema": "rtdl.v4.public_builtin_triangle_callback_lifecycle.v1",
            "executable_identity_sha256": self._identity.identity_sha256,
            "protocol_contract_verdict": self._decision.verdict,
        }

    def _check_open(self) -> None:
        if self._closed:
            _fail("GC021_CLOSED", "prepared", "already closed")
        if os.getpid() != self._pid:
            _fail("GC010_PROCESS_BOUNDARY", "prepared", "crossed process boundary")
        if threading.get_ident() != self._thread:
            _fail("GC011_THREAD_BOUNDARY", "prepared", "crossed thread boundary")

    def execute(
        self, batch: BuiltinTriangleCallbackBatch,
    ) -> BuiltinTriangleCallbackExecutionResult:
        self._check_open()
        if not isinstance(batch, BuiltinTriangleCallbackBatch):
            _fail("GC022_BATCH_REQUIRED", "batch", type(batch).__name__)
        if not self._active.acquire(blocking=False):
            _fail("GC012_REENTRANT", "prepared.execute", "already active")
        try:
            # Oracles are deliberately absent from the public execution
            # surface.  A caller may compare the returned bytes afterward,
            # but no expected value can influence the trusted owner.
            if batch.uses_contiguous_columns:
                result = self._owner.execute(
                    batch.queries, partner_column_output=True)
            else:
                result = self._owner.execute(batch.queries)
            if result.composed_ptx_sha256 != self._identity.composed_ptx_sha256:
                _fail(
                    "GC023_EXECUTED_PTX_IDENTITY_MISMATCH", "execute.composed_ptx_sha256",
                    f"expected {self._identity.composed_ptx_sha256}, "
                    f"observed {result.composed_ptx_sha256}",
                )
            if result.native_library_sha256 != self._identity.native_library_sha256:
                _fail(
                    "GC024_EXECUTED_NATIVE_IDENTITY_MISMATCH", "execute.native_library_sha256",
                    f"expected {self._identity.native_library_sha256}, "
                    f"observed {result.native_library_sha256}",
                )
            observed_output = result.output
            if batch.uses_contiguous_columns:
                # The runtime and public wrapper independently derive the same
                # domain-separated digest directly from the contiguous output
                # bytes.  Neither side creates per-row Python objects.
                observed_output_sha = _bulk_u32x3_digest(observed_output)
            else:
                observed_output_sha = _digest(observed_output)
            if result.output_sha256 != observed_output_sha:
                _fail(
                    "GC025_OUTPUT_IDENTITY_MISMATCH", "execute.output_sha256",
                    f"expected {observed_output_sha}, observed {result.output_sha256}",
                )
            receipt = result.traversal_receipt
            if not isinstance(receipt, Mapping):
                _fail("GC026_TRAVERSAL_RECEIPT_INVALID", "execute.receipt", type(receipt).__name__)
            try:
                from .physical_execution_provenance import (
                    validate_traversal_receipt,
                )
                validate_traversal_receipt(
                    receipt,
                    provider_library_sha256=self._identity.native_library_sha256,
                    route_identity=(
                        "v4_builtin_triangle_callback_ir:four_role_composed_v1"),
                    output_digest=result.output_sha256,
                    expected_program_bundles=(
                        "v4_builtin_triangle_callback_ir_four_role_composed",),
                    expected_successful_launch_count=1,
                    expected_raygen_invocation_count=len(batch.queries),
                )
            except (RuntimeError, TypeError, ValueError):
                _fail(
                    "GC026_TRAVERSAL_RECEIPT_INVALID", "execute.receipt",
                    "route/provider/output/seal binding failed",
                )
            return BuiltinTriangleCallbackExecutionResult(
                output=result.output,
                hit_observations=result.hit_observations,
                role_counters=result.role_counters,
                launch_status=result.launch_status,
                traversal_receipt=result.traversal_receipt,
                output_sha256=result.output_sha256,
                executable_identity=self._identity,
                protocol_contract_decision=self._decision,
            )
        finally:
            self._active.release()

    def close(self) -> None:
        if self._closed:
            return
        if os.getpid() != self._pid:
            _fail("GC010_PROCESS_BOUNDARY", "prepared.close", "crossed process boundary")
        if threading.get_ident() != self._thread:
            _fail("GC011_THREAD_BOUNDARY", "prepared.close", "crossed thread boundary")
        if not self._active.acquire(blocking=False):
            _fail("GC012_REENTRANT", "prepared.close", "already active")
        try:
            self._owner.close()
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self) -> "PreparedBuiltinTriangleCallbackProgram":
        self._check_open()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


__all__ = [
    "BuiltinTriangleCallbackBatch",
    "BuiltinTriangleCallbackExecutableIdentity",
    "BuiltinTriangleCallbackExecutionResult",
    "BuiltinTriangleCallbackPhysicalPlan",
    "BuiltinTriangleCallbackProgramIdentity",
    "BuiltinTriangleCallbackStaticInput",
    "BuiltinTriangleOrientationDeclaration",
    "BuiltinTriangleU32x3FieldIds",
    "MaterializedBuiltinTriangleCallbackProgram",
    "PreparedBuiltinTriangleCallbackProgram",
    "PublicCallbackLifecycleError",
    "VerifiedBuiltinTriangleCallbackProgram",
    "VerifiedBuiltinTriangleCallbackSource",
    "compile_builtin_triangle_callback_program",
    "build_builtin_triangle_u32x3_physical_plan",
    "materialize_builtin_triangle_callback_program",
    "verify_builtin_triangle_callback_source",
]
