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
        self.assertIn("Gemini review accepted Goal1903", text)
        self.assertIn("post-pod acceptance validator", text)
        self.assertIn("public v2 claim-boundary scanner", text)
        self.assertIn("source-tree policy with boundary", text)
        self.assertIn("one-command local non-pod preflight", text)
        self.assertIn("goal1903_fixed_radius_batch_pod.json", text)
        self.assertIn("goal1903_segment_polygon_batch_pod_512.json", text)
        self.assertIn("goal1903_segment_polygon_batch_pod_2048.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_512.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_2048.json", text)
        self.assertIn("goal1903_v2_partner_pod_batch_summary.json", text)
        self.assertIn("scripts/goal1905_v2_partner_pod_batch_acceptance.py", text)
        self.assertIn("scripts/goal1906_public_v2_claim_boundary_scan.py", text)
        self.assertIn("scripts/goal1908_v2_local_preflight.py", text)
        self.assertIn("Goal1898", text)
        self.assertIn("Goal1900", text)
        self.assertIn("Source doc written and linked", text)
        self.assertIn("v2.0 is still not born", text)
        self.assertIn("external review of the Goal1900 partner-acceleration boundary document", text)
        self.assertIn("Claude or Pro-class review", text)


if __name__ == "__main__":
    unittest.main()
