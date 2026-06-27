from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .optix_runtime import OPTIX_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_PREPARED_LEFT_EXECUTOR_DESTROY_SYMBOL
from .optix_runtime import OPTIX_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_PREPARED_LEFT_EXECUTOR_PREPARE_SYMBOL
from .optix_runtime import OPTIX_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_PREPARED_LEFT_EXECUTOR_RUN_SYMBOL
from .optix_runtime import prepare_shape_pair_relation_flags_optix
from .optix_runtime import prepare_shape_pair_relation_left_set_optix


V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_SURFACE = (
    "v4_shape_pair_relation_active_count_2d_prepared_left_executor"
)
V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_STATUS = (
    "goal4680_local_static_gate_not_pod_measured"
)
V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_OPERATOR = (
    "SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR"
)


def shape_pair_relation_active_count_2d_prepared_left_executor_claim_boundary_v4(
    *,
    backend: str = "optix",
) -> dict[str, object]:
    """Return the V4 local/static boundary for generic shape-pair active count."""

    if backend != "optix":
        raise ValueError("backend must be optix")
    return {
        "status": V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_STATUS,
        "v4_api_surface": V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_SURFACE,
        "generic_primitive": V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_OPERATOR,
        "continuation_class": "relation_topology_active_count",
        "backend": backend,
        "candidate_surface": False,
        "measured_v4_operator_surface": False,
        "measured_v4_release_surface": False,
        "goal4680_static_gate_passed": True,
        "goal4681_pod_measured": False,
        "v2_14_same_primitive_existed": True,
        "v2_14_denominator": (
            "strongest V2.14 prepared shape-pair active-count route, including "
            "prepared-left executor/device-continuation mode when available"
        ),
        "same_primitive_speed_credit_requires_material_improvement": True,
        "native_prepare_symbol": (
            OPTIX_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_PREPARED_LEFT_EXECUTOR_PREPARE_SYMBOL
        ),
        "native_run_symbol": (
            OPTIX_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_PREPARED_LEFT_EXECUTOR_RUN_SYMBOL
        ),
        "native_destroy_symbol": (
            OPTIX_SHAPE_PAIR_RELATION_ACTIVE_DEVICE_PREPARED_LEFT_EXECUTOR_DESTROY_SYMBOL
        ),
        "row_stream_materialized_in_hot_path": False,
        "device_resident_query_stream_required": True,
        "small_host_outputs_allowed": ("active_count", "phase_timings", "executor_metadata"),
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
        "partner_migration_counts_as_speed": False,
    }


def _executor_metadata(executor: Any) -> dict[str, object]:
    to_metadata = getattr(executor, "to_metadata", None)
    if callable(to_metadata):
        metadata = to_metadata()
        if isinstance(metadata, dict):
            return dict(metadata)
    return {}


def _last_phase_timings(prepared_relation: Any) -> dict[str, object] | None:
    last_phase_timings = getattr(prepared_relation, "last_phase_timings", None)
    if callable(last_phase_timings):
        timings = last_phase_timings()
        if isinstance(timings, dict):
            return dict(timings)
    return None


@dataclass
class V4ShapePairRelationActiveCount2DPreparedLeftExecutor:
    """Local/static V4 wrapper for generic prepared-left active-count executor."""

    prepared_relation: Any
    prepared_left: Any
    executor: Any
    backend: str = "optix"

    def __post_init__(self) -> None:
        if self.backend != "optix":
            raise ValueError("backend must be optix")
        self._closed = False

    @property
    def claim_boundary(self) -> dict[str, object]:
        return shape_pair_relation_active_count_2d_prepared_left_executor_claim_boundary_v4(
            backend=self.backend,
        )

    def close(self) -> None:
        if self._closed:
            return
        for owner in (self.executor, self.prepared_left, self.prepared_relation):
            close = getattr(owner, "close", None)
            if callable(close):
                close()
        self._closed = True

    def __enter__(self) -> "V4ShapePairRelationActiveCount2DPreparedLeftExecutor":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def run(self, *, return_metadata: bool = True) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("V4 shape-pair relation active-count executor is closed")
        active_count = int(self.executor.run())
        executor_metadata = _executor_metadata(self.executor)
        if executor_metadata.get("row_stream_materialized") is True:
            raise RuntimeError(
                "shape-pair relation active-count V4 gate forbids hot-path row-stream materialization"
            )
        phase_timings = _last_phase_timings(self.prepared_relation)
        result = {
            "active_count": active_count,
            "phase_timings": phase_timings,
            "executor_metadata": executor_metadata,
        }
        if return_metadata:
            result["metadata"] = {
                **self.claim_boundary,
                "active_count": active_count,
                "phase_timings": phase_timings,
                "executor_metadata": executor_metadata,
                "host_materialization_in_hot_path": False,
                "runtime_executed": True,
            }
        return result


def prepare_shape_pair_relation_active_count_2d_prepared_left_executor_v4(
    right_polygons: Iterable[object],
    left_polygons: Iterable[object],
    *,
    backend: str = "optix",
) -> V4ShapePairRelationActiveCount2DPreparedLeftExecutor:
    """Prepare the V4 local/static gate wrapper for generic active-count queries."""

    if backend != "optix":
        raise ValueError("backend must be optix")
    prepared_relation = prepare_shape_pair_relation_flags_optix(right_polygons)
    prepared_left = prepare_shape_pair_relation_left_set_optix(left_polygons)
    executor = prepared_relation.prepare_active_count_prepared_left_executor(prepared_left)
    return V4ShapePairRelationActiveCount2DPreparedLeftExecutor(
        prepared_relation=prepared_relation,
        prepared_left=prepared_left,
        executor=executor,
        backend=backend,
    )


__all__ = [
    "V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_OPERATOR",
    "V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_STATUS",
    "V4_SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR_SURFACE",
    "V4ShapePairRelationActiveCount2DPreparedLeftExecutor",
    "prepare_shape_pair_relation_active_count_2d_prepared_left_executor_v4",
    "shape_pair_relation_active_count_2d_prepared_left_executor_claim_boundary_v4",
]
