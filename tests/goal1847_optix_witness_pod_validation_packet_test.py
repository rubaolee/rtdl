from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_goal1828_optix_device_column_pod_validation.py"
REPORT = ROOT / "docs" / "reports" / "goal1847_optix_witness_pod_validation_packet_2026-05-13.md"


class Goal1847OptixWitnessPodValidationPacketTest(unittest.TestCase):
    def test_runner_exposes_mutually_exclusive_witness_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("--output-witnesses", text)
        self.assertIn("--output-flags and --output-witnesses are mutually exclusive", text)
        self.assertIn("write_device_any_hit_witnesses", text)
        self.assertIn("observed_witness_ray_ids", text)
        self.assertIn("observed_witness_primitive_ids", text)
        self.assertIn("first_hit_witness_identity_observed", text)
        self.assertIn("witness_outputs_true_zero_copy_observed", text)

    def test_report_records_exact_pod_commands_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal1847", text)
        self.assertIn("--output-witnesses", text)
        self.assertIn("observed_witness_ray_ids == [101, 102]", text)
        self.assertIn("observed_witness_primitive_ids == [11, 4294967295]", text)
        self.assertIn("not a v2.0 release gate pass", text)
        self.assertIn("pod-required", text)


if __name__ == "__main__":
    unittest.main()
