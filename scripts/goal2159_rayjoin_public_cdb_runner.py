from __future__ import annotations

import argparse
import json
import os
import signal
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.rtdl_rayjoin_v2_spatial_join_app import run_rayjoin_workload
from examples.reference.rtdl_language_reference import county_soil_overlay_reference
from rtdsl.baseline_contracts import compare_baseline_rows
from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import CdbDataset
from rtdsl.datasets import chains_to_polygons
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import download_rayjoin_sample
from rtdsl.datasets import load_cdb
from rtdsl.datasets import write_cdb
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix
from rtdsl.optix_runtime import prepare_shape_pair_relation_flags_optix


DEFAULT_DATA_DIR = ROOT / "data" / "rayjoin"


@dataclass(frozen=True)
class SliceSpec:
    source: str
    start: int
    count: int
    filename: str


@dataclass(frozen=True)
class CaseSpec:
    label: str
    workload: str
    dataset: str
    slices: tuple[SliceSpec, ...]
    note: str


CASES: dict[str, CaseSpec] = {
    "pip_county512": CaseSpec(
        label="pip_county512",
        workload="pip",
        dataset="{county_0_512}",
        slices=(SliceSpec("br_county", 0, 512, "br_county_start0_count512.cdb"),),
        note="Point-in-polygon over a bounded county slice.",
    ),
    "lsi_county64_soil64_prefix": CaseSpec(
        label="lsi_county64_soil64_prefix",
        workload="lsi",
        dataset="{county_0_64} + {soil_0_64}",
        slices=(
            SliceSpec("br_county", 0, 64, "br_county_start0_count64.cdb"),
            SliceSpec("br_soil", 0, 64, "br_soil_start0_count64.cdb"),
        ),
        note="Prefix county/soil LSI slice retained as a zero-hit control.",
    ),
    "lsi_county256_soil256_count48": CaseSpec(
        label="lsi_county256_soil256_count48",
        workload="lsi",
        dataset="{county_256_48} + {soil_256_48}",
        slices=(
            SliceSpec("br_county", 256, 48, "br_county_start256_count48.cdb"),
            SliceSpec("br_soil", 256, 48, "br_soil_start256_count48.cdb"),
        ),
        note="First nonzero county/soil LSI slice from the Goal2157 offset search.",
    ),
    "lsi_county256_soil256_count128": CaseSpec(
        label="lsi_county256_soil256_count128",
        workload="lsi",
        dataset="{county_256_128} + {soil_256_128}",
        slices=(
            SliceSpec("br_county", 256, 128, "br_county_start256_count128.cdb"),
            SliceSpec("br_soil", 256, 128, "br_soil_start256_count128.cdb"),
        ),
        note="Larger nonzero county/soil LSI slice with a mild warm OptiX win.",
    ),
    "lsi_county256_soil256_count192": CaseSpec(
        label="lsi_county256_soil256_count192",
        workload="lsi",
        dataset="{county_256_192} + {soil_256_192}",
        slices=(
            SliceSpec("br_county", 256, 192, "br_county_start256_count192.cdb"),
            SliceSpec("br_soil", 256, 192, "br_soil_start256_count192.cdb"),
        ),
        note="Best Goal2157 bounded nonzero county/soil LSI slice.",
    ),
    "lsi_county256_soil256_count256": CaseSpec(
        label="lsi_county256_soil256_count256",
        workload="lsi",
        dataset="{county_256_256} + {soil_256_256}",
        slices=(
            SliceSpec("br_county", 256, 256, "br_county_start256_count256.cdb"),
            SliceSpec("br_soil", 256, 256, "br_soil_start256_count256.cdb"),
        ),
        note="Larger nonzero county/soil LSI slice for prepared OptiX amortization checks.",
    ),
    "lsi_county256_soil256_count384": CaseSpec(
        label="lsi_county256_soil256_count384",
        workload="lsi",
        dataset="{county_256_384} + {soil_256_384}",
        slices=(
            SliceSpec("br_county", 256, 384, "br_county_start256_count384.cdb"),
            SliceSpec("br_soil", 256, 384, "br_soil_start256_count384.cdb"),
        ),
        note="Larger bounded county/soil LSI stress slice for RT-vs-CUDA-core comparison.",
    ),
    "lsi_county256_soil256_count512": CaseSpec(
        label="lsi_county256_soil256_count512",
        workload="lsi",
        dataset="{county_256_512} + {soil_256_512}",
        slices=(
            SliceSpec("br_county", 256, 512, "br_county_start256_count512.cdb"),
            SliceSpec("br_soil", 256, 512, "br_soil_start256_count512.cdb"),
        ),
        note="Larger bounded county/soil LSI stress slice for count-first prepared OptiX checks.",
    ),
    "lsi_county64_self_positive_control": CaseSpec(
        label="lsi_county64_self_positive_control",
        workload="lsi",
        dataset="{county_0_64} + {county_0_64}",
        slices=(SliceSpec("br_county", 0, 64, "br_county_start0_count64.cdb"),),
        note="Self-join endpoint-touch diagnostic; not RayJoin performance evidence.",
    ),
    "overlay_county128_soil128": CaseSpec(
        label="overlay_county128_soil128",
        workload="overlay_seed",
        dataset="{county_0_128} + {soil_0_128}",
        slices=(
            SliceSpec("br_county", 0, 128, "br_county_start0_count128.cdb"),
            SliceSpec("br_soil", 0, 128, "br_soil_start0_count128.cdb"),
        ),
        note="Bounded overlay dependency row slice.",
    ),
    "overlay_county256_soil256": CaseSpec(
        label="overlay_county256_soil256",
        workload="overlay_seed",
        dataset="{county_0_256} + {soil_0_256}",
        slices=(
            SliceSpec("br_county", 0, 256, "br_county_start0_count256.cdb"),
            SliceSpec("br_soil", 0, 256, "br_soil_start0_count256.cdb"),
        ),
        note="Larger bounded overlay dependency row slice.",
    ),
    "overlay_county384_soil384": CaseSpec(
        label="overlay_county384_soil384",
        workload="overlay_seed",
        dataset="{county_0_384} + {soil_0_384}",
        slices=(
            SliceSpec("br_county", 0, 384, "br_county_start0_count384.cdb"),
            SliceSpec("br_soil", 0, 384, "br_soil_start0_count384.cdb"),
        ),
        note="Mid-scale bounded overlay dependency row slice for OptiX/Embree scaling checks.",
    ),
    "overlay_county512_soil512": CaseSpec(
        label="overlay_county512_soil512",
        workload="overlay_seed",
        dataset="{county_0_512} + {soil_0_512}",
        slices=(
            SliceSpec("br_county", 0, 512, "br_county_start0_count512.cdb"),
            SliceSpec("br_soil", 0, 512, "br_soil_start0_count512.cdb"),
        ),
        note="Larger bounded overlay dependency row slice for OptiX/Embree scaling checks.",
    ),
}


