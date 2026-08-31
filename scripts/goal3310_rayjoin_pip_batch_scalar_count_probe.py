from __future__ import annotations

import argparse
import contextlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _load_rayjoin_case,
)
from rtdsl.optix_runtime import pack_points  # noqa: E402
from rtdsl.optix_runtime import pack_polygons  # noqa: E402
from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix  # noqa: E402


def _median_ms(samples_s: list[float]) -> float | None:
    if not samples_s:
        return None
    return float(statistics.median(samples_s) * 1000.0)


@contextlib.contextmanager
def _temporary_env(name: str, value: str | None):
    old = os.environ.get(name)
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _parse_batch_stream_count(value: str) -> int | str:
    if value == "auto":
        return value
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("batch stream count must be a positive integer or auto") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("batch stream count must be a positive integer or auto")
    return parsed


def _effective_batch_stream_count(request_count: int, requested: int | str | None) -> int:
    if requested is None:
        return 1
    if requested == "auto":
        if request_count >= 64:
            return min(request_count, 16)
        if request_count >= 16:
            return min(request_count, 8)
        if request_count >= 8:
            return min(request_count, 4)
        return 1
    return min(request_count, min(int(requested), 64))


def _time_call(fn) -> tuple[float, Any]:
    start = time.perf_counter()
    result = fn()
    end = time.perf_counter()
    return end - start, result


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    print("[goal3310] load RayJoin PIP case", flush=True)
    case = _load_rayjoin_case("pip", str(args.dataset))
    points = case.inputs["points"]
    polygons = case.inputs["polygons"]
    print(f"[goal3310] points={len(points)} polygons={len(polygons)}", flush=True)

    packed_points = pack_points(records=points, dimension=2)
    packed_shapes = pack_polygons(records=polygons)

    with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS", args.query_axis), _temporary_env(
        "RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE",
        "1" if args.scalar_count_pipeline else None,
    ), _temporary_env(
        "RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT",
        str(args.batch_stream_count) if args.batch_stream_count is not None else None,
    ):
        with prepare_point_closed_shape_membership_2d_optix(packed_shapes) as prepared:
            with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", None):
                exact_count = int(prepared.count(packed_points))
            with prepared.prepare_point_probe_columns(packed_points) as prepared_points:
                with _temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_BOUNDARY_MODE", args.boundary_mode):
                    print(f"[goal3310] exact_count={exact_count}", flush=True)
                    for index in range(args.single_warmup):
                        count = prepared.count_device_filtered_prepared_points(prepared_points)
                        if count != exact_count:
                            raise RuntimeError(f"single warmup mismatch: {count} != {exact_count}")
                        print(f"[goal3310] single warmup {index + 1}/{args.single_warmup}", flush=True)

                    single_samples: list[float] = []
                    for index in range(args.single_repeat):
                        elapsed_s, count = _time_call(
                            lambda: prepared.count_device_filtered_prepared_points(prepared_points)
                        )
                        if count != exact_count:
                            raise RuntimeError(f"single repeat mismatch: {count} != {exact_count}")
                        single_samples.append(elapsed_s)
                        print(
                            f"[goal3310] single repeat {index + 1}/{args.single_repeat} "
                            f"{elapsed_s * 1000.0:.6f} ms",
                            flush=True,
                        )

                    batch_rows: list[dict[str, object]] = []
                    for request_count in args.request_counts:
                        batch_executor = None
                        if args.batch_executor:
                            batch_executor = prepared.prepare_device_filtered_prepared_points_batch_executor(
                                prepared_points,
                                request_count,
                                stream_count=args.batch_stream_count,
                            )
                            print(
                                f"[goal3310] batch {request_count} executor prepared "
                                f"effective_streams={batch_executor.stream_count_effective}",
                                flush=True,
                            )
                        for index in range(args.batch_warmup):
                            counts = (
                                prepared.count_device_filtered_prepared_points_batch(
                                    prepared_points,
                                    request_count,
                                )
                                if batch_executor is None
                                else batch_executor.run()
                            )
                            if any(count != exact_count for count in counts):
                                raise RuntimeError(
                                    f"batch warmup mismatch for request_count={request_count}: {counts[:5]}"
                                )
                            print(
                                f"[goal3310] batch {request_count} warmup "
                                f"{index + 1}/{args.batch_warmup}",
                                flush=True,
                            )

                        batch_samples: list[float] = []
                        native_candidate_samples: list[float] = []
                        native_modes: set[str] = set()
                        last_counts: tuple[int, ...] = ()
                        for index in range(args.batch_repeat):
                            if batch_executor is None:
                                elapsed_s, counts = _time_call(
                                    lambda request_count=request_count: prepared.count_device_filtered_prepared_points_batch(
                                        prepared_points,
                                        request_count,
                                    )
                                )
                            else:
                                elapsed_s, counts = _time_call(batch_executor.run)
                            if any(count != exact_count for count in counts):
                                raise RuntimeError(
                                    f"batch repeat mismatch for request_count={request_count}: {counts[:5]}"
                                )
                            timings = prepared.last_phase_timings() or {}
                            native_modes.add(str(timings.get("mode")))
                            native_candidate_samples.append(float(timings.get("candidate_count_pass", 0.0)))
                            batch_samples.append(elapsed_s)
                            last_counts = counts
                            print(
                                f"[goal3310] batch {request_count} repeat "
                                f"{index + 1}/{args.batch_repeat} total={elapsed_s * 1000.0:.6f} ms "
                                f"per={elapsed_s * 1000.0 / request_count:.6f} ms",
                                flush=True,
                            )

                        total_ms = _median_ms(batch_samples)
                        native_total_ms = _median_ms(native_candidate_samples)
                        batch_rows.append(
                            {
                                "request_count": int(request_count),
                                "batch_executor": bool(args.batch_executor),
                                "batch_stream_count_effective": _effective_batch_stream_count(
                                    int(request_count),
                                    args.batch_stream_count,
                                ),
                                "total_ms_median": total_ms,
                                "per_request_ms_median": (
                                    float(total_ms / request_count) if total_ms is not None else None
                                ),
                                "native_candidate_total_ms_median": native_total_ms,
                                "native_candidate_per_request_ms_median": (
                                    float(native_total_ms / request_count)
                                    if native_total_ms is not None
                                    else None
                                ),
                                "count_first": int(last_counts[0]) if last_counts else None,
                                "count_last": int(last_counts[-1]) if last_counts else None,
                                "native_modes": sorted(native_modes),
                            }
                        )
                        if batch_executor is not None:
                            batch_executor.close()

    return {
        "goal": 3310,
        "schema": "rtdl.goal3310.rayjoin_pip_batch_scalar_count_probe.v1",
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "dataset": str(args.dataset),
        "point_count": int(packed_points.count),
        "shape_count": int(packed_shapes.polygon_count),
        "query_axis": args.query_axis,
        "boundary_mode": args.boundary_mode,
        "scalar_count_pipeline": bool(args.scalar_count_pipeline),
        "batch_stream_count": args.batch_stream_count,
        "batch_executor": bool(args.batch_executor),
        "exact_count": int(exact_count),
        "single_ms_median": _median_ms(single_samples),
        "batch_rows": batch_rows,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "interpretation": (
            "Batch rows are repeated-query throughput evidence only; they do not replace "
            "one-shot RayJoin latency comparisons."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3310 RayJoin PIP prepared-points batch count probe.")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--query-axis", default="z_point")
    parser.add_argument("--boundary-mode", default="inclusive")
    parser.add_argument("--scalar-count-pipeline", action="store_true")
    parser.add_argument(
        "--batch-stream-count",
        type=_parse_batch_stream_count,
        default=None,
        help="Optional RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT value: positive integer or auto.",
    )
    parser.add_argument("--batch-executor", action="store_true")
    parser.add_argument("--single-warmup", type=int, default=4)
    parser.add_argument("--single-repeat", type=int, default=20)
    parser.add_argument("--batch-warmup", type=int, default=3)
    parser.add_argument("--batch-repeat", type=int, default=12)
    parser.add_argument("--request-counts", type=int, nargs="+", default=[1, 2, 4, 8, 16, 32])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
