import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3979_short_row_scale_calibration_probe_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3979_short_row_scale_calibration_probe_2026-06-08"


class Goal3979ShortRowScaleCalibrationProbeTest(unittest.TestCase):
    def test_robot_collision_repeat_probe_shows_hot_traversal_is_tiny(self) -> None:
        payload = json.loads((ARTIFACT / "robot_collision_repeats30.stdout.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["mode"], "optix_prepared_device_count")
        self.assertEqual(payload["warmup_protocol"]["repeat_count"], 30)
        timing = payload["benchmark_timing_sec"]
        self.assertGreater(timing["app_lowering_sec"], 0.1)
        self.assertGreater(timing["tail_phase_prepare_build_sec"], 0.01)
        self.assertLess(timing["tail_phase_traversal_sec"], 0.001)
        self.assertLess(timing["tail_total_run_sec"], 0.001)

    def test_raydb_repeat_probe_shows_wrapper_duration_is_not_hot_path(self) -> None:
        payload = json.loads((ARTIFACT / "raydb_repeat25.stdout.json").read_text(encoding="utf-8"))
        metadata = payload["metadata"]
        timings = metadata["timings"]
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(metadata["prepared_internal_repeat"], 25)
        self.assertLess(payload["elapsed_sec"], 0.01)
        self.assertLess(timings["native_call_wall"], 0.01)
        self.assertLess(timings["traversal"], 0.001)
        self.assertGreater(timings["cold_prepare_total"], 0.1)

    def test_report_rejects_blind_repeat_calibration(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Do not update the current scale registry",
            "merely increasing repeat counts",
            "representative_hot_path_metric",
            "negative calibration probe",
            "does not authorize",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
