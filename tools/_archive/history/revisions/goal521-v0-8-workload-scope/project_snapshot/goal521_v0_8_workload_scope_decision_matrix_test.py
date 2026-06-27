from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal521V08WorkloadScopeDecisionMatrixTest(unittest.TestCase):
    def test_scope_matrix_covers_all_goal519_workloads(self) -> None:
        text = (
            REPO_ROOT
            / "docs"
            / "reports"
            / "goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md"
        ).read_text(encoding="utf-8")

        for workload in (
            "Penetration Depth",
            "SpMM",
            "BFS",
            "Triangle Counting",
            "Set Intersection",
            "Binary Search",
            "Point Queries",
            "Range Queries",
            "Barnes-Hut",
            "Discrete CD",
            "Continuous CD",
            "RMQ",
            "Line-Segment Intersection",
            "Point in Polygon",
            "Non-euclidean kNN",
            "ANN",
            "Outlier Detection",
            "Index Scan",
            "kNN",
            "Particle Simulation",
            "Radio Wave Propagation",
            "DBSCAN",
            "Point Location",
            "FRNN",
            "Particle Tracking",
            "Graph Drawing",
            "Space Skipping",
            "Segmentation",
            "Particle-Mesh Coupling",
            "Infrared Radiation",
            "Particle Transport",
            "Voxelization",
        ):
            self.assertIn(workload, text)

    def test_scope_matrix_names_decision_classes_and_closure_list(self) -> None:
        text = (
            REPO_ROOT
            / "docs"
            / "reports"
            / "goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md"
        ).read_text(encoding="utf-8")

        for decision in ("do-now-v0.8", "already-covered", "defer-version", "out-of-scope-until-reframed"):
            self.assertIn(decision, text)

        for app in (
            "Hausdorff distance",
            "ANN candidate search",
            "outlier detection",
            "DBSCAN clustering",
            "robot collision screening",
            "Barnes-Hut force approximation",
        ):
            self.assertIn(app, text)

        self.assertIn("at least one Claude or Gemini review", text)
        self.assertIn("Codex must write a consensus note", text)


if __name__ == "__main__":
    unittest.main()
