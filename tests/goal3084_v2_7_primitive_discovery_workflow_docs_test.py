from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "current" / "getting_started" / "rtdl_primitive_discovery_workflow.py"
LEARN_DOC = ROOT / "docs" / "learn" / "primitive_discovery_workflow.md"


class Goal3084V27PrimitiveDiscoveryWorkflowDocsTest(unittest.TestCase):
    def test_primitive_discovery_workflow_example_runs(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
        completed = subprocess.run(
            [sys.executable, str(EXAMPLE)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(completed.stdout)
        plan = payload["advisory_plan"]

        self.assertEqual(payload["app"], "primitive_discovery_workflow")
        self.assertEqual(payload["status"], "metadata_only_no_execution")
        self.assertEqual(payload["recipe_match"]["id"], "recipe.fixed_radius_ranked_candidates")
        self.assertEqual(plan["recipe_id"], "recipe.fixed_radius_ranked_candidates")
        self.assertIsNone(plan["selected_partner"])
        self.assertFalse(plan["executes"])
        self.assertFalse(plan["automatic_partner_selection_allowed"])
        self.assertTrue(plan["partner_options"])
        self.assertIn(
            {
                "operation": "grouped_argmin_f64",
                "partner": "numba",
                "status": "unsupported_fail_closed",
                "supported": False,
            },
            plan["partner_options"],
        )
        self.assertIn("performance wording", payload["claim_boundary"])

    def test_learn_doc_explains_three_step_workflow_and_boundaries(self) -> None:
        text = LEARN_DOC.read_text(encoding="utf-8")

        self.assertIn("rt.find_primitive", text)
        self.assertIn("rt.find_recipe", text)
        self.assertIn("rt.plan_continuation", text)
        self.assertIn("metadata-only", text)
        self.assertIn("selected_partner", text)
        self.assertIn("Always `False`", text)
        self.assertIn("does not authorize", text)
        self.assertIn("automatic partner selection", text)

    def test_public_indexes_link_workflow(self) -> None:
        paths = (
            ROOT / "docs" / "learn" / "README.md",
            ROOT / "docs" / "tutorials" / "README.md",
            ROOT / "docs" / "app_example_quickstart.md",
            ROOT / "docs" / "application_catalog.md",
            ROOT / "examples" / "README.md",
            ROOT / "examples" / "current" / "getting_started" / "README.md",
            ROOT / "examples" / "current" / "README.md",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertIn("primitive_discovery", path.read_text(encoding="utf-8").lower())

    def test_examples_alias_exports_workflow(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                "import examples; print('rtdl_primitive_discovery_workflow' in examples.__all__)",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        self.assertEqual(completed.stdout.strip(), "True")


if __name__ == "__main__":
    unittest.main()
