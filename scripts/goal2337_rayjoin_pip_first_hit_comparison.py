from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import pack_segments
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix
from scripts.goal2335_rayjoin_pip_vertical_probe_comparison import _commit
from scripts.goal2335_rayjoin_pip_vertical_probe_comparison import _gpu_name
from scripts.goal2335_rayjoin_pip_vertical_probe_comparison import _load_json
from scripts.goal2335_rayjoin_pip_vertical_probe_comparison import _rayjoin_positive_point_ids
from scripts.goal2335_rayjoin_pip_vertical_probe_comparison import _resolve
from scripts.goal2335_rayjoin_pip_vertical_probe_comparison import _vertical_probe_segments
from scripts.goal2192_rayjoin_same_query_stream_runner import load_query_stream


def _parse_rayjoin_query_ms(path: str | Path | None) -> float | None:
    if not path:
        return None
    text = _resolve(path).read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^\s*-\s*Query:\s*([0-9.]+)\s*ms\s*$", text, re.MULTILINE)
    if not match:
        return None
    return float(match.group(1))


def _v2_0_baseline(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    payload = _load_json(path)
    return {
        "schema": payload.get("schema"),
        "median_query_sec": float(payload["median_query_sec"]),
        "median_reduce_sec": float(payload.get("median_reduce_sec", 0.0)),
        "median_total_query_reduce_sec": float(payload["median_query_sec"])
        + float(payload.get("median_reduce_sec", 0.0)),
        "raw_rows": int(payload["runs"][0]["raw_intersection_rows"]),
    }


def _probe_ids_from_first_hit_rows(rows_ptr, row_count: int) -> set[int]:
    return {int(rows_ptr[index].probe_id) for index in range(row_count)}


def _probe_ids_from_first_hit_rows_numpy(rows_ptr, row_count: int) -> tuple[set[int] | None, str]:
    try:
        import numpy as np
    except Exception as exc:  # pragma: no cover - depends on environment
        return None, f"numpy_unavailable:{exc.__class__.__name__}"
    try:
        array = np.ctypeslib.as_array(rows_ptr, shape=(row_count,))
        return {int(value) for value in np.unique(array["probe_id"])}, "numpy_unique"
    except Exception as exc:  # pragma: no cover - defensive for ctypes dtype variance
        return None, f"numpy_failed:{exc.__class__.__name__}"


def compare_pip_first_hit(
    *,
    pip_stream: str | Path,
    rayjoin_pip_results: str | Path,
    rayjoin_log: str | Path | None,
    v2_baseline_json: str | Path | None,
    repeats: int,
) -> dict[str, Any]:
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    stream = load_query_stream(pip_stream)
    if stream["workload"] != "pip":
        raise ValueError("PIP query stream expected")
    rayjoin_results = _load_json(rayjoin_pip_results)
    rayjoin_points = _rayjoin_positive_point_ids(rayjoin_results)

    load_start = time.perf_counter()
    base = load_cdb(_resolve(str(stream["base_cdb"])))
    base_load_sec = time.perf_counter() - load_start

    build_start = time.perf_counter()
    vertical_probes = _vertical_probe_segments(stream, base)
    right_segments = segments_from_records(chains_to_segments(base))
    vertical_probe_build_sec = time.perf_counter() - build_start

    pack_start = time.perf_counter()
    packed_vertical_probes = pack_segments(records=vertical_probes)
    vertical_probe_pack_sec = time.perf_counter() - pack_start
    prepare_start = time.perf_counter()
    prepared = prepare_segment_pair_intersection_optix(right_segments)
    prepare_sec = time.perf_counter() - prepare_start

    runs: list[dict[str, Any]] = []
    try:
        for index in range(repeats):
            query_start = time.perf_counter()
            view = prepared.first_hit_raw(packed_vertical_probes)
            query_sec = time.perf_counter() - query_start
            try:
                reduce_start = time.perf_counter()
                numpy_points, numpy_status = _probe_ids_from_first_hit_rows_numpy(
                    view.rows_ptr,
                    int(view.row_count),
                )
                if numpy_points is None:
                    rtdl_points = _probe_ids_from_first_hit_rows(view.rows_ptr, int(view.row_count))
                    reduction_mode = "python_set"
                else:
                    rtdl_points = numpy_points
                    reduction_mode = numpy_status
                reduce_sec = time.perf_counter() - reduce_start
                missing = rayjoin_points - rtdl_points
                extra = rtdl_points - rayjoin_points
                phase = prepared.last_phase_timings() or {}
                runs.append(
                    {
                        "repeat_index": index,
                        "first_hit_rows": int(view.row_count),
                        "query_sec": float(query_sec),
                        "reduction_mode": reduction_mode,
                        "reduce_sec": float(reduce_sec),
                        "rtdl_unique_positive_count": len(rtdl_points),
                        "rayjoin_positive_count": len(rayjoin_points),
                        "same_positive_point_set": not missing and not extra,
                        "missing_count": len(missing),
                        "extra_count": len(extra),
                        "missing_sample": sorted(missing)[:10],
                        "extra_sample": sorted(extra)[:10],
                        "native_phase_timings": phase,
                    }
                )
            finally:
                view.close()
    finally:
        prepared.close()

    query_values = [float(run["query_sec"]) for run in runs]
    reduce_values = [float(run["reduce_sec"]) for run in runs]
    rayjoin_query_ms = _parse_rayjoin_query_ms(rayjoin_log)
    baseline = _v2_0_baseline(v2_baseline_json)
    median_query_sec = statistics.median(query_values)
    median_reduce_sec = statistics.median(reduce_values)
    total_sec = median_query_sec + median_reduce_sec
    v2_speedup = None
    if baseline:
        v2_speedup = baseline["median_total_query_reduce_sec"] / total_sec if total_sec > 0.0 else None
    rayjoin_ratio = None
    if rayjoin_query_ms:
        rayjoin_ratio = total_sec / (rayjoin_query_ms / 1000.0)

    return {
        "goal": 2337,
        "schema": "rtdl.rayjoin.pip_first_hit_comparison.v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "commit": _commit(),
        "gpu": _gpu_name(),
        "query_stream": str(_resolve(pip_stream)),
        "query_stream_producer": stream["producer"],
        "rayjoin_pip_results": str(_resolve(rayjoin_pip_results)),
        "rayjoin_log": str(_resolve(rayjoin_log)) if rayjoin_log else None,
        "query_count": int(stream["query_count"]),
        "base_segment_count": len(right_segments),
        "base_load_sec": base_load_sec,
        "vertical_probe_build_sec": vertical_probe_build_sec,
        "vertical_probe_pack_sec": vertical_probe_pack_sec,
        "prepare_sec": prepare_sec,
        "repeats": repeats,
        "median_query_sec": median_query_sec,
        "median_reduce_sec": median_reduce_sec,
        "median_total_query_reduce_sec": total_sec,
        "rayjoin_query_ms": rayjoin_query_ms,
        "median_total_over_rayjoin_query_ratio": rayjoin_ratio,
        "v2_0_vertical_probe_baseline": baseline,
        "v2_1_speedup_over_v2_0_vertical_probe": v2_speedup,
        "all_same_positive_point_set": all(bool(run["same_positive_point_set"]) for run in runs),
        "runs": runs,
        "contract_note": (
            "This v2.1 path keeps the native engine generic: a prepared segment set answers one "
            "nearest/first segment hit per probe. RayJoin PIP uses that bounded witness contract "
            "at the Python/application layer by mapping vertical probes back to point ids."
        ),
        "claim_boundary": {
            "same_positive_point_set_with_rayjoin_query_exec": all(
                bool(run["same_positive_point_set"]) for run in runs
            ),
            "generic_segment_first_hit_primitive_measured": True,
            "v2_1_beats_v2_0_vertical_probe_claim_authorized": v2_speedup is not None and v2_speedup > 1.0,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "paper_scale_perf_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "v2_1_release_authorized": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare RayJoin PIP positives against the RTDL v2.1 generic segment first-hit route."
    )
    parser.add_argument("--pip-stream", required=True)
    parser.add_argument("--rayjoin-pip-results", required=True)
    parser.add_argument("--rayjoin-log")
    parser.add_argument("--v2-baseline-json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args(argv)

    payload = compare_pip_first_hit(
        pip_stream=args.pip_stream,
        rayjoin_pip_results=args.rayjoin_pip_results,
        rayjoin_log=args.rayjoin_log,
        v2_baseline_json=args.v2_baseline_json,
        repeats=args.repeats,
    )
    output = _resolve(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal2337] wrote {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
