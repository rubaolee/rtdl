"""Public selected-topology lifecycle for built-in-sphere any-hit count."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .v4_callback_lifecycle import V4Toolchain
from .v4_public_builtin_sphere import MotionSegmentBatch, V4SphereTarget
from .v4_sphere_any_hit_count_contract import (
    SPHERE_ANY_HIT_COUNT_SOURCE,
    SphereAnyHitCountPhysicalSchema,
    compile_sphere_any_hit_count_callback,
    derive_sphere_any_hit_count_proof,
    sphere_any_hit_count_manifest,
    verify_sphere_any_hit_count_abi,
    verify_sphere_any_hit_count_callback_program,
    verify_sphere_any_hit_count_physical_schema,
)
from .v4_sphere_any_hit_count_wrapper_codegen import (
    generate_trusted_optix_sphere_any_hit_count_wrapper_v1,
)
from .v4_sphere_physical_schema import verify_reference_sphere_contents

_TOKEN = object()


class PublicSphereAnyHitCountError(RuntimeError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise PublicSphereAnyHitCountError(code, path, message)


@dataclass(frozen=True)
class SphereAnyHitCountStaticInput:
    centers: object
    radii: object

    def __post_init__(self) -> None:
        try:
            centers = tuple(self.centers)
            radii = tuple(self.radii)
        except TypeError as exc:
            raise PublicSphereAnyHitCountError(
                "GC001_STATIC_INPUT",
                "static_input",
                "iterable center and radius columns required",
            ) from exc
        provider_ids = tuple(range(len(centers)))
        normalized = verify_reference_sphere_contents(
            centers, radii, provider_ids
        )
        object.__setattr__(self, "centers", normalized[0])
        object.__setattr__(self, "radii", normalized[1])


class VerifiedSphereAnyHitCountSource:
    def __init__(self, source, manifest, callback, *, _token) -> None:
        if _token is not _TOKEN:
            _fail(
                "GC002_LIVE_SOURCE",
                "source",
                "use sphere_any_hit_count_source",
            )
        self._source = source
        self._manifest = manifest
        self.callback = callback
        self.source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()

    def compile(self, *, target: V4SphereTarget):
        return compile_sphere_any_hit_count_program(self, target=target)


def sphere_any_hit_count_source() -> VerifiedSphereAnyHitCountSource:
    callback = compile_sphere_any_hit_count_callback()
    return VerifiedSphereAnyHitCountSource(
        SPHERE_ANY_HIT_COUNT_SOURCE,
        sphere_any_hit_count_manifest(),
        callback,
        _token=_TOKEN,
    )


class VerifiedSphereAnyHitCountProgram:
    def __init__(
        self,
        source,
        target,
        authority,
        proof,
        abi,
        behavior,
        wrapper,
        *,
        _token,
    ) -> None:
        if _token is not _TOKEN:
            _fail("GC003_LIVE_PROGRAM", "program", "use public compiler")
        self.source = source
        self.target = target
        self.authority = authority
        self.proof = proof
        self.abi = abi
        self.behavior = behavior
        self.wrapper = wrapper

    def materialize(self, *, toolchain: V4Toolchain):
        return materialize_sphere_any_hit_count_program(
            self, toolchain=toolchain
        )


def compile_sphere_any_hit_count_program(
    source: VerifiedSphereAnyHitCountSource,
    *,
    target: V4SphereTarget,
) -> VerifiedSphereAnyHitCountProgram:
    if type(source) is not VerifiedSphereAnyHitCountSource:
        _fail("GC004_COMPILE_INPUT", "source", type(source).__name__)
    if type(target) is not V4SphereTarget:
        _fail("GC004_COMPILE_INPUT", "target", type(target).__name__)
    canonical = sphere_any_hit_count_source()
    if (
        source._source != SPHERE_ANY_HIT_COUNT_SOURCE
        or source._manifest != sphere_any_hit_count_manifest()
        or source.callback != canonical.callback
        or source.source_sha256 != canonical.source_sha256
    ):
        _fail("GC005_SOURCE_DRIFT", "source", "selected source changed")
    callback = verify_sphere_any_hit_count_callback_program(
        source.callback.program
    )
    schema = SphereAnyHitCountPhysicalSchema(
        callback.ir_sha256, callback.effect_digest
    )
    authority = verify_sphere_any_hit_count_physical_schema(
        callback, schema, target=target.profile
    )
    proof = derive_sphere_any_hit_count_proof(callback)
    from .v4_sphere_any_hit_count_contract import (
        SphereAnyHitCountBehaviorSchema,
        compile_sphere_any_hit_count_abi,
    )

    abi = compile_sphere_any_hit_count_abi(authority, proof)
    verify_sphere_any_hit_count_abi(abi, authority, proof)
    behavior = SphereAnyHitCountBehaviorSchema(
        callback.ir_sha256, callback.effect_digest, schema.schema_sha256
    )
    wrapper = generate_trusted_optix_sphere_any_hit_count_wrapper_v1(
        authority, authority.canonical_plan, abi
    )
    return VerifiedSphereAnyHitCountProgram(
        source,
        target,
        authority,
        proof,
        abi,
        behavior,
        wrapper,
        _token=_TOKEN,
    )


class MaterializedSphereAnyHitCountProgram:
    def __init__(self, program, executable, compiler_log, *, _token) -> None:
        if _token is not _TOKEN:
            _fail("GC006_LIVE_MATERIALIZATION", "materialized", "use materialize")
        self.program = program
        self.executable = executable
        self.compiler_log = compiler_log

    def prepare(self, static_input: SphereAnyHitCountStaticInput):
        if type(static_input) is not SphereAnyHitCountStaticInput:
            _fail("GC007_STATIC_INPUT", "static_input", type(static_input).__name__)
        return PreparedSphereAnyHitCountProgram(self, static_input)


def materialize_sphere_any_hit_count_program(
    program: VerifiedSphereAnyHitCountProgram,
    *,
    toolchain: V4Toolchain,
) -> MaterializedSphereAnyHitCountProgram:
    if type(program) is not VerifiedSphereAnyHitCountProgram:
        _fail("GC008_MATERIALIZE_INPUT", "program", type(program).__name__)
    if type(toolchain) is not V4Toolchain:
        _fail("GC008_MATERIALIZE_INPUT", "toolchain", type(toolchain).__name__)
    from .v4_sphere_any_hit_count_optix_compiler import (
        compile_verified_sphere_any_hit_count_executable,
    )

    executable, log = compile_verified_sphere_any_hit_count_executable(
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
    return MaterializedSphereAnyHitCountProgram(
        program, executable, log, _token=_TOKEN
    )


class PreparedSphereAnyHitCountProgram:
    def __init__(self, materialized, static_input) -> None:
        from .v4_sphere_any_hit_count_prepared_runtime import (
            PreparedSphereAnyHitCountOwner,
        )

        program = materialized.program
        self._owner = PreparedSphereAnyHitCountOwner(
            authority=program.authority,
            plan=program.authority.canonical_plan,
            abi=program.abi,
            executable=materialized.executable,
            centers=static_input.centers,
            radii=static_input.radii,
            native_library_path=program.target.native_library_path,
        )

    @property
    def lifecycle_receipt(self):
        return self._owner.lifecycle_receipt

    @property
    def last_failure_receipt(self):
        return self._owner.last_failure_receipt

    def execute(self, batch: MotionSegmentBatch):
        if type(batch) is not MotionSegmentBatch:
            _fail("GC009_BATCH", "batch", type(batch).__name__)
        return self._owner.execute(batch.queries)

    def close(self) -> None:
        self._owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


__all__ = [
    "MaterializedSphereAnyHitCountProgram",
    "MotionSegmentBatch",
    "PreparedSphereAnyHitCountProgram",
    "PublicSphereAnyHitCountError",
    "SphereAnyHitCountStaticInput",
    "V4SphereTarget",
    "VerifiedSphereAnyHitCountProgram",
    "VerifiedSphereAnyHitCountSource",
    "compile_sphere_any_hit_count_program",
    "materialize_sphere_any_hit_count_program",
    "sphere_any_hit_count_source",
]
