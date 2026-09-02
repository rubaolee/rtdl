"""Public lifecycle for curve owner-grouped any-hit Boolean reduction."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import struct

from .v4_callback_lifecycle import V4Toolchain
from .v4_curve_owner_grouped_any_hit_optix_compiler import (
    compile_verified_curve_owner_grouped_any_hit_executable,
)
from .v4_curve_owner_grouped_any_hit_optix_wrapper_codegen import (
    generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1,
)
from .v4_curve_owner_grouped_any_hit_prepared_runtime import (
    PreparedCurveOwnerGroupedAnyHit,
)
from .v4_curve_owner_grouped_any_hit_standard_library import (
    CURVE_OWNER_GROUPED_ANY_HIT_SOURCE,
    build_curve_owner_grouped_any_hit_authority,
)
from .v4_owner_grouped_any_hit import compile_owner_grouped_any_hit_abi
from .v4_public_builtin_curve import V4CurveTarget


_TOKEN = object()


class PublicCurveOwnerGroupedAnyHitError(RuntimeError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise PublicCurveOwnerGroupedAnyHitError(code, path, message)


def _f32(value: object, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) \
            or not math.isfinite(float(value)):
        _fail("GOG001_F32", path, repr(value))
    try:
        result = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    except OverflowError:
        _fail("GOG001_F32", path, repr(value))
    if not math.isfinite(result):
        _fail("GOG001_F32", path, repr(value))
    return result


@dataclass(frozen=True)
class OwnerGroupedCurveStaticInput:
    control_points: object
    widths: object
    segment_indices: object
    owner_ids: object
    owner_count: int

    def __post_init__(self) -> None:
        try:
            source_points = tuple(tuple(row) for row in self.control_points)
            source_widths = tuple(self.widths)
            source_indices = tuple(self.segment_indices)
            source_owners = tuple(self.owner_ids)
        except TypeError:
            _fail("GOG002_STATIC_SHAPE", "static_input", "iterable columns required")
        if len(source_points) < 2 or len(source_points) != len(source_widths):
            _fail(
                "GOG003_VERTEX_CARDINALITY", "static_input",
                "at least two points and one width per point required",
            )
        if not source_indices or len(source_indices) != len(source_owners):
            _fail(
                "GOG004_PRIMITIVE_CARDINALITY", "static_input",
                "equal nonzero index and owner columns required",
            )
        if not isinstance(self.owner_count, int) \
                or isinstance(self.owner_count, bool) \
                or not 1 <= self.owner_count <= 0xFFFFFFFF:
            _fail("GOG005_OWNER_COUNT", "owner_count", repr(self.owner_count))
        points = []
        widths = []
        for index, point in enumerate(source_points):
            if len(point) != 3:
                _fail("GOG006_POINT", f"control_points[{index}]", "vec3 required")
            points.append(tuple(_f32(value, f"control_points[{index}]")
                                for value in point))
            width = _f32(source_widths[index], f"widths[{index}]")
            if width <= 0.0:
                _fail("GOG007_WIDTH", f"widths[{index}]", "positive radius required")
            widths.append(width)
        indices = []
        owners = []
        for primitive, (start, owner) in enumerate(
                zip(source_indices, source_owners)):
            if not isinstance(start, int) or isinstance(start, bool) \
                    or not 0 <= start < len(points) - 1:
                _fail("GOG008_SEGMENT_INDEX", f"segment_indices[{primitive}]", repr(start))
            if points[start] == points[start + 1]:
                _fail("GOG009_ZERO_SEGMENT", f"segment_indices[{primitive}]", repr(start))
            if widths[start] != widths[start + 1]:
                _fail("GOG010_TAPERED", f"segment_indices[{primitive}]", repr(start))
            if not isinstance(owner, int) or isinstance(owner, bool) \
                    or not 0 <= owner < self.owner_count:
                _fail("GOG011_OWNER", f"owner_ids[{primitive}]", repr(owner))
            indices.append(start)
            owners.append(owner)
        if len(set(indices)) != len(indices):
            _fail("GOG012_DUPLICATE_SEGMENT", "segment_indices", "unique starts required")
        object.__setattr__(self, "control_points", tuple(points))
        object.__setattr__(self, "widths", tuple(widths))
        object.__setattr__(self, "segment_indices", tuple(indices))
        object.__setattr__(self, "owner_ids", tuple(owners))


@dataclass(frozen=True)
class OwnerGroupedCurveQueryBatch:
    queries: object

    def __post_init__(self) -> None:
        from .v4_curve_physical_schema import verify_curve_boolean_motion_segments

        try:
            rows = tuple(tuple(row) for row in self.queries)
            if any(len(row) != 2 for row in rows):
                raise ValueError
            starts = tuple(tuple(row[0]) for row in rows)
            ends = tuple(tuple(row[1]) for row in rows)
        except (TypeError, ValueError):
            _fail("GOG013_QUERY_SHAPE", "queries", "(start,end) rows required")
        try:
            normalized = verify_curve_boolean_motion_segments(starts, ends)
        except Exception as exc:
            _fail("GOG013_QUERY_SHAPE", "queries", str(exc))
        object.__setattr__(self, "queries", tuple(
            (row[:3], row[3:]) for row in normalized))


class VerifiedCurveOwnerGroupedAnyHitSource:
    def __init__(self, authority_builder, source_sha256: str, *, _token) -> None:
        if _token is not _TOKEN:
            _fail("GOG014_LIVE_SOURCE", "source", "use public source constructor")
        self._authority_builder = authority_builder
        self.source_sha256 = source_sha256

    def compile(self, *, target: V4CurveTarget):
        if not isinstance(target, V4CurveTarget):
            _fail("GOG015_TARGET", "target", type(target).__name__)
        authority, proof = self._authority_builder(target.profile)
        abi = compile_owner_grouped_any_hit_abi(authority.behavior)
        wrapper = generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1(
            authority, abi)
        return VerifiedCurveOwnerGroupedAnyHitProgram(
            target, authority, proof, abi, wrapper, _token=_TOKEN)


class VerifiedCurveOwnerGroupedAnyHitProgram:
    def __init__(self, target, authority, proof, abi, wrapper, *, _token) -> None:
        if _token is not _TOKEN:
            _fail("GOG016_LIVE_PROGRAM", "program", "use public compiler")
        self.target = target
        self.authority = authority
        self.proof = proof
        self.abi = abi
        self.wrapper = wrapper

    def materialize(self, *, toolchain: V4Toolchain):
        if not isinstance(toolchain, V4Toolchain):
            _fail("GOG017_TOOLCHAIN", "toolchain", type(toolchain).__name__)
        executable, compiler_log = \
            compile_verified_curve_owner_grouped_any_hit_executable(
                self.authority,
                self.abi,
                compute_capability=toolchain.compute_capability,
                optix_include=toolchain.optix_include,
                cuda_include=toolchain.cuda_include,
                expected_python_version=toolchain.expected_python_version,
                expected_numba_version=toolchain.expected_numba_version,
                expected_numpy_version=toolchain.expected_numpy_version,
            )
        return MaterializedCurveOwnerGroupedAnyHitProgram(
            self, executable, compiler_log, _token=_TOKEN)


class MaterializedCurveOwnerGroupedAnyHitProgram:
    def __init__(self, program, executable, compiler_log, *, _token) -> None:
        if _token is not _TOKEN:
            _fail("GOG018_LIVE_MATERIALIZATION", "materialized", "use materialize")
        self.program = program
        self.executable = executable
        self.compiler_log = compiler_log

    def prepare(self, static_input: OwnerGroupedCurveStaticInput):
        if not isinstance(static_input, OwnerGroupedCurveStaticInput):
            _fail("GOG019_STATIC_INPUT", "static_input", type(static_input).__name__)
        return PreparedCurveOwnerGroupedAnyHitProgram(self, static_input)


class PreparedCurveOwnerGroupedAnyHitProgram:
    def __init__(self, materialized, static_input) -> None:
        program = materialized.program
        self._owner = PreparedCurveOwnerGroupedAnyHit(
            authority=program.authority,
            abi=program.abi,
            executable=materialized.executable,
            control_points=static_input.control_points,
            widths=static_input.widths,
            segment_indices=static_input.segment_indices,
            owner_ids=static_input.owner_ids,
            owner_count=static_input.owner_count,
            native_library_path=program.target.native_library_path,
        )

    @property
    def lifecycle_receipt(self):
        return self._owner.lifecycle_receipt

    def execute(self, batch: OwnerGroupedCurveQueryBatch):
        if not isinstance(batch, OwnerGroupedCurveQueryBatch):
            _fail("GOG020_BATCH", "batch", type(batch).__name__)
        return self._owner.execute(batch.queries)

    def close(self):
        self._owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def curve_owner_grouped_any_hit_source() \
        -> VerifiedCurveOwnerGroupedAnyHitSource:
    return VerifiedCurveOwnerGroupedAnyHitSource(
        build_curve_owner_grouped_any_hit_authority,
        hashlib.sha256(
            CURVE_OWNER_GROUPED_ANY_HIT_SOURCE.encode("utf-8")).hexdigest(),
        _token=_TOKEN,
    )


__all__ = [
    "MaterializedCurveOwnerGroupedAnyHitProgram",
    "OwnerGroupedCurveQueryBatch", "OwnerGroupedCurveStaticInput",
    "PreparedCurveOwnerGroupedAnyHitProgram",
    "PublicCurveOwnerGroupedAnyHitError", "V4CurveTarget",
    "VerifiedCurveOwnerGroupedAnyHitProgram",
    "VerifiedCurveOwnerGroupedAnyHitSource",
    "curve_owner_grouped_any_hit_source",
]
