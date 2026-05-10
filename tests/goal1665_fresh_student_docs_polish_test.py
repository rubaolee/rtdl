from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Goal1665FreshStudentDocsPolishTest(unittest.TestCase):
    def test_secondary_beginner_entries_are_productized(self) -> None:
        for path in (
            ROOT / "docs" / "app_example_quickstart.md",
            ROOT / "examples" / "README.md",
        ):
            text = _text(path)
            for forbidden in (
                "v1.0-era",
                "proof machinery",
                "architecture milestone",
                "Current release: `v1.6`",
                "v0.8 app example boundary",
                "Goal748",
            ):
                with self.subTest(path=path, forbidden=forbidden):
                    self.assertNotIn(forbidden, text)
            self.assertIn("PYTHONPATH=src:.", text)
            self.assertIn("cpu_python_reference", text)
            self.assertIn("History Index", text)

    def test_release_facing_examples_is_labeled_as_archive(self) -> None:
        text = _text(ROOT / "docs" / "release_facing_examples.md")
        self.assertIn("# Release-Facing Example Command Archive", text)
        self.assertIn("command and evidence archive", text)
        self.assertIn("If you are learning RTDL for the first time", text)
        self.assertIn("[Quick Tutorial](quick_tutorial.md)", text)

    def test_backend_and_reduction_guidance_is_visible(self) -> None:
        quick = _text(ROOT / "docs" / "quick_tutorial.md")
        guide = _text(ROOT / "docs" / "rtdl" / "programming_guide.md")
        reference = _text(ROOT / "docs" / "rtdl" / "dsl_reference.md")
        joined = " ".join("\n".join((quick, guide, reference)).split())

        for phrase in (
            "Backend Names In Two Places",
            "kernel is authored for the RTDL language",
            "runtime execution engine",
            "portable learning backend",
            "Runtime Backend Selection Is Separate",
            "New code should use `backend=\"rtdl\"`",
            "`rt.reduce_rows(...)` is a deterministic helper",
            "not a blanket native-backend reduction speedup claim",
            "Common First-Run Problems",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, joined)


if __name__ == "__main__":
    unittest.main()
