from __future__ import annotations

import json
import platform
import socket
import statistics
import time
from datetime import datetime
from pathlib import Path

from .baseline_contracts import compare_baseline_rows
from .baseline_runner import load_representative_case
from .goal112_segment_polygon_perf import measure_dataset_backend
from .goal114_segment_polygon_postgis import run_goal114_segment_polygon_postgis_validation


ORACLE_DATASETS = (
    "authored_segment_polygon_minimal",
    "tests/fixtures/rayjoin/br_county_subset.cdb",
    "derived/br_county_subset_segment_polygon_tiled_x4",
    "derived/br_county_subset_segment_polygon_tiled_x16",
)

FULL_BACKENDS = ("cpu", "embree", "optix", "vulkan")
LARGE_POSTGIS_BACKENDS = ("cpu", "embree", "optix")


def _kernel():
    from examples.reference.rtdl_goal10_reference import segment_polygon_hitcount_reference

    return segment_polygon_hitcount_reference


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
        if backend == "vulkan":
            rt.vulkan_version()
            return True
    except Exception:
        return False
    raise ValueError(f"unsupported Goal 116 backend `{backend}`")


def _run_backend(backend: str, case_inputs: dict[str, object]):
    import rtdsl as rt

    kernel = _kernel()
    if backend == "cpu":
        return rt.run_cpu(kernel, **case_inputs)
    if backend == "embree":
        return rt.run_embree(kernel, **case_inputs)
    if backend == "optix":
        return rt.run_optix(kernel, **case_inputs)
    if backend == "vulkan":
        return rt.run_vulkan(kernel, **case_inputs)
    raise ValueError(f"unsupported Goal 116 backend `{backend}`")


def _measure_vulkan_current(dataset: str, *, iterations: int) -> dict[str, object]:
    import rtdsl as rt

    case = load_representative_case("segment_polygon_hitcount", dataset)
    expected = rt.run_cpu_python_reference(_kernel(), **case.inputs)
    rows = rt.run_vulkan(_kernel(), **case.inputs)
    parity = compare_baseline_rows("segment_polygon_hitcount", expected, rows)

    timings: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        rt.run_vulkan(_kernel(), **case.inputs)
        timings.append(time.perf_counter() - start)
    return {
        "dataset": dataset,
        "backend": "vulkan",
        "available": True,
        "parity": parity,
        "row_count": len(rows),
        "current": {
            "boundary": "current_run",
            "timings_sec": timings,
            "mean_sec": statistics.mean(timings) if timings else 0.0,
            "median_sec": statistics.median(timings) if timings else 0.0,
            "min_sec": min(timings) if timings else 0.0,
            "max_sec": max(timings) if timings else 0.0,
        },
        "prepared_bind_and_run": None,
        "prepared_reuse": None,
        "prepared_reuse_parity": None,
        "implementation_note": (
            "Correctness currently uses the accepted Vulkan runtime fallback to "
            "the native CPU oracle for this workload family."
        ),
    }


