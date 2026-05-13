from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1899_v2_strict_birth_gate_current_board_2026-05-13.md"


class Goal1899V2StrictBirthGateCurrentBoardTest(unittest.TestCase):
    def test_board_tracks_all_goal1814_blockers_and_next_actions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: active-blockers-pod-and-consensus-pending", text)
        for blocker in (
            "True zero-copy",
            "Direct device-pointer handoff",
            "Broad RT-core speedup",
            "Whole-application acceleration",
            "Arbitrary PyTorch/CuPy acceleration boundary",
            "Package-install support",
        ):
            self.assertIn(blocker, text)

        self.assertIn("Goal1897", text)
        self.assertIn("Goal1903", text)
        self.assertIn("Goal1904", text)
        self.assertIn("Goal1905", text)
        self.assertIn("Goal1906", text)
        self.assertIn("Goal1907", text)
        self.assertIn("Goal1908", text)
        self.assertIn("Goal1909", text)
        self.assertIn("Goal1910", text)
        self.assertIn("Goal1911", text)
        self.assertIn("Goal1912", text)
        self.assertIn("Goal1913", text)
        self.assertIn("Goal1940", text)
        self.assertIn("Goal1941", text)
        self.assertIn("segment any-hit rows now have", text)
        self.assertIn("robot has large exact-parity scaling", text)
        self.assertIn("11 positive rows, 1 positive-subsecond robot row, and 4 control rows", text)
        self.assertIn("Gemini review accepted Goal1903", text)
        self.assertIn("post-pod acceptance validator", text)
        self.assertIn("public v2 claim-boundary scanner", text)
        self.assertIn("source-tree policy with", text)
        self.assertIn("Source-tree-only v2.0 policy accepted", text)
        self.assertIn("one-command local non-pod preflight", text)
        self.assertIn("v2 release packet skeleton", text)
        self.assertIn("Gemini review accepted the Goal1909 skeleton", text)
        self.assertIn("machine-readable v2 readiness aggregator", text)
        self.assertIn("post-pod external review handoff template", text)
        self.assertIn("visible-progress pod session runbook", text)
        self.assertIn("Goal1945", text)
        self.assertIn("Goal1947", text)
        self.assertIn("source-tree-only policy now has 3-AI consensus", text)
        self.assertIn("scripts/goal1906_public_v2_claim_boundary_scan.py", text)
        self.assertIn("scripts/goal1908_v2_local_preflight.py", text)
        self.assertIn("scripts/goal1911_v2_readiness_aggregator.py", text)
        self.assertIn("Goal1898", text)
        self.assertIn("Goal1900", text)
        self.assertIn("Source doc written and linked", text)
        self.assertIn("v2.0 is still not born", text)
        self.assertIn("external review of the Goal1900 partner-acceleration boundary document", text)
        self.assertIn("final v2.0 release consensus", text)
        self.assertIn("explicit user release action", text)
        self.assertIn("Still not a broad claim", text)
        self.assertIn("Use row-by-row claims only", text)
        self.assertIn("Goal1946", text)
        self.assertIn("Goal1947", text)


if __name__ == "__main__":
    unittest.main()
