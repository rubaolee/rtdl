import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal698_rtx_cloud_validation_commands.sh"
RUNBOOK = ROOT / "docs" / "handoff" / "GOAL698_RTX_CLOUD_VALIDATION_RUNBOOK_2026-04-21.md"


class Goal698RtxCloudValidationRunbookTest(unittest.TestCase):
    def test_cloud_script_has_required_preflights_and_artifacts(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "nvidia-smi",
            "OPTIX_PREFIX",
            "include/optix.h",
            "make build-optix",
            "RTDL_OPTIX_LIB",
            "RTDL_NVCC",
            "RTDL_OPTIX_PTX_COMPILER",
            "goal697_optix_fixed_radius_phase_profiler.py",
            "goal698_rtx_cloud_environment_",
            "goal698_rtx_cloud_fixed_radius_phase_profile_",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_cloud_script_does_not_embed_credentials(self):
        text = SCRIPT.read_text(encoding="utf-8").lower()
        forbidden = (
            "aws_secret_access_key",
            "aws_access_key_id=",
            "gcp_service_account",
            "azure_client_secret",
            "password=",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_runbook_preserves_honest_interpretation_boundary(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        for phrase in (
            "NVIDIA L4",
            "Minimal User Action",
            "OptiX SDK headers",
            "Do not claim general OptiX speedup",
            "Do not claim KNN/Hausdorff/ANN/Barnes-Hut acceleration",
            "stop or terminate the cloud VM",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
