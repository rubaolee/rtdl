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
        self.assertIn("RTDL Source Tree Doctor", result.stdout)
        self.assertIn("version: v3.0.1", result.stdout)
        self.assertIn("[PASS] version marker", result.stdout)
        self.assertIn("[PASS] V3 current test matrix", result.stdout)
        self.assertIn("optional module cupy", result.stdout)
        self.assertIn("optional OptiX library", result.stdout)
        self.assertIn("Optional warnings only affect native/partner paths", result.stdout)

    def test_json_output_is_machine_readable_and_fail_closed_for_required_checks(self) -> None:
        result = self._run("--json")

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("rtdl_source_tree_doctor", payload["tool"])
        self.assertEqual("v3.0.1", payload["version"])
        self.assertTrue(payload["ok"])
        self.assertEqual([], payload["required_failures"])

        names = {item["name"] for item in payload["checks"]}
        for required in (
            "version marker",
            "src/rtdsl",
            "front page",
            "top-level tutorials",
            "current examples",
            "v3.0.1 release package",
            "V3 app-author strategy",
            "V3 current test matrix",
            "module rtdsl",
            "module numpy",
        ):
            self.assertIn(required, names)

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
                (ROOT / "tutorials" / "current" / "01_source_tree_first_run.md").read_text(
                    encoding="utf-8"
                ),
            ]
        )

        self.assertIn("scripts/rtdl_source_tree_doctor.py", docs)
        self.assertIn("scripts/run_test_matrix.py --group v3_current", docs)
        self.assertIn("Source-Tree Doctor", docs)
        self.assertIn("not a benchmark", docs)
        self.assertNotIn("examples/v2_0", docs)
        self.assertNotIn("v2.6", docs)


if __name__ == "__main__":
    unittest.main()
