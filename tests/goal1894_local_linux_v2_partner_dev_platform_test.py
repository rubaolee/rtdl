from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1894_local_linux_v2_partner_dev_platform_2026-05-13.md"


class Goal1894LocalLinuxV2PartnerDevPlatformTest(unittest.TestCase):
    def test_report_records_reusable_local_linux_setup_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: dev-platform-ready-with-boundary", text)
        self.assertIn("192.168.1.20", text)
        self.assertIn("/tmp/rtdl_goal1889_smoke", text)
        self.assertIn("NVIDIA GeForce GTX 1070", text)
        self.assertIn("/home/lestat/vendor/optix-dev", text)
        self.assertIn("/tmp/rtdl_v2_partner_pydeps", text)
        self.assertIn("make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev", text)
        self.assertIn("cupy-cuda12x", text)
        self.assertIn("does not replace RTX-class pod", text)
        self.assertIn("v2.0 release readiness", text)


if __name__ == "__main__":
    unittest.main()
