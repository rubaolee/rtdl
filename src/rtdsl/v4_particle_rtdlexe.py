"""Public verified ``.rtdlexe`` lifecycle for Particle strict-interior lookup.

This module is a standard-library specialization, not a general callback
compiler.  The build-only entry point binds an accepted
``compile_standard_builtin_triangle_program`` result to the exact shared
strict-interior device template, compiles that template twice with the same
absolute NVCC tool, and freezes only byte-identical PTX.  The deployment path
does not import the RTDL compiler, Numba, or NVRTC.  It loads one
content-addressed artifact and calls only the six product-native Particle
ABIs: source query, descriptor query, prepare, defensive execute,
sealed-prevalidated execute, and destroy.

The specialization deliberately excludes edge/vertex ties and complete
multi-step particle advection.  It implements only the frozen strict-interior
closest-face core.
"""

from __future__ import annotations

import base64
import ctypes
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import threading
from types import MappingProxyType, SimpleNamespace
from typing import Mapping, Sequence
import weakref


_ARTIFACT_SCHEMA = "rtdl.v4.particle_strict_interior.rtdlexe.v1"
_SPECIALIZATION_SCHEMA = (
    "rtdl.v4.particle_strict_interior.standard_lowering.v1")
_BUILD_SCHEMA = "rtdl.v4.particle_strict_interior.nvcc_reproducible_build.v1"
_QUERY_COUNT = 5_000
_QUERY_COLUMN_COUNT = 7
_QUERY_H2D_BYTES = 140_000
_OUTPUT_D2H_BYTES = 60_000
_CONTROL_BYTES = 16
_PARAMETER_BYTES = 120
_U32_MAX = 0xFFFFFFFF
_SHA256 = re.compile(r"[0-9a-f]{64}")

_SOURCE_SYMBOL = "rtdl_optix_v4_particle_strict_interior_source_v1"
_DESCRIPTOR_SYMBOL = "rtdl_optix_v4_particle_strict_interior_descriptor_v1"
_PREPARE_SYMBOL = "rtdl_optix_v4_prepare_particle_strict_interior_v1"
_EXECUTE_SYMBOL = (
    "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2")
_EXECUTE_PREVALIDATED_SYMBOL = (
    "rtdl_optix_v4_execute_prepared_particle_strict_interior_"
    "prevalidated_v3")
_DESTROY_SYMBOL = "rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1"
_PRODUCT_SYMBOLS = (
    _SOURCE_SYMBOL, _DESCRIPTOR_SYMBOL, _PREPARE_SYMBOL, _EXECUTE_SYMBOL,
    _EXECUTE_PREVALIDATED_SYMBOL, _DESTROY_SYMBOL,
)
_PTX_ENTRY_PATTERN = re.compile(
    rb"(?m)^[ \t]*(?:\.visible[ \t]+)?\.entry[ \t]+([^\s(]+)"
)
_EXPECTED_PTX_ENTRIES = {
    b"__raygen__rtdl_particle_strict_interior",
    b"__closesthit__rtdl_particle_strict_interior",
    b"__miss__rtdl_particle_strict_interior",
}


class ParticleRTDLExecutableError(RuntimeError):
    """Fail-closed public lifecycle error with a stable reason id."""

    def __init__(self, code: str, path: str, detail: object) -> None:
        self.code = code
        self.path = path
        self.detail = str(detail)
        super().__init__(f"{code}@{path}: {detail}")


class ParticleDeviceStatusError(ParticleRTDLExecutableError):
    """Validated device failure with the complete immutable native evidence."""

    def __init__(
        self, *, control: Mapping[str, int], receipt: Mapping[str, int],
    ) -> None:
        self.control = MappingProxyType(dict(control))
        self.receipt = MappingProxyType(dict(receipt))
        super().__init__(
            "PX071_DEVICE_STATUS_FAILED", "execute.control",
            {"control": dict(self.control), "receipt": dict(self.receipt)},
        )


def _fail(code: str, path: str, detail: object) -> None:
    raise ParticleRTDLExecutableError(code, path, detail)


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        _fail("PX001_CANONICAL_JSON_INVALID", "json", exc)


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _digest(value: object) -> str:
    return _sha_bytes(_canonical(value))


def _require_sha(value: object, path: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        _fail("PX002_SHA256_INVALID", path, value)
    return value


def _require_exact_keys(
    value: object, expected: set[str], path: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != expected:
        observed = sorted(value) if isinstance(value, Mapping) else type(value).__name__
        _fail("PX003_SCHEMA_INVALID", path, observed)
    return value


def _read_regular_bytes(path: str | os.PathLike[str], *, code: str) -> bytes:
    resolved = Path(path).expanduser().resolve(strict=True)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(resolved, flags)
    except OSError as exc:
        _fail(code, str(resolved), exc)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            _fail(code, str(resolved), "regular file required")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size) != (
                after.st_dev, after.st_ino, after.st_size):
            _fail(code, str(resolved), "file identity changed while reading")
        payload = b"".join(chunks)
        if len(payload) != before.st_size:
            _fail(code, str(resolved), "short read")
        return payload
    finally:
        os.close(descriptor)


def _write_create_or_exact(path: Path, payload: bytes, *, code: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(
            path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o644,
        )
    except FileExistsError:
        if _read_regular_bytes(path, code=code) != payload:
            _fail(code, str(path), "existing bytes differ")
        return
    except OSError as exc:
        _fail(code, str(path), exc)
    try:
        offset = 0
        while offset != len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                _fail(code, str(path), "short write")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _parse_canonical_artifact(raw: bytes) -> Mapping[str, object]:
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        _fail("PX004_ARTIFACT_NONCANONICAL", "artifact", "one terminal LF required")
    try:
        value = json.loads(raw[:-1].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("PX004_ARTIFACT_NONCANONICAL", "artifact", exc)
    if _canonical(value) + b"\n" != raw:
        _fail("PX004_ARTIFACT_NONCANONICAL", "artifact", "canonical bytes required")
    if not isinstance(value, Mapping):
        _fail("PX003_SCHEMA_INVALID", "artifact", type(value).__name__)
    return value


def _require_exact_ptx_entry_set(ptx: bytes, path: str) -> bytes:
    entries = _PTX_ENTRY_PATTERN.findall(ptx)
    if len(entries) != len(_EXPECTED_PTX_ENTRIES) \
            or set(entries) != _EXPECTED_PTX_ENTRIES:
        _fail("PX011_PTX_ENTRY_SET_INVALID", path, [
            item.decode("ascii", errors="replace") for item in entries
        ])
    return ptx


class _ParticleControl(ctypes.Structure):
    _fields_ = [
        ("validated_row_count", ctypes.c_uint32),
        ("first_error", ctypes.c_uint32),
        ("error_code", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
    ]


class _ParticleFastReceipt(ctypes.Structure):
    _fields_ = [
        ("schema_version", ctypes.c_uint32),
        ("optix_launch_count", ctypes.c_uint32),
        ("query_count", ctypes.c_uint32),
        ("query_h2d_copy_call_count", ctypes.c_uint32),
        ("control_reset_h2d_copy_call_count", ctypes.c_uint32),
        ("parameter_h2d_copy_call_count", ctypes.c_uint32),
        ("control_d2h_copy_call_count", ctypes.c_uint32),
        ("output_d2h_copy_call_count", ctypes.c_uint32),
        ("host_blocking_boundary_count", ctypes.c_uint32),
        ("status_before_output", ctypes.c_uint32),
        ("query_h2d_bytes", ctypes.c_uint64),
        ("control_reset_h2d_bytes", ctypes.c_uint64),
        ("parameter_h2d_bytes", ctypes.c_uint64),
        ("control_d2h_bytes", ctypes.c_uint64),
        ("output_d2h_bytes", ctypes.c_uint64),
        ("output_d2h_after_status_failure", ctypes.c_uint64),
        ("boundary_owner_table_bytes", ctypes.c_uint64),
    ]


if ctypes.sizeof(_ParticleControl) != 16:  # pragma: no cover - ABI invariant
    raise RuntimeError("Particle control ctypes layout changed")
if ctypes.sizeof(_ParticleFastReceipt) != 96:  # pragma: no cover
    raise RuntimeError("Particle receipt ctypes layout changed")


_SUCCESS_RECEIPT_VALUES = MappingProxyType({
    "schema_version": 1,
    "optix_launch_count": 1,
    "query_count": _QUERY_COUNT,
    "query_h2d_copy_call_count": 7,
    "control_reset_h2d_copy_call_count": 1,
    "parameter_h2d_copy_call_count": 1,
    "control_d2h_copy_call_count": 1,
    "output_d2h_copy_call_count": 1,
    "host_blocking_boundary_count": 2,
    "status_before_output": 1,
    "query_h2d_bytes": _QUERY_H2D_BYTES,
    "control_reset_h2d_bytes": _CONTROL_BYTES,
    "parameter_h2d_bytes": _PARAMETER_BYTES,
    "control_d2h_bytes": _CONTROL_BYTES,
    "output_d2h_bytes": _OUTPUT_D2H_BYTES,
    "output_d2h_after_status_failure": 0,
    "boundary_owner_table_bytes": 0,
})
_SUCCESS_RECEIPT_BYTES = bytes(_ParticleFastReceipt(
    **dict(_SUCCESS_RECEIPT_VALUES)))


@dataclass(frozen=True)
class BuiltParticleRTDLExecutable:
    artifact_path: Path
    artifact_sha256: str
    artifact_bytes: int
    source_path: Path
    descriptor_path: Path
    ptx_pass1_path: Path
    ptx_pass2_path: Path
    ptx_sha256: str
    native_library_sha256: str
    protocol_decision_sha256: str
    template_semantic_sha256: str
    nvcc_absolute_path: Path
    optix_include_absolute_path: Path
    nvcc_executable_sha256: str
    optix_device_header_sha256: str


_DEPLOYMENT_TOKEN = object()
_DEPLOYMENT_REGISTRY_LOCK = threading.Lock()
_DEPLOYMENT_REGISTRY: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


class InstalledParticleRTDLDeployment:
    """Request-external trust capability for one exact deployment tuple."""

    __slots__ = (
        "_deployment_id", "_expected_artifact_sha256",
        "_expected_native_sha256", "_expected_protocol_decision_sha256",
        "_expected_template_semantic_sha256", "_token", "__weakref__",
    )

    def __init__(
        self, *, deployment_id: str, expected_artifact_sha256: str,
        expected_native_sha256: str, expected_protocol_decision_sha256: str,
        expected_template_semantic_sha256: str, _token: object,
    ) -> None:
        if _token is not _DEPLOYMENT_TOKEN:
            _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "deployment", "use installer")
        object.__setattr__(self, "_deployment_id", deployment_id)
        object.__setattr__(self, "_expected_artifact_sha256", expected_artifact_sha256)
        object.__setattr__(self, "_expected_native_sha256", expected_native_sha256)
        object.__setattr__(
            self, "_expected_protocol_decision_sha256",
            expected_protocol_decision_sha256)
        object.__setattr__(
            self, "_expected_template_semantic_sha256",
            expected_template_semantic_sha256)
        object.__setattr__(self, "_token", _token)

    def __setattr__(self, name: str, value: object) -> None:
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "deployment", "immutable")

    @property
    def deployment_id(self) -> str:
        return self._deployment_id

    @property
    def expected_artifact_sha256(self) -> str:
        return self._expected_artifact_sha256

    @property
    def expected_native_sha256(self) -> str:
        return self._expected_native_sha256

    @property
    def expected_protocol_decision_sha256(self) -> str:
        return self._expected_protocol_decision_sha256

    @property
    def expected_template_semantic_sha256(self) -> str:
        return self._expected_template_semantic_sha256

    def __getstate__(self):
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "deployment", "not serializable")

    def __reduce__(self):
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "deployment", "not serializable")


