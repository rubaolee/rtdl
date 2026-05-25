from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "docs" / "release_reports" / "v2_3" / "README.md"
CATALOG = ROOT / "docs" / "application_catalog.md"


class Goal2613V23AppPortfolioReleaseTest(unittest.TestCase):
    def test_version_and_front_door_docs_name_v2_3(self) -> None:
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "v2.3")
        for rel in ("README.md", "docs/README.md", "docs/current_architecture.md"):
            with self.subTest(rel=rel):
                text = (ROOT / rel).read_text(encoding="utf-8")
                self.assertIn("current released version is `v2.3`", text)
                self.assertIn("source-tree", text)
                self.assertIn("Python+partner+RTDL", text)

    def test_release_package_has_two_app_tables(self) -> None:
        text = RELEASE.read_text(encoding="utf-8")
        self.assertIn("## Promoted Benchmark Apps", text)
        self.assertIn("## Learner And Example Apps", text)
        for name in (
            "Hausdorff / X-HD-style",
            "Spatial RayJoin-style",
            "RT-DBSCAN-style",
            "Robot collision",
            "RayDB-style grouped aggregate",
            "Barnes-Hut / RT-BarnesHut-style",
            "LibRTS-style spatial index",
            "RTNN neighbor search",
            "Triangle counting",
        ):
            with self.subTest(name=name):
                self.assertIn(name, text)
        for name in (
            "Getting started",
            "Ray query features",
            "Neighbor features",
            "Database feature recipes",
            "Graph feature recipes",
            "Spatial feature recipes",
            "Partner continuation examples",
            "Geospatial apps",
            "ML apps",
            "Analytics apps",
            "Trajectory app",
            "GPU-RMQ learner app",
            "Visual demos",
        ):
            with self.subTest(name=name):
                self.assertIn(name, text)

    def test_catalog_demotes_gpu_rmq_and_continuous_frechet(self) -> None:
        text = CATALOG.read_text(encoding="utf-8")
        self.assertIn("## v2.3 Portfolio Snapshot", text)
        self.assertIn("Goal2612 rejects benchmark promotion", text)
        self.assertIn("Explicitly demoted learner/design-pressure app after Goal2612", text)
        self.assertIn("Explicitly demoted learner/demo app", text)
        old_gpu_rmq_path = "/".join(("examples", "v2_0", "research_benchmarks", "gpu_rmq"))
        self.assertNotIn(old_gpu_rmq_path, text)

    def test_release_blocks_overclaims(self) -> None:
        text = RELEASE.read_text(encoding="utf-8")
        for phrase in (
            "not a package-install release",
            "No universal speedup claim",
            "No whole-application speedup claim",
            "No GPU-RMQ benchmark promotion",
            "No Continuous Frechet benchmark promotion",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
