from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4718_release_matrix_after_custom_predicate import (  # noqa: E402
    V4_GOAL4718_DECISION_LABEL,
    validate_v4_goal4718_release_matrix_after_custom_predicate,
)


SCRIPT = ROOT / "scripts" / "v4_goal4718_release_matrix_after_custom_predicate.py"


class V4Goal4718ReleaseMatrixAfterCustomPredicateTest(unittest.TestCase):
    def test_matrix_separates_new_workflow_from_legacy_all_app_claim(self) -> None:
        validation = validate_v4_goal4718_release_matrix_after_custom_predicate()
        self.assertEqual("passed", validation["status"])
        matrix = validation["matrix"]

        self.assertEqual(V4_GOAL4718_DECISION_LABEL, matrix["decision_label"])
        self.assertEqual(10, matrix["measured_surface_count"])
        self.assertTrue(matrix["v4_python_edsl_release_candidate_supported"])
        self.assertTrue(matrix["v4_operator_pushdown_workflow_high_performance_supported"])
        self.assertFalse(matrix["legacy_all_app_high_performance_supported"])
        self.assertFalse(matrix["broad_all_benchmark_speedup_supported"])
        self.assertFalse(matrix["release_authorized"])
        self.assertFalse(matrix["formal_tag_authorized"])
        self.assertFalse(matrix["public_wording_authorized_before_goal4719"])

        workflow = matrix["new_v4_workflow_rows"][0]
        self.assertEqual("v4_ray_triangle_custom_predicate_early_exit_3d_numba", workflow["api_surface"])
        self.assertGreaterEqual(workflow["v4_vs_v3_0_2_primary_geomean"], 1.50)
        self.assertGreaterEqual(workflow["min_primary_v4_vs_v3_0_2"], 1.20)
        self.assertTrue(workflow["correctness_all_passed"])
        self.assertTrue(workflow["counts_as_v4_edsl_value"])
        self.assertFalse(workflow["counts_as_legacy_all_app_speedup"])

        legacy = matrix["legacy_promoted_app_state"]
        self.assertEqual(
            "bounded_operator_v4_only__app_level_high_performance_not_supported",
            legacy["decision_label"],
        )
        self.assertFalse(legacy["formal_high_performance_v4_supported"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "goal4718.json"
            md_out = tmp_path / "goal4718.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            stdout_payload = json.loads(proc.stdout)
            markdown = md_out.read_text(encoding="utf-8")
        self.assertEqual("passed", payload["status"])
        self.assertEqual("passed", stdout_payload["status"])
        self.assertIn("Release Matrix", markdown)
        self.assertIn("legacy all-app high-performance supported: `False`", markdown)


if __name__ == "__main__":
    unittest.main()
