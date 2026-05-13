from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal1808_v2_partner_optix_pod"
REPORT = ROOT / "docs" / "reports" / "goal1808_v2_partner_optix_pod_hardware_evidence_2026-05-13.md"


class Goal1808V2PartnerOptixPodHardwareEvidenceTest(unittest.TestCase):
    def test_pod_environment_records_rtx_hardware_and_commit(self) -> None:
        environment = (ARTIFACT_DIR / "environment.txt").read_text(encoding="utf-8")
        self.assertIn("commit=573b18183cd33bed3512c3e49d5e64017ee167fc", environment)
        self.assertIn("NVIDIA RTX 4000 Ada", environment)
        self.assertIn("Driver Version: 550.127.05", environment)
        self.assertIn("CUDA Version: 12.4", environment)
        self.assertIn("optix_prefix=/root/vendor/optix-dev", environment)

    def test_partner_probe_records_real_cuda_frameworks(self) -> None:
        probe = json.loads((ARTIFACT_DIR / "partner_probe.json").read_text(encoding="utf-8"))
        self.assertEqual(probe["torch"], "2.5.1+cu121")
        self.assertTrue(probe["torch_cuda_available"])
        self.assertEqual(probe["torch_cuda"], "12.1")
        self.assertEqual(probe["cupy"], "14.0.1")
        self.assertEqual(probe["cupy_device_count"], 1)

    def test_summary_preserves_required_claim_guards(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(
            sorted(summary),
            ["example_cupy-cuda_optix", "example_numpy_optix", "example_torch-cuda_optix"],
        )
        expected_protocols = {
            "example_cupy-cuda_optix": ["cupy"],
            "example_numpy_optix": ["numpy"],
            "example_torch-cuda_optix": ["torch"],
        }
        for name, result in summary.items():
            self.assertEqual(result["hit_count"], 1)
            self.assertEqual(result["transfer_mode"], "host_stage")
            self.assertEqual(result["source_protocols"], expected_protocols[name])
            self.assertFalse(result["true_zero_copy_authorized"])
            self.assertFalse(result["rt_core_speedup_claim_authorized"])

    def test_report_keeps_release_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", report)
        self.assertIn("does not prove", report)
        self.assertIn("true zero-copy", report)
        self.assertIn("RT-core speedup", report)
        self.assertIn("v2.0 release readiness", report)
        self.assertIn("final release-scope audit", report)

    def test_focused_unittest_log_passed(self) -> None:
        log = (ARTIFACT_DIR / "focused_unittest.log").read_text(encoding="utf-8")
        self.assertIn("Ran 31 tests", log)
        self.assertIn("OK (skipped=2)", log)


if __name__ == "__main__":
    unittest.main()
