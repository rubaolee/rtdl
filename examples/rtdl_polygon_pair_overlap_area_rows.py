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


def _shift_vertices(vertices: tuple[tuple[float, float], ...], offset_x: float) -> tuple[tuple[float, float], ...]:
    return tuple((x + offset_x, y) for x, y in vertices)


def make_authored_polygon_pair_overlap_case(*, copies: int = 1):
    if copies < 1:
        raise ValueError("copies must be >= 1")
    base_left = (
        (1, ((0.0, 0.0), (3.0, 0.0), (3.0, 3.0), (0.0, 3.0))),
        (2, ((4.0, 0.0), (6.0, 0.0), (6.0, 2.0), (4.0, 2.0))),
    )
    base_right = (
        (10, ((1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0))),
        (11, ((5.0, 0.0), (7.0, 0.0), (7.0, 1.0), (5.0, 1.0))),
        (12, ((8.0, 8.0), (9.0, 8.0), (9.0, 9.0), (8.0, 9.0))),
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


def _summarize_rows(rows: tuple[dict[str, int], ...]) -> dict[str, int]:
    return {
        "overlap_pair_count": len(rows),
        "total_intersection_area": sum(int(row["intersection_area"]) for row in rows),
        "total_union_area": sum(int(row["union_area"]) for row in rows),
    }


def _exact_overlap_summary_for_candidates(
    left: tuple[rt.Polygon, ...],
    right: tuple[rt.Polygon, ...],
    candidate_pairs: set[tuple[int, int]],
) -> dict[str, int]:
    left_cells_by_id = {polygon.id: set(_polygon_unit_cells(polygon)) for polygon in left}
    right_cells_by_id = {polygon.id: set(_polygon_unit_cells(polygon)) for polygon in right}
    left_area_by_id = {polygon.id: len(cells) for polygon, cells in zip(left, left_cells_by_id.values())}
    right_area_by_id = {polygon.id: len(cells) for polygon, cells in zip(right, right_cells_by_id.values())}
    overlap_pair_count = 0
    total_intersection_area = 0
    total_union_area = 0
    for left_id, right_id in candidate_pairs:
        left_cells = left_cells_by_id[left_id]
        right_cells = right_cells_by_id[right_id]
        intersection_area = len(left_cells & right_cells)
        if intersection_area <= 0:
            continue
        overlap_pair_count += 1
        total_intersection_area += intersection_area
        total_union_area += left_area_by_id[left_id] + right_area_by_id[right_id] - intersection_area
    return {
        "overlap_pair_count": overlap_pair_count,
        "total_intersection_area": total_intersection_area,
        "total_union_area": total_union_area,
    }


def _run_embree_native_assisted(left: tuple[rt.Polygon, ...], right: tuple[rt.Polygon, ...]):
    candidate_rows = rt.run_embree(polygon_pair_overlap_candidates_embree_kernel, left=left, right=right)
    candidate_pairs = {
        (int(row["left_polygon_id"]), int(row["right_polygon_id"]))
        for row in candidate_rows
        if int(row["requires_lsi"]) or int(row["requires_pip"])
    }
    rows = _exact_overlap_rows_for_candidates(left, right, candidate_pairs)
    return rows, candidate_rows


def _run_embree_summary(left: tuple[rt.Polygon, ...], right: tuple[rt.Polygon, ...]):
    candidate_rows = rt.run_embree(polygon_pair_overlap_candidates_embree_kernel, left=left, right=right)
    candidate_pairs = {
        (int(row["left_polygon_id"]), int(row["right_polygon_id"]))
        for row in candidate_rows
        if int(row["requires_lsi"]) or int(row["requires_pip"])
    }
    return _exact_overlap_summary_for_candidates(left, right, candidate_pairs), candidate_rows


def run_case(backend: str = "cpu_python_reference", *, copies: int = 1, output_mode: str = "rows") -> dict[str, object]:
    if output_mode not in {"rows", "summary"}:
        raise ValueError("output_mode must be 'rows' or 'summary'")
    case = make_authored_polygon_pair_overlap_case(copies=copies)
    rows: tuple[dict[str, int], ...] = ()
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(polygon_pair_overlap_area_rows_reference, **case)
        candidate_row_count = None
        summary = _summarize_rows(tuple(rows))
    elif backend == "cpu":
        rows = rt.run_cpu(polygon_pair_overlap_area_rows_reference, **case)
        candidate_row_count = None
        summary = _summarize_rows(tuple(rows))
    elif backend == "embree":
        if output_mode == "summary":
            summary, candidate_rows = _run_embree_summary(case["left"], case["right"])
        else:
            rows, candidate_rows = _run_embree_native_assisted(case["left"], case["right"])
            summary = _summarize_rows(tuple(rows))
        candidate_row_count = len(candidate_rows)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    payload: dict[str, object] = {
        "app": "polygon_pair_overlap_area_rows",
        "backend": backend,
        "backend_mode": "embree_native_assisted" if backend == "embree" else "cpu_exact",
        "copies": copies,
        "output_mode": output_mode,
        "left_polygon_count": len(case["left"]),
        "right_polygon_count": len(case["right"]),
        "row_count": summary["overlap_pair_count"],
        "candidate_row_count": candidate_row_count,
        "summary": summary,
        "boundary": (
            "Embree mode uses native Embree overlay/candidate discovery and CPU/Python exact grid-cell "
            "area refinement. It is native-assisted, not a fully native area-overlay kernel."
        ),
    }
    if output_mode == "rows":
        payload["rows"] = rows
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded polygon-pair overlap area rows.")
    parser.add_argument("--backend", choices=("cpu_python_reference", "cpu", "embree"), default="cpu_python_reference")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--output-mode", choices=("rows", "summary"), default="rows")
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend, copies=args.copies, output_mode=args.output_mode), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
