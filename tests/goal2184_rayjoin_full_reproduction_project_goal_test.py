from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2184_rayjoin_full_reproduction_project_goal_2026-05-17.md"


class Goal2184RayjoinFullReproductionProjectGoalTest(unittest.TestCase):
    def test_report_defines_serious_reproduction_lane(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2184 RayJoin Full Reproduction Project Goal", text)
        self.assertIn("https://github.com/rubaolee/RayJoin", text)
        self.assertIn("query_exec", text)
        self.assertIn("polyover_exec", text)
        self.assertIn("grid", text)
        self.assertIn("lbvh", text)
        self.assertIn("rt", text)
        self.assertIn("3.0x", text)
        self.assertIn("28.3x", text)

    def test_report_preserves_app_agnostic_engine_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("The RTDL native engine remains app-agnostic", text)
        self.assertIn("no app-customized native engine code", text)
        self.assertIn("Not allowed", text)
        self.assertIn("native symbols named after RayJoin", text)
        self.assertIn("hidden RayJoin-only native code paths", text)

    def test_report_requires_protocol_baselines_and_consensus(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Paper Protocol Reconstruction", text)
        self.assertIn("Dataset Reproduction", text)
        self.assertIn("Fair Baselines", text)
        self.assertIn("RayJoin `grid`", text)
        self.assertIn("RayJoin `lbvh`", text)
        self.assertIn("RayJoin `rt`", text)
        self.assertIn("Final public claims require 3-AI consensus", text)

    def test_report_blocks_premature_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("This goal does not authorize", text)
        self.assertIn("claiming RTDL reproduces RayJoin results", text)
        self.assertIn("claiming RTDL beats RayJoin", text)
        self.assertIn("claiming broad RT-core speedup", text)
        self.assertIn("claiming v2.0 release readiness", text)
        self.assertIn("adding app-specific native engine code", text)


if __name__ == "__main__":
    unittest.main()
