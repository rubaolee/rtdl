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
from rtdsl.v4 import V4_AUTHORIZED_RELEASE_LABEL


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
        self.assertTrue(payload["release_authorized"])
        self.assertEqual(V4_AUTHORIZED_RELEASE_LABEL, payload["authorized_release_label"])
        self.assertIn("brute-force partner/CPU baselines", payload["authorized_release_label"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])
        self.assertEqual(11, len(payload["examples"]))
        self.assertTrue(all(row["passed"] for row in payload["examples"]))
        rows_by_name = {row["name"]: row for row in payload["examples"]}
        self.assertIn("fixed_radius", rows_by_name)
        self.assertIn("primitive_grouped_i64_reduction", rows_by_name)
        self.assertIn("point_group_nearest_witness", rows_by_name)
        self.assertIn("ray_triangle_any_hit_weighted_sum", rows_by_name)
        self.assertIn("aabb_index_all_ops_count", rows_by_name)
        self.assertIn("v4_frontdoor_quickstart", rows_by_name)
        self.assertEqual(
            "dry_run",
            rows_by_name["primitive_grouped_i64_reduction"]["payload"]["status"],
        )
        self.assertEqual("dry_run", rows_by_name["point_group_nearest_witness"]["payload"]["status"])
        self.assertEqual("dry_run", rows_by_name["ray_triangle_any_hit_weighted_sum"]["payload"]["status"])
        self.assertEqual("dry_run", rows_by_name["aabb_index_all_ops_count"]["payload"]["status"])
        self.assertEqual(
            "tier2_measured_v4_0_0_release_surface",
            rows_by_name["aabb_index_all_ops_count"]["payload"]["surface_status"],
        )
        self.assertEqual(
            "tier2_measured_v4_0_0_release_surface",
            rows_by_name["ray_triangle_any_hit_weighted_sum"]["payload"]["surface_status"],
        )
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
        self.assertIn("Status: generated V4.0.0 catalog gate", markdown)

    def test_include_candidates_is_backward_compatible_with_no_current_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "catalog_candidates.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "dry-run",
                    "--copies",
                    "16",
                    "--ray-count",
                    "16",
                    "--include-candidates",
                    "--json-out",
                    str(json_out),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))

        self.assertEqual("passed", payload["status"])
        self.assertEqual(11, len(payload["examples"]))
        rows_by_name = {row["name"]: row for row in payload["examples"]}
        weighted = rows_by_name["ray_triangle_any_hit_weighted_sum"]["payload"]
        self.assertEqual("dry_run", weighted["status"])
        self.assertEqual("tier2_measured_v4_0_0_release_surface", weighted["surface_status"])
        self.assertFalse(weighted["release_claim_authorized"])
        self.assertFalse(weighted["true_zero_copy_authorized"])

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
