from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

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
    triangle_count: int,
    radius: float,
    center_x: float,
    center_y: float,
) -> tuple[rt.Triangle, ...]:
    triangles: list[rt.Triangle] = []
    for index in range(triangle_count):
        angle0 = (index / triangle_count) * math.tau
        angle1 = ((index + 1) / triangle_count) * math.tau
        triangles.append(
            rt.Triangle(
                id=index,
                x0=center_x,
                y0=center_y,
                x1=center_x + math.cos(angle0) * radius,
                y1=center_y + math.sin(angle0) * radius,
                x2=center_x + math.cos(angle1) * radius,
                y2=center_y + math.sin(angle1) * radius,
            )
        )
    return tuple(triangles)


def make_scanline_rays(
    *,
    sample_rows: int,
    scene_left: float,
    scene_right: float,
    scene_bottom: float,
    scene_top: float,
) -> tuple[rt.Ray2D, ...]:
    rays: list[rt.Ray2D] = []
    for row in range(sample_rows):
        y = scene_top - ((row + 0.5) / sample_rows) * (scene_top - scene_bottom)
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


def _sphere_normal(x: float, y: float, *, center_x: float, center_y: float, radius: float) -> tuple[float, float, float] | None:
    nx = (x - center_x) / radius
    ny = (y - center_y) / radius
    d2 = nx * nx + ny * ny
    if d2 > 1.0:
        return None
    nz = math.sqrt(max(0.0, 1.0 - d2))
    inv = 1.0 / math.sqrt(max(1.0e-9, d2 + nz * nz))
    return nx * inv, ny * inv, nz * inv


def _normalize3(x: float, y: float, z: float) -> tuple[float, float, float]:
    length = math.sqrt(max(1.0e-9, x * x + y * y + z * z))
    return x / length, y / length, z / length


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _mix(a: float, b: float, t: float) -> float:
    return a * (1.0 - t) + b * t


def _blend_rgb(
    base: tuple[int, int, int],
    overlay: tuple[int, int, int],
    alpha: float,
) -> tuple[int, int, int]:
    alpha = _clamp01(alpha)
    return (
        int(round(_mix(base[0], overlay[0], alpha))),
        int(round(_mix(base[1], overlay[1], alpha))),
        int(round(_mix(base[2], overlay[2], alpha))),
    )


def _surface_color(nx: float, ny: float, nz: float, spin_phase: float) -> tuple[float, float, float]:
    longitude = math.atan2(ny, nx) + spin_phase
    latitude = math.asin(max(-1.0, min(1.0, nz)))
    pearl = 0.5 + 0.5 * math.sin(longitude * 2.1 + latitude * 1.7)
    drift = 0.5 + 0.5 * math.sin(longitude * 0.8 - latitude * 2.4 + spin_phase * 0.6)
    edge_cool = (1.0 - max(0.0, nz)) ** 1.6

    deep_r, deep_g, deep_b = 0.10, 0.18, 0.33
    warm_r, warm_g, warm_b = 0.87, 0.34, 0.54
    cool_r, cool_g, cool_b = 0.18, 0.78, 0.86

    base_r = _mix(deep_r, warm_r, pearl)
    base_g = _mix(deep_g, warm_g, pearl)
    base_b = _mix(deep_b, warm_b, pearl)

    base_r = _mix(base_r, cool_r, 0.28 * drift + 0.20 * edge_cool)
    base_g = _mix(base_g, cool_g, 0.28 * drift + 0.20 * edge_cool)
    base_b = _mix(base_b, cool_b, 0.28 * drift + 0.20 * edge_cool)
    return _clamp01(base_r), _clamp01(base_g), _clamp01(base_b)


def _background_pixel(x: float, y: float, *, scene_left: float, scene_right: float, scene_bottom: float, scene_top: float) -> tuple[int, int, int]:
    u = (x - scene_left) / (scene_right - scene_left)
    v = (y - scene_bottom) / (scene_top - scene_bottom)
    cx = (u - 0.5) * 1.35
    cy = (v - 0.52) * 1.10
    dist = math.sqrt(cx * cx + cy * cy)
    vignette = _clamp01(1.0 - dist)
    horizon = 0.35 + 0.65 * v
    r = _mix(0.02, 0.08, horizon) * (0.65 + 0.35 * vignette)
    g = _mix(0.03, 0.09, horizon) * (0.65 + 0.35 * vignette)
    b = _mix(0.08, 0.20, horizon) * (0.72 + 0.28 * vignette)
    return int(round(_clamp01(r) * 255.0)), int(round(_clamp01(g) * 255.0)), int(round(_clamp01(b) * 255.0))


