from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .aggregate_tree_reference import AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CONTRACT
from .aggregate_tree_reference import AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_NATIVE_ABI_CONTRACT
from .aggregate_tree_reference import AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PRIMITIVE
from .optix_runtime import prepare_aggregate_frontier_device_columns_2d_optix


V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PREPARED_RUNNER_SURFACE = (
    "v4_aggregate_frontier_device_columns_2d_prepared_runner"
)
V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CANDIDATE_STATUS = (
    "candidate_goal4675_local_runner_not_pod_measured"
)
V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_MEASURED_STATUS = (
    "tier2_measured_goal4677_v2_14_host_frontier_bottleneck_no_release"
)
V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_ALLOWED_BACKENDS = ("optix",)
V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_ALLOWED_DOWNSTREAM_PARTNERS = (
    "none",
    "rtdl_native",
    "cupy",
    "numba",
)


def _require_backend(backend: str) -> str:
    backend = str(backend)
    if backend not in V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_ALLOWED_BACKENDS:
        allowed = ", ".join(V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_ALLOWED_BACKENDS)
        raise ValueError(f"backend must be one of: {allowed}")
    return backend


def _require_downstream_partner(partner: str) -> str:
    partner = str(partner)
    if partner not in V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_ALLOWED_DOWNSTREAM_PARTNERS:
        allowed = ", ".join(V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_ALLOWED_DOWNSTREAM_PARTNERS)
        raise ValueError(f"downstream_partner must be one of: {allowed}")
    return partner


def aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4(
    *,
    backend: str = "optix",
    downstream_partner: str = "none",
) -> dict[str, object]:
    """Return the V4 boundary for the aggregate-frontier device-column runner."""

    backend = _require_backend(backend)
    downstream_partner = _require_downstream_partner(downstream_partner)
    return {
        "status": V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_MEASURED_STATUS,
        "v4_api_surface": V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PREPARED_RUNNER_SURFACE,
        "generic_primitive": AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PRIMITIVE,
        "contract": AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CONTRACT,
        "native_abi_contract": AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_NATIVE_ABI_CONTRACT,
        "continuation_class": "aggregate_frontier_device_columns",
        "backend": backend,
        "downstream_partner": downstream_partner,
        "candidate_surface": False,
        "measured_v4_operator_surface": True,
        "measured_v4_release_surface": False,
        "goal4676_pod_measured": True,
        "v2_14_denominator": (
            "RTDL/OptiX aggregate-frontier host/native row collection plus "
            "explicit CuPy or Numba weighted-vector continuation"
        ),
        "v3_0_2_same_route_caveat": (
            "V3.0.2 already has aggregate-frontier device-column symbols; "
            "V4/V3.0.2 parity is not a clean new V4 performance failure or win."
        ),
        "device_resident_frontier_columns_required": True,
        "host_frontier_materialization_before_partner_forbidden": True,
        "goal4676_v4_frontier_only_hot_over_v2_14": 302.9977973413469,
        "goal4676_v4_full_hot_over_v2_14": 310.02390072012497,
        "goal4676_v4_full_wall_over_v2_14": 200.82645806332002,
        "goal4676_v4_full_hot_over_v3_0_2_control": 0.9975684883734833,
        "goal4676_performance_caveat": (
            "measured V2.14 host-frontier bottleneck removal; V4/V3.0.2 is "
            "parity because V3.0.2 already has the same device-column primitive family"
        ),
        "small_host_outputs_allowed": ("row_count", "attempted_count", "overflow", "phase_timings"),
        "app_specific_native_kernel_authorized": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "pod_benchmark_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "old_fused_weighted_vector_sum_promoted": False,
    }


def _metadata_from_frontier_output(frontier_output: Any) -> dict[str, object]:
    to_metadata = getattr(frontier_output, "to_metadata", None)
    if callable(to_metadata):
        metadata = to_metadata()
        if isinstance(metadata, dict):
            return dict(metadata)
    return {}


def _with_runner_metadata(
    frontier_output: Any,
    *,
    backend: str,
    downstream_partner: str,
    source_count: int,
    row_capacity: int,
) -> dict[str, object]:
    frontier_metadata = _metadata_from_frontier_output(frontier_output)
    frontier_columns_materialized_on_host = bool(
        frontier_metadata.get("frontier_columns_materialized_on_host", False)
    )
    row_offsets_materialized_on_host = bool(
        frontier_metadata.get("row_offsets_materialized_on_host", False)
    )
    if frontier_columns_materialized_on_host or row_offsets_materialized_on_host:
        raise RuntimeError(
            "aggregate-frontier device-column runner requires no host frontier "
            "or row-offset materialization before downstream continuation"
        )
    traversal_seconds = frontier_metadata.get("traversal_seconds")
    phase_accounting = {
        "aggregate_frontier_traversal_seconds": traversal_seconds,
        "downstream_partner_seconds": None,
        "host_frontier_materialization_seconds": 0.0,
        "phase_accounting_is_first_class": True,
    }
    metadata = {
        **aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4(
            backend=backend,
            downstream_partner=downstream_partner,
        ),
        "adapter": V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PREPARED_RUNNER_SURFACE,
        "native_prepared_route": "prepare_aggregate_frontier_device_columns_2d_optix",
        "native_run_route": "PreparedOptixAggregateFrontierDeviceColumns2D.run_device_columns",
        "source_count": int(source_count),
        "row_capacity": int(row_capacity),
        "frontier_output_metadata": frontier_metadata,
        "phase_accounting": phase_accounting,
        "frontier_columns_materialized_on_host": frontier_columns_materialized_on_host,
        "row_offsets_materialized_on_host": row_offsets_materialized_on_host,
        "host_materialization_in_hot_path": False,
        "device_resident": bool(frontier_metadata.get("device_resident", False)),
    }
    return metadata


