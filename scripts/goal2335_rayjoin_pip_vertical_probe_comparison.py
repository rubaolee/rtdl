from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import CdbDataset
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import pack_segments
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix
from scripts.goal2192_rayjoin_same_query_stream_runner import load_query_stream


def _resolve(path: str | Path) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    return ROOT / value


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(_resolve(path).read_text(encoding="utf-8"))


def _commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            cwd=ROOT,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except Exception:
        return "unavailable"


def _gpu_name() -> str:
    try:
        return subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except Exception:
        return "unavailable"


def _vertical_probe_segments(stream: dict[str, Any], base: CdbDataset) -> tuple[rt.Segment, ...]:
    y_top = max(point.y for chain in base.chains for point in chain.points) + 1.0
    return tuple(
        rt.Segment(
            id=int(row["id"]),
            x0=float(row["x"]),
            y0=float(row["y"]),
            x1=float(row["x"]),
            y1=y_top,
        )
        for row in stream["queries"]
    )


def _rayjoin_positive_point_ids(results: dict[str, Any]) -> set[int]:
    if results.get("schema") != "rtdl.rayjoin.pip_results.v1":
        raise ValueError("RayJoin PIP results must use schema rtdl.rayjoin.pip_results.v1")
    positives = results.get("positive_points")
    if not isinstance(positives, list):
        raise ValueError("RayJoin PIP results must contain positive_points")
    return {int(row["point_id1"]) for row in positives}


def _unique_left_ids_python(rows_ptr, row_count: int) -> set[int]:
    return {int(rows_ptr[index].left_id) for index in range(row_count)}


def _unique_left_ids_numpy(rows_ptr, row_count: int) -> tuple[set[int] | None, str]:
    try:
        import numpy as np
    except Exception as exc:  # pragma: no cover - depends on environment
        return None, f"numpy_unavailable:{exc.__class__.__name__}"
    try:
        array = np.ctypeslib.as_array(rows_ptr, shape=(row_count,))
        return {int(value) for value in np.unique(array["left_id"])}, "numpy_unique"
    except Exception as exc:  # pragma: no cover - defensive for ctypes dtype variance
        return None, f"numpy_failed:{exc.__class__.__name__}"


def compare_pip_vertical_probe(
    *,
    pip_stream: str | Path,
    rayjoin_pip_results: str | Path,
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
            view = prepared.run_raw(packed_vertical_probes)
            query_sec = time.perf_counter() - query_start
            try:
                reduce_start = time.perf_counter()
                numpy_points, numpy_status = _unique_left_ids_numpy(view.rows_ptr, int(view.row_count))
                numpy_reduce_sec = time.perf_counter() - reduce_start
                if numpy_points is None:
                    reduce_start = time.perf_counter()
                    rtdl_points = _unique_left_ids_python(view.rows_ptr, int(view.row_count))
                    reduction_mode = "python_set"
                    reduce_sec = time.perf_counter() - reduce_start
                else:
                    rtdl_points = numpy_points
                    reduction_mode = numpy_status
                    reduce_sec = numpy_reduce_sec

                missing = rayjoin_points - rtdl_points
                extra = rtdl_points - rayjoin_points
                phase = prepared.last_phase_timings() or {}
                runs.append(
                    {
                        "repeat_index": index,
                        "raw_intersection_rows": int(view.row_count),
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
    return {
        "goal": 2335,
        "schema": "rtdl.rayjoin.pip_vertical_probe_comparison.v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "commit": _commit(),
        "gpu": _gpu_name(),
        "query_stream": str(_resolve(pip_stream)),
        "query_stream_producer": stream["producer"],
        "rayjoin_pip_results": str(_resolve(rayjoin_pip_results)),
        "query_count": int(stream["query_count"]),
        "base_segment_count": len(right_segments),
        "base_load_sec": base_load_sec,
        "vertical_probe_build_sec": vertical_probe_build_sec,
        "vertical_probe_pack_sec": vertical_probe_pack_sec,
        "prepare_sec": prepare_sec,
        "repeats": repeats,
        "median_query_sec": statistics.median(query_values),
        "median_reduce_sec": statistics.median(reduce_values),
        "all_same_positive_point_set": all(bool(run["same_positive_point_set"]) for run in runs),
        "runs": runs,
        "contract_note": (
            "RayJoin query=pip exposes a vertical-ray nearest-boundary support contract, "
            "not the same contract as RTDL's faster closed-shape membership count. "
            "This v2.0 comparison expresses the RayJoin support contract using generic "
            "prepared segment-pair intersection plus app/partner reduction by point id."
        ),
        "claim_boundary": {
            "same_positive_point_set_with_rayjoin_query_exec": all(
                bool(run["same_positive_point_set"]) for run in runs
            ),
            "rtdl_beats_rayjoin_claim_authorized": False,
            "paper_scale_perf_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare RayJoin PIP positive points against a current-v2.0 vertical-probe RTDL route."
    )
    parser.add_argument("--pip-stream", required=True)
    parser.add_argument("--rayjoin-pip-results", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--repeats", type=int, default=1)
    args = parser.parse_args(argv)

    payload = compare_pip_vertical_probe(
        pip_stream=args.pip_stream,
        rayjoin_pip_results=args.rayjoin_pip_results,
        repeats=args.repeats,
    )
    output = _resolve(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal2335] wrote {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
