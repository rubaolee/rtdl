from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import sys
import time
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (str(REPO_ROOT), str(SRC_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import rtdsl as rt

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional fast path
    np = None  # type: ignore[assignment]

from examples.rtdl_spinning_ball_3d_demo import _background_pixel
from examples.rtdl_spinning_ball_3d_demo import _paint_disc
from examples.rtdl_spinning_ball_3d_demo import _paint_ellipse
from examples.rtdl_spinning_ball_3d_demo import _paint_ground_shadow
from examples.rtdl_spinning_ball_3d_demo import _paint_halo
from examples.rtdl_spinning_ball_3d_demo import _project_world_to_screen
from examples.rtdl_spinning_ball_3d_demo import _ray_sphere_intersection
from examples.rtdl_spinning_ball_3d_demo import _run_backend_rows
from examples.rtdl_spinning_ball_3d_demo import _shade_hit
from examples.rtdl_spinning_ball_3d_demo import _write_ppm
from examples.rtdl_spinning_ball_3d_demo import make_camera_rays
from examples.rtdl_spinning_ball_3d_demo import make_uv_sphere_mesh


_ORBIT_WORKER_STATE: dict[str, object] = {}


def _orbit_phase_samples(frame_count: int) -> tuple[float, ...]:
    if frame_count <= 1:
        return (0.0,)
    weights: list[float] = []
    steps = 4096
    for index in range(steps):
        phase = index / steps
        angle = phase * math.tau
        front = max(0.0, math.sin(angle))
        near_front = max(0.0, math.sin(angle - 0.12 * math.pi))
        weights.append(0.10 + 1.55 * front + 0.65 * near_front)
    total = sum(weights)
    cumulative: list[float] = []
    acc = 0.0
    for weight in weights:
        acc += weight
        cumulative.append(acc / total)
    phases: list[float] = []
    target_count = frame_count
    for frame_index in range(target_count):
        target = frame_index / max(1, target_count - 1)
        low = 0
        high = len(cumulative) - 1
        while low < high:
            mid = (low + high) // 2
            if cumulative[mid] < target:
                low = mid + 1
            else:
                high = mid
        phases.append(low / steps)
    return tuple(phases)


def _frame_light(phase: float) -> dict[str, object]:
    angle = phase * math.tau
    # Tilt the sun path so the visible highlight travels from upper-right
    # toward lower-left instead of reading as a mostly horizontal sweep.
    diag = math.cos(angle)
    return {
        "position": (
            math.cos(angle) * 36.0,
            4.0 + diag * 10.5,
            math.sin(angle) * 36.0,
        ),
        "color": (1.0, 0.96, 0.84),
        "intensity": 2.2,
        "display_color": (255, 240, 205),
    }


def _make_shadow_rays(
    *,
    ray: rt.Ray3D,
    hit_point: tuple[float, float, float],
    center: tuple[float, float, float],
    light: dict[str, object],
    base_id: int,
) -> tuple[rt.Ray3D, ...]:
    nx = hit_point[0] - center[0]
    ny = hit_point[1] - center[1]
    nz = hit_point[2] - center[2]
    length = math.sqrt(max(1.0e-12, nx * nx + ny * ny + nz * nz))
    origin = (
        hit_point[0] + (nx / length) * 1.0e-3,
        hit_point[1] + (ny / length) * 1.0e-3,
        hit_point[2] + (nz / length) * 1.0e-3,
    )
    lx, ly, lz = light["position"]  # type: ignore[index]
    dx = lx - origin[0]
    dy = ly - origin[1]
    dz = lz - origin[2]
    distance = math.sqrt(max(1.0e-12, dx * dx + dy * dy + dz * dz))
    return (
        rt.Ray3D(
            id=base_id,
            ox=origin[0],
            oy=origin[1],
            oz=origin[2],
            dx=dx / distance,
            dy=dy / distance,
            dz=dz / distance,
            tmax=max(0.0, distance - 2.0e-3),
        ),
    )


def _light_visibility_to_camera(
    *,
    light_position: tuple[float, float, float],
    eye: tuple[float, float, float],
    center: tuple[float, float, float],
    radius: float,
) -> float:
    dx = light_position[0] - eye[0]
    dy = light_position[1] - eye[1]
    dz = light_position[2] - eye[2]
    distance = math.sqrt(max(1.0e-12, dx * dx + dy * dy + dz * dz))
    probe = rt.Ray3D(
        id=0,
        ox=eye[0],
        oy=eye[1],
        oz=eye[2],
        dx=dx / distance,
        dy=dy / distance,
        dz=dz / distance,
        tmax=max(0.0, distance - 4.0e-3),
    )
    hit = _ray_sphere_intersection(probe, center=center, radius=radius)
    if hit is not None:
        return 0.0
    return 1.0


def _overlay_star_and_ground(
    image: list[list[tuple[int, int, int]]],
    *,
    light: dict[str, object],
    eye: tuple[float, float, float],
    target: tuple[float, float, float],
    up_hint: tuple[float, float, float],
    width: int,
    height: int,
    fov_y_degrees: float,
    center: tuple[float, float, float],
    radius: float,
    show_light_source: bool,
) -> None:
    light_position = light["position"]  # type: ignore[index]
    color = tuple(light.get("display_color", (255, 240, 205)))  # type: ignore[arg-type]
    visibility = _light_visibility_to_camera(
        light_position=light_position,  # type: ignore[arg-type]
        eye=eye,
        center=center,
        radius=radius,
    )
    projected = _project_world_to_screen(
        light_position,  # type: ignore[arg-type]
        eye=eye,
        target=target,
        up_hint=up_hint,
        width=width,
        height=height,
        fov_y_degrees=fov_y_degrees,
    )
    if show_light_source and projected is not None and visibility > 0.0:
        _paint_disc(image, projected[0], projected[1], 34.0, color, 0.16)
        _paint_disc(image, projected[0], projected[1], 18.0, color, 0.42)
        _paint_disc(image, projected[0], projected[1], 7.5, (255, 250, 238), 0.96)
        _paint_halo(
            image,
            center_x=projected[0],
            center_y=projected[1],
            radius=min(width, height) * 0.065,
            color=color,
            alpha=0.32,
        )

    horizontal_len = math.sqrt(light_position[0] * light_position[0] + light_position[2] * light_position[2])
    horizontal_dir = (
        light_position[0] / max(1.0e-6, horizontal_len),
        light_position[2] / max(1.0e-6, horizontal_len),
    )
    ground_projected = _project_world_to_screen(
        (horizontal_dir[0] * 1.55, -1.82, horizontal_dir[1] * 1.55),
        eye=eye,
        target=target,
        up_hint=up_hint,
        width=width,
        height=height,
        fov_y_degrees=fov_y_degrees,
    )
    if ground_projected is not None:
        warm_core = (255, 246, 222)
        outer_alpha = 0.14 + 0.24 * visibility
        inner_alpha = 0.12 + 0.28 * visibility
        _paint_ellipse(
            image,
            ground_projected[0],
            ground_projected[1],
            width * 0.22,
            height * 0.074,
            color,
            outer_alpha,
        )
        _paint_ellipse(
            image,
            ground_projected[0],
            ground_projected[1],
            width * 0.124,
            height * 0.042,
            warm_core,
            inner_alpha,
        )


def _make_background_image(width: int, height: int) -> Any:
    if np is not None:
        return _make_background_image_numpy(width, height)
    return [
        [_background_pixel(px, py, width, height) for px in range(width)]
        for py in range(height)
    ]


def _make_background_image_numpy(width: int, height: int) -> Any:
    assert np is not None
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


def _shade_pending_hits_numpy(
    image: Any,
    *,
    pending_hits: list[tuple[int, int, rt.Ray3D, tuple[float, float, float]]],
    center: tuple[float, float, float],
    light: dict[str, object],
    shadow_lookup: dict[int, int],
    light_count: int,
) -> None:
    assert np is not None
    hit_count = len(pending_hits)
    if hit_count == 0:
        return

    py = np.empty(hit_count, dtype=np.int32)
    px = np.empty(hit_count, dtype=np.int32)
    ray_id = np.empty(hit_count, dtype=np.int64)
    ray_dx = np.empty(hit_count, dtype=np.float32)
    ray_dy = np.empty(hit_count, dtype=np.float32)
    ray_dz = np.empty(hit_count, dtype=np.float32)
    hit_x = np.empty(hit_count, dtype=np.float32)
    hit_y = np.empty(hit_count, dtype=np.float32)
    hit_z = np.empty(hit_count, dtype=np.float32)
    for index, (row, col, ray, hit_point) in enumerate(pending_hits):
        py[index] = row
        px[index] = col
        ray_id[index] = ray.id
        ray_dx[index] = ray.dx
        ray_dy[index] = ray.dy
        ray_dz[index] = ray.dz
        hit_x[index] = hit_point[0]
        hit_y[index] = hit_point[1]
        hit_z[index] = hit_point[2]

    nx = hit_x - center[0]
    ny = hit_y - center[1]
    nz = hit_z - center[2]
    n_len = np.sqrt(np.maximum(1.0e-12, nx * nx + ny * ny + nz * nz))
    nx /= n_len
    ny /= n_len
    nz /= n_len

    crown = np.clip((ny + 0.65) / 1.65, 0.0, 1.0)
    side = np.clip((nz + 1.0) * 0.5, 0.0, 1.0)
    midnight = np.asarray((0.04, 0.07, 0.18), dtype=np.float32)
    deep_blue = np.asarray((0.08, 0.14, 0.34), dtype=np.float32)
    steel = np.asarray((0.12, 0.18, 0.42), dtype=np.float32)
    base = midnight + (deep_blue - midnight) * (0.35 + 0.30 * crown[:, None])
    base = np.clip(base + (steel - base) * (0.10 * side[:, None]), 0.0, 1.0)

    view_x = -ray_dx
    view_y = -ray_dy
    view_z = -ray_dz
    view_len = np.sqrt(np.maximum(1.0e-12, view_x * view_x + view_y * view_y + view_z * view_z))
    view_x /= view_len
    view_y /= view_len
    view_z /= view_len

    fresnel = np.power(1.0 - np.maximum(0.0, nx * view_x + ny * view_y + nz * view_z), 2.6)
    upper_glow = np.clip((ny + 0.55) / 1.55, 0.0, 1.0)
    lower_cool = np.clip((0.15 - ny) / 1.15, 0.0, 1.0)

    shadow_factor = np.asarray(
        [0.0 if shadow_lookup.get(int(identifier), 0) > 0 else 1.0 for identifier in (ray_id * light_count)],
        dtype=np.float32,
    )

    lx, ly, lz = light["position"]  # type: ignore[index]
    lr, lg, lb = light["color"]  # type: ignore[index]
    intensity = float(light.get("intensity", 1.0))  # type: ignore[call-arg]

    ldx = np.asarray(lx, dtype=np.float32) - hit_x
    ldy = np.asarray(ly, dtype=np.float32) - hit_y
    ldz = np.asarray(lz, dtype=np.float32) - hit_z
    light_len = np.sqrt(np.maximum(1.0e-12, ldx * ldx + ldy * ldy + ldz * ldz))
    ldx /= light_len
    ldy /= light_len
    ldz /= light_len
    lambert = np.maximum(0.0, nx * ldx + ny * ldy + nz * ldz) * shadow_factor

    light_rgb = np.empty((hit_count, 3), dtype=np.float32)
    light_rgb[:, 0] = 0.11 + lambert * float(lr) * 1.05 * intensity
    light_rgb[:, 1] = 0.12 + lambert * float(lg) * 1.05 * intensity
    light_rgb[:, 2] = 0.16 + lambert * float(lb) * 1.05 * intensity

    half_x = ldx + view_x
    half_y = ldy + view_y
    half_z = ldz + view_z
    half_len = np.sqrt(np.maximum(1.0e-12, half_x * half_x + half_y * half_y + half_z * half_z))
    half_x /= half_len
    half_y /= half_len
    half_z /= half_len
    specular = shadow_factor * intensity * np.power(np.maximum(0.0, nx * half_x + ny * half_y + nz * half_z), 52.0)

    final = base * light_rgb
    final[:, 0] += fresnel * 0.10 + upper_glow * 0.03 + specular * 0.14
    final[:, 1] += fresnel * 0.10 + upper_glow * 0.05 + lower_cool * 0.01 + specular * 0.21
    final[:, 2] += fresnel * 0.14 + upper_glow * 0.08 + lower_cool * 0.05 + specular * 0.28
    image[py, px] = np.clip(np.rint(np.clip(final, 0.0, 1.0) * 255.0), 0.0, 255.0).astype(np.uint8)


def _init_orbit_worker(state: dict[str, object]) -> None:
    global _ORBIT_WORKER_STATE
    _ORBIT_WORKER_STATE = state


def _render_orbit_frame(task: tuple[int, float]) -> dict[str, object]:
    frame_index, phase = task
    state = _ORBIT_WORKER_STATE
    light = _frame_light(phase)
    shading_started = time.perf_counter()
    source_image = state["background_image"]  # type: ignore[index]
    if np is not None and hasattr(source_image, "shape"):
        image = source_image.copy()
    else:
        image = [list(row) for row in source_image]  # type: ignore[arg-type]
    pending_hits = state["pending_hits"]  # type: ignore[assignment]
    center = state["center"]  # type: ignore[assignment]
    radius = state["radius"]  # type: ignore[assignment]
    triangles = state["triangles"]  # type: ignore[assignment]
    backend = state["backend"]  # type: ignore[assignment]

    shadow_rays: list[rt.Ray3D] = []
    light_count = int(state["light_count"])  # type: ignore[arg-type]
    for _, _, ray, hit_point in pending_hits:
        shadow_rays.extend(
            _make_shadow_rays(
                ray=ray,
                hit_point=hit_point,
                center=center,
                light=light,
                base_id=ray.id * light_count,
            )
        )

    shadow_query_seconds = 0.0
    shadow_lookup: dict[int, int] = {}
    if shadow_rays:
        shadow_started = time.perf_counter()
        shadow_rows = _run_backend_rows(backend, rays=tuple(shadow_rays), triangles=triangles)
        shadow_query_seconds = time.perf_counter() - shadow_started
        shadow_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in shadow_rows}

    if np is not None and hasattr(image, "shape"):
        _shade_pending_hits_numpy(
            image,
            pending_hits=pending_hits,  # type: ignore[arg-type]
            center=center,  # type: ignore[arg-type]
            light=light,
            shadow_lookup=shadow_lookup,
            light_count=light_count,
        )
    else:
        for py, px, ray, hit_point in pending_hits:
            shadow_factor = 0.0 if shadow_lookup.get(ray.id * light_count, 0) > 0 else 1.0
            image[py][px] = _shade_hit(
                ray,
                hit_point,
                center=center,
                radius=radius,
                lights=(light,),
                shadow_factors=(shadow_factor,),
            )

    projected_center = state["projected_center"]  # type: ignore[assignment]
    width = state["width"]  # type: ignore[assignment]
    height = state["height"]  # type: ignore[assignment]
    if projected_center is not None:
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

    _overlay_star_and_ground(
        image,
        light=light,
        eye=state["eye"],  # type: ignore[arg-type]
        target=state["target"],  # type: ignore[arg-type]
        up_hint=state["up_hint"],  # type: ignore[arg-type]
        width=width,
        height=height,
        fov_y_degrees=state["fov_y"],  # type: ignore[arg-type]
        center=center,
        radius=radius,
        show_light_source=state["show_light_source"],  # type: ignore[arg-type]
    )

    shading_seconds = time.perf_counter() - shading_started
    frame_path = Path(state["output_dir"]) / f"frame_{frame_index:03d}.ppm"  # type: ignore[arg-type]
    _write_ppm(frame_path, image)
    return {
        "frame_index": frame_index,
        "phase": phase,
        "frame_path": str(frame_path),
        "query_seconds": state["query_seconds"] if frame_index == 0 else 0.0,  # type: ignore[index]
        "shadow_query_seconds": shadow_query_seconds,
        "shading_seconds": shading_seconds,
        "rt_rows": state["rt_rows"],  # type: ignore[index]
        "shadow_rays": len(shadow_rays),
        "hit_pixels": state["hit_pixels"],  # type: ignore[index]
        "compare_backend": state["compare_summary"] if frame_index == 0 else None,  # type: ignore[index]
    }


def render_orbiting_star_ball_frames(
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
    show_light_source: bool = False,
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
    phases = _orbit_phase_samples(frame_count)

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
        "radius": radius,
        "triangles": triangles,
        "pending_hits": pending_hits,
        "projected_center": projected_center,
        "eye": eye,
        "target": target,
        "up_hint": up_hint,
        "width": width,
        "height": height,
        "fov_y": fov_y,
        "output_dir": output_dir,
        "query_seconds": query_seconds,
        "rt_rows": len(rows),
        "hit_pixels": hit_pixels,
        "compare_summary": compare_summary,
        "show_light_source": show_light_source,
        "light_count": 1,
    }
    tasks = list(enumerate(phases))
    if jobs <= 1:
        _init_orbit_worker(worker_state)
        summary_frames = [_render_orbit_frame(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs, initializer=_init_orbit_worker, initargs=(worker_state,)) as executor:
            summary_frames = list(executor.map(_render_orbit_frame, tasks))
    summary_frames.sort(key=lambda row: int(row["frame_index"]))
    total_query_seconds = query_seconds
    total_shadow_query_seconds = sum(float(row["shadow_query_seconds"]) for row in summary_frames)
    total_shading_seconds = sum(float(row["shading_seconds"]) for row in summary_frames)

    summary = {
        "backend": backend,
        "image_width": width,
        "image_height": height,
        "frame_count": frame_count,
        "jobs": jobs,
        "numpy_fast_path": np is not None,
        "show_light_source": show_light_source,
        "triangle_count": len(triangles),
        "latitude_bands": latitude_bands,
        "longitude_bands": longitude_bands,
        "total_query_seconds": total_query_seconds,
        "total_shadow_query_seconds": total_shadow_query_seconds,
        "total_shading_seconds": total_shading_seconds,
        "wall_clock_seconds": time.perf_counter() - wall_started,
        "query_share": (total_query_seconds + total_shadow_query_seconds)
        / max(1.0e-9, total_query_seconds + total_shadow_query_seconds + total_shading_seconds),
        "frames": summary_frames,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a static-ball orbiting-star RTDL demo.")
    parser.add_argument("--backend", default="cpu_python_reference")
    parser.add_argument("--compare-backend", default="none")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--latitude-bands", type=int, default=80)
    parser.add_argument("--longitude-bands", type=int, default=160)
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--show-light-source", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("build/rtdl_orbiting_star_ball_demo"))
    args = parser.parse_args()

    summary = render_orbiting_star_ball_frames(
        backend=args.backend,
        compare_backend=args.compare_backend,
        width=args.width,
        height=args.height,
        latitude_bands=args.latitude_bands,
        longitude_bands=args.longitude_bands,
        frame_count=args.frames,
        output_dir=args.output_dir,
        jobs=args.jobs,
        show_light_source=args.show_light_source,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