class StepTimeout(Exception):
    pass


_CUPY_LSI_KERNEL_SOURCE = r"""
extern "C" __global__
void rtdl_goal2159_lsi_flags(
    const double* left,
    const double* right,
    const int n_left,
    const int n_right,
    unsigned char* flags
) {
    const long long total = (long long)n_left * (long long)n_right;
    const long long index = (long long)blockDim.x * (long long)blockIdx.x + threadIdx.x;
    if (index >= total) {
        return;
    }
    const int left_index = (int)(index / n_right);
    const int right_index = (int)(index - (long long)left_index * (long long)n_right);

    const double px = left[left_index * 4 + 0];
    const double py = left[left_index * 4 + 1];
    const double lx1 = left[left_index * 4 + 2];
    const double ly1 = left[left_index * 4 + 3];
    const double rx = lx1 - px;
    const double ry = ly1 - py;

    const double qx = right[right_index * 4 + 0];
    const double qy = right[right_index * 4 + 1];
    const double sx1 = right[right_index * 4 + 2];
    const double sy1 = right[right_index * 4 + 3];
    const double sx = sx1 - qx;
    const double sy = sy1 - qy;

    const double denom = rx * sy - ry * sx;
    if (fabs(denom) < 1.0e-7) {
        flags[index] = 0;
        return;
    }
    const double qpx = qx - px;
    const double qpy = qy - py;
    const double t = (qpx * sy - qpy * sx) / denom;
    const double u = (qpx * ry - qpy * rx) / denom;
    flags[index] = (t >= 0.0 && t <= 1.0 && u >= 0.0 && u <= 1.0) ? 1 : 0;
}
"""


