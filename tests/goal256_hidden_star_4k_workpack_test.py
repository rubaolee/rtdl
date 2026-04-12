from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.visual_demo.render_hidden_star_chunked_video import render_chunked_video
from examples.visual_demo.rtdl_hidden_star_stable_ball_demo import render_hidden_star_stable_ball_frames


class _FakeWriter:
    def __init__(self) -> None:
        self.frames: list[object] = []

    def __enter__(self) -> "_FakeWriter":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def append_data(self, frame: object) -> None:
        self.frames.append(frame)


class _FakeImageIO:
    def __init__(self, writer: _FakeWriter) -> None:
        self._writer = writer

    def get_writer(self, *args, **kwargs) -> _FakeWriter:
        return self._writer

    def imread(self, path: str | Path) -> bytes:
        return Path(path).read_bytes()


class Goal256HiddenStar4KWorkpackTest(unittest.TestCase):
    def test_crossed_dual_hidden_scene_reports_two_lights(self) -> None:
        output_dir = Path("build/goal256_hidden_star_4k_workpack_test/crossed_dual")
        summary = render_hidden_star_stable_ball_frames(
            backend="cpu_python_reference",
            compare_backend=None,
            width=24,
            height=24,
            latitude_bands=8,
            longitude_bands=16,
            frame_count=2,
            output_dir=output_dir,
            jobs=1,
            shadow_mode="rtdl_light_to_surface",
            scene="crossed_dual_hidden",
        )
        self.assertEqual(summary["scene"], "crossed_dual_hidden")
        self.assertEqual(summary["light_count"], 2)
        self.assertEqual(summary["light_layout"], "crossed_dual_rtdl_light_to_surface_shadow")
        self.assertTrue(any(int(frame["shadow_rays"]) > 0 for frame in summary["frames"]))

    def test_chunked_video_summary_and_chunk_cleanup(self) -> None:
        output_dir = Path("build/goal256_hidden_star_4k_workpack_test/chunked")
        writer = _FakeWriter()
        fake_imageio = _FakeImageIO(writer)
        with mock.patch("examples.visual_demo.render_hidden_star_chunked_video.imageio", fake_imageio):
            summary = render_chunked_video(
                backend="cpu_python_reference",
                compare_backend=None,
                width=20,
                height=20,
                latitude_bands=6,
                longitude_bands=12,
                total_frames=3,
                chunk_frames=2,
                output_dir=output_dir,
                jobs=1,
                shadow_mode="rtdl_light_to_surface",
                scene="crossed_dual_hidden",
                fps=32,
            )
        self.assertEqual(summary["scene"], "crossed_dual_hidden")
        self.assertEqual(summary["total_frames"], 3)
        self.assertEqual(len(summary["chunks"]), 2)
        self.assertEqual(len(writer.frames), 3)
        self.assertTrue((output_dir / "summary.json").exists())
        self.assertFalse(list((output_dir / "chunks").rglob("frame_*.ppm")))


if __name__ == "__main__":
    unittest.main()
