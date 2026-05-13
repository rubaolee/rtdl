from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1821_optix_partner_device_descriptor_fail_closed_2026-05-13.md"
GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"


class Goal1821OptixPartnerDeviceDescriptorReportTest(unittest.TestCase):
    def test_report_documents_fail_closed_no_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Status: `accept-with-boundary`", text)
        self.assertIn("fails closed unless a future native OptiX device-column ABI exists", text)
        self.assertIn('transfer_mode = "device_descriptor_only"', text)
        self.assertIn("direct_device_handoff_authorized = False", text)
        self.assertIn("true_zero_copy_authorized = False", text)
        self.assertIn("does not silently fall", text)
        self.assertIn("still does not satisfy the v2.0 direct device-pointer blocker", text)

    def test_release_gate_links_goal1821_as_incomplete_progress(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        self.assertIn("Goal1821 OptiX Partner Device-Descriptor Fail-Closed Path", text)
        self.assertIn("fail-closed", text)
        self.assertIn("native OptiX", text)
        self.assertIn("device-column ABI is not implemented", text)
        self.assertIn("v2.0 remains `needs-more-evidence`", text)


if __name__ == "__main__":
    unittest.main()
