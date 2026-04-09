from __future__ import annotations

import json
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "src" / "rtdsl" / "__init__.py").exists():
            return candidate
    raise RuntimeError("could not locate RTDL repo root from generated program path")


ROOT = _find_repo_root(Path(__file__).resolve().parent)
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt

REQUEST_WORKLOAD = "segment_polygon_anyhit_rows"
REQUEST_DATASET = "authored_segment_polygon_minimal"
REQUEST_BACKEND = "cpu_python_reference"
REQUEST_VERIFY = True
REQUEST_OUTPUT_MODE = "summary"


@rt.kernel(backend="rtdl", precision="float_approx")
def generated_segment_polygon_anyhit_rows():
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows(exact=False))
    return rt.emit(hits, fields=["segment_id", "polygon_id"])


def build_fixture_case() -> dict[str, object]:
    county = rt.load_cdb("tests/fixtures/rayjoin/br_county_subset.cdb")
    segments = tuple(
        rt.Segment(**{k: v for k, v in record.items() if k in {"id", "x0", "y0", "x1", "y1"}})
        for record in rt.chains_to_segments(county)[:10]
    )
    polygons = tuple(
        rt.Polygon(id=chain.chain_id, vertices=tuple((point.x, point.y) for point in chain.points))
        for chain in county.chains[:2]
        if len(chain.points) >= 3
    )
    return {"segments": segments, "polygons": polygons}


def tile_segments(segments, *, copies: int, step_x: float, step_y: float):
    tiled = []
    for copy_index in range(copies):
        dx = copy_index * step_x
        dy = copy_index * step_y
        for segment in segments:
            tiled.append(
                rt.Segment(
                    id=int(segment.id) + copy_index * 10,
                    x0=float(segment.x0) + dx,
                    y0=float(segment.y0) + dy,
                    x1=float(segment.x1) + dx,
                    y1=float(segment.y1) + dy,
                )
            )
    return tuple(tiled)


def tile_polygons(polygons, *, copies: int, step_x: float, step_y: float):
    tiled = []
    for copy_index in range(copies):
        dx = copy_index * step_x
        dy = copy_index * step_y
        for polygon in polygons:
            tiled.append(
                rt.Polygon(
                    id=int(polygon.id) + copy_index * 10,
                    vertices=tuple((float(x) + dx, float(y) + dy) for x, y in polygon.vertices),
                )
            )
    return tuple(tiled)


def build_case() -> dict[str, object]:
    if REQUEST_DATASET == "authored_segment_polygon_minimal":
        return {
            "segments": (
                rt.Segment(id=1, x0=-1.0, y0=1.0, x1=3.0, y1=1.0),
                rt.Segment(id=2, x0=5.0, y0=5.0, x1=6.0, y1=6.0),
            ),
            "polygons": (
                rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
                rt.Polygon(id=11, vertices=((4.0, 4.0), (7.0, 4.0), (7.0, 7.0), (4.0, 7.0))),
            ),
        }
    if REQUEST_DATASET == "tests/fixtures/rayjoin/br_county_subset.cdb":
        return build_fixture_case()
    if REQUEST_DATASET == "derived/br_county_subset_segment_polygon_tiled_x4":
        case = build_fixture_case()
        return {
            "segments": tile_segments(case["segments"], copies=4, step_x=30.0, step_y=20.0),
            "polygons": tile_polygons(case["polygons"], copies=4, step_x=30.0, step_y=20.0),
        }
    raise ValueError(f"unsupported generated dataset `{REQUEST_DATASET}`")


def run_backend(case_inputs: dict[str, object]):
    if REQUEST_BACKEND == "cpu_python_reference":
        return rt.run_cpu_python_reference(generated_segment_polygon_anyhit_rows, **case_inputs)
    if REQUEST_BACKEND == "cpu":
        return rt.run_cpu(generated_segment_polygon_anyhit_rows, **case_inputs)
    if REQUEST_BACKEND == "embree":
        return rt.run_embree(generated_segment_polygon_anyhit_rows, **case_inputs)
    if REQUEST_BACKEND == "optix":
        return rt.run_optix(generated_segment_polygon_anyhit_rows, **case_inputs)
    raise ValueError(f"unsupported generated backend `{REQUEST_BACKEND}`")


def verify_rows(case_inputs: dict[str, object], actual_rows) -> bool:
    expected_rows = rt.run_cpu_python_reference(generated_segment_polygon_anyhit_rows, **case_inputs)
    return rt.compare_baseline_rows("segment_polygon_anyhit_rows", expected_rows, actual_rows)


def main() -> int:
    case_inputs = build_case()
    rows = run_backend(case_inputs)
    verified = verify_rows(case_inputs, rows) if REQUEST_VERIFY else None
    payload = {
        "workload": REQUEST_WORKLOAD,
        "dataset": REQUEST_DATASET,
        "backend": REQUEST_BACKEND,
    }
    if REQUEST_VERIFY:
        payload["verified_against_cpu_python_reference"] = verified
    if REQUEST_OUTPUT_MODE == "summary":
        payload["row_count"] = len(rows)
    else:
        payload["rows"] = rows
    print(json.dumps(payload, indent=2, sort_keys=True))
    if verified is False:
        raise SystemExit("generated program verification failed")
    return 0


if __name__ == "__main__":
    # Generated by RTDL generate-only support for the second workload family.
    raise SystemExit(main())
