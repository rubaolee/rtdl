import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.visual_demo.rtdl_orbit_lights_ball_demo import make_disk_mesh
from examples.visual_demo.rtdl_orbit_lights_ball_demo import make_scanline_rays
from examples.visual_demo.rtdl_orbit_lights_ball_demo import ray_triangle_hitcount_demo
from tests.rtdl_sorting_test import optix_available


@unittest.skipUnless(optix_available(), "OptiX is not available in the current environment")
class Goal162OptixVisualDemoParityTest(unittest.TestCase):
    def test_optix_matches_cpu_for_visual_demo_frame_zero(self) -> None:
        frame_index = 0
        frame_count = 4
        phase = frame_index / frame_count
        center_x = 0.16 * math.cos(phase * math.tau * 0.8)
        center_y = 0.10 * math.sin(phase * math.tau * 1.3)
        radius = 0.92 + 0.05 * math.sin(phase * math.tau * 1.1)

        triangles = make_disk_mesh(
            triangle_count=1024,
            radius=radius,
            center_x=center_x,
            center_y=center_y,
        )
        rays = make_scanline_rays(
            sample_rows=96 * 4,
            scene_left=-1.55,
            scene_right=1.55,
            scene_bottom=-1.45,
            scene_top=1.45,
        )

        cpu_rows = rt.run_cpu(ray_triangle_hitcount_demo, rays=rays, triangles=triangles)
        optix_rows = rt.run_optix(ray_triangle_hitcount_demo, rays=rays, triangles=triangles)
        self.assertEqual(optix_rows, cpu_rows)


if __name__ == "__main__":
    unittest.main()