def install_particle_rtdlexe_deployment(
    *, deployment_id: str, expected_artifact_sha256: str,
    expected_native_sha256: str, expected_protocol_decision_sha256: str,
    expected_template_semantic_sha256: str,
) -> InstalledParticleRTDLDeployment:
    """Carry externally selected identities; this does not authenticate provenance."""

    if not isinstance(deployment_id, str) or not deployment_id:
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "deployment_id", deployment_id)
    capability = InstalledParticleRTDLDeployment(
        deployment_id=deployment_id,
        expected_artifact_sha256=_require_sha(
            expected_artifact_sha256, "deployment.artifact_sha256"),
        expected_native_sha256=_require_sha(
            expected_native_sha256, "deployment.native_sha256"),
        expected_protocol_decision_sha256=_require_sha(
            expected_protocol_decision_sha256,
            "deployment.protocol_decision_sha256"),
        expected_template_semantic_sha256=_require_sha(
            expected_template_semantic_sha256,
            "deployment.template_semantic_sha256"),
        _token=_DEPLOYMENT_TOKEN,
    )
    registry_value = (
        capability.deployment_id, capability.expected_artifact_sha256,
        capability.expected_native_sha256,
        capability.expected_protocol_decision_sha256,
        capability.expected_template_semantic_sha256,
    )
    with _DEPLOYMENT_REGISTRY_LOCK:
        _DEPLOYMENT_REGISTRY[capability] = registry_value
    return capability


def _require_installed_deployment(value: object) -> InstalledParticleRTDLDeployment:
    if not isinstance(value, InstalledParticleRTDLDeployment):
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "deployment", "installed capability required")
    observed = (
        value.deployment_id, value.expected_artifact_sha256,
        value.expected_native_sha256, value.expected_protocol_decision_sha256,
        value.expected_template_semantic_sha256,
    )
    with _DEPLOYMENT_REGISTRY_LOCK:
        issued = _DEPLOYMENT_REGISTRY.get(value)
    if value._token is not _DEPLOYMENT_TOKEN or issued != observed:
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "deployment", "unissued or mutated capability")
    return value


class PrevalidatedParticleRTDLExecutionInput:
    """Sealed immutable query/oracle bytes admitted before a formal clock."""

    __slots__ = (
        "_columns", "_expected", "_pointers", "_object_ids", "_sealed",
        "__weakref__",
    )

    def __new__(cls, *args, **kwargs):
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "prevalidated_input",
            "use prevalidate_particle_rtdlexe_exact_core_input")

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_sealed", False):
            _fail(
                "PX024_PREVALIDATED_INPUT_INVALID", "prevalidated_input",
                "immutable")
        object.__setattr__(self, name, value)

    @property
    def columns(self) -> tuple[object, ...]:
        return self._columns

    @property
    def expected_u32x3(self) -> object:
        return self._expected


_PREVALIDATED_PARTICLE_INPUTS: weakref.WeakKeyDictionary = \
    weakref.WeakKeyDictionary()


def _new_prevalidated_particle_rtdlexe_input(
    columns: tuple[object, ...], expected: object,
) -> PrevalidatedParticleRTDLExecutionInput:
    value = object.__new__(PrevalidatedParticleRTDLExecutionInput)
    arrays = (*columns, expected)
    pointers = tuple(int(item.ctypes.data) for item in arrays)
    object_ids = tuple(id(item) for item in arrays)
    object.__setattr__(value, "_columns", columns)
    object.__setattr__(value, "_expected", expected)
    object.__setattr__(value, "_pointers", pointers)
    object.__setattr__(value, "_object_ids", object_ids)
    object.__setattr__(value, "_sealed", True)
    _PREVALIDATED_PARTICLE_INPUTS[value] = (
        columns, expected, pointers, object_ids)
    return value


def prevalidate_particle_rtdlexe_exact_core_input(
    query_ox, query_oy, query_oz, query_dx, query_dy, query_dz, query_tmax,
    *, expected_u32x3,
) -> PrevalidatedParticleRTDLExecutionInput:
    """Copy validated formal input into immutable backing before any clock."""

    np = _numpy()
    caller_values = (
        query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
        query_tmax,
    )
    if any(type(value) is not np.ndarray for value in caller_values) \
            or type(expected_u32x3) is not np.ndarray:
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "prevalidated_input",
            "exact base ndarray storage required")
    caller_columns = tuple(
        np.ndarray.view(
            _require_numpy_array(
                np, column, f"query[{index}]", "<f4", 1), np.ndarray)
        for index, column in enumerate(caller_values))
    if any(column.shape != (_QUERY_COUNT,) for column in caller_columns):
        _fail(
            "PX022_QUERY_SHAPE_INVALID", "query",
            [item.shape for item in caller_columns])
    caller_expected = np.ndarray.view(
        _require_numpy_array(
            np, expected_u32x3, "expected_u32x3", "<u4", 2, 3),
        np.ndarray)
    if caller_expected.shape != (_QUERY_COUNT, 3):
        _fail(
            "PX023_ORACLE_SHAPE_INVALID", "expected_u32x3",
            caller_expected.shape)
    for index, column in enumerate(caller_columns):
        if column.flags.writeable:
            _fail(
                "PX024_PREVALIDATED_INPUT_INVALID", f"query[{index}]",
                "read-only storage required")
    if caller_expected.flags.writeable:
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "expected_u32x3",
            "read-only storage required")

    # Snapshot through the ndarray base-class implementation before validating
    # any value.  This prevents an ndarray subclass from presenting one value
    # to NumPy validation while overriding virtual helpers such as ``tobytes``
    # to seal different bytes.  A read-only view over mutable caller storage is
    # also safe: all subsequent validation and execution use only these exact
    # immutable bytes-backed snapshots.
    admitted_columns = tuple(
        np.frombuffer(
            np.ndarray.tobytes(column, order="C"), dtype=np.float32)
        for column in caller_columns)
    admitted_expected = np.ndarray(
        shape=(_QUERY_COUNT, 3), dtype=np.uint32,
        buffer=np.ndarray.tobytes(caller_expected, order="C"), order="C")

    columns = admitted_columns
    expected = admitted_expected
    if not all(bool(np.isfinite(column).all()) for column in columns):
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "query",
            "nonfinite value")
    if bool((columns[6] <= np.float32(0.0)).any()):
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "query_tmax",
            "nonpositive value")
    if bool(((columns[3] == np.float32(0.0))
             & (columns[4] == np.float32(0.0))
             & (columns[5] == np.float32(0.0))).any()):
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "query.direction",
            "zero direction")

    return _new_prevalidated_particle_rtdlexe_input(
        admitted_columns, admitted_expected)


def _require_prevalidated_particle_rtdlexe_input(
    np, value: object,
) -> tuple[tuple[object, ...], object]:
    if type(value) is not PrevalidatedParticleRTDLExecutionInput:
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "prevalidated_input",
            "public sealed token required")
    registered = _PREVALIDATED_PARTICLE_INPUTS.get(value)
    if registered is None:
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "prevalidated_input",
            "unissued token")
    columns, expected, pointers, object_ids = registered
    arrays = (*columns, expected)
    if (value._columns is not columns or value._expected is not expected
            or value._pointers != pointers or value._object_ids != object_ids
            or value._sealed is not True
            or tuple(int(item.ctypes.data) for item in arrays) != pointers
            or tuple(id(item) for item in arrays) != object_ids
            or any(not isinstance(item.base, bytes) for item in arrays)
            or any(item.flags.writeable for item in arrays)
            or any(not item.flags.c_contiguous for item in arrays)
            or any(item.dtype != np.dtype("<f4")
                   or item.shape != (_QUERY_COUNT,)
                   or item.strides != (4,)
                   for item in columns)
            or expected.dtype != np.dtype("<u4")
            or expected.shape != (_QUERY_COUNT, 3)
            or expected.strides != (12, 4)):
        _fail(
            "PX024_PREVALIDATED_INPUT_INVALID", "prevalidated_input",
            "provenance, pointer, or immutable storage drift")
    return columns, expected


