import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal703_runpod_rtx_validation_commands.sh"
HANDOFF = ROOT / "docs" / "handoff" / "GOAL703_RUNPOD_RTX_VALIDATION_HANDOFF_2026-04-21.md"


class Goal703RunpodRtxValidationHandoffTest(unittest.TestCase):
    def test_runpod_script_delegates_to_existing_rtx_validation(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "nvidia-smi",
            "nvcc",
            "OPTIX_PREFIX",
            "include/optix.h",
            "git clone",
            "libc6-dev-i386",
            "libgeos-dev",
            "RTDL_OPTIX_PTX_COMPILER",
            "goal698_rtx_cloud_validation_commands.sh",
            "goal699_rtx_profile_report.py",
            "--profile-json",
            "--environment",
            "goal703_runpod_rtx_profile_report_",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_runpod_script_does_not_manage_cloud_credentials_or_billing(self):
        text = SCRIPT.read_text(encoding="utf-8").lower()
        forbidden = (
            "runpod_api_key",
            "aws_secret_access_key",
            "gcp_service_account",
            "azure_client_secret",
            "password=",
            "terminatepod",
            "podterminate",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_handoff_preserves_gpu_choice_and_claim_boundaries(self):
        text = HANDOFF.read_text(encoding="utf-8")
        for phrase in (
            "RTX 4090",
            "L40S",
            "L4",
            "Avoid T4",
            "Use Secure Cloud first",
            "Make the NVIDIA OptiX SDK headers available",
            "libc6-dev-i386",
            "NVIDIA RTX A5000",
            "RTDL_OPTIX_PTX_COMPILER=nvcc",
            "Do not claim broad RTDL speedup",
            "KNN, Hausdorff, ANN, Barnes-Hut, graph, or DB",
            "terminate the Pod",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
