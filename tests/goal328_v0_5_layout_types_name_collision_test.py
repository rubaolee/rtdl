from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LayoutTypesNameCollisionTest(unittest.TestCase):
    def test_stdlib_types_wins_when_rtdsl_package_dir_is_on_sys_path(self) -> None:
        code = """
import pathlib
import sys

repo_root = pathlib.Path.cwd()
sys.path.insert(0, str(repo_root / "src" / "rtdsl"))
import types
print(types.__file__)
"""
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        normalized = completed.stdout.strip().replace("\\", "/")
        self.assertTrue(normalized.endswith("/types.py"), normalized)
        self.assertNotIn("/src/rtdsl/", normalized)

    def test_public_rtdsl_import_surface_still_exposes_layout_objects(self) -> None:
        code = """
import pathlib
import sys

repo_root = pathlib.Path.cwd()
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root))
import rtdsl as rt
print(rt.Point2DLayout.name)
print(rt.Points.required_fields)
"""
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("Point2D", completed.stdout)
        self.assertIn("('x', 'y', 'id')", completed.stdout)


if __name__ == "__main__":
    unittest.main()
