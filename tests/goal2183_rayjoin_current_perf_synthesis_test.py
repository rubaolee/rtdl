from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2183_rayjoin_current_perf_synthesis_2026-05-16.md"


class Goal2183RayjoinCurrentPerfSynthesisTest(unittest.TestCase):
    def test_report_summarizes_current_rayjoin_rows(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("pip_county512", text)
        self.assertIn("lsi_county256_soil256_count512", text)
        self.assertIn("overlay_county256_soil256", text)
        self.assertIn("overlay_county384_soil384", text)
        self.assertIn("overlay_county512_soil512", text)
        self.assertIn("62.472x", text)
        self.assertIn("12.653x", text)
        self.assertIn("3.688x", text)

    def test_report_explains_mixed_perf_shape(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RTDL/OptiX wins when traversal rejects lots of work", text)
        self.assertIn("Overlay improves with scale", text)
        self.assertIn("PIP is not automatically an RT win", text)
        self.assertIn("Prepared state is workload-shaped", text)

    def test_report_keeps_claim_boundary_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("does not authorize", text)
        self.assertIn("full RayJoin paper reproduction", text)
        self.assertIn("broad RT-core speedup claims", text)
        self.assertIn("v2.0 release authorization", text)
        self.assertIn("whole-app RayJoin speedup claims", text)
        self.assertIn("spatial-indexed baselines", text)
        self.assertIn("claims that OptiX wins every RayJoin subproblem", text)


if __name__ == "__main__":
    unittest.main()
