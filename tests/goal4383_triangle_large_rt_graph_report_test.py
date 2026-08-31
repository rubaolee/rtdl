from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4383_triangle_large_rt_graph_2026-06-14.md"


class Goal4383TriangleLargeRtGraphReportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.report = REPORT.read_text(encoding="utf-8")

    def test_report_records_large_same_contract_rows(self) -> None:
        self.assertIn("1,048,576 ray probes", self.report)
        self.assertIn("2,621,440 triangle primitives", self.report)
        self.assertIn("PREPARED_TRIANGLE_SCENE_3D_RAY_ANY_HIT_WEIGHTED_SUM_V1", self.report)
        self.assertIn("Counts match", self.report)

    def test_report_keeps_public_claim_narrow(self) -> None:
        self.assertIn("not a full paper-dataset speedup claim", self.report)
        self.assertIn("The whole triangle-counting application is 108x faster", self.report)
        self.assertIn("large RT-Graph-shaped prepared primitive row", self.report)


if __name__ == "__main__":
    unittest.main()
