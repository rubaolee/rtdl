from __future__ import annotations

import ctypes
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Mapping


ACTION_NATIVE_LIBRARY_IDENTITY_VERSION = "rtdl.native_library_identity.v1"
ACTION_NATIVE_TEMPLATE_SYMBOL_PROBE_VERSION = "rtdl.native_template_symbol_probe.v1"

CERTIFIED_NEAREST_GLOBAL_WITNESS_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_cuda_prepare_certified_nearest_grid_3d",
    "rtdl_cuda_prepare_certified_nearest_grid_3d_from_validated_columns",
    "rtdl_cuda_execute_prepared_certified_nearest_global_witness_3d",
    "rtdl_cuda_close_prepared_certified_nearest_grid_3d",
)

CERTIFIED_NEAREST_OPTIX_TRAVERSAL_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_cuda_point_grid_cell_mbrs_3d",
    "rtdl_optix_prepare_certified_nearest_state_3d",
    "rtdl_optix_run_prepared_certified_nearest_global_witness_3d",
    "rtdl_optix_destroy_prepared_certified_nearest_state_3d",
)

CELL_MBR_EXACT_WITNESS_OPTIX_TRAVERSAL_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_cuda_point_grid_cell_mbrs_3d",
    "rtdl_optix_seed_nearest_witness_local_grid_3d",
    "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4",
)

FIXED_RADIUS_GRAPH_COMPONENTS_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_prepare_fixed_radius_count_threshold_3d",
    "rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs",
    "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs",
    "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d",
)

PREPARED_RANKED_DISTANCE_WINDOW_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_prepare_fixed_radius_neighbors_3d",
    "rtdl_optix_run_prepared_ranked_distance_window_neighbors_3d",
    "rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d",
    "rtdl_optix_free_rows",
)

CANDIDATE_PRUNED_EXACT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_cuda_prepare_certified_nearest_grid_3d",
    "rtdl_cuda_prepare_certified_nearest_grid_3d_from_validated_columns",
    "rtdl_cuda_execute_prepared_certified_nearest_global_witness_3d",
    "rtdl_cuda_execute_prepared_exact_bounded_selection_3d",
    "rtdl_cuda_close_prepared_certified_nearest_grid_3d",
)

ACTION_POINT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_prepare_action_point_candidates_3d",
    "rtdl_optix_run_prepared_action_bounded_selection_3d",
    "rtdl_optix_destroy_prepared_action_point_candidates_3d",
    "rtdl_optix_free_rows",
)

METRIC_KNN_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_prepare_metric_knn_3d",
    "rtdl_optix_execute_prepared_metric_knn_3d",
    "rtdl_optix_destroy_prepared_metric_knn_3d",
    "rtdl_optix_free_rows",
)

RAY_TRIANGLE_GROUPED_I64_3D_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_static_triangle_scene_3d_create",
    "rtdl_optix_static_triangle_scene_3d_create_device_triangles",
    "rtdl_optix_static_triangle_scene_3d_destroy",
    "rtdl_optix_primitive_grouped_i64_payload_3d_create_signed_v2",
    "rtdl_optix_primitive_grouped_i64_payload_3d_create_signed_verified_v3",
    "rtdl_optix_primitive_grouped_i64_payload_3d_destroy",
    "rtdl_optix_ray_batch_3d_create",
    "rtdl_optix_ray_batch_3d_create_device_rays",
    "rtdl_optix_ray_batch_3d_destroy",
    "rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction_signed_v2",
    "rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_signed_v2",
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(
        dict(payload), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalized_required_symbols(required_symbols) -> tuple[str, ...]:
    symbols = tuple(required_symbols)
    if (
        not symbols
        or len(set(symbols)) != len(symbols)
        or any(
            not isinstance(symbol, str)
            or not symbol
            or any(char.isspace() for char in symbol)
            for symbol in symbols
        )
    ):
        raise ValueError("required_symbols must be unique nonempty identifiers")
    return symbols


def _optix_version_from_library(library) -> tuple[int, int, int]:
    symbol = getattr(library, "rtdl_optix_get_version", None)
    if symbol is None:
        raise RuntimeError("loaded native library lacks rtdl_optix_get_version")
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    status = int(symbol(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch)))
    if status != 0:
        raise RuntimeError(f"native OptiX version query failed with status {status}")
    version = (int(major.value), int(minor.value), int(patch.value))
    if any(value < 0 for value in version):
        raise RuntimeError("native OptiX version contains a negative component")
    return version


@dataclass(frozen=True)
class ActionNativeLibraryIdentity:
    resolved_path: str
    binary_sha256: str
    optix_version: tuple[int, int, int]
    required_symbols: tuple[str, ...]
    required_symbols_digest: str
    process_handle_token: str
    identity_digest: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": ACTION_NATIVE_LIBRARY_IDENTITY_VERSION,
            "resolved_path": self.resolved_path,
            "binary_sha256": self.binary_sha256,
            "optix_version": list(self.optix_version),
            "required_symbols": list(self.required_symbols),
            "required_symbols_digest": self.required_symbols_digest,
            "process_handle_token": self.process_handle_token,
            "identity_digest": self.identity_digest,
        }


