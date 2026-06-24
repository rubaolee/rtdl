from __future__ import annotations

from typing import Any, Mapping


TOPOLOGY_STREAM_PHASE_ACCOUNTING_CONTRACT = "topology_stream_phase_accounting_v1"
TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT = "topology_stream_m3_phase_table_v1"
TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT = "topology_stream_prepared_handle_v1"
TOPOLOGY_STREAM_PUBLIC_ROW_STATUS = "internal_accounting_not_public_row"
TOPOLOGY_STREAM_M3_PHASES = (
    "static_scene_prepare_sec",
    "query_stream_prepare_sec",
    "device_transfer_or_residency_sec",
    "rt_traversal_sec",
    "topology_continuation_sec",
    "host_return_or_scalar_materialization_sec",
)
TOPOLOGY_STREAM_MISSING_M3_PHASES = TOPOLOGY_STREAM_M3_PHASES


def build_topology_stream_phase_accounting(
    *,
    backend: str,
    output_contract: str,
    query_count: int,
    wall_sec: float,
    native_traversal_sec: float | None,
    repeat: int,
    warmup: int,
    timer_basis: str,
) -> dict[str, Any]:
    """Describe visible topology-stream timing phases without authorizing a claim."""

    normalized_backend = backend.strip().lower().replace("-", "_")
    wall = float(wall_sec)
    native = None if native_traversal_sec is None else float(native_traversal_sec)
    visible_overhead = None if native is None else max(0.0, wall - native)
    native_fraction = None if native is None or wall <= 0.0 else native / wall
    overhead_fraction = None if visible_overhead is None or wall <= 0.0 else visible_overhead / wall
    payload = {
        "contract": TOPOLOGY_STREAM_PHASE_ACCOUNTING_CONTRACT,
        "status": TOPOLOGY_STREAM_PUBLIC_ROW_STATUS,
        "backend": normalized_backend,
        "output_contract": output_contract,
        "query_count": int(query_count),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "timer_basis": timer_basis,
        "wall_sec": wall,
        "native_traversal_sec": native,
        "visible_non_traversal_overhead_sec": visible_overhead,
        "native_traversal_fraction_of_wall": native_fraction,
        "visible_non_traversal_overhead_fraction_of_wall": overhead_fraction,
        "full_m3_phase_table_complete": False,
        "missing_m3_phases_for_public_row": TOPOLOGY_STREAM_MISSING_M3_PHASES,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }
    validate_topology_stream_phase_accounting(payload)
    return payload