@dataclass(frozen=True)
class ParticleStaticInput:
    """Borrowed public bulk columns; construction performs no row expansion."""

    vertices_f32: object
    triangles_u32: object
    front_values_u32: object
    back_values_u32: object

    def __post_init__(self) -> None:
        np = _numpy()
        vertices = _require_numpy_array(
            np, self.vertices_f32, "static.vertices_f32", "<f4", 2, 3)
        triangles = _require_numpy_array(
            np, self.triangles_u32, "static.triangles_u32", "<u4", 2, 3)
        front = _require_numpy_array(
            np, self.front_values_u32, "static.front_values_u32", "<u4", 1)
        back = _require_numpy_array(
            np, self.back_values_u32, "static.back_values_u32", "<u4", 1)
        if vertices.shape[0] == 0 or triangles.shape[0] == 0:
            _fail("PX020_STATIC_INPUT_INVALID", "static", "nonempty geometry required")
        if front.shape != (triangles.shape[0],) or back.shape != front.shape:
            _fail("PX020_STATIC_INPUT_INVALID", "static.metadata", "primitive count drift")
        object.__setattr__(self, "vertices_f32", vertices)
        object.__setattr__(self, "triangles_u32", triangles)
        object.__setattr__(self, "front_values_u32", front)
        object.__setattr__(self, "back_values_u32", back)


@dataclass(frozen=True)
class ParticleExecutionResult:
    """Borrowed 5000x3 view over three contiguous native output columns."""

    output_u32x3: object
    control: tuple[int, int, int, int]
    receipt: Mapping[str, int]
    artifact_sha256: str
    ptx_sha256: str


class ParticleExactCoreCompletion:
    """Owner-created borrowed output after the exact measured oracle."""

    __slots__ = (
        "_output_u32x3", "_control", "_receipt", "_output_pointer",
        "_output_rows", "_owner", "_generation", "_packed", "__weakref__",
    )

    def __new__(cls, *args, **kwargs):
        _fail(
            "PX061_LIFECYCLE_STATE_INVALID", "execute.core_completion",
            "completion is prepared-owner-created")


_PARTICLE_CORE_COMPLETIONS: weakref.WeakKeyDictionary = \
    weakref.WeakKeyDictionary()


def _new_particle_core_completion(
    *, output_u32x3, control: _ParticleControl, receipt: _ParticleFastReceipt,
    output_pointer, output_rows: int, owner, generation: int, packed,
) -> ParticleExactCoreCompletion:
    completion = object.__new__(ParticleExactCoreCompletion)
    completion._output_u32x3 = output_u32x3
    completion._control = control
    completion._receipt = receipt
    completion._output_pointer = output_pointer
    completion._output_rows = output_rows
    completion._owner = owner
    completion._generation = generation
    completion._packed = packed
    _PARTICLE_CORE_COMPLETIONS[completion] = (
        output_u32x3, control, receipt, output_pointer, output_rows,
        owner, generation, packed, bytes(control), bytes(receipt),
    )
    return completion


def _numpy():
    # Kept out of the artifact loader.  Formal workers construct common NumPy
    # inputs before timing and therefore have already paid this import.
    import numpy  # pylint: disable=import-outside-toplevel
    return numpy


def _require_numpy_array(
    np, value: object, path: str, dtype: str, ndim: int,
    trailing: int | None = None,
    *, require_c_contiguous: bool = True,
    require_exact_base: bool = False,
):
    # Full exact-oracle entry points are trust boundaries.  ndarray subclasses can
    # override __array_function__/__array_ufunc__ and thereby forge alias,
    # validity, or exact-oracle predicates while the native call still reads
    # their underlying storage.  Those callers request the exact-base rule;
    # lower-level defensive execute retains its historical subclass surface
    # and relies on the native value scan.
    if not isinstance(value, np.ndarray):
        _fail("PX021_BULK_INPUT_REQUIRED", path, type(value).__name__)
    if type(value) is not np.ndarray:
        # Invoke the base implementation directly.  The result is a zero-copy
        # base ndarray view, so later NumPy predicates cannot dispatch through
        # attacker-controlled ndarray-subclass hooks.
        value = np.ndarray.view(value, np.ndarray)
    expected = np.dtype(dtype)
    if (value.dtype != expected or value.ndim != ndim
            or (require_c_contiguous and not value.flags.c_contiguous)):
        _fail("PX021_BULK_INPUT_REQUIRED", path, {
            "dtype": value.dtype.str, "ndim": value.ndim,
            "c_contiguous": bool(value.flags.c_contiguous),
        })
    if trailing is not None and value.shape[-1] != trailing:
        _fail("PX021_BULK_INPUT_REQUIRED", path, value.shape)
    return value


def _array_pointer(value, ctype):
    return ctypes.cast(int(value.ctypes.data), ctypes.POINTER(ctype))


class _VerifiedNativeImage:
    """Exact-byte native image loaded without the historical private loader."""

    def __init__(self, *, library: object, descriptor: int | None, sha256: str) -> None:
        self.library = library
        self.descriptor = descriptor
        self.sha256 = sha256

    def close(self) -> None:
        descriptor, self.descriptor = self.descriptor, None
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def _open_verified_native(
    path: str | os.PathLike[str], *, expected_sha256: str,
) -> _VerifiedNativeImage:
    expected_sha256 = _require_sha(expected_sha256, "native.sha256")
    payload = _read_regular_bytes(path, code="PX030_NATIVE_READ_FAILED")
    observed = _sha_bytes(payload)
    if observed != expected_sha256:
        _fail("PX031_NATIVE_IDENTITY_MISMATCH", "native.sha256", {
            "expected": expected_sha256, "observed": observed,
        })
    mode = getattr(os, "RTLD_LOCAL", 0) | getattr(os, "RTLD_NOW", 0)
    if hasattr(os, "memfd_create") and Path("/proc/self/fd").is_dir():
        flags = getattr(os, "MFD_CLOEXEC", 0) | getattr(os, "MFD_ALLOW_SEALING", 0)
        descriptor = os.memfd_create(
            f"rtdl_particle_{observed[:16]}", flags=flags)
        try:
            offset = 0
            while offset != len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    _fail("PX030_NATIVE_READ_FAILED", "native.memfd", "short write")
                offset += written
            os.lseek(descriptor, 0, os.SEEK_SET)
            try:
                import fcntl  # pylint: disable=import-outside-toplevel
                seals = (
                    getattr(fcntl, "F_SEAL_SEAL", 0)
                    | getattr(fcntl, "F_SEAL_SHRINK", 0)
                    | getattr(fcntl, "F_SEAL_GROW", 0)
                    | getattr(fcntl, "F_SEAL_WRITE", 0)
                )
                if seals:
                    fcntl.fcntl(descriptor, fcntl.F_ADD_SEALS, seals)
            except (ImportError, OSError, AttributeError):
                pass
            library = ctypes.CDLL(f"/proc/self/fd/{descriptor}", mode=mode)
            return _VerifiedNativeImage(
                library=library, descriptor=descriptor, sha256=observed)
        except BaseException:
            os.close(descriptor)
            raise
    # Non-Linux fallback still loads private exact copied bytes, never the
    # mutable caller path.  It is not used by the Linux formal target.
    temporary = tempfile.NamedTemporaryFile(prefix="rtdl_particle_", suffix=".so", delete=False)
    try:
        temporary.write(payload)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary.close()
        library = ctypes.CDLL(temporary.name, mode=mode)
    except BaseException:
        temporary.close()
        try:
            os.unlink(temporary.name)
        except OSError:
            pass
        raise
    try:
        os.unlink(temporary.name)
    except OSError:
        pass
    return _VerifiedNativeImage(library=library, descriptor=None, sha256=observed)


def _raise_native(result: int, error, path: str) -> None:
    if result != 0:
        detail = bytes(error.value).decode("utf-8", errors="replace")
        _fail("PX032_NATIVE_CALL_FAILED", path, detail or result)


class _ParticleNativeApi:
    """The complete and only native symbol surface of this lifecycle."""

    def __init__(self, library: object) -> None:
        missing = [name for name in _PRODUCT_SYMBOLS if not hasattr(library, name)]
        if missing:
            _fail("PX033_NATIVE_SYMBOL_MISSING", "native.symbols", missing)
        self.source = getattr(library, _SOURCE_SYMBOL)
        self.descriptor = getattr(library, _DESCRIPTOR_SYMBOL)
        self.prepare = getattr(library, _PREPARE_SYMBOL)
        self.execute = getattr(library, _EXECUTE_SYMBOL)
        self.execute_prevalidated = getattr(
            library, _EXECUTE_PREVALIDATED_SYMBOL)
        self.destroy = getattr(library, _DESTROY_SYMBOL)
        query_args = [
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_char),
            ctypes.c_size_t,
        ]
        for query in (self.source, self.descriptor):
            query.argtypes = query_args
            query.restype = ctypes.c_int
        self.prepare.argtypes = [
            ctypes.c_char_p, ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
            ctypes.c_size_t,
        ]
        self.prepare.restype = ctypes.c_int
        self.execute.argtypes = [
            ctypes.c_uint64,
            *([ctypes.POINTER(ctypes.c_float)] * _QUERY_COLUMN_COUNT),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)),
            ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(_ParticleControl),
            ctypes.POINTER(_ParticleFastReceipt), ctypes.POINTER(ctypes.c_char),
            ctypes.c_size_t,
        ]
        self.execute.restype = ctypes.c_int
        self.execute_prevalidated.argtypes = list(self.execute.argtypes)
        self.execute_prevalidated.restype = ctypes.c_int
        self.destroy.argtypes = [
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char),
            ctypes.c_size_t,
        ]
        self.destroy.restype = ctypes.c_int

    @staticmethod
    def _query(function, path: str) -> bytes:
        error = ctypes.create_string_buffer(16_384)
        byte_count = ctypes.c_size_t()
        _raise_native(int(function(
            None, 0, ctypes.byref(byte_count), error, len(error))), error, path)
        output = ctypes.create_string_buffer(byte_count.value + 1)
        _raise_native(int(function(
            output, len(output), ctypes.byref(byte_count), error, len(error))),
            error, path)
        return bytes(output.raw[:byte_count.value])

    def query_source(self) -> bytes:
        return self._query(self.source, "native.source_query")

    def query_descriptor(self) -> bytes:
        return self._query(self.descriptor, "native.descriptor_query")


