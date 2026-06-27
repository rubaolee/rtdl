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

from rtdsl.v4_goal4714_custom_predicate_early_exit_smoke_result import (
    classify_v4_goal4714_custom_predicate_early_exit_smoke,
    validate_v4_goal4714_custom_predicate_early_exit_smoke_result_contract,
)


SCRIPT = ROOT / "scripts" / "v4_goal4714_custom_predicate_early_exit_smoke_pod.py"


class V4Goal4714CustomPredicateEarlyExitSmokeResultTest(unittest.TestCase):
    def test_classifier_requires_early_termination_on_primary_rows(self) -> None:
        validation = validate_v4_goal4714_custom_predicate_early_exit_smoke_result_contract()
        self.assertEqual("passed", validation["status"])
        rows = [
            {
                "row_role": "primary",
                "correctness_passed": True,
                "early_termination_observed": True,
                "v4_anyhit_invocations": 100,
                "fallback_all_hit_invocations": 800,
            },
            {
                "row_role": "primary",
                "correctness_passed": True,
                "early_termination_observed": True,
                "v4_anyhit_invocations": 100,
                "fallback_all_hit_invocations": 3200,
            },
            {"row_role": "control", "correctness_passed": True},
            {"row_role": "control", "correctness_passed": True},
        ]
        result = classify_v4_goal4714_custom_predicate_early_exit_smoke(rows)
        self.assertEqual("pass_smoke_gate_not_timing_not_release", result["classification"])
        self.assertFalse(result["pod_timing_authorized"])

    def test_script_dry_run_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "goal4714.json"
            md_out = tmp_path / "goal4714.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
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
        self.assertEqual("dry_run_contract_passed", payload["status"])
        self.assertEqual("dry_run_contract_passed", stdout_payload["status"])
        self.assertIn("Custom Predicate Early-Exit Smoke", markdown)


if __name__ == "__main__":
    unittest.main()
