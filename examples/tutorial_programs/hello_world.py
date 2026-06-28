from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl as rt


# Scene sketch (not to scale):
#
#  left miss         middle hit         right miss
# +---------+      +---------------+      +---------+
# |         |      |               |      |         |
# +---------+      | hello, world  |      +---------+
# ---------------->|---------------|---------------->
#                  |               |
#                  +---------------+
#
# The ray travels horizontally at y = 0. Only the middle rectangle crosses the
# ray and carries the label "hello, world".


@dataclass(frozen=True)
class SceneRect:
    id: int
    label: str
    x0: float
    y0: float
    x1: float
    y1: float


@rt.kernel(backend="rtdl", precision="float_approx")
def hello_world_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def rect_as_two_triangles(rect: SceneRect) -> tuple[rt.Triangle, rt.Triangle]:
    return (
        rt.Triangle(id=rect.id * 2, x0=rect.x0, y0=rect.y0, x1=rect.x1, y1=rect.y0, x2=rect.x1, y2=rect.y1),
        rt.Triangle(id=rect.id * 2 + 1, x0=rect.x0, y0=rect.y0, x1=rect.x1, y1=rect.y1, x2=rect.x0, y2=rect.y1),
    )


def make_scene() -> tuple[tuple[rt.Ray2D, ...], tuple[SceneRect, ...], tuple[rt.Triangle, ...]]:
    rays = (
        rt.Ray2D(id=0, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=20.0),
    )
    rectangles = (
        SceneRect(id=1, label="left miss", x0=1.0, y0=1.0, x1=2.0, y1=2.0),
        SceneRect(id=2, label="hello, world", x0=4.0, y0=-1.0, x1=7.0, y1=1.0),
        SceneRect(id=3, label="right miss", x0=9.0, y0=1.0, x1=10.0, y1=2.0),
    )
    triangles = tuple(triangle for rect in rectangles for triangle in rect_as_two_triangles(rect))
    return rays, rectangles, triangles


def main() -> int:
    rays, rectangles, triangles = make_scene()
    rows = rt.run_cpu_python_reference(hello_world_kernel, rays=rays, triangles=triangles)

    if len(rows) != 1 or int(rows[0]["hit_count"]) != 2:
        raise SystemExit(f"unexpected RTDL result: {rows}")

    visible_rectangles = [rect for rect in rectangles if rect.y0 <= 0.0 <= rect.y1]
    if len(visible_rectangles) != 1:
        raise SystemExit(f"expected one visible rectangle, got {visible_rectangles}")

    print(visible_rectangles[0].label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