@dataclass(frozen=True)
class ActionNativeTemplateSymbolProbe:
    attempted: bool
    available: bool
    required_symbols: tuple[str, ...]
    missing_symbols: tuple[str, ...] = ()
    library_identity: ActionNativeLibraryIdentity | None = None
    error: str | None = None
    _library_ref: object | None = field(default=None, repr=False, compare=False)

    @property
    def library_ref(self):
        return self._library_ref

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": ACTION_NATIVE_TEMPLATE_SYMBOL_PROBE_VERSION,
            "attempted": self.attempted,
            "available": self.available,
            "required_symbols": list(self.required_symbols),
            "missing_symbols": list(self.missing_symbols),
            "library_path": (
                self.library_identity.resolved_path
                if self.library_identity is not None
                else None
            ),
            "library_identity": (
                self.library_identity.to_metadata()
                if self.library_identity is not None
                else None
            ),
            "error": self.error,
            "availability_derived_from_target_optix_flag_only": False,
        }


def native_library_identity(
    library,
    *,
    required_symbols: tuple[str, ...],
) -> ActionNativeLibraryIdentity:
    """Bind one loaded native object to its path, bytes, ABI, version, and handle."""

    symbols = _normalized_required_symbols(required_symbols)
    raw_path = getattr(library, "_rtdl_library_path", None)
    if not isinstance(raw_path, str) or not raw_path:
        raise RuntimeError("loaded native library has no resolved path identity")
    path = Path(raw_path).expanduser().resolve(strict=True)
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("loaded native library path is not a regular file")
    handle = getattr(library, "_handle", None)
    if not isinstance(handle, int) or isinstance(handle, bool) or handle <= 0:
        raise RuntimeError("loaded native library has no process handle identity")
    required_symbols_digest = hashlib.sha256(
        json.dumps(list(symbols), separators=(",", ":")).encode("ascii")
    ).hexdigest()
    payload = {
        "contract": ACTION_NATIVE_LIBRARY_IDENTITY_VERSION,
        "resolved_path": str(path),
        "binary_sha256": _sha256_file(path),
        "optix_version": list(_optix_version_from_library(library)),
        "required_symbols": list(symbols),
        "required_symbols_digest": required_symbols_digest,
        "process_handle_token": str(handle),
    }
    return ActionNativeLibraryIdentity(
        resolved_path=str(payload["resolved_path"]),
        binary_sha256=str(payload["binary_sha256"]),
        optix_version=tuple(int(value) for value in payload["optix_version"]),
        required_symbols=symbols,
        required_symbols_digest=required_symbols_digest,
        process_handle_token=str(handle),
        identity_digest=_digest(payload),
    )


def validate_native_library_identity(
    library,
    expected: ActionNativeLibraryIdentity,
) -> ActionNativeLibraryIdentity:
    """Recompute a sealed library identity and require every ABI symbol again."""

    if not isinstance(expected, ActionNativeLibraryIdentity):
        raise TypeError("expected must be an ActionNativeLibraryIdentity")
    from .optix_runtime import _find_optional_backend_symbol

    missing = tuple(
        symbol
        for symbol in expected.required_symbols
        if _find_optional_backend_symbol(library, symbol) is None
    )
    if missing:
        raise RuntimeError(
            "loaded native library lost required symbols: " + ", ".join(missing)
        )
    actual = native_library_identity(
        library,
        required_symbols=expected.required_symbols,
    )
    if actual != expected:
        raise RuntimeError("loaded native library identity changed after planning")
    return actual


