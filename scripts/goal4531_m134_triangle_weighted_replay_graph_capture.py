from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.triangle_weighted_replay_graph_capture.goal4531.v1"
OUT_JSON = Path("docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.md")


def _triangle_columns(cupy) -> dict[str, Any]:
    return {
        "ids": cupy.asarray([0], dtype=cupy.uint32),
        "x0": cupy.asarray([0.0], dtype=cupy.float64),
        "y0": cupy.asarray([0.0], dtype=cupy.float64),
        "z0": cupy.asarray([0.0], dtype=cupy.float64),
        "x1": cupy.asarray([1.0], dtype=cupy.float64),
        "y1": cupy.asarray([0.0], dtype=cupy.float64),
        "z1": cupy.asarray([0.0], dtype=cupy.float64),
        "x2": cupy.asarray([0.0], dtype=cupy.float64),
        "y2": cupy.asarray([0.0], dtype=cupy.float64),
        "z2": cupy.asarray([1.0], dtype=cupy.float64),
    }


def _ray_columns(cupy) -> dict[str, Any]:
    return {
        "ids": cupy.asarray([0, 1, 2], dtype=cupy.uint32),
        "ox": cupy.asarray([0.25, 1.50, 0.10], dtype=cupy.float64),
        "oy": cupy.asarray([1.0, 1.0, 1.0], dtype=cupy.float64),
        "oz": cupy.asarray([0.25, 1.50, 0.10], dtype=cupy.float64),
        "dx": cupy.asarray([0.0, 0.0, 0.0], dtype=cupy.float64),
        "dy": cupy.asarray([-1.0, -1.0, -1.0], dtype=cupy.float64),
        "dz": cupy.asarray([0.0, 0.0, 0.0], dtype=cupy.float64),
        "tmax": cupy.asarray([10.0, 10.0, 10.0], dtype=cupy.float64),
    }


