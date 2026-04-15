from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal410_tutorial_example_check.py"
SPEC = importlib.util.spec_from_file_location("goal410_tutorial_example_check", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal411PublicSurfaceCiAutomationTest(unittest.TestCase):
    def test_public_cases_include_portable_minimum(self) -> None:
        names = {entry["name"] for entry in MODULE.public_cases()}
        self.assertIn("hello_world", names)
        self.assertIn("hello_world_cpu_python_reference", names)
        self.assertIn("hello_world_cpu", names)
        self.assertIn("graph_bfs_cpu_python_reference", names)
        self.assertIn("graph_bfs_cpu", names)
        self.assertIn("graph_triangle_cpu_python_reference", names)
        self.assertIn("graph_triangle_cpu", names)

    def test_gpu_cases_are_explicitly_linux_only(self) -> None:
        gpu_case_names = {
            "hello_world_optix",
            "hello_world_vulkan",
            "graph_bfs_optix",
            "graph_bfs_vulkan",
            "graph_triangle_optix",
            "graph_triangle_vulkan",
        }
        by_name = {entry["name"]: entry for entry in MODULE.public_cases()}
        for name in gpu_case_names:
            self.assertTrue(by_name[name]["linux_only"], name)

    def test_portable_minimum_has_no_linux_only_flag(self) -> None:
        for entry in MODULE.public_cases():
            if entry["name"].endswith("_cpu_python_reference") or entry["name"].endswith("_cpu"):
                self.assertFalse(entry["linux_only"], entry["name"])


if __name__ == "__main__":
    unittest.main()
