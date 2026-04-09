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

from examples.rtdl_orbiting_star_ball_demo import _make_background_image
from examples.rtdl_orbiting_star_ball_demo import _make_shadow_rays
from examples.rtdl_orbiting_star_ball_demo import _materialize_orbit_frames
from examples.rtdl_orbiting_star_ball_demo import _orbit_frame_paths
from examples.rtdl_orbiting_star_ball_demo import _orbit_phase_samples
from examples.rtdl_orbiting_star_ball_demo import _overlay_star_and_ground
from examples.rtdl_orbiting_star_ball_demo import _shade_orbit_hit
from examples.rtdl_orbiting_star_ball_demo import _shade_pending_hits_numpy
from examples.rtdl_orbiting_star_ball_demo import _write_frame_meta
from examples.rtdl_spinning_ball_3d_demo import _paint_ground_shadow
from examples.rtdl_spinning_ball_3d_demo import _paint_halo
from examples.rtdl_spinning_ball_3d_demo import _project_world_to_screen
from examples.rtdl_spinning_ball_3d_demo import _ray_sphere_intersection
from examples.rtdl_spinning_ball_3d_demo import _run_backend_rows
from examples.rtdl_spinning_ball_3d_demo import _write_ppm
from examples.rtdl_spinning_ball_3d_demo import make_camera_rays
from examples.rtdl_spinning_ball_3d_demo import make_uv_sphere_mesh


_SMOOTH_WORKER_STATE: dict[str, object] = {}
_SMOOTH_DEMO_THEMES: dict[str, dict[str, object]] = {
    "true_onelight": {
        "lights": (
            {
                "position": (4.35, 2.35, 5.55),
                "color": (1.0, 0.87, 0.34),
                "intensity": 3.05,
                "display_color": (255, 214, 98),
                "ground_core_color": (255, 226, 132),
                "display_alpha": 1.0,
                "ground_alpha_scale": 1.05,
                "size_scale": 1.36,
            },
        ),
        "halo_color": (76, 120, 255),
        "halo_alpha": 0.17,
        "ground_shadow_alpha": 0.28,
    },
    "deep_blue_redsun": {
        "lights": (
            {
                "position": (4.55, 2.55, 5.65),
                "color": (1.0, 0.34, 0.24),
                "intensity": 3.55,
                "display_color": (255, 92, 64),
                "ground_core_color": (255, 128, 96),
                "display_alpha": 1.0,
                "ground_alpha_scale": 1.12,
                "size_scale": 1.44,
            },
        ),
        "halo_color": (44, 98, 255),
        "halo_alpha": 0.23,
        "ground_shadow_alpha": 0.20,
    },
}


def _smooth_demo_theme(theme: str = "true_onelight") -> dict[str, object]:
    theme_spec = _SMOOTH_DEMO_THEMES.get(theme)
    if theme_spec is None:
        raise ValueError(f"unsupported smooth-camera theme: {theme}")
    return theme_spec


def _smooth_demo_lights(theme: str = "true_onelight") -> tuple[dict[str, object], ...]:
    return _smooth_demo_theme(theme)["lights"]  # type: ignore[return-value]


def _compare_hit_lookups(
    hit_lookup: dict[int, int],
    compare_lookup: dict[int, int],
) -> dict[str, object]:
    ray_ids = set(hit_lookup) | set(compare_lookup)
    exact_mismatch_count = sum(1 for ray_id in ray_ids if hit_lookup.get(ray_id) != compare_lookup.get(ray_id))
    visible_mismatch_count = sum(
        1
        for ray_id in ray_ids
        if (hit_lookup.get(ray_id, 0) > 0) != (compare_lookup.get(ray_id, 0) > 0)
    )
    return {
        "matches": visible_mismatch_count == 0,
        "exact_matches": exact_mismatch_count == 0,
        "visible_mismatch_count": visible_mismatch_count,
        "exact_mismatch_count": exact_mismatch_count,
    }


def _camera_eye_for_phase(phase: float, *, center: tuple[float, float, float]) -> tuple[float, float, float]:
    azimuth = math.radians(-42.0 + 84.0 * phase)
    distance = 6.28 - 0.16 * math.cos(phase * math.tau)
    height = center[1] + 0.28 + 0.06 * math.sin(phase * math.tau)
    return (
        center[0] + math.sin(azimuth) * distance,
        height,
        center[2] + math.cos(azimuth) * distance,
    )


def _restore_smooth_frame(task: tuple[int, float], state: dict[str, object]) -> dict[str, object] | None:
    frame_index, phase = task
    output_dir = Path(state["output_dir"])  # type: ignore[arg-type]
    final_path, raw_path, meta_path = _orbit_frame_paths(output_dir, frame_index)
    if not raw_path.exists() or not meta_path.exists():
        return None
    try:
        row = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if int(row.get("frame_index", -1)) != frame_index:
        return None
    if abs(float(row.get("phase", -999.0)) - phase) > 1.0e-12:
        return None
    row["frame_path"] = str(final_path)
    row["raw_frame_path"] = str(raw_path)
    return row