def _validate_native_descriptor(raw: bytes) -> Mapping[str, object]:
    try:
        descriptor = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("PX034_NATIVE_DESCRIPTOR_INVALID", "native.descriptor", exc)
    if not isinstance(descriptor, Mapping):
        _fail("PX034_NATIVE_DESCRIPTOR_INVALID", "native.descriptor", type(descriptor).__name__)
    try:
        entries = descriptor["entry_points"]
        domain = descriptor["domain"]
        transfer = descriptor["transfer_contract"]
        host_validation = descriptor["host_value_validation_contract"]
        layout = descriptor["launch_parameter_layout"]
        pipeline = descriptor["pipeline_options"]
    except KeyError as exc:
        _fail("PX034_NATIVE_DESCRIPTOR_INVALID", "native.descriptor", exc)
    expected = {
        "schema": "rtdl.v4.particle_strict_interior_template.v1",
        "family": "builtin_triangle_particle_strict_interior_v1",
        "native_abi": "rtdl.v4.prepared_particle_strict_interior.v3",
    }
    if any(descriptor.get(key) != value for key, value in expected.items()):
        _fail("PX034_NATIVE_DESCRIPTOR_INVALID", "native.descriptor.identity", descriptor)
    if entries != {
        "raygen": "__raygen__rtdl_particle_strict_interior",
        "closest_hit": "__closesthit__rtdl_particle_strict_interior",
        "miss": "__miss__rtdl_particle_strict_interior",
        "intersection": None,
        "any_hit": None,
    }:
        _fail("PX034_NATIVE_DESCRIPTOR_INVALID", "native.descriptor.entry_points", entries)
    checks = (
        domain.get("query_count") == _QUERY_COUNT,
        domain.get("unique_closest_face_required") is True,
        domain.get("strictly_positive_barycentric_coordinates_required") is True,
        domain.get("edge_or_vertex_hit") == "OUTSIDE_DOMAIN_FAIL_CLOSED",
        domain.get("full_50000_step_advection") is False,
        layout.get("bytes") == _PARAMETER_BYTES,
        layout.get("query_layout") == "seven_soa_f32",
        layout.get("output_layout") == "selected_neighbor_face_three_soa_u32",
        pipeline.get("payload_values") == 2,
        pipeline.get("attribute_values") == 2,
        pipeline.get("max_trace_depth") == 1,
        transfer.get("query_h2d_bytes") == _QUERY_H2D_BYTES,
        transfer.get("query_h2d_copy_call_count") == 7,
        transfer.get("optix_launch_count") == 1,
        transfer.get("control_d2h_bytes") == _CONTROL_BYTES,
        transfer.get("control_before_output") is True,
        transfer.get("success_output_d2h_bytes") == _OUTPUT_D2H_BYTES,
        transfer.get("failure_output_d2h_bytes") == 0,
        transfer.get("execute_abi_version") == 3,
        transfer.get("legacy_defensive_execute_abi_version") == 2,
        transfer.get("success_host_output")
            == "borrowed_native_owned_pinned_packed_soa_u32",
        transfer.get("borrowed_output_lifetime")
            == "until_next_execute_or_destroy",
        transfer.get("failure_host_output") == "null_pointer_zero_rows",
        descriptor.get("boundary_owner_table") == {
            "present": False, "bytes": 0,
            "avoided_generic_table_bytes_at_frozen_scale": 94_990_840,
        },
        host_validation == {
            "preferred_execute_symbol": _EXECUTE_PREVALIDATED_SYMBOL,
            "authority": (
                "product_public_registry_authenticated_token_over_"
                "immutable_bytes"),
            "admission_timing": "outside_execute",
            "admission_validates": [
                "seven_owned_read_only_c_contiguous_f32_5000",
                "all_query_values_finite", "positive_tmax",
                "nonzero_direction",
                "owned_read_only_c_contiguous_u32_5000x3_oracle",
            ],
            "native_revalidates": [
                "prepared_token", "query_count",
                "seven_non_null_query_pointers", "output_pointers",
            ],
            "native_skips_only": [
                "finite_value_rescan", "positive_tmax_rescan",
                "nonzero_direction_rescan",
            ],
            "legacy_defensive_execute_symbol": _EXECUTE_SYMBOL,
            "legacy_native_value_scan": True,
        },
    )
    if not all(checks):
        _fail("PX034_NATIVE_DESCRIPTOR_INVALID", "native.descriptor.contract", descriptor)
    _require_sha(descriptor.get("source_sha256"), "native.descriptor.source_sha256")
    _require_sha(descriptor.get("semantic_sha256"), "native.descriptor.semantic_sha256")
    return descriptor


def _standard_protocol_bundle(standard_program: object) -> Mapping[str, object]:
    """Build-only accepted projection from the existing standard compiler."""

    from .v4_builtin_triangle_standard_library import (  # build-only imports
        StandardBuiltinTriangleProgram,
        compile_adjacency_callback,
    )
    if not isinstance(standard_program, StandardBuiltinTriangleProgram):
        _fail("PX040_STANDARD_PROGRAM_REQUIRED", "standard_program", type(standard_program).__name__)
    authority = standard_program.authority
    plan = standard_program.plan
    abi = standard_program.abi
    executable = standard_program.executable
    fresh_callback = compile_adjacency_callback()
    if (authority.callback.ir_sha256 != fresh_callback.ir_sha256
            or authority.callback.effect_digest != fresh_callback.effect_digest):
        _fail("PX041_STANDARD_PROGRAM_DRIFT", "standard_program.callback", "not standard adjacency")

    from .v4_triangle_optix_wrapper_codegen import (  # build only
        generate_trusted_optix_triangle_wrapper_v1,
    )
    expected_wrapper = generate_trusted_optix_triangle_wrapper_v1(
        authority, plan, abi)
    if executable.wrapper != expected_wrapper:
        _fail("PX041_STANDARD_PROGRAM_DRIFT", "standard_program.wrapper", "not canonical")

    from .v4_protocol_contract import (  # build only
        CompilerProtocolProjection,
        ProtocolContractDeclaration,
        verify_protocol_contract,
    )
    from .v4_public_builtin_triangle import (  # build-only projection helpers
        _compiled_role_effects,
        _continuation_projection,
        _declared_ownership,
        _declared_physical_facts,
        _declared_role_effects,
        _projected_ownership,
        _projected_physical_facts,
        _rederive_checked_executable_sha256,
        _task_semantics_from_callback,
        _task_semantics_from_compiler,
    )
    declared_physical = _declared_physical_facts(
        authority, plan, expected_wrapper, abi)
    checked_executable = _rederive_checked_executable_sha256(
        executable, authority, plan, abi)
    declaration = ProtocolContractDeclaration(
        family="builtin_triangle_callback_ir",
        task_semantics_sha256=_task_semantics_from_callback(
            authority.callback, authority.schema, plan),
        role_effects=tuple(sorted(
            _declared_role_effects(authority.callback).items())),
        attribute_abi_ownership=tuple(sorted(
            _declared_ownership(authority.callback).items())),
        physical_bindings=tuple(sorted(declared_physical.items())),
        continuation_policy="REQUIRE_COMPLETE_BEFORE_CONSUME",
        checked_executable_sha256=checked_executable,
    )
    projection = CompilerProtocolProjection(
        family="builtin_triangle_callback_ir",
        task_semantics_sha256=_task_semantics_from_compiler(
            authority, plan, abi),
        role_effects=tuple(sorted(_compiled_role_effects(abi).items())),
        attribute_abi_ownership=tuple(sorted(
            _projected_ownership(authority, abi).items())),
        physical_bindings=tuple(sorted(_projected_physical_facts(
            authority, plan, abi, executable).items())),
        continuation_policy=_continuation_projection(executable, abi),
        actual_executable_sha256=str(executable.executable_sha256),
        generated_device_source_sha256=str(executable.composed.ptx_sha256),
        generated_host_source_sha256=_digest({
            "standard_entrypoint": "compile_standard_builtin_triangle_program",
            "expected_wrapper_sha256": expected_wrapper.source_sha256,
        }),
    )
    decision = verify_protocol_contract(declaration, projection)
    if decision.verdict != "ACCEPT" or decision.findings:
        _fail("PX042_STANDARD_PROTOCOL_REJECTED", "standard_program.decision", decision.to_mapping())
    orientation = authority.triangle_orientation_authority
    return {
        "schema": "rtdl.v4.particle_standard_protocol_bundle.v1",
        "producer": "compile_standard_builtin_triangle_program",
        "callback_ir_sha256": authority.callback.ir_sha256,
        "callback_effect_digest": authority.callback.effect_digest,
        "physical_schema_sha256": authority.schema.schema_sha256,
        "canonical_plan_sha256": plan.plan_sha256,
        "callback_abi_sha256": abi.abi_sha256,
        "orientation_authority_sha256": (
            None if orientation is None else orientation.authority_sha256),
        "generic_checked_executable_sha256": checked_executable,
        "generic_composed_ptx_sha256": executable.composed.ptx_sha256,
        "contract": declaration.to_mapping(),
        "projection": projection.to_mapping(),
        "decision": decision.to_mapping(),
    }


