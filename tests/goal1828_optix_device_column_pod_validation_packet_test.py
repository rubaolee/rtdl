from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_goal1828_optix_device_column_pod_validation.py"
REPORT = ROOT / "docs" / "reports" / "goal1828_optix_device_column_pod_validation_packet_2026-05-13.md"


class Goal1828OptixDeviceColumnPodValidationPacketTest(unittest.TestCase):
    def test_pod_validation_script_exercises_device_ray_and_triangle_paths(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("pack_optix_ray_any_hit_2d_device_ray_inputs", text)
        self.assertIn("pack_optix_ray_any_hit_2d_device_triangle_inputs", text)
        self.assertIn("prepare_optix_ray_triangle_any_hit_2d_device_triangles", text)
        self.assertIn("count_device_rays", text)
        self.assertIn("torch.cuda.is_available", text)
        self.assertIn('"true_zero_copy_authorized": False', text)
        self.assertIn('"v2_0_release_authorized": False', text)

    def test_report_is_ready_for_pod_without_overclaiming_release(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("`ready-for-pod`", text)
        self.assertIn("does not claim hardware success yet", text)
        self.assertIn("If it passes on an RTX pod", text)
        self.assertIn("true zero-copy", text)
        self.assertIn("v2.0 release readiness", text)
        self.assertIn("Goal1814", text)


if __name__ == "__main__":
    unittest.main()
