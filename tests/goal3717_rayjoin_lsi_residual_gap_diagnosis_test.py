import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3717_rayjoin_lsi_residual_gap_diagnosis_2026-06-07.md"


class Goal3717RayJoinLsiResidualGapDiagnosisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = REPORT.read_text(encoding="utf-8")

    def test_report_tracks_current_lsi_correctness_and_gap(self):
        self.assertIn("RayJoin LSI: `20860`", self.text)
        self.assertIn("RTDL LSI: `20860`", self.text)
        self.assertIn("delta: `0`", self.text)
        self.assertIn("RTDL is therefore `0.794x` RayJoin speed", self.text)
        self.assertIn("about `1.26x` the latency", self.text)

    def test_phase_split_math_is_recorded(self):
        self.assertIn("hot query median | `0.001100961`", self.text)
        self.assertIn("native `candidate_count_pass` | `0.000942941`", self.text)
        self.assertIn("Python/ctypes/timing residual | about `0.000158020`", self.text)
        self.assertIn("`0.001100961 - 0.000942941 = 0.000158020`", self.text)
        self.assertIn("`0.001100961 - 0.000873963 = 0.000226998`", self.text)

    def test_next_step_is_native_repeated_executor_not_telemetry_toggle(self):
        self.assertIn("Native Repeated LSI Count Executor", self.text)
        self.assertIn("generic prepared segment-pair exact-count repeated executor", self.text)
        self.assertIn("Do not spend more time on optional candidate telemetry", self.text)
        self.assertIn("Immediate Next Goal", self.text)

    def test_boundary_and_app_agnostic_constraints_are_explicit(self):
        self.assertIn("not a public speedup claim", self.text)
        self.assertIn("not an RTDL-beats-RayJoin claim", self.text)
        self.assertIn("not a RayJoin paper reproduction claim", self.text)
        self.assertIn("Do not add RayJoin-specific native ABI names", self.text)
        self.assertIn("app-agnostic", self.text)


if __name__ == "__main__":
    unittest.main()
