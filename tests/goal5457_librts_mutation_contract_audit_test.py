from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl.aabb_index as aabb_index


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
AUDIT = APP_DIR / "results" / "librts_goal5457_mutation_contract_audit.json"


class Goal5457LibRTSMutationContractAuditTest(unittest.TestCase):
    def test_current_prepared_aabb_types_have_no_mutation_surface(self):
        for prepared_type in (aabb_index.AabbIndex2D, aabb_index.OptixAabbIndex2D):
            for method in ("insert", "update", "delete", "clear", "apply_mutations"):
                self.assertFalse(hasattr(prepared_type, method), (prepared_type, method))

    def test_audit_requires_generic_api_without_native_refit_claim(self):
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(audit["status"], "requires_new_generic_mutable_aabb_api")
        self.assertEqual(audit["decision"]["label"], "requires_new_generic_api")
        self.assertIn("snapshot rebuild", audit["decision"]["first_implementation"])
        self.assertFalse(audit["decision"]["native_incremental_refit_claimed"])
        self.assertFalse(audit["decision"]["author_mutation_performance_parity_claimed"])
        self.assertTrue(audit["decision"]["non_librts_consumer_required"])
        self.assertFalse(audit["backend_scope"]["embree"])

    def test_historical_benchmark_does_not_masquerade_as_prepared_mutation(self):
        source = (
            ROOT
            / "examples/current/research_benchmarks/librts_spatial_index"
            / "rtdl_librts_spatial_index_benchmark_app.py"
        ).read_text(encoding="utf-8")
        start = source.index("def apply_mutation_scenario")
        end = source.index("def write_wkt_fixture", start)
        window = source[start:end]
        self.assertIn("run_counts(mutated, operation)", window)
        self.assertNotIn("prepare_aabb_index_2d", window)
        self.assertNotIn("apply_mutations", window)


if __name__ == "__main__":
    unittest.main()
