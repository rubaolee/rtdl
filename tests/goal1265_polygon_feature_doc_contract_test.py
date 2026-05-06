from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal1265PolygonFeatureDocContractTest(unittest.TestCase):
    def test_polygon_feature_examples_use_source_tree_commands(self) -> None:
        docs = (
            ROOT / "docs" / "features" / "polygon_pair_overlap_area_rows" / "README.md",
            ROOT / "docs" / "features" / "polygon_set_jaccard" / "README.md",
        )
        bare_command = re.compile(r"^python (examples|scripts)/", re.MULTILINE)

        for path in docs:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, bare_command)
                self.assertIn("PYTHONPATH=src:. python", text)

    def test_polygon_pair_feature_doc_names_goal1263_boundary(self) -> None:
        text = (
            ROOT / "docs" / "features" / "polygon_pair_overlap_area_rows" / "README.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Goal1263 bounded", text)
        self.assertIn("RT-assisted LSI/PIP positive candidate discovery", text)
        self.assertIn("backend-neutral exact area summary", text)
        self.assertIn("whole-app polygon speedup remains outside", text)

    def test_jaccard_feature_doc_keeps_positive_speedup_blocked(self) -> None:
        text = (ROOT / "docs" / "features" / "polygon_set_jaccard" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("backend-neutral set-area summary plumbing", text)
        self.assertIn("not a monolithic GPU Jaccard kernel or a public RTX speedup claim", text)


if __name__ == "__main__":
    unittest.main()
