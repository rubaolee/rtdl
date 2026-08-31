"""Bounded Goal5814 owner adapter for the product-only Particle native ABI.

This module deliberately is not the public ``rtdlexe`` integration.  It binds
one frozen 5,000-query scientific application to the five new product-native
entry points, checks the exported source/descriptor and prebuilt PTX identity,
and keeps exact-output comparison inside the complete execute boundary.

There are no timers or performance claims here.  The adapter imports neither
RTDL's compiler/runtime Python modules nor PyOptiX.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import json
import re
import threading
from typing import Any, Mapping

import numpy as np


QUERY_COUNT = 5_000
VERTEX_COUNT = 314_587
TRIANGLE_COUNT = 3_392_530
UINT32_MAX = (1 << 32) - 1

EXPECTED_SOURCE_SHA256 = (
    "9484a5a4e600885d335cff16130e9cbbc0d1c5d8ed6d24297e2ecb202e0c6e67"
)
EXPECTED_SEMANTIC_SHA256 = (
    "4378dddd0e3089517d16a295c00d7172e0327f52e8715424d6c834da53076fbb"
)

SOURCE_SYMBOL = "rtdl_optix_v4_particle_strict_interior_source_v1"
DESCRIPTOR_SYMBOL = "rtdl_optix_v4_particle_strict_interior_descriptor_v1"
PREPARE_SYMBOL = "rtdl_optix_v4_prepare_particle_strict_interior_v1"
EXECUTE_SYMBOL = (
    "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2"
)
DESTROY_SYMBOL = (
    "rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1"
)
PRODUCT_SYMBOLS = (
    SOURCE_SYMBOL,
    DESCRIPTOR_SYMBOL,
    PREPARE_SYMBOL,
    EXECUTE_SYMBOL,
    DESTROY_SYMBOL,
)

ENTRY_POINTS = (
    "__raygen__rtdl_particle_strict_interior",
    "__closesthit__rtdl_particle_strict_interior",
    "__miss__rtdl_particle_strict_interior",
)


class ParticleProductError(RuntimeError):
    """Base class for bounded product-owner failures."""


class ParticleInputError(ParticleProductError):
    """An array or prebuilt-PTX input is outside the frozen contract."""


class ParticleAuthorityError(ParticleProductError):
    """The exported source/descriptor or PTX identity does not match."""


class ParticleNativeError(ParticleProductError):
    """A product-native ABI call failed."""


class ParticleReceiptError(ParticleProductError):
    """Native control/receipt bytes do not prove the required boundary."""


class ParticleDeviceStatusError(ParticleProductError):
    """The device rejected at least one frozen-domain query."""

    def __init__(self, control: Mapping[str, int], receipt: Mapping[str, int]):
        self.control = dict(control)
        self.receipt = dict(receipt)
        super().__init__(
            "Particle device status failed closed: "
            f"validated_row_count={control['validated_row_count']}, "
            f"first_error={control['first_error']}, "
            f"error_code={control['error_code']}, status={control['status']}"
        )


class ParticleOracleMismatch(ParticleProductError):
    """The exact 5,000-row product output differs from the supplied oracle."""


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


if ctypes.sizeof(_ParticleControl) != 16:
    raise RuntimeError("Particle control ctypes layout is not 16 bytes")
if ctypes.sizeof(_ParticleFastReceipt) != 96:
    raise RuntimeError("Particle receipt ctypes layout is not 96 bytes")


_FLOAT_PTR = ctypes.POINTER(ctypes.c_float)
_U32_PTR = ctypes.POINTER(ctypes.c_uint32)
_CHAR_PTR = ctypes.POINTER(ctypes.c_char)


@dataclass(frozen=True)
class ParticlePrebuiltPTX:
    """Prebuilt PTX plus the exact authorities under which it was compiled."""

    ptx: bytes
    source_sha256: str
    descriptor_sha256: str
    semantic_sha256: str
    ptx_sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.ptx, bytes) or not self.ptx:
            raise ParticleInputError("prebuilt PTX must be nonempty bytes")
        if b"\x00" in self.ptx:
            raise ParticleInputError("prebuilt PTX must not contain NUL bytes")
        for label, value in (
            ("source_sha256", self.source_sha256),
            ("descriptor_sha256", self.descriptor_sha256),
            ("semantic_sha256", self.semantic_sha256),
            ("ptx_sha256", self.ptx_sha256),
        ):
            _require_sha256(label, value)


@dataclass(frozen=True)
class ParticleStaticInput:
    """Exact frozen mesh and primitive-owner arrays consumed at prepare."""

    vertices: np.ndarray
    triangles: np.ndarray
    front_values: np.ndarray
    back_values: np.ndarray

    def __post_init__(self) -> None:
        _require_array(
            "vertices", self.vertices, np.float32, (VERTEX_COUNT, 3)
        )
        _require_array(
            "triangles", self.triangles, np.uint32, (TRIANGLE_COUNT, 3)
        )
        _require_array(
            "front_values", self.front_values, np.uint32, (TRIANGLE_COUNT,)
        )
        _require_array(
            "back_values", self.back_values, np.uint32, (TRIANGLE_COUNT,)
        )


@dataclass(frozen=True)
class ParticleQueryColumns:
    """The seven exact contiguous SoA query columns used by formal execute."""

    ox: np.ndarray
    oy: np.ndarray
    oz: np.ndarray
    dx: np.ndarray
    dy: np.ndarray
    dz: np.ndarray
    tmax: np.ndarray

    def __post_init__(self) -> None:
        for label, value in (
            ("ox", self.ox),
            ("oy", self.oy),
            ("oz", self.oz),
            ("dx", self.dx),
            ("dy", self.dy),
            ("dz", self.dz),
            ("tmax", self.tmax),
        ):
            _require_array(label, value, np.float32, (QUERY_COUNT,))

    def native_order(self) -> tuple[np.ndarray, ...]:
        return (self.ox, self.oy, self.oz, self.dx, self.dy, self.dz, self.tmax)


@dataclass(frozen=True)
class ParticleAuthority:
    source: bytes
    source_sha256: str
    descriptor: bytes
    descriptor_sha256: str
    semantic_sha256: str
    ptx_sha256: str


def _require_sha256(label: str, value: Any) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ParticleInputError(f"{label} must be a lowercase SHA-256 hex string")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_array(
    label: str,
    value: Any,
    dtype: Any,
    shape: tuple[int, ...],
    *,
    require_c_contiguous: bool = True,
) -> np.ndarray:
    if not isinstance(value, np.ndarray):
        raise ParticleInputError(f"{label} must be a NumPy ndarray")
    if value.dtype != np.dtype(dtype):
        raise ParticleInputError(
            f"{label} dtype must be exactly {np.dtype(dtype)}, got {value.dtype}"
        )
    if value.shape != shape:
        raise ParticleInputError(
            f"{label} shape must be exactly {shape}, got {value.shape}"
        )
    if require_c_contiguous and not value.flags.c_contiguous:
        raise ParticleInputError(f"{label} must be C-contiguous")
    if not value.flags.aligned:
        raise ParticleInputError(f"{label} must be aligned")
    return value


def _native_error(error_buffer: ctypes.Array[ctypes.c_char]) -> str:
    return bytes(error_buffer.value).decode("utf-8", errors="replace")


def _checked_call(label: str, function: Any, *args: Any) -> None:
    error_buffer = ctypes.create_string_buffer(2_048)
    result = function(*args, error_buffer, ctypes.sizeof(error_buffer))
    if int(result) != 0:
        detail = _native_error(error_buffer) or "native call returned nonzero"
        raise ParticleNativeError(f"{label} failed: {detail}")


def _query_export(label: str, function: Any) -> bytes:
    byte_count = ctypes.c_size_t(0)
    _checked_call(label, function, None, 0, ctypes.byref(byte_count))
    if byte_count.value == 0:
        raise ParticleAuthorityError(f"{label} returned an empty authority")
    output = ctypes.create_string_buffer(byte_count.value + 1)
    second_count = ctypes.c_size_t(0)
    _checked_call(
        label,
        function,
        output,
        ctypes.sizeof(output),
        ctypes.byref(second_count),
    )
    if second_count.value != byte_count.value:
        raise ParticleAuthorityError(
            f"{label} changed size across its two-call query"
        )
    if output.raw[byte_count.value] != 0:
        raise ParticleAuthorityError(f"{label} omitted its terminal NUL")
    result = bytes(output.raw[: byte_count.value])
    if b"\x00" in result:
        raise ParticleAuthorityError(f"{label} contains an embedded NUL")
    return result


def _configure_native(library: Any) -> dict[str, Any]:
    try:
        functions = {name: getattr(library, name) for name in PRODUCT_SYMBOLS}
    except AttributeError as exc:
        raise ParticleNativeError(f"missing product-only Particle symbol: {exc}") from exc

    query_args = [
        _CHAR_PTR,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t),
        _CHAR_PTR,
        ctypes.c_size_t,
    ]
    functions[SOURCE_SYMBOL].argtypes = query_args
    functions[SOURCE_SYMBOL].restype = ctypes.c_int
    functions[DESCRIPTOR_SYMBOL].argtypes = query_args
    functions[DESCRIPTOR_SYMBOL].restype = ctypes.c_int

    functions[PREPARE_SYMBOL].argtypes = [
        ctypes.c_char_p,
        _FLOAT_PTR,
        ctypes.c_size_t,
        _U32_PTR,
        ctypes.c_size_t,
        _U32_PTR,
        _U32_PTR,
        ctypes.POINTER(ctypes.c_uint64),
        _CHAR_PTR,
        ctypes.c_size_t,
    ]
    functions[PREPARE_SYMBOL].restype = ctypes.c_int

    functions[EXECUTE_SYMBOL].argtypes = [
        ctypes.c_uint64,
        _FLOAT_PTR,
        _FLOAT_PTR,
        _FLOAT_PTR,
        _FLOAT_PTR,
        _FLOAT_PTR,
        _FLOAT_PTR,
        _FLOAT_PTR,
        ctypes.c_size_t,
        ctypes.POINTER(_U32_PTR),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(_ParticleControl),
        ctypes.POINTER(_ParticleFastReceipt),
        _CHAR_PTR,
        ctypes.c_size_t,
    ]
    functions[EXECUTE_SYMBOL].restype = ctypes.c_int

    functions[DESTROY_SYMBOL].argtypes = [
        ctypes.POINTER(ctypes.c_uint64),
        _CHAR_PTR,
        ctypes.c_size_t,
    ]
    functions[DESTROY_SYMBOL].restype = ctypes.c_int
    return functions


def _expected_descriptor(source: bytes) -> dict[str, Any]:
    return {
        "schema": "rtdl.v4.particle_strict_interior_template.v1",
        "family": "builtin_triangle_particle_strict_interior_v1",
        "native_abi": "rtdl.v4.prepared_particle_strict_interior.v2",
        "semantic_sha256": EXPECTED_SEMANTIC_SHA256,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": len(source),
        "entry_points": {
            "raygen": ENTRY_POINTS[0],
            "closest_hit": ENTRY_POINTS[1],
            "miss": ENTRY_POINTS[2],
            "intersection": None,
            "any_hit": None,
        },
        "compile_options": {
            "language": "cuda_cxx14",
            "target": "compute_<target_cc>",
            "requires_optix_device_header": True,
        },
        "pipeline_options": {
            "uses_motion_blur": False,
            "traversable_graph": "single_gas",
            "payload_values": 2,
            "attribute_values": 2,
            "exception_flags": 0,
            "launch_params_symbol": "params",
            "primitive_type": "triangle",
            "max_trace_depth": 1,
        },
        "launch_parameter_layout": {
            "bytes": 120,
            "query_layout": "seven_soa_f32",
            "static_metadata_layout": "front_u32_back_u32_by_primitive",
            "output_layout": "selected_neighbor_face_three_soa_u32",
        },
        "domain": {
            "query_count": QUERY_COUNT,
            "unique_closest_face_required": True,
            "strictly_positive_barycentric_coordinates_required": True,
            "edge_or_vertex_hit": "OUTSIDE_DOMAIN_FAIL_CLOSED",
            "full_50000_step_advection": False,
        },
        "transfer_contract": {
            "query_h2d_bytes": 140_000,
            "query_h2d_copy_call_count": 7,
            "optix_launch_count": 1,
            "control_d2h_bytes": 16,
            "control_before_output": True,
            "success_output_d2h_bytes": 60_000,
            "failure_output_d2h_bytes": 0,
            "execute_abi_version": 2,
            "success_host_output": "borrowed_native_owned_pinned_packed_soa_u32",
            "borrowed_output_lifetime": "until_next_execute_or_destroy",
            "failure_host_output": "null_pointer_zero_rows",
        },
        "boundary_owner_table": {
            "present": False,
            "bytes": 0,
            "avoided_generic_table_bytes_at_frozen_scale": 94_990_840,
        },
    }


def _verify_authority(
    source: bytes,
    descriptor_bytes: bytes,
    prebuilt: ParticlePrebuiltPTX,
) -> tuple[ParticleAuthority, dict[str, Any]]:
    source_sha256 = _sha256(source)
    descriptor_sha256 = _sha256(descriptor_bytes)
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        raise ParticleAuthorityError(
            "exported Particle source does not match the frozen source identity"
        )
    if prebuilt.source_sha256 != source_sha256:
        raise ParticleAuthorityError("prebuilt PTX source binding mismatch")
    if prebuilt.descriptor_sha256 != descriptor_sha256:
        raise ParticleAuthorityError("prebuilt PTX descriptor binding mismatch")
    if prebuilt.semantic_sha256 != EXPECTED_SEMANTIC_SHA256:
        raise ParticleAuthorityError("prebuilt PTX semantic binding mismatch")
    actual_ptx_sha256 = _sha256(prebuilt.ptx)
    if prebuilt.ptx_sha256 != actual_ptx_sha256:
        raise ParticleAuthorityError("prebuilt PTX byte identity mismatch")

    try:
        descriptor = json.loads(descriptor_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ParticleAuthorityError("exported Particle descriptor is not UTF-8 JSON") from exc
    if not isinstance(descriptor, dict) or descriptor != _expected_descriptor(source):
        raise ParticleAuthorityError(
            "exported Particle descriptor is not the exact frozen descriptor"
        )

    try:
        ptx_text = prebuilt.ptx.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ParticleAuthorityError("prebuilt PTX is not UTF-8 text") from exc
    # Anchor at a PTX directive line so a comment containing ``.entry`` cannot
    # manufacture a false binding.
    entry_pattern = re.compile(
        r"(?m)^[ \t]*(?:\.visible[ \t]+)?\.entry[ \t]+([^\s(]+)"
    )
    ptx_entries = entry_pattern.findall(ptx_text)
    if len(ptx_entries) != len(ENTRY_POINTS) or set(ptx_entries) != set(ENTRY_POINTS):
        raise ParticleAuthorityError(
            "prebuilt PTX does not contain exactly the three frozen entry points"
        )

    authority = ParticleAuthority(
        source=source,
        source_sha256=source_sha256,
        descriptor=descriptor_bytes,
        descriptor_sha256=descriptor_sha256,
        semantic_sha256=EXPECTED_SEMANTIC_SHA256,
        ptx_sha256=actual_ptx_sha256,
    )
    return authority, descriptor


def _structure_values(value: ctypes.Structure) -> dict[str, int]:
    return {name: int(getattr(value, name)) for name, _ in value._fields_}


_RECEIPT_COMMON = {
    "schema_version": 1,
    "optix_launch_count": 1,
    "query_count": QUERY_COUNT,
    "query_h2d_copy_call_count": 7,
    "control_reset_h2d_copy_call_count": 1,
    "parameter_h2d_copy_call_count": 1,
    "control_d2h_copy_call_count": 1,
    "status_before_output": 1,
    "query_h2d_bytes": 140_000,
    "control_reset_h2d_bytes": 16,
    "parameter_h2d_bytes": 120,
    "control_d2h_bytes": 16,
    "output_d2h_after_status_failure": 0,
    "boundary_owner_table_bytes": 0,
}


def _validate_control(control: Mapping[str, int]) -> bool:
    success = {
        "validated_row_count": QUERY_COUNT,
        "first_error": UINT32_MAX,
        "error_code": 0,
        "status": 0,
    }
    if dict(control) == success:
        return True
    valid_failure = (
        control["status"] == 1
        and 0 <= control["validated_row_count"] < QUERY_COUNT
        and 0 <= control["first_error"] < QUERY_COUNT
        and 1 <= control["error_code"] <= 5
    )
    if not valid_failure:
        raise ParticleReceiptError(
            f"Particle control is neither exact success nor a valid failure: {dict(control)}"
        )
    return False


def _validate_receipt(receipt: Mapping[str, int], success: bool) -> None:
    expected = dict(_RECEIPT_COMMON)
    if success:
        expected.update(
            output_d2h_copy_call_count=1,
            host_blocking_boundary_count=2,
            output_d2h_bytes=60_000,
        )
    else:
        expected.update(
            output_d2h_copy_call_count=0,
            host_blocking_boundary_count=1,
            output_d2h_bytes=0,
        )
    if dict(receipt) != expected:
        mismatches = {
            key: {"expected": expected[key], "actual": receipt.get(key)}
            for key in expected
            if receipt.get(key) != expected[key]
        }
        extra = sorted(set(receipt) - set(expected))
        raise ParticleReceiptError(
            f"Particle fast receipt mismatch: mismatches={mismatches}, extra={extra}"
        )


class ParticleProductOwner:
    """Prepared owner of the exact product-native Particle lifecycle."""

    def __init__(
        self,
        library: Any,
        functions: Mapping[str, Any],
        token: int,
        authority: ParticleAuthority,
        descriptor: Mapping[str, Any],
    ) -> None:
        self._library = library
        self._functions = dict(functions)
        self._token = int(token)
        self.authority = authority
        self.descriptor = dict(descriptor)
        self.last_control: dict[str, int] | None = None
        self.last_receipt: dict[str, int] | None = None
        self._execution_lock = threading.Lock()

    @property
    def closed(self) -> bool:
        return self._token == 0

    def execute_complete(
        self,
        query_columns: ParticleQueryColumns,
        expected_output: np.ndarray,
    ) -> np.ndarray:
        """Execute seven prebuilt SoA columns and return an exact read-only view."""

        if not self._execution_lock.acquire(blocking=False):
            raise ParticleNativeError(
                "Particle product owner already has an active operation"
            )
        try:
            return self._execute_complete_locked(query_columns, expected_output)
        finally:
            self._execution_lock.release()

    def _execute_complete_locked(
        self,
        query_columns: ParticleQueryColumns,
        expected_output: np.ndarray,
    ) -> np.ndarray:
        """Native execute and oracle comparison while the owner lock is held."""

        if self.closed:
            raise ParticleNativeError("Particle product owner is closed")
        if not isinstance(query_columns, ParticleQueryColumns):
            raise ParticleInputError(
                "query_columns must be seven contiguous ParticleQueryColumns; "
                "Nx7 conversion is outside this formal adapter"
            )
        _require_array(
            "expected_output", expected_output, np.uint32, (QUERY_COUNT, 3),
            require_c_contiguous=False,
        )

        # The caller supplies the seven already-contiguous SoA columns.  This
        # formal path performs no Nx7 transpose, coercion, or hidden H2H copy.
        query_pointers = tuple(
            column.ctypes.data_as(_FLOAT_PTR)
            for column in query_columns.native_order()
        )
        borrowed_output = _U32_PTR()
        borrowed_row_count = ctypes.c_size_t(0)
        control = _ParticleControl()
        receipt = _ParticleFastReceipt()
        _checked_call(
            EXECUTE_SYMBOL,
            self._functions[EXECUTE_SYMBOL],
            ctypes.c_uint64(self._token),
            *query_pointers,
            ctypes.c_size_t(QUERY_COUNT),
            ctypes.byref(borrowed_output),
            ctypes.byref(borrowed_row_count),
            ctypes.byref(control),
            ctypes.byref(receipt),
        )

        control_values = _structure_values(control)
        receipt_values = _structure_values(receipt)
        success = _validate_control(control_values)
        _validate_receipt(receipt_values, success)
        self.last_control = control_values
        self.last_receipt = receipt_values
        if not success:
            # Receipt validation above proves that no output D2H happened.
            # The native v2 ABI must also withhold its borrowed output.
            if bool(borrowed_output) or borrowed_row_count.value != 0:
                raise ParticleReceiptError(
                    "Particle failure exposed a non-null borrowed output"
                )
            raise ParticleDeviceStatusError(control_values, receipt_values)

        if not bool(borrowed_output) or borrowed_row_count.value != QUERY_COUNT:
            raise ParticleReceiptError(
                "Particle success did not expose exactly 5,000 borrowed rows"
            )
        # Keep the same borrowed-transpose convention as the matched PyOptiX
        # arm.  The native v2 pointer is its already-filled page-locked SoA;
        # there is no Python output allocation and no extra 60-KB host copy.
        packed_output = np.ctypeslib.as_array(
            borrowed_output, shape=(3 * QUERY_COUNT,)
        )
        output = packed_output.reshape((3, QUERY_COUNT)).T
        output.setflags(write=False)
        if output.dtype != np.dtype(np.uint32) or output.shape != (QUERY_COUNT, 3):
            raise ParticleReceiptError("Particle output view has an invalid layout")
        if np.shares_memory(output, expected_output):
            raise ParticleInputError(
                "Particle output and exact oracle must not share memory"
            )
        if not np.array_equal(output, expected_output):
            raise ParticleOracleMismatch(
                "Particle output differs from the supplied exact 5,000-row oracle"
            )
        return output

    def close(self) -> None:
        if not self._execution_lock.acquire(blocking=False):
            raise ParticleNativeError(
                "Particle product owner already has an active operation"
            )
        try:
            if self.closed:
                return
            token = ctypes.c_uint64(self._token)
            _checked_call(
                DESTROY_SYMBOL,
                self._functions[DESTROY_SYMBOL],
                ctypes.byref(token),
            )
            if token.value != 0:
                raise ParticleNativeError(
                    "Particle destroy did not zero its token cell"
                )
            self._token = 0
        finally:
            self._execution_lock.release()

    def __enter__(self) -> "ParticleProductOwner":
        if self.closed:
            raise ParticleNativeError("Particle product owner is closed")
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


def prepare_particle_product_owner(
    library: Any,
    prebuilt: ParticlePrebuiltPTX,
    static_input: ParticleStaticInput,
) -> ParticleProductOwner:
    """Verify authorities and prepare the exact product-native lifecycle."""

    if not isinstance(prebuilt, ParticlePrebuiltPTX):
        raise ParticleInputError("prebuilt must be ParticlePrebuiltPTX")
    if not isinstance(static_input, ParticleStaticInput):
        raise ParticleInputError("static_input must be ParticleStaticInput")
    functions = _configure_native(library)
    source = _query_export(SOURCE_SYMBOL, functions[SOURCE_SYMBOL])
    descriptor_bytes = _query_export(
        DESCRIPTOR_SYMBOL, functions[DESCRIPTOR_SYMBOL]
    )
    authority, descriptor = _verify_authority(source, descriptor_bytes, prebuilt)

    token = ctypes.c_uint64(0)
    _checked_call(
        PREPARE_SYMBOL,
        functions[PREPARE_SYMBOL],
        prebuilt.ptx,
        static_input.vertices.ctypes.data_as(_FLOAT_PTR),
        ctypes.c_size_t(VERTEX_COUNT),
        static_input.triangles.ctypes.data_as(_U32_PTR),
        ctypes.c_size_t(TRIANGLE_COUNT),
        static_input.front_values.ctypes.data_as(_U32_PTR),
        static_input.back_values.ctypes.data_as(_U32_PTR),
        ctypes.byref(token),
    )
    if token.value == 0:
        raise ParticleNativeError("Particle prepare returned a zero token")
    return ParticleProductOwner(
        library, functions, token.value, authority, descriptor
    )


__all__ = [
    "ParticleAuthority",
    "ParticleAuthorityError",
    "ParticleDeviceStatusError",
    "ParticleInputError",
    "ParticleNativeError",
    "ParticleOracleMismatch",
    "ParticlePrebuiltPTX",
    "ParticleProductError",
    "ParticleProductOwner",
    "ParticleQueryColumns",
    "ParticleReceiptError",
    "ParticleStaticInput",
    "prepare_particle_product_owner",
]
