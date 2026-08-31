"""Public Goal5833 lifecycle for static OptiX built-in spheres."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .v4_builtin_sphere_standard_library import FIRST_CONTACT_SOURCE, first_contact_manifest
from .v4_callback_frontend import parse_callback_source
from .v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackModuleManifest,
)
from .v4_callback_lifecycle import V4Toolchain
from .v4_sphere_callback_abi import compile_sphere_callback_abi
from .v4_sphere_optix_wrapper_codegen import generate_trusted_optix_sphere_wrapper_v1
from .v4_sphere_physical_schema import (
    BuiltinSpherePhysicalSchema,
    SphereTargetProfile,
    verify_builtin_sphere_physical_schema,
    verify_callback_program_for_builtin_sphere,
    verify_reference_sphere_contents,
)


_TOKEN = object()


class PublicSphereLifecycleError(RuntimeError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code; self.path = path; self.message = message
        super().__init__(f"{code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise PublicSphereLifecycleError(code, path, message)


@dataclass(frozen=True)
class BuiltinSphereFieldIds:
    centers: str = "sphere_centers"
    radii: str = "sphere_radii"
    application_ids: str = "application_ids"
    queries: str = "motion_segments"
    outputs: str = "first_contacts"
    status: str = "device_status"


@dataclass(frozen=True)
class BuiltinSphereStaticInput:
    centers: object
    radii: object
    application_ids: object

    def __post_init__(self) -> None:
        normalized = verify_reference_sphere_contents(
            self.centers, self.radii, self.application_ids)
        object.__setattr__(self, "centers", normalized[0])
        object.__setattr__(self, "radii", normalized[1])
        object.__setattr__(self, "application_ids", normalized[2])


@dataclass(frozen=True)
class MotionSegmentBatch:
    queries: tuple[tuple[tuple[float, float, float], tuple[float, float, float]], ...]

    def __post_init__(self) -> None:
        try:
            source_rows = tuple(self.queries)
        except TypeError:
            _fail("GS014_QUERY_SHAPE", "batch.queries", "iterable rows required")
        if not source_rows:
            _fail("GS001_QUERY_REQUIRED", "batch.queries", "rows required")
        rows = []
        for index, row in enumerate(source_rows):
            try:
                parts = tuple(row)
            except TypeError:
                _fail("GS014_QUERY_SHAPE", f"batch.queries[{index}]",
                      "exactly (start,end) required")
            if len(parts) != 2:
                _fail("GS014_QUERY_SHAPE", f"batch.queries[{index}]",
                      "exactly (start,end) required")
            try:
                start, end = tuple(parts[0]), tuple(parts[1])
            except TypeError:
                _fail("GS014_QUERY_SHAPE", f"batch.queries[{index}]",
                      "start and end vec3 values required")
            if len(start) != 3 or len(end) != 3:
                _fail("GS014_QUERY_SHAPE", f"batch.queries[{index}]",
                      "start and end must each be vec3")
            rows.append((start, end))
        object.__setattr__(self, "queries", tuple(rows))


@dataclass(frozen=True)
class V4SphereTarget:
    profile: SphereTargetProfile
    native_library_path: Path

    def __post_init__(self) -> None:
        if not isinstance(self.profile, SphereTargetProfile):
            _fail("GS002_TARGET_PROFILE", "target.profile", type(self.profile).__name__)
        path = Path(self.native_library_path).expanduser().resolve()
        if not path.is_file():
            _fail("GS003_NATIVE_MISSING", "target.native_library_path", str(path))
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != self.profile.native_sha256:
            _fail("GS004_NATIVE_IDENTITY", "target.native_library_path", observed)
        object.__setattr__(self, "native_library_path", path)

    @classmethod
    def from_native(cls, path, *, optix_sdk: str, compute_capability: str):
        resolved = Path(path).expanduser().resolve()
        if not resolved.is_file():
            _fail("GS003_NATIVE_MISSING", "native_library_path", str(resolved))
        profile = SphereTargetProfile(
            "optix", optix_sdk, compute_capability,
            hashlib.sha256(resolved.read_bytes()).hexdigest())
        return cls(profile, resolved)


class VerifiedBuiltinSphereSource:
    def __init__(self, source, manifest, callback, *, _token):
        if _token is not _TOKEN:
            _fail("GS005_LIVE_SOURCE", "source", "use verify_builtin_sphere_callback_source")
        self._source = source; self._manifest = manifest; self.callback = callback
        self.source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()

    def compile(self, *, target: V4SphereTarget, field_ids=BuiltinSphereFieldIds()):
        return compile_builtin_sphere_callback_program(
            self, target=target, field_ids=field_ids)


def verify_builtin_sphere_callback_source(
    source: str, manifest: CallbackModuleManifest,
) -> VerifiedBuiltinSphereSource:
    if not isinstance(source, str) or not source.strip() \
            or not isinstance(manifest, CallbackModuleManifest):
        _fail("GS006_SOURCE_MANIFEST", "source", "nonempty source and manifest required")
    spec = parse_callback_source(
        source, manifest,
        schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION)
    callback = verify_callback_program_for_builtin_sphere(spec)
    return VerifiedBuiltinSphereSource(source, manifest, callback, _token=_TOKEN)


class VerifiedBuiltinSphereProgram:
    def __init__(self, source, target, authority, abi, wrapper, *, _token):
        if _token is not _TOKEN:
            _fail("GS007_LIVE_PROGRAM", "program", "use public compiler")
        self.source = source; self.target = target; self.authority = authority
        self.abi = abi; self.wrapper = wrapper

    def materialize(self, *, toolchain: V4Toolchain):
        return materialize_builtin_sphere_callback_program(self, toolchain=toolchain)


def compile_builtin_sphere_callback_program(
    source: VerifiedBuiltinSphereSource, *, target: V4SphereTarget,
    field_ids: BuiltinSphereFieldIds,
) -> VerifiedBuiltinSphereProgram:
    if not isinstance(source, VerifiedBuiltinSphereSource) \
            or not isinstance(target, V4SphereTarget) \
            or not isinstance(field_ids, BuiltinSphereFieldIds):
        _fail("GS008_COMPILE_INPUT", "compile", "verified source/target/field IDs required")
    fresh = verify_builtin_sphere_callback_source(source._source, source._manifest)
    if fresh.callback != source.callback or fresh.source_sha256 != source.source_sha256:
        _fail("GS009_SOURCE_DRIFT", "source", "source does not rederive")
    schema = BuiltinSpherePhysicalSchema(
        fresh.callback.ir_sha256, fresh.callback.effect_digest,
        field_ids.centers, field_ids.radii, field_ids.application_ids,
        field_ids.queries, field_ids.outputs, field_ids.status)
    authority = verify_builtin_sphere_physical_schema(
        fresh.callback, schema, target=target.profile)
    abi = compile_sphere_callback_abi(authority)
    wrapper = generate_trusted_optix_sphere_wrapper_v1(
        authority, authority.canonical_plan, abi)
    return VerifiedBuiltinSphereProgram(
        fresh, target, authority, abi, wrapper, _token=_TOKEN)


class MaterializedBuiltinSphereProgram:
    def __init__(self, program, executable, compiler_log, *, _token):
        if _token is not _TOKEN:
            _fail("GS010_LIVE_MATERIALIZATION", "materialized", "use materialize")
        self.program = program; self.executable = executable
        self.compiler_log = compiler_log

    def prepare(self, static_input: BuiltinSphereStaticInput):
        if not isinstance(static_input, BuiltinSphereStaticInput):
            _fail("GS011_STATIC_INPUT", "static_input", type(static_input).__name__)
        return PreparedBuiltinSphereProgram(self, static_input)


def materialize_builtin_sphere_callback_program(
    program: VerifiedBuiltinSphereProgram, *, toolchain: V4Toolchain,
) -> MaterializedBuiltinSphereProgram:
    if not isinstance(program, VerifiedBuiltinSphereProgram) \
            or not isinstance(toolchain, V4Toolchain):
        _fail("GS012_MATERIALIZE_INPUT", "materialize", "verified program/toolchain required")
    from .v4_sphere_optix_compiler import compile_verified_sphere_executable
    executable, log = compile_verified_sphere_executable(
        program.authority, program.authority.canonical_plan, program.abi,
        compute_capability=toolchain.compute_capability,
        optix_include=toolchain.optix_include,
        cuda_include=toolchain.cuda_include,
        expected_python_version=toolchain.expected_python_version,
        expected_numba_version=toolchain.expected_numba_version,
        expected_numpy_version=toolchain.expected_numpy_version)
    return MaterializedBuiltinSphereProgram(program, executable, log, _token=_TOKEN)


class PreparedBuiltinSphereProgram:
    def __init__(self, materialized, static_input):
        from .v4_sphere_prepared_runtime import PreparedBuiltinSphereOwner
        program = materialized.program
        self._owner = PreparedBuiltinSphereOwner(
            authority=program.authority,
            plan=program.authority.canonical_plan,
            abi=program.abi,
            executable=materialized.executable,
            centers=static_input.centers,
            radii=static_input.radii,
            application_ids=static_input.application_ids,
            native_library_path=program.target.native_library_path)

    @property
    def lifecycle_receipt(self):
        return self._owner.lifecycle_receipt

    @property
    def last_failure_receipt(self):
        return self._owner.last_failure_receipt

    def execute(self, batch: MotionSegmentBatch, *, expected_output=None):
        if not isinstance(batch, MotionSegmentBatch):
            _fail("GS013_BATCH", "batch", type(batch).__name__)
        return self._owner.execute(batch.queries, expected_output=expected_output)

    def close(self):
        self._owner.close()

    def __enter__(self): return self
    def __exit__(self, exc_type, exc, traceback): self.close()


def first_contact_source() -> VerifiedBuiltinSphereSource:
    return verify_builtin_sphere_callback_source(
        FIRST_CONTACT_SOURCE, first_contact_manifest())


__all__ = [
    "BuiltinSphereFieldIds", "BuiltinSphereStaticInput", "MotionSegmentBatch",
    "PreparedBuiltinSphereProgram", "PublicSphereLifecycleError",
    "V4SphereTarget", "VerifiedBuiltinSphereProgram",
    "VerifiedBuiltinSphereSource", "compile_builtin_sphere_callback_program",
    "first_contact_source", "materialize_builtin_sphere_callback_program",
    "verify_builtin_sphere_callback_source",
]
