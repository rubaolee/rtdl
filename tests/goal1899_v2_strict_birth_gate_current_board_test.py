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
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_512.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_2048.json", text)
        self.assertIn("Goal1898", text)
        self.assertIn("v2.0 is still not born", text)
        self.assertIn("partner-acceleration boundary document", text)


if __name__ == "__main__":
    unittest.main()