def _compile_twice(
    *, source: bytes, source_sha256: str, nvcc_path: Path,
    optix_include: Path, compute_arch: str, build_directory: Path,
) -> tuple[bytes, Mapping[str, object], Path, Path, Path]:
    if not re.fullmatch(r"compute_[0-9]+", compute_arch):
        _fail("PX050_BUILD_INPUT_INVALID", "compute_arch", compute_arch)
    source_path = build_directory / f"{source_sha256}.particle_strict_interior.cu"
    pass1 = build_directory / f"{source_sha256}.{compute_arch}.pass1.ptx"
    pass2 = build_directory / f"{source_sha256}.{compute_arch}.pass2.ptx"
    _write_create_or_exact(source_path, source, code="PX051_BUILD_COLLISION")
    nvcc_bytes = _read_regular_bytes(nvcc_path, code="PX050_BUILD_INPUT_INVALID")
    header_path = optix_include / "optix_device.h"
    header_bytes = _read_regular_bytes(header_path, code="PX050_BUILD_INPUT_INVALID")
    version = subprocess.run(
        [str(nvcc_path), "--version"], check=False, capture_output=True)
    if version.returncode != 0:
        _fail("PX052_NVCC_FAILED", "nvcc.--version", version.stderr.decode(errors="replace"))
    common = [
        str(nvcc_path), "-ptx", "-std=c++14", f"-arch={compute_arch}",
        f"-I{optix_include}", source_path.name,
    ]
    for output in (pass1, pass2):
        completed = subprocess.run(
            [*common, "-o", output.name], cwd=build_directory,
            check=False, capture_output=True)
        if completed.returncode != 0:
            _fail("PX052_NVCC_FAILED", str(output), completed.stderr.decode(errors="replace"))
    ptx1 = _read_regular_bytes(pass1, code="PX052_NVCC_FAILED")
    ptx2 = _read_regular_bytes(pass2, code="PX052_NVCC_FAILED")
    if not ptx1 or ptx1 != ptx2:
        _fail("PX053_PTX_NOT_REPRODUCIBLE", "ptx", {
            "pass1": _sha_bytes(ptx1), "pass2": _sha_bytes(ptx2),
        })
    _require_exact_ptx_entry_set(
        _require_embedded_text(ptx1, "build.ptx"), "build.ptx.entries")
    identity = {
        "schema": _BUILD_SCHEMA,
        "nvcc_executable_sha256": _sha_bytes(nvcc_bytes),
        "nvcc_version_stdout_base64": base64.b64encode(version.stdout).decode("ascii"),
        "nvcc_version_stderr_base64": base64.b64encode(version.stderr).decode("ascii"),
        "optix_device_header_sha256": _sha_bytes(header_bytes),
        "source_sha256": source_sha256,
        "compiler_arguments_path_independent": [
            "nvcc@nvcc_executable_sha256", "-ptx", "-std=c++14",
            f"-arch={compute_arch}", "-I<optix_include@optix_device_header_sha256>",
            f"{source_sha256}.particle_strict_interior.cu", "-o", "<output.ptx>",
        ],
        "independent_invocation_count": 2,
        "ptx_byte_identical": True,
        "ptx_sha256": _sha_bytes(ptx1),
        "ptx_bytes": len(ptx1),
    }
    return ptx1, identity, source_path, pass1, pass2


def _specialization_binding(
    *, protocol_bundle: Mapping[str, object], descriptor: Mapping[str, object],
) -> Mapping[str, object]:
    body = {
        "schema": _SPECIALIZATION_SCHEMA,
        "claim_scope": "STRICT_INTERIOR_STANDARD_LIBRARY_SPECIALIZATION_ONLY",
        "arbitrary_user_dsl_generalization_claimed": False,
        "complete_particle_advection_claimed": False,
        "standard_protocol_decision_sha256": protocol_bundle["decision"]["decision_sha256"],
        "standard_protocol_projection_sha256": protocol_bundle["projection"]["projection_sha256"],
        "standard_callback_ir_sha256": protocol_bundle["callback_ir_sha256"],
        "standard_callback_effect_digest": protocol_bundle["callback_effect_digest"],
        "standard_physical_schema_sha256": protocol_bundle["physical_schema_sha256"],
        "standard_canonical_plan_sha256": protocol_bundle["canonical_plan_sha256"],
        "standard_callback_abi_sha256": protocol_bundle["callback_abi_sha256"],
        "template_semantic_sha256": descriptor["semantic_sha256"],
        "template_source_sha256": descriptor["source_sha256"],
        "role_lowering": {
            "make_ray": "raygen_prefix",
            "closest_hit": "closest_hit",
            "miss": "miss_fail_closed",
            "finalize": "raygen_status_gate_and_u32x3_commit",
        },
        "restricted_domain": {
            "unique_strict_interior_closest_face": True,
            "edge_or_vertex_ties": "OUTSIDE_DOMAIN_FAIL_CLOSED",
        },
        "transfer_contract": dict(descriptor["transfer_contract"]),
        "entry_points": dict(descriptor["entry_points"]),
    }
    return {**body, "binding_sha256": _digest(body)}


def build_particle_rtdlexe(
    standard_program: object,
    *,
    native_library_path: str | os.PathLike[str],
    nvcc_path: str | os.PathLike[str],
    optix_include: str | os.PathLike[str],
    compute_arch: str,
    build_directory: str | os.PathLike[str],
    artifact_directory: str | os.PathLike[str],
) -> BuiltParticleRTDLExecutable:
    """Build and freeze one strict-interior executable outside all timers."""

    protocol_bundle = _standard_protocol_bundle(standard_program)
    native_path = Path(native_library_path).expanduser().resolve(strict=True)
    native_bytes = _read_regular_bytes(native_path, code="PX030_NATIVE_READ_FAILED")
    native_sha = _sha_bytes(native_bytes)
    image = _open_verified_native(native_path, expected_sha256=native_sha)
    try:
        api = _ParticleNativeApi(image.library)
        source = _require_embedded_text(
            api.query_source(), "build.native_source")
        descriptor_bytes = api.query_descriptor()
    finally:
        image.close()
    descriptor = _validate_native_descriptor(descriptor_bytes)
    source_sha = _sha_bytes(source)
    if (source_sha != descriptor["source_sha256"]
            or len(source) != descriptor.get("source_bytes")):
        _fail("PX035_SOURCE_DESCRIPTOR_MISMATCH", "native.source", source_sha)
    nvcc = Path(nvcc_path).expanduser().resolve(strict=True)
    include = Path(optix_include).expanduser().resolve(strict=True)
    build_root = Path(build_directory).expanduser().resolve()
    build_root.mkdir(parents=True, exist_ok=True)
    ptx, build_identity, source_path, pass1, pass2 = _compile_twice(
        source=source, source_sha256=source_sha, nvcc_path=nvcc,
        optix_include=include, compute_arch=compute_arch,
        build_directory=build_root)
    descriptor_sha = _sha_bytes(descriptor_bytes)
    descriptor_path = build_root / f"{descriptor_sha}.particle_descriptor.json"
    _write_create_or_exact(
        descriptor_path, descriptor_bytes, code="PX051_BUILD_COLLISION")
    specialization = _specialization_binding(
        protocol_bundle=protocol_bundle, descriptor=descriptor)
    artifact = {
        "schema": _ARTIFACT_SCHEMA,
        "format_version": 1,
        "native_library_sha256": native_sha,
        "source_sha256": source_sha,
        "source_base64": base64.b64encode(source).decode("ascii"),
        "descriptor_sha256": descriptor_sha,
        "descriptor_base64": base64.b64encode(descriptor_bytes).decode("ascii"),
        "template_semantic_sha256": descriptor["semantic_sha256"],
        "ptx_sha256": _sha_bytes(ptx),
        "ptx_base64": base64.b64encode(ptx).decode("ascii"),
        "standard_protocol": protocol_bundle,
        "specialization_binding": specialization,
        "build_identity": build_identity,
    }
    artifact_bytes = _canonical(artifact) + b"\n"
    artifact_sha = _sha_bytes(artifact_bytes)
    artifact_path = (
        Path(artifact_directory).expanduser().resolve()
        / f"{artifact_sha}.rtdlexe")
    _write_create_or_exact(
        artifact_path, artifact_bytes, code="PX054_ARTIFACT_COLLISION")
    return BuiltParticleRTDLExecutable(
        artifact_path=artifact_path, artifact_sha256=artifact_sha,
        artifact_bytes=len(artifact_bytes), source_path=source_path,
        descriptor_path=descriptor_path, ptx_pass1_path=pass1,
        ptx_pass2_path=pass2, ptx_sha256=_sha_bytes(ptx),
        native_library_sha256=native_sha,
        protocol_decision_sha256=str(
            protocol_bundle["decision"]["decision_sha256"]),
        template_semantic_sha256=str(descriptor["semantic_sha256"]),
        nvcc_absolute_path=nvcc,
        optix_include_absolute_path=include,
        nvcc_executable_sha256=str(build_identity["nvcc_executable_sha256"]),
        optix_device_header_sha256=str(
            build_identity["optix_device_header_sha256"]),
    )


def _decode_bound_bytes(
    artifact: Mapping[str, object], *, data_key: str, sha_key: str,
) -> bytes:
    encoded = artifact.get(data_key)
    if not isinstance(encoded, str):
        _fail("PX003_SCHEMA_INVALID", f"artifact.{data_key}", type(encoded).__name__)
    try:
        raw = base64.b64decode(encoded, validate=True)
    except ValueError as exc:
        _fail("PX003_SCHEMA_INVALID", f"artifact.{data_key}", exc)
    expected = _require_sha(artifact.get(sha_key), f"artifact.{sha_key}")
    if _sha_bytes(raw) != expected:
        _fail("PX005_ARTIFACT_MEMBER_MISMATCH", f"artifact.{data_key}", expected)
    return raw


