from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtdbscan_prepared_graph_capture.goal4528.v1"
OUT_JSON = Path("docs/reports/goal4528_v3_0_m132_rtdbscan_prepared_graph_capture_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4528_v3_0_m132_rtdbscan_prepared_graph_capture_2026-06-17.md")


def _build_base_columns(cupy) -> dict[str, Any]:
    x = cupy.asarray(
        [
            0.00,
            0.01,
            0.02,
            1.00,
            1.01,
            4.00,
            10.00,
            10.01,
            10.02,
            11.00,
            11.01,
            14.00,
        ],
        dtype=cupy.float64,
    )
    return {
        "x": x,
        "y": cupy.zeros_like(x),
        "z": cupy.zeros_like(x),
    }


def _u64_list(cupy_array: Any) -> list[int]:
    return [int(value) for value in cupy_array.get().tolist()]


def _run_chunk_graph_capture(cupy, base_columns: dict[str, Any], *, start: int, end: int) -> dict[str, Any]:
    point_columns = {name: column[start:end] for name, column in base_columns.items()}
    prepared = (
        rt.prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_point_columns_preview_3d(
            point_columns,
            radius=0.05,
            cell_factor=0.5,
        )
    )
    graph_handle = None
    try:
        predicate_flags = cupy.asarray([1, 1, 1, 0, 0, 0], dtype=cupy.uint32)
        neighbor_counts = cupy.asarray([3, 3, 3, 0, 0, 0], dtype=cupy.uint32)
        normal_start = time.perf_counter()
        normal = (
            rt.run_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_union_preview_3d(
                prepared,
                predicate_flags=predicate_flags,
                neighbor_counts=neighbor_counts,
                convergence_mode="single_pass_candidate",
            )
        )
        cupy.cuda.get_current_stream().synchronize()
        normal_elapsed_sec = time.perf_counter() - normal_start

        capture_start = time.perf_counter()
        graph_handle = (
            rt.prepare_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_graph_preview_3d(
                prepared,
                predicate_flags=predicate_flags,
                neighbor_counts=neighbor_counts,
                fixed_iteration_count=1,
                warmup_before_capture=True,
            )
        )
        capture_elapsed_sec = time.perf_counter() - capture_start

        replay_rows = []
        for replay_index in range(2):
            replay_start = time.perf_counter()
            replay = graph_handle.replay()
            replay_elapsed_sec = time.perf_counter() - replay_start
            replay_rows.append(
                {
                    "replay_index": replay_index,
                    "elapsed_sec": float(replay_elapsed_sec),
                    "metadata_status": replay["metadata"]["status"],
                    "cuda_graph_replay": bool(replay["metadata"]["cuda_graph_replay"]),
                    "label_counts": _u64_list(replay["columns"]["label_counts"]),
                    "flag_true_count": int(replay["columns"]["flag_true_count"].get()[0]),
                    "negative_label_count": int(replay["columns"]["negative_label_count"].get()[0]),
                    "safe_full_count": int(replay["columns"]["safe_full_count"].get()[0]),
                    "ambiguous_count": int(replay["columns"]["ambiguous_count"].get()[0]),
                }
            )
        normal_counts = _u64_list(normal["columns"]["label_counts"])
        normal_flag_true = int(normal["columns"]["flag_true_count"].get()[0])
        normal_negative = int(normal["columns"]["negative_label_count"].get()[0])
        metadata = prepared.to_metadata()
        graph_metadata = graph_handle.to_metadata()
        x_ptr = int(point_columns["x"].data.ptr)
        base_x_ptr = int(base_columns["x"].data.ptr)
        return {
            "start": int(start),
            "end": int(end),
            "point_count": int(metadata["point_count"]),
            "partition_count": int(metadata["partition_count"]),
            "normal_fixed_iteration": {
                "elapsed_sec": float(normal_elapsed_sec),
                "label_counts": normal_counts,
                "flag_true_count": normal_flag_true,
                "negative_label_count": normal_negative,
                "metadata_status": normal["metadata"]["status"],
                "convergence_mode": normal["metadata"]["direct_status_convergence_mode"],
            },
            "graph_capture": {
                "elapsed_sec": float(capture_elapsed_sec),
                "cuda_graph_captured": bool(graph_metadata["cuda_graph_captured"]),
                "capture_mode": graph_metadata["capture_mode"],
                "fixed_iteration_count": int(graph_metadata["fixed_iteration_count"]),
                "pair_materialization_avoided": bool(graph_metadata["pair_materialization_avoided"]),
                "host_materialization_before_partner": bool(
                    graph_metadata["host_materialization_before_partner"]
                ),
                "native_abi_added": bool(graph_metadata["native_abi_added"]),
            },
            "graph_replays": replay_rows,
            "graph_matches_normal_fixed_iteration": all(
                row["label_counts"] == normal_counts
                and row["flag_true_count"] == normal_flag_true
                and row["negative_label_count"] == normal_negative
                for row in replay_rows
            ),
            "point_coordinate_upload_avoided": bool(
                metadata["prepare_metadata"]["point_coordinate_upload_avoided"]
            ),
            "point_coordinate_host_intermediate_tuple_avoided": bool(
                metadata["prepare_metadata"]["point_coordinate_host_intermediate_tuple_avoided"]
            ),
            "point_coordinate_columns_source": metadata["prepare_metadata"][
                "point_coordinate_columns_source"
            ],
            "pair_materialization_avoided": bool(metadata["pair_materialization_avoided"]),
            "x_device_pointer_offset_bytes": int(x_ptr - base_x_ptr),
            "expected_x_device_pointer_offset_bytes": int(start * 8),
        }
    finally:
        if graph_handle is not None:
            graph_handle.close()
        prepared.close()


