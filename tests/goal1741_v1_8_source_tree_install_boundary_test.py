import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1741_v1_8_source_tree_install_boundary_2026-05-12.md"


class Goal1741V18SourceTreeInstallBoundaryTest(unittest.TestCase):
    def test_report_records_source_tree_boundary_and_packaging_gap(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("source_tree_boundary_validated_packaging_pending", text)
        self.assertIn("no `pyproject.toml`", text)
        self.assertIn("no `setup.py`", text)
        self.assertIn("no `setup.cfg`", text)
        self.assertIn("not a packaging implementation", text)
        self.assertIn("not a tag authorization", text)

    def test_packaging_metadata_is_still_absent(self) -> None:
        for name in ("pyproject.toml", "setup.py", "setup.cfg"):
            self.assertFalse((ROOT / name).exists(), name)

    def test_source_tree_hello_world_smoke(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src;." if os.name == "nt" else "src:."
        completed = subprocess.run(
            [sys.executable, "examples/rtdl_hello_world.py"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("hello, world", completed.stdout)

    def test_source_tree_backend_smoke(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src;." if os.name == "nt" else "src:."
        completed = subprocess.run(
            [sys.executable, "examples/rtdl_hello_world_backends.py", "--backend", "cpu_python_reference"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["backend"], "cpu_python_reference")
        self.assertEqual(payload["visible_hit_label"], "hello, world")
        self.assertEqual(payload["triangle_hit_count"], 2)


if __name__ == "__main__":
    unittest.main()
