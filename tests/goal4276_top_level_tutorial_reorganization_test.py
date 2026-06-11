"""Goal4276: tutorials are a top-level teaching path, not docs subpages."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal4276TopLevelTutorialReorganizationTest(unittest.TestCase):
    def test_tutorials_are_top_level_and_docs_tutorials_is_gone(self) -> None:
        self.assertTrue((ROOT / "tutorials" / "README.md").is_file())
        self.assertTrue((ROOT / "tutorials" / "current" / "README.md").is_file())
        self.assertFalse((ROOT / "docs" / "tutorials").exists())

    def test_front_doors_explain_tutorial_doc_example_distinction(self) -> None:
        tutorial_index = (ROOT / "tutorials" / "README.md").read_text(encoding="utf-8")
        docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for token in (
            "Tutorials are for teaching",
            "`docs/` | Reference docs",
            "`examples/` | Runnable code",
        ):
            self.assertIn(token, tutorial_index)

        self.assertIn("[Tutorials](../tutorials/README.md)", docs_index)
        self.assertIn("[Tutorials](tutorials/README.md)", root_readme)
        self.assertIn("| `tutorials/` | Ordered teaching path", root_readme)

    def test_archived_loose_tutorials_are_not_current_front_door(self) -> None:
        archive = ROOT / "history" / "tutorial_archive"
        archived = {
            "README.md",
            "hello_world.md",
            "partner_anyhit.md",
            "partner_optix_column_anyhit.md",
            "nearest_neighbor_workloads.md",
            "segment_polygon_workloads.md",
            "db_workloads.md",
            "graph_workloads.md",
            "feature_quickstart_cookbook.md",
            "v2_app_building.md",
        }
        missing = [name for name in archived if not (archive / name).is_file()]
        self.assertEqual([], missing)

        archive_index = (archive / "README.md").read_text(encoding="utf-8")
        self.assertIn("not the current learner path", archive_index)
        self.assertIn("../../tutorials/current/README.md", archive_index)

    def test_report_records_file_by_file_operations(self) -> None:
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal4276_top_level_tutorial_reorganization_2026-06-10.md"
        ).read_text(encoding="utf-8")

        required = [
            "tutorials/current/08_spatial_join_rayjoin_reference.md",
            "history/tutorial_archive/*.md",
            "scripts/goal4248_current_public_docs_claim_boundary_scan.py",
            "tests/goal4274_current_doc_recheck_test.py",
            "documentation-structure cleanup",
        ]
        missing = [token for token in required if token not in report]
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
