from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rtdsl as rt
from rtdsl.reference import _polygon_set_unit_cells
from rtdsl.reference import _polygon_unit_cells
from examples.rtdl_polygon_pair_overlap_area_rows import polygon_pair_overlap_candidates_embree_kernel


@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_set_jaccard_reference():
    left = rt.input("left", rt.Polygons, layout=rt.Polygon2DLayout, role="probe")
    right = rt.input("right", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    rows = rt.refine(candidates, predicate=rt.polygon_set_jaccard(exact=False))
    return rt.emit(
        rows,
        fields=[
            "intersection_area",
            "left_area",
            "right_area",
            "union_area",
            "jaccard_similarity",
        ],
    )


def make_authored_polygon_set_jaccard_case():
    left = (
        rt.Polygon(id=1, vertices=((0.0, 0.0), (3.0, 0.0), (3.0, 3.0), (0.0, 3.0))),
        rt.Polygon(id=2, vertices=((4.0, 0.0), (6.0, 0.0), (6.0, 2.0), (4.0, 2.0))),
    )
    right = (
        rt.Polygon(id=10, vertices=((1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0))),
        rt.Polygon(id=11, vertices=((5.0, 0.0), (7.0, 0.0), (7.0, 1.0), (5.0, 1.0))),
    )
    return {"left": left, "right": right}


def _run_embree_native_assisted(left: tuple[rt.Polygon, ...], right: tuple[rt.Polygon, ...]):
    candidate_rows = rt.run_embree(polygon_pair_overlap_candidates_embree_kernel, left=left, right=right)
    candidate_pairs = {
        (int(row["left_polygon_id"]), int(row["right_polygon_id"]))
        for row in candidate_rows
        if int(row["requires_lsi"]) or int(row["requires_pip"])
    }
    left_cells_by_id = {polygon.id: set(_polygon_unit_cells(polygon)) for polygon in left}
    right_cells_by_id = {polygon.id: set(_polygon_unit_cells(polygon)) for polygon in right}
    left_cells = _polygon_set_unit_cells(left)
    right_cells = _polygon_set_unit_cells(right)
    intersection_cells = set()
    for left_id, right_id in candidate_pairs:
        intersection_cells.update(left_cells_by_id[left_id] & right_cells_by_id[right_id])
    intersection_area = len(intersection_cells)
    left_area = len(left_cells)
    right_area = len(right_cells)
    union_area = left_area + right_area - intersection_area
    rows = (
        {
            "intersection_area": intersection_area,
            "left_area": left_area,
            "right_area": right_area,
            "union_area": union_area,
            "jaccard_similarity": 0.0 if union_area == 0 else intersection_area / union_area,
        },
    )
    return rows, candidate_rows


def run_case(backend: str = "cpu_python_reference") -> dict[str, object]:
    case = make_authored_polygon_set_jaccard_case()
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(polygon_set_jaccard_reference, **case)
        candidate_row_count = None
    elif backend == "cpu":
        rows = rt.run_cpu(polygon_set_jaccard_reference, **case)
        candidate_row_count = None
    elif backend == "embree":
        rows, candidate_rows = _run_embree_native_assisted(case["left"], case["right"])
        candidate_row_count = len(candidate_rows)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    return {
        "app": "polygon_set_jaccard",
        "backend": backend,
        "backend_mode": "embree_native_assisted" if backend == "embree" else "cpu_exact",
        "row_count": len(rows),
        "candidate_row_count": candidate_row_count,
        "rows": rows,
        "boundary": (
            "Embree mode uses native Embree overlay/candidate discovery and CPU/Python exact grid-cell "
            "set-area refinement. It is native-assisted, not a fully native Jaccard kernel."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded polygon-set Jaccard.")
    parser.add_argument("--backend", choices=("cpu_python_reference", "cpu", "embree"), default="cpu_python_reference")
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
