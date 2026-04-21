from __future__ import annotations

import argparse
import json
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


def make_demo_case() -> dict[str, tuple[object, ...]]:
    roads = (
        rt.Segment(id=1, x0=0.0, y0=1.0, x1=6.0, y1=1.0),
        rt.Segment(id=2, x0=0.0, y0=4.5, x1=6.0, y1=4.5),
        rt.Segment(id=3, x0=3.0, y0=-1.0, x1=3.0, y1=6.0),
    )
    hazards = (
        rt.Polygon(id=10, vertices=((1.0, 0.0), (2.5, 0.0), (2.5, 2.0), (1.0, 2.0))),
        rt.Polygon(id=11, vertices=((4.0, 0.5), (5.5, 0.5), (5.5, 2.5), (4.0, 2.5))),
        rt.Polygon(id=12, vertices=((2.0, 3.5), (4.5, 3.5), (4.5, 5.5), (2.0, 5.5))),
    )
    return {"roads": roads, "hazards": hazards}


def _optix_performance() -> dict[str, str]:
    support = rt.optix_app_performance_support("road_hazard_screening")
    return {"class": support.performance_class, "note": support.note}


def run_case(backend: str) -> dict[str, object]:
    case = make_demo_case()
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(road_hazard_hitcount, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(road_hazard_hitcount, **case)
    elif backend == "embree":
        rows = rt.run_embree(road_hazard_hitcount, **case)
    elif backend == "optix":
        rows = rt.run_optix(road_hazard_hitcount, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(road_hazard_hitcount, **case)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    hot_segments = [row["segment_id"] for row in rows if row["hit_count"] >= 2]
    return {
        "app": "road_hazard_screening",
        "backend": backend,
        "row_count": len(rows),
        "rows": rows,
        "priority_segments": hot_segments,
        "optix_performance": _optix_performance(),
        "boundary": "OptiX app exposure is currently classified separately from RT-core performance; use optix_performance for the current classification.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Demo app: count how many hazard polygons each road segment intersects."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        default="cpu_python_reference",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
