from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import sys
import time
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (str(REPO_ROOT), str(SRC_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional fast path
    np = None  # type: ignore[assignment]

from examples.visual_demo.rtdl_spinning_ball_3d_demo import _background_pixel
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _clamp01
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _dot3
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _normalize3
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _project_world_to_screen
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _ray_sphere_intersection
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _run_backend_rows
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _write_ppm
from examples.visual_demo.rtdl_spinning_ball_3d_demo import make_camera_rays
from examples.visual_demo.rtdl_spinning_ball_3d_demo import make_uv_sphere_mesh
import rtdsl as rt


_STABLE_WORKER_STATE: dict[str, object] = {}
_STABLE_MIDNIGHT = (0.03, 0.08, 0.24)
_STABLE_DEEP_BLUE = (0.06, 0.19, 0.54)
_STABLE_STEEL = (0.10, 0.24, 0.60)


def _frame_light(phase: float) -> dict[str, object]:
    x = 68.0 - 136.0 * phase
    return {
        "position": (
            x,
            0.08,
            11.8,
        ),
        "color": (1.0, 0.86, 0.30),
        "intensity": 2.95,
    }


def _orbit_surface_color(normal: tuple[float, float, float]) -> tuple[float, float, float]:
    _, ny, nz = normal
    crown = _clamp01((ny + 0.65) / 1.65)
    side = _clamp01((nz + 1.0) * 0.5)
    base = tuple(
        _STABLE_MIDNIGHT[index] + (_STABLE_DEEP_BLUE[index] - _STABLE_MIDNIGHT[index]) * (0.35 + 0.30 * crown)
        for index in range(3)
    )
    return tuple(
        _clamp01(base[index] + (_STABLE_STEEL[index] - base[index]) * (0.10 * side))
        for index in range(3)
    )


def _stable_shade_hit(
    ray: rt.Ray3D,
    hit_point: tuple[float, float, float],
    *,
    center: tuple[float, float, float],
    light: dict[str, object],
    visibility: float = 1.0,
) -> tuple[int, int, int]:
    nx, ny, nz = _normalize3(
        hit_point[0] - center[0],
        hit_point[1] - center[1],
        hit_point[2] - center[2],
    )
    base = _orbit_surface_color((nx, ny, nz))
    view = _normalize3(-ray.dx, -ray.dy, -ray.dz)
    fresnel = (1.0 - max(0.0, _dot3(nx, ny, nz, view[0], view[1], view[2]))) ** 2.6
    upper_glow = _clamp01((ny + 0.55) / 1.55)
    lower_cool = _clamp01((0.15 - ny) / 1.15)

    lx, ly, lz = light["position"]  # type: ignore[index]
    ldx, ldy, ldz = _normalize3(lx - hit_point[0], ly - hit_point[1], lz - hit_point[2])
    lambert = max(0.0, _dot3(nx, ny, nz, ldx, ldy, ldz)) * visibility
    lr, lg, lb = light["color"]  # type: ignore[index]
    intensity = float(light.get("intensity", 1.0))  # type: ignore[call-arg]

    half_x, half_y, half_z = _normalize3(ldx + view[0], ldy + view[1], ldz + view[2])
    specular = intensity * (max(0.0, _dot3(nx, ny, nz, half_x, half_y, half_z)) ** 52.0)

    light_rgb = [
        0.10 + lambert * float(lr) * 1.08 * intensity,
        0.11 + lambert * float(lg) * 1.08 * intensity,
        0.15 + lambert * float(lb) * 1.08 * intensity,
    ]

    final = []
    for index in range(3):
        channel = base[index] * light_rgb[index]
        channel += fresnel * (0.14 if index == 2 else 0.10)
        channel += upper_glow * (0.03 if index == 0 else 0.05 if index == 1 else 0.08)
        channel += lower_cool * (0.00 if index == 0 else 0.01 if index == 1 else 0.05)
        channel += specular * (0.13 + 0.06 * index)
        final.append(int(round(_clamp01(channel) * 255.0)))
    return final[0], final[1], final[2]


def _light_facing_visibility(
    *,
    hit_point: tuple[float, float, float],
    center: tuple[float, float, float],
    light: dict[str, object],
) -> float:
    nx, ny, nz = _normalize3(
        hit_point[0] - center[0],
        hit_point[1] - center[1],
        hit_point[2] - center[2],
    )
    lx, ly, lz = light["position"]  # type: ignore[index]
    ldx, ldy, ldz = _normalize3(lx - hit_point[0], ly - hit_point[1], lz - hit_point[2])
    return max(0.0, _dot3(nx, ny, nz, ldx, ldy, ldz))


def _make_light_to_surface_shadow_ray(
    *,
    ray_id: int,
    hit_point: tuple[float, float, float],
    light: dict[str, object],
) -> rt.Ray3D:
    lx, ly, lz = light["position"]  # type: ignore[index]
    dx = hit_point[0] - lx
    dy = hit_point[1] - ly
    dz = hit_point[2] - lz
    distance = math.sqrt(max(1.0e-12, dx * dx + dy * dy + dz * dz))
    tmax = max(0.0, distance - max(3.0e-3, distance * 1.0e-5))
    return rt.Ray3D(
        id=ray_id,
        ox=lx,
        oy=ly,
        oz=lz,
        dx=dx / distance,
        dy=dy / distance,
        dz=dz / distance,
        tmax=tmax,
    )


def _make_background_image(width: int, height: int) -> Any:
    if np is not None:
        xs = np.linspace(0.0, 1.0, width, dtype=np.float32)
        ys = np.linspace(0.0, 1.0, height, dtype=np.float32)
        u, v = np.meshgrid(xs, ys)
        horizon = v
        vignette = 1.0 - np.minimum(1.0, np.sqrt((u - 0.5) ** 2 + (v - 0.46) ** 2) * 1.32)
        nebula = np.exp(-(((u - 0.34) ** 2) / 0.025 + ((v - 0.22) ** 2) / 0.008))
        bloom = np.exp(-(((u - 0.70) ** 2) / 0.040 + ((v - 0.30) ** 2) / 0.018))
        floor = np.exp(-(((v - 0.84) ** 2) / 0.010))
        red = 0.015 + 0.025 * horizon + 0.060 * vignette + 0.090 * nebula + 0.035 * floor
        green = 0.020 + 0.030 * horizon + 0.080 * vignette + 0.030 * nebula + 0.050 * bloom + 0.045 * floor
        blue = 0.060 + 0.120 * horizon + 0.160 * vignette + 0.060 * bloom + 0.055 * floor
        image = np.stack((red, green, blue), axis=-1)
        return np.clip(np.rint(image * 255.0), 0.0, 255.0).astype(np.uint8)
    return [[_background_pixel(px, py, width, height) for px in range(width)] for py in range(height)]


def _init_stable_worker(state: dict[str, object]) -> None:
    global _STABLE_WORKER_STATE
    _STABLE_WORKER_STATE = state


def _render_stable_frame(task: tuple[int, float]) -> dict[str, object]:
    frame_index, phase = task
    state = _STABLE_WORKER_STATE
    light = _frame_light(phase)
    source_image = state["background_image"]  # type: ignore[index]
    if np is not None and hasattr(source_image, "shape"):
        image = source_image.copy()
    else:
        image = [list(row) for row in source_image]  # type: ignore[arg-type]
    pending_hits = state["pending_hits"]  # type: ignore[assignment]
    center = state["center"]  # type: ignore[assignment]
    shadow_mode = str(state["shadow_mode"])  # type: ignore[index]
    backend = str(state["backend"])  # type: ignore[index]
    triangles = state["triangles"]  # type: ignore[assignment]

    shadow_rays: list[rt.Ray3D] = []
    shadow_lookup: dict[int, int] = {}
    shadow_candidates: dict[int, float] = {}
    shadow_query_seconds = 0.0
    if shadow_mode == "rtdl_light_to_surface":
        for _, _, ray, hit_point in pending_hits:
            facing = _light_facing_visibility(hit_point=hit_point, center=center, light=light)
            shadow_candidates[ray.id] = facing
            if facing <= 0.0:
                continue
            shadow_rays.append(
                _make_light_to_surface_shadow_ray(
                    ray_id=ray.id,
                    hit_point=hit_point,
                    light=light,
                )
            )
        if shadow_rays:
            shadow_started = time.perf_counter()
            shadow_rows = _run_backend_rows(backend, rays=tuple(shadow_rays), triangles=triangles)
            shadow_query_seconds = time.perf_counter() - shadow_started
            shadow_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in shadow_rows}

    shading_started = time.perf_counter()
    if np is not None and hasattr(image, "shape"):
        py = np.empty(len(pending_hits), dtype=np.int32)
        px = np.empty(len(pending_hits), dtype=np.int32)
        colors = np.empty((len(pending_hits), 3), dtype=np.uint8)
        for index, (row, col, ray, hit_point) in enumerate(pending_hits):
            py[index] = row
            px[index] = col
            visibility = 1.0
            if shadow_mode == "rtdl_light_to_surface":
                visibility = 0.0 if shadow_lookup.get(ray.id, 0) > 0 else (1.0 if shadow_candidates.get(ray.id, 0.0) > 0.0 else 0.0)
            colors[index] = _stable_shade_hit(ray, hit_point, center=center, light=light, visibility=visibility)
        image[py, px] = colors
    else:
        for py, px, ray, hit_point in pending_hits:
            visibility = 1.0
            if shadow_mode == "rtdl_light_to_surface":
                visibility = 0.0 if shadow_lookup.get(ray.id, 0) > 0 else (1.0 if shadow_candidates.get(ray.id, 0.0) > 0.0 else 0.0)
            image[py][px] = _stable_shade_hit(ray, hit_point, center=center, light=light, visibility=visibility)

    projected_center = state["projected_center"]  # type: ignore[assignment]
    width = int(state["width"])  # type: ignore[arg-type]
    height = int(state["height"])  # type: ignore[arg-type]
    if projected_center is not None:
        from examples.visual_demo.rtdl_spinning_ball_3d_demo import _paint_ground_shadow, _paint_halo

        _paint_ground_shadow(
            image,
            center_x=projected_center[0],
            center_y=min(height - 1.0, projected_center[1] + height * 0.24),
            radius_x=width * 0.19,
            radius_y=height * 0.060,
            alpha=0.42,
        )
        _paint_halo(
            image,
            center_x=projected_center[0],
            center_y=projected_center[1],
            radius=min(width, height) * 0.18,
            color=(76, 120, 255),
            alpha=0.14,
        )

    shading_seconds = time.perf_counter() - shading_started
    frame_path = Path(state["output_dir"]) / f"frame_{frame_index:03d}.ppm"  # type: ignore[arg-type]
    _write_ppm(frame_path, image)
    return {
        "frame_index": frame_index,
        "phase": phase,
        "frame_path": str(frame_path),
        "query_seconds": float(state["query_seconds"]) if frame_index == 0 else 0.0,  # type: ignore[arg-type]
        "shadow_query_seconds": shadow_query_seconds,
        "shading_seconds": shading_seconds,
        "rt_rows": int(state["rt_rows"]),  # type: ignore[arg-type]
        "shadow_rays": len(shadow_rays),
        "hit_pixels": int(state["hit_pixels"]),  # type: ignore[arg-type]
        "compare_backend": state["compare_summary"] if frame_index == 0 else None,  # type: ignore[index]
    }


def render_hidden_star_stable_ball_frames(
    *,
    backend: str,
    compare_backend: str | None,
    width: int,
    height: int,
    latitude_bands: int,
    longitude_bands: int,
    frame_count: int,
    output_dir: Path,
    jobs: int = 1,
    shadow_mode: str = "analytic",
) -> dict[str, object]:
    wall_started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    eye = (0.0, 0.16, 6.1)
    target = (0.0, 0.08, 0.0)
    up_hint = (0.0, 1.0, 0.0)
    radius = 1.46
    center = (0.0, 0.08, 0.0)
    fov_y = 28.0

    triangles = make_uv_sphere_mesh(
        latitude_bands=latitude_bands,
        longitude_bands=longitude_bands,
        radius=radius,
        center=center,
    )
    rays = make_camera_rays(
        width=width,
        height=height,
        eye=eye,
        target=target,
        up_hint=up_hint,
        fov_y_degrees=fov_y,
    )

    query_started = time.perf_counter()
    rows = _run_backend_rows(backend, rays=rays, triangles=triangles)
    query_seconds = time.perf_counter() - query_started
    hit_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in rows}

    compare_summary = None
    if compare_backend and compare_backend != "none":
        compare_rows = _run_backend_rows(compare_backend, rays=rays, triangles=triangles)
        compare_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in compare_rows}
        compare_summary = {"backend": compare_backend, "matches": compare_lookup == hit_lookup}

    background_image = _make_background_image(width, height)
    pending_hits: list[tuple[int, int, rt.Ray3D, tuple[float, float, float]]] = []
    hit_pixels = 0
    for py in range(height):
        for px in range(width):
            ray = rays[py * width + px]
            if hit_lookup.get(ray.id, 0) <= 0:
                continue
            intersection = _ray_sphere_intersection(ray, center=center, radius=radius)
            if intersection is None:
                continue
            _, hit_point = intersection
            pending_hits.append((py, px, ray, hit_point))
            hit_pixels += 1

    projected_center = _project_world_to_screen(
        center,
        eye=eye,
        target=target,
        up_hint=up_hint,
        width=width,
        height=height,
        fov_y_degrees=fov_y,
    )

    worker_state: dict[str, object] = {
        "backend": backend,
        "background_image": background_image,
        "center": center,
        "pending_hits": pending_hits,
        "projected_center": projected_center,
        "width": width,
        "height": height,
        "output_dir": output_dir,
        "query_seconds": query_seconds,
        "rt_rows": len(rows),
        "hit_pixels": hit_pixels,
        "compare_summary": compare_summary,
        "shadow_mode": shadow_mode,
        "triangles": triangles,
    }
    tasks = [(frame_index, frame_index / max(1, frame_count - 1)) for frame_index in range(frame_count)]
    if jobs <= 1:
        _init_stable_worker(worker_state)
        summary_frames = [_render_stable_frame(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs, initializer=_init_stable_worker, initargs=(worker_state,)) as executor:
            summary_frames = list(executor.map(_render_stable_frame, tasks))
    summary_frames.sort(key=lambda row: int(row["frame_index"]))

    total_shading_seconds = sum(float(row["shading_seconds"]) for row in summary_frames)
    total_shadow_query_seconds = sum(float(row["shadow_query_seconds"]) for row in summary_frames)
    light_layout = "single_analytic" if shadow_mode == "analytic" else "single_rtdl_light_to_surface_shadow"
    summary = {
        "backend": backend,
        "image_width": width,
        "image_height": height,
        "frame_count": frame_count,
        "jobs": jobs,
        "light_count": 1,
        "light_layout": light_layout,
        "shadow_mode": shadow_mode,
        "numpy_fast_path": np is not None,
        "show_light_source": False,
        "phase_mode": "uniform",
        "triangle_count": len(triangles),
        "latitude_bands": latitude_bands,
        "longitude_bands": longitude_bands,
        "total_query_seconds": query_seconds,
        "total_shadow_query_seconds": total_shadow_query_seconds,
        "total_shading_seconds": total_shading_seconds,
        "wall_clock_seconds": time.perf_counter() - wall_started,
        "query_share": (query_seconds + total_shadow_query_seconds)
        / max(1.0e-9, query_seconds + total_shadow_query_seconds + total_shading_seconds),
        "frames": summary_frames,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a stable hidden-star Earth ball using RTDL camera hits and optional RTDL shadow visibility.")
    parser.add_argument("--backend", default="embree")
    parser.add_argument("--compare-backend", default="none")
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--height", type=int, default=256)
    parser.add_argument("--latitude-bands", type=int, default=80)
    parser.add_argument("--longitude-bands", type=int, default=160)
    parser.add_argument("--frames", type=int, default=320)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--shadow-mode", choices=("analytic", "rtdl_light_to_surface"), default="analytic")
    parser.add_argument("--output-dir", type=Path, default=Path("build/win_embree_hidden_star_earth_stable"))
    args = parser.parse_args()

    summary = render_hidden_star_stable_ball_frames(
        backend=args.backend,
        compare_backend=args.compare_backend,
        width=args.width,
        height=args.height,
        latitude_bands=args.latitude_bands,
        longitude_bands=args.longitude_bands,
        frame_count=args.frames,
        output_dir=args.output_dir,
        jobs=args.jobs,
        shadow_mode=args.shadow_mode,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
