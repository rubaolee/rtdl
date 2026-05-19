from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"


class Goal2403RtDbscanRepeatProbeTest(unittest.TestCase):
    def test_repeat_probe_records_warm_and_steady_state_fields(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("partner_cupy_grid_components_3d", text)
        self.assertIn("optix_core_flags_cupy_grid_components_3d", text)
        self.assertIn("outer_elapsed_sec", text)
        self.assertIn("app_elapsed_sec", text)
        self.assertIn("steady_state_probe_only", text)
        self.assertIn("signatures_match", text)


if __name__ == "__main__":
    unittest.main()
