import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1765_github_learner_readiness_double_check_2026-05-12.md"


class Goal1765GithubLearnerReadinessDoubleCheckTest(unittest.TestCase):
    def _read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def _run_example(self, *args: str) -> str:
        completed = subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": "src:."},
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout

    def test_learner_path_files_exist_and_are_linked_from_front_doors(self) -> None:
        for rel in (
            "README.md",
            "docs/README.md",
            "docs/quick_tutorial.md",
            "examples/README.md",
            "docs/app_example_quickstart.md",
            "docs/current_architecture.md",
            "docs/performance_model.md",
        ):
            self.assertTrue((ROOT / rel).exists(), rel)

        readme = self._read("README.md")
        docs_index = self._read("docs/README.md")
        examples_index = self._read("examples/README.md")
        self.assertIn("[Quick Tutorial](docs/quick_tutorial.md)", readme)
        self.assertIn("[App And Example Quickstart](docs/app_example_quickstart.md)", readme)
        self.assertIn("[Quick Tutorial](quick_tutorial.md)", docs_index)
        self.assertIn("[App And Example Quickstart](../docs/app_example_quickstart.md)", examples_index)

    def test_portable_first_commands_run(self) -> None:
        self.assertEqual(self._run_example("examples/rtdl_hello_world.py").strip(), "hello, world")

        backends = json.loads(
            self._run_example(
                "examples/rtdl_hello_world_backends.py",
                "--backend",
                "cpu_python_reference",
            )
        )
        self.assertEqual(backends["backend"], "cpu_python_reference")
        self.assertEqual(backends["visible_hit_label"], "hello, world")

        cookbook = json.loads(self._run_example("examples/rtdl_feature_quickstart_cookbook.py"))
        self.assertEqual(cookbook["app"], "feature_quickstart_cookbook")
        self.assertGreaterEqual(cookbook["feature_count"], 19)

    def test_design_message_is_visible_without_history_reports(self) -> None:
        joined = "\n".join(
            (
                self._read("README.md"),
                self._read("docs/README.md"),
                self._read("docs/quick_tutorial.md"),
                self._read("examples/README.md"),
                self._read("docs/app_example_quickstart.md"),
            )
        )
        self.assertIn("Python writes the application", joined)
        self.assertIn("RTDL expresses the RT-shaped kernel", joined)
        self.assertIn("Native backends execute generic engine contracts", joined)
        self.assertIn("input -> traverse -> refine -> emit", joined)
        self.assertIn("--backend optix", joined)
        self.assertIn("not automatically", joined)

    def test_report_records_double_check_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("github_learner_path_ready_for_v1_8_source_tree_release", text)
        self.assertIn("No `pip install -e .` or package-install claim is made", text)
        self.assertIn("explicit user release authorization", text)
        self.assertIn("zero-copy", text)


if __name__ == "__main__":
    unittest.main()
