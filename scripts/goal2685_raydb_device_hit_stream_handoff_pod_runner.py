#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path
from time import perf_counter

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


ROOT = Path(__file__).resolve().parents[1]


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _nvidia_smi() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            text=True,
        ).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def _parse_ints(text: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    if not values or any(value <= 0 for value in values):
        raise argparse.ArgumentTypeError("expected comma-separated positive integers")
    return values


def _parse_modes(text: str) -> tuple[str, ...]:
    values = tuple(item.strip() for item in text.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one mode")
    for value in values:
        if value not in raydb.PAPER_RT_RESULT_MODES:
            raise argparse.ArgumentTypeError(f"unsupported mode: {value}")
    return values


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _summarize_result(
    *,
    backend: str,
    mode: str,
    row_count: int,
    group_count: int,
    repeats: int,
    warmup: int,
    timings: list[float],
    result: dict[str, object],
) -> dict[str, object]:
    metadata = result.get("metadata", {})
    handoff = metadata.get("hit_stream_handoff", {})
    return {
        "backend": backend,
        "mode": mode,
        "row_count": row_count,
        "group_count": group_count,
        "repeats": repeats,
        "warmup": warmup,
        "median_wall_sec": _median(timings),
        "all_wall_sec": timings,
        "matches_cpu_reference": bool(result.get("matches_cpu_reference")),
        "result_row_count": len(result.get("rows", ())),
        "metadata_timings": metadata.get("timings", {}),
        "phase_timing": metadata.get("v2_4_phase_timing", {}),
        "native_symbol": metadata.get("native_symbol"),
        "rt_core_accelerated": metadata.get("rt_core_accelerated"),
        "native_device_hit_stream_columns_ready": metadata.get("native_device_hit_stream_columns_ready"),
        "native_device_column_path_used": metadata.get("native_device_column_path_used"),
        "host_row_bridge_bypassed": metadata.get("host_row_bridge_bypassed"),
        "true_zero_copy_authorized": metadata.get("true_zero_copy_authorized"),
        "hit_stream_row_count": metadata.get("hit_stream_row_count"),
        "hit_stream_overflow": metadata.get("hit_stream_overflow"),
        "continuation_execution_path": metadata.get("continuation_execution_path"),
        "prepared_steady_state": metadata.get("prepared_steady_state"),
        "prepared_payload_columns_reused": metadata.get("prepared_payload_columns_reused"),
        "prepared_optix_scene_reused": metadata.get("prepared_optix_scene_reused"),
        "handoff_gather_mode": handoff.get("gather_mode"),
        "handoff_requested_gather_partner": handoff.get("requested_gather_partner"),
        "handoff_selected_gather_partner": handoff.get("selected_gather_partner"),
        "handoff_materializes_host_rows_for_bridge": handoff.get("materializes_host_rows_for_bridge"),
        "handoff_native_device_column_output_proven_on_hardware": (
            handoff.get("native_device_column_output_proven_on_hardware")
        ),
        "handoff_removes_host_materialization_bottleneck": (
            handoff.get("removes_host_materialization_bottleneck")
        ),
        "torch_carrier_adapter": handoff.get("torch_carrier_adapter"),
        "torch_carrier_execution": handoff.get("torch_carrier_execution"),
        "torch_carrier_same_pointer_evidence_observed": (
            (handoff.get("torch_carrier_execution") or {}).get("same_pointer_evidence_observed")
        ),
        "neutral_buffer_handoff_summary": handoff.get("neutral_buffer_handoff_summary"),
        "claim_boundary": metadata.get("claim_boundary"),
    }


def _run_case(
    *,
    backend: str,
    mode: str,
    row_count: int,
    group_count: int,
    repeats: int,
    warmup: int,
) -> dict[str, object]:
    if backend == raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND:
        print(
            f"[goal2685] starting prepared backend={backend} mode={mode} rows={row_count} "
            f"warmup={warmup} repeats={repeats}",
            flush=True,
        )
        result = raydb.run_result_mode(
            mode,
            backend=backend,
            fixture_kind="generated",
            generated_rows=row_count,
            generated_groups=group_count,
            repeat=repeats,
            warmup=warmup,
        )
        metadata = result.get("metadata", {})
        timings = [float(value) for value in metadata.get("prepared_iteration_wall_sec", ())]
        print(
            f"[goal2685] prepared backend={backend} mode={mode} rows={row_count} "
            f"median={_median(timings):.6f}s",
            flush=True,
        )
        return _summarize_result(
            backend=backend,
            mode=mode,
            row_count=row_count,
            group_count=group_count,
            repeats=repeats,
            warmup=warmup,
            timings=timings,
            result=result,
        )

    timings: list[float] = []
    last = None
    for iteration in range(warmup + repeats):
        print(
            f"[goal2685] starting backend={backend} mode={mode} rows={row_count} "
            f"iter={iteration + 1}/{warmup + repeats}",
            flush=True,
        )
        started = perf_counter()
        result = raydb.run_result_mode(
            mode,
            backend=backend,
            fixture_kind="generated",
            generated_rows=row_count,
            generated_groups=group_count,
        )
        elapsed = perf_counter() - started
        if iteration >= warmup:
            timings.append(elapsed)
            last = result
            print(
                f"[goal2685] backend={backend} mode={mode} rows={row_count} "
                f"iter={iteration - warmup + 1}/{repeats} elapsed={elapsed:.6f}s",
                flush=True,
            )
    assert last is not None
    return _summarize_result(
        backend=backend,
        mode=mode,
        row_count=row_count,
        group_count=group_count,
        repeats=repeats,
        warmup=warmup,
        timings=timings,
        result=last,
    )


def run(args: argparse.Namespace) -> dict[str, object]:
    row_counts = _parse_ints(args.row_counts)
    modes = _parse_modes(args.modes)
    backends = tuple(item.strip() for item in args.backends.split(",") if item.strip())
    payload: dict[str, object] = {
        "goal": "Goal2685 Device-Resident Hit-Stream Handoff And Typed Payload Columns",
        "git_head": _git_head(),
        "repo_root": str(ROOT),
        "nvidia_smi": _nvidia_smi(),
        "row_counts": row_counts,
        "group_count": int(args.group_count),
        "modes": modes,
        "backends": backends,
        "repeats": int(args.repeats),
        "warmup": int(args.warmup),
        "no_public_speedup_claim": True,
        "cases": [],
    }
    if args.dry_run:
        payload["status"] = "dry_run"
        return payload
    cases: list[dict[str, object]] = []
    for row_count in row_counts:
        for mode in modes:
            for backend in backends:
                cases.append(
                    _run_case(
                        backend=backend,
                        mode=mode,
                        row_count=row_count,
                        group_count=int(args.group_count),
                        repeats=int(args.repeats),
                        warmup=int(args.warmup),
                    )
                )
    payload["status"] = "ok"
    payload["cases"] = cases
    payload["all_correct"] = all(bool(case.get("matches_cpu_reference")) for case in cases)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--row-counts", default="1000,10000")
    parser.add_argument("--group-count", type=int, default=128)
    parser.add_argument("--modes", default="count,sum,min,max,avg_as_sum_count")
    parser.add_argument(
        "--backends",
        default=(
            f"{raydb.PAPER_RT_OPTIX_HIT_STREAM_TRITON_BACKEND},"
            f"{raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND}"
        ),
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    payload = run(args)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
