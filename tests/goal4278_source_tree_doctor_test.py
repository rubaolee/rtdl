from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_source_tree_doctor.py"
DOC = ROOT / "docs" / "learn" / "source_tree_doctor.md"


class Goal4278SourceTreeDoctorTest(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=False,
        )

    def test_human_output_reports_required_and_optional_boundaries(self) -> None:
        result = self._run()

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("RTDL V3 Source Tree Doctor", result.stdout)
        self.assertIn("surface: current V3", result.stdout)
        self.assertIn("[PASS] current V3 marker", result.stdout)
        self.assertIn("[PASS] current V3 test matrix", result.stdout)
        self.assertNotIn("V4 preparatory C ABI", result.stdout)
        self.assertNotIn("optional module cupy", result.stdout)
        self.assertNotIn("optional OptiX library", result.stdout)
        self.assertIn("Core V3 checks passed", result.stdout)

    def test_json_output_is_machine_readable_and_fail_closed_for_required_checks(self) -> None:
        result = self._run("--json")

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("rtdl_source_tree_doctor", payload["tool"])
        self.assertEqual("v3.0.0", payload["version"])
        self.assertTrue(payload["ok"])
        self.assertEqual([], payload["required_failures"])

        names = {item["name"] for item in payload["checks"]}
        for required in (
            "current V3 marker",
            "pyproject V3 package version",
            "front page",
            "docs index",
            "current V3 status",
            "public documentation map",
            "tutorials path",
            "V3 tutorial path",
            "examples path",
            "performance wording guide",
            "source-tree doctor docs",
            "current V3 test matrix",
            "module rtdsl",
            "module numpy",
            "optional module cupy",
            "optional OptiX library",
        ):
            self.assertIn(required, names)
        self.assertNotIn("V4 preparatory C ABI surface", names)
        self.assertNotIn("V4 preparatory C ABI docs", names)

    def test_smoke_option_runs_portable_hello_world(self) -> None:
        result = self._run("--json", "--run-smoke")

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        smoke = [item for item in payload["checks"] if item["name"] == "hello-world smoke"]
        self.assertEqual(1, len(smoke))
        self.assertEqual("pass", smoke[0]["status"])

    def test_docs_wire_doctor_into_learner_path(self) -> None:
        docs = "\n".join(
            [
                DOC.read_text(encoding="utf-8"),
                (ROOT / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "learn" / "README.md").read_text(encoding="utf-8"),
                (ROOT / "tutorials" / "current" / "01_first_run.md").read_text(
                    encoding="utf-8"
                ),
            ]
        )

        self.assertIn("scripts/rtdl_source_tree_doctor.py", docs)
        self.assertIn("run_test_matrix.py --group v3_current_surface", docs)
        self.assertIn("Source-Tree Doctor", docs)
        self.assertIn("checkout sanity check", docs)
        self.assertNotIn("examples/v2_0", docs)
        self.assertNotIn("v2.6", docs)


if __name__ == "__main__":
    unittest.main()
