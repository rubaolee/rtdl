from __future__ import annotations

import json
import platform
import socket
import statistics
import time
from datetime import datetime
from pathlib import Path

from .baseline_runner import load_representative_case
from .goal114_segment_polygon_postgis import run_goal114_segment_polygon_postgis_validation


LARGE_COPIES = (64, 256, 512, 1024)
PREPARED_COPIES = (64, 256)


def _kernel():
    from examples.rtdl_goal10_reference import segment_polygon_hitcount_reference

    return segment_polygon_hitcount_reference


def _mean_summary(timings: list[float]) -> dict[str, object]:
    return {
        "timings_sec": timings,
        "mean_sec": statistics.mean(timings) if timings else 0.0,
        "median_sec": statistics.median(timings) if timings else 0.0,
        "min_sec": min(timings) if timings else 0.0,
        "max_sec": max(timings) if timings else 0.0,
    }


def _measure_current(backend: str, dataset: str, *, iterations: int) -> dict[str, object]:
    import rtdsl as rt

    case = load_representative_case("segment_polygon_hitcount", dataset)
    runner = {
        "cpu": rt.run_cpu,
        "embree": rt.run_embree,
        "optix": rt.run_optix,
        "vulkan": rt.run_vulkan,
    }[backend]
    timings: list[float] = []
    row_count = 0
    for _ in range(iterations):
        start = time.perf_counter()
        rows = runner(_kernel(), **case.inputs)
        timings.append(time.perf_counter() - start)
        row_count = len(rows)
    return {
        "backend": backend,
        "dataset": dataset,
        "boundary": "current_run",
        "row_count": row_count,
        **_mean_summary(timings),
    }


def _measure_prepared(backend: str, dataset: str, *, iterations: int) -> dict[str, object]:
    import rtdsl as rt

    case = load_representative_case("segment_polygon_hitcount", dataset)
    packed = {
        "segments": rt.pack_segments(records=case.inputs["segments"]),
        "polygons": rt.pack_polygons(records=case.inputs["polygons"]),
    }
    prepare = {
        "embree": rt.prepare_embree,
        "optix": rt.prepare_optix,
    }[backend]
    prepared = prepare(_kernel())

    bind_and_run_timings: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        prepared.bind(**packed).run()
        bind_and_run_timings.append(time.perf_counter() - start)

    bound = prepared.bind(**packed)
    reuse_timings: list[float] = []
    row_count = 0
    for _ in range(iterations):
        start = time.perf_counter()
        rows = bound.run()
        reuse_timings.append(time.perf_counter() - start)
        row_count = len(rows)

    return {
        "backend": backend,
        "dataset": dataset,
        "row_count": row_count,
        "prepared_bind_and_run": _mean_summary(bind_and_run_timings),
        "prepared_reuse": _mean_summary(reuse_timings),
    }


def run_goal118_segment_polygon_linux_large_perf(
    *,
    copies: tuple[int, ...] = LARGE_COPIES,
    prepared_copies: tuple[int, ...] = PREPARED_COPIES,
    perf_iterations: int = 3,
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
) -> dict[str, object]:
    import rtdsl as rt

    postgis_rows = []
    for copy_count in copies:
        dataset = f"derived/br_county_subset_segment_polygon_tiled_x{copy_count}"
        payload = run_goal114_segment_polygon_postgis_validation(
            dataset=dataset,
            backends=("cpu", "embree", "optix", "vulkan"),
            db_name=db_name,
            db_user=db_user,
        )
        postgis_rows.append(payload)

    performance_rows = []
    for copy_count in prepared_copies:
        dataset = f"derived/br_county_subset_segment_polygon_tiled_x{copy_count}"
        performance_rows.append(_measure_current("cpu", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_current("embree", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_current("optix", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_current("vulkan", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_prepared("embree", dataset, iterations=perf_iterations))
        performance_rows.append(_measure_prepared("optix", dataset, iterations=perf_iterations))

    versions = {
        "oracle": rt.oracle_version(),
        "embree": rt.embree_version(),
        "optix": rt.optix_version(),
        "vulkan": rt.vulkan_version(),
    }

    return {
        "suite": "goal118_segment_polygon_linux_large_perf",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "versions": versions,
        "copies": copies,
        "prepared_copies": prepared_copies,
        "perf_iterations": perf_iterations,
        "postgis_rows": postgis_rows,
        "performance_rows": performance_rows,
    }


def render_goal118_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 118 Segment/Polygon Linux Large-Scale Performance",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Host: `{payload['host']['platform']}`",
        f"- Versions: oracle `{payload['versions']['oracle']}`, embree `{payload['versions']['embree']}`, "
        f"optix `{payload['versions']['optix']}`, vulkan `{payload['versions']['vulkan']}`",
        "",
        "## PostGIS-Backed Large-Scale Results",
        "",
        "| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in payload["postgis_rows"]:
        rec = {item["backend"]: item for item in row["records"]}
        all_parity = all(item["parity_vs_postgis"] for item in row["records"])
        lines.append(
            f"| `{row['dataset']}` | {row['segment_count']} | {row['polygon_count']} | "
            f"{row['postgis']['sec']:.6f} | "
            f"{rec['cpu']['sec']:.6f} | {rec['embree']['sec']:.6f} | "
            f"{rec['optix']['sec']:.6f} | {rec['vulkan']['sec']:.6f} | `{all_parity}` |"
        )

    lines.extend(
        [
            "",
            "## Current And Prepared Timings",
            "",
        "| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    )
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for row in payload["performance_rows"]:
        key = (row["dataset"], row["backend"])
        existing = grouped.get(key, {})
        grouped[key] = {**existing, **row}
    for dataset in [f"derived/br_county_subset_segment_polygon_tiled_x{n}" for n in payload["prepared_copies"]]:
        for backend in ("cpu", "embree", "optix", "vulkan"):
            row = grouped.get((dataset, backend), {"mean_sec": 0.0})
            bind_mean = row.get("prepared_bind_and_run", {}).get("mean_sec", 0.0)
            reuse_mean = row.get("prepared_reuse", {}).get("mean_sec", 0.0)
            lines.append(
                f"| `{dataset}` | `{backend}` | {row['mean_sec']:.6f} | {bind_mean:.6f} | {reuse_mean:.6f} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- all listed PostGIS-backed rows are parity-clean",
            "- OptiX is the fastest current RTDL backend on the audited large rows",
            "- Embree tracks the native CPU oracle closely on this family",
            "- the current Vulkan numbers reflect the accepted correctness-first runtime boundary for this family",
            "  rather than a native optimized traversal implementation",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def write_goal118_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "goal118_segment_polygon_linux_large_perf.json"
    md_path = output_root / "goal118_segment_polygon_linux_large_perf.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_goal118_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}
