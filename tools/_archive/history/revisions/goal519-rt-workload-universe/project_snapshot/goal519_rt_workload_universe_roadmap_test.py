from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal519RtWorkloadUniverseRoadmapTest(unittest.TestCase):
    def test_roadmap_covers_paper_workload_families_and_boundaries(self) -> None:
        text = (
            REPO_ROOT
            / "docs"
            / "reports"
            / "goal519_rt_workload_universe_from_2603_28771_2026-04-17.md"
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
            "Discrete Collision Detection",
            "Continuous Collision Detection",
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

        self.assertIn("Hardware modification papers", text)
        self.assertIn("Full systems", text)
        self.assertIn("Arbitrary high-dimensional exact geometry", text)
        self.assertIn("Per-Workload Lifecycle Template", text)
        self.assertIn("ANN / outlier detection / DBSCAN", text)
        self.assertIn("many short rays over a few long rays", text)
        self.assertIn("Set Intersection / SpMM performance risk", text)


if __name__ == "__main__":
    unittest.main()
