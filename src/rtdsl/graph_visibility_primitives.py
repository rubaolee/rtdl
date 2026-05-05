from __future__ import annotations

from copy import deepcopy
from typing import Any


ACTIVE_V1_4_BACKENDS = ("embree", "optix")


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
    payload["primitive_contract"] = visibility_edges_primitive_contract(
        backend=backend,
        output_mode=output_mode,
        prepared_summary=prepared_summary,
    )
    return payload