def _signal_handler(signum, frame) -> None:
    raise StepTimeout()


def _maybe_download_samples(data_dir: Path, *, download: bool) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in ("br_county", "br_soil"):
        path = data_dir / f"{name}.cdb"
        if path.exists():
            continue
        if not download:
            raise FileNotFoundError(f"{path} is missing; rerun with --download")
        download_rayjoin_sample(name, path)


def _source_path(data_dir: Path, source: str) -> Path:
    return data_dir / f"{source}.cdb"


def _slice_key(spec: SliceSpec) -> str:
    prefix = "county" if spec.source == "br_county" else "soil"
    return f"{prefix}_{spec.start}_{spec.count}"


def _materialize_slices(data_dir: Path, selected_cases: tuple[CaseSpec, ...]) -> dict[str, dict[str, object]]:
    needed: dict[SliceSpec, None] = {}
    for case in selected_cases:
        for spec in case.slices:
            needed[spec] = None

    loaded: dict[str, CdbDataset] = {}
    materialized: dict[str, dict[str, object]] = {}
    for spec in needed:
        if spec.source not in loaded:
            loaded[spec.source] = load_cdb(_source_path(data_dir, spec.source))
        source = loaded[spec.source]
        sliced = CdbDataset(
            name=f"{spec.source}_start{spec.start}_count{spec.count}",
            chains=tuple(source.chains[spec.start : spec.start + spec.count]),
        )
        path = write_cdb(sliced, data_dir / spec.filename)
        segment_count = len(chains_to_segments(sliced))
        materialized[_slice_key(spec)] = {
            "path": str(path),
            "source": spec.source,
            "start": spec.start,
            "count": spec.count,
            "chains": len(sliced.chains),
            "segments": segment_count,
            "bytes": path.stat().st_size,
        }
    return materialized


def _resolve_dataset_template(template: str, slices: dict[str, dict[str, object]]) -> str:
    values = {key: value["path"] for key, value in slices.items()}
    return template.format(**values)


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _split_dataset_paths(dataset: str) -> tuple[Path, ...]:
    return tuple(Path(part.strip()) for part in dataset.split("+") if part.strip())


def _load_lsi_segments(dataset: str) -> tuple[tuple[object, ...], tuple[object, ...]]:
    paths = _split_dataset_paths(dataset)
    if len(paths) != 2:
        raise ValueError("cupy_lsi_bruteforce requires an LSI dataset shaped as `left.cdb + right.cdb`")
    left = segments_from_records(chains_to_segments(load_cdb(paths[0])))
    right = segments_from_records(chains_to_segments(load_cdb(paths[1])))
    return left, right


def _load_overlay_polygons(dataset: str) -> tuple[tuple[object, ...], tuple[object, ...]]:
    paths = _split_dataset_paths(dataset)
    if len(paths) != 2:
        raise ValueError("optix_prepared_overlay_seed requires an overlay dataset shaped as `left.cdb + right.cdb`")
    left = chains_to_polygons(load_cdb(paths[0]))
    right = chains_to_polygons(load_cdb(paths[1]))
    return left, right


