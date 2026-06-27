from __future__ import annotations

import ctypes
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .optix_runtime import _check_status
from .optix_runtime import _find_optional_backend_symbol
from .optix_runtime import _load_optix_library
from .rt_barneshut_author_contract import (
    RT_BARNESHUT_AUTHOR_COMMIT,
    RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
)


V4_RT_BARNESHUT_NATIVE_ROUTE_VERSION = "rtdl.v4.rt_barneshut.native_author_route.feasibility.v1"
V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_BLOCKED = (
    "blocked_missing_native_3d_author_semantics_rt_core_route"
)
V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_SYMBOLS_PRESENT_UNVALIDATED = (
    "native_3d_author_semantics_symbols_present_unvalidated"
)
V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE = (
    "native_3d_author_semantics_host_fallback_available"
)
V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE = (
    "native_3d_author_semantics_rt_core_candidate_available"
)

V4_RT_BARNESHUT_NATIVE_IMPLEMENTATION_STATUS_HOST_FALLBACK = 2
V4_RT_BARNESHUT_NATIVE_IMPLEMENTATION_STATUS_RT_CORE = 3

V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS = (
    "rtdl_optix_prepare_rt_barneshut_author_3d",
    "rtdl_optix_run_rt_barneshut_author_3d",
    "rtdl_optix_destroy_rt_barneshut_author_3d",
)

V4_RT_BARNESHUT_EXISTING_2D_AGGREGATE_TREE_SYMBOLS = (
    "rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d",
    "rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d",
    "rtdl_optix_destroy_aggregate_tree_fused_weighted_vector_sum_2d",
)

V4_RT_BARNESHUT_NATIVE_REQUIRED_DATAFLOW = (
    "author_format_input_loader_or_device_column_ingest",
    "3d_float32_position_columns_x_y_z",
    "float32_mass_column_with_author_csv_scaling_when_applicable",
    "author_z_order_or_equivalent_tree_order",
    "bucket_size_32_leaf_contract",
    "3d_tree_or_bvh_nodes_with_child_or_rope_resume_metadata",
    "theta_0_5_author_opening_rule",
    "author_force_law_checksum_parity",
    "phase_seconds_preprocessing_rt_force_execution_wall",
)


class V4RtBarnesHutNativeRouteUnavailable(RuntimeError):
    """Raised when a caller asks for the native author route before it exists."""


@dataclass(frozen=True)
class V4RtBarnesHutNativeFeasibility:
    status: str
    route_version: str
    contract_version: str
    author_commit: str
    source_root: str
    inspected_files: tuple[str, ...]
    existing_2d_aggregate_tree_symbols: dict[str, bool]
    required_native_author_symbols: tuple[str, ...]
    missing_native_author_symbols: tuple[str, ...]
    required_dataflow: tuple[str, ...]
    reusable_assets: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    next_implementation_steps: tuple[str, ...]
    claim_boundary: dict[str, bool | str]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class V4RtBarnesHutNativeFallbackRun:
    status: str
    route_version: str
    contract_version: str
    author_commit: str
    point_count: int
    implementation_status_code: int
    implementation_status: str
    force_checksum: float
    force_abs_checksum: float
    force_min: float
    force_max: float
    first_forces: tuple[float, ...]
    phase_seconds: dict[str, float]
    device_columns: dict[str, bool | int]
    claim_boundary: dict[str, bool | str]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class _RtdlRtBarnesHutAuthor3DOutput(ctypes.Structure):
    _fields_ = [
        ("point_ids_device_ptr", ctypes.c_uint64),
        ("force_device_ptr", ctypes.c_uint64),
        ("point_count", ctypes.c_uint64),
        ("diagnostic_status_code", ctypes.c_int32),
        ("implementation_status_code", ctypes.c_uint32),
        ("device_ordinal", ctypes.c_int32),
        ("owner_handle", ctypes.c_void_p),
        ("preprocessing_seconds", ctypes.c_double),
        ("rt_force_seconds", ctypes.c_double),
        ("execution_seconds", ctypes.c_double),
        ("copy_seconds", ctypes.c_double),
    ]


def _repo_root_from_module() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_available_files(paths: Iterable[Path]) -> tuple[tuple[str, str], ...]:
    contents: list[tuple[str, str]] = []
    for path in paths:
        if path.exists():
            contents.append((str(path), path.read_text(encoding="utf-8", errors="replace")))
    return tuple(contents)


