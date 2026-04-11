from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rtdsl as rt


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


def main() -> None:
    rows = rt.run_cpu_python_reference(
        polygon_pair_overlap_area_rows_reference,
        **make_authored_polygon_pair_overlap_case(),
    )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
