from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class Goal525V08ProximityPerfDocRefreshTest(unittest.TestCase):
    def test_public_docs_reference_goal524_without_external_speedup_claim(self) -> None:
        paths = [
            "README.md",
            "docs/README.md",
            "docs/release_facing_examples.md",
            "docs/rtdl_feature_guide.md",
            "docs/tutorials/v0_8_app_building.md",
            "docs/current_architecture.md",
        ]

        for rel_path in paths:
            with self.subTest(path=rel_path):
                text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
                self.assertIn("Goal524", text)

        combined = "\n".join(
            (REPO_ROOT / rel_path).read_text(encoding="utf-8") for rel_path in paths
        )
        self.assertIn("ANN candidate", combined)
        self.assertIn("outlier", combined)
        self.assertIn("DBSCAN", combined)
        self.assertIn("SciPy was not installed", combined)
        self.assertIn("not an external-baseline speedup claim", combined)
        self.assertNotIn("do not yet have Linux performance closure", combined)

    def test_goal524_report_and_raw_json_are_linked_and_bounded(self) -> None:
        report = (
            REPO_ROOT
            / "docs"
            / "reports"
            / "goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md"
        ).read_text(encoding="utf-8")
        raw_json = (
            REPO_ROOT
            / "docs"
            / "reports"
            / "goal524_linux_stage1_proximity_perf_2026-04-17.json"
        ).read_text(encoding="utf-8")

        self.assertIn("passed\": 15", raw_json)
        self.assertIn("skipped\": 3", raw_json)
        self.assertIn("ModuleNotFoundError: No module named 'scipy'", raw_json)
        self.assertIn("This is a characterization gate, not a speedup claim.", report)
        self.assertIn("no external-baseline\nspeedup claim yet", report)


if __name__ == "__main__":
    unittest.main()
