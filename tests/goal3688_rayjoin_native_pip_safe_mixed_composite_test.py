from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py"
ARTIFACT = ROOT / "docs/reports/goal3688_rayjoin_native_pip_safe_mixed_composite_a5000/summary.json"


class Goal3688RayJoinNativePipSafeMixedCompositeTest(unittest.TestCase):
    def test_runner_uses_native_pip_executor_and_safe_existing_routes(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("prepare_relation_status_corrected_scalar_count_executor", source)
        self.assertIn("prepared_native_relation_status_corrected_scalar_count_executor", source)
        self.assertIn("_run_exact_lsi_prepared_optix", source)
        self.assertIn("run_rtdl_optix(", source)
        self.assertIn('"rtdl_optix_native_scalar_count_executor"', source)
        self.assertIn('"rtdl_optix_exact_refined_count"', source)
        self.assertIn('"rtdl_optix_active_count"', source)

    def test_runner_is_candidate_non_authorizing_packet(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("not promote a default route", source)
        self.assertIn("_claim_boundary()", source)
        self.assertIn("native_pip_safe_mixed_speedup_vs_all_cupy", source)
        self.assertIn("all_counts_match", source)
        self.assertIn("count mismatch", source)
        self.assertIn("goal3688_scoped_source_dirty", source)
        self.assertIn("SCOPED_SOURCE_PATHS", source)

    def test_a5000_artifact_preserves_boundary_and_exact_counts(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3688.rayjoin_native_pip_safe_mixed_composite.v1")
        self.assertEqual(payload["source_commit_short"], "f55ba72d")
        self.assertFalse(payload["goal3688_scoped_source_dirty"])
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertGreater(payload["summary"]["min_native_pip_safe_mixed_speedup_vs_all_cupy"], 1.0)
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        rows = payload["rows"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["chain_count"], 4096)
        self.assertTrue(row["all_counts_match"])
        self.assertGreater(row["native_pip_safe_mixed_speedup_vs_all_cupy"], 100.0)
        workloads = {item["workload"]: item for item in row["workloads"]}
        self.assertEqual(set(workloads), {"pip", "lsi", "overlay_seed"})
        self.assertEqual(workloads["pip"]["candidate_route"]["execution_route"], "prepared_native_relation_status_corrected_scalar_count_executor")
        for workload in workloads.values():
            self.assertTrue(workload["counts_match"])
            self.assertEqual(
                workload["all_cupy_baseline"]["row_count"],
                workload["candidate_route"]["row_count"],
            )
            self.assertGreater(workload["candidate_speedup_vs_cupy"], 1.0)


if __name__ == "__main__":
    unittest.main()