def _overlay_light_scene(
    background: tuple[int, int, int],
    x: float,
    y: float,
    *,
    lights: tuple[dict[str, tuple[float, float, float] | float], ...],
    phase: float,
    center_x: float,
    center_y: float,
    radius: float,
) -> tuple[int, int, int]:
    color = background

    # Two visible orbiting lights with a short fading trajectory.
    for light_index, light in enumerate(lights[:2]):
        lr, lg, lb = light["color"]  # type: ignore[index]
        orb_rgb = (
            int(round(_clamp01(lr) * 255.0)),
            int(round(_clamp01(lg) * 255.0)),
            int(round(_clamp01(lb) * 255.0)),
        )

        for step in range(8, 0, -1):
            trail_phase = (phase - (step / 90.0)) % 1.0
            trail_lights = _frame_lights(trail_phase)
            tx, ty, _ = trail_lights[light_index]["position"]  # type: ignore[index]
            trail_dx = x - tx
            trail_dy = y - ty
            trail_d2 = trail_dx * trail_dx + trail_dy * trail_dy
            trail_alpha = (1.0 - step / 9.0) * 0.14 * math.exp(-trail_d2 / 0.010)
            if trail_alpha > 1.0e-4:
                color = _blend_rgb(color, orb_rgb, trail_alpha)

        lx, ly, _ = light["position"]  # type: ignore[index]
        dx = x - lx
        dy = y - ly
        d2 = dx * dx + dy * dy
        glow_alpha = 0.55 * math.exp(-d2 / 0.020)
        core_alpha = 0.95 * math.exp(-d2 / 0.0028)
        if glow_alpha > 1.0e-4:
            color = _blend_rgb(color, orb_rgb, glow_alpha)
        if core_alpha > 1.0e-4:
            color = _blend_rgb(color, (255, 255, 255), core_alpha)

    # Subtle atmospheric halo behind the ball.
    hx = (x - center_x) / (radius * 1.9)
    hy = (y - center_y) / (radius * 1.9)
    halo = math.exp(-(hx * hx + hy * hy) / 0.9) * 0.08
    if halo > 1.0e-4:
        color = _blend_rgb(color, (70, 110, 170), halo)
    return color


def _shade_pixel(
    x: float,
    y: float,
    *,
    center_x: float,
    center_y: float,
    radius: float,
    spin_phase: float,
    lights: tuple[dict[str, tuple[float, float, float] | float], ...],
    ambient: float,
) -> tuple[int, int, int]:
    normal = _sphere_normal(x, y, center_x=center_x, center_y=center_y, radius=radius)
    if normal is None:
        return (0, 0, 0)
    nx, ny, nz = normal
    base_r, base_g, base_b = _surface_color(nx, ny, nz, spin_phase)
    view_x, view_y, view_z = 0.0, 0.0, 1.0

    light_r = ambient
    light_g = ambient
    light_b = ambient
    specular = 0.0
    rim = (1.0 - max(0.0, nz)) ** 2.2
    px = (x - center_x) / radius
    py = (y - center_y) / radius
    pz = nz
    for light in lights:
        lx, ly, lz = light["position"]  # type: ignore[index]
        dx, dy, dz = _normalize3(lx - px, ly - py, lz - pz)
        lambert = max(0.0, nx * dx + ny * dy + nz * dz)
        if lambert <= 0.0:
            continue
        cr, cg, cb = light["color"]  # type: ignore[index]
        strength = float(light["strength"])  # type: ignore[arg-type]
        light_r += lambert * cr * strength
        light_g += lambert * cg * strength
        light_b += lambert * cb * strength
        rx = 2.0 * lambert * nx - dx
        ry = 2.0 * lambert * ny - dy
        rz = 2.0 * lambert * nz - dz
        specular += max(0.0, rx * view_x + ry * view_y + rz * view_z) ** 28 * 0.42 * strength

    r = _clamp01(base_r * light_r + specular + rim * 0.08)
    g = _clamp01(base_g * light_g + specular + rim * 0.12)
    b = _clamp01(base_b * light_b + specular + rim * 0.20)
    return int(round(r * 255.0)), int(round(g * 255.0)), int(round(b * 255.0))


