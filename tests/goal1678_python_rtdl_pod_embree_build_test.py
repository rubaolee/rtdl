from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1678_python_rtdl_pod_embree_build_2026-05-10.md"
POD_REPORT = ROOT / "docs" / "reports" / "goal1677_partner_pod_smoke_2026-05-10.md"
ROADMAP_GATE = ROOT / "docs" / "release_reports" / "v1_8_v2_0_python_partner_rtdl_gate.md"


class Goal1678PythonRtdlPodEmbreeBuildTest(unittest.TestCase):
    def test_report_records_embree_build_and_load_smoke(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "apt-get install -y libembree-dev libgeos-dev",
            "make build-embree",
            "Embree 3.12.2",
            "Embree backend build\nand load smoke passes",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_keeps_remaining_release_and_optix_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "not a complete v1.8 release authorization",
            "native app-agnostic gate still fails",
            "/opt/optix/include/optix.h",
            "missing item for\nthe OptiX build target is the SDK header package",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_and_roadmap_reports_link_embree_build(self) -> None:
        pod_text = POD_REPORT.read_text(encoding="utf-8")
        gate_text = ROADMAP_GATE.read_text(encoding="utf-8")
        self.assertIn("goal1678_python_rtdl_pod_embree_build_2026-05-10.md", pod_text)
        self.assertIn("goal1678_python_rtdl_pod_embree_build_2026-05-10.md", gate_text)


if __name__ == "__main__":
    unittest.main()