@dataclass
class V4AggregateFrontierDeviceColumns2DPreparedRunner:
    """V4 candidate runner for generic aggregate-frontier device columns."""

    prepared: Any
    backend: str = "optix"
    downstream_partner: str = "none"

    def __post_init__(self) -> None:
        self.backend = _require_backend(self.backend)
        self.downstream_partner = _require_downstream_partner(self.downstream_partner)
        self._closed = False

    @property
    def claim_boundary(self) -> dict[str, object]:
        return aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4(
            backend=self.backend,
            downstream_partner=self.downstream_partner,
        )

    def __enter__(self) -> "V4AggregateFrontierDeviceColumns2DPreparedRunner":
        enter = getattr(self.prepared, "__enter__", None)
        if callable(enter):
            enter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        close = getattr(self.prepared, "close", None)
        if callable(close):
            close()
        self._closed = True

    def run_device_columns(
        self,
        *,
        source_ids_device_ptr: int,
        source_x_device_ptr: int,
        source_y_device_ptr: int,
        source_count: int,
        row_capacity: int,
        source_column_owners: tuple[object, ...] = (),
        return_metadata: bool = True,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("V4 aggregate-frontier device-column runner is closed")
        frontier = self.prepared.run_device_columns(
            source_ids_device_ptr=source_ids_device_ptr,
            source_x_device_ptr=source_x_device_ptr,
            source_y_device_ptr=source_y_device_ptr,
            source_count=source_count,
            row_capacity=row_capacity,
            source_column_owners=source_column_owners,
        )
        metadata = _with_runner_metadata(
            frontier,
            backend=self.backend,
            downstream_partner=self.downstream_partner,
            source_count=source_count,
            row_capacity=row_capacity,
        )
        result = {
            "frontier": frontier,
            "frontier_metadata": metadata["frontier_output_metadata"],
            "phase_accounting": metadata["phase_accounting"],
        }
        if return_metadata:
            result["metadata"] = metadata
        return result

    def run_cupy(
        self,
        source_points: Iterable[object],
        *,
        row_capacity: int | None = None,
        return_metadata: bool = True,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("V4 aggregate-frontier device-column runner is closed")
        frontier = self.prepared.run_cupy(source_points, row_capacity=row_capacity)
        frontier_metadata = _metadata_from_frontier_output(frontier)
        source_count = int(frontier_metadata.get("source_count", 0))
        capacity = int(frontier_metadata.get("capacity", 0 if row_capacity is None else row_capacity))
        metadata = _with_runner_metadata(
            frontier,
            backend=self.backend,
            downstream_partner=self.downstream_partner,
            source_count=source_count,
            row_capacity=capacity,
        )
        result = {
            "frontier": frontier,
            "frontier_metadata": metadata["frontier_output_metadata"],
            "phase_accounting": metadata["phase_accounting"],
        }
        if return_metadata:
            result["metadata"] = metadata
        return result


def prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4(
    tree_nodes: Iterable[object],
    *,
    theta: float,
    deduplicate_fallback_targets: bool = True,
    backend: str = "optix",
    downstream_partner: str = "none",
) -> V4AggregateFrontierDeviceColumns2DPreparedRunner:
    """Prepare the V4 aggregate-frontier device-column candidate runner."""

    backend = _require_backend(backend)
    downstream_partner = _require_downstream_partner(downstream_partner)
    prepared = prepare_aggregate_frontier_device_columns_2d_optix(
        tree_nodes,
        theta=theta,
        deduplicate_fallback_targets=deduplicate_fallback_targets,
    )
    return V4AggregateFrontierDeviceColumns2DPreparedRunner(
        prepared=prepared,
        backend=backend,
        downstream_partner=downstream_partner,
    )


__all__ = [
    "V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PREPARED_RUNNER_SURFACE",
    "V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CANDIDATE_STATUS",
    "V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_MEASURED_STATUS",
    "V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_ALLOWED_BACKENDS",
    "V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_ALLOWED_DOWNSTREAM_PARTNERS",
    "V4AggregateFrontierDeviceColumns2DPreparedRunner",
    "aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4",
    "prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4",
]
