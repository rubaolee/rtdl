"""Public Goal5834 lifecycle for static OptiX round-linear curves."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .v4_builtin_curve_standard_library import (
    CURVE_ANY_CONTACT_BOOLEAN_SOURCE,
    CURVE_FIRST_CONTACT_SOURCE,
    curve_any_contact_boolean_manifest,
    curve_first_contact_manifest,
)
from .v4_callback_frontend import parse_callback_source
from .v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackModuleManifest,
)
from .v4_callback_lifecycle import V4Toolchain
from .v4_curve_callback_abi import compile_curve_callback_abi
from .v4_curve_optix_wrapper_codegen import generate_trusted_optix_curve_wrapper_v1
from .v4_curve_physical_schema import (
    BuiltinCurveBooleanPhysicalSchema,
    BuiltinCurvePhysicalSchema,
    CurveTargetProfile,
    verify_builtin_curve_physical_schema,
    verify_callback_program_for_builtin_curve,
    verify_curve_boolean_motion_segments,
    verify_reference_curve_contents,
)


_TOKEN = object()
_FIRST_CONTACT_VARIANT = "first_contact_u32x3"
_BOOLEAN_VARIANT = "provider_any_contact_u32"


class PublicCurveLifecycleError(RuntimeError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise PublicCurveLifecycleError(code, path, message)


@dataclass(frozen=True)
class BuiltinCurveFieldIds:
    control_points: str = "curve_control_points"
    widths: str = "curve_widths"
    segment_indices: str = "curve_segment_indices"
    application_ids: str = "application_ids"
    queries: str = "motion_segments"
    outputs: str = "first_contacts"
    status: str = "device_status"


@dataclass(frozen=True)
class BuiltinCurveBooleanFieldIds:
    control_points: str = "curve_control_points"
    widths: str = "curve_widths"
    segment_indices: str = "curve_segment_indices"
    application_ids: str = "application_ids"
    queries: str = "motion_segments"
    outputs: str = "any_contact_bits"
    status: str = "device_status"


@dataclass(frozen=True)
class BuiltinCurveStaticInput:
    control_points: object
    widths: object
    segment_indices: object
    application_ids: object

    def __post_init__(self) -> None:
        normalized = verify_reference_curve_contents(
            self.control_points, self.widths,
            self.segment_indices, self.application_ids)
        object.__setattr__(self, "control_points", normalized[0])
        object.__setattr__(self, "widths", normalized[1])
        object.__setattr__(self, "segment_indices", normalized[2])
        object.__setattr__(self, "application_ids", normalized[3])

    @property
    def commitment_sha256(self) -> str:
        from .v4_curve_prepared_runtime import (
            curve_static_input_commitment_sha256,
        )
        return curve_static_input_commitment_sha256(
            self.control_points, self.widths,
            self.segment_indices, self.application_ids)


@dataclass(frozen=True)
class CurveMotionSegmentBatch:
    queries: object

    def __post_init__(self) -> None:
        try:
            source_rows = tuple(self.queries)
        except TypeError:
            _fail("GC014_QUERY_SHAPE", "batch.queries", "iterable rows required")
        if not source_rows:
            _fail("GC001_QUERY_REQUIRED", "batch.queries", "rows required")
        rows = []
        for index, row in enumerate(source_rows):
            try:
                parts = tuple(row)
                start, end = tuple(parts[0]), tuple(parts[1])
            except (TypeError, IndexError):
                _fail(
                    "GC014_QUERY_SHAPE", f"batch.queries[{index}]",
                    "exactly (start,end) vec3 values required",
                )
            if len(parts) != 2 or len(start) != 3 or len(end) != 3:
                _fail(
                    "GC014_QUERY_SHAPE", f"batch.queries[{index}]",
                    "exactly (start,end) vec3 values required",
                )
            rows.append((start, end))
        object.__setattr__(self, "queries", tuple(rows))


@dataclass(frozen=True)
class CurveBooleanSegmentBatch:
    queries: object

    def __post_init__(self) -> None:
        try:
            source_rows = tuple(self.queries)
            split_rows = tuple(tuple(row) for row in source_rows)
            if any(len(row) != 2 for row in split_rows):
                raise ValueError("exactly two row fields required")
            starts = tuple(tuple(row[0]) for row in split_rows)
            ends = tuple(tuple(row[1]) for row in split_rows)
        except (TypeError, IndexError, ValueError):
            _fail(
                "GCB014_QUERY_SHAPE", "batch.queries",
                "exactly (start,end) vec3 values required",
            )
        try:
            normalized = verify_curve_boolean_motion_segments(starts, ends)
        except Exception as exc:
            _fail("GCB014_QUERY_SHAPE", "batch.queries", str(exc))
        object.__setattr__(self, "queries", tuple(
            (row[:3], row[3:]) for row in normalized))

    @property
    def commitment_sha256(self) -> str:
        from .v4_curve_prepared_runtime import curve_query_commitment_sha256
        flattened = tuple((*row[0], *row[1]) for row in self.queries)
        return curve_query_commitment_sha256(flattened)


@dataclass(frozen=True)
class V4CurveTarget:
    profile: CurveTargetProfile
    native_library_path: Path

    def __post_init__(self) -> None:
        if not isinstance(self.profile, CurveTargetProfile):
            _fail("GC002_TARGET_PROFILE", "target.profile", type(self.profile).__name__)
        path = Path(self.native_library_path).expanduser().resolve()
        if not path.is_file():
            _fail("GC003_NATIVE_MISSING", "target.native_library_path", str(path))
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != self.profile.native_sha256:
            _fail("GC004_NATIVE_IDENTITY", "target.native_library_path", observed)
        object.__setattr__(self, "native_library_path", path)

    @classmethod
    def from_native(cls, path, *, optix_sdk: str, compute_capability: str):
        resolved = Path(path).expanduser().resolve()
        if not resolved.is_file():
            _fail("GC003_NATIVE_MISSING", "native_library_path", str(resolved))
        return cls(CurveTargetProfile(
            "optix", optix_sdk, compute_capability,
            hashlib.sha256(resolved.read_bytes()).hexdigest()), resolved)


class VerifiedBuiltinCurveSource:
    def __init__(self, source, manifest, callback, variant, *, _token):
        if _token is not _TOKEN:
            _fail("GC005_LIVE_SOURCE", "source", "use public verifier")
        self._source = source
        self._manifest = manifest
        self._variant = variant
        self.callback = callback
        self.source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()

    def compile(self, *, target: V4CurveTarget, field_ids=None):
        if field_ids is None:
            field_ids = (
                BuiltinCurveBooleanFieldIds()
                if self._variant == _BOOLEAN_VARIANT else
                BuiltinCurveFieldIds())
        return compile_builtin_curve_callback_program(
            self, target=target, field_ids=field_ids)


def verify_builtin_curve_callback_source(
    source: str, manifest: CallbackModuleManifest,
) -> VerifiedBuiltinCurveSource:
    if not isinstance(source, str) or not source.strip() \
            or not isinstance(manifest, CallbackModuleManifest):
        _fail("GC006_SOURCE_MANIFEST", "source", "source and manifest required")
    spec = parse_callback_source(
        source, manifest,
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION)
    callback = verify_callback_program_for_builtin_curve(spec)
    return VerifiedBuiltinCurveSource(
        source, manifest, callback, _FIRST_CONTACT_VARIANT, _token=_TOKEN)


def verify_builtin_curve_boolean_callback_source(
    source: str, manifest: CallbackModuleManifest,
) -> VerifiedBuiltinCurveSource:
    expected_manifest = curve_any_contact_boolean_manifest()
    if source != CURVE_ANY_CONTACT_BOOLEAN_SOURCE \
            or manifest != expected_manifest:
        _fail(
            "GCB006_FIXED_SOURCE", "source",
            "exact fixed Boolean source and manifest required",
        )
    spec = parse_callback_source(
        source, manifest,
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION)
    callback = verify_callback_program_for_builtin_curve(spec)
    return VerifiedBuiltinCurveSource(
        source, manifest, callback, _BOOLEAN_VARIANT, _token=_TOKEN)


class VerifiedBuiltinCurveProgram:
    def __init__(self, source, target, authority, abi, wrapper, *, _token):
        if _token is not _TOKEN:
            _fail("GC007_LIVE_PROGRAM", "program", "use public compiler")
        self.source = source
        self.target = target
        self.authority = authority
        self.abi = abi
        self.wrapper = wrapper

    def materialize(self, *, toolchain: V4Toolchain):
        return materialize_builtin_curve_callback_program(
            self, toolchain=toolchain)


def compile_builtin_curve_callback_program(
    source: VerifiedBuiltinCurveSource,
    *,
    target: V4CurveTarget,
    field_ids: BuiltinCurveFieldIds | BuiltinCurveBooleanFieldIds,
) -> VerifiedBuiltinCurveProgram:
    if not isinstance(source, VerifiedBuiltinCurveSource) \
            or not isinstance(target, V4CurveTarget) \
            or type(field_ids) not in {
                BuiltinCurveFieldIds, BuiltinCurveBooleanFieldIds}:
        _fail("GC008_COMPILE_INPUT", "compile", "verified inputs required")
    if source._variant == _BOOLEAN_VARIANT:
        if type(field_ids) is not BuiltinCurveBooleanFieldIds:
            _fail(
                "GCB008_FIELD_IDS", "compile.field_ids",
                "Boolean field IDs required",
            )
        fresh = verify_builtin_curve_boolean_callback_source(
            source._source, source._manifest)
    else:
        if type(field_ids) is not BuiltinCurveFieldIds:
            _fail(
                "GC008_FIELD_IDS", "compile.field_ids",
                "First Contact field IDs required",
            )
        fresh = verify_builtin_curve_callback_source(
            source._source, source._manifest)
    if fresh.callback != source.callback \
            or fresh.source_sha256 != source.source_sha256 \
            or fresh._variant != source._variant:
        _fail("GC009_SOURCE_DRIFT", "source", "source does not rederive")
    schema_type = (
        BuiltinCurveBooleanPhysicalSchema
        if fresh._variant == _BOOLEAN_VARIANT else
        BuiltinCurvePhysicalSchema)
    schema = schema_type(
        fresh.callback.ir_sha256, fresh.callback.effect_digest,
        field_ids.control_points, field_ids.widths,
        field_ids.segment_indices, field_ids.application_ids,
        field_ids.queries, field_ids.outputs, field_ids.status)
    authority = verify_builtin_curve_physical_schema(
        fresh.callback, schema, target=target.profile)
    abi = compile_curve_callback_abi(authority)
    wrapper = generate_trusted_optix_curve_wrapper_v1(
        authority, authority.canonical_plan, abi)
    return VerifiedBuiltinCurveProgram(
        fresh, target, authority, abi, wrapper, _token=_TOKEN)


class MaterializedBuiltinCurveProgram:
    def __init__(self, program, executable, compiler_log, *, _token):
        if _token is not _TOKEN:
            _fail("GC010_LIVE_MATERIALIZATION", "materialized", "use materialize")
        self.program = program
        self.executable = executable
        self.compiler_log = compiler_log

    def prepare(self, static_input: BuiltinCurveStaticInput):
        if not isinstance(static_input, BuiltinCurveStaticInput):
            _fail("GC011_STATIC_INPUT", "static_input", type(static_input).__name__)
        return PreparedBuiltinCurveProgram(self, static_input)


def materialize_builtin_curve_callback_program(
    program: VerifiedBuiltinCurveProgram,
    *,
    toolchain: V4Toolchain,
) -> MaterializedBuiltinCurveProgram:
    if not isinstance(program, VerifiedBuiltinCurveProgram) \
            or not isinstance(toolchain, V4Toolchain):
        _fail("GC012_MATERIALIZE_INPUT", "materialize", "verified inputs required")
    from .v4_curve_optix_compiler import compile_verified_curve_executable
    executable, log = compile_verified_curve_executable(
        program.authority,
        program.authority.canonical_plan,
        program.abi,
        compute_capability=toolchain.compute_capability,
        optix_include=toolchain.optix_include,
        cuda_include=toolchain.cuda_include,
        expected_python_version=toolchain.expected_python_version,
        expected_numba_version=toolchain.expected_numba_version,
        expected_numpy_version=toolchain.expected_numpy_version,
    )
    return MaterializedBuiltinCurveProgram(
        program, executable, log, _token=_TOKEN)


class PreparedBuiltinCurveProgram:
    def __init__(self, materialized, static_input):
        from .v4_curve_prepared_runtime import PreparedBuiltinCurveOwner
        program = materialized.program
        self._variant = program.source._variant
        self._owner = PreparedBuiltinCurveOwner(
            authority=program.authority,
            plan=program.authority.canonical_plan,
            abi=program.abi,
            executable=materialized.executable,
            control_points=static_input.control_points,
            widths=static_input.widths,
            segment_indices=static_input.segment_indices,
            application_ids=static_input.application_ids,
            native_library_path=program.target.native_library_path,
        )

    @property
    def lifecycle_receipt(self):
        return self._owner.lifecycle_receipt

    @property
    def last_failure_receipt(self):
        return self._owner.last_failure_receipt

    def execute(self, batch, *, expected_output=None):
        required_type = (
            CurveBooleanSegmentBatch
            if self._variant == _BOOLEAN_VARIANT else
            CurveMotionSegmentBatch)
        if type(batch) is not required_type:
            _fail("GC013_BATCH", "batch", type(batch).__name__)
        if self._variant == _BOOLEAN_VARIANT and expected_output is not None:
            _fail(
                "GCB015_ORACLE_IN_WORKER", "expected_output",
                "Boolean oracle comparison must run after the raw receipt",
            )
        return self._owner.execute(
            batch.queries, expected_output=expected_output)

    def close(self):
        self._owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def curve_first_contact_source() -> VerifiedBuiltinCurveSource:
    return verify_builtin_curve_callback_source(
        CURVE_FIRST_CONTACT_SOURCE, curve_first_contact_manifest())


def curve_any_contact_boolean_source() -> VerifiedBuiltinCurveSource:
    return verify_builtin_curve_boolean_callback_source(
        CURVE_ANY_CONTACT_BOOLEAN_SOURCE,
        curve_any_contact_boolean_manifest())


__all__ = [
    "BuiltinCurveBooleanFieldIds", "BuiltinCurveFieldIds",
    "BuiltinCurveStaticInput", "CurveBooleanSegmentBatch",
    "CurveMotionSegmentBatch",
    "MaterializedBuiltinCurveProgram", "PreparedBuiltinCurveProgram",
    "PublicCurveLifecycleError", "V4CurveTarget",
    "VerifiedBuiltinCurveProgram", "VerifiedBuiltinCurveSource",
    "compile_builtin_curve_callback_program",
    "curve_any_contact_boolean_source", "curve_first_contact_source",
    "materialize_builtin_curve_callback_program",
    "verify_builtin_curve_boolean_callback_source",
    "verify_builtin_curve_callback_source",
]
