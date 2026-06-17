from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.triangle_capture_mode_audit.goal4539.v1"
OUT_JSON = Path("docs/reports/goal4539_v3_0_m140_triangle_capture_mode_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4539_v3_0_m140_triangle_capture_mode_audit_2026-06-17.md")


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


def _capture_mode_rows(cupy) -> tuple[tuple[str, int | None], ...]:
    return (
        ("default", None),
        ("relaxed", cupy.cuda.runtime.streamCaptureModeRelaxed),
        ("global", cupy.cuda.runtime.streamCaptureModeGlobal),
        ("thread_local", cupy.cuda.runtime.streamCaptureModeThreadLocal),
    )


def build_packet() -> dict[str, Any]:
    import cupy

    expected_sum = 20
    scene = None
    ray_batch = None
    executor = None
    prelaunch_sum = None
    capture_rows: list[dict[str, Any]] = []

    try:
        scene = rt.prepare_optix_static_triangle_scene_3d_device_triangles(_triangle_columns(cupy))
        ray_batch = scene.prepare_ray_batch_device_columns(_ray_columns(cupy))
        weights = cupy.asarray([7, 11, 13], dtype=cupy.uint64)
        output = cupy.zeros(1, dtype=cupy.uint64)
        executor = scene.prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor(
            ray_batch,
            weights,
            output,
        )

        warm_stream = cupy.cuda.Stream(non_blocking=True)
        executor.launch(warm_stream)
        warm_stream.synchronize()
        prelaunch_sum = int(output.get()[0])

        for name, mode in _capture_mode_rows(cupy):
            row: dict[str, Any] = {
                "mode": name,
                "mode_value": mode,
                "capture_status": "not_run",
                "replay_weighted_sum": None,
                "error": None,
            }
            stream = cupy.cuda.Stream(non_blocking=True)
            try:
                output.fill(cupy.uint64(123))
                cupy.cuda.Stream.null.synchronize()
                if mode is None:
                    stream.begin_capture()
                else:
                    stream.begin_capture(mode)
                executor.launch(stream)
                graph = stream.end_capture()
                output.fill(cupy.uint64(999))
                cupy.cuda.Stream.null.synchronize()
                graph.launch(stream=stream)
                stream.synchronize()
                replay_sum = int(output.get()[0])
                row["replay_weighted_sum"] = replay_sum
                row["capture_status"] = (
                    "accept_expected_sum" if replay_sum == expected_sum else "reject_wrong_sum"
                )
            except Exception as exc:  # pragma: no cover - pod evidence path
                row["capture_status"] = "reject_error"
                row["error"] = f"{type(exc).__name__}: {exc}"
                try:
                    stream.end_capture()
                except Exception:
                    pass
            capture_rows.append(row)
    finally:
        if executor is not None:
            executor.close()
        if ray_batch is not None:
            ray_batch.close()
        if scene is not None:
            scene.close()

    graph_capture_validated_modes = tuple(
        row["mode"] for row in capture_rows if row["capture_status"] == "accept_expected_sum"
    )
    validation_errors = []
    if prelaunch_sum != expected_sum:
        validation_errors.append("device-output stream prelaunch weighted sum mismatch")
    if graph_capture_validated_modes:
        validation_errors.append("at least one capture mode unexpectedly validated")
    if len(capture_rows) != 4:
        validation_errors.append("capture mode matrix incomplete")

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4539 / V3 M140",
        "status": "triangle_capture_mode_audit_checked",
        "date": "2026-06-17",
        "runtime": {
            "runtime_executed": True,
            "backend": "optix",
            "partner": "cupy",
            "cupy_version": str(cupy.__version__),
            "expected_weighted_sum": expected_sum,
            "device_output_stream_prelaunch_weighted_sum": prelaunch_sum,
            "device_output_stream_prelaunch_validated": prelaunch_sum == expected_sum,
            "capture_modes": tuple(capture_rows),
            "graph_capture_validated_modes": graph_capture_validated_modes,
            "graph_capture_mode_independent_reject": not graph_capture_validated_modes
            and len(capture_rows) == 4,
        },
        "acceptance": {
            "non_graph_stream_continuation_contract": (
                "PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_WEIGHTED_SUM_DEVICE_OUTPUT_STREAM_CONTINUATION_V1"
            ),
            "non_graph_stream_continuation_evidence_accepted": (
                prelaunch_sum == expected_sum and not graph_capture_validated_modes
            ),
            "m113_graph_capture_still_blocked": True,
            "queue_reclassification_done": False,
        },
        "validation": {
            "status": "accept" if not validation_errors else "reject",
            "errors": tuple(validation_errors),
        },
        "claim_boundary": {
            "current_route_changed": False,
            "runtime_executed": True,
            "prepared_weighted_replay_device_output_stream_validated": prelaunch_sum == expected_sum,
            "prepared_weighted_replay_graph_capture_validated": bool(graph_capture_validated_modes),
            "m113_promotion_authorized_for_future_triangle_shape": False,
            "m113_replaces_current_triangle_route": False,
            "queue_reclassification_authorized": False,
            "app_specific_native_callback_required": False,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
        "conclusion": (
            "Goal4539 confirms that Triangle weighted-replay CUDA graph capture "
            "does not become valid by switching CuPy stream-capture mode after a "
            "validated device-output stream launch. The non-graph device-output "
            "stream executor remains the accepted evidence shape for generic "
            "Triangle weighted replay, but this goal does not reclassify the V3 "
            "queue and does not authorize M113 graph, public speedup, broad "
            "RT-core, automatic partner-selection, or app-specific native-engine "
            "wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    runtime = packet["runtime"]
    lines = [
        "# Goal4539 / V3 M140 Triangle Capture-Mode Audit",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Runtime",
        "",
        f"- Expected weighted sum: `{runtime['expected_weighted_sum']}`",
        f"- Device-output stream prelaunch sum: `{runtime['device_output_stream_prelaunch_weighted_sum']}`",
        f"- Device-output stream prelaunch validated: `{runtime['device_output_stream_prelaunch_validated']}`",
        f"- Graph capture validated modes: `{', '.join(runtime['graph_capture_validated_modes'])}`",
        f"- Graph capture mode-independent reject: `{runtime['graph_capture_mode_independent_reject']}`",
        "",
        "## Capture Modes",
        "",
        "| Mode | Status | Replay sum | Error |",
        "| --- | --- | --- | --- |",
    ]
    for row in runtime["capture_modes"]:
        lines.append(
            f"| `{row['mode']}` | `{row['capture_status']}` | "
            f"`{row['replay_weighted_sum']}` | {row['error'] or ''} |"
        )
    acceptance = packet["acceptance"]
    lines.extend(
        [
            "",
            "## Acceptance",
            "",
            f"- Non-graph stream continuation evidence accepted: `{acceptance['non_graph_stream_continuation_evidence_accepted']}`",
            f"- M113 graph capture still blocked: `{acceptance['m113_graph_capture_still_blocked']}`",
            f"- Queue reclassification done: `{acceptance['queue_reclassification_done']}`",
            "",
            "## Boundary",
            "",
            "- No current Triangle Counting route changed.",
            "- No queue reclassification is authorized by this packet.",
            "- No M113 graph promotion, automatic partner selection, public speedup, or RT-core speedup wording is authorized.",
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
