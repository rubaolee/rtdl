from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .aabb_index import prepare_aabb_index_2d


V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE = (
    "v4_aabb_index_query_2d_all_ops_count_prepared_runner"
)
V4_AABB_INDEX_MEASURED_PARTNERS = ("rtdl_native",)
V4_AABB_INDEX_ALLOWED_PARTNERS = V4_AABB_INDEX_MEASURED_PARTNERS
V4_AABB_INDEX_VALIDATED_BACKENDS = ("optix", "embree")


def _require_partner(partner: str) -> str:
    partner = str(partner)
    if partner not in V4_AABB_INDEX_ALLOWED_PARTNERS:
        allowed = ", ".join(V4_AABB_INDEX_ALLOWED_PARTNERS)
        raise ValueError(f"partner must be one of: {allowed}")
    return partner


def _require_backend(backend: str) -> str:
    backend = str(backend)
    if backend not in {"cpu", "embree", "optix", "hiprt"}:
        raise ValueError("backend must be one of: cpu, embree, optix, hiprt")
    return backend


def aabb_index_query_2d_all_ops_count_claim_boundary_v4(
    *,
    partner: str = "rtdl_native",
    backend: str = "optix",
) -> dict[str, object]:
    """Return the V4 claim boundary for the AABB all-ops count surface."""

    partner = _require_partner(partner)
    backend = _require_backend(backend)
    measured_backend = backend in V4_AABB_INDEX_VALIDATED_BACKENDS
    return {
        "v4_api_surface": V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE,
        "partner": partner,
        "backend": backend,
        "measured_partner": partner in V4_AABB_INDEX_MEASURED_PARTNERS,
        "measured_partners": V4_AABB_INDEX_MEASURED_PARTNERS,
        "validated_backends": V4_AABB_INDEX_VALIDATED_BACKENDS,
        "measured_backend": measured_backend,
        "partner_claim_status": (
            "measured_on_v4_goal4636c_pod_optix8_native"
            if measured_backend
            else "cpu_or_unvalidated_backend_correctness_only"
        ),
        "python_box_object_boundary_in_hot_path": False,
        "host_materialization_in_hot_path": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "embedding_c_abi_claim_authorized": False,
        "non_python_host_binding_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


@dataclass
class V4AabbIndexQuery2DAllOpsCountPreparedRunner:
    """Prepared V4 AABB all-ops count session over RTDL native AABB runtime."""

    prepared: Any
    partner: str = "rtdl_native"
    backend: str = "optix"

    def __post_init__(self) -> None:
        self.partner = _require_partner(self.partner)
        self.backend = _require_backend(self.backend)
        self._closed = False

    @property
    def claim_boundary(self) -> dict[str, object]:
        return aabb_index_query_2d_all_ops_count_claim_boundary_v4(
            partner=self.partner,
            backend=self.backend,
        )

    def __enter__(self) -> "V4AabbIndexQuery2DAllOpsCountPreparedRunner":
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

    def run(
        self,
        *,
        point_queries: Iterable[Any] = (),
        box_queries: Iterable[Any] = (),
        return_metadata: bool = True,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("V4 AABB index prepared runner is closed")
        native_result = self.prepared.count(
            point_queries=point_queries,
            box_queries=box_queries,
            operation="all",
        )
        metadata = {
            **self.claim_boundary,
            "adapter": V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE,
            "generic_primitive": "AABB_INDEX_QUERY_2D",
            "input_contract": "caller_supplied_2d_aabb_boxes_and_queries",
            "output_contract": "generic_prepared_aabb_index_query_2d_all_ops_counts",
            "native_prepared_route": "prepare_aabb_index_2d.count(operation='all')",
            "primitive_contract": native_result["contract"],
            "rt_core_accelerated": bool(native_result["rt_core_accelerated"]),
            "native_engine_customization": bool(native_result["native_engine_customization"]),
            "public_speedup_claim_authorized": False,
        }
        result = {
            "counts": native_result["counts"],
            "run_phases": native_result["run_phases"],
            "metadata": metadata,
        }
        if return_metadata:
            return result
        return {"counts": native_result["counts"], "run_phases": native_result["run_phases"]}


def prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4(
    indexed_boxes: Iterable[Any],
    *,
    point_queries_for_bounds: Iterable[Any] = (),
    box_queries_for_bounds: Iterable[Any] = (),
    indexed_ids: Iterable[int] | None = None,
    resolution: int = 32,
    backend: str = "optix",
    partner: str = "rtdl_native",
) -> V4AabbIndexQuery2DAllOpsCountPreparedRunner:
    """Prepare the V4 AABB all-ops count front-door surface."""

    partner = _require_partner(partner)
    backend = _require_backend(backend)
    prepared = prepare_aabb_index_2d(
        indexed_boxes,
        point_queries=point_queries_for_bounds,
        box_queries=box_queries_for_bounds,
        indexed_ids=indexed_ids,
        resolution=resolution,
        backend=backend,
    )
    return V4AabbIndexQuery2DAllOpsCountPreparedRunner(
        prepared=prepared,
        partner=partner,
        backend=backend,
    )


__all__ = [
    "V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE",
    "V4_AABB_INDEX_MEASURED_PARTNERS",
    "V4_AABB_INDEX_ALLOWED_PARTNERS",
    "V4_AABB_INDEX_VALIDATED_BACKENDS",
    "V4AabbIndexQuery2DAllOpsCountPreparedRunner",
    "aabb_index_query_2d_all_ops_count_claim_boundary_v4",
    "prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4",
]