def run_goal116_segment_polygon_backend_audit(
    *,
    oracle_datasets: tuple[str, ...] = ORACLE_DATASETS,
    postgis_dataset: str = "derived/br_county_subset_segment_polygon_tiled_x64",
    postgis_large_dataset: str = "derived/br_county_subset_segment_polygon_tiled_x256",
    perf_iterations: int = 5,
    db_name: str = "rtdl_postgis",
    db_user: str | None = None,
) -> dict[str, object]:
    import rtdsl as rt

    oracle_records: list[dict[str, object]] = []
    for dataset in oracle_datasets:
        case = load_representative_case("segment_polygon_hitcount", dataset)
        expected = rt.run_cpu_python_reference(_kernel(), **case.inputs)
        oracle_records.append(
            {
                "dataset": dataset,
                "oracle_row_count": len(expected),
                "oracle_backend": "cpu_python_reference",
            }
        )
        for backend in FULL_BACKENDS:
            if not backend_available(backend):
                oracle_records.append(
                    {
                        "dataset": dataset,
                        "backend": backend,
                        "available": False,
                    }
                )
                continue
            rows = _run_backend(backend, case.inputs)
            oracle_records.append(
                {
                    "dataset": dataset,
                    "backend": backend,
                    "available": True,
                    "row_count": len(rows),
                    "parity_vs_cpu_python_reference": compare_baseline_rows(
                        "segment_polygon_hitcount",
                        expected,
                        rows,
                    ),
                }
            )

    performance_records: list[dict[str, object]] = []
    for dataset in (
        "authored_segment_polygon_minimal",
        "tests/fixtures/rayjoin/br_county_subset.cdb",
        "derived/br_county_subset_segment_polygon_tiled_x4",
    ):
        for backend in ("cpu", "embree", "optix"):
            if backend_available(backend):
                record = measure_dataset_backend(dataset, backend, iterations=perf_iterations)
                record["available"] = True
            else:
                record = {"dataset": dataset, "backend": backend, "available": False}
            performance_records.append(record)
        if backend_available("vulkan"):
            performance_records.append(_measure_vulkan_current(dataset, iterations=perf_iterations))
        else:
            performance_records.append({"dataset": dataset, "backend": "vulkan", "available": False})

    full_postgis_backends = tuple(backend for backend in FULL_BACKENDS if backend_available(backend))
    large_postgis_backends = tuple(
        backend for backend in LARGE_POSTGIS_BACKENDS if backend_available(backend)
    )

    postgis_current = run_goal114_segment_polygon_postgis_validation(
        dataset=postgis_dataset,
        backends=full_postgis_backends,
        db_name=db_name,
        db_user=db_user,
    )
    postgis_large = run_goal114_segment_polygon_postgis_validation(
        dataset=postgis_large_dataset,
        backends=large_postgis_backends,
        db_name=db_name,
        db_user=db_user,
    )

    return {
        "suite": "goal116_segment_polygon_backend_audit",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "oracle_datasets": oracle_datasets,
        "oracle_records": oracle_records,
        "performance_iterations": perf_iterations,
        "performance_records": performance_records,
        "postgis_validation": postgis_current,
        "postgis_large_validation": postgis_large,
    }


def render_goal116_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 116 Segment/Polygon Full Backend Audit",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Host: `{payload['host']['platform']}`",
        "",
        "## Oracle Parity",
        "",
        "| Dataset | Backend | Available | Parity vs CPU Python Reference | Row Count |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for record in payload["oracle_records"]:
        if "backend" not in record:
            continue
        lines.append(
            f"| `{record['dataset']}` | `{record['backend']}` | `{record.get('available', False)}` | "
            f"`{record.get('parity_vs_cpu_python_reference', False)}` | {record.get('row_count', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Performance",
            "",
            "| Dataset | Backend | Available | Parity | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |",
            "| --- | --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for record in payload["performance_records"]:
        bind_mean = (
            record["prepared_bind_and_run"]["mean_sec"]
            if isinstance(record.get("prepared_bind_and_run"), dict)
            else 0.0
        )
        reuse_mean = (
            record["prepared_reuse"]["mean_sec"]
            if isinstance(record.get("prepared_reuse"), dict)
            else 0.0
        )
        lines.append(
            f"| `{record['dataset']}` | `{record['backend']}` | `{record.get('available', False)}` | "
            f"`{record.get('parity', False)}` | "
            f"{record.get('current', {}).get('mean_sec', 0.0):.6f} | "
            f"{bind_mean:.6f} | {reuse_mean:.6f} |"
        )

    lines.extend(
        [
            "",
            "## PostGIS Validation",
            "",
            f"- Current scale dataset: `{payload['postgis_validation']['dataset']}`",
            f"- Large scale dataset: `{payload['postgis_large_validation']['dataset']}`",
            f"- Current scale PostGIS SHA256: `{payload['postgis_validation']['postgis']['sha256']}`",
            f"- Large scale PostGIS SHA256: `{payload['postgis_large_validation']['postgis']['sha256']}`",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_goal116_artifacts(payload: dict[str, object], output_dir: str | Path) -> dict[str, Path]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "goal116_segment_polygon_backend_audit.json"
    md_path = output_root / "goal116_segment_polygon_backend_audit.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_goal116_markdown(payload), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}