def inspect_v4_rt_barneshut_native_feasibility(
    source_root: str | Path | None = None,
) -> V4RtBarnesHutNativeFeasibility:
    root = Path(source_root) if source_root is not None else _repo_root_from_module()
    paths = (
        root / "src" / "native" / "optix" / "rtdl_optix_prelude.h",
        root / "src" / "native" / "optix" / "rtdl_optix_api.cpp",
        root / "src" / "rtdsl" / "optix_runtime.py",
        root / "src" / "rtdsl" / "aggregate_tree_reference.py",
        root / "src" / "rtdsl" / "rt_barneshut_author_contract.py",
    )
    contents = _read_available_files(paths)
    haystack = "\n".join(text for _, text in contents)
    existing_2d = {
        symbol: symbol in haystack
        for symbol in V4_RT_BARNESHUT_EXISTING_2D_AGGREGATE_TREE_SYMBOLS
    }
    missing = tuple(
        symbol
        for symbol in V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS
        if symbol not in haystack
    )

    host_fallback_available = (
        not missing
        and "rtdl_rt_barneshut_author_host_fallback_forces" in haystack
        and "kRtBarnesHutAuthorImplementationStatusHostFallback" in haystack
    )
    rt_core_candidate_available = (
        host_fallback_available
        and "kRtBarnesHutAuthorImplementationStatusRtCore" in haystack
        and "__raygen__rt_barneshut_author3d" in haystack
        and "rtdl_rt_barneshut_author_rt_core_forces" in haystack
    )

    if missing:
        blocking_reasons = (
            "Existing RTDL fused aggregate-tree primitive is 2D; author RT-BarnesHut is 3D.",
            "Existing 2D primitive uses RTDL aggregate-tree rows, not the author z-order/bucket-size-32 tree contract.",
            "No native V4 prepare/run/destroy ABI exists for author-semantics 3D RT-BarnesHut.",
            "The external author binary route is a reference/control route and cannot count as a native V4 operator.",
        )
        next_steps = (
            "Add the three native OptiX ABI symbols listed in required_native_author_symbols.",
            "Bind 3D x/y/z/mass/id device columns and author-compatible tree metadata to the native ABI.",
            "Implement the RT-core traversal/force kernel against the Goal4760 checksum oracle on 4096 and 8192 rows first.",
            "Only after checksum parity, scale to 32768 then 1M author-format points and compare with the author binary.",
            "Keep this route out of generic V4 operator geomean until an external reviewer accepts the paper-reproduction claim.",
        )
    elif rt_core_candidate_available:
        blocking_reasons = (
            "Native 3D author-route ABI symbols are present and an RT-core candidate path exists.",
            "The candidate still builds author-compatible tree metadata on the host from device-column snapshots.",
            "It must pass 4096/8192 checksum parity before it can be called a native V4 RT-core operator.",
            "Existing 2D aggregate-tree route remains non-author-equivalent and cannot substitute for this route.",
            "The external author binary route remains a reference/control route and cannot count as this native V4 operator.",
        )
        next_steps = (
            "Run the 4096/8192 checksum parity probes against the native RT-core candidate path.",
            "If checksum parity fails, record the traversal/control-geometry blocker rather than falling back silently.",
            "If checksum parity passes, compare phase timings against the Goal4761 external author reference route.",
            "Only after those gates, scale to 32768 and then 1M author-format points.",
            "Keep public RT-BarnesHut paper reproduction wording blocked until external review accepts the result.",
        )
    elif host_fallback_available:
        blocking_reasons = (
            "Native 3D author-route ABI symbols are present and a checksum route exists, but it is a host fallback.",
            "The current route downloads device columns, computes author semantics on host, and uploads force output back to device.",
            "This proves the ABI/dataflow/checksum contract, not RT-core traversal or V4 operator performance.",
            "Existing 2D aggregate-tree route remains non-author-equivalent and cannot substitute for this route.",
            "The external author binary route remains a reference/control route and cannot count as a native V4 operator.",
        )
        next_steps = (
            "Replace the host fallback with author-compatible OptiX traversal and force evaluation behind the same ABI.",
            "Bind author-compatible 3D tree/BVH metadata instead of the RTDL 2D aggregate-tree rows.",
            "Keep the 4096/8192 checksum parity probes as regression gates during the RT-core replacement.",
            "After RT-core checksum parity, compare phase timings against the Goal4761 external author reference route.",
            "Only after those gates, scale to 32768 and then 1M author-format points.",
        )
    else:
        blocking_reasons = (
            "Native 3D author-route ABI symbols are present, but the run path is not checksum-validated.",
            "The current ABI first slice intentionally fails closed until the OptiX traversal and force kernel are implemented.",
            "Existing 2D aggregate-tree route remains non-author-equivalent and cannot substitute for this route.",
            "The external author binary route remains a reference/control route and cannot count as a native V4 operator.",
        )
        next_steps = (
            "Implement the OptiX traversal and force kernel behind rtdl_optix_run_rt_barneshut_author_3d.",
            "Bind author-compatible 3D tree/BVH metadata instead of the RTDL 2D aggregate-tree rows.",
            "Pass checksum parity against the Goal4760 CPU oracle on 4096 and 8192 author-format rows.",
            "After checksum parity, compare phase timings against the Goal4761 external author reference route.",
            "Only after those gates, scale to 32768 and then 1M author-format points.",
        )

    return V4RtBarnesHutNativeFeasibility(
        status=(
            V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_BLOCKED
            if missing
            else (
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE
                if rt_core_candidate_available
                else V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE
                if host_fallback_available
                else V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_SYMBOLS_PRESENT_UNVALIDATED
            )
        ),
        route_version=V4_RT_BARNESHUT_NATIVE_ROUTE_VERSION,
        contract_version=RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
        author_commit=RT_BARNESHUT_AUTHOR_COMMIT,
        source_root=str(root),
        inspected_files=tuple(path for path, _ in contents),
        existing_2d_aggregate_tree_symbols=existing_2d,
        required_native_author_symbols=V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS,
        missing_native_author_symbols=missing,
        required_dataflow=V4_RT_BARNESHUT_NATIVE_REQUIRED_DATAFLOW,
        reusable_assets=(
            "Goal4760 author-format loader and checksum CPU oracle",
            "Goal4761 external author RT-core reference route",
            "existing 2D aggregate-tree fused weighted-vector-sum runner for non-author 2D workflow",
            "native OptiX/Driver API loading pattern in src/rtdsl/optix_runtime.py",
        ),
        blocking_reasons=blocking_reasons,
        next_implementation_steps=next_steps,
        claim_boundary={
            "native_v4_abi_symbols_available": not missing,
            "native_v4_checksum_route_available": host_fallback_available,
            "native_v4_operator_available": False,
            "rt_core_candidate_available": rt_core_candidate_available,
            "host_fallback_used_when_available": host_fallback_available and not rt_core_candidate_available,
            "rt_core_execution_authorized": False,
            "external_author_binary_used": False,
            "same_semantics_author_contract_required": True,
            "existing_2d_aggregate_tree_route_is_author_equivalent": False,
            "old_2d_rtdl_workflow_may_be_divided_by_author_binary": False,
            "public_rt_barneshut_paper_reproduction_claim_authorized": False,
            "v2_v3_v4_author_speed_table_authorized": False,
            "goal4762_completion_authorizes_release": False,
            "purpose": "fail-closed native-route feasibility gate for RT-BarnesHut author semantics",
        },
    )


