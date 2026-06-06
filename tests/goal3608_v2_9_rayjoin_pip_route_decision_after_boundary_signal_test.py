from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3608_v2_9_rayjoin_pip_route_decision_after_boundary_signal_2026-06-06.md"
GOAL3604 = ROOT / "docs" / "reports" / "goal3604_rayjoin_pip_boundary_event_signal_timing_2026-06-06.md"
GOAL3606 = ROOT / "docs" / "reports" / "goal3606_rayjoin_pip_boundary_signal_4096_negative_2026-06-06.md"


class Goal3608V29RayJoinPipRouteDecisionAfterBoundarySignalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.goal3604 = GOAL3604.read_text(encoding="utf-8")
        cls.goal3606 = GOAL3606.read_text(encoding="utf-8")

    def test_decision_recommends_mixed_route_not_forced_rt(self):
        self.assertIn("CuPy dense CUDA-core scalar count", self.report)
        self.assertIn("Prepared OptiX exact count", self.report)
        self.assertIn("Do not promote the boundary-event signal route", self.report)
        self.assertIn("PIP scalar count: CuPy dense", self.report)
        self.assertIn("LSI count: RTDL/OptiX", self.report)
        self.assertIn("Overlay active-count: RTDL/OptiX", self.report)

    def test_report_carries_goal3604_and_goal3606_evidence(self):
        self.assertIn("0.012200347", self.report)
        self.assertIn("0.023x", self.report)
        self.assertIn("11316 | 11314", self.report)
        self.assertIn("Goal3604", self.goal3604)
        self.assertIn("Goal3606", self.goal3606)

    def test_design_boundary_stays_app_agnostic(self):
        self.assertIn("fused generic exact closed-shape membership/count", self.report)
        self.assertIn("must stay app-agnostic", self.report)
        self.assertIn("not allowed in the engine ABI", self.report)
        self.assertIn("RayJoin, CDB, county, GIS assignment semantics", self.report)

    def test_single_rayjoin_number_requires_workload_mix(self):
        self.assertIn("a single RayJoin number must define a workload mix/weighting first", self.report)
        self.assertIn("not a release packet", self.report)
        self.assertIn("not a public claim packet", self.report)


if __name__ == "__main__":
    unittest.main()
