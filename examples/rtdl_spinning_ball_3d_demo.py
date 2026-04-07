from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (str(REPO_ROOT), str(SRC_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_hitcount_3d_demo():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _normalize3(x: float, y: float, z: float) -> tuple[float, float, float]:
    length = math.sqrt(max(1.0e-12, x * x + y * y + z * z))
    return x / length, y / length, z / length


def _dot3(ax: float, ay: float, az: float, bx: float, by: float, bz: float) -> float:
    return ax * bx + ay * by + az * bz


def _cross3(ax: float, ay: float, az: float, bx: float, by: float, bz: float) -> tuple[float, float, float]:
    return (
        ay * bz - az * by,
        az * bx - ax * bz,
        ax * by - ay * bx,
    )


def _mix(a: float, b: float, t: float) -> float:
    return a * (1.0 - t) + b * t


def _blend_rgb(base: tuple[int, int, int], overlay: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    alpha = _clamp01(alpha)
    return (
        int(round(_mix(base[0], overlay[0], alpha))),
        int(round(_mix(base[1], overlay[1], alpha))),
        int(round(_mix(base[2], overlay[2], alpha))),
    )


def make_uv_sphere_mesh(
    *,
    latitude_bands: int,
    longitude_bands: int,
    radius: float,
    center: tuple[float, float, float],
) -> tuple[rt.Triangle3D, ...]:
    cx, cy, cz = center
    triangles: list[rt.Triangle3D] = []
    triangle_id = 0

    for lat_index in range(latitude_bands):
        phi0 = math.pi * (lat_index / latitude_bands)
        phi1 = math.pi * ((lat_index + 1) / latitude_bands)
        for lon_index in range(longitude_bands):
            theta0 = math.tau * (lon_index / longitude_bands)
            theta1 = math.tau * ((lon_index + 1) / longitude_bands)

            p00 = _sphere_vertex(theta0, phi0, radius, cx, cy, cz)
            p01 = _sphere_vertex(theta1, phi0, radius, cx, cy, cz)
            p10 = _sphere_vertex(theta0, phi1, radius, cx, cy, cz)
            p11 = _sphere_vertex(theta1, phi1, radius, cx, cy, cz)

            if lat_index == 0:
                triangles.append(
                    rt.Triangle3D(
                        id=triangle_id,
                        x0=p00[0],
                        y0=p00[1],
                        z0=p00[2],
                        x1=p10[0],
                        y1=p10[1],
                        z1=p10[2],
                        x2=p11[0],
                        y2=p11[1],
                        z2=p11[2],
                    )
                )
                triangle_id += 1
                continue

            if lat_index == latitude_bands - 1:
                triangles.append(
                    rt.Triangle3D(
                        id=triangle_id,
                        x0=p00[0],
                        y0=p00[1],
                        z0=p00[2],
                        x1=p10[0],
                        y1=p10[1],
                        z1=p10[2],
                        x2=p01[0],
                        y2=p01[1],
                        z2=p01[2],
                    )
                )
                triangle_id += 1
                continue

            triangles.append(
                rt.Triangle3D(
                    id=triangle_id,
                    x0=p00[0],
                    y0=p00[1],
                    z0=p00[2],
                    x1=p10[0],
                    y1=p10[1],
                    z1=p10[2],
                    x2=p11[0],
                    y2=p11[1],
                    z2=p11[2],
                )
            )
            triangle_id += 1
            triangles.append(
                rt.Triangle3D(
                    id=triangle_id,
                    x0=p00[0],
                    y0=p00[1],
                    z0=p00[2],
                    x1=p11[0],
                    y1=p11[1],
                    z1=p11[2],
                    x2=p01[0],
                    y2=p01[1],
                    z2=p01[2],
                )
            )
            triangle_id += 1

    return tuple(triangles)


def _sphere_vertex(
    theta: float,
    phi: float,
    radius: float,
    cx: float,
    cy: float,
    cz: float,
) -> tuple[float, float, float]:
    sin_phi = math.sin(phi)
    return (
        cx + radius * math.cos(theta) * sin_phi,
        cy + radius * math.cos(phi),
        cz + radius * math.sin(theta) * sin_phi,
    )


def _camera_basis(
    eye: tuple[float, float, float],
    target: tuple[float, float, float],
    up_hint: tuple[float, float, float],
) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    fx, fy, fz = _normalize3(target[0] - eye[0], target[1] - eye[1], target[2] - eye[2])
    rx, ry, rz = _normalize3(*_cross3(fx, fy, fz, up_hint[0], up_hint[1], up_hint[2]))
    ux, uy, uz = _normalize3(*_cross3(rx, ry, rz, fx, fy, fz))
    return (fx, fy, fz), (rx, ry, rz), (ux, uy, uz)


def make_camera_rays(
    *,
    width: int,
    height: int,
    eye: tuple[float, float, float],
    target: tuple[float, float, float],
    up_hint: tuple[float, float, float],
    fov_y_degrees: float,
) -> tuple[rt.Ray3D, ...]:
    forward, right, up = _camera_basis(eye, target, up_hint)
    half_y = math.tan(math.radians(fov_y_degrees) * 0.5)
    half_x = half_y * (width / max(1, height))

    rays: list[rt.Ray3D] = []
    ray_id = 0
    for py in range(height):
        sy = 1.0 - (2.0 * (py + 0.5) / height)
        for px in range(width):
            sx = (2.0 * (px + 0.5) / width) - 1.0
            dir_x = forward[0] + right[0] * (sx * half_x) + up[0] * (sy * half_y)
            dir_y = forward[1] + right[1] * (sx * half_x) + up[1] * (sy * half_y)
            dir_z = forward[2] + right[2] * (sx * half_x) + up[2] * (sy * half_y)
            dx, dy, dz = _normalize3(dir_x, dir_y, dir_z)
            rays.append(
                rt.Ray3D(
                    id=ray_id,
                    ox=eye[0],
                    oy=eye[1],
                    oz=eye[2],
                    dx=dx,
                    dy=dy,
                    dz=dz,
                    tmax=100.0,
                )
            )
            ray_id += 1
    return tuple(rays)


def _ray_sphere_intersection(
    ray: rt.Ray3D,
    *,
    center: tuple[float, float, float],
    radius: float,
) -> tuple[float, tuple[float, float, float]] | None:
    ocx = ray.ox - center[0]
    ocy = ray.oy - center[1]
    ocz = ray.oz - center[2]
    a = _dot3(ray.dx, ray.dy, ray.dz, ray.dx, ray.dy, ray.dz)
    b = 2.0 * _dot3(ocx, ocy, ocz, ray.dx, ray.dy, ray.dz)
    c = _dot3(ocx, ocy, ocz, ocx, ocy, ocz) - radius * radius
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return None
    root = math.sqrt(disc)
    t0 = (-b - root) / (2.0 * a)
    t1 = (-b + root) / (2.0 * a)
    t = None
    for candidate in (t0, t1):
        if 0.0 <= candidate <= ray.tmax:
            t = candidate
            break
    if t is None:
        return None
    hit = (ray.ox + ray.dx * t, ray.oy + ray.dy * t, ray.oz + ray.dz * t)
    return t, hit


def _frame_lights(phase: float) -> tuple[dict[str, object], ...]:
    return (
        {
            "position": (
                math.cos(phase * math.tau) * 2.8,
                0.95 + math.sin(phase * math.tau * 0.8) * 0.55,
                math.sin(phase * math.tau) * 2.8,
            ),
            "color": (1.00, 0.78, 0.42),
        },
        {
            "position": (
                math.cos(phase * math.tau + math.pi) * 2.3,
                -0.75 + math.sin(phase * math.tau * 1.3 + 0.7) * 0.45,
                math.sin(phase * math.tau + math.pi) * 2.3,
            ),
            "color": (0.45, 0.82, 1.00),
        },
    )


def _surface_color(normal: tuple[float, float, float]) -> tuple[float, float, float]:
    nx, ny, nz = normal
    latitude = math.asin(max(-1.0, min(1.0, ny)))
    crown = _clamp01((ny + 0.65) / 1.65)
    side = _clamp01((nz + 1.0) * 0.5)

    midnight = (0.04, 0.07, 0.18)
    deep_blue = (0.08, 0.14, 0.34)
    steel = (0.12, 0.18, 0.42)

    base = tuple(_mix(midnight[index], deep_blue[index], 0.35 + 0.30 * crown) for index in range(3))
    return tuple(_clamp01(_mix(base[index], steel[index], 0.10 * side)) for index in range(3))


def _shade_hit(
    ray: rt.Ray3D,
    hit_point: tuple[float, float, float],
    *,
    center: tuple[float, float, float],
    radius: float,
    lights: tuple[dict[str, object], ...],
    shadow_factors: tuple[float, ...] | None = None,
) -> tuple[int, int, int]:
    nx, ny, nz = _normalize3(
        hit_point[0] - center[0],
        hit_point[1] - center[1],
        hit_point[2] - center[2],
    )
    base = _surface_color((nx, ny, nz))
    view = _normalize3(-ray.dx, -ray.dy, -ray.dz)
    fresnel = (1.0 - max(0.0, _dot3(nx, ny, nz, view[0], view[1], view[2]))) ** 2.6
    upper_glow = _clamp01((ny + 0.55) / 1.55)
    lower_cool = _clamp01((0.15 - ny) / 1.15)

    light_rgb = [0.11, 0.12, 0.16]
    specular = 0.0
    for light_index, light in enumerate(lights):
        lx, ly, lz = light["position"]  # type: ignore[index]
        ldx, ldy, ldz = _normalize3(lx - hit_point[0], ly - hit_point[1], lz - hit_point[2])
        lambert = max(0.0, _dot3(nx, ny, nz, ldx, ldy, ldz))
        if lambert <= 0.0:
            continue
        visibility = shadow_factors[light_index] if shadow_factors is not None else 1.0
        if visibility <= 0.0:
            continue
        lr, lg, lb = light["color"]  # type: ignore[index]
        intensity = float(light.get("intensity", 1.0))  # type: ignore[call-arg]
        light_rgb[0] += lambert * visibility * float(lr) * 1.05 * intensity
        light_rgb[1] += lambert * visibility * float(lg) * 1.05 * intensity
        light_rgb[2] += lambert * visibility * float(lb) * 1.05 * intensity

        hx, hy, hz = _normalize3(ldx + view[0], ldy + view[1], ldz + view[2])
        specular += visibility * intensity * (max(0.0, _dot3(nx, ny, nz, hx, hy, hz)) ** 52.0)

    final = []
    for index in range(3):
        channel = base[index] * light_rgb[index]
        channel += fresnel * (0.14 if index == 2 else 0.10)
        channel += upper_glow * (0.03 if index == 0 else 0.05 if index == 1 else 0.08)
        channel += lower_cool * (0.00 if index == 0 else 0.01 if index == 1 else 0.05)
        channel += specular * (0.14 + 0.07 * index)
        final.append(int(round(_clamp01(channel) * 255.0)))
    return final[0], final[1], final[2]


def _background_pixel(px: int, py: int, width: int, height: int) -> tuple[int, int, int]:
    u = px / max(1, width - 1)
    v = py / max(1, height - 1)
    horizon = _mix(0.0, 1.0, v)
    vignette = 1.0 - min(1.0, math.sqrt((u - 0.5) ** 2 + (v - 0.46) ** 2) * 1.32)
    nebula = math.exp(-(((u - 0.34) ** 2) / 0.025 + ((v - 0.22) ** 2) / 0.008))
    bloom = math.exp(-(((u - 0.70) ** 2) / 0.040 + ((v - 0.30) ** 2) / 0.018))
    floor = math.exp(-(((v - 0.84) ** 2) / 0.010))
    r = 0.015 + 0.025 * horizon + 0.060 * vignette + 0.090 * nebula + 0.035 * floor
    g = 0.020 + 0.030 * horizon + 0.080 * vignette + 0.030 * nebula + 0.050 * bloom + 0.045 * floor
    b = 0.060 + 0.120 * horizon + 0.160 * vignette + 0.060 * bloom + 0.055 * floor
    return int(round(_clamp01(r) * 255.0)), int(round(_clamp01(g) * 255.0)), int(round(_clamp01(b) * 255.0))


def _project_world_to_screen(
    position: tuple[float, float, float],
    *,
    eye: tuple[float, float, float],
    target: tuple[float, float, float],
    up_hint: tuple[float, float, float],
    width: int,
    height: int,
    fov_y_degrees: float,
) -> tuple[float, float] | None:
    forward, right, up = _camera_basis(eye, target, up_hint)
    vx = position[0] - eye[0]
    vy = position[1] - eye[1]
    vz = position[2] - eye[2]
    cam_x = _dot3(vx, vy, vz, right[0], right[1], right[2])
    cam_y = _dot3(vx, vy, vz, up[0], up[1], up[2])
    cam_z = _dot3(vx, vy, vz, forward[0], forward[1], forward[2])
    if cam_z <= 1.0e-6:
        return None
    half_y = math.tan(math.radians(fov_y_degrees) * 0.5)
    half_x = half_y * (width / max(1, height))
    ndc_x = cam_x / (cam_z * half_x)
    ndc_y = cam_y / (cam_z * half_y)
    px = (ndc_x + 1.0) * 0.5 * width
    py = (1.0 - (ndc_y + 1.0) * 0.5) * height
    return px, py


def _overlay_lights(
    image: list[list[tuple[int, int, int]]],
    *,
    phase: float,
    eye: tuple[float, float, float],
    target: tuple[float, float, float],
    up_hint: tuple[float, float, float],
    width: int,
    height: int,
    fov_y_degrees: float,
) -> None:
    ground_plane_y = -1.75
    for light_index in range(2):
        for step in range(14, 0, -1):
            trail_phase = (phase - step / 84.0) % 1.0
            trail_light = _frame_lights(trail_phase)[light_index]
            trail_position = trail_light["position"]  # type: ignore[index]
            projected = _project_world_to_screen(
                trail_position,  # type: ignore[arg-type]
                eye=eye,
                target=target,
                up_hint=up_hint,
                width=width,
                height=height,
                fov_y_degrees=fov_y_degrees,
            )
            if projected is None:
                continue
            color = tuple(int(round(_clamp01(channel) * 255.0)) for channel in trail_light["color"])  # type: ignore[arg-type]
            ground_projected = _project_world_to_screen(
                (trail_position[0] * 0.96, ground_plane_y, trail_position[2] * 0.96),  # type: ignore[index]
                eye=eye,
                target=target,
                up_hint=up_hint,
                width=width,
                height=height,
                fov_y_degrees=fov_y_degrees,
            )
            if ground_projected is not None:
                _paint_disc(
                    image,
                    ground_projected[0],
                    ground_projected[1],
                    max(width, height) * 0.050,
                    color,
                    0.028 * (1.0 - step / 15.0),
                )
            _paint_disc(
                image,
                projected[0],
                projected[1],
                max(1.2, 6.4 - step * 0.22),
                color,
                0.19 * (1.0 - step / 15.0),
            )

    for light in _frame_lights(phase):
        light_position = light["position"]  # type: ignore[index]
        projected = _project_world_to_screen(
            light_position,  # type: ignore[arg-type]
            eye=eye,
            target=target,
            up_hint=up_hint,
            width=width,
            height=height,
            fov_y_degrees=fov_y_degrees,
        )
        if projected is None:
            continue
        color = tuple(int(round(_clamp01(channel) * 255.0)) for channel in light["color"])  # type: ignore[arg-type]
        ground_projected = _project_world_to_screen(
            (light_position[0] * 0.96, ground_plane_y, light_position[2] * 0.96),  # type: ignore[index]
            eye=eye,
            target=target,
            up_hint=up_hint,
            width=width,
            height=height,
            fov_y_degrees=fov_y_degrees,
        )
        if ground_projected is not None:
            _paint_ellipse(
                image,
                ground_projected[0],
                ground_projected[1],
                width * 0.075,
                height * 0.030,
                color,
                0.16,
            )
            _paint_ellipse(
                image,
                ground_projected[0],
                ground_projected[1],
                width * 0.040,
                height * 0.016,
                (255, 244, 220),
                0.12,
            )
        _paint_disc(image, projected[0], projected[1], 14.0, color, 0.18)
        _paint_disc(image, projected[0], projected[1], 7.4, color, 0.46)
        _paint_disc(image, projected[0], projected[1], 3.0, (255, 255, 255), 0.97)


def _paint_ground_shadow(
    image: list[list[tuple[int, int, int]]],
    *,
    center_x: float,
    center_y: float,
    radius_x: float,
    radius_y: float,
    alpha: float,
) -> None:
    height = len(image)
    width = len(image[0]) if height else 0
    min_x = max(0, int(math.floor(center_x - radius_x - 2.0)))
    max_x = min(width - 1, int(math.ceil(center_x + radius_x + 2.0)))
    min_y = max(0, int(math.floor(center_y - radius_y - 2.0)))
    max_y = min(height - 1, int(math.ceil(center_y + radius_y + 2.0)))
    if min_x > max_x or min_y > max_y:
        return
    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            nx = ((px + 0.5) - center_x) / max(1.0e-6, radius_x)
            ny = ((py + 0.5) - center_y) / max(1.0e-6, radius_y)
            dist = nx * nx + ny * ny
            if dist > 1.0:
                continue
            strength = math.exp(-dist * 2.2) * alpha
            image[py][px] = _blend_rgb(image[py][px], (6, 8, 16), strength)


def _paint_halo(
    image: list[list[tuple[int, int, int]]],
    *,
    center_x: float,
    center_y: float,
    radius: float,
    color: tuple[int, int, int],
    alpha: float,
) -> None:
    _paint_disc(image, center_x, center_y, radius * 1.45, color, alpha * 0.12)
    _paint_disc(image, center_x, center_y, radius * 1.12, color, alpha * 0.18)


def _paint_ellipse(
    image: list[list[tuple[int, int, int]]],
    cx: float,
    cy: float,
    radius_x: float,
    radius_y: float,
    color: tuple[int, int, int],
    alpha: float,
) -> None:
    height = len(image)
    width = len(image[0]) if height else 0
    min_x = max(0, int(math.floor(cx - radius_x - 2.0)))
    max_x = min(width - 1, int(math.ceil(cx + radius_x + 2.0)))
    min_y = max(0, int(math.floor(cy - radius_y - 2.0)))
    max_y = min(height - 1, int(math.ceil(cy + radius_y + 2.0)))
    if min_x > max_x or min_y > max_y:
        return
    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            nx = ((px + 0.5) - cx) / max(1.0e-6, radius_x)
            ny = ((py + 0.5) - cy) / max(1.0e-6, radius_y)
            dist = nx * nx + ny * ny
            if dist > 1.0:
                continue
            falloff = math.exp(-dist * 2.0)
            image[py][px] = _blend_rgb(image[py][px], color, alpha * falloff)


def _paint_disc(
    image: list[list[tuple[int, int, int]]],
    cx: float,
    cy: float,
    radius: float,
    color: tuple[int, int, int],
    alpha: float,
) -> None:
    height = len(image)
    width = len(image[0]) if height else 0
    min_x = max(0, int(math.floor(cx - radius - 1.0)))
    max_x = min(width - 1, int(math.ceil(cx + radius + 1.0)))
    min_y = max(0, int(math.floor(cy - radius - 1.0)))
    max_y = min(height - 1, int(math.ceil(cy + radius + 1.0)))
    if min_x > max_x or min_y > max_y:
        return
    radius_sq = radius * radius
    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            dx = (px + 0.5) - cx
            dy = (py + 0.5) - cy
            dist_sq = dx * dx + dy * dy
            if dist_sq > radius_sq:
                continue
            falloff = math.exp(-dist_sq / max(1.0e-6, radius_sq * 0.55))
            image[py][px] = _blend_rgb(image[py][px], color, alpha * falloff)


def _write_ppm(path: Path, image: list[list[tuple[int, int, int]]]) -> None:
    height = len(image)
    width = len(image[0]) if height else 0
    with path.open("wb") as handle:
        handle.write(f"P6\n{width} {height}\n255\n".encode("ascii"))
        for row in image:
            for pixel in row:
                handle.write(bytes(pixel))


def _make_shadow_rays(
    *,
    ray: rt.Ray3D,
    hit_point: tuple[float, float, float],
    center: tuple[float, float, float],
    radius: float,
    lights: tuple[dict[str, object], ...],
    base_id: int,
) -> tuple[rt.Ray3D, ...]:
    nx, ny, nz = _normalize3(
        hit_point[0] - center[0],
        hit_point[1] - center[1],
        hit_point[2] - center[2],
    )
    origin = (
        hit_point[0] + nx * 1.0e-3,
        hit_point[1] + ny * 1.0e-3,
        hit_point[2] + nz * 1.0e-3,
    )
    rays: list[rt.Ray3D] = []
    for light_index, light in enumerate(lights):
        lx, ly, lz = light["position"]  # type: ignore[index]
        dx = lx - origin[0]
        dy = ly - origin[1]
        dz = lz - origin[2]
        distance = math.sqrt(max(1.0e-12, dx * dx + dy * dy + dz * dz))
        dir_x, dir_y, dir_z = dx / distance, dy / distance, dz / distance
        rays.append(
            rt.Ray3D(
                id=base_id + light_index,
                ox=origin[0],
                oy=origin[1],
                oz=origin[2],
                dx=dir_x,
                dy=dir_y,
                dz=dir_z,
                tmax=max(0.0, distance - 2.0e-3),
            )
        )
    return tuple(rays)


def render_spinning_ball_3d_frames(
    *,
    backend: str,
    compare_backend: str | None,
    width: int,
    height: int,
    latitude_bands: int,
    longitude_bands: int,
    frame_count: int,
    spin_speed: float,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    eye = (0.55, 0.30, 5.7)
    target = (0.0, 0.10, 0.0)
    up_hint = (0.0, 1.0, 0.0)
    radius = 1.38
    center = (0.0, 0.08, 0.0)
    fov_y = 31.0
    triangles = make_uv_sphere_mesh(
        latitude_bands=latitude_bands,
        longitude_bands=longitude_bands,
        radius=radius,
        center=center,
    )
    rays = make_camera_rays(width=width, height=height, eye=eye, target=target, up_hint=up_hint, fov_y_degrees=fov_y)

    summary_frames = []
    total_query_seconds = 0.0
    total_shadow_query_seconds = 0.0
    total_shading_seconds = 0.0
    for frame_index in range(frame_count):
        phase = frame_index / max(1, frame_count)
        spin_phase = phase * spin_speed
        lights = _frame_lights(spin_phase)

        query_started = time.perf_counter()
        rows = _run_backend_rows(backend, rays=rays, triangles=triangles)
        query_seconds = time.perf_counter() - query_started
        total_query_seconds += query_seconds

        hit_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in rows}
        compare_summary = None
        if compare_backend and compare_backend != "none":
            compare_rows = _run_backend_rows(compare_backend, rays=rays, triangles=triangles)
            compare_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in compare_rows}
            compare_summary = {
                "backend": compare_backend,
                "matches": compare_lookup == hit_lookup,
            }
        shading_started = time.perf_counter()
        image: list[list[tuple[int, int, int]]] = []
        hit_pixels = 0
        pending_hits: list[tuple[int, int, rt.Ray3D, tuple[float, float, float]]] = []
        for py in range(height):
            row_pixels: list[tuple[int, int, int]] = []
            for px in range(width):
                background = _background_pixel(px, py, width, height)
                ray = rays[py * width + px]
                if hit_lookup.get(ray.id, 0) <= 0:
                    row_pixels.append(background)
                    continue
                intersection = _ray_sphere_intersection(ray, center=center, radius=radius)
                if intersection is None:
                    row_pixels.append(background)
                    continue
                _, hit_point = intersection
                pending_hits.append((py, px, ray, hit_point))
                row_pixels.append(background)
                hit_pixels += 1
            image.append(row_pixels)

        shadow_rays: list[rt.Ray3D] = []
        for _, _, ray, hit_point in pending_hits:
            shadow_rays.extend(
                _make_shadow_rays(
                    ray=ray,
                    hit_point=hit_point,
                    center=center,
                    radius=radius,
                    lights=lights,
                    base_id=ray.id * len(lights),
                )
            )
        shadow_ray_total = len(shadow_rays)
        shadow_query_seconds = 0.0
        shadow_lookup: dict[int, int] = {}
        if shadow_rays:
            shadow_started = time.perf_counter()
            shadow_rows = _run_backend_rows(backend, rays=tuple(shadow_rays), triangles=triangles)
            shadow_query_seconds = time.perf_counter() - shadow_started
            shadow_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in shadow_rows}

        for py, px, ray, hit_point in pending_hits:
            shadow_factors = tuple(
                0.0 if shadow_lookup.get(ray.id * len(lights) + light_index, 0) > 0 else 1.0
                for light_index in range(len(lights))
            )
            image[py][px] = _shade_hit(
                ray,
                hit_point,
                center=center,
                radius=radius,
                lights=lights,
                shadow_factors=shadow_factors,
            )

        projected_center = _project_world_to_screen(
            center,
            eye=eye,
            target=target,
            up_hint=up_hint,
            width=width,
            height=height,
            fov_y_degrees=fov_y,
        )
        if projected_center is not None:
            _paint_ground_shadow(
                image,
                center_x=projected_center[0],
                center_y=min(height - 1.0, projected_center[1] + height * 0.23),
                radius_x=width * 0.16,
                radius_y=height * 0.055,
                alpha=0.36,
            )
            _paint_halo(
                image,
                center_x=projected_center[0],
                center_y=projected_center[1],
                radius=min(width, height) * 0.18,
                color=(88, 138, 255),
                alpha=0.18,
            )

        _overlay_lights(
            image,
            phase=phase,
            eye=eye,
            target=target,
            up_hint=up_hint,
            width=width,
            height=height,
            fov_y_degrees=fov_y,
        )
        total_shadow_query_seconds += shadow_query_seconds
        shading_seconds = time.perf_counter() - shading_started
        total_shading_seconds += shading_seconds

        frame_path = output_dir / f"frame_{frame_index:03d}.ppm"
        _write_ppm(frame_path, image)
        summary_frames.append(
            {
                "frame_index": frame_index,
                "frame_path": str(frame_path),
                "query_seconds": query_seconds,
                "shadow_query_seconds": shadow_query_seconds,
                "shading_seconds": shading_seconds,
                "rt_rows": len(rows),
                "shadow_rays": shadow_ray_total,
                "hit_pixels": hit_pixels,
                "compare_backend": compare_summary,
            }
        )

    summary = {
        "backend": backend,
        "image_width": width,
        "image_height": height,
        "frame_count": frame_count,
        "triangle_count": len(triangles),
        "latitude_bands": latitude_bands,
        "longitude_bands": longitude_bands,
        "spin_speed": spin_speed,
        "total_query_seconds": total_query_seconds,
        "total_shadow_query_seconds": total_shadow_query_seconds,
        "total_shading_seconds": total_shading_seconds,
        "query_share": (total_query_seconds + total_shadow_query_seconds)
        / max(1.0e-9, total_query_seconds + total_shadow_query_seconds + total_shading_seconds),
        "frames": summary_frames,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def _run_backend_rows(backend: str, **inputs):
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(ray_triangle_hitcount_3d_demo, **inputs)
    if backend == "embree":
        return rt.run_embree(ray_triangle_hitcount_3d_demo, **inputs)
    if backend == "optix":
        return rt.run_optix(ray_triangle_hitcount_3d_demo, **inputs)
    if backend == "vulkan":
        return rt.run_vulkan(ray_triangle_hitcount_3d_demo, **inputs)
    raise ValueError(f"unsupported backend for rtdl_spinning_ball_3d_demo: {backend}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a 3D spinning-ball RTDL demo.")
    parser.add_argument("--backend", default="cpu_python_reference")
    parser.add_argument("--compare-backend", default="none")
    parser.add_argument("--width", type=int, default=192)
    parser.add_argument("--height", type=int, default=192)
    parser.add_argument("--latitude-bands", type=int, default=32)
    parser.add_argument("--longitude-bands", type=int, default=64)
    parser.add_argument("--frames", type=int, default=12)
    parser.add_argument("--spin-speed", type=float, default=1.1)
    parser.add_argument("--output-dir", type=Path, default=Path("build/rtdl_spinning_ball_3d_demo"))
    args = parser.parse_args()

    summary = render_spinning_ball_3d_frames(
        backend=args.backend,
        compare_backend=args.compare_backend,
        width=args.width,
        height=args.height,
        latitude_bands=args.latitude_bands,
        longitude_bands=args.longitude_bands,
        frame_count=args.frames,
        spin_speed=args.spin_speed,
        output_dir=args.output_dir,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