def validate_native_library_identity_metadata(
    payload: Mapping[str, object],
) -> dict[str, object]:
    """Validate a persisted identity without loading or trusting its library."""

    if not isinstance(payload, Mapping):
        raise ValueError("native library identity metadata must be a mapping")
    expected_keys = {
        "contract",
        "resolved_path",
        "binary_sha256",
        "optix_version",
        "required_symbols",
        "required_symbols_digest",
        "process_handle_token",
        "identity_digest",
    }
    if set(payload) != expected_keys:
        raise ValueError("native library identity metadata fields are incomplete")
    if payload.get("contract") != ACTION_NATIVE_LIBRARY_IDENTITY_VERSION:
        raise ValueError("native library identity metadata contract is invalid")
    path = payload.get("resolved_path")
    binary_sha256 = payload.get("binary_sha256")
    version = payload.get("optix_version")
    symbols = _normalized_required_symbols(payload.get("required_symbols", ()))
    symbols_digest = hashlib.sha256(
        json.dumps(list(symbols), separators=(",", ":")).encode("ascii")
    ).hexdigest()
    handle = payload.get("process_handle_token")
    identity_digest = payload.get("identity_digest")
    cross_platform_absolute = (
        isinstance(path, str)
        and bool(path)
        and "\x00" not in path
        and (
            PurePosixPath(path).is_absolute()
            or PureWindowsPath(path).is_absolute()
        )
    )
    if not cross_platform_absolute:
        raise ValueError("native library identity path is not absolute")
    for name, value in (
        ("binary_sha256", binary_sha256),
        ("required_symbols_digest", payload.get("required_symbols_digest")),
        ("identity_digest", identity_digest),
    ):
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"native library identity {name} is invalid")
        try:
            int(value, 16)
        except ValueError as exc:
            raise ValueError(
                f"native library identity {name} is invalid"
            ) from exc
    if payload.get("required_symbols_digest") != symbols_digest:
        raise ValueError("native library required-symbol digest is invalid")
    if (
        not isinstance(version, list)
        or len(version) != 3
        or any(
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
            for value in version
        )
    ):
        raise ValueError("native library OptiX version is invalid")
    if not isinstance(handle, str) or not handle.isdigit() or int(handle) <= 0:
        raise ValueError("native library process handle token is invalid")
    unsigned = {key: payload[key] for key in expected_keys - {"identity_digest"}}
    if _digest(unsigned) != identity_digest:
        raise ValueError("native library identity digest is invalid")
    return dict(payload)


def probe_native_template_symbols(
    required_symbols: tuple[str, ...],
) -> ActionNativeTemplateSymbolProbe:
    """Resolve one native object and prove an exact template ABI on that object."""

    symbols = _normalized_required_symbols(required_symbols)
    try:
        from .optix_runtime import _find_optional_backend_symbol, _load_optix_library

        library = _load_optix_library()
        identity = native_library_identity(library, required_symbols=symbols)
        missing = tuple(
            symbol
            for symbol in symbols
            if _find_optional_backend_symbol(library, symbol) is None
        )
        return ActionNativeTemplateSymbolProbe(
            attempted=True,
            available=not missing,
            required_symbols=symbols,
            missing_symbols=missing,
            library_identity=identity,
            error=("required_native_symbol_missing" if missing else None),
            _library_ref=library,
        )
    except Exception as exc:
        return ActionNativeTemplateSymbolProbe(
            attempted=True,
            available=False,
            required_symbols=symbols,
            error=f"{type(exc).__name__}:{exc}",
        )


def probe_certified_nearest_global_witness_3d(
) -> ActionNativeTemplateSymbolProbe:
    return probe_native_template_symbols(
        CERTIFIED_NEAREST_GLOBAL_WITNESS_3D_REQUIRED_SYMBOLS
    )


def probe_certified_nearest_optix_traversal_3d(
) -> ActionNativeTemplateSymbolProbe:
    return probe_native_template_symbols(
        CERTIFIED_NEAREST_OPTIX_TRAVERSAL_3D_REQUIRED_SYMBOLS
    )


def probe_cell_mbr_exact_witness_optix_traversal_3d(
) -> ActionNativeTemplateSymbolProbe:
    return probe_native_template_symbols(
        CELL_MBR_EXACT_WITNESS_OPTIX_TRAVERSAL_3D_REQUIRED_SYMBOLS
    )


__all__ = [
    "ACTION_NATIVE_LIBRARY_IDENTITY_VERSION",
    "ACTION_NATIVE_TEMPLATE_SYMBOL_PROBE_VERSION",
    "CERTIFIED_NEAREST_GLOBAL_WITNESS_3D_REQUIRED_SYMBOLS",
    "CERTIFIED_NEAREST_OPTIX_TRAVERSAL_3D_REQUIRED_SYMBOLS",
    "CELL_MBR_EXACT_WITNESS_OPTIX_TRAVERSAL_3D_REQUIRED_SYMBOLS",
    "FIXED_RADIUS_GRAPH_COMPONENTS_3D_REQUIRED_SYMBOLS",
    "PREPARED_RANKED_DISTANCE_WINDOW_3D_REQUIRED_SYMBOLS",
    "ACTION_POINT_BOUNDED_SELECTION_3D_REQUIRED_SYMBOLS",
    "METRIC_KNN_3D_REQUIRED_SYMBOLS",
    "RAY_TRIANGLE_GROUPED_I64_3D_REQUIRED_SYMBOLS",
    "ActionNativeLibraryIdentity",
    "ActionNativeTemplateSymbolProbe",
    "native_library_identity",
    "probe_certified_nearest_global_witness_3d",
    "probe_certified_nearest_optix_traversal_3d",
    "probe_cell_mbr_exact_witness_optix_traversal_3d",
    "probe_native_template_symbols",
    "validate_native_library_identity",
    "validate_native_library_identity_metadata",
]
