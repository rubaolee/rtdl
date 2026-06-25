from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "future" / "v4" / "v4_goal4626_section8_release_scorecard_protocol_2026-06-24.md"


class V4Goal4626Section8ScorecardProtocolTest(unittest.TestCase):
    def test_protocol_reconciles_fixed_radius_chain_without_release_claims(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")

        self.assertIn("goal4626_protocol_current_not_release", text)
        self.assertIn("Original whole-call Section 8 route", text)
        self.assertIn("strict gate failed", text)
        self.assertIn("Prepared hot-path revision", text)
        self.assertIn("1.655x, 1.772x, 1.970x", text)
        self.assertIn("Route D hand-written OptiX ceiling", text)
        self.assertIn("192x-1140x", text)
        self.assertIn("Torch device-array front door", text)
        self.assertIn("1022.93x, 3841.66x, and 9699.17x", text)
        self.assertIn("claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md", text)
        self.assertIn("external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive", text)
        self.assertIn("pass_bounded_one_primitive", text)
        self.assertIn("not release-complete", text)

    def test_protocol_freezes_next_scorecard_gates(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")

        for gate in ("G1", "G2", "G3", "G4", "G5", "G6", "G7"):
            self.assertIn(f"{gate}:", text)
        self.assertIn("goal4627", text)
        self.assertIn("goal4628", text)
        self.assertIn("goal4629", text)
        self.assertIn("goal4630", text)
        self.assertIn("goal4631", text)
        self.assertIn("goal4632", text)
        self.assertIn("gated by the fixed-radius wrapper productization prerequisite", text)
        self.assertIn("do not keep adding primitives merely to avoid the negative result", text)

    def test_protocol_preserves_non_authorization_boundary(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")

        for forbidden in (
            "V4 release",
            "V4 release-candidate status",
            "public broad speedup wording",
            "whole-application speedup wording",
            "public true-zero-copy wording",
            "Tier-3 callback support",
            "raw OptiX callback support",
            "CuPy performance claims",
            "C ABI / embedding / non-Python-host work",
            "app-specific native kernels",
        ):
            self.assertIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