def _write_ppm(path: Path, rgb_rows: list[list[tuple[int, int, int]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    height = len(rgb_rows)
    width = len(rgb_rows[0]) if height else 0
    with path.open("w", encoding="ascii") as handle:
        handle.write(f"P3\n{width} {height}\n255\n")
        for row in rgb_rows:
            values: list[str] = []
            for red, green, blue in row:
                values.extend((str(red), str(green), str(blue)))
            handle.write(" ".join(values))
            handle.write("\n")


def _apply_shadow(
    background: tuple[int, int, int],
    x: float,
    y: float,
    *,
    center_x: float,
    center_y: float,
    radius: float,
) -> tuple[int, int, int]:
    sx = (x - center_x) / (radius * 1.28)
    sy = (y - (center_y - radius * 0.92)) / (radius * 0.34)
    d2 = sx * sx + sy * sy
    if d2 >= 1.0:
        return background
    shadow = (1.0 - d2) ** 1.8 * 0.42
    red, green, blue = background
    return (
        int(round(red * (1.0 - shadow))),
        int(round(green * (1.0 - shadow))),
        int(round(blue * (1.0 - shadow))),
    )


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


def _frame_lights(phase: float) -> tuple[dict[str, tuple[float, float, float] | float], ...]:
    return (
        {
            "position": (
                math.cos(phase * math.tau) * 1.9,
                math.sin(phase * math.tau) * 1.1,
                1.8 + 0.2 * math.sin(phase * math.tau * 2.0),
            ),
            "color": (1.0, 0.35, 0.30),
            "strength": 1.15,
        },
        {
            "position": (
                math.cos(phase * math.tau + 2.1) * 1.6,
                math.sin(phase * math.tau + 2.1) * 1.5,
                1.4 + 0.3 * math.cos(phase * math.tau * 1.5),
            ),
            "color": (0.25, 0.85, 1.0),
            "strength": 0.95,
        },
        {
            "position": (
                math.cos(phase * math.tau + 4.0) * 2.2,
                math.sin(phase * math.tau + 4.0) * 0.9,
                1.1 + 0.25 * math.sin(phase * math.tau * 3.0),
            ),
            "color": (0.85, 0.35, 1.0),
            "strength": 0.55,
        },
    )


def render_orbit_lights_ball_frames(
    *,
    backend: str = "cpu_python_reference",
    compare_backend: str | None = "cpu",
    width: int = 256,
    height: int = 256,
    triangle_count: int = 4096,
    frame_count: int = 24,
    vertical_samples: int = 6,
    output_dir: Path = Path("build/rtdl_orbit_lights_ball_demo"),
    ambient: float = 0.10,
) -> dict[str, object]:
    scene_left = -1.55
    scene_right = 1.55
    scene_bottom = -1.45
    scene_top = 1.45
    runner = _select_runner(backend)
    sample_rows = height * vertical_samples
    rays = make_scanline_rays(
        sample_rows=sample_rows,
        scene_left=scene_left,
        scene_right=scene_right,
        scene_bottom=scene_bottom,
        scene_top=scene_top,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    frame_summaries: list[dict[str, object]] = []
    total_query_seconds = 0.0
    total_shading_seconds = 0.0

    for frame_index in range(frame_count):
        phase = frame_index / max(1, frame_count)
        center_x = 0.16 * math.cos(phase * math.tau * 0.8)
        center_y = 0.10 * math.sin(phase * math.tau * 1.3)
        radius = 0.92 + 0.05 * math.sin(phase * math.tau * 1.1)
        spin_phase = phase * math.tau * 2.0
        triangles = make_disk_mesh(
            triangle_count=triangle_count,
            radius=radius,
            center_x=center_x,
            center_y=center_y,
        )

        query_start = time.perf_counter()
        rows = runner(ray_triangle_hitcount_demo, rays=rays, triangles=triangles)
        query_seconds = time.perf_counter() - query_start
        total_query_seconds += query_seconds
        hit_counts = {int(row["ray_id"]): int(row["hit_count"]) for row in rows}
        sample_spans: list[tuple[float, float] | None] = []
        for sample_row in range(sample_rows):
            y = scene_top - ((sample_row + 0.5) / sample_rows) * (scene_top - scene_bottom)
            if hit_counts.get(sample_row, 0) <= 0:
                sample_spans.append(None)
                continue
            sample_spans.append(_scanline_span(triangles, y))

        comparison = None
        if compare_backend is not None:
            compare_rows = _select_runner(compare_backend)(ray_triangle_hitcount_demo, rays=rays, triangles=triangles)
            compare_counts = {int(row["ray_id"]): int(row["hit_count"]) for row in compare_rows}
            comparison = {
                "backend": compare_backend,
                "matches": compare_counts == hit_counts,
            }

        lights = _frame_lights(phase)
        shading_start = time.perf_counter()
        rgb_rows: list[list[tuple[int, int, int]]] = []
        sample_hit_rows = sum(1 for row_id in range(sample_rows) if hit_counts.get(row_id, 0) > 0)
        for row in range(height):
            row_pixels: list[tuple[int, int, int]] = []
            center_sample_y = scene_top - (((row * vertical_samples) + 0.5 * vertical_samples) / sample_rows) * (scene_top - scene_bottom)
            for col in range(width):
                x = scene_left + ((col + 0.5) / width) * (scene_right - scene_left)
                background = _apply_shadow(
                    _background_pixel(
                        x,
                        center_sample_y,
                        scene_left=scene_left,
                        scene_right=scene_right,
                        scene_bottom=scene_bottom,
                        scene_top=scene_top,
                    ),
                    x,
                    center_sample_y,
                    center_x=center_x,
                    center_y=center_y,
                    radius=radius,
                )
                background = _overlay_light_scene(
                    background,
                    x,
                    center_sample_y,
                    lights=lights,
                    phase=phase,
                    center_x=center_x,
                    center_y=center_y,
                    radius=radius,
                )
                red_acc = 0
                green_acc = 0
                blue_acc = 0
                covered = 0
                for sample_index in range(vertical_samples):
                    sample_row = row * vertical_samples + sample_index
                    y = scene_top - ((sample_row + 0.5) / sample_rows) * (scene_top - scene_bottom)
                    span = sample_spans[sample_row]
                    if hit_counts.get(sample_row, 0) <= 0 or span is None:
                        continue
                    left_x, right_x = span
                    if x < left_x or x > right_x:
                        continue
                    covered += 1
                    red, green, blue = _shade_pixel(
                        x,
                        y,
                        center_x=center_x,
                        center_y=center_y,
                        radius=radius,
                        spin_phase=spin_phase,
                        lights=lights,
                        ambient=ambient,
                    )
                    red_acc += red
                    green_acc += green
                    blue_acc += blue
                if covered == 0:
                    row_pixels.append(background)
                else:
                    row_pixels.append(
                        (
                            int(round(red_acc / covered)),
                            int(round(green_acc / covered)),
                            int(round(blue_acc / covered)),
                        )
                    )
            rgb_rows.append(row_pixels)
        shading_seconds = time.perf_counter() - shading_start
        total_shading_seconds += shading_seconds

        frame_path = output_dir / f"frame_{frame_index:03d}.ppm"
        _write_ppm(frame_path, rgb_rows)
        frame_summaries.append(
            {
                "frame_index": frame_index,
                "phase": phase,
                "frame_path": str(frame_path),
                "query_seconds": query_seconds,
                "shading_seconds": shading_seconds,
                "rt_rows": len(rows),
                "sample_rows_with_hits": sample_hit_rows,
                "compare_backend": comparison,
            }
        )

    summary = {
        "backend": backend,
        "compare_backend": compare_backend,
        "frame_count": frame_count,
        "image_width": width,
        "image_height": height,
        "vertical_samples": vertical_samples,
        "triangle_count": triangle_count,
        "output_dir": str(output_dir),
        "total_query_seconds": total_query_seconds,
        "total_shading_seconds": total_shading_seconds,
        "query_share": (
            total_query_seconds / max(1.0e-9, total_query_seconds + total_shading_seconds)
        ),
        "frames": frame_summaries,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render animated color PPM frames of a multi-light ball. "
            "RTDL performs dense scanline ray/triangle hit queries; "
            "Python performs shading and frame writing."
        )
    )
    parser.add_argument("--backend", default="cpu_python_reference")
    parser.add_argument("--compare-backend", default="cpu")
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--height", type=int, default=256)
    parser.add_argument("--triangles", type=int, default=4096)
    parser.add_argument("--frames", type=int, default=24)
    parser.add_argument("--vertical-samples", type=int, default=6)
    parser.add_argument("--output-dir", type=Path, default=Path("build/rtdl_orbit_lights_ball_demo"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    compare_backend = None if str(args.compare_backend).lower() == "none" else args.compare_backend
    summary = render_orbit_lights_ball_frames(
        backend=args.backend,
        compare_backend=compare_backend,
        width=args.width,
        height=args.height,
        triangle_count=args.triangles,
        frame_count=args.frames,
        vertical_samples=args.vertical_samples,
        output_dir=args.output_dir,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