def _load_native_author_library(optix_library: str | Path | None):
    if optix_library is not None:
        lib = ctypes.CDLL(str(optix_library))
        setattr(lib, "_rtdl_library_path", str(optix_library))
        return lib
    return _load_optix_library()


def _configure_native_author_symbols(lib):
    prepare = _find_optional_backend_symbol(lib, "rtdl_optix_prepare_rt_barneshut_author_3d")
    run = _find_optional_backend_symbol(lib, "rtdl_optix_run_rt_barneshut_author_3d")
    destroy = _find_optional_backend_symbol(lib, "rtdl_optix_destroy_rt_barneshut_author_3d")
    if prepare is None or run is None or destroy is None:
        missing = [
            name
            for name, symbol in (
                ("rtdl_optix_prepare_rt_barneshut_author_3d", prepare),
                ("rtdl_optix_run_rt_barneshut_author_3d", run),
                ("rtdl_optix_destroy_rt_barneshut_author_3d", destroy),
            )
            if symbol is None
        ]
        raise V4RtBarnesHutNativeRouteUnavailable(
            "Native V4 RT-BarnesHut author-semantics route is not available; "
            f"missing required native symbols: {', '.join(missing)}"
        )
    prepare.argtypes = [
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    prepare.restype = ctypes.c_int
    run.argtypes = [
        ctypes.c_void_p,
        ctypes.c_double,
        ctypes.POINTER(_RtdlRtBarnesHutAuthor3DOutput),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    run.restype = ctypes.c_int
    destroy.argtypes = [ctypes.c_void_p]
    destroy.restype = None
    return prepare, run, destroy


def _copy_force_column_from_device(force_device_ptr: int, point_count: int) -> tuple[float, ...]:
    if point_count == 0:
        return ()
    if force_device_ptr == 0:
        raise RuntimeError("native RT-BarnesHut fallback returned a null force device pointer")
    try:
        import cupy as cp
    except ImportError as exc:  # pragma: no cover - exercised on GPU/POD only.
        raise RuntimeError("copying native RT-BarnesHut device output requires cupy") from exc

    memory = cp.cuda.UnownedMemory(int(force_device_ptr), int(point_count) * 4, object())
    pointer = cp.cuda.MemoryPointer(memory, 0)
    device_forces = cp.ndarray((int(point_count),), dtype=cp.float32, memptr=pointer)
    host = cp.asnumpy(device_forces)
    return tuple(float(value) for value in host.tolist())


def run_v4_rt_barneshut_native_author_route(
    *,
    point_ids_device_ptr: int | None = None,
    point_x_device_ptr: int | None = None,
    point_y_device_ptr: int | None = None,
    point_z_device_ptr: int | None = None,
    point_mass_device_ptr: int | None = None,
    point_count: int | None = None,
    theta: float = 0.5,
    optix_library: str | Path | None = None,
    first_force_count: int = 8,
) -> V4RtBarnesHutNativeFallbackRun:
    feasibility = inspect_v4_rt_barneshut_native_feasibility()
    if feasibility.missing_native_author_symbols:
        missing = ", ".join(feasibility.missing_native_author_symbols)
        raise V4RtBarnesHutNativeRouteUnavailable(
            "Native V4 RT-BarnesHut author-semantics route is not implemented; "
            f"missing required native symbols: {missing}"
        )
    if (
        point_ids_device_ptr is None
        or point_x_device_ptr is None
        or point_y_device_ptr is None
        or point_z_device_ptr is None
        or point_mass_device_ptr is None
        or point_count is None
    ):
        raise V4RtBarnesHutNativeRouteUnavailable(
            "Native V4 RT-BarnesHut fallback route requires explicit CUDA device column pointers"
        )
    if int(point_count) < 0:
        raise ValueError("point_count must be non-negative")

    lib = _load_native_author_library(optix_library)
    prepare, run, destroy = _configure_native_author_symbols(lib)
    error = ctypes.create_string_buffer(4096)
    prepared = ctypes.c_void_p()
    _check_status(
        prepare(
            ctypes.c_uint64(int(point_ids_device_ptr)),
            ctypes.c_uint64(int(point_x_device_ptr)),
            ctypes.c_uint64(int(point_y_device_ptr)),
            ctypes.c_uint64(int(point_z_device_ptr)),
            ctypes.c_uint64(int(point_mass_device_ptr)),
            ctypes.c_size_t(int(point_count)),
            ctypes.byref(prepared),
            error,
            ctypes.sizeof(error),
        ),
        error,
    )
    output = _RtdlRtBarnesHutAuthor3DOutput()
    try:
        error = ctypes.create_string_buffer(4096)
        _check_status(
            run(
                prepared,
                ctypes.c_double(float(theta)),
                ctypes.byref(output),
                error,
                ctypes.sizeof(error),
            ),
            error,
        )
        if output.diagnostic_status_code != 0:
            raise RuntimeError(
                f"native RT-BarnesHut fallback returned diagnostic status {output.diagnostic_status_code}"
            )
        forces = _copy_force_column_from_device(output.force_device_ptr, int(output.point_count))
    finally:
        if prepared.value:
            destroy(prepared)

    force_checksum = float(sum(forces))
    force_abs_checksum = float(sum(abs(value) for value in forces))
    implementation_status_code = int(output.implementation_status_code)
    rt_core_execution = implementation_status_code == V4_RT_BARNESHUT_NATIVE_IMPLEMENTATION_STATUS_RT_CORE
    host_fallback_used = (
        implementation_status_code == V4_RT_BARNESHUT_NATIVE_IMPLEMENTATION_STATUS_HOST_FALLBACK
    )
    return V4RtBarnesHutNativeFallbackRun(
        status=(
            V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE
            if rt_core_execution
            else V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE
            if host_fallback_used
            else V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_SYMBOLS_PRESENT_UNVALIDATED
        ),
        route_version=V4_RT_BARNESHUT_NATIVE_ROUTE_VERSION,
        contract_version=RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
        author_commit=RT_BARNESHUT_AUTHOR_COMMIT,
        point_count=int(output.point_count),
        implementation_status_code=implementation_status_code,
        implementation_status=(
            "host_fallback_author_semantics_checksum_route"
            if host_fallback_used
            else "rt_core_author_semantics_candidate_route"
            if rt_core_execution
            else "unknown"
        ),
        force_checksum=force_checksum,
        force_abs_checksum=force_abs_checksum,
        force_min=float(min(forces)) if forces else 0.0,
        force_max=float(max(forces)) if forces else 0.0,
        first_forces=tuple(forces[:first_force_count]),
        phase_seconds={
            "preprocessing_seconds": float(output.preprocessing_seconds),
            (
                "rt_force_seconds_field_contains_fallback_force_seconds"
                if host_fallback_used
                else "rt_force_seconds"
            ): float(output.rt_force_seconds),
            "execution_seconds": float(output.execution_seconds),
            "copy_seconds": float(output.copy_seconds),
        },
        device_columns={
            "point_ids_device_ptr_nonzero": bool(output.point_ids_device_ptr),
            "force_device_ptr_nonzero": bool(output.force_device_ptr),
            "point_count": int(output.point_count),
        },
        claim_boundary={
            "native_v4_abi_symbols_available": True,
            "native_v4_checksum_route_available": True,
            "native_v4_operator_available": rt_core_execution,
            "host_fallback_used": host_fallback_used,
            "rt_core_execution": rt_core_execution,
            "input_columns_downloaded_for_tree_build": True,
            "external_author_binary_used": False,
            "same_semantics_author_contract_required": True,
            "public_rt_barneshut_paper_reproduction_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "v2_v3_v4_author_speed_table_authorized": False,
            "purpose": "native ABI author-semantics checksum route with explicit RT-core/fallback status",
        },
    )


def validate_v4_rt_barneshut_native_feasibility(
    feasibility: V4RtBarnesHutNativeFeasibility,
) -> None:
    if feasibility.route_version != V4_RT_BARNESHUT_NATIVE_ROUTE_VERSION:
        raise ValueError("unexpected RT-BarnesHut native feasibility route version")
    if feasibility.contract_version != RT_BARNESHUT_AUTHOR_CONTRACT_VERSION:
        raise ValueError("unexpected RT-BarnesHut author contract version")
    if not feasibility.claim_boundary["same_semantics_author_contract_required"]:
        raise ValueError("native route must require the author semantics contract")
    if feasibility.claim_boundary["existing_2d_aggregate_tree_route_is_author_equivalent"]:
        raise ValueError("2D aggregate-tree route must not be marked author-equivalent")
    if feasibility.claim_boundary["public_rt_barneshut_paper_reproduction_claim_authorized"]:
        raise ValueError("Goal4762 must not authorize public RT-BarnesHut reproduction claims")
    if feasibility.claim_boundary["v2_v3_v4_author_speed_table_authorized"]:
        raise ValueError("Goal4762 must not authorize a V2/V3/V4 author-speed table")
    if feasibility.status == V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_BLOCKED:
        if not feasibility.missing_native_author_symbols:
            raise ValueError("blocked feasibility status requires missing native symbols")
    if feasibility.status == V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE:
        if not feasibility.claim_boundary["host_fallback_used_when_available"]:
            raise ValueError("host fallback status must preserve host_fallback_used_when_available")
        if feasibility.claim_boundary["rt_core_execution_authorized"]:
            raise ValueError("host fallback status must not authorize RT-core execution")
    if feasibility.status == V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE:
        if not feasibility.claim_boundary["rt_core_candidate_available"]:
            raise ValueError("RT-core candidate status must expose rt_core_candidate_available")
    for symbol in V4_RT_BARNESHUT_EXISTING_2D_AGGREGATE_TREE_SYMBOLS:
        if symbol not in feasibility.existing_2d_aggregate_tree_symbols:
            raise ValueError(f"missing existing 2D symbol audit entry: {symbol}")
