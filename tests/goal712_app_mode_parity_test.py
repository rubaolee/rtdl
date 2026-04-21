from __future__ import annotations

import unittest

from examples import rtdl_robot_collision_screening_app as robot_app
from examples import rtdl_segment_polygon_anyhit_rows as segment_anyhit_app
from examples import rtdl_segment_polygon_hitcount as segment_hitcount_app


def _canonical(value):
    if isinstance(value, dict):
        return {
            key: _canonical(item)
            for key, item in value.items()
            if key not in {"backend", "requested_backend", "data_flow", "prepared_dataset"}
        }
    if isinstance(value, list) or isinstance(value, tuple):
        return sorted((_canonical(item) for item in value), key=repr)
    if isinstance(value, float):
        return round(value, 12)
    return value


class Goal712AppModeParityTest(unittest.TestCase):
    def test_segment_polygon_hitcount_identifies_app(self) -> None:
        payload = segment_hitcount_app.run_case(
            "cpu_python_reference",
            "authored_segment_polygon_minimal",
        )
        self.assertEqual(payload["app"], "segment_polygon_hitcount")

    def test_segment_polygon_anyhit_modes_match_embree(self) -> None:
        for output_mode in ("rows", "segment_flags", "segment_counts"):
            with self.subTest(output_mode=output_mode):
                cpu = segment_anyhit_app.run_case(
                    "cpu_python_reference",
                    "authored_segment_polygon_minimal",
                    output_mode,
                )
                embree = segment_anyhit_app.run_case(
                    "embree",
                    "authored_segment_polygon_minimal",
                    output_mode,
                )
                self.assertEqual(cpu["app"], "segment_polygon_anyhit_rows")
                self.assertEqual(embree["app"], "segment_polygon_anyhit_rows")
                self.assertEqual(_canonical(cpu), _canonical(embree))

    def test_robot_collision_output_modes_match_embree(self) -> None:
        for output_mode in ("full", "pose_flags", "hit_count"):
            with self.subTest(output_mode=output_mode):
                cpu = robot_app.run_app("cpu_python_reference", output_mode=output_mode)
                embree = robot_app.run_app("embree", output_mode=output_mode)
                self.assertEqual(cpu["app"], "robot_collision_screening")
                self.assertEqual(embree["app"], "robot_collision_screening")
                self.assertEqual(_canonical(cpu), _canonical(embree))


if __name__ == "__main__":
    unittest.main()
