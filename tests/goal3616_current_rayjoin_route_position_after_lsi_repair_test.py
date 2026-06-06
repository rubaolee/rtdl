from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3616_current_rayjoin_route_position_after_lsi_repair_2026-06-06.md"


class Goal3616CurrentRayJoinRoutePositionAfterLsiRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_current_route_recommends_repaired_lsi_fast_path(self):
        self.assertIn("PIP scalar count | CuPy dense CUDA-core count", self.report)
        self.assertIn("LSI count | RTDL/OptiX left-id dense count with strict segment predicate", self.report)
        self.assertIn("Overlay active-count | RTDL/OptiX prepared shape-pair active count", self.report)
        self.assertIn("2032.908x LSI speedup", self.report)
        self.assertIn("188.997x", self.report)

    def test_report_explains_superseded_blocker_and_remaining_risk(self):
        self.assertIn("Goal3613 then repaired the fast dense-count route itself", self.report)
        self.assertIn("broader public claims still need", self.report)
        self.assertIn("not a release packet", self.report)
        self.assertIn("not a public claim packet", self.report)


if __name__ == "__main__":
    unittest.main()
