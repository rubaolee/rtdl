from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtdbscan_chunk_handle_smoke.goal4520.v1"
OUT_JSON = Path("docs/reports/goal4520_v3_0_m124_rtdbscan_chunk_handle_smoke_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4520_v3_0_m124_rtdbscan_chunk_handle_smoke_2026-06-17.md")


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


def _nonzero_label_counts(cupy_array: Any) -> list[int]:
    return [int(value) for value in cupy_array.get().tolist() if int(value)]


def _run_chunk_smoke(cupy, base_columns: dict[str, Any], *, start: int, end: int) -> dict[str, Any]:
    point_columns = {
        name: column[start:end]
        for name, column in base_columns.items()
    }
    prepared = (
        rt.prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_point_columns_preview_3d(
            point_columns,
            radius=0.05,
            cell_factor=0.5,
        )
    )
    repeat_rows = []
    try:
        for repeat_index in range(2):
            predicate_flags = cupy.asarray([1, 1, 1, 0, 0, 0], dtype=cupy.uint32)
            neighbor_counts = cupy.asarray([3, 3, 3, 0, 0, 0], dtype=cupy.uint32)
            start_sec = time.perf_counter()
            result = (
                rt.run_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_union_preview_3d(
                    prepared,
                    predicate_flags=predicate_flags,
                    neighbor_counts=neighbor_counts,
                )
            )
            cupy.cuda.get_current_stream().synchronize()
            repeat_rows.append(
                {
                    "repeat_index": repeat_index,
                    "elapsed_sec": float(time.perf_counter() - start_sec),
                    "metadata_status": result["metadata"]["status"],
                    "handle_reused": bool(result["metadata"]["prepared_predicate_direct_status_union_reused"]),
                    "run_index": int(result["metadata"]["prepared_predicate_direct_status_union_run_index"]),
                    "label_counts_nonzero": _nonzero_label_counts(result["columns"]["label_counts"]),
                    "flag_true_count": int(result["columns"]["flag_true_count"].get()[0]),
                    "negative_label_count": int(result["columns"]["negative_label_count"].get()[0]),
                }
            )
    finally:
        prepared.close()

    metadata = prepared.to_metadata()
    prepare_metadata = metadata["prepare_metadata"]
    x_ptr = int(point_columns["x"].data.ptr)
    base_x_ptr = int(base_columns["x"].data.ptr)
    return {
        "start": int(start),
        "end": int(end),
        "point_count": int(metadata["point_count"]),
        "partition_count": int(metadata["partition_count"]),
        "component_signature_runs": int(metadata["component_signature_runs"]),
        "closed_after_smoke": bool(metadata["closed"]),
        "point_coordinate_upload_avoided": bool(prepare_metadata["point_coordinate_upload_avoided"]),
        "point_coordinate_host_intermediate_tuple_avoided": bool(
            prepare_metadata["point_coordinate_host_intermediate_tuple_avoided"]
        ),
        "point_coordinate_columns_source": prepare_metadata["point_coordinate_columns_source"],
        "pair_materialization_avoided": bool(metadata["pair_materialization_avoided"]),
        "native_abi_added": bool(metadata["native_abi_added"]),
        "x_device_pointer": x_ptr,
        "base_x_device_pointer": base_x_ptr,
        "x_device_pointer_offset_bytes": int(x_ptr - base_x_ptr),
        "expected_x_device_pointer_offset_bytes": int(start * 8),
        "repeat_rows": repeat_rows,
    }


