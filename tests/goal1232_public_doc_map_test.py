from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1232PublicDocMapTest(unittest.TestCase):
    def test_public_doc_map_covers_current_user_priorities(self) -> None:
        text = (ROOT / "docs" / "public_documentation_map.md").read_text(encoding="utf-8")

        for phrase in (
            "What RTDL is",
            "First program",
            "Workload recipes",
            "Apps and examples",
            "Architecture",
            "Programming model",
            "IR and lowering",
            "Performance",
            "History or audits",
            "Current User Message",
            "History Boundary",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_public_doc_map_keeps_history_out_of_user_path(self) -> None:
        text = (ROOT / "docs" / "public_documentation_map.md").read_text(encoding="utf-8")
        compact = " ".join(text.split())

        self.assertIn("They should explain RTDL as it is now", compact)
        self.assertIn("[History Index](history/README.md)", text)
        for phrase in (
            "v1.0 remains the foundation proof line",
            "v1.7-v2.0 are the Python+partner+RTDL track",
            "v1.5 remains the standalone",
            "goal archive",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_entry_points_link_current_docs_and_history_index(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        language_index = (ROOT / "docs" / "rtdl" / "README.md").read_text(encoding="utf-8")

        for phrase in (
            "[Public Documentation Map](docs/public_documentation_map.md)",
            "[App And Example Quickstart](docs/app_example_quickstart.md)",
            "[Performance Model](docs/performance_model.md)",
            "[IR And Lowering](docs/rtdl/ir_and_lowering.md)",
            "[History Index](docs/history/README.md)",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, readme)
        for phrase in (
            "[Public Documentation Map](public_documentation_map.md)",
            "[App And Example Quickstart](app_example_quickstart.md)",
            "[Performance Model](performance_model.md)",
            "[IR And Lowering](rtdl/ir_and_lowering.md)",
            "[History Index](history/README.md)",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, docs_index)
        self.assertIn("[IR And Lowering](ir_and_lowering.md)", language_index)


if __name__ == "__main__":
    unittest.main()
