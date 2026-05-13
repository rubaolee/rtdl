from __future__ import annotations

import pathlib
import json
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_goal1828_optix_device_column_pod_validation.py"
REPORT = ROOT / "docs" / "reports" / "goal1847_optix_witness_pod_validation_packet_2026-05-13.md"
CUPY_ARTIFACT = ROOT / "docs" / "reports" / "goal1847_optix_partner_witness_cupy_pod_validation.json"
TORCH_ARTIFACT = ROOT / "docs" / "reports" / "goal1847_optix_partner_witness_torch_pod_validation.json"


class Goal1847OptixWitnessPodValidationPacketTest(unittest.TestCase):
    def test_runner_exposes_mutually_exclusive_witness_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("--output-witnesses", text)
        self.assertIn("--output-flags, --output-witnesses, and --output-all-witnesses are mutually exclusive", text)
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
        self.assertIn("pass-with-boundary", text)
        self.assertIn("NVIDIA RTX A4500", text)
        self.assertIn("Torch: 2.4.1+cu124", text)
        self.assertIn("CuPy: 14.0.1", text)

    def test_pod_artifacts_record_partner_witness_identity_without_release_claim(self) -> None:
        for partner, artifact in (("cupy", CUPY_ARTIFACT), ("torch", TORCH_ARTIFACT)):
            with self.subTest(partner=partner):
                data = json.loads(artifact.read_text(encoding="utf-8"))
                self.assertEqual(data["status"], "pass")
                self.assertEqual(data["partner"], partner)
                self.assertEqual(data["device"], "NVIDIA RTX A4500")
                self.assertEqual(data["observed_count"], 1)
                self.assertEqual(data["observed_witness_ray_ids"], [101, 102])
                self.assertEqual(data["observed_witness_primitive_ids"], [11, 4294967295])

                boundary = data["claim_boundary"]
                self.assertIs(boundary["ray_column_true_zero_copy_observed"], True)
                self.assertIs(boundary["triangle_scene_true_zero_copy_observed"], True)
                self.assertIs(boundary["witness_outputs_true_zero_copy_observed"], True)
                self.assertIs(boundary["first_hit_witness_identity_observed"], True)
                self.assertIs(boundary["rt_core_speedup_claim_authorized"], False)
                self.assertIs(boundary["v2_0_release_authorized"], False)

                output_metadata = data["output_metadata"]
                self.assertEqual(
                    output_metadata["native_symbol"],
                    "rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses",
                )
                self.assertEqual(
                    output_metadata["witness_contract"],
                    "one first-hit witness row per ray; not all-hit collection",
                )


if __name__ == "__main__":
    unittest.main()
