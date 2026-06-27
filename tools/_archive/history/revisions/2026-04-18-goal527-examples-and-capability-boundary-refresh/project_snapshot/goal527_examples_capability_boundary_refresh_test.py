from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal527ExamplesCapabilityBoundaryRefreshTest(unittest.TestCase):
    def test_examples_readme_carries_goal524_boundary_for_stage1_apps(self) -> None:
        text = (REPO_ROOT / "examples" / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "Goal524 records bounded Linux CPU/oracle, Embree, OptiX, and Vulkan",
            text,
        )
        self.assertIn("not an external ANN-baseline speedup\n  claim", text)
        self.assertIn("not a claim against SciPy, scikit-learn", text)
        self.assertIn("not a claim against scikit-learn DBSCAN", text)

    def test_capability_boundaries_distinguish_candidate_ann_from_full_ann(self) -> None:
        text = (REPO_ROOT / "docs" / "capability_boundaries.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("candidate-subset reranking, not a full ANN index", text)
        self.assertIn("Hausdorff distance, ANN\ncandidate search", text)
        self.assertIn("outlier detection, DBSCAN clustering", text)
        self.assertIn("Goal507, Goal509, and Goal524", text)
        self.assertIn(
            "not\nFAISS, HNSW, IVF, PQ, or learned/vector-index support",
            text,
        )


if __name__ == "__main__":
    unittest.main()
