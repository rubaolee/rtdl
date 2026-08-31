from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest


WORKSPACE = Path(__file__).resolve().parents[1]
FINDINGS = WORKSPACE / "history/internal_docs/goal5777_source_supported_causal_findings_20260814.json"
AUDIT = WORKSPACE / "history/internal_docs/goal5777_read_only_phase_audit_result_20260814.json"
SOURCE = Path(os.environ.get(
    "RTDL_GOAL5777_FROZEN_SOURCE",
    r"C:\Users\Lestat\AppData\Local\Temp\rtdl_goal5776_v9_verify_20260814\SOURCE",
))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Goal5777ReadOnlyCausalAuditTest(unittest.TestCase):
    def setUp(self):
        self.findings = json.loads(FINDINGS.read_text(encoding="utf-8"))
        self.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_all_frozen_source_pins_match(self):
        self.assertTrue(SOURCE.is_dir())
        for relative, expected in self.findings["source_pins"].items():
            self.assertEqual(sha(SOURCE / relative), expected, relative)

    def test_formal_phase_reconstruction_is_exact_and_complete(self):
        summary = self.audit["audit"]
        self.assertEqual(summary["independent_row_count"], 34)
        self.assertEqual((summary["pass_count"], summary["fail_count"]), (9, 25))
        self.assertEqual(summary["maximum_accounting_residual_seconds"], 0.0)

    def test_prepared_timer_only_attributes_execute(self):
        prepared = [r for r in self.audit["rows"] if r["lifecycle"] == "prepared_first_execute"]
        self.assertTrue(prepared)
        self.assertTrue(all(r["endpoint_relevant_phases"] == ["execute"] for r in prepared))
        self.assertTrue(all(r["loading_preparation_close_outside_prepared_registered_timer"] for r in prepared))

    def test_triangle_weighted_extra_device_work_is_source_present(self):
        source = (SOURCE / "src/rtdsl/v4_triangle_reduction_device_runtime.py").read_text(encoding="utf-8")
        self.assertIn("cp.max(ray_weights).item()", source)
        self.assertIn("cp.sum(ray_weights, dtype=cp.uint64).item()", source)
        self.assertIn("per_ray * ray_weights", source)
        self.assertGreaterEqual(source.count("_device_columns("), 3)
        v2 = (SOURCE / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py").read_text(encoding="utf-8")
        self.assertIn("scene.ray_any_hit_weighted_sum_device_columns(rays, weights)", v2)

    def test_barneshut_linear_validation_is_source_present(self):
        source = (SOURCE / "src/rtdsl/v4_hierarchy_frontier.py").read_text(encoding="utf-8")
        self.assertIn('rows = tuple(dict(row) for row in endpoint["rows"])', source)
        self.assertIn("actual_ids = tuple(int(row.get(\"source_id\", -1)) for row in rows)", source)
        self.assertIn("for index, row in enumerate(rows):", source)

    def test_claim_boundary_rejects_savings_and_repair(self):
        self.assertFalse(self.findings["claim_boundary"]["direct_phase_observation_is_predicted_saving"])
        self.assertFalse(self.findings["claim_boundary"]["eliminability_proven"])
        self.assertFalse(self.findings["claim_boundary"]["repair_authorized_or_implemented"])
        self.assertEqual(
            self.findings["decision"]["one_global_repair_for_all_25_failures"], "REJECTED")


if __name__ == "__main__":
    unittest.main()
