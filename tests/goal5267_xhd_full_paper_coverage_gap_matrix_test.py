from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
MATRIX = APP_DIR / "results" / "xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json"


class Goal5267XhdFullPaperCoverageGapMatrixTest(unittest.TestCase):
    def _matrix(self) -> dict[str, object]:
        if not MATRIX.exists():
            self.skipTest(f"missing coverage matrix: {MATRIX}")
        return json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_matrix_keeps_full_paper_incomplete_boundary(self) -> None:
        payload = self._matrix()

        self.assertEqual(payload["schema"], "rtdl.paper_reproduction.xhd.full_paper_coverage_gap_matrix.v1")
        self.assertEqual(payload["status"], "full_paper_reproduction_gap_matrix_ready__full_paper_incomplete")
        does_not_claim = set(payload["scope"]["does_not_claim"])
        self.assertIn("full X-HD paper reproduction", does_not_claim)
        self.assertIn("exact paper byte-input identity", does_not_claim)
        self.assertIn("author RT-core algorithm equivalence", does_not_claim)
        self.assertIn("author performance parity", does_not_claim)

    def test_current_entrypoint_evidence_lists_modelnet40_and_four_graphics_gates(self) -> None:
        payload = self._matrix()
        workloads = {item["name"]: item for item in payload["current_entrypoint_evidence"]["covered_workloads"]}

        self.assertIn("ModelNet40 all-400 paper-log pair identities", workloads)
        self.assertIn("Dragon -> HappyBuddha", workloads)
        self.assertIn("Dragon -> AsianDragon scaled 1e-3", workloads)
        self.assertIn("ThaiStatuette scaled 1e-3 -> HappyBuddha", workloads)
        self.assertIn("ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3", workloads)
        self.assertTrue(workloads["ThaiStatuette scaled 1e-3 -> AsianDragon scaled 1e-3"]["per_source_witness_exact"])

    def test_figures_are_not_marked_reproduced_and_figure6_is_next_target(self) -> None:
        payload = self._matrix()
        figures = {item["figure"]: item for item in payload["figure_status"]}

        self.assertEqual(set(figures), {"Figure 5", "Figure 6", "Figure 7", "Figure 8", "Figure 9", "Figure 10", "Figure 11"})
        for item in figures.values():
            self.assertIn("not_reproduced", item["status"])

        figure6 = figures["Figure 6"]
        self.assertIn("best_next_algorithmic_figure_target", figure6["status"])
        self.assertIn("No-Opt / EB / EB+Prune / RT-HDIST phase mapping", figure6["missing_for_reproduction"])
        self.assertIn("intersection counts and visited point-pair counts", figure6["missing_for_reproduction"])

        next_goal = payload["recommended_next_goal"]
        self.assertEqual(next_goal["id"], "Goal5268")
        self.assertIn("pruning-effectiveness", next_goal["title"])
        self.assertIn("phase/counter mapping", next_goal["reason"])

    def test_dataset_targets_keep_exact_input_provenance_as_blocker(self) -> None:
        payload = self._matrix()
        targets = {item["dataset"]: item for item in payload["dataset_target_status"]}

        self.assertIn("BraTS", targets)
        self.assertIn("Geospatial families", targets)
        self.assertIn("Stanford Graphics", targets)
        self.assertIn("ModelNet40", targets)
        self.assertIn("exact", targets["Stanford Graphics"]["blocking_gap"])
        self.assertIn("not proven exact", targets["ModelNet40"]["blocking_gap"])


if __name__ == "__main__":
    unittest.main()