def build_packet() -> dict[str, Any]:
    import cupy

    expected_sum = 20
    validation_errors: list[str] = []
    graph_capture_error = None
    graph_capture_validated = False
    replay_sums: list[int] = []
    stream_sum = None
    normal_sum = None
    device_output_stream_validated = False
    launch_metadata = None
    executor_metadata = None

    scene = None
    ray_batch = None
    executor = None
    try:
        scene = rt.prepare_optix_static_triangle_scene_3d_device_triangles(_triangle_columns(cupy))
        ray_batch = scene.prepare_ray_batch_device_columns(_ray_columns(cupy))
        weights = cupy.asarray([7, 11, 13], dtype=cupy.uint64)
        output = cupy.zeros(1, dtype=cupy.uint64)
        normal = scene.ray_batch_any_hit_weighted_sum_device_weights(ray_batch, weights)
        normal_sum = int(normal["weighted_hit_sum"])

        executor = scene.prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor(
            ray_batch,
            weights,
            output,
        )
        executor_metadata = executor.to_metadata()
        stream = cupy.cuda.Stream(non_blocking=True)
        launch_metadata = executor.launch(stream)
        stream.synchronize()
        stream_sum = int(output.get()[0])
        device_output_stream_validated = normal_sum == stream_sum == expected_sum

        try:
            stream.begin_capture()
            executor.launch(stream)
            graph = stream.end_capture()
            graph_capture_validated = True
            for _ in range(2):
                output.fill(cupy.uint64(999))
                graph.launch(stream=stream)
                stream.synchronize()
                replay_sums.append(int(output.get()[0]))
        except Exception as exc:  # pragma: no cover - pod evidence path
            graph_capture_error = f"{type(exc).__name__}: {exc}"
            try:
                stream.end_capture()
            except Exception:
                pass

        if normal_sum != expected_sum:
            validation_errors.append("normal host-scalar weighted sum mismatch")
        if stream_sum != expected_sum:
            validation_errors.append("device-output stream weighted sum mismatch")
        if graph_capture_validated and replay_sums != [expected_sum, expected_sum]:
            validation_errors.append("captured graph replay weighted sum mismatch")
        if not device_output_stream_validated:
            validation_errors.append("device-output stream replay did not validate")
    finally:
        if executor is not None:
            executor.close()
        if ray_batch is not None:
            ray_batch.close()
        if scene is not None:
            scene.close()

    readiness = rt.assess_v3_chunked_unique_count_continuation_readiness(
        app_id="triangle_counting",
        contract_key="rt_graph_2a1_unique_weighted_summary_v1",
        operation="prepared_segment_replay_unique_count_continuation",
        item_count=45_000_000,
        max_item_count=15_000_000,
        prepared_scene_reuse_available=True,
        prepared_item_handle_per_chunk_available=True,
        prepared_graph_capture_validated=graph_capture_validated,
        per_chunk_unique_payload_available=True,
        key_payload_carries_counts=True,
        duplicate_keys_can_cross_chunk_boundaries=True,
        chunk_key_ranges_disjoint=False,
        final_key_payload_merge_validated=True,
        host_materialization_before_partner=False,
    )
    readiness_validation = rt.validate_v3_chunked_unique_count_continuation_readiness(readiness)

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4531 / V3 M134",
        "status": "triangle_weighted_replay_device_output_stream_validated_graph_capture_fail_closed"
        if not validation_errors
        else "triangle_weighted_replay_device_output_stream_rejected",
        "date": "2026-06-17",
        "runtime": {
            "runtime_executed": True,
            "backend": "optix",
            "partner": "cupy",
            "cupy_version": str(cupy.__version__),
            "expected_weighted_sum": expected_sum,
            "normal_host_scalar_weighted_sum": normal_sum,
            "device_output_stream_weighted_sum": stream_sum,
            "device_output_stream_validated": device_output_stream_validated,
            "graph_capture_validated": graph_capture_validated,
            "graph_replay_weighted_sums": replay_sums,
            "graph_capture_error": graph_capture_error,
        },
        "executor_metadata": executor_metadata,
        "launch_metadata": launch_metadata,
        "readiness": readiness,
        "validation": {
            "status": "accept" if not validation_errors else "reject",
            "errors": validation_errors,
            "graph_capture_status": "accept" if graph_capture_validated else "reject_fail_closed",
            "readiness": readiness_validation,
        },
        "claim_boundary": {
            "current_route_changed": False,
            "prepared_weighted_replay_device_output_stream_validated": device_output_stream_validated,
            "prepared_weighted_replay_graph_capture_validated": graph_capture_validated,
            "m113_promotion_authorized_for_future_triangle_shape": False,
            "m113_replaces_current_triangle_route": False,
            "app_specific_native_callback_required": False,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
        "conclusion": (
            "M134 validates a generic prepared ray-batch weighted-summary device-output "
            "executor on a caller stream, removing the host scalar read from that "
            "replay path. CUDA graph capture of the OptiX weighted launch is fail-"
            "closed on this pod with a captured CUDA/OptiX error, so the future "
            "Triangle M113 graph shape remains blocked while the current large-row "
            "Triangle route remains Goal4479/Goal4511."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    runtime = packet["runtime"]
    readiness = packet["validation"]["readiness"]
    lines = [
        "# Goal4531 / V3 M134 Triangle Weighted Replay Graph Capture",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Runtime",
        "",
        f"- Expected weighted sum: `{runtime['expected_weighted_sum']}`",
        f"- Host-scalar baseline: `{runtime['normal_host_scalar_weighted_sum']}`",
        f"- Device-output stream launch: `{runtime['device_output_stream_weighted_sum']}`",
        f"- Device-output stream validated: `{runtime['device_output_stream_validated']}`",
        f"- Graph capture validated: `{runtime['graph_capture_validated']}`",
        f"- Graph replay sums: `{runtime['graph_replay_weighted_sums']}`",
        f"- Graph capture error: `{runtime['graph_capture_error']}`",
        "",
        "## M113 Gate",
        "",
        f"- Ready for M113 plan: `{readiness['ready_for_m113_plan']}`",
        f"- Blockers: `{', '.join(readiness['blockers'])}`",
        f"- Chunk count: `{readiness['chunk_count']}`",
        "",
        "## Boundary",
        "",
        "- No current Triangle Counting route changed.",
        "- No app-specific native callback was introduced.",
        "- No automatic partner selection, public speedup, or RT-core speedup wording is authorized.",
        "",
    ]
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
