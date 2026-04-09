from __future__ import annotations

import json
import platform
import socket
import statistics
import time
from datetime import datetime
from pathlib import Path

from .baseline_runner import load_representative_case
from .embree_runtime import pack_polygons
from .embree_runtime import pack_segments
from .reference import Segment
from .reference import Polygon


DATASETS = (
    "authored_segment_polygon_minimal",
    "tests/fixtures/rayjoin/br_county_subset.cdb",
    "derived/br_county_subset_segment_polygon_tiled_x4",
)

BACKENDS = ("cpu", "embree", "optix")


def backend_available(backend: str) -> bool:
    import rtdsl as rt

    try:
        if backend == "cpu":
            rt.oracle_version()
            return True
        if backend == "embree":
            rt.embree_version()
            return True
        if backend == "optix":
            rt.optix_version()
            return True
    except Exception:
        return False
    raise ValueError(f"unsupported Goal 112 backend `{backend}`")


def _kernel():
    from examples.reference.rtdl_goal10_reference import segment_polygon_hitcount_reference

    return segment_polygon_hitcount_reference


def _pack_case(case: dict[str, tuple[Segment, ...] | tuple[Polygon, ...]]) -> dict[str, object]:
    return {
        "segments": pack_segments(records=case["segments"]),
        "polygons": pack_polygons(records=case["polygons"]),
    }


def _run_current(backend: str, case_inputs: dict[str, object]):
    import rtdsl as rt

    kernel = _kernel()
    if backend == "cpu":
        return rt.run_cpu(kernel, **case_inputs)
    if backend == "embree":
        return rt.run_embree(kernel, **case_inputs)
    if backend == "optix":
        return rt.run_optix(kernel, **case_inputs)
    raise ValueError(f"unsupported Goal 112 backend `{backend}`")


def _prepare_backend(backend: str):
    import rtdsl as rt

    kernel = _kernel()
    if backend == "embree":
        return rt.prepare_embree(kernel)
    if backend == "optix":
        return rt.prepare_optix(kernel)
    raise ValueError(f"unsupported Goal 112 prepared backend `{backend}`")


def _measure_loop(fn, *, iterations: int) -> list[float]:
    timings = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        timings.append(time.perf_counter() - start)
    return timings


def _summarize_timings(timings: list[float]) -> dict[str, object]:
    return {
        "timings_sec": timings,
        "mean_sec": statistics.mean(timings) if timings else 0.0,
        "median_sec": statistics.median(timings) if timings else 0.0,
        "min_sec": min(timings) if timings else 0.0,
        "max_sec": max(timings) if timings else 0.0,
    }


def measure_dataset_backend(
    dataset: str,
    backend: str,
    *,
    iterations: int = 5,
) -> dict[str, object]:
    import rtdsl as rt

    case = load_representative_case("segment_polygon_hitcount", dataset)
    expected = rt.run_cpu_python_reference(_kernel(), **case.inputs)
    current_rows = _run_current(backend, case.inputs)
    parity = rt.compare_baseline_rows("segment_polygon_hitcount", expected, current_rows)

    current = _summarize_timings(
        _measure_loop(lambda: _run_current(backend, case.inputs), iterations=iterations)
    )
    current["boundary"] = "current_run"

    record: dict[str, object] = {
        "dataset": dataset,
        "backend": backend,
        "parity": parity,
        "row_count": len(current_rows),
        "current": current,
    }

    if backend in {"embree", "optix"}:
        packed = _pack_case(case.inputs)
        prepared_kernel = _prepare_backend(backend)
        bind_and_run = _summarize_timings(
            _measure_loop(lambda: prepared_kernel.bind(**packed).run(), iterations=iterations)
        )
        bind_and_run["boundary"] = "prepared_bind_and_run"
        prepared_execution = prepared_kernel.bind(**packed)
        reuse_rows = prepared_execution.run()
        reuse_parity = rt.compare_baseline_rows("segment_polygon_hitcount", expected, reuse_rows)
        reuse = _summarize_timings(
            _measure_loop(lambda: prepared_execution.run(), iterations=iterations)
        )
        reuse["boundary"] = "prepared_reuse"
        record["prepared_bind_and_run"] = bind_and_run
        record["prepared_reuse"] = reuse
        record["prepared_reuse_parity"] = reuse_parity

    return record


def run_goal112_segment_polygon_perf(
    *,
    datasets: tuple[str, ...] = DATASETS,
    backends: tuple[str, ...] = BACKENDS,
    iterations: int = 5,
) -> dict[str, object]:
    records = []
    for dataset in datasets:
        for backend in backends:
            if not backend_available(backend):
                records.append(
                    {
                        "dataset": dataset,
                        "backend": backend,
                        "available": False,
                    }
                )
                continue
            measured = measure_dataset_backend(dataset, backend, iterations=iterations)
            measured["available"] = True
            records.append(measured)
    return {
        "suite": "goal112_segment_polygon_performance",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "iterations": iterations,
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "records": records,
    }


def render_goal112_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 112 Segment/Polygon Performance Summary",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Iterations: `{payload['iterations']}`",
        f"- Host: `{payload['host']['platform']}`",
        "",
        "| Dataset | Backend | Available | Parity | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for record in payload["records"]:
        current_mean = record.get("current", {}).get("mean_sec", 0.0)
        bind_mean = record.get("prepared_bind_and_run", {}).get("mean_sec", 0.0)
        reuse_mean = record.get("prepared_reuse", {}).get("mean_sec", 0.0)
        lines.append(
            f"| `{record['dataset']}` | `{record['backend']}` | `{record.get('available', False)}` | "
            f"`{record.get('parity', False)}` | {current_mean:.6f} | {bind_mean:.6f} | {reuse_mean:.6f} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_goal112_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "goal112_segment_polygon_performance.json"
    md_path = output_root / "goal112_segment_polygon_performance.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_goal112_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}
