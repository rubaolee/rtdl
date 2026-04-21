from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rtdsl as rt
from rtdsl.reference import _polygon_unit_cells


@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_pair_overlap_area_rows_reference():
    left = rt.input("left", rt.Polygons, layout=rt.Polygon2DLayout, role="probe")
    right = rt.input("right", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    rows = rt.refine(candidates, predicate=rt.polygon_pair_overlap_area_rows(exact=False))
    return rt.emit(
        rows,
        fields=[
            "left_polygon_id",
            "right_polygon_id",
            "intersection_area",
            "left_area",
            "right_area",
            "union_area",
        ],
    )


@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_pair_overlap_candidates_embree_kernel():
    left = rt.input("left", rt.Polygons, layout=rt.Polygon2DLayout, role="probe")
    right = rt.input("right", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    rows = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(
        rows,
        fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
    )


def make_authored_polygon_pair_overlap_case():
    left = (
        rt.Polygon(id=1, vertices=((0.0, 0.0), (3.0, 0.0), (3.0, 3.0), (0.0, 3.0))),
        rt.Polygon(id=2, vertices=((4.0, 0.0), (6.0, 0.0), (6.0, 2.0), (4.0, 2.0))),
    )
    right = (
        rt.Polygon(id=10, vertices=((1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0))),
        rt.Polygon(id=11, vertices=((5.0, 0.0), (7.0, 0.0), (7.0, 1.0), (5.0, 1.0))),
        rt.Polygon(id=12, vertices=((8.0, 8.0), (9.0, 8.0), (9.0, 9.0), (8.0, 9.0))),
    )
    return {"left": left, "right": right}


def _exact_overlap_rows_for_candidates(
    left: tuple[rt.Polygon, ...],
    right: tuple[rt.Polygon, ...],
    candidate_pairs: set[tuple[int, int]],
) -> tuple[dict[str, int], ...]:
    right_by_id = {polygon.id: polygon for polygon in right}
    left_cells_by_id = {polygon.id: tuple(_polygon_unit_cells(polygon)) for polygon in left}
    right_cells_by_id = {polygon.id: tuple(_polygon_unit_cells(polygon)) for polygon in right}
    rows: list[dict[str, int]] = []
    for left_polygon in left:
        left_cells = left_cells_by_id[left_polygon.id]
        left_area = len(left_cells)
        left_cell_lookup = set(left_cells)
        for right_polygon in right:
            if (left_polygon.id, right_polygon.id) not in candidate_pairs:
                continue
            right_cells = right_cells_by_id[right_polygon.id]
            intersection_area = sum(1 for cell in right_cells if cell in left_cell_lookup)
            if intersection_area <= 0:
                continue
            right_area = len(right_cells)
            rows.append(
                {
                    "left_polygon_id": left_polygon.id,
                    "right_polygon_id": right_by_id[right_polygon.id].id,
                    "intersection_area": intersection_area,
                    "left_area": left_area,
                    "right_area": right_area,
                    "union_area": left_area + right_area - intersection_area,
                }
            )
    return tuple(rows)


def _run_embree_native_assisted(left: tuple[rt.Polygon, ...], right: tuple[rt.Polygon, ...]):
    candidate_rows = rt.run_embree(polygon_pair_overlap_candidates_embree_kernel, left=left, right=right)
    candidate_pairs = {
        (int(row["left_polygon_id"]), int(row["right_polygon_id"]))
        for row in candidate_rows
        if int(row["requires_lsi"]) or int(row["requires_pip"])
    }
    rows = _exact_overlap_rows_for_candidates(left, right, candidate_pairs)
    return rows, candidate_rows


def run_case(backend: str = "cpu_python_reference") -> dict[str, object]:
    case = make_authored_polygon_pair_overlap_case()
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(polygon_pair_overlap_area_rows_reference, **case)
        candidate_row_count = None
    elif backend == "cpu":
        rows = rt.run_cpu(polygon_pair_overlap_area_rows_reference, **case)
        candidate_row_count = None
    elif backend == "embree":
        rows, candidate_rows = _run_embree_native_assisted(case["left"], case["right"])
        candidate_row_count = len(candidate_rows)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    return {
        "app": "polygon_pair_overlap_area_rows",
        "backend": backend,
        "backend_mode": "embree_native_assisted" if backend == "embree" else "cpu_exact",
        "row_count": len(rows),
        "candidate_row_count": candidate_row_count,
        "rows": rows,
        "boundary": (
            "Embree mode uses native Embree overlay/candidate discovery and CPU/Python exact grid-cell "
            "area refinement. It is native-assisted, not a fully native area-overlay kernel."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded polygon-pair overlap area rows.")
    parser.add_argument("--backend", choices=("cpu_python_reference", "cpu", "embree"), default="cpu_python_reference")
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
