from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rtdsl as rt
from rtdsl.reference import _polygon_set_unit_cells
from rtdsl.reference import _polygon_unit_cells
from examples.rtdl_polygon_pair_overlap_area_rows import _positive_candidate_pairs_embree
from examples.rtdl_polygon_pair_overlap_area_rows import _shift_vertices


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


def make_authored_polygon_set_jaccard_case(*, copies: int = 1):
    if copies < 1:
        raise ValueError("copies must be >= 1")
    base_left = (
        (1, ((0.0, 0.0), (3.0, 0.0), (3.0, 3.0), (0.0, 3.0))),
        (2, ((4.0, 0.0), (6.0, 0.0), (6.0, 2.0), (4.0, 2.0))),
    )
    base_right = (
        (10, ((1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0))),
        (11, ((5.0, 0.0), (7.0, 0.0), (7.0, 1.0), (5.0, 1.0))),
    )
    left: list[rt.Polygon] = []
    right: list[rt.Polygon] = []
    for copy_index in range(copies):
        offset_x = float(copy_index * 16)
        id_offset = copy_index * 100
        left.extend(
            rt.Polygon(id=id_offset + polygon_id, vertices=_shift_vertices(vertices, offset_x))
            for polygon_id, vertices in base_left
        )
        right.extend(
            rt.Polygon(id=id_offset + polygon_id, vertices=_shift_vertices(vertices, offset_x))
            for polygon_id, vertices in base_right
        )
    return {"left": tuple(left), "right": tuple(right)}


def _run_embree_native_assisted(left: tuple[rt.Polygon, ...], right: tuple[rt.Polygon, ...]):
    candidate_pairs = _positive_candidate_pairs_embree(left, right)
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
    return rows, candidate_pairs


def run_case(backend: str = "cpu_python_reference", *, copies: int = 1) -> dict[str, object]:
    case = make_authored_polygon_set_jaccard_case(copies=copies)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(polygon_set_jaccard_reference, **case)
        candidate_row_count = None
    elif backend == "cpu":
        rows = rt.run_cpu(polygon_set_jaccard_reference, **case)
        candidate_row_count = None
    elif backend == "embree":
        rows, candidate_pairs = _run_embree_native_assisted(case["left"], case["right"])
        candidate_row_count = len(candidate_pairs)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    return {
        "app": "polygon_set_jaccard",
        "backend": backend,
        "backend_mode": "embree_native_assisted" if backend == "embree" else "cpu_exact",
        "copies": copies,
        "left_polygon_count": len(case["left"]),
        "right_polygon_count": len(case["right"]),
        "row_count": len(rows),
        "candidate_row_count": candidate_row_count,
        "rows": rows,
        "boundary": (
            "Embree mode uses native Embree LSI/PIP positive candidate discovery and CPU/Python exact "
            "grid-cell set-area refinement. It is native-assisted, not a fully native Jaccard kernel."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded polygon-set Jaccard.")
    parser.add_argument("--backend", choices=("cpu_python_reference", "cpu", "embree"), default="cpu_python_reference")
    parser.add_argument("--copies", type=int, default=1)
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend, copies=args.copies), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
