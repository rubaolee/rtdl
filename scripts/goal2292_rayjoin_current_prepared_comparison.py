from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import chains_to_polygons
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import pack_points
from rtdsl.optix_runtime import pack_polygons
from rtdsl.optix_runtime import pack_segments
from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix
from scripts.goal2192_rayjoin_same_query_stream_runner import _stream_points
from scripts.goal2192_rayjoin_same_query_stream_runner import _stream_segments
from scripts.goal2192_rayjoin_same_query_stream_runner import load_query_stream


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _gpu_name() -> str:
    try:
        return subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return "unavailable"


def _commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _time(label: str, fn):
    start = time.perf_counter()
    value = fn()
    elapsed = time.perf_counter() - start
    print(f"[goal2292] {label} value={value} elapsed={elapsed:.6f}s", flush=True)
    return elapsed, value


def _run_repeats(label: str, fn, *, warmups: int, repeats: int) -> dict[str, object]:
    for index in range(warmups):
        _time(f"warmup {label} {index + 1}/{warmups}", fn)

    seconds: list[float] = []
    values: list[int] = []
    phases: list[dict[str, object] | None] = []
    for index in range(repeats):
        elapsed, value = _time(f"repeat {label} {index + 1}/{repeats}", fn)
        seconds.append(float(elapsed))
        values.append(int(value))
        phase = getattr(fn, "last_phase", None)
        phases.append(phase if isinstance(phase, dict) else None)
    return {
        "seconds": seconds,
        "median_sec": _median(seconds),
        "values": values,
        "value_consistent": len(set(values)) == 1,
        "phase_samples": phases,
    }


def _load_base(stream: dict[str, object]):
    return load_cdb(Path(str(stream["base_cdb"])))


def run_lsi(stream_path: Path, *, warmups: int, repeats: int) -> dict[str, object]:
    stream = load_query_stream(stream_path)
    if stream["workload"] != "lsi":
        raise ValueError("LSI stream expected")
    base = _load_base(stream)
    left_records = _stream_segments(stream)
    right_records = segments_from_records(chains_to_segments(base))

    start = time.perf_counter()
    packed_left = pack_segments(records=left_records)
    one_time_left_pack_sec = time.perf_counter() - start
    print(f"[goal2292] lsi one_time_left_pack_sec={one_time_left_pack_sec:.6f}", flush=True)

    start = time.perf_counter()
    prepared = prepare_segment_pair_intersection_optix(right_records)
    prepare_sec = time.perf_counter() - start
    print(f"[goal2292] lsi prepare_sec={prepare_sec:.6f}", flush=True)

    try:
        def run_raw_count() -> int:
            rows = prepared.run_raw(packed_left)
            try:
                return int(rows.row_count)
            finally:
                rows.close()

        def run_scalar_count() -> int:
            return int(prepared.count(packed_left))

        def raw_with_phase() -> int:
            value = run_raw_count()
            raw_with_phase.last_phase = prepared.last_phase_timings()
            return value

        def count_with_phase() -> int:
            value = run_scalar_count()
            count_with_phase.last_phase = prepared.last_phase_timings()
            return value

        raw = _run_repeats("lsi/raw_rows", raw_with_phase, warmups=warmups, repeats=repeats)
        count = _run_repeats("lsi/scalar_count", count_with_phase, warmups=warmups, repeats=repeats)
    finally:
        prepared.close()

    return {
        "query_stream": str(stream_path),
        "query_stream_producer": stream["producer"],
        "query_count": int(stream["query_count"]),
        "left_segments": len(left_records),
        "right_segments": len(right_records),
        "one_time_left_pack_sec": one_time_left_pack_sec,
        "prepare_sec": prepare_sec,
        "route": "prepared_segment_pair_intersection_optix_with_prepacked_left",
        "raw_rows": raw,
        "scalar_count": count,
        "row_count_parity": raw["values"] == count["values"],
        "expected_rows_from_prior_cpu_verified_artifacts": 8921,
        "matches_prior_expected_count": all(value == 8921 for value in raw["values"] + count["values"]),
    }


def run_pip(stream_path: Path, *, warmups: int, repeats: int) -> dict[str, object]:
    stream = load_query_stream(stream_path)
    if stream["workload"] != "pip":
        raise ValueError("PIP stream expected")
    base = _load_base(stream)
    points = _stream_points(stream)
    polygons = chains_to_polygons(base)

    start = time.perf_counter()
    packed_points = pack_points(records=points, dimension=2)
    one_time_point_pack_sec = time.perf_counter() - start
    print(f"[goal2292] pip one_time_point_pack_sec={one_time_point_pack_sec:.6f}", flush=True)

    start = time.perf_counter()
    packed_polygons = pack_polygons(records=polygons)
    one_time_shape_pack_sec = time.perf_counter() - start
    print(f"[goal2292] pip one_time_shape_pack_sec={one_time_shape_pack_sec:.6f}", flush=True)

    start = time.perf_counter()
    prepared = prepare_point_closed_shape_membership_2d_optix(packed_polygons)
    prepare_sec = time.perf_counter() - start
    print(f"[goal2292] pip prepare_sec={prepare_sec:.6f}", flush=True)

    try:
        def run_positive_raw_count() -> int:
            rows = prepared.run_raw(packed_points, result_mode="positive_hits")
            try:
                return int(rows.row_count)
            finally:
                rows.close()

        row_return = _run_repeats(
            "pip/positive_rows",
            run_positive_raw_count,
            warmups=warmups,
            repeats=repeats,
        )
        count = _run_repeats(
            "pip/scalar_count",
            lambda: int(prepared.count(packed_points)),
            warmups=warmups,
            repeats=repeats,
        )
    finally:
        prepared.close()

    return {
        "query_stream": str(stream_path),
        "query_stream_producer": stream["producer"],
        "query_count": int(stream["query_count"]),
        "points": len(points),
        "shapes": len(polygons),
        "one_time_point_pack_sec": one_time_point_pack_sec,
        "one_time_shape_pack_sec": one_time_shape_pack_sec,
        "prepare_sec": prepare_sec,
        "route": "prepared_point_closed_shape_membership_2d_optix_with_prepacked_points",
        "positive_rows": row_return,
        "scalar_count": count,
        "row_count_parity": row_return["values"] == count["values"],
        "expected_rows_from_prior_cpu_verified_artifacts": 8686,
        "matches_prior_expected_count": all(value == 8686 for value in row_return["values"] + count["values"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Current prepared RTDL RayJoin-style comparison.")
    parser.add_argument("--lsi-stream", required=True)
    parser.add_argument("--pip-stream", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=11)
    args = parser.parse_args()

    payload = {
        "goal": 2292,
        "schema": "rtdl.rayjoin.current_prepared_comparison.v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "commit": _commit(),
        "gpu": _gpu_name(),
        "warmups": args.warmups,
        "repeats": args.repeats,
        "lsi": run_lsi(Path(args.lsi_stream), warmups=args.warmups, repeats=args.repeats),
        "pip": run_pip(Path(args.pip_stream), warmups=args.warmups, repeats=args.repeats),
        "claim_boundary": {
            "same_contract_with_rayjoin_query_exec": True,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal2292] wrote {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
