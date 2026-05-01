from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal833ExternalGpuBackendReportIntakeTest(unittest.TestCase):
    def test_external_reports_are_preserved_and_intake_exists(self) -> None:
        optix = ROOT / "docs" / "reports" / "goal727_gemini_optix_rtx_engine_polish_review_2026-04-23.md"
        vulkan_hiprt = ROOT / "docs" / "reports" / "gemini_vulkan_hiprt_status_report_2026-04-23.md"
        intake = ROOT / "docs" / "reports" / "goal833_external_gpu_backend_report_intake_2026-04-23.md"

        for path in (optix, vulkan_hiprt, intake):
            self.assertTrue(path.exists(), str(path))

        optix_text = optix.read_text(encoding="utf-8")
        self.assertIn("Verdict", optix_text)
        self.assertIn("ACCEPT", optix_text)

        status_text = vulkan_hiprt.read_text(encoding="utf-8")
        self.assertIn("Vulkan Engine Status", status_text)
        self.assertIn("HIP RT Engine Status", status_text)

        intake_text = intake.read_text(encoding="utf-8")
        self.assertIn("RTX 4090 cloud evidence should be treated as OptiX-only", intake_text)
        self.assertIn("No Vulkan/HIPRT comparison should be inferred", intake_text)
        self.assertIn("No cloud action was taken", intake_text)


if __name__ == "__main__":
    unittest.main()