def _segment_intersection_row(left, right) -> dict[str, float | int] | None:
    px = float(left.x0)
    py = float(left.y0)
    rx = float(left.x1) - float(left.x0)
    ry = float(left.y1) - float(left.y0)
    qx = float(right.x0)
    qy = float(right.y0)
    sx = float(right.x1) - float(right.x0)
    sy = float(right.y1) - float(right.y0)

    denom = rx * sy - ry * sx
    if abs(denom) < 1.0e-7:
        return None
    qpx = qx - px
    qpy = qy - py
    t = (qpx * sy - qpy * sx) / denom
    u = (qpx * ry - qpy * rx) / denom
    if not (0.0 <= t <= 1.0 and 0.0 <= u <= 1.0):
        return None
    return {
        "left_id": int(left.id),
        "right_id": int(right.id),
        "intersection_point_x": px + t * rx,
        "intersection_point_y": py + t * ry,
    }


def _cupy_lsi_rows(left_segments: tuple[object, ...], right_segments: tuple[object, ...]):
    import numpy as np
    import cupy as cp

    left_coords = np.asarray(
        [(segment.x0, segment.y0, segment.x1, segment.y1) for segment in left_segments],
        dtype=np.float64,
    )
    right_coords = np.asarray(
        [(segment.x0, segment.y0, segment.x1, segment.y1) for segment in right_segments],
        dtype=np.float64,
    )
    n_left = int(left_coords.shape[0])
    n_right = int(right_coords.shape[0])
    left_gpu = cp.asarray(left_coords)
    right_gpu = cp.asarray(right_coords)
    flags = cp.zeros(n_left * n_right, dtype=cp.uint8)
    kernel = cp.RawKernel(_CUPY_LSI_KERNEL_SOURCE, "rtdl_goal2159_lsi_flags")
    threads = 256
    blocks = (flags.size + threads - 1) // threads
    kernel((blocks,), (threads,), (left_gpu, right_gpu, n_left, n_right, flags))
    hit_indexes = cp.asnumpy(cp.nonzero(flags)[0])
    cp.cuda.runtime.deviceSynchronize()

    rows = []
    for flat_index in hit_indexes:
        left_index = int(flat_index // n_right)
        right_index = int(flat_index - left_index * n_right)
        row = _segment_intersection_row(left_segments[left_index], right_segments[right_index])
        if row is not None:
            rows.append(row)
    return tuple(rows)


def _run_cupy_lsi_backend(
    case: CaseSpec,
    dataset: str,
    *,
    warmups: int,
    repeats: int,
) -> dict[str, object]:
    if case.workload != "lsi":
        raise ValueError("cupy_lsi_bruteforce currently supports only the LSI workload")
    left_segments, right_segments = _load_lsi_segments(dataset)
    reference = run_rayjoin_workload(case.workload, backend="cpu_python_reference", dataset=dataset, include_rows=True)
    reference_rows = tuple(reference["rows"])

    times: list[float] = []
    rows: list[int] = []
    parity: list[bool] = []
    for index in range(warmups):
        start = time.perf_counter()
        result_rows = _cupy_lsi_rows(left_segments, right_segments)
        elapsed = time.perf_counter() - start
        print(
            f"[goal2159] warmup {case.label}/cupy_lsi_bruteforce {index + 1}/{warmups} "
            f"app={elapsed:.6f}s rows={len(result_rows)} "
            f"parity={compare_baseline_rows('lsi', reference_rows, result_rows)}",
            flush=True,
        )
    for index in range(repeats):
        start = time.perf_counter()
        result_rows = _cupy_lsi_rows(left_segments, right_segments)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        rows.append(len(result_rows))
        parity.append(compare_baseline_rows("lsi", reference_rows, result_rows))
        print(
            f"[goal2159] repeat {case.label}/cupy_lsi_bruteforce {index + 1}/{repeats} "
            f"app={times[-1]:.6f}s rows={rows[-1]} parity={parity[-1]}",
            flush=True,
        )
    return {
        "status": "ok",
        "app_elapsed_sec_values": times,
        "app_elapsed_sec_median": _median(times),
        "row_counts": rows,
        "row_count_consistent": len(set(rows)) == 1,
        "all_parity_vs_cpu_python_reference": all(parity),
        "rt_core_accelerated": False,
        "partner_accelerated": True,
        "baseline_kind": "cupy_rawkernel_cuda_core_bruteforce_lsi",
        "left_segment_count": len(left_segments),
        "right_segment_count": len(right_segments),
        "candidate_pair_count": len(left_segments) * len(right_segments),
    }


def _run_optix_prepared_lsi_backend(
    case: CaseSpec,
    dataset: str,
    *,
    warmups: int,
    repeats: int,
) -> dict[str, object]:
    if case.workload != "lsi":
        raise ValueError("optix_prepared_lsi currently supports only the LSI workload")
    left_segments, right_segments = _load_lsi_segments(dataset)
    reference = run_rayjoin_workload(case.workload, backend="cpu_python_reference", dataset=dataset, include_rows=True)
    reference_rows = tuple(reference["rows"])

    prepare_start = time.perf_counter()
    prepared = prepare_segment_pair_intersection_optix(right_segments)
    prepare_elapsed = time.perf_counter() - prepare_start
    times: list[float] = []
    rows: list[int] = []
    parity: list[bool] = []
    try:
        for index in range(warmups):
            start = time.perf_counter()
            result_rows = prepared.run(left_segments)
            elapsed = time.perf_counter() - start
            print(
                f"[goal2159] warmup {case.label}/optix_prepared_lsi {index + 1}/{warmups} "
                f"app={elapsed:.6f}s rows={len(result_rows)} "
                f"parity={compare_baseline_rows('lsi', reference_rows, result_rows)}",
                flush=True,
            )
        for index in range(repeats):
            start = time.perf_counter()
            result_rows = prepared.run(left_segments)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            rows.append(len(result_rows))
            parity.append(compare_baseline_rows("lsi", reference_rows, result_rows))
            print(
                f"[goal2159] repeat {case.label}/optix_prepared_lsi {index + 1}/{repeats} "
                f"app={times[-1]:.6f}s rows={rows[-1]} parity={parity[-1]}",
                flush=True,
            )
    finally:
        prepared.close()
    return {
        "status": "ok",
        "prepare_elapsed_sec": prepare_elapsed,
        "app_elapsed_sec_values": times,
        "app_elapsed_sec_median": _median(times),
        "row_counts": rows,
        "row_count_consistent": len(set(rows)) == 1,
        "all_parity_vs_cpu_python_reference": all(parity),
        "rt_core_accelerated": True,
        "partner_accelerated": False,
        "baseline_kind": "prepared_optix_segment_pair_intersection_reused_build_side",
        "prepared_build_side_reused": True,
        "left_segment_count": len(left_segments),
        "right_segment_count": len(right_segments),
        "candidate_pair_count": len(left_segments) * len(right_segments),
    }


def _run_optix_prepared_overlay_seed_backend(
    case: CaseSpec,
    dataset: str,
    *,
    warmups: int,
    repeats: int,
    reference_rows: tuple[dict[str, object], ...] | None = None,
) -> dict[str, object]:
    if case.workload != "overlay_seed":
        raise ValueError("optix_prepared_overlay_seed currently supports only the overlay_seed workload")
    left_polygons, right_polygons = _load_overlay_polygons(dataset)
    if reference_rows is None:
        reference = run_rayjoin_workload(case.workload, backend="cpu_python_reference", dataset=dataset, include_rows=True)
        reference_rows = tuple(reference["rows"])

    prepare_start = time.perf_counter()
    prepared = prepare_shape_pair_relation_flags_optix(right_polygons)
    prepare_elapsed = time.perf_counter() - prepare_start
    times: list[float] = []
    rows: list[int] = []
    parity: list[bool] = []
    try:
        for index in range(warmups):
            start = time.perf_counter()
            result_rows = prepared.run(left_polygons)
            elapsed = time.perf_counter() - start
            print(
                f"[goal2159] warmup {case.label}/optix_prepared_overlay_seed {index + 1}/{warmups} "
                f"app={elapsed:.6f}s rows={len(result_rows)} "
                f"parity={compare_baseline_rows('overlay', reference_rows, result_rows)}",
                flush=True,
            )
        for index in range(repeats):
            start = time.perf_counter()
            result_rows = prepared.run(left_polygons)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            rows.append(len(result_rows))
            parity.append(compare_baseline_rows("overlay", reference_rows, result_rows))
            print(
                f"[goal2159] repeat {case.label}/optix_prepared_overlay_seed {index + 1}/{repeats} "
                f"app={times[-1]:.6f}s rows={rows[-1]} parity={parity[-1]}",
                flush=True,
            )
    finally:
        prepared.close()
    return {
        "status": "ok",
        "prepare_elapsed_sec": prepare_elapsed,
        "app_elapsed_sec_values": times,
        "app_elapsed_sec_median": _median(times),
        "row_counts": rows,
        "row_count_consistent": len(set(rows)) == 1,
        "all_parity_vs_cpu_python_reference": all(parity),
        "rt_core_accelerated": True,
        "partner_accelerated": False,
        "baseline_kind": "prepared_optix_shape_pair_relation_reused_build_side",
        "prepared_build_side_reused": True,
        "left_polygon_count": len(left_polygons),
        "right_polygon_count": len(right_polygons),
        "candidate_pair_count": len(left_polygons) * len(right_polygons),
    }


def _run_overlay_seed_direct_backend(
    case: CaseSpec,
    dataset: str,
    backend: str,
    *,
    warmups: int,
    repeats: int,
    reference_rows: tuple[dict[str, object], ...] | None = None,
) -> dict[str, object]:
    if case.workload != "overlay_seed":
        raise ValueError("direct overlay backend currently supports only the overlay_seed workload")
    runners = {
        "cpu": rt.run_cpu,
        "embree": rt.run_embree,
        "optix": rt.run_optix,
    }
    if backend not in runners:
        raise ValueError(f"unsupported direct overlay backend: {backend!r}")
    left_polygons, right_polygons = _load_overlay_polygons(dataset)
    if reference_rows is None:
        reference = run_rayjoin_workload(case.workload, backend="cpu_python_reference", dataset=dataset, include_rows=True)
        reference_rows = tuple(reference["rows"])

    times: list[float] = []
    rows: list[int] = []
    parity: list[bool] = []
    runner = runners[backend]
    for index in range(warmups):
        start = time.perf_counter()
        result_rows = runner(county_soil_overlay_reference, left=left_polygons, right=right_polygons)
        elapsed = time.perf_counter() - start
        print(
            f"[goal2159] warmup {case.label}/{backend} {index + 1}/{warmups} "
            f"app={elapsed:.6f}s rows={len(result_rows)} "
            f"parity={compare_baseline_rows('overlay', reference_rows, result_rows)}",
            flush=True,
        )
    for index in range(repeats):
        start = time.perf_counter()
        result_rows = runner(county_soil_overlay_reference, left=left_polygons, right=right_polygons)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        rows.append(len(result_rows))
        parity.append(compare_baseline_rows("overlay", reference_rows, result_rows))
        print(
            f"[goal2159] repeat {case.label}/{backend} {index + 1}/{repeats} "
            f"app={times[-1]:.6f}s rows={rows[-1]} parity={parity[-1]}",
            flush=True,
        )
    return {
        "status": "ok",
        "app_elapsed_sec_values": times,
        "app_elapsed_sec_median": _median(times),
        "row_counts": rows,
        "row_count_consistent": len(set(rows)) == 1,
        "all_parity_vs_cpu_python_reference": all(parity),
        "rt_core_accelerated": backend == "optix",
        "direct_overlay_seed_runner": True,
        "reference_reused_per_backend": True,
        "left_polygon_count": len(left_polygons),
        "right_polygon_count": len(right_polygons),
        "candidate_pair_count": len(left_polygons) * len(right_polygons),
    }


def _run_case(
    case: CaseSpec,
    dataset: str,
    *,
    backends: tuple[str, ...],
    warmups: int,
    repeats: int,
    step_timeout: int,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "workload": case.workload,
        "dataset": dataset,
        "note": case.note,
        "backends": {},
    }
    shared_overlay_reference_rows: tuple[dict[str, object], ...] | None = None
    overlay_reference_backends = {"cpu", "embree", "optix", "optix_prepared_overlay_seed"}
    if case.workload == "overlay_seed" and any(backend in overlay_reference_backends for backend in backends):
        print(f"[goal2159] prepare shared {case.label}/cpu_python_reference rows", flush=True)
        reference_start = time.perf_counter()
        reference = run_rayjoin_workload(case.workload, backend="cpu_python_reference", dataset=dataset, include_rows=True)
        shared_overlay_reference_rows = tuple(reference["rows"])
        reference_elapsed = time.perf_counter() - reference_start
        payload["shared_reference"] = {
            "backend": "cpu_python_reference",
            "elapsed_sec": reference_elapsed,
            "row_count": len(shared_overlay_reference_rows),
            "reused_by_backends": tuple(backend for backend in backends if backend in overlay_reference_backends),
        }
        print(
            f"[goal2159] shared {case.label}/cpu_python_reference "
            f"rows={len(shared_overlay_reference_rows)} elapsed={reference_elapsed:.6f}s",
            flush=True,
        )
    for backend in backends:
        print(f"[goal2159] start {case.label}/{backend}", flush=True)
        start = time.perf_counter()
        times: list[float] = []
        rows: list[int] = []
        parity: list[bool] = []
        if hasattr(signal, "SIGALRM"):
            signal.alarm(step_timeout)
        try:
            if backend == "cupy_lsi_bruteforce":
                backend_payload = _run_cupy_lsi_backend(
                    case,
                    dataset,
                    warmups=warmups,
                    repeats=repeats,
                )
                backend_payload["elapsed_outer_sec"] = time.perf_counter() - start
                payload["backends"][backend] = backend_payload
                if hasattr(signal, "SIGALRM"):
                    signal.alarm(0)
                continue
            if backend == "optix_prepared_lsi":
                backend_payload = _run_optix_prepared_lsi_backend(
                    case,
                    dataset,
                    warmups=warmups,
                    repeats=repeats,
                )
                backend_payload["elapsed_outer_sec"] = time.perf_counter() - start
                payload["backends"][backend] = backend_payload
                if hasattr(signal, "SIGALRM"):
                    signal.alarm(0)
                continue
            if case.workload == "overlay_seed" and backend in {"cpu", "embree", "optix"}:
                backend_payload = _run_overlay_seed_direct_backend(
                    case,
                    dataset,
                    backend,
                    warmups=warmups,
                    repeats=repeats,
                    reference_rows=shared_overlay_reference_rows,
                )
                backend_payload["elapsed_outer_sec"] = time.perf_counter() - start
                payload["backends"][backend] = backend_payload
                if hasattr(signal, "SIGALRM"):
                    signal.alarm(0)
                continue
            if backend == "optix_prepared_overlay_seed":
                backend_payload = _run_optix_prepared_overlay_seed_backend(
                    case,
                    dataset,
                    warmups=warmups,
                    repeats=repeats,
                    reference_rows=shared_overlay_reference_rows,
                )
                backend_payload["elapsed_outer_sec"] = time.perf_counter() - start
                payload["backends"][backend] = backend_payload
                if hasattr(signal, "SIGALRM"):
                    signal.alarm(0)
                continue
            for index in range(warmups):
                result = run_rayjoin_workload(case.workload, backend=backend, dataset=dataset, include_rows=False)
                print(
                    f"[goal2159] warmup {case.label}/{backend} {index + 1}/{warmups} "
                    f"app={float(result['elapsed_sec']):.6f}s rows={int(result['row_count'])} "
                    f"parity={bool(result['parity_vs_cpu_python_reference'])}",
                    flush=True,
                )
            for index in range(repeats):
                result = run_rayjoin_workload(case.workload, backend=backend, dataset=dataset, include_rows=False)
                times.append(float(result["elapsed_sec"]))
                rows.append(int(result["row_count"]))
                parity.append(bool(result["parity_vs_cpu_python_reference"]))
                print(
                    f"[goal2159] repeat {case.label}/{backend} {index + 1}/{repeats} "
                    f"app={times[-1]:.6f}s rows={rows[-1]} parity={parity[-1]}",
                    flush=True,
                )
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
            payload["backends"][backend] = {
                "status": "ok",
                "elapsed_outer_sec": time.perf_counter() - start,
                "app_elapsed_sec_values": times,
                "app_elapsed_sec_median": _median(times),
                "row_counts": rows,
                "row_count_consistent": len(set(rows)) == 1,
                "all_parity_vs_cpu_python_reference": all(parity),
                "rt_core_accelerated": backend == "optix",
            }
        except StepTimeout:
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
            payload["backends"][backend] = {
                "status": "timeout",
                "elapsed_outer_sec": time.perf_counter() - start,
            }
        except Exception as exc:  # pragma: no cover - artifact path records runtime failures.
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
            payload["backends"][backend] = {
                "status": "error",
                "elapsed_outer_sec": time.perf_counter() - start,
                "error": repr(exc),
            }
    return payload


def build_artifact(args: argparse.Namespace) -> dict[str, object]:
    selected = tuple(CASES[name] for name in args.cases.split(",") if name)
    if not selected:
        raise ValueError("at least one case must be selected")

    data_dir = Path(args.data_dir)
    _maybe_download_samples(data_dir, download=args.download)
    slices = _materialize_slices(data_dir, selected)
    backends = tuple(backend.strip() for backend in args.backends.split(",") if backend.strip())

    artifact: dict[str, object] = {
        "goal": "2159",
        "commit": os.popen("git rev-parse HEAD").read().strip(),
        "data_dir": str(data_dir),
        "warmups": args.warmups,
        "repeats": args.repeats,
        "step_timeout_sec": args.step_timeout,
        "slices": slices,
        "cases": {},
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "whole_app_rayjoin_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }
    for case in selected:
        dataset = _resolve_dataset_template(case.dataset, slices)
        if args.dry_run:
            artifact["cases"][case.label] = {
                "workload": case.workload,
                "dataset": dataset,
                "note": case.note,
                "backends": {backend: {"status": "dry_run"} for backend in backends},
            }
            continue
        artifact["cases"][case.label] = _run_case(
            case,
            dataset,
            backends=backends,
            warmups=args.warmups,
            repeats=args.repeats,
            step_timeout=args.step_timeout,
        )
    return artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bounded public RayJoin CDB RTDL v2 evidence cases.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directory containing or receiving RayJoin CDB files.")
    parser.add_argument("--output", required=True, help="JSON artifact path.")
    parser.add_argument("--download", action="store_true", help="Download missing public RayJoin samples.")
    parser.add_argument("--dry-run", action="store_true", help="Write planned slices/cases without running backends.")
    parser.add_argument("--cases", default=",".join(CASES), help="Comma-separated case labels.")
    parser.add_argument("--backends", default="cpu,embree,optix", help="Comma-separated backends.")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--step-timeout", type=int, default=240)
    return parser.parse_args()


def main() -> None:
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _signal_handler)
    args = parse_args()
    artifact = build_artifact(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal2159] wrote {output}", flush=True)


if __name__ == "__main__":
    main()
