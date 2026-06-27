from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import re
import sys
import time
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (str(REPO_ROOT), str(SRC_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import rtdsl as rt

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional fast path
    np = None  # type: ignore[assignment]

from examples.visual_demo.rtdl_spinning_ball_3d_demo import _background_pixel
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _clamp01
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _dot3
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _normalize3
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _paint_disc
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _paint_ellipse
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _paint_ground_shadow
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _paint_halo
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _project_world_to_screen
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _ray_sphere_intersection
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _run_backend_rows
from examples.visual_demo.rtdl_spinning_ball_3d_demo import _write_ppm
from examples.visual_demo.rtdl_spinning_ball_3d_demo import make_camera_rays
from examples.visual_demo.rtdl_spinning_ball_3d_demo import make_uv_sphere_mesh


_ORBIT_WORKER_STATE: dict[str, object] = {}
_ORBIT_MIDNIGHT = (0.03, 0.08, 0.24)
_ORBIT_DEEP_BLUE = (0.06, 0.19, 0.54)
_ORBIT_STEEL = (0.10, 0.24, 0.60)
_PPM_DIMENSIONS_RE = re.compile(rb"^(\d+)\s+(\d+)$")


def _orbit_phase_samples(frame_count: int, *, mode: str = "weighted") -> tuple[float, ...]:
    if frame_count <= 1:
        return (0.0,)
    if mode == "uniform":
        step = 1.0 / max(1, frame_count - 1)
        return tuple(index * step for index in range(frame_count))
    if mode != "weighted":
        raise ValueError(f"unsupported phase sampling mode: {mode}")
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
    x = 68.0 - 136.0 * phase
    return {
        "position": (
            x,
            0.08,
            11.8,
        ),
        "color": (1.0, 0.86, 0.30),
        "intensity": 2.95,
        "display_color": (255, 212, 92),
        "ground_core_color": (255, 224, 128),
        "display_alpha": 1.0,
        "ground_alpha_scale": 1.08,
        "size_scale": 1.28,
    }


def _support_star_strength(phase: float) -> float:
    if phase <= 0.32:
        return 1.0
    if phase >= 0.58:
        return 0.0
    return 1.0 - _smoothstep(0.32, 0.58, phase)


def _secondary_frame_light(phase: float) -> dict[str, object]:
    strength = _support_star_strength(phase)
    x = -54.0 + 56.0 * min(1.0, phase / 0.58)
    return {
        "position": (
            x,
            -1.18,
            8.6,
        ),
        "color": (1.0, 0.84, 0.30),
        "intensity": 1.12 * strength,
        "display_color": (255, 214, 112),
        "ground_core_color": (255, 226, 148),
        "display_alpha": 0.78 * strength,
        "ground_alpha_scale": 0.74 * strength,
        "size_scale": 0.82,
    }


def _stable_fill_light() -> dict[str, object]:
    return {
        "position": (
            -4.8,
            -1.05,
            4.7,
        ),
        "color": (0.34, 0.38, 0.52),
        "intensity": 0.72,
        "display_color": (0, 0, 0),
        "ground_core_color": (0, 0, 0),
        "display_alpha": 0.0,
        "ground_alpha_scale": 0.0,
    }


def _frame_lights(phase: float) -> tuple[dict[str, object], ...]:
    return (_frame_light(phase), _secondary_frame_light(phase))


def _smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge1 <= edge0:
        return 1.0 if value >= edge1 else 0.0
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


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
    segment_len_sq = max(1.0e-12, dx * dx + dy * dy + dz * dz)
    cx = center[0] - eye[0]
    cy = center[1] - eye[1]
    cz = center[2] - eye[2]
    t = max(0.0, min(1.0, (cx * dx + cy * dy + cz * dz) / segment_len_sq))
    closest_x = eye[0] + dx * t
    closest_y = eye[1] + dy * t
    closest_z = eye[2] + dz * t
    clearance_x = closest_x - center[0]
    clearance_y = closest_y - center[1]
    clearance_z = closest_z - center[2]
    closest_distance = math.sqrt(
        max(1.0e-12, clearance_x * clearance_x + clearance_y * clearance_y + clearance_z * clearance_z)
    )
    soft_band = max(0.12, radius * 0.16)
    return _smoothstep(radius - soft_band, radius + soft_band, closest_distance)


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
    color = tuple(light.get("display_color", (255, 212, 92)))  # type: ignore[arg-type]
    draw_alpha = float(light.get("display_alpha", 1.0))
    if float(light.get("intensity", 1.0)) <= 0.0 or draw_alpha <= 0.0:
        return
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
    size_scale = float(light.get("size_scale", 1.0))
    if show_light_source and projected is not None and visibility > 0.0:
        alpha_scale = visibility * draw_alpha
        _paint_disc(image, projected[0], projected[1], 34.0 * size_scale, color, 0.16 * alpha_scale)
        _paint_disc(image, projected[0], projected[1], 18.0 * size_scale, color, 0.42 * alpha_scale)
        _paint_disc(image, projected[0], projected[1], 7.5 * size_scale, (255, 250, 238), 0.96 * alpha_scale)
        _paint_halo(
            image,
            center_x=projected[0],
            center_y=projected[1],
            radius=min(width, height) * 0.065 * size_scale,
            color=color,
            alpha=0.32 * alpha_scale,
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
        warm_core = tuple(light.get("ground_core_color", (255, 224, 128)))  # type: ignore[arg-type]
        ground_alpha_scale = float(light.get("ground_alpha_scale", 1.0))
        outer_alpha = (0.14 + 0.24 * visibility) * ground_alpha_scale
        inner_alpha = (0.12 + 0.28 * visibility) * ground_alpha_scale
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


def _read_ppm_bytes(path: Path) -> tuple[int, int, bytes]:
    with path.open("rb") as handle:
        magic = handle.readline().strip()
        if magic != b"P6":
            raise ValueError(f"unsupported PPM magic in {path}: {magic!r}")
        dims_line = handle.readline().strip()
        match = _PPM_DIMENSIONS_RE.match(dims_line)
        if match is None:
            raise ValueError(f"invalid PPM dimensions in {path}: {dims_line!r}")
        width = int(match.group(1))
        height = int(match.group(2))
        max_value = handle.readline().strip()
        if max_value != b"255":
            raise ValueError(f"unsupported PPM max value in {path}: {max_value!r}")
        payload = handle.read()
    expected = width * height * 3
    if len(payload) != expected:
        raise ValueError(f"invalid PPM payload size in {path}: {len(payload)} != {expected}")
    return width, height, payload


def _blend_ppm_payloads(previous: bytes, current: bytes, alpha: float) -> bytes:
    if len(previous) != len(current):
        raise ValueError("PPM payloads must have equal length for temporal blending")
    if alpha <= 0.0:
        return current
    if alpha >= 1.0:
        return previous
    if np is not None:
        prev_arr = np.frombuffer(previous, dtype=np.uint8).astype(np.float32)
        curr_arr = np.frombuffer(current, dtype=np.uint8).astype(np.float32)
        blended = np.rint(curr_arr * (1.0 - alpha) + prev_arr * alpha)
        return np.clip(blended, 0.0, 255.0).astype(np.uint8).tobytes()
    blended = bytearray(len(current))
    keep = 1.0 - alpha
    for index, (prev_value, curr_value) in enumerate(zip(previous, current)):
        blended[index] = int(round(curr_value * keep + prev_value * alpha))
    return bytes(blended)


def _write_ppm_payload(path: Path, *, width: int, height: int, payload: bytes) -> None:
    with path.open("wb") as handle:
        handle.write(b"P6\n")
        handle.write(f"{width} {height}\n".encode("ascii"))
        handle.write(b"255\n")
        handle.write(payload)


def _orbit_frame_paths(output_dir: Path, frame_index: int) -> tuple[Path, Path, Path]:
    final_path = output_dir / f"frame_{frame_index:03d}.ppm"
    raw_path = output_dir / f"frame_{frame_index:03d}_raw.ppm"
    meta_path = output_dir / f"frame_{frame_index:03d}.json"
    return final_path, raw_path, meta_path


def _load_frame_meta(meta_path: Path) -> dict[str, object] | None:
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _write_frame_meta(meta_path: Path, row: dict[str, object]) -> None:
    meta_path.write_text(json.dumps(row, indent=2, sort_keys=True), encoding="utf-8")


def _restore_orbit_frame(task: tuple[int, float], state: dict[str, object]) -> dict[str, object] | None:
    frame_index, phase = task
    output_dir = Path(state["output_dir"])  # type: ignore[arg-type]
    final_path, raw_path, meta_path = _orbit_frame_paths(output_dir, frame_index)
    if not raw_path.exists():
        return None
    row = _load_frame_meta(meta_path)
    if row is None:
        return None
    if int(row.get("frame_index", -1)) != frame_index:
        return None
    if abs(float(row.get("phase", -999.0)) - phase) > 1.0e-12:
        return None
    row["frame_path"] = str(final_path)
    row["raw_frame_path"] = str(raw_path)
    return row


def _materialize_orbit_frames(summary_frames: list[dict[str, object]], alpha: float) -> None:
    if not summary_frames:
        return
    previous_raw_payload: bytes | None = None
    previous_width: int | None = None
    previous_height: int | None = None
    for row in summary_frames:
        raw_path = Path(str(row["raw_frame_path"]))
        final_path = Path(str(row["frame_path"]))
        width, height, raw_payload = _read_ppm_bytes(raw_path)
        payload = raw_payload
        if alpha > 0.0 and previous_raw_payload is not None:
            if width != previous_width or height != previous_height:
                raise ValueError("all temporally blended frames must have the same dimensions")
            payload = _blend_ppm_payloads(previous_raw_payload, payload, alpha)
        _write_ppm_payload(final_path, width=width, height=height, payload=payload)
        previous_raw_payload = raw_payload
        previous_width = width
        previous_height = height


def _apply_temporal_blend(frame_paths: list[Path], alpha: float) -> None:
    if alpha <= 0.0 or len(frame_paths) <= 1:
        return
    previous_width, previous_height, previous_raw_payload = _read_ppm_bytes(frame_paths[0])
    for path in frame_paths[1:]:
        width, height, payload = _read_ppm_bytes(path)
        if width != previous_width or height != previous_height:
            raise ValueError("all temporally blended frames must have the same dimensions")
        blended = _blend_ppm_payloads(previous_raw_payload, payload, alpha)
        _write_ppm_payload(path, width=width, height=height, payload=blended)
        previous_raw_payload = payload


def _orbit_surface_color(normal: tuple[float, float, float]) -> tuple[float, float, float]:
    _, ny, nz = normal
    crown = _clamp01((ny + 0.65) / 1.65)
    side = _clamp01((nz + 1.0) * 0.5)
    base = tuple(
        _ORBIT_MIDNIGHT[index] + (_ORBIT_DEEP_BLUE[index] - _ORBIT_MIDNIGHT[index]) * (0.35 + 0.30 * crown)
        for index in range(3)
    )
    return tuple(
        _clamp01(base[index] + (_ORBIT_STEEL[index] - base[index]) * (0.10 * side))
        for index in range(3)
    )


def _shade_orbit_hit(
    ray: rt.Ray3D,
    hit_point: tuple[float, float, float],
    *,
    center: tuple[float, float, float],
    lights: tuple[dict[str, object], ...],
    shadow_lookup: dict[int, int],
    light_count: int,
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

    light_rgb = [0.11, 0.12, 0.16]
    specular = 0.0
    for light_index, light in enumerate(lights):
        intensity = float(light.get("intensity", 1.0))  # type: ignore[call-arg]
        if intensity <= 0.0:
            continue
        shadow_factor = 0.0 if shadow_lookup.get(ray.id * light_count + light_index, 0) > 0 else 1.0
        lx, ly, lz = light["position"]  # type: ignore[index]
        ldx, ldy, ldz = _normalize3(lx - hit_point[0], ly - hit_point[1], lz - hit_point[2])
        lambert = max(0.0, _dot3(nx, ny, nz, ldx, ldy, ldz)) * shadow_factor
        lr, lg, lb = light["color"]  # type: ignore[index]
        light_rgb[0] += lambert * float(lr) * 1.05 * intensity
        light_rgb[1] += lambert * float(lg) * 1.05 * intensity
        light_rgb[2] += lambert * float(lb) * 1.05 * intensity
        half_x, half_y, half_z = _normalize3(ldx + view[0], ldy + view[1], ldz + view[2])
        specular += shadow_factor * intensity * (max(0.0, _dot3(nx, ny, nz, half_x, half_y, half_z)) ** 52.0)

    final = []
    for index in range(3):
        channel = base[index] * light_rgb[index]
        channel += fresnel * (0.14 if index == 2 else 0.10)
        channel += upper_glow * (0.03 if index == 0 else 0.05 if index == 1 else 0.08)
        channel += lower_cool * (0.00 if index == 0 else 0.01 if index == 1 else 0.05)
        channel += specular * (0.14 + 0.07 * index)
        final.append(int(round(_clamp01(channel) * 255.0)))
    return final[0], final[1], final[2]


def _shade_pending_hits_numpy(
    image: Any,
    *,
    pending_hits: list[tuple[int, int, rt.Ray3D, tuple[float, float, float]]],
    center: tuple[float, float, float],
    lights: tuple[dict[str, object], ...],
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
    midnight = np.asarray(_ORBIT_MIDNIGHT, dtype=np.float32)
    deep_blue = np.asarray(_ORBIT_DEEP_BLUE, dtype=np.float32)
    steel = np.asarray(_ORBIT_STEEL, dtype=np.float32)
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

    light_rgb = np.empty((hit_count, 3), dtype=np.float32)
    light_rgb[:, 0] = 0.11
    light_rgb[:, 1] = 0.12
    light_rgb[:, 2] = 0.16
    specular = np.zeros(hit_count, dtype=np.float32)
    for light_index, light in enumerate(lights):
        intensity = float(light.get("intensity", 1.0))  # type: ignore[call-arg]
        if intensity <= 0.0:
            continue
        shadow_factor = np.asarray(
            [0.0 if shadow_lookup.get(int(identifier), 0) > 0 else 1.0 for identifier in (ray_id * light_count + light_index)],
            dtype=np.float32,
        )
        lx, ly, lz = light["position"]  # type: ignore[index]
        lr, lg, lb = light["color"]  # type: ignore[index]
        ldx = np.asarray(lx, dtype=np.float32) - hit_x
        ldy = np.asarray(ly, dtype=np.float32) - hit_y
        ldz = np.asarray(lz, dtype=np.float32) - hit_z
        light_len = np.sqrt(np.maximum(1.0e-12, ldx * ldx + ldy * ldy + ldz * ldz))
        ldx /= light_len
        ldy /= light_len
        ldz /= light_len
        lambert = np.maximum(0.0, nx * ldx + ny * ldy + nz * ldz) * shadow_factor
        light_rgb[:, 0] += lambert * float(lr) * 1.05 * intensity
        light_rgb[:, 1] += lambert * float(lg) * 1.05 * intensity
        light_rgb[:, 2] += lambert * float(lb) * 1.05 * intensity
        half_x = ldx + view_x
        half_y = ldy + view_y
        half_z = ldz + view_z
        half_len = np.sqrt(np.maximum(1.0e-12, half_x * half_x + half_y * half_y + half_z * half_z))
        half_x /= half_len
        half_y /= half_len
        half_z /= half_len
        specular += shadow_factor * intensity * np.power(np.maximum(0.0, nx * half_x + ny * half_y + nz * half_z), 52.0)

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
    restored = _restore_orbit_frame(task, state)
    if restored is not None:
        return restored
    lights = _frame_lights(phase)
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
        for light_index, light in enumerate(lights):
            if float(light.get("intensity", 1.0)) <= 0.0:
                continue
            shadow_rays.extend(
                _make_shadow_rays(
                    ray=ray,
                    hit_point=hit_point,
                    center=center,
                    light=light,
                    base_id=ray.id * light_count + light_index,
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
            lights=lights,
            shadow_lookup=shadow_lookup,
            light_count=light_count,
        )
    else:
        for py, px, ray, hit_point in pending_hits:
            image[py][px] = _shade_orbit_hit(
                ray,
                hit_point,
                center=center,
                lights=lights,
                shadow_lookup=shadow_lookup,
                light_count=light_count,
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

    for light in lights:
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
    output_dir = Path(state["output_dir"])  # type: ignore[arg-type]
    frame_path, raw_frame_path, meta_path = _orbit_frame_paths(output_dir, frame_index)
    _write_ppm(raw_frame_path, image)
    row = {
        "frame_index": frame_index,
        "phase": phase,
        "frame_path": str(frame_path),
        "raw_frame_path": str(raw_frame_path),
        "query_seconds": state["query_seconds"] if frame_index == 0 else 0.0,  # type: ignore[index]
        "shadow_query_seconds": shadow_query_seconds,
        "shading_seconds": shading_seconds,
        "rt_rows": state["rt_rows"],  # type: ignore[index]
        "shadow_rays": len(shadow_rays),
        "hit_pixels": state["hit_pixels"],  # type: ignore[index]
        "compare_backend": state["compare_summary"] if frame_index == 0 else None,  # type: ignore[index]
    }
    _write_frame_meta(meta_path, row)
    return row


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
    temporal_blend_alpha: float = 0.0,
    phase_mode: str = "weighted",
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
    phases = _orbit_phase_samples(frame_count, mode=phase_mode)

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
        "light_count": len(_frame_lights(0.0)),
    }
    tasks = list(enumerate(phases))
    if jobs <= 1:
        _init_orbit_worker(worker_state)
        summary_frames = [_render_orbit_frame(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs, initializer=_init_orbit_worker, initargs=(worker_state,)) as executor:
            summary_frames = list(executor.map(_render_orbit_frame, tasks))
    summary_frames.sort(key=lambda row: int(row["frame_index"]))
    _materialize_orbit_frames(summary_frames, temporal_blend_alpha)
    total_query_seconds = query_seconds
    total_shadow_query_seconds = sum(float(row["shadow_query_seconds"]) for row in summary_frames)
    total_shading_seconds = sum(float(row["shading_seconds"]) for row in summary_frames)

    summary = {
        "backend": backend,
        "image_width": width,
        "image_height": height,
        "frame_count": frame_count,
        "jobs": jobs,
        "light_count": int(worker_state["light_count"]),
        "numpy_fast_path": np is not None,
        "show_light_source": show_light_source,
        "temporal_blend_alpha": temporal_blend_alpha,
        "phase_mode": phase_mode,
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


def render_orbiting_star_ball_vulkan_frames(
    *,
    output_dir: Path,
    compare_backend: str | None = "cpu_python_reference",
    width: int = 1024,
    height: int = 1024,
    latitude_bands: int = 80,
    longitude_bands: int = 160,
    frame_count: int = 120,
    jobs: int = 1,
    show_light_source: bool = False,
    temporal_blend_alpha: float = 0.0,
    phase_mode: str = "weighted",
) -> dict[str, object]:
    return render_orbiting_star_ball_frames(
        backend="vulkan",
        compare_backend=compare_backend,
        width=width,
        height=height,
        latitude_bands=latitude_bands,
        longitude_bands=longitude_bands,
        frame_count=frame_count,
        output_dir=output_dir,
        jobs=jobs,
        show_light_source=show_light_source,
        temporal_blend_alpha=temporal_blend_alpha,
        phase_mode=phase_mode,
    )


def render_orbiting_star_ball_optix_4k(
    *,
    output_dir: Path,
    compare_backend: str | None = "cpu_python_reference",
    width: int = 3840,
    height: int = 2160,
    latitude_bands: int = 96,
    longitude_bands: int = 192,
    frame_count: int = 320,
    jobs: int = 1,
    show_light_source: bool = False,
    temporal_blend_alpha: float = 0.0,
    phase_mode: str = "weighted",
) -> dict[str, object]:
    return render_orbiting_star_ball_frames(
        backend="optix",
        compare_backend=compare_backend,
        width=width,
        height=height,
        latitude_bands=latitude_bands,
        longitude_bands=longitude_bands,
        frame_count=frame_count,
        output_dir=output_dir,
        jobs=jobs,
        show_light_source=show_light_source,
        temporal_blend_alpha=temporal_blend_alpha,
        phase_mode=phase_mode,
    )


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
    parser.add_argument("--temporal-blend-alpha", type=float, default=0.0)
    parser.add_argument("--phase-mode", choices=("weighted", "uniform"), default="weighted")
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
        temporal_blend_alpha=args.temporal_blend_alpha,
        phase_mode=args.phase_mode,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
