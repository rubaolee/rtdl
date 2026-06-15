from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
import importlib.util
import os
from pathlib import Path
import statistics
import time

from .reference import Point3D
from .v2_8_fixed_radius_graph_component_front_door import fixed_radius_graph_component_labels_3d_v2_8
from .v2_8_fixed_radius_graph_component_front_door import prepare_v2_8_fixed_radius_graph_component_continuation_3d
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import REQUIRED_PHASE_NAMES
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_instrumentation import EvidenceRecord
from .v3_0_instrumentation import InstrumentationPacket
from .v3_0_instrumentation import PhaseTimingRecord
from .v3_0_instrumentation import ResidencyEvidence


V3_M9_GROUPED_STREAM_VERSION = "rtdl.v3_0.grouped_stream_partner.m9"
V3_M9_GROUPED_STREAM_STATUS = "m9_device_resident_partner_rows_no_public_claim"
V3_M9_GRAPH_ID = "fixed_radius_component_grouped_stream_pilot"
V3_M9_CONTRACT_KEY = "fixed_radius_component_grouped_stream_contract_v1"
V3_M9_PARTNERS = ("cupy", "numba")


def make_v3_m9_point_grid_3d(point_count: int) -> tuple[Point3D, ...]:
    count = int(point_count)
    if count <= 0:
        raise GraphValidationError("point_count must be positive")
    width = max(1, round(count ** (1.0 / 3.0)))
    rows = []
    for index in range(count):
        x = float(index % width)
        y = float((index // width) % width)
        z = float(index // (width * width))
        rows.append(Point3D(index, x, y, z))
    return tuple(rows)


def run_v3_m9_grouped_stream_partner_case(
    *,
    point_count: int = 2048,
    radius: float = 1.01,
    component_threshold: int = 1,
    warmups: int = 1,
    repeats: int = 3,
    hardware: str = "local_host",
    partners: Sequence[str] = V3_M9_PARTNERS,
    grouped_union_query_block_size: int | None = None,
    grouped_union_direct_side_effect: bool = False,
) -> dict[str, object]:
    compat = _apply_numba_cuda_compat_env()
    validate_v3_public_name(V3_M9_GRAPH_ID, label="M9 graph id")
    if int(warmups) < 0 or int(repeats) <= 0:
        raise GraphValidationError("warmups/repeats are invalid")
    if float(radius) <= 0.0:
        raise GraphValidationError("radius must be positive")
    if int(component_threshold) < 1:
        raise GraphValidationError("component_threshold must be at least 1")
    partner_tuple = tuple(str(partner) for partner in partners)
    if partner_tuple != V3_M9_PARTNERS:
        raise GraphValidationError("M9 grouped-stream partner case requires cupy and numba rows")

    points = make_v3_m9_point_grid_3d(int(point_count))
    rows = []
    signatures = {}
    for partner in partner_tuple:
        row = _run_partner_row(
            partner=partner,
            points=points,
            radius=float(radius),
            component_threshold=int(component_threshold),
            warmups=int(warmups),
            repeats=int(repeats),
            hardware=hardware,
            grouped_union_query_block_size=grouped_union_query_block_size,
            grouped_union_direct_side_effect=bool(grouped_union_direct_side_effect),
            compat_env=compat,
        )
        rows.append(row)
        signatures[partner] = tuple(row["validation_signature"])

    signatures_match = len(set(signatures.values())) == 1
    if not signatures_match:
        raise GraphValidationError("M9 grouped-stream CuPy and Numba signatures differ")

    cupy_row = next(row for row in rows if row["partner"] == "cupy")
    numba_row = next(row for row in rows if row["partner"] == "numba")
    cupy_seconds = float(cupy_row["median_seconds"])
    numba_seconds = float(numba_row["median_seconds"])
    return {
        "version": V3_M9_GROUPED_STREAM_VERSION,
        "status": V3_M9_GROUPED_STREAM_STATUS,
        "graph_id": V3_M9_GRAPH_ID,
        "contract_key": V3_M9_CONTRACT_KEY,
        "parameters": {
            "point_count": int(point_count),
            "radius": float(radius),
            "component_threshold": int(component_threshold),
            "warmups": int(warmups),
            "repeats": int(repeats),
            "grouped_union_query_block_size": grouped_union_query_block_size,
            "grouped_union_direct_side_effect": bool(grouped_union_direct_side_effect),
        },
        "partner_rows": tuple(rows),
        "comparison": {
            "cupy_median_seconds": cupy_seconds,
            "numba_median_seconds": numba_seconds,
            "cupy_over_numba_ratio": cupy_seconds / numba_seconds if numba_seconds > 0 else None,
            "winner": "cupy" if cupy_seconds < numba_seconds else "numba",
            "signature_match": True,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "reason": (
                "This gate measures explicit user-selected CuPy and Numba continuations "
                "over an existing OptiX grouped-stream path. It records device-resident "
                "output pointers, but does not prove same-stream ordering or authorize "
                "public true-zero-copy wording."
            ),
        },
    }


def build_v3_m9_grouped_stream_instrumentation(
    *,
    partner: str,
    hardware: str,
    prepare_seconds: float,
    run_seconds: float,
    native_seconds: float,
    continuation_seconds: float,
    validation_seconds: float,
    data_ptrs: Mapping[str, int],
    metadata: Mapping[str, object],
) -> InstrumentationPacket:
    partner = str(partner)
    if partner not in V3_M9_PARTNERS:
        raise GraphValidationError("M9 instrumentation partner must be cupy or numba")
    native_handle_id = f"{partner}_optix_native_handle_record"
    pointer_id = f"{partner}_device_pointer_record"
    timer_id = f"{partner}_host_timer_record"
    validation_id = f"{partner}_validation_timer_record"
    evidence = (
        EvidenceRecord(
            evidence_id=native_handle_id,
            kind="backend_native_handle",
            backend="optix",
            phase="rt_traversal",
            source="prepared_optix_grouped_stream_metadata",
            hardware=hardware,
            details={
                "native_execution_path": metadata.get("native_execution_path"),
                "native_engine_row_contract": metadata.get("native_engine_row_contract"),
                "partner": partner,
                "rt_core_accelerated_metadata": bool(metadata.get("rt_core_accelerated", False)),
            },
        ),
        EvidenceRecord(
            evidence_id=pointer_id,
            kind="pointer_identity",
            backend="optix",
            phase="stream_handoff",
            source=f"{partner}_device_array_pointer_probe",
            hardware=hardware,
            details={key: int(value) for key, value in data_ptrs.items()},
        ),
        EvidenceRecord(
            evidence_id=timer_id,
            kind="host_timer",
            backend="optix",
            phase="continuation_or_reduction",
            source="python_perf_counter_wrapper",
            hardware=hardware,
            details={
                "run_seconds_median": float(run_seconds),
                "native_seconds_from_metadata": float(native_seconds),
                "continuation_seconds_estimate": float(continuation_seconds),
            },
        ),
        EvidenceRecord(
            evidence_id=validation_id,
            kind="host_timer",
            backend="optix",
            phase="validation",
            source="post_measurement_signature_materialization",
            hardware=hardware,
            details={"validation_seconds": float(validation_seconds)},
        ),
    )
    timings = tuple(
        PhaseTimingRecord(
            phase=phase,
            seconds=_phase_seconds(
                phase,
                prepare_seconds=prepare_seconds,
                run_seconds=run_seconds,
                native_seconds=native_seconds,
                continuation_seconds=continuation_seconds,
                validation_seconds=validation_seconds,
            ),
            backend="optix",
            timing_source=_phase_source(phase),
            evidence_ids=_phase_evidence_ids(
                phase,
                native_handle_id=native_handle_id,
                pointer_id=pointer_id,
                timer_id=timer_id,
                validation_id=validation_id,
            ),
            steady_state_candidate=phase in {"rt_traversal", "stream_handoff", "continuation_or_reduction"},
            setup_candidate=phase in {"prepare", "build", "upload", "query_prepare"},
            materialization_candidate=phase == "download_or_materialization",
        )
        for phase in REQUIRED_PHASE_NAMES
    )
    residency = (
        ResidencyEvidence(
            value_name="component_labels",
            storage="cuda",
            residency="device_resident",
            lifetime="partner_owned",
            stream_ordering="host_synchronized",
            data_ptr_observed=bool(data_ptrs.get("component_labels")),
            backend_handle_observed=True,
            transfer_counter_observed=False,
            host_materialized=False,
            hidden_copy_observed=False,
            evidence_ids=(native_handle_id, pointer_id),
        ),
    )
    return InstrumentationPacket(
        graph_id=V3_M9_GRAPH_ID,
        backend="optix",
        hardware=hardware,
        phase_timings=timings,
        evidence_records=evidence,
        residency_evidence=residency,
    )


def validate_v3_m9_grouped_stream_payload(payload: Mapping[str, object]) -> dict[str, object]:
    if payload.get("version") != V3_M9_GROUPED_STREAM_VERSION:
        raise GraphValidationError("unexpected M9 grouped-stream version")
    if payload.get("status") != V3_M9_GROUPED_STREAM_STATUS:
        raise GraphValidationError("unexpected M9 grouped-stream status")
    rows = tuple(payload.get("partner_rows", ()))
    if len(rows) != 2:
        raise GraphValidationError("M9 grouped-stream payload requires two partner rows")
    partners = {str(row["partner"]) for row in rows if isinstance(row, Mapping)}
    if partners != set(V3_M9_PARTNERS):
        raise GraphValidationError("M9 grouped-stream payload must include cupy and numba")
    comparison = payload.get("comparison", {})
    if not isinstance(comparison, Mapping) or comparison.get("signature_match") is not True:
        raise GraphValidationError("M9 grouped-stream signatures must match")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("M9 grouped-stream payload requires claim boundary")
    for key in (
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "true_zero_copy_public_claim_authorized",
        "automatic_partner_selection_authorized",
    ):
        if bool(boundary.get(key)):
            raise GraphValidationError(f"M9 grouped-stream payload must not authorize {key}")
    return {
        "status": V3_M9_GROUPED_STREAM_STATUS,
        "partner_count": len(rows),
        "signature_match": True,
        "public_claim_authorized": False,
    }


def _run_partner_row(
    *,
    partner: str,
    points: Sequence[object],
    radius: float,
    component_threshold: int,
    warmups: int,
    repeats: int,
    hardware: str,
    grouped_union_query_block_size: int | None,
    grouped_union_direct_side_effect: bool,
    compat_env: Mapping[str, object],
) -> dict[str, object]:
    prepare_start = time.perf_counter()
    prepared = prepare_v2_8_fixed_radius_graph_component_continuation_3d(
        points,
        radius=radius,
        component_threshold=component_threshold,
        backend="optix",
        partner=partner,
        strategy="grouped_stream",
        grouped_union_query_block_size=grouped_union_query_block_size,
        grouped_union_direct_side_effect=grouped_union_direct_side_effect,
    )
    prepare_seconds = time.perf_counter() - prepare_start
    try:
        for _ in range(warmups):
            fixed_radius_graph_component_labels_3d_v2_8(
                prepared,
                component_threshold=component_threshold,
                return_metadata=True,
            )

        samples = []
        native_samples = []
        continuation_samples = []
        last_result = None
        for _ in range(repeats):
            start = time.perf_counter()
            result = fixed_radius_graph_component_labels_3d_v2_8(
                prepared,
                component_threshold=component_threshold,
                return_metadata=True,
            )
            elapsed = time.perf_counter() - start
            metadata = dict(result["metadata"])
            native_seconds = float(
                dict(metadata.get("native_grouped_stream_metadata") or {}).get("native_elapsed_sec", 0.0)
            )
            samples.append(elapsed)
            native_samples.append(native_seconds)
            continuation_samples.append(max(0.0, elapsed - native_seconds))
            last_result = result
        if last_result is None:
            raise GraphValidationError("M9 grouped-stream partner run produced no samples")

        validation_start = time.perf_counter()
        signature = _component_signature_from_columns(last_result["columns"])
        validation_seconds = time.perf_counter() - validation_start
        data_ptrs = _column_data_ptrs(last_result["columns"])
        metadata = dict(last_result["metadata"])
        instrumentation = build_v3_m9_grouped_stream_instrumentation(
            partner=partner,
            hardware=hardware,
            prepare_seconds=prepare_seconds,
            run_seconds=statistics.median(samples),
            native_seconds=statistics.median(native_samples),
            continuation_seconds=statistics.median(continuation_samples),
            validation_seconds=validation_seconds,
            data_ptrs=data_ptrs,
            metadata=metadata,
        )
        return {
            "partner": partner,
            "backend": "optix",
            "samples_seconds": tuple(samples),
            "median_seconds": statistics.median(samples),
            "min_seconds": min(samples),
            "max_seconds": max(samples),
            "prepare_seconds": prepare_seconds,
            "native_seconds_median": statistics.median(native_samples),
            "continuation_seconds_median": statistics.median(continuation_samples),
            "validation_seconds": validation_seconds,
            "validation_signature": signature,
            "device_data_ptrs": data_ptrs,
            "metadata": metadata,
            "numba_cuda_compat_env": dict(compat_env) if partner == "numba" else None,
            "instrumentation": instrumentation.to_metadata(),
            "claim_readiness": instrumentation.claim_readiness,
            "public_claim_authorized": False,
        }
    finally:
        close = getattr(prepared, "close", None)
        if close is not None:
            close()


def _component_signature_from_columns(columns: Mapping[str, object]) -> tuple[int, ...]:
    labels = _column_to_host_ints(columns["component_labels"])
    counts: dict[int, int] = {}
    for label in labels:
        if label < 0:
            continue
        counts[label] = counts.get(label, 0) + 1
    return tuple(sorted(counts.values()))


def _column_to_host_ints(column: object) -> tuple[int, ...]:
    if hasattr(column, "get"):
        values = column.get()
    elif hasattr(column, "copy_to_host"):
        values = column.copy_to_host()
    else:
        values = column
    return tuple(int(value) for value in values)


def _column_data_ptrs(columns: Mapping[str, object]) -> dict[str, int]:
    ptrs = {}
    for key, value in columns.items():
        ptr = _device_pointer(value)
        if ptr:
            ptrs[str(key)] = ptr
    return ptrs


def _device_pointer(value: object) -> int:
    data = getattr(value, "data", None)
    ptr = getattr(data, "ptr", None)
    if ptr is not None:
        return int(ptr)
    device_ctypes_pointer = getattr(value, "device_ctypes_pointer", None)
    ptr_value = getattr(device_ctypes_pointer, "value", None)
    if ptr_value is not None:
        return int(ptr_value)
    cuda_array_interface = getattr(value, "__cuda_array_interface__", None)
    if isinstance(cuda_array_interface, Mapping):
        data_tuple = cuda_array_interface.get("data")
        if isinstance(data_tuple, tuple) and data_tuple:
            return int(data_tuple[0])
    return 0


def _phase_seconds(
    phase: str,
    *,
    prepare_seconds: float,
    run_seconds: float,
    native_seconds: float,
    continuation_seconds: float,
    validation_seconds: float,
) -> float:
    if phase == "prepare":
        return float(prepare_seconds)
    if phase == "rt_traversal":
        return float(native_seconds)
    if phase == "continuation_or_reduction":
        return float(continuation_seconds)
    if phase == "validation":
        return float(validation_seconds)
    if phase == "host_wrapper":
        return float(run_seconds)
    return 0.0


def _phase_source(phase: str) -> str:
    if phase in {"prepare", "rt_traversal", "continuation_or_reduction", "validation", "host_wrapper"}:
        return "host_timer"
    return "metadata_only"


def _phase_evidence_ids(
    phase: str,
    *,
    native_handle_id: str,
    pointer_id: str,
    timer_id: str,
    validation_id: str,
) -> tuple[str, ...]:
    if phase == "rt_traversal":
        return (native_handle_id, timer_id)
    if phase == "stream_handoff":
        return (pointer_id,)
    if phase == "continuation_or_reduction":
        return (timer_id,)
    if phase == "validation":
        return (validation_id,)
    return ()


def _apply_numba_cuda_compat_env() -> dict[str, object]:
    """Prefer a driver-compatible packaged CUDA NVVM for Numba if available."""

    if os.environ.get("RTDL_DISABLE_NUMBA_CUDA_COMPAT") == "1":
        return {"applied": False, "reason": "disabled_by_env"}
    root = _find_packaged_cuda_nvcc_root()
    if root is None:
        return {"applied": False, "reason": "packaged_cuda_nvcc_not_found"}
    nvvm_dir = root / "nvvm" / "lib64"
    bin_dir = root / "bin"
    libnvvm = nvvm_dir / "libnvvm.so"
    if not libnvvm.exists():
        return {"applied": False, "reason": "packaged_libnvvm_not_found", "root": str(root)}
    _prepend_env_path("LD_LIBRARY_PATH", str(nvvm_dir))
    if bin_dir.exists():
        _prepend_env_path("PATH", str(bin_dir))
    os.environ["CUDA_HOME"] = str(root)
    os.environ["NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY"] = "0"
    return {
        "applied": True,
        "cuda_home": str(root),
        "ld_library_path_prefix": str(nvvm_dir),
        "path_prefix": str(bin_dir) if bin_dir.exists() else None,
        "reason": "prefer_packaged_cuda_nvcc_nvvm_for_driver_compatible_ptx",
    }


def _find_packaged_cuda_nvcc_root() -> Path | None:
    spec = importlib.util.find_spec("nvidia.cuda_nvcc")
    locations = getattr(spec, "submodule_search_locations", None) if spec is not None else None
    if locations:
        candidate = Path(tuple(locations)[0])
        if (candidate / "nvvm" / "lib64" / "libnvvm.so").exists():
            return candidate
    fallback = Path("/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc")
    if (fallback / "nvvm" / "lib64" / "libnvvm.so").exists():
        return fallback
    return None


def _prepend_env_path(name: str, value: str) -> None:
    current = os.environ.get(name, "")
    parts = [part for part in current.split(os.pathsep) if part]
    if value in parts:
        parts.remove(value)
    os.environ[name] = os.pathsep.join([value, *parts])
