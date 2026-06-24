import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TUTORIAL_ROOT = REPO_ROOT / "tutorials" / "current"


class V3RebuildTutorialSurfaceTest(unittest.TestCase):
    def test_short_tutorial_ladder_exists(self) -> None:
        expected = [
            "01_first_run.md",
            "02_hello_world.md",
            "03_backend_choice.md",
            "04_prepared_runtime.md",
            "05_measurement_boundaries.md",
            "README.md",
        ]
        actual = sorted(path.name for path in TUTORIAL_ROOT.glob("*.md"))
        self.assertEqual(expected, actual)

    def test_tutorials_are_current_v3_not_archive_tours(self) -> None:
        for path in TUTORIAL_ROOT.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("V3", text, path.name)
            self.assertNotIn("docs/rebuild", text, path.name)
            self.assertNotIn("docs/reviews", text, path.name)
            self.assertNotIn("C ABI", text, path.name)

    def test_tutorial_readme_is_short_user_path(self) -> None:
        text = (TUTORIAL_ROOT / "README.md").read_text(encoding="utf-8")
        compact = " ".join(text.split())
        for lesson in (
            "[First Run](01_first_run.md)",
            "[Hello World](02_hello_world.md)",
            "[Backend Choice](03_backend_choice.md)",
            "[Prepared Runtime](04_prepared_runtime.md)",
            "[Measurement Boundaries](05_measurement_boundaries.md)",
        ):
            self.assertIn(lesson, text)
        self.assertIn("teach the current RTDL V3.0.0 contract directly", compact)

    def test_first_run_wires_source_tree_doctor(self) -> None:
        text = (TUTORIAL_ROOT / "01_first_run.md").read_text(encoding="utf-8")
        self.assertIn("scripts\\rtdl_source_tree_doctor.py --run-smoke", text)
        self.assertIn("checkout sanity check", text)

    def test_hello_world_tutorial_has_command_and_expected_output(self) -> None:
        text = (TUTORIAL_ROOT / "02_hello_world.md").read_text(encoding="utf-8")
        self.assertIn("examples\\current\\getting_started\\rtdl_hello_world.py", text)
        self.assertIn("hello, world", text)

    def test_measurement_boundaries_reject_broad_claims(self) -> None:
        text = (TUTORIAL_ROOT / "05_measurement_boundaries.md").read_text(encoding="utf-8")
        self.assertIn("RTDL V3 performance text should be specific", text)
        self.assertIn("the exact command or row", text)
        self.assertIn("Avoid broad statements", text)


if __name__ == "__main__":
    unittest.main()
