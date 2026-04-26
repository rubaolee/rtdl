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
from examples.rtdl_polygon_pair_overlap_area_rows import _positive_candidate_pairs_optix
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


def _run_native_assisted(
    left: tuple[rt.Polygon, ...],
    right: tuple[rt.Polygon, ...],
    *,
    candidate_backend: str,
):
    if candidate_backend == "embree":
        candidate_pairs = _positive_candidate_pairs_embree(left, right)
    elif candidate_backend == "optix":
        candidate_pairs = _positive_candidate_pairs_optix(left, right)
    else:
        raise ValueError("candidate_backend must be 'embree' or 'optix'")
    return _native_jaccard_rows_for_candidates(left, right, candidate_pairs), candidate_pairs


def _exact_jaccard_rows_for_candidates(
    left: tuple[rt.Polygon, ...],
    right: tuple[rt.Polygon, ...],
    candidate_pairs: set[tuple[int, int]],
):
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
    return rows


def _native_jaccard_rows_for_candidates(
    left: tuple[rt.Polygon, ...],
    right: tuple[rt.Polygon, ...],
    candidate_pairs: set[tuple[int, int]],
):
    return tuple(
        dict(row)
        for row in rt.refine_polygon_set_jaccard_for_pairs(left, right, candidate_pairs)
    )


def _run_embree_native_assisted(left: tuple[rt.Polygon, ...], right: tuple[rt.Polygon, ...]):
    return _run_native_assisted(left, right, candidate_backend="embree")


def _run_optix_native_assisted(left: tuple[rt.Polygon, ...], right: tuple[rt.Polygon, ...]):
    return _run_native_assisted(left, right, candidate_backend="optix")


def _enforce_rt_core_requirement(backend: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")


def run_case(
    backend: str = "cpu_python_reference",
    *,
    copies: int = 1,
    require_rt_core: bool = False,
) -> dict[str, object]:
    _enforce_rt_core_requirement(backend, require_rt_core)
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
    elif backend == "optix":
        rows, candidate_pairs = _run_optix_native_assisted(case["left"], case["right"])
        candidate_row_count = len(candidate_pairs)
    else:
        raise ValueError(f"unsupported backend `{backend}`")
    backend_mode = (
        "embree_native_assisted" if backend == "embree"
        else "optix_native_assisted" if backend == "optix"
        else "cpu_exact"
    )
    return {
        "app": "polygon_set_jaccard",
        "backend": backend,
        "backend_mode": backend_mode,
        "copies": copies,
        "left_polygon_count": len(case["left"]),
        "right_polygon_count": len(case["right"]),
        "row_count": len(rows),
        "candidate_row_count": candidate_row_count,
        "rows": rows,
        "rt_core_accelerated": False,
        "rt_core_candidate_discovery_active": backend == "optix",
        "native_continuation_active": backend in {"embree", "optix"},
        "native_continuation_backend": "oracle_cpp" if backend in {"embree", "optix"} else None,
        "optix_performance": {
            "class": rt.optix_app_performance_support("polygon_set_jaccard").performance_class,
            "note": rt.optix_app_performance_support("polygon_set_jaccard").note,
        },
        "boundary": (
            "Embree mode uses native Embree LSI/PIP positive candidate discovery and native C++ exact "
            "grid-cell set-area continuation. OptiX mode uses native OptiX LSI/PIP positive candidate "
            "discovery and the same native C++ continuation. These modes are RT-candidate plus "
            "native-continuation pipelines, not monolithic GPU Jaccard kernels."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded polygon-set Jaccard.")
    parser.add_argument("--backend", choices=("cpu_python_reference", "cpu", "embree", "optix"), default="cpu_python_reference")
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Require the native-assisted OptiX candidate-discovery path.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_case(
                args.backend,
                copies=args.copies,
                require_rt_core=args.require_rt_core,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
