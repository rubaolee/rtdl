from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_test_matrix.py"
SPEC = importlib.util.spec_from_file_location("run_test_matrix", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestMatrixRunnerTest(unittest.TestCase):
    def test_groups_are_pairwise_disjoint(self) -> None:
        groups = MODULE.TEST_GROUPS
        names = list(groups)
        for i, left_name in enumerate(names):
            left = set(groups[left_name])
            for right_name in names[i + 1 :]:
                right = set(groups[right_name])
                self.assertEqual(left & right, set(), f"{left_name} overlaps {right_name}")

    def test_group_modules_exist(self) -> None:
        for group_name, modules in MODULE.TEST_GROUPS.items():
            for module_name in modules:
                spec = importlib.util.find_spec(module_name)
                self.assertIsNotNone(spec, f"{group_name} missing module {module_name}")

    def test_full_group_is_union_of_all_groups(self) -> None:
        expected = (
            MODULE.TEST_GROUPS["unit"]
            + MODULE.TEST_GROUPS["integration"]
            + MODULE.TEST_GROUPS["system"]
        )
        self.assertEqual(MODULE.group_modules("full"), expected)

    def test_run_group_reports_command(self) -> None:
        payload = MODULE.run_group("unit")
        self.assertEqual(payload["group"], "unit")
        self.assertIn("python3 -m unittest", payload["command"])
        self.assertEqual(payload["module_count"], len(MODULE.TEST_GROUPS["unit"]))
        self.assertIn("output", payload)

    def test_cli_unit_group_runs(self) -> None:
        cp = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--group", "unit"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(cp.returncode, 0, cp.stdout + "\n" + cp.stderr)
        payload = json.loads(cp.stdout)
        self.assertEqual(payload["group"], "unit")
        self.assertTrue(payload["ok"])


if __name__ == "__main__":
    unittest.main()