def compare_topology_stream_accounting(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    validate_topology_stream_phase_accounting(baseline)
    validate_topology_stream_phase_accounting(candidate)
    return {
        "baseline_backend": baseline["backend"],
        "candidate_backend": candidate["backend"],
        "candidate_over_baseline_wall_speedup": _speedup(
            float(baseline["wall_sec"]),
            float(candidate["wall_sec"]),
        ),
        "candidate_over_baseline_native_traversal_speedup": _speedup(
            _maybe_float(baseline["native_traversal_sec"]),
            _maybe_float(candidate["native_traversal_sec"]),
        ),
        "candidate_visible_overhead_sec": candidate["visible_non_traversal_overhead_sec"],
        "candidate_visible_overhead_fraction_of_wall": candidate[
            "visible_non_traversal_overhead_fraction_of_wall"
        ],
        "public_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
    }


def compare_author_timer_to_topology_stream(
    *,
    author_label: str,
    author_query_sec: float,
    rtdl_accounting: Mapping[str, Any],
    author_timer_basis: str,
) -> dict[str, Any]:
    validate_topology_stream_phase_accounting(rtdl_accounting)
    author_sec = float(author_query_sec)
    wall_sec = float(rtdl_accounting["wall_sec"])
    native_sec = _maybe_float(rtdl_accounting["native_traversal_sec"])
    return {
        "author_label": author_label,
        "author_timer_basis": author_timer_basis,
        "rtdl_backend": rtdl_accounting["backend"],
        "rtdl_timer_basis": rtdl_accounting["timer_basis"],
        "author_query_sec": author_sec,
        "author_speedup_vs_rtdl_wall": _speedup(wall_sec, author_sec),
        "author_speedup_vs_rtdl_native_traversal": _speedup(native_sec, author_sec),
        "mixed_timing_basis": True,
        "rtdl_beats_author_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "public_speedup_claim_authorized": False,
    }


def build_topology_stream_m3_phase_table(
    *,
    phases_sec: Mapping[str, Any],
    native_phase_timings: Mapping[str, Any] | None,
    output_contract: str,
    query_count: int,
    repeat: int,
    warmup: int,
    query_stream_resident: bool,
    table_basis: str,
) -> dict[str, Any]:
    """Normalize prepared topology-stream timings into the V3 M3 phase shape.

    The table is deliberately non-authorizing: it can make missing or present
    phases machine-checkable, but it does not turn a route into an M7 row.
    """

    native = dict(native_phase_timings or {})
    static_scene = _sum_present(
        phases_sec,
        (
            "static_shape_pack_sec",
            "static_segment_pack_sec",
            "prepare_static_scene_sec",
        ),
    )
    query_stream = _sum_present(
        phases_sec,
        (
            "left_shape_pack_sec",
            "query_point_order_sec",
            "query_pack_sec",
            "prepare_query_points_sec",
            "prepare_left_set_sec",
            "prepared_left_set_sec",
            "prepare_batch_executor_sec",
            "prepare_active_count_executor_sec",
            "prepare_exact_scalar_count_executor_sec",
            "prepare_relation_status_corrected_scalar_count_executor_sec",
        ),
    )
    device_transfer = _first_present(
        native,
        ("point_upload", "left_upload", "row_offset_upload"),
    )
    if device_transfer is None and query_stream_resident:
        device_transfer = 0.0

    candidate_write_as_traversal = _candidate_write_pass_is_traversal(native)
    traversal_keys = ["native_query_sec", "traversal", "candidate_count_pass"]
    if candidate_write_as_traversal:
        traversal_keys.append("candidate_write_pass")
    traversal = _sum_present(native, tuple(traversal_keys))
    continuation_keys = ["exact_refine", "containment", "active_scan"]
    if not candidate_write_as_traversal:
        continuation_keys.insert(0, "candidate_write_pass")
    continuation = _sum_present(native, tuple(continuation_keys))
    if continuation is None:
        continuation = _sum_present(
            phases_sec,
            (
                "boundary_event_device_columns_sec",
                "boundary_event_grouped_count_sec",
            ),
        )
    host_return = _sum_present(
        native,
        (
            "candidate_download",
            "flag_download",
            "count_download",
            "row_download",
        ),
    )
    # A prepared-query marker plus no download timings means the hot path kept
    # the result device-resident until scalar/summary materialization.
    if host_return is None and _phase_value(phases_sec, "prepared_query_sec") is not None:
        host_return = 0.0

    phase_values = {
        "static_scene_prepare_sec": static_scene,
        "query_stream_prepare_sec": query_stream,
        "device_transfer_or_residency_sec": device_transfer,
        "rt_traversal_sec": traversal,
        "topology_continuation_sec": continuation,
        "host_return_or_scalar_materialization_sec": host_return,
    }
    missing = tuple(phase for phase, value in phase_values.items() if value is None)
    normalized_values = {
        phase: (None if value is None else float(value))
        for phase, value in phase_values.items()
    }
    table = {
        "contract": TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT,
        "status": "complete_non_authorizing_m3_table" if not missing else "partial_m3_table_not_public_row",
        "output_contract": output_contract,
        "query_count": int(query_count),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "table_basis": table_basis,
        "query_stream_resident": bool(query_stream_resident),
        "phase_seconds": normalized_values,
        "full_m3_phase_table_complete": not missing,
        "missing_m3_phases_for_public_row": missing,
        "source_phase_keys": {
            "app_phases_sec": sorted(str(key) for key in phases_sec.keys()),
            "native_phase_timings": sorted(str(key) for key in native.keys()),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "true_zero_copy_claim_authorized": False,
    }
    validate_topology_stream_m3_phase_table(table)
    return table


def build_topology_stream_prepared_handle_metadata(
    *,
    backend: str,
    generic_capability: str,
    output_contract: str,
    query_count: int,
    static_scene_prepared: bool,
    query_stream_prepared: bool,
    query_stream_residency: str,
    m3_phase_table: Mapping[str, Any],
) -> dict[str, Any]:
    validate_topology_stream_m3_phase_table(m3_phase_table)
    payload = {
        "contract": TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT,
        "status": "prepared_topology_stream_handle_non_authorizing",
        "backend": backend.strip().lower().replace("-", "_"),
        "generic_capability": generic_capability,
        "output_contract": output_contract,
        "query_count": int(query_count),
        "static_scene_prepared": bool(static_scene_prepared),
        "query_stream_prepared": bool(query_stream_prepared),
        "query_stream_residency": query_stream_residency,
        "full_m3_phase_table_complete": bool(m3_phase_table["full_m3_phase_table_complete"]),
        "reusable_engine_surface": True,
        "app_specific_native_engine_logic_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_claim_authorized": False,
    }
    validate_topology_stream_prepared_handle_metadata(payload)
    return payload


def validate_topology_stream_m3_phase_table(payload: Mapping[str, Any]) -> None:
    if payload.get("contract") != TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT:
        raise ValueError("topology stream M3 phase table contract mismatch")
    if bool(payload.get("release_authorized")):
        raise ValueError("topology stream M3 table cannot authorize release")
    if bool(payload.get("public_speedup_claim_authorized")):
        raise ValueError("topology stream M3 table cannot authorize public speedup")
    if bool(payload.get("row_scoped_public_speedup_claim_authorized")):
        raise ValueError("topology stream M3 table cannot authorize row-scoped public speedup")
    if bool(payload.get("m7_promotion_authorized")):
        raise ValueError("topology stream M3 table cannot authorize M7 promotion")
    if bool(payload.get("true_zero_copy_claim_authorized")):
        raise ValueError("topology stream M3 table cannot authorize true zero-copy")
    phase_seconds = payload.get("phase_seconds")
    if not isinstance(phase_seconds, Mapping):
        raise ValueError("topology stream M3 table needs phase_seconds")
    for phase in TOPOLOGY_STREAM_M3_PHASES:
        if phase not in phase_seconds:
            raise ValueError(f"topology stream M3 table missing {phase}")
        value = phase_seconds[phase]
        if value is not None and float(value) < 0.0:
            raise ValueError(f"topology stream M3 phase {phase} must be non-negative")
    missing = tuple(payload.get("missing_m3_phases_for_public_row", ()))
    complete = bool(payload.get("full_m3_phase_table_complete"))
    if complete and missing:
        raise ValueError("complete topology stream M3 table cannot list missing phases")
    if not complete and not missing:
        raise ValueError("partial topology stream M3 table must list missing phases")


def validate_topology_stream_prepared_handle_metadata(payload: Mapping[str, Any]) -> None:
    if payload.get("contract") != TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT:
        raise ValueError("topology stream prepared handle contract mismatch")
    if bool(payload.get("app_specific_native_engine_logic_allowed")):
        raise ValueError("topology stream prepared handle cannot allow app-specific native logic")
    for key in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "row_scoped_public_speedup_claim_authorized",
        "m7_promotion_authorized",
        "true_zero_copy_claim_authorized",
        "v4_embedding_claim_authorized",
    ):
        if bool(payload.get(key)):
            raise ValueError(f"topology stream prepared handle cannot authorize {key}")


def validate_topology_stream_phase_accounting(payload: Mapping[str, Any]) -> None:
    if payload.get("contract") != TOPOLOGY_STREAM_PHASE_ACCOUNTING_CONTRACT:
        raise ValueError("topology stream accounting contract mismatch")
    if bool(payload.get("release_authorized")):
        raise ValueError("topology stream accounting cannot authorize release")
    if bool(payload.get("public_speedup_claim_authorized")):
        raise ValueError("topology stream accounting cannot authorize public speedup")
    if bool(payload.get("m7_promotion_authorized")):
        raise ValueError("topology stream accounting cannot authorize M7 promotion")
    if float(payload.get("wall_sec", 0.0)) <= 0.0:
        raise ValueError("topology stream wall_sec must be positive")
    native = payload.get("native_traversal_sec")
    if native is not None and float(native) <= 0.0:
        raise ValueError("native_traversal_sec must be positive when present")
    missing = tuple(payload.get("missing_m3_phases_for_public_row", ()))
    if not missing:
        raise ValueError("public-row missing M3 phases must be explicit")


def _maybe_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _phase_value(values: Mapping[str, Any], key: str) -> float | None:
    if key not in values:
        return None
    value = values[key]
    if value is None:
        return None
    return float(value)


def _sum_present(values: Mapping[str, Any], keys: tuple[str, ...]) -> float | None:
    present = [_phase_value(values, key) for key in keys if _phase_value(values, key) is not None]
    if not present:
        return None
    return float(sum(present))


def _first_present(values: Mapping[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = _phase_value(values, key)
        if value is not None:
            return value
    return None


def _candidate_write_pass_is_traversal(native: Mapping[str, Any]) -> bool:
    """Return true when native PIP exact count stores traversal in write-pass timing."""

    if _phase_value(native, "candidate_write_pass") is None:
        return False
    mode = str(native.get("mode", "")).lower()
    if "prepared_points_exact_count" in mode:
        return True
    if "exact_prepared_points" in mode:
        return True
    count_pass = _phase_value(native, "candidate_count_pass")
    has_exact_or_download = (
        _phase_value(native, "exact_refine") is not None
        or _phase_value(native, "candidate_download") is not None
    )
    return (count_pass is None or count_pass == 0.0) and has_exact_or_download


def _speedup(baseline_sec: float | None, candidate_sec: float | None) -> float | None:
    if baseline_sec is None or candidate_sec is None:
        return None
    if baseline_sec <= 0.0 or candidate_sec <= 0.0:
        return None
    return float(baseline_sec) / float(candidate_sec)
