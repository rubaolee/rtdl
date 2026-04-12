from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

try:
    import imageio.v2 as imageio
except ImportError:  # pragma: no cover - optional packaging dependency
    imageio = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (str(REPO_ROOT), str(SRC_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import render_hidden_star_stable_ball_frames


def render_chunked_video(
    *,
    backend: str,
    compare_backend: str | None,
    width: int,
    height: int,
    latitude_bands: int,
    longitude_bands: int,
    total_frames: int,
    chunk_frames: int,
    output_dir: Path,
    jobs: int,
    shadow_mode: str,
    scene: str,
    fps: int,
) -> dict[str, object]:
    if imageio is None:
        raise RuntimeError(
            "render_hidden_star_chunked_video requires imageio; install it with "
            "`python -m pip install imageio imageio-ffmpeg`."
        )
    wall_started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    chunk_root = output_dir / "chunks"
    chunk_root.mkdir(parents=True, exist_ok=True)

    video_name = (
        f"win_{backend}_hidden_star_earth_{width}x{height}_{total_frames}f_{fps}fps_{scene}_{shadow_mode}_chunked.mp4"
    )
    video_path = output_dir / video_name

    total_query_seconds = 0.0
    total_shadow_query_seconds = 0.0
    total_shading_seconds = 0.0
    chunk_summaries: list[dict[str, object]] = []

    with imageio.get_writer(video_path, fps=fps) as writer:
        for chunk_start in range(0, total_frames, chunk_frames):
            chunk_count = min(chunk_frames, total_frames - chunk_start)
            chunk_end = chunk_start + chunk_count - 1
            chunk_dir = chunk_root / f"chunk_{chunk_start:03d}_{chunk_end:03d}"
            chunk_summary = render_hidden_star_stable_ball_frames(
                backend=backend,
                compare_backend=compare_backend,
                width=width,
                height=height,
                latitude_bands=latitude_bands,
                longitude_bands=longitude_bands,
                frame_count=chunk_count,
                output_dir=chunk_dir,
                jobs=jobs,
                shadow_mode=shadow_mode,
                scene=scene,
                frame_number_offset=chunk_start,
                phase_index_start=chunk_start,
                phase_index_total=total_frames,
            )
            total_query_seconds += float(chunk_summary["total_query_seconds"])
            total_shadow_query_seconds += float(chunk_summary["total_shadow_query_seconds"])
            total_shading_seconds += float(chunk_summary["total_shading_seconds"])

            for frame_index in range(chunk_start, chunk_start + chunk_count):
                frame_path = chunk_dir / f"frame_{frame_index:03d}.ppm"
                writer.append_data(imageio.imread(frame_path))
                frame_path.unlink()

            chunk_summaries.append(
                {
                    "chunk_start": chunk_start,
                    "chunk_end": chunk_end,
                    "frame_count": chunk_count,
                    "wall_clock_seconds": float(chunk_summary["wall_clock_seconds"]),
                    "total_query_seconds": float(chunk_summary["total_query_seconds"]),
                    "total_shadow_query_seconds": float(chunk_summary["total_shadow_query_seconds"]),
                    "total_shading_seconds": float(chunk_summary["total_shading_seconds"]),
                    "summary_path": str(chunk_dir / "summary.json"),
                }
            )

    summary = {
        "backend": backend,
        "compare_backend": compare_backend,
        "width": width,
        "height": height,
        "total_frames": total_frames,
        "chunk_frames": chunk_frames,
        "jobs": jobs,
        "fps": fps,
        "latitude_bands": latitude_bands,
        "longitude_bands": longitude_bands,
        "scene": scene,
        "shadow_mode": shadow_mode,
        "video_path": str(video_path),
        "total_query_seconds": total_query_seconds,
        "total_shadow_query_seconds": total_shadow_query_seconds,
        "total_shading_seconds": total_shading_seconds,
        "wall_clock_seconds": time.perf_counter() - wall_started,
        "chunks": chunk_summaries,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the hidden-star Earth demo in disk-safe chunks and stream frames into one MP4."
    )
    parser.add_argument("--backend", default="embree")
    parser.add_argument("--compare-backend", default=None)
    parser.add_argument("--width", type=int, default=3840)
    parser.add_argument("--height", type=int, default=2160)
    parser.add_argument("--latitude-bands", type=int, default=80)
    parser.add_argument("--longitude-bands", type=int, default=160)
    parser.add_argument("--frames", type=int, default=320)
    parser.add_argument("--chunk-frames", type=int, default=16)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--fps", type=int, default=32)
    parser.add_argument("--shadow-mode", choices=("analytic", "rtdl_light_to_surface"), default="rtdl_light_to_surface")
    parser.add_argument("--scene", choices=("single_hidden", "crossed_dual_hidden"), default="crossed_dual_hidden")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    summary = render_chunked_video(
        backend=args.backend,
        compare_backend=args.compare_backend,
        width=args.width,
        height=args.height,
        latitude_bands=args.latitude_bands,
        longitude_bands=args.longitude_bands,
        total_frames=args.frames,
        chunk_frames=args.chunk_frames,
        output_dir=args.output_dir,
        jobs=args.jobs,
        shadow_mode=args.shadow_mode,
        scene=args.scene,
        fps=args.fps,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