def _init_smooth_worker(state: dict[str, object]) -> None:
    global _SMOOTH_WORKER_STATE
    _SMOOTH_WORKER_STATE = state


def _render_smooth_frame(task: tuple[int, float]) -> dict[str, object]:
    frame_index, phase = task
    state = _SMOOTH_WORKER_STATE
    restored = _restore_smooth_frame(task, state)
    if restored is not None:
        return restored

    width = int(state["width"])  # type: ignore[arg-type]
    height = int(state["height"])  # type: ignore[arg-type]
    center = state["center"]  # type: ignore[assignment]
    radius = float(state["radius"])  # type: ignore[arg-type]
    backend = str(state["backend"])  # type: ignore[arg-type]
    compare_backend = state["compare_backend"]  # type: ignore[assignment]
    fov_y = float(state["fov_y"])  # type: ignore[arg-type]
    up_hint = state["up_hint"]  # type: ignore[assignment]
    target = state["target"]  # type: ignore[assignment]
    triangles = state["triangles"]  # type: ignore[assignment]
    lights = state["lights"]  # type: ignore[assignment]
    light_count = int(state["light_count"])  # type: ignore[arg-type]
    halo_color = state["halo_color"]  # type: ignore[assignment]
    halo_alpha = float(state["halo_alpha"])  # type: ignore[arg-type]
    ground_shadow_alpha = float(state["ground_shadow_alpha"])  # type: ignore[arg-type]

    eye = _camera_eye_for_phase(phase, center=center)  # type: ignore[arg-type]
    rays = make_camera_rays(
        width=width,
        height=height,
        eye=eye,
        target=target,  # type: ignore[arg-type]
        up_hint=up_hint,  # type: ignore[arg-type]
        fov_y_degrees=fov_y,
    )

    query_started = time.perf_counter()
    rows = _run_backend_rows(backend, rays=rays, triangles=triangles)
    query_seconds = time.perf_counter() - query_started
    hit_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in rows}

    compare_summary = None
    if frame_index == 0 and compare_backend and compare_backend != "none":
        compare_rows = _run_backend_rows(compare_backend, rays=rays, triangles=triangles)
        compare_lookup = {int(row["ray_id"]): int(row["hit_count"]) for row in compare_rows}
        compare_summary = {"backend": compare_backend, **_compare_hit_lookups(hit_lookup, compare_lookup)}

    source_image = state["background_image"]  # type: ignore[index]
    if np is not None and hasattr(source_image, "shape"):
        image = source_image.copy()
    else:
        image = [list(row) for row in source_image]  # type: ignore[arg-type]

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

    shading_started = time.perf_counter()
    shadow_rays: list[rt.Ray3D] = []
    for _, _, ray, hit_point in pending_hits:
        for light_index, light in enumerate(lights):
            shadow_rays.extend(
                _make_shadow_rays(
                    ray=ray,
                    hit_point=hit_point,
                    center=center,  # type: ignore[arg-type]
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
            pending_hits=pending_hits,
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
                center=center,  # type: ignore[arg-type]
                lights=lights,
                shadow_lookup=shadow_lookup,
                light_count=light_count,
            )

    projected_center = _project_world_to_screen(
        center,  # type: ignore[arg-type]
        eye=eye,
        target=target,  # type: ignore[arg-type]
        up_hint=up_hint,  # type: ignore[arg-type]
        width=width,
        height=height,
        fov_y_degrees=fov_y,
    )
    if projected_center is not None:
        _paint_ground_shadow(
            image,
            center_x=projected_center[0],
            center_y=min(height - 1.0, projected_center[1] + height * 0.24),
            radius_x=width * 0.18,
            radius_y=height * 0.058,
            alpha=ground_shadow_alpha,
        )
        _paint_halo(
            image,
            center_x=projected_center[0],
            center_y=projected_center[1],
            radius=min(width, height) * 0.15,
            color=halo_color,  # type: ignore[arg-type]
            alpha=halo_alpha,
        )

    if bool(state["show_light_source"]):  # type: ignore[arg-type]
        for light in lights:
            _overlay_star_and_ground(
                image,
                light=light,
                eye=eye,
                target=target,  # type: ignore[arg-type]
                up_hint=up_hint,  # type: ignore[arg-type]
                width=width,
                height=height,
                fov_y_degrees=fov_y,
                center=center,  # type: ignore[arg-type]
                radius=radius,
                show_light_source=True,
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
        "eye": [float(eye[0]), float(eye[1]), float(eye[2])],
        "query_seconds": query_seconds,
        "shadow_query_seconds": shadow_query_seconds,
        "shading_seconds": shading_seconds,
        "rt_rows": len(rows),
        "shadow_rays": len(shadow_rays),
        "hit_pixels": hit_pixels,
        "compare_backend": compare_summary,
    }
    _write_frame_meta(meta_path, row)
    return row


def render_smooth_camera_orbit_frames(
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
    phase_mode: str = "uniform",
    theme: str = "true_onelight",
) -> dict[str, object]:
    wall_started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    center = (0.0, 0.08, 0.0)
    target = (0.0, 0.08, 0.0)
    up_hint = (0.0, 1.0, 0.0)
    radius = 1.46
    fov_y = 28.0
    theme_spec = _smooth_demo_theme(theme)
    lights = theme_spec["lights"]  # type: ignore[assignment]
    triangles = make_uv_sphere_mesh(
        latitude_bands=latitude_bands,
        longitude_bands=longitude_bands,
        radius=radius,
        center=center,
    )
    phases = _orbit_phase_samples(frame_count, mode=phase_mode)
    worker_state: dict[str, object] = {
        "backend": backend,
        "compare_backend": compare_backend,
        "background_image": _make_background_image(width, height),
        "center": center,
        "radius": radius,
        "target": target,
        "up_hint": up_hint,
        "fov_y": fov_y,
        "width": width,
        "height": height,
        "triangles": triangles,
        "lights": lights,
        "light_count": len(lights),
        "halo_color": theme_spec["halo_color"],
        "halo_alpha": theme_spec["halo_alpha"],
        "ground_shadow_alpha": theme_spec["ground_shadow_alpha"],
        "show_light_source": show_light_source,
        "output_dir": output_dir,
    }
    tasks = list(enumerate(phases))
    if jobs <= 1:
        _init_smooth_worker(worker_state)
        summary_frames = [_render_smooth_frame(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs, initializer=_init_smooth_worker, initargs=(worker_state,)) as executor:
            summary_frames = list(executor.map(_render_smooth_frame, tasks))
    summary_frames.sort(key=lambda row: int(row["frame_index"]))
    _materialize_orbit_frames(summary_frames, temporal_blend_alpha)

    total_query_seconds = sum(float(row["query_seconds"]) for row in summary_frames)
    total_shadow_query_seconds = sum(float(row["shadow_query_seconds"]) for row in summary_frames)
    total_shading_seconds = sum(float(row["shading_seconds"]) for row in summary_frames)
    summary = {
        "backend": backend,
        "image_width": width,
        "image_height": height,
        "frame_count": frame_count,
        "jobs": jobs,
        "light_count": len(lights),
        "numpy_fast_path": np is not None,
        "show_light_source": show_light_source,
        "temporal_blend_alpha": temporal_blend_alpha,
        "phase_mode": phase_mode,
        "camera_motion": "front_arc",
        "theme": theme,
        "camera_sweep_degrees": 84.0,
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


def render_smooth_camera_orbit_vulkan_frames(
    *,
    output_dir: Path,
    compare_backend: str | None = "cpu_python_reference",
    width: int = 1024,
    height: int = 1024,
    latitude_bands: int = 80,
    longitude_bands: int = 160,
    frame_count: int = 320,
    jobs: int = 1,
    show_light_source: bool = False,
    temporal_blend_alpha: float = 0.0,
    phase_mode: str = "uniform",
    theme: str = "true_onelight",
) -> dict[str, object]:
    return render_smooth_camera_orbit_frames(
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
        theme=theme,
    )


def render_smooth_camera_orbit_optix_frames(
    *,
    output_dir: Path,
    compare_backend: str | None = "cpu_python_reference",
    width: int = 1024,
    height: int = 1024,
    latitude_bands: int = 80,
    longitude_bands: int = 160,
    frame_count: int = 320,
    jobs: int = 1,
    show_light_source: bool = False,
    temporal_blend_alpha: float = 0.0,
    phase_mode: str = "uniform",
    theme: str = "true_onelight",
) -> dict[str, object]:
    return render_smooth_camera_orbit_frames(
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
        theme=theme,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a smooth camera-orbit RTDL sphere demo.")
    parser.add_argument("--backend", default="cpu_python_reference")
    parser.add_argument("--compare-backend", default="none")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--latitude-bands", type=int, default=80)
    parser.add_argument("--longitude-bands", type=int, default=160)
    parser.add_argument("--frames", type=int, default=320)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--show-light-source", action="store_true")
    parser.add_argument("--temporal-blend-alpha", type=float, default=0.0)
    parser.add_argument("--phase-mode", choices=("weighted", "uniform"), default="uniform")
    parser.add_argument("--theme", choices=("true_onelight", "deep_blue_redsun"), default="true_onelight")
    parser.add_argument("--output-dir", type=Path, default=Path("build/rtdl_smooth_camera_orbit_demo"))
    args = parser.parse_args()

    summary = render_smooth_camera_orbit_frames(
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
        theme=args.theme,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
