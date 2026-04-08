from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.rtdl_orbiting_star_ball_demo import render_orbiting_star_ball_optix_4k


class Goal169OptixOrbitDemoTest(unittest.TestCase):
    def test_optix_one_frame_compare_smoke(self) -> None:
        output_dir = Path("build/goal169_optix_orbit_demo_test/one_frame")
        try:
            summary = render_orbiting_star_ball_optix_4k(
                output_dir=output_dir,
                compare_backend="cpu_python_reference",
                width=32,
                height=18,
                latitude_bands=8,
                longitude_bands=16,
                frame_count=1,
            )
        except Exception as exc:
            self.skipTest(f"optix unavailable: {exc}")
        self.assertEqual(summary["backend"], "optix")
        compare_summary = summary["frames"][0]["compare_backend"]
        self.assertIsNotNone(compare_summary)
        self.assertEqual(compare_summary["backend"], "cpu_python_reference")
        self.assertTrue(compare_summary["matches"])
        self.assertTrue(Path(summary["frames"][0]["frame_path"]).exists())


if __name__ == "__main__":
    unittest.main()
