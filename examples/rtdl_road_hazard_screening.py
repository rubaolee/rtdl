from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def road_hazard_hitcount():
    roads = rt.input("roads", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    hazards = rt.input("hazards", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(roads, hazards, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])


def make_demo_case(*, copies: int = 1) -> dict[str, tuple[object, ...]]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    base_roads = (
        rt.Segment(id=1, x0=0.0, y0=1.0, x1=6.0, y1=1.0),
        rt.Segment(id=2, x0=0.0, y0=4.5, x1=6.0, y1=4.5),
        rt.Segment(id=3, x0=3.0, y0=-1.0, x1=3.0, y1=6.0),
    )
    base_hazards = (
        rt.Polygon(id=10, vertices=((1.0, 0.0), (2.5, 0.0), (2.5, 2.0), (1.0, 2.0))),
        rt.Polygon(id=11, vertices=((4.0, 0.5), (5.5, 0.5), (5.5, 2.5), (4.0, 2.5))),
        rt.Polygon(id=12, vertices=((2.0, 3.5), (4.5, 3.5), (4.5, 5.5), (2.0, 5.5))),
    )
    roads: list[object] = []
    hazards: list[object] = []
    for copy_index in range(copies):
        x_offset = float(copy_index * 10)
        road_id_offset = copy_index * 100
        hazard_id_offset = copy_index * 100
        for road in base_roads:
            roads.append(
                rt.Segment(
                    id=int(road.id) + road_id_offset,
                    x0=float(road.x0) + x_offset,
                    y0=float(road.y0),
                    x1=float(road.x1) + x_offset,
                    y1=float(road.y1),
                )
            )
        for hazard in base_hazards:
            hazards.append(
                rt.Polygon(
                    id=int(hazard.id) + hazard_id_offset,
                    vertices=tuple((x + x_offset, y) for x, y in hazard.vertices),
                )
            )
    return {"roads": tuple(roads), "hazards": tuple(hazards)}


def _optix_performance() -> dict[str, str]:
    support = rt.optix_app_performance_support("road_hazard_screening")
    return {"class": support.performance_class, "note": support.note}


@contextmanager
def _temporary_optix_segpoly_mode(optix_mode: str):
    previous = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")
    if optix_mode == "native":
        os.environ["RTDL_OPTIX_SEGPOLY_MODE"] = "native"
    elif optix_mode == "host_indexed":
        os.environ.pop("RTDL_OPTIX_SEGPOLY_MODE", None)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("RTDL_OPTIX_SEGPOLY_MODE", None)
        else:
            os.environ["RTDL_OPTIX_SEGPOLY_MODE"] = previous


def run_case(
    backend: str,
    *,
    copies: int = 1,
    output_mode: str = "rows",
    optix_mode: str = "auto",
) -> dict[str, object]:
    if output_mode not in {"rows", "priority_segments", "summary"}:
        raise ValueError("output_mode must be 'rows', 'priority_segments', or 'summary'")
    if optix_mode not in {"auto", "host_indexed", "native"}:
        raise ValueError("optix_mode must be 'auto', 'host_indexed', or 'native'")
    case = make_demo_case(copies=copies)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(road_hazard_hitcount, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(road_hazard_hitcount, **case)
    elif backend == "embree":
        rows = rt.run_embree(road_hazard_hitcount, **case)
    elif backend == "optix":
        with _temporary_optix_segpoly_mode(optix_mode):
            rows = rt.run_optix(road_hazard_hitcount, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(road_hazard_hitcount, **case)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    hot_segments = [row["segment_id"] for row in rows if row["hit_count"] >= 2]
    payload: dict[str, object] = {
        "app": "road_hazard_screening",
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "optix_mode": optix_mode if backend == "optix" else "not_applicable",
        "row_count": len(rows),
        "priority_segments": hot_segments,
        "priority_segment_count": len(hot_segments),
        "optix_performance": _optix_performance(),
        "boundary": (
            "Rows mode emits per-road hit-count rows. Compact priority_segments "
            "and summary modes omit rows from the app payload when only priority "
            "road ids or counts are needed. OptiX app exposure is currently "
            "classified separately from RT-core performance; use optix_performance "
            "for the current classification."
        ),
    }
    if output_mode == "rows":
        payload["rows"] = rows
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Demo app: count how many hazard polygons each road segment intersects."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1, help="Tile the demo roads/hazards for larger app-output tests.")
    parser.add_argument(
        "--output-mode",
        choices=("rows", "priority_segments", "summary"),
        default="rows",
        help="Use compact modes to omit full per-road rows from the JSON payload.",
    )
    parser.add_argument(
        "--optix-mode",
        choices=("auto", "host_indexed", "native"),
        default="auto",
        help="OptiX only: preserve current default, force host-indexed fallback, or request experimental native segment/polygon hit-count mode.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_case(
                args.backend,
                copies=args.copies,
                output_mode=args.output_mode,
                optix_mode=args.optix_mode,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
