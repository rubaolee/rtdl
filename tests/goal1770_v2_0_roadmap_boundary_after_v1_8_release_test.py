import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1770_v2_0_roadmap_boundary_after_v1_8_release_2026-05-12.md"


class Goal1770V20RoadmapBoundaryAfterV18ReleaseTest(unittest.TestCase):
    def test_report_separates_v2_partner_from_v3_extensions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v2_0_partner_track_active_v3_0_extensions_parked", text)
        self.assertIn("v2.0 is not custom shader injection", text)
        self.assertIn("Host/tensor interop", text)
        self.assertIn("device/shader injection", text)
        self.assertIn("Python-to-shader JIT", text)

    def test_report_keeps_partner_consensus_and_engine_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Protocol first. PyTorch reference first. CuPy conformance alongside it.", text)
        self.assertIn("Engine absolutely app-agnostic throughout.", text)
        self.assertIn("must not link directly against PyTorch, CuPy", text)

    def test_report_lists_concrete_v2_path(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "PyTorch the reference adapter",
            "CuPy the conformance adapter",
            "NumPy/Embree host descriptor acceptance",
            "one narrow OptiX primitive path",
            "phase-timing artifacts",
            "hardware/pod validation",
            "distinct-AI review",
        ):
            self.assertIn(phrase, text)

    def test_report_blocks_v3_claims_from_v2(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "general true zero-copy support",
            "arbitrary PyTorch/CuPy program acceleration",
            "v3.0 custom shader extension support",
            "Python-to-PTX/SPIR-V/Metal JIT support",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