def _require_embedded_text(raw: bytes, path: str) -> bytes:
    """Admit one exact C/PTX text payload, never a prefix plus tail bytes."""

    if not raw or b"\0" in raw or not raw.endswith(b"\n") or b"\r" in raw:
        _fail("PX008_EMBEDDED_TEXT_INVALID", path, {
            "bytes": len(raw), "contains_nul": b"\0" in raw,
            "terminal_lf": raw.endswith(b"\n"), "contains_cr": b"\r" in raw,
        })
    return raw


def _verify_protocol_bundle(value: object) -> Mapping[str, object]:
    bundle = _require_exact_keys(value, {
        "schema", "producer", "callback_ir_sha256", "callback_effect_digest",
        "physical_schema_sha256", "canonical_plan_sha256", "callback_abi_sha256",
        "orientation_authority_sha256", "generic_checked_executable_sha256",
        "generic_composed_ptx_sha256", "contract", "projection", "decision",
    }, "artifact.standard_protocol")
    if (bundle["schema"] != "rtdl.v4.particle_standard_protocol_bundle.v1"
            or bundle["producer"] != "compile_standard_builtin_triangle_program"):
        _fail("PX006_PROTOCOL_BINDING_INVALID", "artifact.standard_protocol", bundle)
    for name in (
        "callback_ir_sha256", "callback_effect_digest", "physical_schema_sha256",
        "canonical_plan_sha256", "callback_abi_sha256",
        "generic_checked_executable_sha256", "generic_composed_ptx_sha256",
    ):
        _require_sha(bundle[name], f"artifact.standard_protocol.{name}")
    _require_sha(
        bundle["orientation_authority_sha256"],
        "artifact.standard_protocol.orientation_authority_sha256")
    contract = bundle["contract"]
    projection = bundle["projection"]
    decision = bundle["decision"]
    if not isinstance(contract, Mapping) or not isinstance(projection, Mapping) \
            or not isinstance(decision, Mapping):
        _fail("PX006_PROTOCOL_BINDING_INVALID", "artifact.standard_protocol.chain", "mapping required")
    contract_body = dict(contract)
    contract_seal = contract_body.pop("contract_sha256", None)
    projection_body = dict(projection)
    projection_seal = projection_body.pop("projection_sha256", None)
    decision_body = dict(decision)
    decision_seal = decision_body.pop("decision_sha256", None)
    if (_require_sha(contract_seal, "contract.contract_sha256") != _digest(contract_body)
            or _require_sha(projection_seal, "projection.projection_sha256") != _digest(projection_body)
            or _require_sha(decision_seal, "decision.decision_sha256") != _digest(decision_body)):
        _fail("PX006_PROTOCOL_BINDING_INVALID", "artifact.standard_protocol.seal", "mismatch")
    if (decision.get("verdict") != "ACCEPT" or decision.get("findings") != []
            or decision.get("contract_sha256") != contract_seal
            or decision.get("projection_sha256") != projection_seal):
        _fail("PX006_PROTOCOL_BINDING_INVALID", "artifact.standard_protocol.decision", decision)
    # Lightweight runtime re-verification: this module has no compiler/Numba/
    # NVRTC dependency, but does not merely trust an artifact saying ACCEPT.
    from .v4_protocol_contract import (  # pylint: disable=import-outside-toplevel
        CompilerProtocolProjection,
        ProtocolContractDeclaration,
        verify_protocol_contract,
    )
    try:
        rechecked = verify_protocol_contract(
            ProtocolContractDeclaration.from_mapping(contract),
            CompilerProtocolProjection.from_mapping(projection),
        ).to_mapping()
    except (TypeError, ValueError) as exc:
        _fail("PX006_PROTOCOL_BINDING_INVALID", "artifact.standard_protocol.recheck", exc)
    if _canonical(rechecked) != _canonical(decision):
        _fail("PX006_PROTOCOL_BINDING_INVALID", "artifact.standard_protocol.recheck", "decision drift")
    return bundle


