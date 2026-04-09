from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (str(REPO_ROOT), str(SRC_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_hitcount_demo():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def make_disk_mesh(
    *,
    triangle_count: int = 128,
    radius: float = 1.0,
    center_x: float = 0.0,
    center_y: float = 0.0,
) -> tuple[rt.Triangle, ...]:
    triangles: list[rt.Triangle] = []
    for index in range(triangle_count):
        a0 = (index / triangle_count) * math.tau
        a1 = ((index + 1) / triangle_count) * math.tau
        triangles.append(
            rt.Triangle(
                id=index,
                x0=center_x,
                y0=center_y,
                x1=center_x + math.cos(a0) * radius,
                y1=center_y + math.sin(a0) * radius,
                x2=center_x + math.cos(a1) * radius,
                y2=center_y + math.sin(a1) * radius,
            )
        )
    return tuple(triangles)


def make_scanline_rays(
    *,
    width: int,
    height: int,
    scene_left: float,
    scene_right: float,
    scene_bottom: float,
    scene_top: float,
) -> tuple[rt.Ray2D, ...]:
    rays: list[rt.Ray2D] = []
    for row in range(height):
        y = scene_top - ((row + 0.5) / height) * (scene_top - scene_bottom)
        rays.append(
            rt.Ray2D(
                id=row,
                ox=scene_left,
                oy=y,
                dx=1.0,
                dy=0.0,
                tmax=scene_right - scene_left,
            )
        )
    return tuple(rays)


def _edge_intersection_x(y: float, ax: float, ay: float, bx: float, by: float) -> float | None:
    if math.isclose(ay, by, abs_tol=1.0e-9):
        return None
    if y < min(ay, by) or y > max(ay, by):
        return None
    t = (y - ay) / (by - ay)
    if t < 0.0 or t > 1.0:
        return None
    return ax + t * (bx - ax)


def _scanline_span(triangles: tuple[rt.Triangle, ...], y: float) -> tuple[float, float] | None:
    xs: list[float] = []
    seen: set[int] = set()
    for triangle in triangles:
        edges = (
            (triangle.x0, triangle.y0, triangle.x1, triangle.y1),
            (triangle.x1, triangle.y1, triangle.x2, triangle.y2),
            (triangle.x2, triangle.y2, triangle.x0, triangle.y0),
        )
        for edge in edges:
            x = _edge_intersection_x(y, *edge)
            if x is None:
                continue
            key = round(x * 1_000_000)
            if key in seen:
                continue
            seen.add(key)
            xs.append(x)
    if len(xs) < 2:
        return None
    return min(xs), max(xs)


def _brightness_at(
    x: float,
    y: float,
    *,
    center_x: float,
    center_y: float,
    radius: float,
    light_dx: float,
    light_dy: float,
    ambient: float,
) -> float:
    nx = (x - center_x) / radius
    ny = (y - center_y) / radius
    normal_len = math.hypot(nx, ny)
    if normal_len <= 1.0e-9:
        return ambient
    nx /= normal_len
    ny /= normal_len
    lambert = max(0.0, nx * light_dx + ny * light_dy)
    return min(1.0, max(ambient, ambient + (1.0 - ambient) * lambert))


def _render_ascii(brightness_rows: list[list[float]]) -> str:
    palette = " .:-=+*#%@"
    lines: list[str] = []
    for row in brightness_rows:
        chars = []
        for value in row:
            idx = min(len(palette) - 1, max(0, int(round(value * (len(palette) - 1)))))
            chars.append(palette[idx])
        lines.append("".join(chars))
    return "\n".join(lines)


def _write_pgm(path: Path, brightness_rows: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    height = len(brightness_rows)
    width = len(brightness_rows[0]) if height else 0
    with path.open("w", encoding="ascii") as handle:
        handle.write(f"P2\n{width} {height}\n255\n")
        for row in brightness_rows:
            handle.write(" ".join(str(int(round(value * 255.0))) for value in row))
            handle.write("\n")


def _select_runner(name: str):
    runners = {
        "cpu_python_reference": rt.run_cpu_python_reference,
        "cpu": rt.run_cpu,
        "embree": rt.run_embree,
        "optix": rt.run_optix,
        "vulkan": rt.run_vulkan,
    }
    try:
        return runners[name]
    except KeyError as exc:
        raise ValueError(f"unsupported backend {name!r}") from exc


def render_lit_ball(
    *,
    backend: str = "cpu_python_reference",
    compare_backend: str | None = "cpu",
    width: int = 72,
    height: int = 36,
    triangle_count: int = 128,
    radius: float = 1.0,
    ambient: float = 0.15,
    light_dx: float = -0.7,
    light_dy: float = 1.0,
    output_path: Path = Path("build/rtdl_lit_ball_demo.pgm"),
) -> dict[str, object]:
    light_len = math.hypot(light_dx, light_dy)
    light_dx /= light_len
    light_dy /= light_len

    center_x = 0.0
    center_y = 0.0
    scene_left = -1.35
    scene_right = 1.35
    scene_bottom = -1.15
    scene_top = 1.15

    triangles = make_disk_mesh(
        triangle_count=triangle_count,
        radius=radius,
        center_x=center_x,
        center_y=center_y,
    )
    rays = make_scanline_rays(
        width=width,
        height=height,
        scene_left=scene_left,
        scene_right=scene_right,
        scene_bottom=scene_bottom,
        scene_top=scene_top,
    )

    runner = _select_runner(backend)
    rows = runner(ray_triangle_hitcount_demo, rays=rays, triangles=triangles)
    hit_counts = {int(row["ray_id"]): int(row["hit_count"]) for row in rows}

    comparison = None
    if compare_backend is not None:
        compare_rows = _select_runner(compare_backend)(ray_triangle_hitcount_demo, rays=rays, triangles=triangles)
        compare_counts = {int(row["ray_id"]): int(row["hit_count"]) for row in compare_rows}
        comparison = {
            "backend": compare_backend,
            "matches": compare_counts == hit_counts,
        }

    brightness_rows: list[list[float]] = []
    hit_rows = 0
    for row in range(height):
        y = scene_top - ((row + 0.5) / height) * (scene_top - scene_bottom)
        span = _scanline_span(triangles, y)
        row_values = [0.0 for _ in range(width)]
        if hit_counts.get(row, 0) > 0 and span is not None:
            hit_rows += 1
            left_x, right_x = span
            for col in range(width):
                x = scene_left + ((col + 0.5) / width) * (scene_right - scene_left)
                if x < left_x or x > right_x:
                    continue
                row_values[col] = _brightness_at(
                    x,
                    y,
                    center_x=center_x,
                    center_y=center_y,
                    radius=radius,
                    light_dx=light_dx,
                    light_dy=light_dy,
                    ambient=ambient,
                )
        brightness_rows.append(row_values)

    ascii_art = _render_ascii(brightness_rows)
    _write_pgm(output_path, brightness_rows)
    return {
        "backend": backend,
        "compare_backend": comparison,
        "triangle_count": triangle_count,
        "image_width": width,
        "image_height": height,
        "rt_rows": len(rows),
        "scanlines_with_hits": hit_rows,
        "pgm_path": str(output_path),
        "ascii_art": ascii_art,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render a lit 2D ball slice from a dense triangle fan. "
            "RTDL provides per-scanline ray/triangle hit relationships; "
            "Python computes the visible span and brightness."
        )
    )
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    parser.add_argument(
        "--compare-backend",
        default="cpu",
        choices=("none", "cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    parser.add_argument("--width", type=int, default=72)
    parser.add_argument("--height", type=int, default=36)
    parser.add_argument("--triangles", type=int, default=128)
    parser.add_argument("--output", type=Path, default=Path("build/rtdl_lit_ball_demo.pgm"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    compare_backend = None if args.compare_backend == "none" else args.compare_backend
    payload = render_lit_ball(
        backend=args.backend,
        compare_backend=compare_backend,
        width=args.width,
        height=args.height,
        triangle_count=args.triangles,
        output_path=args.output,
    )
    print(
        f"RTDL lit-ball demo backend={payload['backend']} "
        f"triangles={payload['triangle_count']} "
        f"scanlines_with_hits={payload['scanlines_with_hits']} "
        f"pgm={payload['pgm_path']}"
    )
    if payload["compare_backend"] is not None:
        compare = payload["compare_backend"]
        print(
            "backend comparison "
            f"{payload['backend']} vs {compare['backend']}: "
            f"{'match' if compare['matches'] else 'DIFFER'}"
        )
    print()
    print(payload["ascii_art"])


if __name__ == "__main__":
    main()
