from __future__ import annotations

from copy import deepcopy
from typing import Any

from .generic_primitives import run_generic_prepared_ray_triangle_any_hit_count


ACTIVE_V1_4_BACKENDS = ("embree", "optix")


def _backend_contract_role(backend: str) -> str:
    if backend == "embree":
        return "cpu_rt_baseline_and_fallback"
    if backend == "optix":
        return "nvidia_rt_target"
    return "compatibility_or_inactive"


def visibility_edges_primitive_contract(
    *,
    backend: str,
    output_mode: str,
    prepared_summary: bool,
) -> dict[str, Any]:
    """Return v1.4 compatibility metadata for graph visibility edges."""
    normalized_backend = backend.lower().replace("-", "_")
    return {
        "app_row": "graph_analytics.visibility_edges",
        "primitive": "ANY_HIT",
        "summary_primitive": "COUNT_HITS" if output_mode == "summary" else "not_applicable",
        "alternate_summary_primitive": "REDUCE_INT(COUNT)" if output_mode == "summary" else "not_applicable",
        "backend": normalized_backend,
        "backend_scope": ACTIVE_V1_4_BACKENDS,
        "active_v1_4_backend": normalized_backend in ACTIVE_V1_4_BACKENDS,
        "backend_contract_role": _backend_contract_role(normalized_backend),
        "same_contract_baseline_required": normalized_backend in ACTIVE_V1_4_BACKENDS,
        "mode": "prepared" if prepared_summary else "one_shot",
        "build_layout": "triangle2d_blocker_buffer",
        "probe_layout": "visibility_ray2d_probe_buffer",
        "result_layout": (
            "aggregate_visible_blocked_counts" if output_mode == "summary" else "per_edge_visibility_rows"
        ),
        "prepared_state": (
            "build_geometry_and_probe_rays_reusable"
            if prepared_summary
            else "none_required_for_row_materialization"
        ),
        "phase_counters": (
            "input_construction_sec",
            "blocker_pack_sec",
            "ray_pack_sec",
            "scene_prepare_sec",
            "ray_prepare_sec",
            "query_anyhit_count_sec",
            "query_visibility_pair_rows_sec",
            "summary_postprocess_sec",
        ),
        "claim_boundary": (
            "graph_analytics.visibility_edges only: candidate graph edges lowered "
            "to ray/triangle any-hit and optional aggregate count. This excludes "
            "BFS, triangle counting, shortest path, graph databases, frontier "
            "bookkeeping, and graph reductions."
        ),
        "migration_status": "compatibility_wrapper_metadata_only",
    }


def attach_visibility_edges_primitive_contract(
    section: dict[str, Any],
    *,
    backend: str,
    output_mode: str,
    prepared_summary: bool,
) -> dict[str, Any]:
    """Attach v1.4 primitive metadata without mutating the caller's payload."""
    payload = deepcopy(section)
    contract = visibility_edges_primitive_contract(
        backend=backend,
        output_mode=output_mode,
        prepared_summary=prepared_summary,
    )
    from .primitive_contract_schema import validate_primitive_contract

    validate_primitive_contract(contract)
    payload["primitive_contract"] = contract
    return payload


def run_prepared_visibility_anyhit_count(
    *,
    blockers: Any,
    rays: Any,
    prepare_scene,
    prepare_rays,
    visibility_query_repeats: int,
) -> dict[str, Any]:
    """Run the prepared `ANY_HIT` plus aggregate count compatibility wrapper."""
    result = run_generic_prepared_ray_triangle_any_hit_count(
        triangles=blockers,
        rays=rays,
        backend="optix",
        query_repeats=visibility_query_repeats,
        prepare_scene=prepare_scene,
        prepare_rays=prepare_rays,
    )
    return {
        "blocked_count": int(result["hit_count"]),
        "run_phases": result["run_phases"],
    }
