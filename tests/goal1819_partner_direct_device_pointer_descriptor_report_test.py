from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1819_partner_direct_device_pointer_descriptor_2026-05-13.md"
GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"


class Goal1819PartnerDirectDevicePointerDescriptorReportTest(unittest.TestCase):
    def test_report_keeps_direct_handoff_and_zero_copy_claims_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Status: `accept-with-boundary`", text)
        self.assertIn("descriptor-only API", text)
        self.assertIn('transfer_mode = "device_descriptor_only"', text)
        self.assertIn("direct_device_handoff_authorized = False", text)
        self.assertIn("true_zero_copy_authorized = False", text)
        self.assertIn("does not satisfy the strict v2.0 blocker yet", text)

    def test_release_gate_links_goal1819_but_still_blocks_v2_0(self) -> None:
        text = GATE.read_text(encoding="utf-8")
        self.assertIn("Goal1819 Partner Direct Device-Pointer Descriptor", text)
        self.assertIn("descriptor-only CUDA", text)
        self.assertIn("does not satisfy the blocker yet", text)
        self.assertIn("v2.0 remains `needs-more-evidence`", text)


if __name__ == "__main__":
    unittest.main()
