from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_rayjoin_v2_spatial_join_app as rayjoin_app


_WORKLOAD_TO_BASELINE = {
    "pip": "pip",
    "lsi": "lsi",
    "overlay_seed": "overlay",
}

_SCALES = {
    "quick": {
        "pip_polygons": 32,
        "pip_points_per_polygon": 2,
        "lsi_segments_per_side": 32,
        "overlay_polygons": 32,
    },
    "medium": {
        "pip_polygons": 256,
        "pip_points_per_polygon": 4,
        "lsi_segments_per_side": 128,
        "overlay_polygons": 128,
    },
    "large": {
        "pip_polygons": 1024,
        "pip_points_per_polygon": 4,
        "lsi_segments_per_side": 256,
        "overlay_polygons": 512,
    },
}


def _square(polygon_id: int, x0: float, y0: float, size: float = 1.0) -> rt.Polygon:
    return rt.Polygon(
        id=polygon_id,
        vertices=(
            (x0, y0),
            (x0 + size, y0),
            (x0 + size, y0 + size),
            (x0, y0 + size),
        ),
    )


def _make_pip_case(polygon_count: int, points_per_polygon: int) -> dict[str, tuple[object, ...]]:
    polygons = []
    points = []
    point_id = 1
    for polygon_index in range(polygon_count):
        x0 = float((polygon_index % 64) * 3)
        y0 = float((polygon_index // 64) * 3)
        polygons.append(_square(polygon_index + 1, x0, y0))
        for point_index in range(points_per_polygon):
            frac = (point_index + 1) / (points_per_polygon + 1)
            points.append(
                rt.Point(
                    id=point_id,
                    x=x0 + 0.2 + 0.6 * frac,
                    y=y0 + 0.3 + 0.4 * frac,
                )
            )
            point_id += 1
    return {"points": tuple(points), "polygons": tuple(polygons)}


def _make_lsi_case(segments_per_side: int) -> dict[str, tuple[object, ...]]:
    left = []
    right = []
    span = float(segments_per_side)
    for index in range(segments_per_side):
        coord = float(index) + 0.5
        left.append(rt.Segment(id=index + 1, x0=-0.5, y0=coord, x1=span + 0.5, y1=coord))
        right.append(rt.Segment(id=index + 1, x0=coord, y0=-0.5, x1=coord, y1=span + 0.5))
    return {"left": tuple(left), "right": tuple(right)}


def _make_overlay_seed_case(polygon_count: int) -> dict[str, tuple[object, ...]]:
    left = []
    right = []
    for polygon_index in range(polygon_count):
        x0 = float((polygon_index % 64) * 3)
        y0 = float((polygon_index // 64) * 3)
        left.append(_square(polygon_index + 1, x0, y0))
        right.append(_square(polygon_index + 1, x0 + 0.45, y0 + 0.45))
    return {"left": tuple(left), "right": tuple(right)}


def make_case(workload: str, scale: str) -> dict[str, tuple[object, ...]]:
    if scale not in _SCALES:
        raise ValueError(f"unknown scale `{scale}`")
    params = _SCALES[scale]
    if workload == "pip":
        return _make_pip_case(
            int(params["pip_polygons"]),
            int(params["pip_points_per_polygon"]),
        )
    if workload == "lsi":
        return _make_lsi_case(int(params["lsi_segments_per_side"]))
    if workload == "overlay_seed":
        return _make_overlay_seed_case(int(params["overlay_polygons"]))
    raise ValueError(f"unknown workload `{workload}`")


def _compact_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in summary.items()
        if key not in {"positive_assignments", "active_seed_pairs"}
    }


def _run_once(workload: str, backend: str, inputs: dict[str, tuple[object, ...]]) -> tuple[float, tuple[dict[str, object], ...]]:
    kernel = rayjoin_app._KERNELS[workload]
    start = time.perf_counter()
    rows = rayjoin_app._run_backend(kernel, backend, inputs)
    return time.perf_counter() - start, rows


def _progress(message: str) -> None:
    print(f"[goal2147] {message}", file=sys.stderr, flush=True)


def measure_backend(
    workload: str,
    backend: str,
    inputs: dict[str, tuple[object, ...]],
    *,
    repeats: int,
    warmups: int,
    reference_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    for warmup_index in range(warmups):
        _progress(f"{workload}/{backend} warmup {warmup_index + 1}/{warmups}")
        _run_once(workload, backend, inputs)
    timings = []
    rows = ()
    for repeat_index in range(repeats):
        _progress(f"{workload}/{backend} repeat {repeat_index + 1}/{repeats}")
        elapsed_sec, rows = _run_once(workload, backend, inputs)
        timings.append(elapsed_sec)
    baseline_workload = _WORKLOAD_TO_BASELINE[workload]
    return {
        "backend": backend,
        "elapsed_sec_median": statistics.median(timings),
        "elapsed_sec_min": min(timings),
        "elapsed_sec_max": max(timings),
        "repeats": repeats,
        "warmups": warmups,
        "row_count": len(rows),
        "parity_vs_cpu_python_reference": rt.compare_baseline_rows(
            baseline_workload,
            reference_rows,
            rows,
        ),
    }


def run_suite(
    *,
    scale: str,
    workloads: tuple[str, ...],
    backends: tuple[str, ...],
    repeats: int,
    warmups: int,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "goal": "2147",
        "app": "rayjoin_v2_spatial_join",
        "scale": scale,
        "workloads": {},
        "claim_boundary": {
            "full_rayjoin_reproduction": False,
            "paper_scale_perf_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
        "notes": (
            "Synthetic deterministic scale cases are designed to exercise RTDL row contracts. "
            "They are not the RayJoin paper datasets and do not authorize paper-scale claims."
        ),
    }
    for workload in workloads:
        _progress(f"{workload}: generating {scale} synthetic inputs")
        inputs = make_case(workload, scale)
        _progress(f"{workload}/cpu_python_reference reference run")
        reference_elapsed, reference_rows = _run_once(workload, "cpu_python_reference", inputs)
        input_counts = {key: len(value) for key, value in inputs.items()}
        reference_summary = _compact_summary(rayjoin_app._summarize_rows(workload, reference_rows))
        workload_payload = {
            "input_counts": input_counts,
            "reference_elapsed_sec": reference_elapsed,
            "reference_row_count": len(reference_rows),
            "reference_summary": reference_summary,
            "output_contract": reference_summary["output_contract"],
            "backends": {},
        }
        for backend in backends:
            _progress(f"{workload}/{backend}: timed measurement start")
            workload_payload["backends"][backend] = measure_backend(
                workload,
                backend,
                inputs,
                repeats=repeats,
                warmups=warmups,
                reference_rows=reference_rows,
            )
        payload["workloads"][workload] = workload_payload
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic RayJoin-style RTDL v2 scale/perf cases."
    )
    parser.add_argument("--scale", choices=tuple(_SCALES), default="quick")
    parser.add_argument(
        "--workloads",
        default="pip,lsi,overlay_seed",
        help="Comma-separated subset of pip, lsi, overlay_seed.",
    )
    parser.add_argument(
        "--backends",
        default="cpu,embree",
        help="Comma-separated backends: cpu_python_reference,cpu,embree,optix.",
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    workloads = tuple(item.strip() for item in args.workloads.split(",") if item.strip())
    backends = tuple(item.strip() for item in args.backends.split(",") if item.strip())
    allowed_workloads = {"pip", "lsi", "overlay_seed"}
    allowed_backends = {"cpu_python_reference", "cpu", "embree", "optix"}
    unknown_workloads = sorted(set(workloads) - allowed_workloads)
    unknown_backends = sorted(set(backends) - allowed_backends)
    if unknown_workloads:
        raise ValueError(f"unknown workloads: {unknown_workloads}")
    if unknown_backends:
        raise ValueError(f"unknown backends: {unknown_backends}")
    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")
    if args.warmups < 0:
        raise ValueError("--warmups must be non-negative")

    payload = run_suite(
        scale=args.scale,
        workloads=workloads,
        backends=backends,
        repeats=args.repeats,
        warmups=args.warmups,
    )
    text = json.dumps(rayjoin_app._json_ready(payload), indent=2, sort_keys=True)
    if args.output is not None:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