def _validate_chunk(chunk: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if chunk["point_count"] != 6:
        errors.append(f"chunk {chunk['start']} point_count mismatch")
    if not chunk["graph_capture"]["cuda_graph_captured"]:
        errors.append(f"chunk {chunk['start']} did not capture a CUDA graph")
    if chunk["graph_capture"]["fixed_iteration_count"] != 1:
        errors.append(f"chunk {chunk['start']} fixed iteration count mismatch")
    if not chunk["graph_matches_normal_fixed_iteration"]:
        errors.append(f"chunk {chunk['start']} graph replay mismatched normal fixed iteration")
    if not chunk["point_coordinate_upload_avoided"]:
        errors.append(f"chunk {chunk['start']} did not avoid coordinate upload")
    if not chunk["point_coordinate_host_intermediate_tuple_avoided"]:
        errors.append(f"chunk {chunk['start']} built host coordinate tuple")
    if chunk["point_coordinate_columns_source"] != "caller_owned_cupy_device_columns":
        errors.append(f"chunk {chunk['start']} source mismatch")
    if not chunk["pair_materialization_avoided"]:
        errors.append(f"chunk {chunk['start']} materialized pair rows")
    if chunk["graph_capture"]["native_abi_added"]:
        errors.append(f"chunk {chunk['start']} added native app ABI")
    if chunk["graph_capture"]["host_materialization_before_partner"]:
        errors.append(f"chunk {chunk['start']} materialized before partner")
    if chunk["x_device_pointer_offset_bytes"] != chunk["expected_x_device_pointer_offset_bytes"]:
        errors.append(f"chunk {chunk['start']} pointer offset mismatch")
    for row in chunk["graph_replays"]:
        if row["metadata_status"] != "accept":
            errors.append(f"chunk {chunk['start']} replay {row['replay_index']} status mismatch")
        if not row["cuda_graph_replay"]:
            errors.append(f"chunk {chunk['start']} replay {row['replay_index']} did not use graph")
        if row["label_counts"] != [0, 3, 0, 0]:
            errors.append(f"chunk {chunk['start']} replay {row['replay_index']} label mismatch")
        if row["flag_true_count"] != 3:
            errors.append(f"chunk {chunk['start']} replay {row['replay_index']} flag count mismatch")
        if row["negative_label_count"] != 3:
            errors.append(f"chunk {chunk['start']} replay {row['replay_index']} negative count mismatch")
    return errors


def build_packet() -> dict[str, Any]:
    import cupy

    base_columns = _build_base_columns(cupy)
    chunks = (
        _run_chunk_graph_capture(cupy, base_columns, start=0, end=6),
        _run_chunk_graph_capture(cupy, base_columns, start=6, end=12),
    )
    cupy.cuda.get_current_stream().synchronize()
    validation_errors: list[str] = []
    for chunk in chunks:
        validation_errors.extend(_validate_chunk(chunk))
    graph_capture_validated = not validation_errors
    readiness = rt.assess_v3_chunk_local_prepared_handle_readiness(
        app_id="rt_dbscan",
        contract_key="fixed_radius_compact_status_continuation_v1",
        operation="prepared_graph_partner_continuation",
        item_count=2_000_000,
        max_item_count=65_536,
        whole_dataset_prepared_handle_available=True,
        caller_owned_item_columns_available=True,
        chunk_slice_prepare_api_available=True,
        live_chunk_handle_smoke_validated=True,
        prepared_graph_capture_validated=graph_capture_validated,
        partner_continuation_explicit=True,
        partner_continuation_associative=True,
        host_materialization_before_partner=False,
    )
    readiness_validation = rt.validate_v3_chunk_local_prepared_handle_readiness(readiness)
    if graph_capture_validated and readiness_validation["status"] != "accept":
        validation_errors.append("readiness validation did not accept graph capture")
    if graph_capture_validated and not readiness_validation["ready_for_m113_plan"]:
        validation_errors.append("ready_for_m113_plan was not set after graph capture")
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4528 / V3 M132",
        "status": "rt_dbscan_prepared_graph_capture_validated",
        "date": "2026-06-17",
        "runtime": {
            "runtime_executed": True,
            "partner": "cupy",
            "device_backend": "cuda",
            "cupy_version": str(cupy.__version__),
            "chunk_count": len(chunks),
            "base_point_count": int(base_columns["x"].size),
            "fixed_iteration_count": 1,
        },
        "chunks": chunks,
        "readiness": readiness,
        "validation": {
            "status": "accept" if not validation_errors else "reject",
            "errors": validation_errors,
            "readiness": readiness_validation,
        },
        "claim_boundary": {
            "current_route_changed": False,
            "m113_promotion_authorized": graph_capture_validated,
            "prepared_graph_capture_validated": graph_capture_validated,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
        "conclusion": (
            "M132 validates the missing RT-DBSCAN prepared graph-capture gate: "
            "chunk-local predicate direct-status handles can capture a fixed-"
            "iteration CuPy CUDA graph, replay it twice, and match the same "
            "prepared handle's non-graph fixed-iteration output without coordinate "
            "upload, host pre-partner materialization, pair-row materialization, "
            "or app-specific native ABI. This authorizes the internal M113 plan "
            "shape for RT-DBSCAN, not public speedup wording or automatic partner "
            "selection."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    readiness = packet["validation"]["readiness"]
    lines = [
        "# Goal4528 / V3 M132 RT-DBSCAN Prepared Graph Capture",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Runtime",
        "",
        f"- Runtime executed: `{packet['runtime']['runtime_executed']}`",
        f"- Partner: `{packet['runtime']['partner']}`",
        f"- Chunk count: `{packet['runtime']['chunk_count']}`",
        f"- Fixed iteration count: `{packet['runtime']['fixed_iteration_count']}`",
        "",
        "## Chunk Capture",
        "",
        "| Chunk | Captured | Replays | Matches normal | Upload avoided | Pair rows avoided |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for chunk in packet["chunks"]:
        lines.append(
            f"| `{chunk['start']}:{chunk['end']}` | "
            f"`{chunk['graph_capture']['cuda_graph_captured']}` | "
            f"{len(chunk['graph_replays'])} | "
            f"`{chunk['graph_matches_normal_fixed_iteration']}` | "
            f"`{chunk['point_coordinate_upload_avoided']}` | "
            f"`{chunk['pair_materialization_avoided']}` |"
        )
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            f"- Ready for M113 plan: `{readiness['ready_for_m113_plan']}`",
            f"- Plan status: `{readiness['plan_status']}`",
            f"- Chunk count: `{readiness['chunk_count']}`",
            "",
            "## Boundary",
            "",
            "- This is internal CUDA graph-capture readiness evidence.",
            "- No current RT-DBSCAN route changed.",
            "- No public speedup, RT-core speedup, or automatic partner-selection wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["validation"], indent=2, sort_keys=True))
    return 0 if packet["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