def _validate_chunk(chunk: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if chunk["point_count"] != 6:
        errors.append(f"chunk {chunk['start']} point_count mismatch")
    if chunk["component_signature_runs"] != 2:
        errors.append(f"chunk {chunk['start']} did not reuse handle twice")
    if not chunk["point_coordinate_upload_avoided"]:
        errors.append(f"chunk {chunk['start']} did not avoid coordinate upload")
    if not chunk["point_coordinate_host_intermediate_tuple_avoided"]:
        errors.append(f"chunk {chunk['start']} created a host coordinate tuple")
    if chunk["point_coordinate_columns_source"] != "caller_owned_cupy_device_columns":
        errors.append(f"chunk {chunk['start']} source mismatch")
    if not chunk["pair_materialization_avoided"]:
        errors.append(f"chunk {chunk['start']} materialized pair rows")
    if chunk["native_abi_added"]:
        errors.append(f"chunk {chunk['start']} added native app ABI")
    if chunk["x_device_pointer_offset_bytes"] != chunk["expected_x_device_pointer_offset_bytes"]:
        errors.append(f"chunk {chunk['start']} pointer offset mismatch")
    for row in chunk["repeat_rows"]:
        if row["metadata_status"] != "accept":
            errors.append(f"chunk {chunk['start']} repeat {row['repeat_index']} status mismatch")
        if not row["handle_reused"]:
            errors.append(f"chunk {chunk['start']} repeat {row['repeat_index']} did not reuse handle")
        if row["label_counts_nonzero"] != [3]:
            errors.append(f"chunk {chunk['start']} repeat {row['repeat_index']} label-count mismatch")
        if row["flag_true_count"] != 3:
            errors.append(f"chunk {chunk['start']} repeat {row['repeat_index']} flag-count mismatch")
        if row["negative_label_count"] != 3:
            errors.append(f"chunk {chunk['start']} repeat {row['repeat_index']} negative-count mismatch")
    return errors


def build_packet() -> dict[str, Any]:
    import cupy

    base_columns = _build_base_columns(cupy)
    chunks = [
        _run_chunk_smoke(cupy, base_columns, start=0, end=6),
        _run_chunk_smoke(cupy, base_columns, start=6, end=12),
    ]
    cupy.cuda.get_current_stream().synchronize()
    validation_errors: list[str] = []
    for chunk in chunks:
        validation_errors.extend(_validate_chunk(chunk))

    readiness = rt.assess_v3_chunk_local_prepared_handle_readiness(
        app_id="rt_dbscan",
        contract_key="fixed_radius_compact_status_continuation_v1",
        operation="prepared_graph_partner_continuation",
        item_count=2_000_000,
        max_item_count=65_536,
        whole_dataset_prepared_handle_available=True,
        caller_owned_item_columns_available=True,
        chunk_slice_prepare_api_available=True,
        live_chunk_handle_smoke_validated=not validation_errors,
        prepared_graph_capture_validated=False,
        partner_continuation_explicit=True,
        partner_continuation_associative=True,
        host_materialization_before_partner=False,
    )
    readiness_validation = rt.validate_v3_chunk_local_prepared_handle_readiness(readiness)
    if readiness_validation["blockers"] != ("prepared_graph_capture_not_validated",):
        validation_errors.append("readiness blockers mismatch")

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4520 / V3 M124",
        "status": "rt_dbscan_chunk_handle_live_smoke_validated_graph_capture_blocked",
        "date": "2026-06-17",
        "runtime": {
            "runtime_executed": True,
            "partner": "cupy",
            "device_backend": "cuda",
            "cupy_version": str(cupy.__version__),
            "chunk_count": len(chunks),
            "base_point_count": int(base_columns["x"].size),
            "base_x_device_pointer": int(base_columns["x"].data.ptr),
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
            "m113_promotion_authorized": False,
            "prepared_graph_capture_validated": False,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
        "conclusion": (
            "M124 validates the RT-DBSCAN live chunk-handle smoke that M123 left "
            "open: caller-owned CuPy point-column slices can be prepared as "
            "chunk-local predicate direct-status handles and replayed without "
            "coordinate upload or pair-row materialization. M113 promotion remains "
            "blocked because prepared graph capture is still not validated."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    readiness_validation = packet["validation"]["readiness"]
    lines = [
        "# Goal4520 / V3 M124 RT-DBSCAN Chunk-Handle Smoke",
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
        f"- Base point count: `{packet['runtime']['base_point_count']}`",
        "",
        "## Chunk Smoke",
        "",
        "| Chunk | Points | Runs | Upload avoided | Pointer offset | Label counts |",
        "| --- | ---: | ---: | --- | ---: | --- |",
    ]
    for chunk in packet["chunks"]:
        labels = ",".join(str(value) for value in chunk["repeat_rows"][-1]["label_counts_nonzero"])
        lines.append(
            f"| `{chunk['start']}:{chunk['end']}` | {chunk['point_count']} | "
            f"{chunk['component_signature_runs']} | `{chunk['point_coordinate_upload_avoided']}` | "
            f"{chunk['x_device_pointer_offset_bytes']} | `{labels}` |"
        )
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            f"- API shape ready: `{readiness_validation['api_shape_ready']}`",
            f"- Live chunk-handle smoke validated: `{packet['readiness']['live_chunk_handle_smoke_validated']}`",
            f"- Ready for M113 plan: `{readiness_validation['ready_for_m113_plan']}`",
            f"- Remaining blockers: `{', '.join(readiness_validation['blockers'])}`",
            "",
            "## Boundary",
            "",
            "- This is CuPy runtime handle evidence, not RT-core speedup evidence.",
            "- No current RT-DBSCAN route changed.",
            "- M113 promotion remains blocked until prepared graph capture is validated.",
            "- Automatic partner selection and public speedup wording remain blocked.",
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