def _verify_specialization(
    value: object, *, protocol: Mapping[str, object],
    descriptor: Mapping[str, object], source_sha: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail("PX007_SPECIALIZATION_BINDING_INVALID", "artifact.specialization", type(value).__name__)
    body = dict(value)
    seal = body.pop("binding_sha256", None)
    if _require_sha(seal, "specialization.binding_sha256") != _digest(body):
        _fail("PX007_SPECIALIZATION_BINDING_INVALID", "artifact.specialization.binding_sha256", seal)
    expected = _specialization_binding(
        protocol_bundle=protocol, descriptor=descriptor)
    if _canonical(value) != _canonical(expected):
        _fail("PX007_SPECIALIZATION_BINDING_INVALID", "artifact.specialization", "projection drift")
    if descriptor["source_sha256"] != source_sha:
        _fail("PX007_SPECIALIZATION_BINDING_INVALID", "artifact.specialization.source", source_sha)
    return value


class LoadedParticleRTDLExecutable:
    """Verified load capability; construction is only through the public loader."""

    def __init__(
        self, *, artifact_path: Path, artifact_sha256: str,
        native_image: _VerifiedNativeImage, api: _ParticleNativeApi,
        ptx: bytes, ptx_sha256: str, descriptor: Mapping[str, object],
    ) -> None:
        self.artifact_path = artifact_path
        self.artifact_sha256 = artifact_sha256
        self.ptx_sha256 = ptx_sha256
        self.descriptor = dict(descriptor)
        self._ptx = ptx
        self._native_image = native_image
        self._api = api
        self._pid = os.getpid()
        self._lock = threading.Lock()
        self._active_owners = 0
        self._closed = False

    @property
    def ptx_bytes(self) -> bytes:
        """Exact artifact PTX consumed by both matched arms."""
        if self._closed:
            _fail("PX060_CLOSED", "loaded.ptx_bytes", "closed")
        return self._ptx

    def prepare(self, static_input: ParticleStaticInput) -> "PreparedParticleRTDLExecutable":
        if type(static_input) is not ParticleStaticInput:
            _fail("PX020_STATIC_INPUT_INVALID", "static_input", type(static_input).__name__)
        with self._lock:
            if self._closed or os.getpid() != self._pid:
                _fail("PX060_CLOSED", "loaded.prepare", "closed or process drift")
            token = ctypes.c_uint64()
            error = ctypes.create_string_buffer(16_384)
            ptx = ctypes.create_string_buffer(self._ptx + b"\0")
            result = int(self._api.prepare(
                ctypes.cast(ptx, ctypes.c_char_p),
                _array_pointer(static_input.vertices_f32, ctypes.c_float),
                static_input.vertices_f32.shape[0],
                _array_pointer(static_input.triangles_u32, ctypes.c_uint32),
                static_input.triangles_u32.shape[0],
                _array_pointer(static_input.front_values_u32, ctypes.c_uint32),
                _array_pointer(static_input.back_values_u32, ctypes.c_uint32),
                ctypes.byref(token), error, len(error),
            ))
            _raise_native(result, error, "native.prepare")
            if token.value == 0:
                _fail("PX032_NATIVE_CALL_FAILED", "native.prepare", "zero token")
            self._active_owners += 1
        return PreparedParticleRTDLExecutable(loaded=self, token=token.value)

    def _owner_closed(self) -> None:
        with self._lock:
            if self._active_owners <= 0:
                _fail("PX061_LIFECYCLE_STATE_INVALID", "loaded.owners", self._active_owners)
            self._active_owners -= 1

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            if self._active_owners:
                _fail("PX061_LIFECYCLE_STATE_INVALID", "loaded.close", "prepared owner active")
            self._closed = True
            self._native_image.close()

    def __enter__(self) -> "LoadedParticleRTDLExecutable":
        if self._closed:
            _fail("PX060_CLOSED", "loaded", "closed")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


class PreparedParticleRTDLExecutable:
    """Reusable owner; execute accepts seven borrowed contiguous SoA columns."""

    def __init__(self, *, loaded: LoadedParticleRTDLExecutable, token: int) -> None:
        self._loaded = loaded
        self._token = token
        self._closed = False
        self._pid = os.getpid()
        self._lock = threading.Lock()
        self._execution_generation = 0

    @property
    def closed(self) -> bool:
        return self._closed

    def execute(
        self, query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
        query_tmax,
    ) -> ParticleExecutionResult:
        np = _numpy()
        columns = self._validate_query_columns(np, (
            query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
            query_tmax,
        ))
        if not self._lock.acquire(blocking=False):
            _fail("PX061_LIFECYCLE_STATE_INVALID", "prepared.execute", "reentrant")
        try:
            return self._execute_locked(np, columns)
        finally:
            self._lock.release()

    @staticmethod
    def _validate_query_columns(
        np, raw_columns, *, require_exact_base: bool = False,
    ) -> tuple[object, ...]:
        columns = tuple(
            _require_numpy_array(
                np, column, f"query[{index}]", "<f4", 1,
                require_exact_base=require_exact_base)
            for index, column in enumerate(raw_columns)
        )
        if any(column.shape != (_QUERY_COUNT,) for column in columns):
            _fail("PX022_QUERY_SHAPE_INVALID", "query", [item.shape for item in columns])
        return columns

    def _execute_locked(self, np, columns) -> ParticleExecutionResult:
        raw = self._execute_native_raw_locked(np, columns)
        return self._materialize_native_result_locked(*raw)

    def _execute_native_raw_locked(
        self, np, columns, *, values_prevalidated: bool = False,
    ) -> tuple[object, _ParticleControl, _ParticleFastReceipt,
               object, int, object]:
        if self._closed or os.getpid() != self._pid:
            _fail("PX060_CLOSED", "prepared.execute", "closed or process drift")
        # Native writes three contiguous page-locked SoA columns.  The public
        # result borrows those exact bytes; it allocates neither a 60-KB
        # destination nor an AoS packing copy.  Its lifetime ends at the next
        # execute on this owner or at close.
        borrowed_columns = ctypes.POINTER(ctypes.c_uint32)()
        borrowed_rows = ctypes.c_size_t()
        control = _ParticleControl()
        receipt = _ParticleFastReceipt()
        error = ctypes.create_string_buffer(16_384)
        native_execute = self._loaded._api.execute_prevalidated \
            if values_prevalidated else self._loaded._api.execute
        native_result = int(native_execute(
            self._token,
            *(_array_pointer(item, ctypes.c_float) for item in columns),
            _QUERY_COUNT,
            ctypes.byref(borrowed_columns), ctypes.byref(borrowed_rows),
            ctypes.byref(control), ctypes.byref(receipt), error, len(error),
        ))
        self._execution_generation += 1
        _raise_native(native_result, error, "native.execute")
        output_rows = int(borrowed_rows.value)
        control_failed = (
            control.validated_row_count != _QUERY_COUNT
            or control.first_error != _U32_MAX
            or control.error_code != 0
            or control.status != 0
        )
        # Failure evidence and unsafe native pointer/row states are validated
        # immediately.  The successful formal route defers full receipt
        # mapping and identity materialization until after its end clock.
        if control_failed or not bool(borrowed_columns) \
                or output_rows != _QUERY_COUNT:
            _validate_receipt(
                control, receipt, output_pointer=borrowed_columns,
                output_rows=output_rows)
        packed_type = ctypes.c_uint32 * (_QUERY_COUNT * 3)
        packed = ctypes.cast(
            borrowed_columns, ctypes.POINTER(packed_type)).contents
        output_soa = np.ctypeslib.as_array(packed).reshape(3, _QUERY_COUNT)
        output = output_soa.T
        output.setflags(write=False)
        return output, control, receipt, borrowed_columns, output_rows, packed

    def _execute_native_core_locked(
        self, np, columns, *, values_prevalidated: bool = False,
    ) -> ParticleExactCoreCompletion:
        output, control, receipt, borrowed_columns, output_rows, packed = \
            self._execute_native_raw_locked(
                np, columns, values_prevalidated=values_prevalidated)
        return _new_particle_core_completion(
            output_u32x3=output, control=control, receipt=receipt,
            output_pointer=borrowed_columns, output_rows=output_rows,
            owner=self, generation=self._execution_generation, packed=packed,
        )

    def _materialize_native_result_locked(
        self, output, control: _ParticleControl,
        receipt: _ParticleFastReceipt, output_pointer,
        output_rows: int, packed,
    ) -> ParticleExecutionResult:
        # ``packed`` keeps the native borrowed storage alive through result
        # construction.  The public ndarray also owns that ctypes base.
        del packed
        receipt_map = _validate_receipt(
            control, receipt, output_pointer=output_pointer,
            output_rows=output_rows)
        return ParticleExecutionResult(
            output_u32x3=output,
            control=(
                int(control.validated_row_count), int(control.first_error),
                int(control.error_code), int(control.status)),
            receipt=receipt_map,
            artifact_sha256=self._loaded.artifact_sha256,
            ptx_sha256=self._loaded.ptx_sha256,
        )

    def prevalidate_exact_core_input(
        self, query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
        query_tmax, *, expected_u32x3,
    ) -> PrevalidatedParticleRTDLExecutionInput:
        """Seal immutable input bytes outside the formal execute clock."""

        if self._closed or os.getpid() != self._pid:
            _fail(
                "PX060_CLOSED", "prepared.prevalidate_exact_core_input",
                "closed or process drift")
        return prevalidate_particle_rtdlexe_exact_core_input(
            query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
            query_tmax, expected_u32x3=expected_u32x3)

    def _materialize_exact_core_locked(
        self, completion: ParticleExactCoreCompletion,
    ) -> ParticleExecutionResult:
        registered = _PARTICLE_CORE_COMPLETIONS.get(completion) \
            if type(completion) is ParticleExactCoreCompletion else None
        if (type(completion) is not ParticleExactCoreCompletion
                or registered is None
                or registered[0] is not completion._output_u32x3
                or registered[1] is not completion._control
                or registered[2] is not completion._receipt
                or registered[3] is not completion._output_pointer
                or registered[4] != completion._output_rows
                or registered[5] is not completion._owner
                or registered[6] != completion._generation
                or registered[7] is not completion._packed
                or registered[8] != bytes(completion._control)
                or registered[9] != bytes(completion._receipt)
                or completion._owner is not self
                or completion._generation != self._execution_generation
                or self._closed or os.getpid() != self._pid):
            _fail(
                "PX061_LIFECYCLE_STATE_INVALID", "execute.core_completion",
                "stale, foreign, forged, closed, or process drift")
        return self._materialize_native_result_locked(
            completion._output_u32x3, completion._control,
            completion._receipt, completion._output_pointer,
            completion._output_rows, completion._packed)

    def execute_exact_core(
        self, query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
        query_tmax, *, expected_u32x3,
    ) -> ParticleExactCoreCompletion:
        """Measured public core; success returns immediately after its oracle."""

        np = _numpy()
        expected = _require_numpy_array(
            np, expected_u32x3, "expected_u32x3", "<u4", 2, 3,
            require_c_contiguous=False, require_exact_base=True)
        if expected.shape != (_QUERY_COUNT, 3):
            _fail("PX023_ORACLE_SHAPE_INVALID", "expected_u32x3", expected.shape)
        columns = self._validate_query_columns(np, (
            query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
            query_tmax,
        ), require_exact_base=True)
        if not self._lock.acquire(blocking=False):
            _fail(
                "PX061_LIFECYCLE_STATE_INVALID", "prepared.execute_exact_core",
                "reentrant")
        try:
            completion = self._execute_native_core_locked(np, columns)
            if np.shares_memory(completion._output_u32x3, expected):
                _fail(
                    "PX073_ORACLE_ALIASES_OUTPUT", "execute_exact_core.expected",
                    "borrowed output alias")
            if not np.array_equal(completion._output_u32x3, expected):
                _fail(
                    "PX072_EXACT_ORACLE_MISMATCH", "execute_exact_core.output",
                    "np.array_equal false")
            return completion
        finally:
            self._lock.release()

    def execute_exact_core_prevalidated(
        self, value: PrevalidatedParticleRTDLExecutionInput,
    ) -> ParticleExactCoreCompletion:
        """Measured core using the sealed v3 no-rescan native route."""

        np = _numpy()
        if not self._lock.acquire(blocking=False):
            _fail(
                "PX061_LIFECYCLE_STATE_INVALID",
                "prepared.execute_exact_core_prevalidated", "reentrant")
        try:
            columns, expected = _require_prevalidated_particle_rtdlexe_input(
                np, value)
            completion = self._execute_native_core_locked(
                np, columns, values_prevalidated=True)
            if np.shares_memory(completion._output_u32x3, expected):
                _fail(
                    "PX073_ORACLE_ALIASES_OUTPUT",
                    "execute_exact_core_prevalidated.expected",
                    "borrowed output alias")
            if not np.array_equal(completion._output_u32x3, expected):
                _fail(
                    "PX072_EXACT_ORACLE_MISMATCH",
                    "execute_exact_core_prevalidated.output",
                    "np.array_equal false")
            return completion
        finally:
            self._lock.release()

    def materialize_exact_core_completion(
        self, completion: ParticleExactCoreCompletion,
    ) -> ParticleExecutionResult:
        """Validate/map native evidence after the caller records its end clock."""

        if not self._lock.acquire(blocking=False):
            _fail(
                "PX061_LIFECYCLE_STATE_INVALID", "prepared.materialize_core",
                "reentrant")
        try:
            return self._materialize_exact_core_locked(completion)
        finally:
            self._lock.release()

    def execute_complete_prevalidated(
        self, value: PrevalidatedParticleRTDLExecutionInput,
    ) -> ParticleExecutionResult:
        """Return one full public result from a sealed immutable input token.

        This is the reusable steady public path.  It retains token provenance,
        the native status/receipt gate, the exact oracle, and borrowed-output
        lifetime checks while avoiding the two-phase completion registry used
        only when callers explicitly split exact-core timing from result
        materialization.
        """

        np = _numpy()
        if not self._lock.acquire(blocking=False):
            _fail(
                "PX061_LIFECYCLE_STATE_INVALID",
                "prepared.execute_complete_prevalidated", "reentrant")
        try:
            columns, expected = _require_prevalidated_particle_rtdlexe_input(
                np, value)
            raw = self._execute_native_raw_locked(
                np, columns, values_prevalidated=True)
            result = self._materialize_native_result_locked(*raw)
            if np.shares_memory(result.output_u32x3, expected):
                _fail(
                    "PX073_ORACLE_ALIASES_OUTPUT",
                    "execute_complete_prevalidated.expected",
                    "borrowed output alias")
            if not np.array_equal(result.output_u32x3, expected):
                _fail(
                    "PX072_EXACT_ORACLE_MISMATCH",
                    "execute_complete_prevalidated.output",
                    "np.array_equal false")
            return result
        finally:
            self._lock.release()

    def execute_complete(
        self, query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
        query_tmax, *, expected_u32x3,
    ) -> ParticleExecutionResult:
        """Formal façade: execute and exact borrowed-view oracle in one call."""

        np = _numpy()
        expected = _require_numpy_array(
            np, expected_u32x3, "expected_u32x3", "<u4", 2, 3,
            require_c_contiguous=False, require_exact_base=True)
        if expected.shape != (_QUERY_COUNT, 3):
            _fail("PX023_ORACLE_SHAPE_INVALID", "expected_u32x3", expected.shape)
        columns = self._validate_query_columns(np, (
            query_ox, query_oy, query_oz, query_dx, query_dy, query_dz,
            query_tmax,
        ), require_exact_base=True)
        if not self._lock.acquire(blocking=False):
            _fail("PX061_LIFECYCLE_STATE_INVALID", "prepared.execute_complete", "reentrant")
        try:
            result = self._execute_locked(np, columns)
            # The expected oracle must be independent storage.  Otherwise a
            # previous borrowed result is overwritten by this execute and an
            # apparent exact comparison degenerates into self-comparison.
            if np.shares_memory(result.output_u32x3, expected):
                _fail("PX073_ORACLE_ALIASES_OUTPUT", "execute_complete.expected", "borrowed output alias")
            # The owner lock remains held across this exact comparison, so no
            # concurrent execute can overwrite the borrowed pinned bytes.
            if not np.array_equal(result.output_u32x3, expected):
                _fail("PX072_EXACT_ORACLE_MISMATCH", "execute_complete.output", "np.array_equal false")
            return result
        finally:
            self._lock.release()

    def close(self) -> None:
        if self._closed:
            return
        if not self._lock.acquire(blocking=False):
            _fail("PX061_LIFECYCLE_STATE_INVALID", "prepared.close", "active execute")
        try:
            if self._closed:
                return
            if os.getpid() != self._pid:
                _fail("PX061_LIFECYCLE_STATE_INVALID", "prepared.close", "process drift")
            cell = ctypes.c_uint64(self._token)
            error = ctypes.create_string_buffer(16_384)
            _raise_native(int(self._loaded._api.destroy(
                ctypes.byref(cell), error, len(error))), error, "native.destroy")
            if cell.value != 0:
                _fail("PX032_NATIVE_CALL_FAILED", "native.destroy", "token not cleared")
            self._token = 0
            self._closed = True
            self._loaded._owner_closed()
        finally:
            self._lock.release()

    def __enter__(self) -> "PreparedParticleRTDLExecutable":
        if self._closed:
            _fail("PX060_CLOSED", "prepared", "closed")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def _validate_receipt(
    control: _ParticleControl, receipt: _ParticleFastReceipt, *,
    output_pointer, output_rows: int,
) -> Mapping[str, int]:
    failed = (
        control.validated_row_count != _QUERY_COUNT
        or control.first_error != _U32_MAX
        or control.error_code != 0
        or control.status != 0
    )
    # The success receipt is a completely fixed ABI value.  Compare its exact
    # 96 bytes and return one immutable shared mapping instead of rebuilding a
    # 17-entry Python dict on every execution.  Failure remains the slower,
    # fully materialized diagnostic path below.
    if not failed:
        if bytes(receipt) != _SUCCESS_RECEIPT_BYTES \
                or not bool(output_pointer) or output_rows != _QUERY_COUNT:
            result = {
                name: int(getattr(receipt, name))
                for name, _ctype in _ParticleFastReceipt._fields_
            }
            _fail("PX070_RECEIPT_INVALID", "execute.receipt.success", result)
        return _SUCCESS_RECEIPT_VALUES

    result = {
        name: int(getattr(receipt, name))
        for name, _ctype in _ParticleFastReceipt._fields_
    }
    common = {
        key: value for key, value in _SUCCESS_RECEIPT_VALUES.items()
        if key not in {
            "output_d2h_copy_call_count", "output_d2h_bytes",
            "host_blocking_boundary_count",
        }
    }
    if any(result[key] != value for key, value in common.items()):
        _fail("PX070_RECEIPT_INVALID", "execute.receipt.common", result)
    if failed:
        if (result["output_d2h_copy_call_count"] != 0
                or result["output_d2h_bytes"] != 0
                or result["host_blocking_boundary_count"] != 1
                or bool(output_pointer) or output_rows != 0):
            _fail("PX070_RECEIPT_INVALID", "execute.receipt.failure", result)
        raise ParticleDeviceStatusError(control={
            "validated_row_count": int(control.validated_row_count),
            "first_error": int(control.first_error),
            "error_code": int(control.error_code),
            "status": int(control.status),
        }, receipt=result)
    raise AssertionError("unreachable Particle receipt branch")


def load_particle_rtdlexe(
    artifact_path: str | os.PathLike[str],
    *,
    deployment: InstalledParticleRTDLDeployment,
    native_library_path: str | os.PathLike[str],
) -> LoadedParticleRTDLExecutable:
    """Verify a cache-hit artifact and bind its exact native product image."""

    deployment = _require_installed_deployment(deployment)
    expected = deployment.expected_artifact_sha256
    path = Path(artifact_path).expanduser().resolve(strict=True)
    raw = _read_regular_bytes(path, code="PX004_ARTIFACT_NONCANONICAL")
    observed = _sha_bytes(raw)
    if observed != expected or path.name != f"{expected}.rtdlexe":
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "artifact", {
            "expected": expected, "observed": observed, "name": path.name,
        })
    artifact = _require_exact_keys(_parse_canonical_artifact(raw), {
        "schema", "format_version", "native_library_sha256", "source_sha256",
        "source_base64", "descriptor_sha256", "descriptor_base64",
        "template_semantic_sha256", "ptx_sha256", "ptx_base64",
        "standard_protocol", "specialization_binding", "build_identity",
    }, "artifact")
    if artifact["schema"] != _ARTIFACT_SCHEMA or artifact["format_version"] != 1:
        _fail("PX003_SCHEMA_INVALID", "artifact.identity", artifact)
    source = _require_embedded_text(_decode_bound_bytes(
        artifact, data_key="source_base64", sha_key="source_sha256"),
        "artifact.source")
    descriptor_bytes = _decode_bound_bytes(
        artifact, data_key="descriptor_base64", sha_key="descriptor_sha256")
    ptx = _require_exact_ptx_entry_set(_require_embedded_text(_decode_bound_bytes(
        artifact, data_key="ptx_base64", sha_key="ptx_sha256"),
        "artifact.ptx"), "artifact.ptx.entries")
    descriptor = _validate_native_descriptor(descriptor_bytes)
    if artifact["template_semantic_sha256"] != descriptor["semantic_sha256"]:
        _fail("PX005_ARTIFACT_MEMBER_MISMATCH", "artifact.template_semantic_sha256", "drift")
    protocol = _verify_protocol_bundle(artifact["standard_protocol"])
    decision_sha = protocol["decision"]["decision_sha256"]
    if decision_sha != deployment.expected_protocol_decision_sha256:
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "protocol_decision", {
            "expected": deployment.expected_protocol_decision_sha256,
            "observed": decision_sha,
        })
    _verify_specialization(
        artifact["specialization_binding"], protocol=protocol,
        descriptor=descriptor, source_sha=_sha_bytes(source))
    build = _require_exact_keys(artifact["build_identity"], {
        "schema", "nvcc_executable_sha256",
        "nvcc_version_stdout_base64", "nvcc_version_stderr_base64",
        "optix_device_header_sha256", "source_sha256",
        "compiler_arguments_path_independent",
        "independent_invocation_count", "ptx_byte_identical",
        "ptx_sha256", "ptx_bytes",
    }, "artifact.build_identity")
    arguments = build.get("compiler_arguments_path_independent")
    if (build.get("schema") != _BUILD_SCHEMA
            or build.get("ptx_byte_identical") is not True
            or build.get("independent_invocation_count") != 2
            or build.get("source_sha256") != artifact["source_sha256"]
            or build.get("ptx_sha256") != artifact["ptx_sha256"]
            or build.get("ptx_bytes") != len(ptx)
            or not isinstance(arguments, list)
            or not arguments
            or any(not isinstance(item, str) or not item for item in arguments)
            or any(item.startswith(("/", "\\\\"))
                   or re.match(r"^[A-Za-z]:[\\/]", item)
                   for item in arguments)):
        _fail("PX009_BUILD_IDENTITY_INVALID", "artifact.build_identity", build)
    _require_sha(
        build.get("nvcc_executable_sha256"),
        "artifact.build_identity.nvcc_executable_sha256")
    _require_sha(
        build.get("optix_device_header_sha256"),
        "artifact.build_identity.optix_device_header_sha256")
    native_sha = _require_sha(
        artifact["native_library_sha256"], "artifact.native_library_sha256")
    if (native_sha != deployment.expected_native_sha256
            or artifact["template_semantic_sha256"]
                != deployment.expected_template_semantic_sha256):
        _fail("PX010_DEPLOYMENT_AUTHORITY_MISMATCH", "deployment.identities", {
            "native": native_sha,
            "semantic": artifact["template_semantic_sha256"],
        })
    image = _open_verified_native(
        native_library_path, expected_sha256=native_sha)
    try:
        api = _ParticleNativeApi(image.library)
        if api.query_source() != source:
            _fail("PX035_SOURCE_DESCRIPTOR_MISMATCH", "load.native_source", "artifact drift")
        if api.query_descriptor() != descriptor_bytes:
            _fail("PX035_SOURCE_DESCRIPTOR_MISMATCH", "load.native_descriptor", "artifact drift")
        return LoadedParticleRTDLExecutable(
            artifact_path=path, artifact_sha256=expected,
            native_image=image, api=api, ptx=ptx,
            ptx_sha256=str(artifact["ptx_sha256"]), descriptor=descriptor)
    except BaseException:
        image.close()
        raise


__all__ = [
    "BuiltParticleRTDLExecutable",
    "InstalledParticleRTDLDeployment",
    "LoadedParticleRTDLExecutable",
    "PrevalidatedParticleRTDLExecutionInput",
    "ParticleExactCoreCompletion",
    "ParticleExecutionResult",
    "ParticleDeviceStatusError",
    "ParticleRTDLExecutableError",
    "ParticleStaticInput",
    "PreparedParticleRTDLExecutable",
    "build_particle_rtdlexe",
    "install_particle_rtdlexe_deployment",
    "load_particle_rtdlexe",
    "prevalidate_particle_rtdlexe_exact_core_input",
]
