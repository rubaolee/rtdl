from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_catalog_regression_gate.py"

SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scripts.v4_catalog_regression_gate import _validate_payload


class V4CatalogRegressionGateTest(unittest.TestCase):
    def test_dry_run_gate_executes_all_catalog_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "catalog.json"
            md_out = tmp_path / "catalog.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "dry-run",
                    "--copies",
                    "16",
                    "--ray-count",
                    "16",
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
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])
        self.assertEqual(7, len(payload["examples"]))
        self.assertTrue(all(row["passed"] for row in payload["examples"]))
        rows_by_name = {row["name"]: row for row in payload["examples"]}
        self.assertIn("fixed_radius", rows_by_name)
        self.assertIn("v4_frontdoor_quickstart", rows_by_name)
        self.assertEqual(
            "tier2_measured_ready",
            rows_by_name["operator_callback_planning_tier2"]["payload"]["status"],
        )
        self.assertEqual(
            "tier3_spike_only_not_v4_0_release_surface",
            rows_by_name["operator_callback_planning_scalar_callback"]["payload"]["status"],
        )
        self.assertIsNone(rows_by_name["operator_callback_planning_scalar_callback"]["payload"]["api_surface"])
        self.assertEqual(
            "rejected_action_shaped_callback_deferred",
            rows_by_name["operator_callback_planning_complex_callback"]["payload"]["status"],
        )
        self.assertIsNone(rows_by_name["operator_callback_planning_complex_callback"]["payload"]["api_surface"])
        self.assertIn("Status: generated development gate", markdown)

    def test_gate_rejects_forbidden_claim_flags_even_when_nested(self) -> None:
        payload = {
            "status": "measured",
            "correctness_passed": True,
            "release_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
            "metadata": {
                "cupy_performance_claim_authorized": True,
                "nested": {"non_python_host_binding_claim_authorized": True},
            },
        }

        passed, failures = _validate_payload("fixed_radius", payload, "gpu")

        self.assertFalse(passed)
        self.assertIn(
            "forbidden_claim_flag_true:payload.metadata.cupy_performance_claim_authorized",
            failures,
        )
        self.assertIn(
            "forbidden_claim_flag_true:payload.metadata.nested.non_python_host_binding_claim_authorized",
            failures,
        )


if __name__ == "__main__":
    unittest.main()
